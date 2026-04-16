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

## Bilingual Rendering

- **SRT / VTT** — two lines per cue (source on top, translation below)
- **JSON** — both `text` and `translation` populated, round-trippable, and `words` arrays (if present in the source) are **preserved**. This is what makes bilingual karaoke possible.
- **ASS** — convert the bilingual JSON via `/lai-caption` (flat `ass.*` keys, not `caption.ass.*`):

  ```bash
  # Bilingual + per-word karaoke on the source language
  laicap-convert aligned_bilingual.json out.ass \
      render.word_level=true \
      ass.karaoke_effect=sweep \
      ass.karaoke_color_scheme=azure-gold \
      ass.translation_color="#00FFFF"
  ```

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
