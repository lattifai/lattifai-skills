---
name: lai-karaoke
description: Generate viral-ready karaoke / lyric-video subtitles with per-word highlighting in one command. Adaptive font size from media resolution. Ready-made style presets for TikTok, Reels, Shorts, 抖音, 小红书, YouTube, and cinematic long-form. Trigger on "karaoke 字幕", "卡拉OK", "lyric video", "逐词歌词", "按字高亮", "TikTok 字幕", "抖音字幕", "Reels caption", "Shorts caption", "小红书歌词", "viral subtitles", "爆款字幕", or when a song / podcast / video clip is given and per-word highlighted captions are asked for. For general caption format conversion without karaoke styling, use /lai-caption.
allowed-tools: Read, Write, Bash(lai:*), Bash(laicap:*), Bash(ffprobe:*), Bash(python:*)
---

# Karaoke / Lyric-Video Subtitles

One command → per-word highlighted ASS ready for TikTok, Reels, Shorts, 抖音, 小红书, or cinematic YouTube. Adaptive font size keeps captions sharp across 1080p, 4K, portrait, square, and cinematic aspect ratios without manual tuning.

## Zero-Arg Hero Path

Invoke via Claude Code — the agent automates the full chain:

```
/lai-karaoke https://youtu.be/VIDEO_ID
/lai-karaoke /path/to/video.mp4
/lai-karaoke /path/to/aligned.json   # when alignment already exists
```

Default behavior (agent executes):
1. `/lai-youtube` with `caption.input.split_sentence=true caption.render.word_level=true` (clean per-word alignment, MP4 for resolution probe)
2. `scripts/probe_media.py` reads the downloaded mp4 and computes `font_size`, `play_res_x`, `play_res_y`
3. Aspect-aware preset auto-selected (portrait → `tiktok`, landscape → `cinematic`, square → `minimal`) — the agent announces the choice and accepts an override
4. `laicap-convert` writes `<video_id>.karaoke.<preset>.ass` alongside the media
5. Agent finishes with a cross-promo — multilingual (`/lai-translate`), custom tuning (`/lai-caption`), or speaker-colored (`/lai-diarize`)

## Named Style Presets

Each preset = `karaoke_effect × karaoke_color_scheme × kinetic_style`, battle-tested for a specific distribution channel:

| Preset | Effect | Color scheme | Kinetic | Built for |
|--------|--------|--------------|---------|-----------|
| `tiktok` | `sweep` | `sunset-warm` | `pop` | TikTok / Reels / Shorts — warm punchy pop |
| `douyin` | `instant` | `navy-pink` | `shake` | 抖音潮流感、快切节奏 |
| `cinematic` | `sweep` | `prussian-elegant` | `fade` | YouTube 长视频 / 播客 / 电影感 |
| `neon` | `outline` | `mint-ocean` | `neon` | 赛博 / 电子乐 / game clip |
| `minimal` | `instant` | `azure-gold` | *(none)* | 商务 / 教程 / 播客精华 |

Ask in plain language:

> *"用 tiktok 风格做个 karaoke"* / *"cinematic 风"* / *"给我个极简商务款"*

The agent maps your phrasing to the preset table above (or asks if ambiguous).

For fully custom tuning (12 color schemes × 15 kinetic styles × 3 effects = 540 combos), see `/lai-caption` §Karaoke.

## Agent Workflow

The agent should drive this skill — do **not** require a wrapper CLI. Follow this decision tree:

### Step 1 — Classify input

| User provides | Next |
|---------------|------|
| YouTube URL | `/lai-youtube align` with `caption.input.split_sentence=true caption.render.word_level=true`, MP4 output |
| media + transcript (SRT/VTT/JSON) | `/lai-align` with `caption.render.word_level=true`, JSON output |
| aligned.json only | Ask for original media path (needed to probe resolution) |
| diarized.json | Use it directly; plan on `ass.speaker_color=auto` or a CSV |
| bilingual JSON (`text` + `translation`) | Use it directly; plan on `ass.translation_color=...` |

Confirm with the user before starting if their intent is ambiguous (e.g., they only said "做个 karaoke" without specifying input).

### Step 2 — Probe media resolution

```bash
python <skill>/scripts/probe_media.py <media_path> [--target-platform tiktok|...]
```

Returns JSON: `{width, height, aspect, font_size, play_res_x, play_res_y, source}`. `source` is `probe` (from ffprobe) or `platform-default:<name>` (audio-only fallback).

If the input is audio-only (mp3/wav/m4a, `width` ≈ `height` = 0), ask the user for the **target platform** and pass `--target-platform` to drive the fallback.

