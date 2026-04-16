#!/usr/bin/env python3
"""Validate a summary.md produced by /lai-summarize against the source.

Checks:
  - YAML frontmatter is parseable and has required fields
  - seo_title <= 60 chars, seo_description <= 160 chars
  - tags: 4 to 8 items
  - confidence in [0.0, 1.0]; source_quality in {high, medium, low}
  - chapters: 1–8 entries; each has title / start / end; start < end
  - if meta.md (auto-detected) has `chapters:`, frontmatter chapter titles
    and timestamps match it verbatim (hard constraint)
  - quoted passages in the body appear verbatim in source transcript text
  - chapter H2 headers (## [MM:SS] Title) align 1:1 with frontmatter chapters

Exits 0 on pass, 1 on failure.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("error: pyyaml is required. `pip install pyyaml`", file=sys.stderr)
    sys.exit(2)

from lattifai.caption import Caption

REQUIRED_FIELDS = ("title", "seo_title", "seo_description", "tags", "chapters", "confidence", "source_quality")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)
QUOTE_RE = re.compile(r"^>\s*\*?\"(.+?)\"\*?\s*$", re.MULTILINE)
CHAPTER_H2_RE = re.compile(r"^##\s*\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s+(.+?)\s*$", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("missing or malformed YAML frontmatter")
    data = yaml.safe_load(m.group(1)) or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data, m.group(2)


def check_frontmatter(fm: dict, errors: list[str]) -> None:
    for f in REQUIRED_FIELDS:
        if f not in fm:
            errors.append(f"missing field: {f}")

    if isinstance(fm.get("seo_title"), str) and len(fm["seo_title"]) > 60:
        errors.append(f"seo_title > 60 chars ({len(fm['seo_title'])})")
    if isinstance(fm.get("seo_description"), str) and len(fm["seo_description"]) > 160:
        errors.append(f"seo_description > 160 chars ({len(fm['seo_description'])})")

    tags = fm.get("tags")
    if isinstance(tags, list) and not (4 <= len(tags) <= 8):
        errors.append(f"tags length {len(tags)} not in [4, 8]")

    conf = fm.get("confidence")
    if isinstance(conf, (int, float)) and not (0.0 <= conf <= 1.0):
        errors.append(f"confidence {conf} out of [0, 1]")

    sq = fm.get("source_quality")
    if sq not in (None, "high", "medium", "low"):
        errors.append(f"source_quality {sq!r} not in high/medium/low")


def check_chapters(fm: dict, body: str, errors: list[str]) -> None:
    chapters = fm.get("chapters") or []
    if not isinstance(chapters, list):
        errors.append("chapters is not a list")
        return
    if not (1 <= len(chapters) <= 8):
        errors.append(f"chapters length {len(chapters)} not in [1, 8]")
    for i, c in enumerate(chapters):
        if not isinstance(c, dict) or not all(k in c for k in ("title", "start", "end")):
            errors.append(f"chapter[{i}] missing title/start/end")
            continue
        if not (isinstance(c["start"], (int, float)) and isinstance(c["end"], (int, float))):
            errors.append(f"chapter[{i}] start/end not numeric")
            continue
        if c["start"] >= c["end"]:
            errors.append(f"chapter[{i}] start >= end")

    # Body H2 headers should match frontmatter chapter titles in order.
    headers = CHAPTER_H2_RE.findall(body)
    fm_titles = [str(c.get("title", "")) for c in chapters if isinstance(c, dict)]
    body_titles = [t for _, t in headers]
    if fm_titles and body_titles != fm_titles:
        errors.append(f"body chapter headers do not match frontmatter (body={body_titles} vs fm={fm_titles})")


def check_meta_hard_constraint(fm: dict, source: Path, errors: list[str]) -> None:
    # meta.md is authoritative when present; chapter titles+timestamps must match verbatim.
    for candidate in (source.with_suffix(".meta.md"), source.parent / "meta.md"):
        if not candidate.is_file():
            continue
        raw = candidate.read_text(encoding="utf-8")
        if "---" not in raw:
            # Silently skipping is the old bug — warn loudly so the user
            # doesn't assume hard-constraint checks ran.
            print(
                f"warning: {candidate} has no YAML frontmatter (needs `---` delimiters); "
                "hard-constraint checks skipped.",
                file=sys.stderr,
            )
            return
        try:
            meta = yaml.safe_load(raw.split("---", 2)[1])
        except yaml.YAMLError as e:
            errors.append(f"meta.md frontmatter is not valid YAML: {e}")
            return
        if not isinstance(meta, dict):
            print(f"warning: {candidate} frontmatter is not a mapping; hard-constraint checks skipped.", file=sys.stderr)
            return
        if "chapters" not in meta:
            # meta.md present but no `chapters:` key → user did not declare
            # a hard constraint; let the agent's chapters stand.
            return
        meta_chapters = meta.get("chapters") or []
        fm_chapters = fm.get("chapters") or []
        if len(meta_chapters) != len(fm_chapters):
            errors.append(f"chapter count drifts from meta.md ({len(fm_chapters)} vs {len(meta_chapters)})")
            return
        for i, (m, f) in enumerate(zip(meta_chapters, fm_chapters)):
            if m.get("title") != f.get("title"):
                errors.append(f"chapter[{i}] title drift from meta.md: {f.get('title')!r} vs {m.get('title')!r}")
            if abs(float(m.get("start", 0)) - float(f.get("start", 0))) > 1e-3:
                errors.append(f"chapter[{i}] start drift from meta.md")
            if abs(float(m.get("end", 0)) - float(f.get("end", 0))) > 1e-3:
                errors.append(f"chapter[{i}] end drift from meta.md")
        return


def check_quotes_verbatim(body: str, source_text: str, errors: list[str]) -> None:
    # Normalize whitespace on both sides; quotes must be substrings of source.
    norm_source = re.sub(r"\s+", " ", source_text).strip()
    for q in QUOTE_RE.findall(body):
        norm_q = re.sub(r"\s+", " ", q).strip()
        if norm_q and norm_q not in norm_source:
            errors.append(f"quote not found verbatim in source: {norm_q[:80]!r}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", type=Path, help="Original caption/transcript file")
    ap.add_argument("summary", type=Path, help="Generated summary.md")
    args = ap.parse_args()

    text = args.summary.read_text(encoding="utf-8")
    errors: list[str] = []
    try:
        fm, body = parse_frontmatter(text)
    except ValueError as e:
        print(f"FAIL — {e}", file=sys.stderr)
        return 1

    check_frontmatter(fm, errors)
    check_chapters(fm, body, errors)
    check_meta_hard_constraint(fm, args.source, errors)

    caption = Caption.read(args.source)
    source_text = " ".join((s.text or "") for s in caption.supervisions)
    check_quotes_verbatim(body, source_text, errors)

    if not errors:
        print("OK — summary invariants hold")
        return 0

    print(f"FAIL — {len(errors)} violation(s):", file=sys.stderr)
    for e in errors[:15]:
        print(f"  {e}", file=sys.stderr)
    if len(errors) > 15:
        print(f"  … and {len(errors) - 15} more", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
