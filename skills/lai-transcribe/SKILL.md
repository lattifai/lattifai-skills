---
name: lai-transcribe
description: Use when transcribing audio/video to text with timestamps. Supports YouTube URLs, local files, multiple ASR models (Gemini, Parakeet, SenseVoice). Use this skill whenever the user has audio or video and needs text output, mentions speech-to-text, wants captions generated from scratch, or asks to "get the text from this video/audio". Also triggers on "transcribe", "转录", "语音转文字", "generate transcript", "ASR", "speech to text", "听写", "我有个音频需要出文字", even if they just provide an audio file path and say "I need captions for this".
allowed-tools: Read, Bash(lai:*)
---

# LattifAI Transcription

Multi-model automatic speech recognition (ASR) producing timestamped transcripts.

**CLI syntax note**: LattifAI uses `nemo_run` configuration syntax. Options use
`key=value` format (e.g., `transcription.model_name=gemini-2.5-pro`), NOT
traditional flags. This applies to all `lai` subcommands.

## When to Use

- User has audio/video but no transcript or captions
- Need to generate text from speech
- YouTube video transcription (Gemini accepts URLs directly)
- Multi-language transcription needs
- Want structured output with timestamps and speaker detection

## When NOT to Use

- **Video has existing captions** -- download them first with `yt-dlp --list-subs`
- Need real-time / streaming transcription
- Only need to fix timing on existing text -- use `/lai-align`
- Want translation, not transcription -- use `/lai-translate`

## Prerequisites

- LattifAI installed (`lai --version`)
- For **Gemini models**: `GEMINI_API_KEY` required
  ```bash
  lai config set GEMINI_API_KEY your-key-here
  ```
  Get a key from https://aistudio.google.com/apikey
- For **local models** (Parakeet, SenseVoice): GPU recommended, additional deps needed

## Models

| Model | Languages | Speed | Quality | Requires |
|-------|-----------|-------|---------|----------|
| `gemini-2.5-flash` | 100+ | Fast | High | Gemini API key |
| `gemini-2.5-pro` | 100+ | Medium | Highest | Gemini API key |
| `nvidia/parakeet-tdt-0.6b-v3` | 24 | Fast (local) | High | GPU + nemo_toolkit |
| `FunAudioLLM/SenseVoiceSmall` | 5 (zh/en/ja/ko/cantonese) | Fast (local) | High | GPU |

Default: `gemini-2.5-flash` (fastest, broadest language coverage).

## CLI Usage

### Basic Transcription

```bash
lai transcribe run audio.wav output.srt
```

Shortcut:

```bash
lai-transcribe audio.wav output.srt
```

### YouTube URL (Gemini Native)

Gemini accepts YouTube URLs directly -- no download needed:

```bash
lai transcribe run "https://www.youtube.com/watch?v=VIDEO_ID" output.json
```

### Specify Model

```bash
# Gemini Pro (highest quality)
lai transcribe run audio.mp4 output.srt \
    transcription.model_name=gemini-2.5-pro

# Local Parakeet (no API key needed, GPU recommended)
lai transcribe run audio.wav output.srt \
    transcription.model_name=nvidia/parakeet-tdt-0.6b-v3

# SenseVoice (optimized for zh/en/ja/ko)
lai transcribe run audio.wav output.srt \
    transcription.model_name=FunAudioLLM/SenseVoiceSmall
```

### Force Language

```bash
lai transcribe run audio.mp4 output.srt \
    transcription.language=zh
```

### Specify Output Directory

```bash
lai transcribe run audio.mp4 output_dir/
```

Output file auto-named based on input: `output_dir/audio_GeminiUnd.json`

## Parameters

| Parameter | CLI Syntax | Default | Description |
|-----------|-----------|---------|-------------|
| Input | positional arg 1 | required | Audio/video file or YouTube URL |
| Output | positional arg 2 | auto | Output path (file or directory) |
| Model | `transcription.model_name=X` | `gemini-2.5-flash` | ASR model |
| Language | `transcription.language=X` | auto-detect | Force language code |
| Gemini key | `transcription.gemini_api_key=X` | from config | Override Gemini API key |
| Device | `transcription.device=cuda` | auto | For local models |
| Streaming | `media.streaming_chunk_secs=N` | off | Chunk long audio |

## Output Formats

Output format is inferred from the file extension:

| Extension | Format | Best For |
|-----------|--------|----------|
| `.json` | JSON with full metadata | Downstream processing (alignment, diarization) |
| `.srt` | SubRip | Video players, simple editing |
| `.vtt` | WebVTT | Web playback |
| `.ass` | Advanced SubStation | Styled subtitles |
| `.txt` | Plain text | Reading, simple export |

**Recommended**: Use `.json` for downstream processing (alignment, diarization).
Convert to other formats later with `/lai-caption`.

## Workflow

### Step 1 -- Check for existing captions

For YouTube videos, check if captions already exist:

```bash
yt-dlp --list-subs "URL"
```

If captions exist, downloading them is faster and often higher quality than
re-transcribing. Use `yt-dlp` to download, then `/lai-align` to fix timing.

### Step 2 -- Verify API key

For Gemini models:
```bash
lai config get GEMINI_API_KEY
```

If not set, guide user to get one from https://aistudio.google.com/apikey

### Step 3 -- Choose model

| Scenario | Recommended Model |
|----------|------------------|
| Quick transcription, any language | `gemini-2.5-flash` (default) |
| Highest quality, cost no concern | `gemini-2.5-pro` |
| Offline / no API key | `nvidia/parakeet-tdt-0.6b-v3` |
| Chinese/Japanese/Korean focus | `FunAudioLLM/SenseVoiceSmall` |

### Step 4 -- Run transcription

```bash
lai transcribe run <input> <output> [options]
```

### Step 5 -- Review output

Check first few segments for accuracy. If timing is coarse, follow up with
`/lai-align` for precision timing.

## Error Handling

| Condition | Action |
|-----------|--------|
| `GEMINI_API_KEY not set` | `lai config set GEMINI_API_KEY your-key` |
| Empty response | Check audio format (mp3/mp4/wav/m4a/webm supported) |
| Upload timeout | File too large (>2GB for Gemini). Split audio first |
| Wrong language detected | Force with `transcription.language=en` |
| Local model OOM | Reduce audio length or use Gemini API instead |
| YouTube URL fails | Try downloading audio first with `yt-dlp`, then transcribe locally |

## Related Skills

| Skill | Use When |
|-------|----------|
| `/lai-align` | Improve transcription timing with forced alignment |
| `/lai-diarize` | Add speaker labels to transcription |
| `/lai-translate` | Translate transcription to another language |
| `/lai-caption` | Convert output format |
| `/lai-youtube` | Full YouTube pipeline (download + align in one step) |
| `/lai-summarize` | Generate summary from transcription |

### Common Workflow Chains

```bash
# Transcribe + Align (best quality timestamps)
lai transcribe run video.mp4 transcript.json
lai alignment align video.mp4 transcript.json aligned.json

# Transcribe + Align + Diarize (full pipeline)
lai transcribe run podcast.mp3 transcript.json
lai alignment align podcast.mp3 transcript.json aligned.json
lai diarize run podcast.mp3 aligned.json diarized.json

# YouTube quick transcription
lai transcribe run "https://youtu.be/xxx" output.srt
```

## Non-Goals

- Does NOT fix timing on existing captions -- use `/lai-align`
- Does NOT identify speakers -- use `/lai-diarize`
- Does NOT translate -- use `/lai-translate`
- Does NOT download video/audio files -- use `yt-dlp` or `/lai-youtube`
- Does NOT handle real-time streaming audio
