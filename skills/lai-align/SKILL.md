---
name: lai-align
description: Use when user needs accurate/precise caption timing, or aligning captions with audio/video using forced alignment. Corrects caption timing to match actual speech. Uses LattifAI Lattice-1 model. Triggers on "align captions", "fix timing", "forced alignment", "对齐字幕", "校准时间轴", or when user has both audio and text that need synchronization.
allowed-tools: Read, Bash(lai:*)
---

# LattifAI Forced Alignment

Precision audio-text forced alignment powered by the Lattice-1 model. Produces
word-level and segment-level timestamps with sub-frame accuracy.

**Requires LattifAI API Key** -- get one free via `lai auth trial` (see `/lai-setup`).

## When to Use

- **Precise timing needed** -- user requests accurate timestamps or precise alignment
- **Sync misaligned captions** -- fix timing drift in downloaded or auto-generated captions
- **Align manual transcripts** -- match hand-written text to speech precisely
- **Post-transcription alignment** -- improve coarse timestamps from ASR output
- **Word-level timestamps** -- need per-word timing for karaoke, highlighting, or TTS
- **Multi-format input** -- SRT, VTT, ASS, TXT, MD, JSON, TextGrid, TSV, and 20+ more

## When NOT to Use

- No existing text/transcript -- use `/lai-transcribe` first to generate one
- Only need format conversion -- use `/lai-caption` instead
- Need speaker identification -- use `/lai-diarize` after alignment
- Very short clips (<3 seconds) -- alignment needs sufficient audio context

## Prerequisites

```bash
lai doctor  # Verify environment
lai auth whoami  # Verify API key
```

If not set up, run `/lai-setup` first.

## CLI Usage

### Basic Alignment

```bash
lai alignment align audio.wav caption.srt output.srt
```

Shortcut form:

```bash
lai-align audio.wav caption.srt output.srt
```

### Word-Level Timestamps

```bash
lai alignment align audio.mp3 caption.srt output.json \
    caption.render.word_level=true
```

Word-level output is best in JSON format (preserves per-word timing data):

```json
{
  "supervisions": [
    {
      "text": "Hello world",
      "start": 0.0,
      "end": 2.5,
      "alignment": [
        {"word": "Hello", "start": 0.0, "end": 0.5},
        {"word": "world", "start": 0.6, "end": 2.5}
      ]
    }
  ]
}
```

### Smart Sentence Segmentation

For word-level or poorly segmented input (e.g., YouTube VTT):

```bash
lai alignment align video.mp4 caption.vtt output.srt \
    caption.input.split_sentence=true
```

Uses `wtpsplit` AI model to re-segment into natural sentences. Especially
useful for YouTube auto-captions where segments break mid-sentence.

### Long Audio (Streaming Mode)

For audio longer than 10 minutes, enable streaming to limit memory usage:

```bash
lai alignment align long_podcast.mp3 transcript.srt output.srt \
    media.streaming_chunk_secs=300
```

Supports audio up to 20 hours. Default chunk: 300 seconds (5 minutes).

## Parameters

| Parameter | CLI Syntax | Default | Description |
|-----------|-----------|---------|-------------|
| Input media | positional arg 1 | required | Audio or video file path |
| Input caption | positional arg 2 | required | Caption/transcript file path |
| Output caption | positional arg 3 | required | Output file path (format from extension) |
| Word-level | `caption.render.word_level=true` | `false` | Include per-word timestamps |
| Split sentence | `caption.input.split_sentence=true` | `false` | AI sentence re-segmentation |
| Streaming | `media.streaming_chunk_secs=N` | off | Chunk size for long audio (seconds) |
| Include speaker | `caption.render.include_speaker_in_text=true` | `false` | Embed speaker labels in text |
| Normalize text | `caption.input.normalize_text=true` | `false` | Normalize input text before alignment |
| API key | `client.api_key=xxx` | from config | Override API key |
| Device | `alignment.device=cuda` | auto | Force device (cuda/mps/cpu) |

## Supported Formats

**Input** (auto-detected from extension/content):

