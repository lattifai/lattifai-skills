---
name: lai-translate
model: sonnet
description: Translate captions into another language (or produce bilingual captions) while preserving segment count, timing, and speaker labels. Trigger on "translate captions", "翻译字幕", "翻译成中文/英文", "make bilingual subtitles", or "translate this" when working with caption files. Agent does the translation; falls back to `lai translate run` CLI on demand.
---

# Caption Translator

Agent-driven translation with a strict 1:1 mapping to the source. Optional self-critique pass for higher quality.

## Invariants

Any violation is a bug.

- Segment count, order, `start` / `end`, `speaker`, and source `text` — preserved verbatim
- `translation` field — added, non-empty, target language
- Non-speech events (`[MUSIC]`, `[APPLAUSE]`, …) — kept as-is

## Parameters

- `<source>` — caption file (SRT, VTT, JSON, …), required
- `--to <lang>` — target language ISO code, required (`zh`, `ja`, `ko`, `es`, `fr`, `de`, `pt`, `hi`, `ru`, `ar`, `it`, …)
- `--bilingual` — keep source text alongside translation
- `--mode normal|refined` — `refined` adds a self-critique revision pass (default `normal`)
- `--chunk-size <N>` — segments per translation chunk (default 30)
- `--output <path>` — default `<source_stem>_<LanguageName>.<ext>`

## Process

1. Read source; detect language, register, domain, recurring terminology
2. Translate in chunks of `--chunk-size`, keeping terminology consistent and speaker voice intact
3. **Refined mode only**: review on accuracy / naturalness / terminology / voice, revise failures
4. Write in source format; validate segment count and non-empty translations

## Bilingual Output

**SRT**:

```
1
00:00:01,000 --> 00:00:03,500
Hello, welcome to the show.
你好，欢迎来到节目。
```

- **JSON** — both `text` and `translation` populated
- **ASS** — dual-line styling (source top, translation bottom). Convert via `/lai-caption`:
  `laicap-convert out.json out.ass caption.ass.style=bilingual`

## CLI Fallback

```bash
lai translate run input.srt output.srt \
    translation.target_lang=zh \
    translation.mode=normal
```

Configure an LLM backend once:

```bash
lai config set translation.llm.model_name gemini-3-flash-preview
# Gemini key: see /lai-transcribe

# Or OpenAI-compatible:
lai config set translation.llm.model_name gpt-4o
lai config set OPENAI_API_KEY <your-key>
```

## Common Issues

| Problem | Fix |
|---------|-----|
| Segment count drift | Bug — re-translate the affected chunk |
| Source-language text leaks into `translation` | Run refined mode |
| Terminology inconsistent across chunks | Refined mode's self-critique pass |
| Source language unclear | Ask the user to specify it |

## Related Skills

- `/lai-transcribe`, `/lai-align` — produce the caption file first
- `/lai-caption` — convert translated output (e.g., bilingual ASS)
- `/lai-summarize` — summarize instead of translating
