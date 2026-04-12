---
name: lai-caption
description: Use when converting between caption/subtitle formats or adjusting timing. Supports 30+ formats including SRT, VTT, ASS, TTML, JSON, TextGrid, LRC, and NLE formats (Premiere, FCPXML). Use this skill whenever the user needs to change subtitle format, shift caption timing, add ASS styling, create karaoke effects, or export captions for video editing software. Also triggers on "convert captions", "转换字幕格式", "change format", "shift timing", "SRT to VTT", "ASS styling", "转换成SRT", "make ASS subtitles", "karaoke effect", "导入Premiere", even if they just say "I have an SRT and need a VTT" or "shift all timestamps by 2 seconds".
allowed-tools: Read, Bash(laicap:*), Bash(lai:*)
---

# Caption Format Conversion

Convert between 30+ caption/subtitle formats with optional timing adjustment
and ASS styling. Preserves text content, timing, speaker labels, and
word-level alignment data where the target format supports it.

**CLI syntax note**: LattifAI uses `nemo_run` configuration syntax. Options use
`key=value` format (e.g., `caption.ass.font_size=48`), NOT traditional flags.
This applies to all `lai` subcommands.

## When to Use

- Convert between caption formats (SRT to VTT, JSON to ASS, etc.)
- Shift timing (offset all timestamps by N seconds)
- Apply ASS styling (fonts, colors, karaoke effects)
- Prepare captions for specific platforms or players
- Export aligned JSON to human-readable formats

## When NOT to Use

- Need to fix timing accuracy -- use `/lai-align` instead
- Need to generate captions from audio -- use `/lai-transcribe`
- Need translation -- use `/lai-translate`

## CLI Usage

### Format Conversion

```bash
laicap-convert input.srt output.vtt
```

Full command form:

```bash
lai caption convert input.srt output.vtt
```

Format is auto-detected from file extension.

### Common Conversions

```bash
# SRT to VTT (for web playback)
laicap-convert video.srt video.vtt

# JSON to SRT (for players)
laicap-convert aligned.json aligned.srt

# SRT to ASS (for styled subtitles)
laicap-convert video.srt video.ass

# JSON to TextGrid (for Praat linguistic analysis)
laicap-convert aligned.json aligned.TextGrid

# Gemini MD to SRT
laicap-convert transcript.md transcript.srt

# Any format to JSON (preserve all data)
laicap-convert caption.srt caption.json
```

### Timing Shift

Offset all timestamps by a fixed amount:

```bash
laicap-shift input.srt output.srt 2.5     # Shift forward 2.5 seconds
laicap-shift input.srt output.srt -1.0    # Shift backward 1 second
```

Full command form:

```bash
lai caption shift input.srt output.srt 2.5
```

### ASS Styling Options

When outputting to ASS format:

```bash
laicap-convert input.srt output.ass \
    caption.ass.font_name="Noto Sans CJK SC" \
    caption.ass.font_size=48 \
    caption.ass.primary_color="#FFFFFF" \
    caption.ass.outline_color="#000000"
```

### Bilingual ASS

```bash
laicap-convert bilingual.srt bilingual.ass \
    caption.ass.style=bilingual \
    caption.ass.line1_color="#00FF00" \
    caption.ass.line2_color="#FFFF00"
```

### Karaoke Effect (Word-Level)

Requires word-level timing data (from alignment JSON):

```bash
laicap-convert aligned.json karaoke.ass \
    caption.ass.karaoke_effect=true
```

### Speaker-Colored ASS

Different colors per speaker:

```bash
laicap-convert diarized.json speakers.ass \
    caption.render.include_speaker_in_text=true \
    caption.ass.speaker_color=true
```

## Supported Formats

### Standard Subtitle Formats

| Format | Extension | Read | Write | Notes |
|--------|-----------|------|-------|-------|
| SubRip | `.srt` | Yes | Yes | Most universal format |
| WebVTT | `.vtt` | Yes | Yes | Web standard, supports styling |
| ASS/SSA | `.ass`, `.ssa` | Yes | Yes | Rich styling, karaoke |
| LRC | `.lrc` | Yes | Yes | Lyrics format |
| Plain text | `.txt` | Yes | Yes | Text only, no timing |
| Markdown | `.md` | Yes | Yes | Gemini-style with timestamps |

### Data / Interchange Formats

| Format | Extension | Read | Write | Notes |
|--------|-----------|------|-------|-------|
| JSON | `.json` | Yes | Yes | Full data (word-level, speakers) |
| TSV | `.tsv` | Yes | Yes | Tab-separated |
| CSV | `.csv` | Yes | Yes | Comma-separated |
| Audacity | `.aud` | Yes | Yes | Audacity label track |

### Linguistic Formats

| Format | Extension | Read | Write | Notes |
|--------|-----------|------|-------|-------|
| TextGrid (Praat) | `.TextGrid` | Yes | Yes | Phonetic analysis |
| TTML | `.ttml`, `.xml` | Yes | Yes | W3C timed text |

### NLE (Non-Linear Editing) Formats

