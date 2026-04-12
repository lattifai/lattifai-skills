#!/usr/bin/env python3
"""Read a caption file and emit agent-ready translation chunks as JSON.

Output schema (stdout or --output):
    {
      "source_path": "<src>",
      "source_format": "srt",
      "language": "en",
      "total_segments": 123,
      "chunk_size": 30,
      "chunks": [
        {
          "chunk_id": 0,
          "items": [
            {"idx": 0, "text": "...", "speaker": "Alice",
             "start": 0.0, "end": 2.5},
            ...
          ]
        },
        ...
      ]
    }

The agent translates each item, producing a companion file with `{idx, translation}`
entries that `merge.py` writes back into the source format.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lattifai.caption import Caption


def build_chunks(supervisions, chunk_size: int) -> list[dict]:
    chunks = []
    current: list[dict] = []
    chunk_id = 0
    for idx, sup in enumerate(supervisions):
        item = {
            "idx": idx,
            "text": sup.text or "",
            "start": round(sup.start, 4),
            "end": round(sup.end, 4),
        }
        if sup.speaker:
            item["speaker"] = sup.speaker
        current.append(item)
        if len(current) >= chunk_size:
            chunks.append({"chunk_id": chunk_id, "items": current})
            chunk_id += 1
            current = []
    if current:
        chunks.append({"chunk_id": chunk_id, "items": current})
    return chunks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", type=Path, help="Caption file (SRT, VTT, JSON, ASS, …)")
    ap.add_argument("--chunk-size", type=int, default=30, help="Segments per chunk (default 30)")
    ap.add_argument("-o", "--output", type=Path, help="Output JSON path (default: stdout)")
    args = ap.parse_args()

    caption = Caption.read(args.source)
    payload = {
        "source_path": str(args.source.resolve()),
        "source_format": caption.source_format,
        "language": caption.language,
        "total_segments": len(caption.supervisions),
        "chunk_size": args.chunk_size,
        "chunks": build_chunks(caption.supervisions, args.chunk_size),
    }

    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(out, encoding="utf-8")
        print(f"Wrote {payload['total_segments']} segments in {len(payload['chunks'])} chunks → {args.output}")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
