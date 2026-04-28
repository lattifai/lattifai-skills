---
name: lai-align
description: Align existing captions to audio/video with word-level precision using the Lattice-1 model. Trigger when the user has both a media file AND a caption/transcript that need to be synchronized, or says "fix caption timing", "字幕对不上", "对齐字幕", "word-level timestamps", "karaoke timing", "timestamps are off". Do NOT trigger without existing text — use `/lai-transcribe` first.
allowed-tools: Read, Bash(lai:*)
---

# LattifAI Forced Alignment

Produces word-level and segment-level timestamps with sub-frame accuracy. Requires an API key — see `/lai-setup`.

## Basic Command

Positional args are `input_media`, `input_caption`, `output_caption`. Pick a `<base>` (the media stem or YouTube ID) and reuse it; outputs land in the current directory:

```bash
# <base> = podcast (from podcast.mp3)
lai alignment align podcast.mp3 podcast.srt podcast.aligned.json
# shortcut:
lai-align podcast.mp3 podcast.srt podcast.aligned.json
# or explicit key=value style (interchangeable, useful inside scripts):
lai alignment align --direct -Y \
    input_media=podcast.mp3 \
    input_caption=podcast.srt \
    output_caption=podcast.aligned.json \
    caption.input.split_sentence=false
```

Format is inferred from the output file extension (30+ formats — see `/lai-caption`). Add `--direct -Y` for non-interactive pipeline runs.

**Output naming**: prefer `<base>.aligned.json` for downstream pipelines (karaoke / translate / diarize all consume aligned JSON). Use `<base>.srt` etc. only when the alignment result is the final deliverable.

## Common Options

Append as `key=value` pairs:

- `caption.input.split_sentence=false` *(default in examples)* — preserve the source caption's original cue boundaries. Set to `true` to re-segment into natural sentences via wtpsplit; useful when the source has mid-sentence cue breaks (typical for YouTube auto-captions) and you want clean segments for downstream karaoke / translation / summarization
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
