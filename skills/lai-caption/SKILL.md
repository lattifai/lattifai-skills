---
name: lai-caption
description: Convert between 30+ caption/subtitle formats (SRT, VTT, ASS, JSON, TextGrid, LRC, FCPXML, Premiere, …) and shift timing. Trigger on "convert captions", "SRT to VTT", "转换字幕格式", "shift timing", "ASS styling", "karaoke effect", "导入Premiere", or any caption-format question. Do NOT trigger to fix timing accuracy (`/lai-align`) or translate (`/lai-translate`).
allowed-tools: Read, Bash(laicap:*), Bash(lai:*)
---

# Caption Format Conversion

Convert, shift, and style caption files. Format is auto-detected from file extension.

## Convert

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

## Shift Timing

```bash
laicap-shift input.srt output.srt 2.5     # forward 2.5 s
laicap-shift input.srt output.srt -1.0    # backward 1 s
```

## ASS Styling

```bash
laicap-convert input.srt output.ass \
    caption.ass.font_name="Noto Sans CJK SC" \
    caption.ass.font_size=48 \
    caption.ass.primary_color="#FFFFFF"
```

- `caption.ass.karaoke_effect=true` — per-word highlighting (needs word-level JSON from `/lai-align`)
- `caption.ass.speaker_color=true` — per-speaker coloring (needs `/lai-diarize` output)
- `caption.ass.style=bilingual` + `line1_color` / `line2_color` — dual-line subtitles

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
| Unknown input format | Specify `caption.input_format=srt` |
| Encoding error | Re-save the file as UTF-8 |
| Karaoke has no highlighting | Re-align with `caption.render.word_level=true` |
| Plain text missing timing | Add timing via `/lai-align` first |

## Related Skills

- `/lai-align` — fix timing accuracy (conversion doesn't change timing)
- `/lai-transcribe` — generate captions from audio first
- `/lai-translate` — translate before bilingual conversion
- `/lai-diarize` — add speaker labels for speaker-colored output
