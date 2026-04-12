---
name: lai-youtube
description: One-command YouTube pipeline — downloads media, fetches or transcribes captions, and runs forced alignment. Trigger when the user provides a YouTube URL (youtube.com / youtu.be) and wants captions/subtitles, or says "align youtube", "下载YouTube字幕", "get captions from youtube".
allowed-tools: Read, Bash(lai:*), Bash(yt-dlp:*)
---

# YouTube Workflow

YouTube URL → aligned captions in one command. Requires an API key (`/lai-setup`) and `yt-dlp` (`pip install yt-dlp`).

## Basic Command

```bash
lai youtube align "https://youtu.be/VIDEO_ID" -o output.srt
# shortcut:
lai-youtube "https://youtu.be/VIDEO_ID" -o output.srt
```

Output extension picks the format (`.srt`, `.vtt`, `.ass`, `.json` — see `/lai-caption`).

### Pipeline steps

1. `yt-dlp` downloads media
2. Fetch YouTube captions (or transcribe with Gemini if missing)
3. Lattice-1 forced alignment
4. Write in the requested format

## Check What's Available First

```bash
yt-dlp --list-subs "URL"
```

- **Manual captions** → best quality, use defaults
- **Auto-captions only** → consider `caption.input.split_sentence=true` (re-segments mid-sentence breaks). **Ask the user before enabling** — it rewrites segment boundaries
- **No captions** → add `use_transcription=true` (needs a Gemini key — see `/lai-transcribe`)

## Common Options

- `use_transcription=true` — transcribe with Gemini instead of using YouTube captions
- `caption.input.split_sentence=true` — re-segment auto-captions (**confirm with user first** — rewrites boundaries)
- `caption.render.word_level=true` — per-word timestamps (use `.json` output)
- `media.prefer_audio=true` — audio-only download (faster, smaller)
- `media.output_dir=./downloads/` — where to save intermediates
- `media.streaming_chunk_secs=300` — long-video chunking

Full list: `lai youtube align --help`.

## Common Issues

| Problem | Fix |
|---------|-----|
| `yt-dlp` not installed | `pip install yt-dlp` |
| Video private / unavailable | URL must be publicly accessible |
| No captions and no Gemini key | Set one up — see `/lai-transcribe` |
| Region-restricted | Use a VPN or fetch from an unrestricted region |
| Age-restricted | `yt-dlp --cookies-from-browser chrome` to download, then `/lai-align` |
| API key invalid | `/lai-setup` |

## Related Skills

- `/lai-setup` — first-time install and auth
- `/lai-align` — when media + captions are already local
- `/lai-transcribe` — transcribe without alignment (Gemini accepts YouTube URLs too)
- `/lai-diarize` — speaker labels on aligned output
- `/lai-translate` — translate captions
- `/lai-caption` — convert output format
