---
name: lai-diarize
description: Use when user needs speaker identification in audio/captions. Detects who speaks when, assigns speaker labels, and optionally infers speaker names from context. Use this skill whenever the user has a podcast, interview, meeting recording, or any multi-speaker audio and wants to know who said what. Also triggers on "diarize", "speaker detection", "说话人识别", "who is speaking", "add speaker labels", "区分说话人", "identify speakers", "which speaker said this", even if they just say "this podcast has two people, I need their names labeled".
allowed-tools: Read, Bash(lai:*)
---

# Speaker Diarization

Identify and label speakers in aligned captions. Uses pyannote.audio for
speaker detection and optional LLM-powered speaker name inference.

**CLI syntax note**: LattifAI uses `nemo_run` configuration syntax. Options use
`key=value` format (e.g., `diarization.infer_speakers=true`), NOT traditional
flags. This applies to all `lai` subcommands.

**Requires**: Aligned captions as input (run `/lai-align` first).

## When to Use

- Multi-speaker content (podcasts, interviews, meetings, panel discussions)
- Need to add speaker labels to aligned captions
- Want to identify who said what
- Speaker-aware downstream tasks (translation, summarization)

## When NOT to Use

- Single-speaker content (narration, audiobooks) -- speaker label not needed
- No aligned captions yet -- run `/lai-align` first
- Only need timing fixes -- use `/lai-align`
- Need transcription -- use `/lai-transcribe`

## Prerequisites

- Aligned captions with timing (from `/lai-align`)
- LattifAI API key (`lai auth whoami`)
- For speaker name inference: LLM backend configured
  ```bash
  lai config set diarization.infer_speakers true
  lai config set diarization.llm.model_name gemini-2.5-flash
  ```

## CLI Usage

### Basic Diarization

```bash
lai diarize run audio.mp3 aligned.json diarized.json
```

Shortcut:

```bash
lai-diarize audio.mp3 aligned.json diarized.json
```

### With Context (Speaker Hints)

Provide context via a `.meta.md` file or inline string for better speaker
identification:

```bash
# From meta.md file (YAML frontmatter with speakers, title, channel)
lai diarize run podcast.mp3 aligned.json diarized.json \
    context=episode.meta.md

# Inline context string
lai diarize run podcast.mp3 aligned.json diarized.json \
    context="Host: Alice Chen (tech journalist), Guest: Bob Smith (AI researcher)"
```

### With Speaker Name Inference

LLM analyzes the conversation to infer speaker names from context:

```bash
lai diarize run podcast.mp3 aligned.json diarized.json \
    diarization.infer_speakers=true
```

Requires an LLM backend:
```bash
lai config set diarization.llm.model_name gemini-2.5-flash
lai config set GEMINI_API_KEY your-key
```

### Specify Number of Speakers

If you know the exact speaker count:

```bash
lai diarize run meeting.mp3 aligned.json diarized.json \
    diarization.num_speakers=3
```

## Parameters

| Parameter | CLI Syntax | Default | Description |
|-----------|-----------|---------|-------------|
| Input media | positional arg 1 | required | Audio or video file |
| Input caption | positional arg 2 | required | Aligned caption file |
| Output | positional arg 3 | auto | Output file path |
| Context | `context=file_or_string` | none | Speaker hints (meta.md or inline) |
| Num speakers | `diarization.num_speakers=N` | auto | Known speaker count |
| Infer speakers | `diarization.infer_speakers=true` | `false` | LLM name inference |
| Min speakers | `diarization.min_speakers=N` | 1 | Minimum expected speakers |
| Max speakers | `diarization.max_speakers=N` | 10 | Maximum expected speakers |
| LLM model | `diarization.llm.model_name=X` | from config | LLM for inference |

## Context File Format (meta.md)

The `context` parameter accepts a `.meta.md` file with YAML frontmatter:

```yaml
---
title: "Deep Dive into LLMs"
channel: "Tech Podcast"
speakers:
  - name: Alice Chen
    role: host
  - name: Bob Smith
    role: guest
---
Discussion about large language models, training techniques,
and the future of AI.
```

The diarizer uses this to:
- Match detected speakers to known names
- Use title/description as context for name inference
- Preserve speaker roles in output

## Output Contract

Output JSON preserves all source fields plus adds `speaker`:

```json
{
  "supervisions": [
    {
      "text": "Welcome to the show.",
      "start": 0.0,
      "end": 2.5,
      "speaker": "Alice Chen"
    },
    {
      "text": "Thanks for having me.",
      "start": 3.0,
      "end": 5.1,
      "speaker": "Bob Smith"
    }
  ]
}
```

Speaker labels follow these conventions:
- With name inference: actual names (`Alice Chen`, `Bob Smith`)
- Without inference: generic labels (`SPEAKER_00`, `SPEAKER_01`)
- With context: matched to provided names where possible

### Speaker Label Preservation

If input captions already have speaker labels (from transcription), the
diarizer recognizes and preserves common formats:
- `[Alice]` prefix
- `>> Bob:` prefix
- `SPEAKER_01:` prefix

Matched speakers keep their original labels; new speakers get assigned labels.

## Workflow

### Step 1 -- Verify inputs

Confirm user has:
1. Audio/video file
2. Aligned caption file (from `/lai-align`)

If no aligned captions, guide user to run `/lai-align` first.

### Step 2 -- Gather context (optional but recommended)

Ask user:
- How many speakers? (if known)
- Speaker names/roles? (if known)
- Is there a meta.md file?

Better context = better speaker identification.

### Step 3 -- Configure LLM (if name inference needed)

```bash
lai config get diarization.llm.model_name
```

If not set and user wants name inference:
```bash
lai config set diarization.llm.model_name gemini-2.5-flash
lai config set GEMINI_API_KEY your-key
```

### Step 4 -- Run diarization

```bash
lai diarize run <audio> <aligned_caption> <output> [options]
```

### Step 5 -- Review speaker assignments

Check the output for correct speaker attribution. Common issues:
- Speakers confused in overlapping speech
- Short utterances misattributed
- Speaker count wrong (too many splits or too few)

## Error Handling

| Condition | Action |
|-----------|--------|
| No aligned segments | Input must have timing. Run `/lai-align` first |
| LLM not configured for inference | Guide user to set `diarization.llm.model_name` |
| Too many speakers detected | Set `diarization.max_speakers=N` |
| Speaker names not inferred | Provide context via `context=` parameter |
| Audio format error | Convert to WAV/MP3/M4A first |

## Related Skills

| Skill | Use When |
|-------|----------|
| `/lai-align` | Need aligned captions before diarization |
| `/lai-transcribe` | Need transcript from scratch |
| `/lai-translate` | Translate diarized captions |
| `/lai-summarize` | Summarize with speaker attribution |
| `/lai-youtube` | Full YouTube pipeline |

### Common Workflow Chains

```bash
# Full pipeline: Transcribe -> Align -> Diarize
lai transcribe run podcast.mp3 transcript.json
lai alignment align podcast.mp3 transcript.json aligned.json
lai diarize run podcast.mp3 aligned.json diarized.json \
    diarization.infer_speakers=true

# YouTube -> Align -> Diarize
lai youtube align "https://youtu.be/xxx" -o aligned.json
lai diarize run video.mp4 aligned.json diarized.json \
    context=video.meta.md
```

## Non-Goals

- Does NOT transcribe audio -- use `/lai-transcribe`
- Does NOT align captions -- use `/lai-align`
- Does NOT perform voice cloning or speaker verification
- Does NOT work on unaligned (no timing) text
- Does NOT guarantee 100% accuracy on overlapping speech
