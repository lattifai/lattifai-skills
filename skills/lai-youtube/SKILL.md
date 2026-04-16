---
name: lai-youtube
description: One-command YouTube pipeline — downloads media, fetches or transcribes captions, and runs forced alignment. Trigger when the user provides a YouTube URL (youtube.com / youtu.be) and wants captions/subtitles, or says "align youtube", "下载YouTube字幕", "get captions from youtube".
allowed-tools: Read, Bash(lai:*), Bash(yt-dlp:*)
---

# YouTube Workflow

YouTube URL → aligned captions in one command. Requires an API key (`/lai-setup`) and `yt-dlp` (`pip install yt-dlp`).

## Basic Command

This command uses `nemo_run` config syntax (`key=value`), **not** `-o / --output`.

```bash
lai youtube align "https://youtu.be/VIDEO_ID" \
    caption.output.path=./output.srt \
    caption.output.format=srt
# shortcut:
lai-youtube "https://youtu.be/VIDEO_ID" caption.output.path=./output.srt
```

Add `-Y` (skip confirmation) for non-interactive runs. `caption.output.format` is inferred from the path suffix but passing it explicitly is safest. Supported: `srt`, `vtt`, `ass`, `json`, `ttml`, `lrc`, … (see `/lai-caption`).

### Pipeline steps

1. `yt-dlp` downloads media (saved to `media.output_dir`, default `./media`)
2. Fetch YouTube captions (or transcribe with Gemini if `use_transcription=true`)
3. Lattice-1 forced alignment
4. Write in the requested format

## Check What's Available First

```bash
yt-dlp --list-subs "URL"
```

- **Manual captions** → best quality, use defaults
- **Auto-captions only** → prefer `caption.input.split_sentence=true` (re-segments mid-sentence breaks). For karaoke / translation / summarization this is almost always a win. Only skip it when the user needs YouTube's original cue boundaries preserved (e.g., replacing an existing caption file)
- **No captions** → add `use_transcription=true` (needs a Gemini key — see `/lai-transcribe`)

## Common Options

All use `key=value` syntax, dot-nested:

- `use_transcription=true` — transcribe with Gemini instead of using YouTube captions
- `caption.input.split_sentence=true` — re-segment auto-captions into clean sentences (recommended for karaoke / translation)
- `caption.render.word_level=true` — per-word timestamps (needed for karaoke; pair with a JSON or ASS output)
- `caption.output.path=./out.json` / `caption.output.format=json` — output destination
- `media.prefer_audio=true` — audio-only download (faster, smaller)
- `media.output_dir=./downloads/` — where to save intermediate audio / vtt
- `media.streaming_chunk_secs=300` — long-video chunking

Full list: `lai youtube align --help`. Discover the full config tree with `lai youtube align --to-yaml /tmp/cfg.yaml URL` (exports and exits without running).

## Download Only (`lai youtube download`)

When you need just the media (no alignment), or want to manage the media + caption files yourself:

```bash
lai youtube download --direct -Y \
    yt_url="https://youtu.be/VIDEO_ID" \
    media.output_dir=./data/ \
    media.output_format=mp4 \
    media.prefer_audio=false
```

- `media.output_format`: `mp4` (default with `prefer_audio=false`), `mp3`, `wav`, …
- `only=meta` — re-download metadata only (writes `<id>.meta.md`, no media)

The downloaded files follow the pattern `<id>.mp4`, `<id>.en.vtt`, `<id>.meta.md` inside `media.output_dir`. Pipe the pair into `/lai-align` afterwards.

## Karaoke Recipe (end-to-end)

```bash
# Step 1 — YouTube → aligned JSON with word-level timestamps
lai youtube align -Y "https://youtu.be/VIDEO_ID" \
    caption.output.path=./aligned.json \
    caption.output.format=json \
    caption.input.split_sentence=true \
    caption.render.word_level=true

# Step 2 — JSON → ASS with per-word karaoke highlighting (see /lai-caption)
laicap-convert -Y ./aligned.json ./aligned.karaoke.ass \
    render.word_level=true \
    ass.karaoke_effect=sweep \
    ass.karaoke_color_scheme=azure-gold
```

For bilingual karaoke, run `/lai-translate` on `aligned.json` first (it preserves `words`), then run step 2 on the bilingual JSON.

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
