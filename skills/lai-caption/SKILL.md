---
name: lai-caption
description: Convert between 30+ caption/subtitle formats (SRT, VTT, ASS, JSON, TextGrid, LRC, FCPXML, Premiere, …) and shift timing. Trigger on "convert captions", "SRT to VTT", "转换字幕格式", "shift timing", "ASS styling", "karaoke effect", "导入Premiere", or any caption-format question. Do NOT trigger to fix timing accuracy (`/lai-align`) or translate (`/lai-translate`).
allowed-tools: Read, Bash(laicap:*), Bash(lai:*)
---

# Caption Format Conversion

Convert, shift, and style caption files. Format is auto-detected from file extension.

`laicap-convert` and `lai caption convert` are **the same command** — the former is the shortcut entry-point. For pipeline / non-interactive use, add `--direct -Y` (direct execution, skip confirmation).

## Convert

`laicap-convert` (== `lai caption convert`) takes two positional args: `input_path` and `output_path`. All styling/rendering keys are **flat top-level config** (`render.*`, `ass.*`), **not** `caption.*`.

```bash
laicap-convert input.srt output.vtt
```

Common pairs:

```bash
laicap-convert aligned.json video.srt           # JSON → playback formats
laicap-convert video.srt video.ass              # basic → styled
laicap-convert transcript.md transcript.srt     # Gemini markdown → SRT
laicap-convert aligned.json aligned.TextGrid    # → Praat
```

Add `-Y` for non-interactive runs. Use `input_format=srt` (top-level flag) to override auto-detection when the extension is wrong.

## Shift Timing

```bash
laicap-shift input.srt output.srt 2.5     # forward 2.5 s
laicap-shift input.srt output.srt -1.0    # backward 1 s
```

## ASS Styling

Top-level `ass.*` keys (see `lai caption convert --help` for the full list):

```bash
laicap-convert input.srt output.ass \
    ass.font_name="Noto Sans CJK SC" \
    ass.font_size=48 \
    ass.primary_color="#FFFFFF"
```

### Karaoke (per-word highlighting)

Requires word-level JSON input (produced by `/lai-align` with `caption.render.word_level=true`, or `/lai-youtube` with the same flag).

```bash
laicap-convert aligned.json out.ass \
    render.word_level=true \
    ass.karaoke_effect=sweep \
    ass.karaoke_color_scheme=azure-gold
```

- `ass.karaoke_effect`: `sweep` (classic karaoke fill), `instant` (hard on/off), `outline` (outline-only highlight)
- `ass.karaoke_color_scheme` (12 presets, each tunes primary/secondary/outline/back):
  `azure-gold`, `sakura-purple`, `mint-ocean`, `gardenia-green`, `sunset-warm`,
  `prussian-elegant`, `burgundy-classic`, `langgan-spring`, `mars-teal`,
  `spring-field`, `navy-pink`, `apricot-dark`
- `ass.kinetic_style` (orthogonal per-word animation, 15 options grouped by feel):
  - **Impact**: `bounce`, `pop`, `shake`, `pulse`, `swing`
  - **Smooth**: `fade`, `zoom`, `rise`, `typewriter`, `blur_in`
  - **Stylized**: `glow`, `neon`, `wave`, `flicker`, `stagger`

### Bilingual ASS

Produce a bilingual JSON via `/lai-translate` (it preserves `words`), then convert:

```bash
laicap-convert aligned_bilingual.json out.ass \
    render.word_level=true \
    ass.karaoke_effect=sweep \
    ass.karaoke_color_scheme=azure-gold \
    ass.translation_color="#00FFFF"
```

### Speaker Color

`ass.speaker_color=...` paints dialogue per speaker (needs `/lai-diarize` output in the source). Accepts:

- `""` — disabled (default)
- `"auto"` — 10-color LattifAI palette (cycles for >10 speakers)
- `"#RRGGBB,#RRGGBB,..."` — CSV of explicit colors, one per speaker in appearance order

```bash
# Host = cyan-blue, Guest = pink — short CSV palette
laicap-convert diarized.json out.ass \
    render.include_speaker_in_text=true \
    ass.speaker_color="#658AE4,#F7C3D9"
```

## Broadcast-Grade Profiles (standardization.*)

`standardization.*` reflows segments to meet CPL/CPS/duration rules before writing. Useful for delivering SRT/VTT to Netflix-class platforms or tighter YouTube specs.

Fields (all top-level):

- `standardization.min_duration` / `max_duration` — segment duration bounds (s)
- `standardization.min_gap` — minimum inter-segment gap (s)
- `standardization.max_lines` / `max_chars_per_line` — line wrapping limits
- `standardization.optimal_cps` — target characters-per-second for readability
- `standardization.start_margin` / `end_margin` — pre/post roll per segment
- `standardization.margin_collision_mode` — `trim` (default), `drop`, …

Ready-made profiles:

```bash
# Netflix-ish: 42 CPL × 2 lines, 0.8-7 s
laicap-convert diarized.json out.netflix.srt \
    standardization.min_duration=0.8 \
    standardization.max_duration=7.0 \
    standardization.min_gap=0.08 \
    standardization.max_lines=2 \
    standardization.max_chars_per_line=42 \
    standardization.start_margin=0.05 \
    standardization.end_margin=0.15

# YouTube-ish: shorter cues, narrower lines
laicap-convert diarized.json out.youtube.srt \
    standardization.min_duration=0.5 \
    standardization.max_duration=5.0 \
    standardization.max_chars_per_line=35 \
    standardization.start_margin=0.03 \
    standardization.end_margin=0.10
```

`start_margin` / `end_margin` also benefit karaoke exports (give lyrics breathing room) — combine with the karaoke recipe above.

## Supported Formats

| Category | Formats (read & write unless noted) |
|----------|-------------------------------------|
| Standard | `.srt`, `.vtt`, `.ass` / `.ssa`, `.lrc`, `.txt`, `.md` |
| Data | `.json`, `.tsv`, `.csv`, `.aud` |
| Linguistic | `.TextGrid`, `.ttml` / `.xml` |
| NLE | `.fcpxml`; `.prproj.xml` (write-only) |

Full list: `lai caption convert --help`.

### Data Preservation

Convert to `.json` first to keep word-level timing, speakers, and translations — then fan out to delivery formats.

- **Word-level timing**: JSON, TextGrid, ASS-karaoke only
- **Speakers**: JSON, VTT, ASS, TextGrid (partial in SRT)
- **Full styling**: ASS only

## Common Issues

| Problem | Fix |
|---------|-----|
| Unknown input format | Specify `input_format=srt` (top-level flag, not `caption.input_format`) |
| Encoding error | Re-save the file as UTF-8 |
| Karaoke has no highlighting | Re-align with `caption.render.word_level=true`, then convert with `render.word_level=true` + `ass.karaoke_effect=sweep` |
| `No parameter named 'caption'` / `'input'` | For `laicap-convert`, styling keys are flat (`render.*`, `ass.*`) and input/output are positional (`input_path`/`output_path`) — there is no `caption.*` namespace here |
| Plain text missing timing | Add timing via `/lai-align` first |

## Related Skills

- `/lai-align` — fix timing accuracy (conversion doesn't change timing)
- `/lai-transcribe` — generate captions from audio first
- `/lai-translate` — translate before bilingual conversion
- `/lai-diarize` — add speaker labels for speaker-colored output
