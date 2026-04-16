---
name: lai-translate
description: Translate captions into another language (or produce bilingual captions) while preserving segment count, timing, and speaker labels. **Primary path uses this session's LLM directly — no API key, no model config.** Trigger on "translate captions", "翻译字幕", "翻译成中文/英文", "make bilingual subtitles", or "translate this" when working with caption files. CLI `lai translate run` is the secondary path for headless / oversized runs.
---

# Caption Translator

> **Preferred model: Claude Sonnet** (cost-efficient for this agent-driven workload). This skill runs on whatever model is active in the parent session — any Claude model works; no hard switch. If you're deliberately on Opus / Haiku, that's fine.

This skill translates using **the agent's own LLM capability** — the model you are running right now. It does not call out to any external translation service by default. Helper scripts do the mechanical parsing, chunking, and writing so the agent only has to produce translations.

**Primary path** (agent-driven, default): `chunk.py` → agent translates → `merge.py` → `validate.py`.
**Secondary path**: `lai translate run` (CLI with its own LLM backend) — use only when there is no agent in the loop (batch pipelines, CI) or when a transcript is too large to fit in the agent's context.

## Invariants

Any violation is a bug; `validate.py` enforces them.

- Segment count, order, `start` / `end`, `speaker` — preserved verbatim
- Every output segment has non-empty text
- Bilingual mode (JSON): source `text` preserved, `translation` non-empty
- Non-speech events (`[MUSIC]`, `[APPLAUSE]`, …) — keep them as-is inside translations

## Primary Path (agent-driven)

### Parameters (agent choices)

- `<source>` — caption file (SRT, VTT, JSON, ASS, …) parsed via `lattifai-captions` (30+ formats)
- target language — ISO code (`zh`, `ja`, `ko`, `es`, `fr`, `de`, …)
- `--bilingual` — keep source text + attach translation (renderers emit dual lines)
- `--mode refined` — agent does a self-critique revision pass on accuracy / naturalness / terminology / voice
- `--chunk-size N` — segments per chunk fed to the agent (default 30)

### Workflow

```bash
# 1. Split the source into agent-sized chunks (JSON, stripped to essentials)
python skills/lai-translate/scripts/chunk.py video.srt --chunk-size 30 -o chunks.json

# 2. Agent translates each chunk and writes translated.json:
#    {"target_lang": "zh",
#     "items": [{"idx": 0, "translation": "..."}, ...]}

# 3. Merge translations back into the source format
#    replace mode (default) — produces a standalone zh SRT:
python skills/lai-translate/scripts/merge.py video.srt translated.json
#    bilingual mode — source + translation lines (SRT/VTT/ASS/JSON):
python skills/lai-translate/scripts/merge.py video.srt translated.json --bilingual -o video_bilingual.srt

# 4. Validate invariants
python skills/lai-translate/scripts/validate.py video.srt video_Chinese.srt
```

Default output path: `<source_stem>_<LanguageName>.<ext>` next to the source.

### Agent responsibilities inside step 2

1. Read the source (and ideally a few surrounding chunks) to lock terminology and register
2. Translate each item, keeping speaker voice distinct and non-speech events intact
3. **Refined mode**: review each chunk against accuracy / naturalness / terminology / voice; revise failures
4. Emit `translated.json` with `idx` matching the source — do not add/remove/reorder items

## Secondary Path (CLI, headless)

The CLI subcommand is `lai translate caption` (not `lai translate run`); `input` / `output` are positional:

```bash
lai translate caption input.srt output.srt \
    translation.target_lang=zh \
    translation.mode=normal
```

Configure an LLM backend once (required for this path only):

```bash
lai config set translation.llm.model_name gemini-3-flash-preview
# Gemini key: see /lai-transcribe

# Or OpenAI-compatible:
lai config set translation.llm.model_name gpt-4o
lai config set OPENAI_API_KEY <your-key>
```

## Bilingual Delivery Guide

This guide is the canonical reference for bilingual captions. `/lai-caption` and `/lai-karaoke` cross-reference it instead of duplicating content.

### 1. Pick the format by scenario

| Scenario | Recommended format | Why |
|----------|-------------------|-----|
| Language learning / foreign-film viewing | **SRT dual-line** (source on top, translation below) | Universal player support, readable on any device; fastest to ship |
| Social short video (抖音 / 小红书 / Reels / TikTok) | **ASS dual-color** (source primary, translation in accent) | Inline styling, brand color, adaptive `font_size` for vertical video |
| Lyric / karaoke video | **ASS bilingual + karaoke** (per-word sweep on source, translation line below) | Keeps per-word highlight; see `/lai-karaoke` §Bilingual variant |
| Broadcast / platform upload (YouTube / Netflix / Bilibili) | **Two independent tracks** — one SRT per language | Platforms want separate subtitle streams, not dual-line merged |
| Further processing / re-rendering | **Bilingual JSON** (both `text` and `translation` populated) | Round-trippable; preserves `words`, `speaker`, and enables any of the above later |

