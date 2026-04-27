#!/usr/bin/env python3
"""Merge agent-produced translations back into a caption file.

Expected `translated.json` shape (produced by the agent):

    {
      "target_lang": "zh",
      "items": [
        {"idx": 0, "translation": "..."},
        {"idx": 1, "translation": "..."},
        ...
      ]
    }

Output modes (selected by `--bilingual`):
  * replace (default) — text is overwritten with the translation; output is a
    standalone target-language caption. Works in every format.
  * bilingual — source text is preserved and `translation` is attached;
    writers that support bilingual rendering (SRT, VTT, ASS, JSON) will emit
    two lines per segment.

Default output path: `<source_stem>_<LanguageName>.<ext>` next to the source.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lattifai.caption import Caption

LANG_NAMES = {
    "zh": "Chinese", "zh-CN": "Chinese", "zh-TW": "TraditionalChinese",
    "ja": "Japanese", "ko": "Korean",
    "en": "English", "fr": "French", "es": "Spanish", "de": "German",
    "pt": "Portuguese", "it": "Italian", "ru": "Russian", "ar": "Arabic",
    "hi": "Hindi", "nl": "Dutch", "vi": "Vietnamese", "th": "Thai",
    "id": "Indonesian", "tr": "Turkish", "pl": "Polish",
}


def default_output_path(source: Path, target_lang: str) -> Path:
    suffix = LANG_NAMES.get(target_lang, target_lang)
    return source.with_name(f"{source.stem}_{suffix}{source.suffix}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", type=Path, help="Original caption file")
    ap.add_argument("translated", type=Path, help="Agent-produced JSON with translation items")
    ap.add_argument("-o", "--output", type=Path, help="Output path (default: <stem>_<Lang>.<ext>)")
    ap.add_argument("--target-lang", help="Override target_lang from translated.json")
    ap.add_argument(
        "--bilingual",
        action="store_true",
        help="Keep source text and attach translation (dual-line renderers honor it)",
    )
    args = ap.parse_args()

    translated = json.loads(args.translated.read_text(encoding="utf-8"))
    items = translated.get("items") or []
    target_lang = args.target_lang or translated.get("target_lang")
    if not target_lang:
        print("error: target_lang missing (pass --target-lang or include it in translated.json)", file=sys.stderr)
        return 2

    by_idx: dict[int, str] = {}
    for item in items:
        idx = item.get("idx")
        tr = item.get("translation")
        if not isinstance(idx, int) or not isinstance(tr, str):
            print(f"error: bad item {item!r} — expected {{idx:int, translation:str}}", file=sys.stderr)
            return 2
        by_idx[idx] = tr

    caption = Caption.read(args.source)
    n = len(caption.supervisions)
    missing: list[int] = []
    for idx, sup in enumerate(caption.supervisions):
        tr = by_idx.get(idx)
        if tr is None or not tr.strip():
            missing.append(idx)
            continue
        # Defensive: drop the source-format raw-cue cache so that format
        # writers (notably the SRT writer's `_splice_raw_cue_texts`) don't
        # silently splice the cached source-only text back over our updated
        # `sup.text` / `sup.translation`. Without this, both `replace` and
        # `--bilingual` modes round-trip to a SRT that still shows only the
        # original source text — i.e. the translation work is dropped.
        if isinstance(getattr(sup, "custom", None), dict):
            sup.custom.pop("srt_raw_text", None)
        if args.bilingual:
            # Keep sup.text as the source; attach translation for bilingual renderers.
            sup.translation = tr
            sup.target_lang = target_lang
        else:
            # Replace source text with the translation; do not set translation field
            # (avoids bilingual output in writers that render both when present).
            sup.text = tr

    if missing:
        print(
            f"error: {len(missing)}/{n} segments have no translation "
            f"(first missing idx: {missing[:5]})",
            file=sys.stderr,
        )
        return 2

    if args.bilingual:
        caption.target_lang = target_lang
    else:
        caption.language = target_lang

    output = args.output or default_output_path(args.source, target_lang)
    caption.write(output)
    mode = "bilingual" if args.bilingual else "replace"
    print(f"Wrote {n} segments ({mode} mode, target_lang={target_lang}) → {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
