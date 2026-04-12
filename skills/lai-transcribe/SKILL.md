---
name: lai-transcribe
description: Transcribe audio/video to timestamped captions with Gemini (100+ languages) or local Parakeet / SenseVoice models. Trigger on "transcribe", "speech to text", "转录", "语音转文字", "generate captions from audio", or when the user provides an audio/video file with no text. If the YouTube video already has captions, prefer `/lai-youtube`.
allowed-tools: Read, Bash(lai:*)
---

# LattifAI Transcription

Generates timestamped text from audio/video. Default is Gemini (fast, broad language coverage); local models run offline on GPU.

## Prerequisites

Gemini needs an API key (free at <https://aistudio.google.com/apikey>):

```bash
lai config set GEMINI_API_KEY <your-key>
```

## Basic Command

```bash
lai transcribe run audio.wav output.srt
# shortcut:
lai-transcribe audio.wav output.srt
```

Gemini accepts YouTube URLs directly — no download needed:

```bash
lai transcribe run "https://youtu.be/VIDEO_ID" output.json
```

## Models

| Model | Languages | Requires |
|-------|-----------|----------|
| `gemini-3-flash-preview` *(default)* | 100+ | Gemini API key |
| `gemini-3.1-pro-preview` | 100+, highest quality | Gemini API key |
| `nvidia/parakeet-tdt-0.6b-v3` | 24, offline | GPU + `nemo_toolkit` |
| `FunAudioLLM/SenseVoiceSmall` | zh / en / ja / ko / cantonese, offline | GPU |

Switch model:

```bash
lai transcribe run audio.mp4 output.srt transcription.model_name=gemini-3.1-pro-preview
```

## Common Options

- `transcription.language=zh` — force language (otherwise auto-detect)
- `media.streaming_chunk_secs=300` — chunk long audio
- Output format is inferred from extension: `.srt` / `.vtt` / `.ass` / `.json` / `.txt`. Use `.json` when you plan to follow up with `/lai-align`.

## Common Issues

| Problem | Fix |
|---------|-----|
| `GEMINI_API_KEY not set` | `lai config set GEMINI_API_KEY <your-key>` |
| Upload timeout / file >2 GB | Split the audio or switch to a local model |
| Wrong language detected | Force with `transcription.language=en` |
| Timestamps are coarse | Follow up with `/lai-align` |

## Related Skills

- `/lai-align` — sharpen timestamps after transcription
- `/lai-diarize` — add speaker labels
- `/lai-translate` — translate the transcript
- `/lai-youtube` — YouTube end-to-end (download + caption + align)
- `/lai-caption` — convert output format
