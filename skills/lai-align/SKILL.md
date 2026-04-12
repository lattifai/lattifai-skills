---
name: lai-align
description: Align existing captions to audio/video with word-level precision using the Lattice-1 model. Trigger when the user has both a media file AND a caption/transcript that need to be synchronized, or says "fix caption timing", "字幕对不上", "对齐字幕", "word-level timestamps", "karaoke timing", "timestamps are off". Do NOT trigger without existing text — use `/lai-transcribe` first.
allowed-tools: Read, Bash(lai:*)
---

# LattifAI Forced Alignment

Produces word-level and segment-level timestamps with sub-frame accuracy. Requires an API key — see `/lai-setup`.

## Basic Command

```bash
lai alignment align audio.wav caption.srt output.srt
# shortcut:
lai-align audio.wav caption.srt output.srt
```

Format is inferred from the output file extension (30+ formats — see `/lai-caption`).

## Common Options

Append as `key=value` pairs:

- `caption.input.split_sentence=true` — re-segment into natural sentences (wtpsplit). Useful for YouTube auto-captions that break mid-sentence. **Ask the user before enabling** — it rewrites segment boundaries and can hurt manually-crafted SRT/VTT
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