### Step 3 — Pick a preset

Auto-select if the user didn't specify one:

- `aspect == "portrait"` → `tiktok`
- `aspect == "landscape"` → `cinematic`
- `aspect == "square"` → `minimal`

Always tell the user which preset you picked; they can override.

### Step 4 — Render

Map preset → ASS config, then call `laicap-convert`:

```bash
# Example: preset=tiktok, probe={font_size:86, play_res_x:1080, play_res_y:1920}
laicap-convert --direct -Y \
    aligned.json output.karaoke.ass \
    render.word_level=true \
    render.include_speaker_in_text=true \
    ass.karaoke_effect=sweep \
    ass.karaoke_color_scheme=sunset-warm \
    ass.kinetic_style=pop \
    ass.font_size=86 \
    ass.play_res_x=1080 \
    ass.play_res_y=1920 \
    standardization.start_margin=0.05 \
    standardization.end_margin=0.15
```

Speaker-aware variant (when input is `diarized.json`):

```bash
    ass.speaker_color="#658AE4,#FFC209,#F7C3D9,#CC5D84"   # per-speaker palette
```

Bilingual variant (when input has `translation` populated — see `/lai-translate`):

```bash
    ass.translation_color="#00FFFF"
```

### Step 5 — Cross-promote (funnel)

After successful render, always surface one of:

- **Multilingual** → *"Want a Chinese / Japanese / Spanish lyric video? Run `/lai-translate` on `aligned.json`, then re-render."*
- **Custom tuning** → *"Tune colors / font / margins? See `/lai-caption` §Karaoke — 12 color schemes × 15 kinetic styles available."*
- **Speaker colors** → *"Multi-speaker clip? Run `/lai-diarize` first, then re-render with `ass.speaker_color=auto`."*

## Adaptive Font Size

Font size is picked from the shorter edge of the media, tuned per aspect:

| Aspect | Formula | Example input | Recommended `font_size` |
|--------|---------|---------------|------------------------|
| portrait (w/h < 0.85) | `w × 0.08` | 1080×1920 (TikTok) | **86** |
| square (0.85–1.4) | `h × 0.075` | 1080×1080 (IG feed) | **81** |
| landscape (w/h > 1.4) | `h × 0.07` | 1920×1080 (YT) | **76** |
| 4K landscape | `h × 0.07` | 3840×2160 | **151** |
| 2.35:1 cinematic | `h × 0.07` | 3840×1634 | **114** |

Also set `ass.play_res_x` / `ass.play_res_y` to the **actual media width/height** so ASS renderers scale all metrics (outline width, shadow depth, margins) correctly for the downstream player. `probe_media.py` emits these values directly.

Override knobs for the agent:

- User asks "字再大一点" → multiply `font_size` by 1.2–1.4
- User asks "轻一点 / 不要太大" → multiply by 0.7–0.85
- Long portrait text overflowing → reduce by ~10% or tighten `ass.margin_l` / `ass.margin_r`

## Output Convention

Default output path: `<media_stem>.karaoke[.<style>].ass` alongside the media. Multi-style exports coexist, e.g.:

```
la0CaZ2R8EY.mp4
la0CaZ2R8EY.karaoke.tiktok.ass
la0CaZ2R8EY.karaoke.cinematic.ass
```

For the exhaustive matrix (3 × 12 × 15 × 2 = 1080 combinations) used in visual tuning, see `/lai-caption` §Karaoke — this skill intentionally ships only 5 curated presets to keep the decision light.

## Common Issues

| Problem | Fix |
|---------|-----|
| `ffprobe: command not found` | `brew install ffmpeg` (macOS) or your distro equivalent |
| Audio-only input, no resolution | Pass `--target-platform tiktok\|youtube\|...` for a fallback |
| Karaoke renders without per-word highlighting | Input JSON has no `words` arrays — re-run `/lai-align` with `caption.render.word_level=true` |
| Text too small on 4K YouTube | Media probed correctly? Confirm `font_size >= 140` for 2160p landscape |
| Text overflows on portrait | Reduce `font_size` by 10% or set `ass.wrap_style=2` (smart wrap) |

## Related Skills

- `/lai-youtube` — URL → aligned captions (what this skill calls under the hood for URL input)
- `/lai-align` — local media + transcript → aligned JSON
- `/lai-caption` — full 540-combo karaoke matrix + broadcast subtitle profiles
- `/lai-translate` — produce bilingual input for multilingual lyric videos
- `/lai-diarize` — per-speaker colored karaoke
