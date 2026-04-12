#!/usr/bin/env python3
"""Convert a caption file (+ optional meta.md) into an agent-ready prompt input.

Output (stdout or --output) is markdown with:

    # Source
    - file: <path>   - language: en   - duration: 01:23:45   - segments: 420

    ## Meta  (if meta.md is provided or auto-detected beside the source)
    title / channel / speakers / ...

    ### Chapters  (HARD CONSTRAINT if meta.md has chapters:)
    - [00:10–00:52] Chapter Title
    ...

    # Transcript
    [MM:SS] speaker? text
    ...

The agent then writes `<source>.summary.md` using the schema in
/lai-summarize. Run `validate.py` afterwards to enforce invariants.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lattifai.caption import Caption


def fmt_ts(seconds: float) -> str:
    s = int(round(seconds))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}" if h else f"{m:02d}:{sec:02d}"


def load_meta(meta_path: Path) -> str:
    """Return meta.md content verbatim (frontmatter + body)."""
    return meta_path.read_text(encoding="utf-8")


def has_chapters_block(meta_text: str) -> bool:
    return "\nchapters:" in meta_text or meta_text.startswith("chapters:")


def detect_meta(source: Path) -> Path | None:
    for candidate in (source.with_suffix(".meta.md"), source.parent / "meta.md"):
        if candidate.is_file():
            return candidate
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", type=Path, help="Caption/transcript file")
    ap.add_argument("--meta", type=Path, help="meta.md (default: auto-detect beside source)")
    ap.add_argument("-o", "--output", type=Path, help="Output markdown (default: stdout)")
    args = ap.parse_args()

    caption = Caption.read(args.source)
    sups = caption.supervisions
    duration = max((s.end for s in sups), default=0.0)

    meta_path = args.meta or detect_meta(args.source)
    meta_text = load_meta(meta_path) if meta_path else ""

    lines: list[str] = []
    lines.append("# Source")
    lines.append(
        f"- file: `{args.source}`   - language: {caption.language or 'unknown'}"
        f"   - duration: {fmt_ts(duration)}   - segments: {len(sups)}"
    )
    lines.append("")

    if meta_text:
        lines.append("## Meta")
        lines.append("")
        lines.append(meta_text.rstrip())
        lines.append("")
        if has_chapters_block(meta_text):
            lines.append("> **HARD CONSTRAINT**: use the chapter titles and timestamps above verbatim.")
            lines.append("> Do not merge, split, reorder, or rename them.")
            lines.append("")

    lines.append("# Transcript")
    lines.append("")
    for sup in sups:
        ts = fmt_ts(sup.start)
        text = (sup.text or "").replace("\n", " ").strip()
        if sup.speaker:
            lines.append(f"[{ts}] {sup.speaker}: {text}")
        else:
            lines.append(f"[{ts}] {text}")

    body = "\n".join(lines) + "\n"
    if args.output:
        args.output.write_text(body, encoding="utf-8")
        print(f"Wrote prompt input → {args.output}")
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
