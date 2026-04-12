---
name: lai-translate
model: sonnet
description: Use when translating captions/subtitles to another language. Agent-driven translation using the agent's own language ability for highest quality. Supports bilingual output. Triggers on "translate captions", "翻译字幕", "translate to Chinese", "翻译成英文", or when user has captions in one language and needs another.
---

# Caption Translator

**Agent-driven translation.** The agent reads source captions and writes
target-language translations itself -- no external translation API by default.
Quality comes from the agent's language ability, contextual understanding, and
optional self-critique. Falls back to `lai translate run` (LLM-based CLI)
when the agent cannot perform the translation directly.

## When to Use

- Translate captions/subtitles to another language
- Generate bilingual captions (source + target)
- Post-alignment translation (after `/lai-align`)
- Re-translate with improved quality
- Translate large transcript files (chunked processing)

## When NOT to Use

- Need transcription, not translation -- use `/lai-transcribe`
- Need real-time / simultaneous translation
- Translating non-caption content (articles, documents) -- use a general translation tool
- Source text has no timing information and just needs plain text translation

## Invariants

These hold at every step. Any violation is a bug.

| Field | Rule |
|-------|------|
| Segment count | IDENTICAL to source. No merge/split. |
| Segment order | IDENTICAL to source |
| `start` / `end` | Preserved verbatim |
| `speaker` | Preserved verbatim |
| Source `text` | Preserved verbatim (not overwritten) |
| `translation` | Added, non-empty target-language string |

## Parameters

| Parameter | Values | Default |
|-----------|--------|---------|
| `<source>` | Path to caption file (SRT, VTT, JSON, etc.) | required |
| `--to <lang>` | Target language ISO code | required |
| `--bilingual` | Output both source + target text | off |
| `--mode <m>` | `normal` \| `refined` | `normal` |
| `--output <path>` | Override output path | `<source>_<Lang>.<ext>` |
| `--chunk-size <N>` | Segments per translation chunk | 30 |

Mode semantics:

| Mode | Steps |
|------|-------|
| `normal` | Read source -> Translate |
| `refined` | Read source -> Translate -> Self-critique -> Revise |

## Supported Languages

Common target languages: `zh` (Chinese), `ja` (Japanese), `ko` (Korean),
`fr` (French), `es` (Spanish), `de` (German), `pt` (Portuguese),
`hi` (Hindi), `nl` (Dutch), `ru` (Russian), `ar` (Arabic), `it` (Italian).

Any language the agent model supports is valid.

## Workflow

### Step 1 -- Read source captions

Read the input caption file. Determine:
- Source language (auto-detect from text content)
- Total segment count
- Whether segments have timing (`start`/`end`) and speaker labels
- File format (SRT, VTT, JSON, etc.)

```bash
# Read the source file to understand its structure
```

For JSON files with `supervisions[]` array, read the schema directly.
For SRT/VTT files, parse segment boundaries.

### Step 2 -- Analyze content

Sample 5-8 segments spread across the file. Note:
- **Domain**: Technical, conversational, academic, entertainment
- **Register**: Formal, casual, mixed
- **Speakers**: How many, their roles (host, guest, narrator)
- **Terminology**: Recurring technical terms that need consistent translation
- **Non-speech**: Events like `[MUSIC]`, `[APPLAUSE]` -- preserve as-is

### Step 3 -- Translate chunks

Split segments into chunks of `--chunk-size` (default 30).

Per chunk, translate each segment:
- Maintain consistent terminology across chunks
- Preserve speaker voice and register
- Keep non-speech events in the source language (e.g., `[MUSIC]` stays `[MUSIC]`)
- For bilingual mode: write both source and translation

**Translation output per segment** (JSON example):

```json
{
  "text": "Original text stays here",
  "translation": "Translated text goes here",
  "start": 0.0,
  "end": 2.5,
  "speaker": "Alice"
}
```

### Step 4 -- Self-critique (refined mode only)

Review the translation against four axes:
1. **Accuracy** -- does the translation convey the same meaning?
2. **Naturalness** -- does it sound natural in the target language?
3. **Terminology** -- are technical terms consistent throughout?
4. **Voice** -- does each speaker maintain their distinct voice?

Revise segments that fail any axis.

### Step 5 -- Write output

Write the translated file in the same format as input:
- **SRT/VTT**: Replace text with translation (or bilingual format)
- **JSON**: Add `translation` field to each supervision
- **ASS**: Support dual-line bilingual rendering

Default output path: `<source_stem>_<LanguageName>.<ext>`
Example: `video.srt` -> `video_Chinese.srt`

### Step 6 -- Validate

Before finishing:
- [ ] Output segment count == source segment count
- [ ] All segments have non-empty translation
- [ ] No source `text`, `start`, `end`, or `speaker` fields were modified
- [ ] No untranslated segments (check for source-language text in translation field)
- [ ] Bilingual mode: both source and target present in each segment

## Bilingual Output

When `--bilingual` is set:

**SRT format**:
```
1
00:00:01,000 --> 00:00:03,500
Hello, welcome to the show.
你好，欢迎来到节目。
```

**ASS format**: Dual-line with distinct styling (source on top, translation below).

**JSON format**: Both `text` and `translation` fields populated.

## Fallback: CLI Translation

If the agent cannot perform translation directly (e.g., unsupported language,
very large file, or user explicitly requests CLI), fall back to:

```bash
lai translate run <input> <output> \
    translation.target_lang=zh \
    translation.mode=normal
```

CLI translation requires an LLM backend configured:

```bash
# Configure LLM for CLI translation
lai config set translation.llm.model_name gemini-2.5-flash
lai config set GEMINI_API_KEY your-key

# Or use OpenAI-compatible endpoint
lai config set translation.llm.model_name gpt-4o
lai config set OPENAI_API_KEY your-key
```

## Error Handling

| Condition | Action |
|-----------|--------|
| Source file not found | Fail loud. Check path. |
| Empty source / no segments | Fail. Not a valid caption file. |
| Unknown source language | Ask user to specify source language |
| Translation segment count drift | Bug. Re-translate the affected chunk. |
| Terminology inconsistency | Use refined mode for self-critique pass |
| Bilingual output format unsupported | Fall back to JSON (always supports bilingual) |

## Related Skills

| Skill | Use When |
|-------|----------|
| `/lai-transcribe` | Need to generate transcript before translating |
| `/lai-align` | Need precise timing before translating |
| `/lai-caption` | Convert translated output to another format |
| `/lai-summarize` | Summarize content instead of translating |

### Common Workflow Chains

```bash
# Transcribe -> Align -> Translate (agent-driven)
lai transcribe run video.mp4 transcript.json
lai alignment align video.mp4 transcript.json aligned.json
# Then /lai-translate for agent-driven translation

# YouTube -> Align -> Translate (agent-driven)
lai youtube align "https://youtu.be/xxx" -o aligned.srt
# Then /lai-translate to target language

# Translate -> Convert to bilingual ASS
# After agent translation produces video_Chinese.srt:
laicap-convert video_Chinese.srt video_bilingual.ass --style bilingual
```

## Non-Goals

- Does NOT generate transcripts -- use `/lai-transcribe`
- Does NOT fix caption timing -- use `/lai-align`
- Does NOT handle non-caption text (articles, web pages)
- Does NOT auto-publish translations to any platform
- Does NOT perform speech synthesis / dubbing