| Format | Extension | Read | Write | Notes |
|--------|-----------|------|-------|-------|
| FCPXML | `.fcpxml` | Yes | Yes | Final Cut Pro |
| Premiere XML | `.prproj.xml` | No | Yes | Adobe Premiere |

## Parameters

### Convert

| Parameter | CLI Syntax | Default | Description |
|-----------|-----------|---------|-------------|
| Input | positional arg 1 | required | Source caption file |
| Output | positional arg 2 | required | Target caption file |
| Input format | `caption.input_format=X` | auto | Override format detection |
| Word-level | `caption.render.word_level=true` | `false` | Include word timing |
| Include speaker | `caption.render.include_speaker_in_text=true` | `false` | Embed speaker labels |
| Translation first | `caption.render.translation_first=true` | `false` | Show translation above source |

### Shift

| Parameter | CLI Syntax | Default | Description |
|-----------|-----------|---------|-------------|
| Input | positional arg 1 | required | Source caption file |
| Output | positional arg 2 | required | Target caption file |
| Offset | positional arg 3 | required | Seconds to shift (positive or negative) |

### ASS Options

| Parameter | CLI Syntax | Default | Description |
|-----------|-----------|---------|-------------|
| Font | `caption.ass.font_name=X` | system default | Font family |
| Font size | `caption.ass.font_size=N` | 24 | Font size |
| Primary color | `caption.ass.primary_color=#HEX` | `#FFFFFF` | Text color |
| Outline color | `caption.ass.outline_color=#HEX` | `#000000` | Outline color |
| Karaoke | `caption.ass.karaoke_effect=true` | `false` | Karaoke highlighting |
| Speaker color | `caption.ass.speaker_color=true` | `false` | Per-speaker coloring |
| Bilingual style | `caption.ass.style=bilingual` | default | Dual-line layout |

## Workflow

### Step 1 -- Identify source format

Read the input file to determine its format and content:
- File extension for format detection
- Check for word-level data (JSON with `alignment` or `words` field)
- Check for speaker labels
- Check for bilingual content

### Step 2 -- Choose target format

| Need | Recommended Format |
|------|--------------------|
| Universal playback | `.srt` |
| Web embedding | `.vtt` |
| Styled subtitles | `.ass` |
| Downstream processing | `.json` |
| Linguistic analysis | `.TextGrid` |
| Video editing (FCP) | `.fcpxml` |
| Lyrics display | `.lrc` |

### Step 3 -- Run conversion

```bash
laicap-convert <input> <output> [options]
```

### Step 4 -- Verify output

Read the first few segments to confirm:
- Text preserved correctly
- Timing intact
- Speaker labels present (if expected)
- Styling applied (for ASS)

## Data Preservation

When converting between formats, data preservation varies:

| Data | JSON | SRT | VTT | ASS | TextGrid | TXT |
|------|------|-----|-----|-----|----------|-----|
| Text | Yes | Yes | Yes | Yes | Yes | Yes |
| Timing | Yes | Yes | Yes | Yes | Yes | No |
| Speakers | Yes | Partial | Yes | Yes | Yes | No |
| Word-level | Yes | No | No | Karaoke | Yes | No |
| Translation | Yes | Bilingual | Bilingual | Bilingual | No | No |
| Styling | No | No | Basic | Full | No | No |

**Rule**: Convert to JSON first to preserve maximum data. Then convert
from JSON to the target format for delivery.

## Error Handling

| Condition | Action |
|-----------|--------|
| Unknown input format | Specify with `caption.input_format=srt` |
| Empty file | Check file has content |
| Encoding error | Ensure file is UTF-8 |
| Missing timing data (for SRT/VTT) | Input may be plain text. Add timing via `/lai-align` |
| Karaoke requested but no word-level | Align first with `caption.render.word_level=true` |

## Related Skills

| Skill | Use When |
|-------|----------|
| `/lai-align` | Need precise timing before conversion |
| `/lai-transcribe` | Need to generate captions first |
| `/lai-translate` | Need translation before bilingual conversion |
| `/lai-diarize` | Need speaker labels before speaker-colored output |

### Common Workflow Chains

```bash
# Align -> Convert to multiple formats
lai alignment align audio.mp3 caption.srt aligned.json \
    caption.render.word_level=true
laicap-convert aligned.json aligned.srt
laicap-convert aligned.json aligned.vtt
laicap-convert aligned.json karaoke.ass caption.ass.karaoke_effect=true

# Shift + Convert
laicap-shift input.srt shifted.srt -2.0
laicap-convert shifted.srt shifted.vtt

# JSON -> bilingual ASS after translation
laicap-convert translated.json bilingual.ass \
    caption.ass.style=bilingual \
    caption.ass.line1_color="#FFFFFF" \
    caption.ass.line2_color="#FFD700"
```

## Non-Goals

- Does NOT fix timing accuracy -- use `/lai-align`
- Does NOT translate text -- use `/lai-translate`
- Does NOT generate captions from audio -- use `/lai-transcribe`
- Does NOT edit caption text content
- Does NOT merge multiple caption files into one