| Format | Extensions |
|--------|-----------|
| SubRip | `.srt` |
| WebVTT | `.vtt` |
| ASS/SSA | `.ass`, `.ssa` |
| Plain text | `.txt` |
| Markdown (Gemini) | `.md` |
| JSON | `.json` |
| TextGrid (Praat) | `.TextGrid` |
| TSV/CSV | `.tsv`, `.csv` |
| Audacity | `.aud` |
| LRC (lyrics) | `.lrc` |
| TTML | `.ttml`, `.xml` |
| And 15+ more | See `lai alignment align --help` |

**Output**: Same formats as input. Format is inferred from output file extension.

**Recommended output format**: JSON (preserves word-level timing for downstream use).
Convert to other formats later with `/lai-caption`.

## Workflow

### Step 1 -- Verify setup

```bash
lai auth whoami
```

If not authenticated, guide user through `/lai-setup`.

### Step 2 -- Identify inputs

Determine:
1. **Audio/video file** -- the media source
2. **Caption/transcript file** -- the text to align
3. **Desired output format** -- SRT for playback, JSON for downstream processing

### Step 3 -- Decide options

| Scenario | Recommended Options |
|----------|-------------------|
| YouTube auto-captions (word-level VTT) | `caption.input.split_sentence=true` |
| Long podcast (>10 min) | `media.streaming_chunk_secs=300` |
| Need per-word timing | `caption.render.word_level=true`, output as `.json` |
| Multi-speaker content | Align first, then `/lai-diarize` |
| Want ASS with styling | Output as `.json` first, then `/lai-caption` to convert |

### Step 4 -- Run alignment

```bash
lai alignment align <audio> <caption> <output> [options]
```

### Step 5 -- Verify output

Read the first few segments of the output to confirm timing looks correct.
For JSON output, check that `start`/`end` values are reasonable.

## Output Contract

The output preserves all input text content. Only timestamps change.

- **Segment-level**: Each caption segment gets precise `start` and `end` timestamps
- **Word-level** (when enabled): Each word within a segment gets its own `start`/`end`
- **Speaker labels**: Preserved from input if present
- **Non-speech events**: `[MUSIC]`, `[APPLAUSE]` etc. are preserved with timing

## Error Handling

| Condition | Action |
|-----------|--------|
| `API KEY verification error` | Key invalid/expired. Run `lai auth whoami` to check, then `lai auth login` or `lai auth trial` |
| `No segments found` | Input caption is empty or unreadable. Check file format |
| `Audio format error` | Convert to WAV/MP3/M4A first: `ffmpeg -i input.xxx -ar 16000 output.wav` |
| `CUDA out of memory` | Add `alignment.device=cpu` or reduce `media.streaming_chunk_secs` |
| `Model download failed` | Check network. Model auto-downloads from HuggingFace on first run |
| Timing looks wrong | Try `caption.input.normalize_text=true` or `caption.input.split_sentence=true` |

## Related Skills

| Skill | Use When |
|-------|----------|
| `/lai-setup` | Need to install or authenticate first |
| `/lai-transcribe` | No transcript exists yet -- generate one |
| `/lai-diarize` | Need speaker labels after alignment |
| `/lai-caption` | Convert aligned output to another format |
| `/lai-youtube` | Working with YouTube videos (download + align combined) |
| `/lai-translate` | Translate aligned captions to another language |

### Common Workflow Chains

```bash
# Transcribe then align (most common)
lai transcribe run video.mp4 transcript.json
lai alignment align video.mp4 transcript.json aligned.json

# Align then convert to multiple formats
lai alignment align audio.mp3 caption.srt aligned.json caption.render.word_level=true
laicap-convert aligned.json aligned.srt
laicap-convert aligned.json aligned.vtt
laicap-convert aligned.json aligned.ass

# Align then diarize
lai alignment align podcast.mp3 transcript.srt aligned.json
lai diarize run podcast.mp3 aligned.json diarized.json
```

## Non-Goals

- Does NOT generate transcripts -- use `/lai-transcribe` for that
- Does NOT identify speakers -- use `/lai-diarize` after alignment
- Does NOT translate text -- use `/lai-translate` for translation
- Does NOT download media -- use `/lai-youtube` or `/lai-caption` for downloads
- Does NOT modify caption text content -- only timestamps change