### 2. Typography conventions

- **Line order** — source on top, translation on bottom (top reads first; faster for learners). Flip only when the translation is the primary viewer experience and the source is the reference
- **Color** — source keeps the primary color (white/near-white on dark video); translation uses an accent that stands out without fighting the source. Field-tested picks: Cyan `#00FFFF` (cool), Amber `#FFC209` (warm), Pink `#F7C3D9` (soft). Aim for contrast ratio ≥ 2:1 against both the source line and the background
- **Font size** — translation at 0.80–0.85× the source (reduces visual weight, keeps source as anchor). For Chinese translation of English source, *do not* scale below 0.8× — CJK glyphs need ~80% of Latin size just to stay legible
- **Position** — default to bottom dual-line. When bottom gets crowded (>42 CPL combined) split top-bottom (source at top, translation at bottom). See `/lai-caption` §Broadcast-Grade Profiles for per-line wrapping rules

### 3. Recipes

All four recipes assume `aligned.json` exists (produced by `/lai-align` or `/lai-youtube`) and the agent has produced `translated.json` via step 2 of the §Primary Path.

**R1 — Language-learning SRT (dual-line, universal player)**

```bash
python skills/lai-translate/scripts/merge.py \
    aligned.json translated.json \
    --bilingual -o video.zh-bilingual.srt
python skills/lai-translate/scripts/validate.py \
    aligned.json video.zh-bilingual.srt
```

Default: source on top, translation below. Works in VLC, YouTube upload, PotPlayer, mpv, Premiere.

**R2 — Social short video (ASS dual-color, adaptive font)**

```bash
# First merge into bilingual JSON (preserves words + translation)
python skills/lai-translate/scripts/merge.py \
    aligned.json translated.json \
    --bilingual -o aligned_bilingual.json

# Then render ASS — MUST set karaoke_effect for translation_color to take effect
# (see "Rendering constraint" below). `instant` = zero animation, just the dual-
# color output we want for social.
laicap-convert --direct -Y aligned_bilingual.json out.ass \
    ass.karaoke_effect=instant \
    ass.primary_color="#FFFFFF" \
    ass.translation_color="#FFC209" \
    ass.font_size=86 \
    ass.play_res_x=1080 ass.play_res_y=1920 \
    standardization.start_margin=0.05 \
    standardization.end_margin=0.15
```

For portrait 9:16 use `ass.font_size=86`, landscape 16:9 `76`, 4K landscape `151` (see `/lai-karaoke` §Adaptive Font Size).

> **Rendering constraint** — `ass.translation_color` is injected into the dialogue only when `ass.karaoke_effect` is set (`sweep` / `instant` / `outline`). Plain ASS without a karaoke effect renders both lines in one style (both use `primary_color`). Use `karaoke_effect=instant` to get dual-color without any per-word animation.

**R3 — Bilingual karaoke (per-word sweep + translation line)**

Route through `/lai-karaoke` — it handles aspect-aware font sizing, presets, and the `ass.translation_color` wiring. Quick form:

```bash
laicap-convert --direct -Y aligned_bilingual.json out.karaoke.ass \
    ass.karaoke_effect=sweep \
    ass.karaoke_color_scheme=azure-gold \
    ass.translation_color="#00FFFF" \
    ass.font_size=<from probe_media.py>
```

**R4 — Two independent tracks (platform upload)**

```bash
# Source-language SRT — skip translation entirely, just convert aligned.json
laicap-convert --direct -Y aligned.json video.en.srt

# Target-language SRT — merge WITHOUT --bilingual (replace mode)
python skills/lai-translate/scripts/merge.py \
    aligned.json translated.json -o video.zh.srt
```

Upload both files as separate subtitle tracks. This is what YouTube / Bilibili multi-language upload and Netflix TTG workflows expect — dual-line merged files get rejected at QC.

### 4. JSON round-trip property

The bilingual JSON produced by `merge.py --bilingual` is the **canonical intermediate format** — it carries `text`, `translation`, `target_lang`, `words` (if any), and `speaker` (if any). Once you have it, every rendering downstream (R1–R3, karaoke variants, speaker-colored bilingual, …) is a single `laicap-convert` call away. Build the JSON once, render many.

## Common Issues

| Problem | Fix |
|---------|-----|
| `merge.py` reports N missing translations | Re-translate those `idx`es and re-run `merge.py` |
| `validate.py` flags segment count drift | Bug — re-run `chunk.py` + `merge.py` from a clean state |
| Terminology inconsistent across chunks | Run in refined mode, or pass earlier chunks as context |
| Source-language text leaks into translation | Refined mode's self-critique; validate `validate.py` on JSON output |
| Transcript too large for the agent | Fall back to CLI (secondary path) |
| Source language unclear | Ask the user to confirm before translating |

## Related Skills

- `/lai-transcribe`, `/lai-align` — produce the caption file first
- `/lai-caption` — convert translated output (e.g., bilingual ASS)
- `/lai-summarize` — summarize instead of translating
