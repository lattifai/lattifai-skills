#!/usr/bin/env python3
"""Validate translation output against the source caption file.

Structural invariants (format-agnostic):
  - Segment count matches
  - start / end / duration unchanged (1 ms tolerance)
  - speaker labels unchanged
  - every output segment has non-empty text
  - **output text differs from source text** for every segment — catches
    silent translation drops (e.g. an SRT round-trip that re-spliced
    source-only cue text over the rendered translation, leaving the file
    structurally valid but content-wise unchanged).

Format-specific: when both files are JSON (lossless), also verifies:
  - every supervision has a non-empty `translation` field
  - source `text` is preserved (bilingual workflow)

For non-JSON outputs (SRT/VTT/ASS/…) the writer fuses translation into text;
the per-segment "text differs" check is the only signal that translation
content actually made it into the file.

Exits 0 on pass, 1 on failure.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from lattifai.caption import Caption

TOL = 1e-3

# Punctuation-parity drift detector. Sister pipeline audited 14 k zh
# supervisions and found 16 % had em-dashes added to sentences whose source
# contained none, plus ~24 with parentheses inserted as glosses. Both
# deform delivery — em-dash forces a hard pause and parens get rendered
# (or read aloud by downstream TTS).
#
# Detection: classify source and translation independently into {dash,
# paren, bracket} buckets, flag any bucket present in translation but
# absent from source. Word-internal hyphens ("follow-up") are excluded
# from the source DASH detector so real free-standing dashes still count.
_SRC_DASH_RE = re.compile(r"(?:^|\s)(?:-{2,}|—|–)(?:\s|$|[A-Za-z　])")
_TGT_DASH_RE = re.compile(r"——|—|-{2,}")
_PAREN_RE = re.compile(r"[()（）]")
_BRACKET_RE = re.compile(r"[\[\]【】]")


def detect_punct_drift(source: str, translation: str) -> list[str]:
    """Return categories ({"dash","paren","bracket"}) the translation added.

    Source already containing the same category is exempt — a translator
    faithfully mirroring source punctuation is fine. We flag *additions*.
    """
    drift: list[str] = []
    if _TGT_DASH_RE.search(translation) and not _SRC_DASH_RE.search(source):
        drift.append("dash")
    if _PAREN_RE.search(translation) and not _PAREN_RE.search(source):
        drift.append("paren")
    if _BRACKET_RE.search(translation) and not _BRACKET_RE.search(source):
        drift.append("bracket")
    return drift


def is_json(path: Path) -> bool:
    return path.suffix.lower() == ".json"


def compare(
    src: Caption, out: Caption, strict_text: bool
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings).

    Errors are hard failures (FAIL → exit 1). Warnings are quality signals
    (e.g. punct_drift) that get printed but do NOT change the exit code —
    `lai-translate`'s validator stays a structural-bug catcher; agents
    should not have produced drift in the first place, and downstream
    flow is not blocked when they do.
    """
    errors: list[str] = []
    warnings: list[str] = []
    n_src = len(src.supervisions)
    n_out = len(out.supervisions)
    if n_src != n_out:
        return ([f"segment count drift: source={n_src} output={n_out}"], warnings)

    for i, (a, b) in enumerate(zip(src.supervisions, out.supervisions)):
        if abs(a.start - b.start) > TOL:
            errors.append(f"[{i}] start drift: {a.start} → {b.start}")
        if abs(a.end - b.end) > TOL:
            errors.append(f"[{i}] end drift: {a.end} → {b.end}")
        if (a.speaker or "") != (b.speaker or ""):
            errors.append(f"[{i}] speaker changed: {a.speaker!r} → {b.speaker!r}")
        if not (b.text and b.text.strip()):
            errors.append(f"[{i}] empty output text")

        if strict_text:
            # JSON-to-JSON bilingual workflow: source text preserved verbatim,
            # translation carried in its own field.
            if (a.text or "") != (b.text or ""):
                errors.append(f"[{i}] source text changed (expected bilingual JSON)")
            if not (b.translation and b.translation.strip()):
                errors.append(f"[{i}] empty translation field")
        else:
            # Non-JSON output: writer fuses translation into text. The output
            # text must differ from source — catches silent drops where the
            # writer round-tripped the source-only cue back over the rendered
            # translation (a real bug surfaced by the SRT raw-cue splice).
            if (a.text or "").strip() == (b.text or "").strip():
                errors.append(
                    f"[{i}] output text identical to source — translation "
                    f"may have been silently dropped"
                )

        # Punctuation parity — source vs translated string. In bilingual JSON
        # the translated string lives in `b.translation`; in fused outputs
        # (SRT/VTT/ASS round-tripped through merge.py replace mode) it sits
        # in `b.text`. Pick whichever carries the actual translation content.
        translated_text = (b.translation or "").strip() if strict_text else (b.text or "").strip()
        if translated_text:
            for cat in detect_punct_drift(a.text or "", translated_text):
                warnings.append(
                    f"[{i}] punct_drift_{cat}: translation added "
                    f"{cat} not present in source"
                )
    return (errors, warnings)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--max-report", type=int, default=10, help="Max violations to print")
    args = ap.parse_args()

    src = Caption.read(args.source)
    out = Caption.read(args.output)

    # Only apply strict text/translation checks when BOTH files are JSON.
    # In that case we assume the bilingual workflow (source text preserved,
    # translation carried in its own field).
    strict_text = is_json(args.source) and is_json(args.output)
    errors, warnings = compare(src, out, strict_text=strict_text)

    if warnings:
        print(
            f"WARN — {len(warnings)} punct-drift signal(s) "
            f"(does not block, but agents should not produce these):",
            file=sys.stderr,
        )
        for w in warnings[: args.max_report]:
            print(f"  {w}", file=sys.stderr)
        if len(warnings) > args.max_report:
            print(f"  … and {len(warnings) - args.max_report} more", file=sys.stderr)

    if not errors:
        mode = "strict (JSON bilingual)" if strict_text else "structural"
        print(f"OK — {len(src.supervisions)} segments, {mode} invariants hold")
        return 0

    print(f"FAIL — {len(errors)} violation(s):", file=sys.stderr)
    for e in errors[: args.max_report]:
        print(f"  {e}", file=sys.stderr)
    if len(errors) > args.max_report:
        print(f"  … and {len(errors) - args.max_report} more", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
