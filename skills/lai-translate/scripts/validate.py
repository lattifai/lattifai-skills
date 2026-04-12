#!/usr/bin/env python3
"""Validate translation output against the source caption file.

Structural invariants (format-agnostic):
  - Segment count matches
  - start / end / duration unchanged (1 ms tolerance)
  - speaker labels unchanged
  - every output segment has non-empty text

Format-specific: when both files are JSON (lossless), also verifies:
  - every supervision has a non-empty `translation` field
  - source `text` is preserved (bilingual workflow)

For non-JSON outputs (SRT/VTT/ASS/…) the writer fuses translation into text,
so `translation` / source-`text` preservation cannot be round-tripped and is
not checked here. Run validation on JSON whenever possible.

Exits 0 on pass, 1 on failure.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lattifai.caption import Caption

TOL = 1e-3


def is_json(path: Path) -> bool:
    return path.suffix.lower() == ".json"


def compare(src: Caption, out: Caption, strict_text: bool) -> list[str]:
    errors: list[str] = []
    n_src = len(src.supervisions)
    n_out = len(out.supervisions)
    if n_src != n_out:
        return [f"segment count drift: source={n_src} output={n_out}"]

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
            if (a.text or "") != (b.text or ""):
                errors.append(f"[{i}] source text changed (expected bilingual JSON)")
            if not (b.translation and b.translation.strip()):
                errors.append(f"[{i}] empty translation field")
    return errors


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
    errors = compare(src, out, strict_text=strict_text)

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
