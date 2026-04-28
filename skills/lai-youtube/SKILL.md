---
name: lai-youtube
description: One-command YouTube pipeline — downloads media, fetches or transcribes captions, and runs forced alignment. Trigger when the user provides a YouTube URL (youtube.com / youtu.be) and wants captions/subtitles, or says "align youtube", "下载YouTube字幕", "get captions from youtube".
allowed-tools: Read, Bash(lai:*), Bash(yt-dlp:*)
---

# YouTube Workflow

YouTube URL → aligned captions in one command. Requires an API key (`/lai-setup`) and `yt-dlp` (`pip install yt-dlp`).

## File path convention

All outputs land in the **current directory** by default (no subdirectories). Use the YouTube **video ID** as `<base>` and chain pipeline files as `<base>.<derivation>.<ext>`:

```
<base>.mp4              # downloaded media
<base>.en.vtt           # YouTube auto-caption
<base>.meta.md          # metadata
<base>.aligned.json     # forced-alignment output (when caption.output.format=json)
<base>.srt              # final SRT (when caption.output.format=srt)
```

`<base>` is the YouTube ID (e.g. `la0CaZ2R8EY`); the agent extracts it from the URL.

## Basic Command

This command uses `nemo_run` config syntax (`key=value`), **not** `-o / --output`.

```bash
# `<base>` = la0CaZ2R8EY (the YouTube video ID)
lai youtube align "https://youtu.be/la0CaZ2R8EY" \
    caption.output.path=la0CaZ2R8EY.aligned.json \
    caption.output.format=json
# shortcut:
lai-youtube "https://youtu.be/la0CaZ2R8EY" caption.output.path=la0CaZ2R8EY.aligned.json
```

Add `-Y` (skip confirmation) for non-interactive runs. `caption.output.format` is inferred from the path suffix but passing it explicitly is safest. Supported: `srt`, `vtt`, `ass`, `json`, `ttml`, `lrc`, … (see `/lai-caption`).

### Pipeline steps

1. `yt-dlp` downloads media into the current directory by default (`media.output_dir=.`); files named `<video_id>.mp4` etc.
2. Fetch YouTube captions (or transcribe with Gemini if `use_transcription=true`)
3. Lattice-1 forced alignment
4. Write in the requested format

## Check What's Available First

```bash
yt-dlp --list-subs "URL"
```

- **Manual captions** → best quality, use defaults
- **Auto-captions only** → consider `caption.input.split_sentence=true` if the auto-captions break mid-sentence and you want cleaner segments for downstream karaoke / translation / summarization. Default in examples is `false` to preserve the source's original cue boundaries
- **No captions** → add `use_transcription=true` (needs a Gemini key — see `/lai-transcribe`)

## Common Options

All use `key=value` syntax, dot-nested:

- `use_transcription=true` — transcribe with Gemini instead of using YouTube captions
- `caption.input.split_sentence=false` *(default in examples)* — preserve source cue boundaries. Set to `true` to re-segment into clean sentences (helpful for messy auto-captions)
- `caption.render.word_level=true` — per-word timestamps (needed for karaoke; pair with a JSON or ASS output)
- `caption.output.path=<base>.aligned.json` / `caption.output.format=json` — output destination (use `<base>.<derivation>.<ext>` naming)
- `media.prefer_audio=true` — audio-only download (faster, smaller)
- `media.prefer_audio=false` — keep the video. **Pair with `media.output_format=mp4`** explicitly; `prefer_audio=false` alone may still emit audio-only output, which breaks downstream karaoke (no width/height for `probe_media.py`)
- `media.output_dir=.` — where downloaded audio / vtt land (default: current directory)
- `media.streaming_chunk_secs=300` — long-video chunking

Full list: `lai youtube align --help`. Discover the full config tree with `lai youtube align --to-yaml /tmp/cfg.yaml URL` (exports and exits without running).

## Download Only (`lai youtube download`)

When you need just the media (no alignment), or want to manage the media + caption files yourself:

```bash
lai youtube download --direct -Y \
    yt_url="https://youtu.be/la0CaZ2R8EY" \
    media.output_dir=. \
    media.output_format=mp4 \
    media.prefer_audio=false
```

- `media.output_format`: `mp4` (default with `prefer_audio=false`), `mp3`, `wav`, …
- `only=meta` — re-download metadata only (writes `<id>.meta.md`, no media)

The downloaded files follow the pattern `<id>.mp4`, `<id>.en.vtt`, `<id>.meta.md` inside `media.output_dir` (current directory by default). Pipe the pair into `/lai-align` afterwards.

## Karaoke Recipe (end-to-end)

`<base>` = YouTube video ID (e.g. `la0CaZ2R8EY`):

```bash
# Step 1 — YouTube → aligned JSON with word-level timestamps
lai youtube align -Y "https://youtu.be/la0CaZ2R8EY" \
    caption.output.path=la0CaZ2R8EY.aligned.json \
    caption.output.format=json \
    caption.input.split_sentence=false \
    caption.render.word_level=true

# Step 2 — JSON → ASS with per-word karaoke highlighting (see /lai-caption)
laicap-convert -Y la0CaZ2R8EY.aligned.json la0CaZ2R8EY.karaoke.ass \
    ass.karaoke_effect=sweep \
    ass.karaoke_color_scheme=azure-gold
```

(`render.word_level` is not needed on the convert side — it's default word-scope. The upstream `caption.render.word_level=true` in Step 1 is what populates the `words` arrays that karaoke reads.)

For bilingual karaoke, run `/lai-translate` on `la0CaZ2R8EY.aligned.json` first (it preserves `words`), then run step 2 on the bilingual JSON.

## Operational Tips

For long alignments (Step 3 lattice search can take minutes on long-form video), redirect to a log file so you can see EXIT code and stderr after truncation:

```bash
lai youtube align -Y URL caption.output.path=la0CaZ2R8EY.aligned.json ... > la0CaZ2R8EY.align.log 2>&1
echo "EXIT=$?"
tail -50 la0CaZ2R8EY.align.log
```

## Common Issues

| Problem | Fix |
|---------|-----|
| `yt-dlp` not installed | `pip install yt-dlp` |
| Video private / unavailable | URL must be publicly accessible |
| No captions and no Gemini key | Set one up — see `/lai-transcribe` |
| Region-restricted | Use a VPN or fetch from an unrestricted region |
| Age-restricted | `yt-dlp --cookies-from-browser chrome` to download, then `/lai-align` |
| API key invalid | `/lai-setup` |
| `media.prefer_audio=false` but downloaded file is still mp3 / m4a | Add `media.output_format=mp4` explicitly — they're separate flags |
| `Couldn't load entrypoint youtube: No module named 'lattifai'` on `lai` startup | Stale editable install — see `/lai-setup` Common Issues |

## Related Skills

- `/lai-setup` — first-time install and auth
- `/lai-align` — when media + captions are already local
- `/lai-transcribe` — transcribe without alignment (Gemini accepts YouTube URLs too)
- `/lai-diarize` — speaker labels on aligned output
- `/lai-translate` — translate captions
- `/lai-caption` — convert output format
