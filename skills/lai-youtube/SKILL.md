---
name: lai-youtube
description: Use when processing YouTube videos -- downloads media and aligns captions in one step. Handles YouTube URL input, optional transcription, and caption download. Triggers on "YouTube", "youtube url", "处理YouTube视频", "align youtube", or when user provides a YouTube URL for caption work.
allowed-tools: Read, Bash(lai:*), Bash(yt-dlp:*)
---

# YouTube Workflow

One-command pipeline: YouTube URL to precisely aligned captions. Downloads
media, fetches or generates captions, and runs forced alignment.

**Requires LattifAI API Key** -- get one free via `lai auth trial`.

## When to Use

- User provides a YouTube URL and wants aligned captions
- Need to download + align YouTube captions in one step
- Want to transcribe a YouTube video (Gemini accepts URLs natively)
- Processing YouTube content for subtitle creation or editing

## When NOT to Use

- Already have downloaded media + captions -- use `/lai-align` directly
- Only need to download video/audio -- use `yt-dlp` directly
- Need to transcribe non-YouTube content -- use `/lai-transcribe`
- Working with local files only

## Prerequisites

- LattifAI installed and authenticated (`lai auth whoami`)
- `yt-dlp` installed for media download (`pip install yt-dlp`)
- For transcription mode: `GEMINI_API_KEY` configured

## CLI Usage

### Basic YouTube Alignment

Downloads YouTube captions and aligns them with the audio:

```bash
lai youtube align "https://www.youtube.com/watch?v=VIDEO_ID" -o output.json
```

Shortcut:

```bash
lai-youtube "https://youtu.be/VIDEO_ID" -o output.srt
```

### With Transcription (No Existing Captions)

If the video has no captions, use Gemini to transcribe:

```bash
lai youtube align "https://youtu.be/xxx" -o output.json \
    use_transcription=true
```

### Output Format Options

```bash
# JSON (recommended -- preserves word-level timing)
lai youtube align "URL" -o output.json caption.render.word_level=true

# SRT
lai youtube align "URL" -o output.srt

# VTT
lai youtube align "URL" -o output.vtt

# ASS with styling
lai youtube align "URL" -o output.ass
```

### Audio-Only Download

Download audio instead of video (faster, smaller):

```bash
lai youtube align "URL" -o output.json \
    media.prefer_audio=true
```

### Specify Output Directory

```bash
lai youtube align "URL" \
    media.output_dir=./downloads/
```

### With Sentence Segmentation

For YouTube auto-captions that break mid-sentence:

```bash
lai youtube align "URL" -o output.srt \
    caption.input.split_sentence=true
```

### Streaming Mode for Long Videos

```bash
lai youtube align "URL" -o output.json \
    media.streaming_chunk_secs=300
```

## Parameters

| Parameter | CLI Syntax | Default | Description |
|-----------|-----------|---------|-------------|
| YouTube URL | positional arg 1 | required | YouTube video URL |
| Output | `-o` / `media.output_path` | auto | Output file path |
| Transcription | `use_transcription=true` | `false` | Use Gemini instead of YouTube captions |
| Prefer audio | `media.prefer_audio=true` | `false` | Download audio-only |
| Output dir | `media.output_dir=path` | current dir | Where to save files |
| Word-level | `caption.render.word_level=true` | `false` | Per-word timestamps |
| Split sentence | `caption.input.split_sentence=true` | `false` | AI re-segmentation |
| Streaming | `media.streaming_chunk_secs=N` | off | Long video chunking |
| Force overwrite | `media.force_overwrite=true` | `false` | Overwrite existing files |
| Audio track | `media.audio_track_id=original` | `original` | Audio track selection |
| Quality | `media.quality=best` | `best` | Download quality |

## Workflow

### Step 1 -- Check for existing captions

Before downloading and transcribing, check what's available:

```bash
yt-dlp --list-subs "URL"
```

- **Has manual captions** -> Best quality. Proceed with default YouTube alignment.
- **Has auto-captions only** -> Usable but noisy. Consider `caption.input.split_sentence=true`.
- **No captions at all** -> Use `use_transcription=true` for Gemini transcription.

### Step 2 -- Run the pipeline

```bash
lai youtube align "URL" -o output.json [options]
```

The command automatically:
1. Downloads media (audio or video)
2. Fetches YouTube captions OR transcribes with Gemini
3. Runs Lattice-1 forced alignment
4. Writes output in the specified format

### Step 3 -- Review and follow up

Check the output. Common next steps:

| Need | Action |
|------|--------|
| Speaker labels | `/lai-diarize` on the aligned output |
| Translation | `/lai-translate` for agent-driven translation |
| Different format | `/lai-caption` to convert |
| Summary | `/lai-summarize` for content summary |

## Pipeline Internals

The YouTube workflow executes these steps internally:

```
YouTube URL
  -> yt-dlp download (audio/video)
  -> Caption fetch (YouTube captions OR Gemini transcription)
  -> Lattice-1 forced alignment
  -> Output in requested format
```

Media is saved to `media.output_dir` (default: current directory).
Intermediate files (downloaded media, raw captions) are preserved for reuse.

## Error Handling

| Condition | Action |
|-----------|--------|
| `yt-dlp` not installed | `pip install yt-dlp` |
| Video unavailable / private | Check URL. Video must be publicly accessible. |
| No captions and no Gemini key | Set `GEMINI_API_KEY` or download captions manually |
| API key invalid | Run `lai auth whoami`, then `lai auth login` if needed |
| Download timeout | Retry. Or download manually with `yt-dlp` then use `/lai-align` |
| Region-restricted video | Use a VPN or download from an unrestricted region |
| Age-restricted video | Download manually with `yt-dlp --cookies-from-browser chrome` |

## Related Skills

| Skill | Use When |
|-------|----------|
| `/lai-setup` | Need to install or authenticate first |
| `/lai-align` | Already have media + captions (skip download) |
| `/lai-transcribe` | Need transcription only (no alignment) |
| `/lai-diarize` | Add speaker labels after YouTube alignment |
| `/lai-translate` | Translate YouTube captions |
| `/lai-caption` | Convert output format |
| `/lai-summarize` | Summarize YouTube content |

### Common Workflow Chains

```bash
# Quick YouTube to SRT
lai youtube align "https://youtu.be/xxx" -o video.srt

# YouTube + Diarize + Translate
lai youtube align "URL" -o aligned.json
lai diarize run video.mp4 aligned.json diarized.json
# Then /lai-translate for agent-driven translation

# YouTube with transcription (no existing captions)
lai youtube align "URL" -o aligned.json \
    use_transcription=true \
    caption.input.split_sentence=true

# YouTube to bilingual ASS
lai youtube align "URL" -o aligned.json caption.render.word_level=true
laicap-convert aligned.json aligned.srt
# Then /lai-translate for translation, then:
laicap-convert translated.srt bilingual.ass --style bilingual
```

## Non-Goals

- Does NOT support non-YouTube video platforms (Vimeo, Bilibili, etc.)
- Does NOT edit or trim downloaded videos
- Does NOT generate thumbnails or metadata
- Does NOT upload or publish content
- Does NOT handle playlists -- process one URL at a time
