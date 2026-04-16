---
name: lai-align
description: Align existing captions to audio/video with word-level precision using the Lattice-1 model. Trigger when the user has both a media file AND a caption/transcript that need to be synchronized, or says "fix caption timing", "字幕对不上", "对齐字幕", "word-level timestamps", "karaoke timing", "timestamps are off". Do NOT trigger without existing text — use `/lai-transcribe` first.
allowed-tools: Read, Bash(lai:*)
---

# LattifAI Forced Alignment

Produces word-level and segment-level timestamps with sub-frame accuracy. Requires an API key — see `/lai-setup`.

## Basic Command

Positional args are `input_media`, `input_caption`, `output_caption`. Both shorthand styles work:

```bash
lai alignment align audio.wav caption.srt output.srt
# shortcut:
lai-align audio.wav caption.srt output.srt
# or explicit key=value style (interchangeable, useful inside scripts):
lai alignment align --direct -Y \
    input_media=audio.wav \
    input_caption=caption.srt \
    output_caption=output.json \
    caption.input.split_sentence=true
```

Format is inferred from the output file extension (30+ formats — see `/lai-caption`). Add `--direct -Y` for non-interactive pipeline runs.

## Common Options

Append as `key=value` pairs:

- `caption.input.split_sentence=true` — re-segment into natural sentences (wtpsplit). **Recommended for YouTube auto-captions, karaoke, translation, and summarization** (clean sentence boundaries almost always improve the result). Skip it only when the user explicitly needs the source file's original cue boundaries preserved (e.g., re-aligning a hand-crafted SRT for broadcast)
- `caption.render.word_level=true` — keep per-word timestamps in the output (needed for karaoke; use a JSON or ASS output path)
- `media.streaming_chunk_secs=300` — process audio >10 min with bounded memory (up to 20 h)
- `alignment.device=auto` — override auto device (cuda/mps/cpu)

Full list: `lai alignment align --help`.

## Word-Level JSON Output

```json
{
  "supervisions": [{
    "text": "Hello world",
    "start": 0.0,
    "end": 2.5,
    "words": [
      {"word": "Hello", "start": 0.0, "end": 0.5},
      {"word": "world", "start": 0.6, "end": 2.5}
    ]
  }]
}
```

Fan out to other formats (karaoke ASS, TextGrid, SRT, …) via `/lai-caption`.

## Common Issues

| Problem | Fix |
|---------|-----|
| `API KEY verification error` | Run `lai auth trial` or `lai auth login` — see `/lai-setup` |
| Timing looks wrong | Try `caption.input.split_sentence=true` or `caption.input.normalize_text=true` |

## Related Skills

- `/lai-transcribe` — generate a transcript first
- `/lai-diarize` — add speaker labels to aligned output
- `/lai-caption` — convert aligned JSON to any format
- `/lai-youtube` — YouTube URL → aligned captions in one command
