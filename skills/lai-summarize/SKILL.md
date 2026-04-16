---
name: lai-summarize
description: Summarize a transcript, podcast, or long caption file into structured markdown (TL;DR, chapters with timestamps, quotes, entities). **Primary path uses this session's LLM directly — no API key, no model config.** Trigger on "summarize", "生成摘要", "总结", "TL;DR", "episode summary", "what was discussed", or when the user has a long caption and wants key points. CLI `lai summarize caption` is the secondary path for oversized transcripts / headless runs.
---

# Content Summarizer

> **Preferred model: Claude Sonnet** (cost-efficient for this agent-driven workload). This skill runs on whatever model is active in the parent session — any Claude model works; no hard switch.

This skill summarizes using **the agent's own LLM capability** — the model you are running right now. It does not call out to any external LLM service by default. Helper scripts turn the source into an agent-ready prompt and validate the finished summary, so the agent only has to write prose.

**Primary path** (agent-driven, default): `prepare.py` → agent writes summary.md → `validate.py`.
**Secondary path**: `lai summarize caption` (CLI with its own LLM backend) — only when the transcript is too large for the agent's context, or there is no agent in the loop.

## Inputs

Any caption format supported by `lattifai-captions` (SRT, VTT, ASS, JSON, Gemini markdown, plain text, …).

Optional `meta.md` beside the source enriches the summary. **If `meta.md` defines `chapters:`, those titles and timestamps are hard constraints** — no merge, split, rename, or reorder.

`meta.md` **must** wrap its YAML in `---` frontmatter delimiters; otherwise `validate.py` can't parse it and hard constraints are silently skipped (with a warning on stderr). Minimal template:

```markdown
---
title: "Episode Title"
chapters:
  - { title: "Intro", start: 0.0, end: 60.0 }
  - { title: "Main Topic", start: 60.0, end: 420.0 }
---

Free-form notes below the frontmatter are fine.
```

## Primary Path (agent-driven)

### Parameters (agent choices)

- `<source>` — caption/transcript file
- `--output <path>` — default `<source>.summary.md`
- `--meta <path>` — episode metadata (auto-detected beside source)
- `--lang <code>` — summary language (default: source language)
- length — `short` / `medium` / `long` ≈ 200–400 / 500–1000 / 1000–2000 words (default `medium`)

### Workflow

```bash
# 1. Build an agent-ready prompt input from the source + meta.md
python skills/lai-summarize/scripts/prepare.py episode.srt -o prompt_input.md

# 2. Agent reads prompt_input.md and writes summary.md following the schema below.

# 3. Validate frontmatter, chapters, and verbatim quotes
python skills/lai-summarize/scripts/validate.py episode.srt summary.md
```

`prepare.py` produces a transcript with `[MM:SS]` timestamps and speaker labels, plus a `# Meta` block that marks `meta.md` chapters as **HARD CONSTRAINT** when present.

### Output Schema

```markdown
---
title: "Episode Title"
seo_title: "SEO title (≤60 chars)"
seo_description: "One-sentence description (≤160 chars)"
tags: ["tag1", "tag2"]             # 4–8 tags
chapters:
  - { title: "Chapter Title", start: 10.0, end: 52.0 }
confidence: 0.85                    # 0.0–1.0 self-assessment
source_quality: high                # high | medium | low
---

TL;DR paragraph (2–4 sentences, active voice).

## [00:10] Chapter Title
Summary paragraph(s).

> *"Verbatim quote, ≤40 words."*

## Entities

- **Name** (Person|Concept|Organization): one-line context
```

### What `validate.py` checks

- Frontmatter is valid YAML with all required fields
- `seo_title` ≤ 60, `seo_description` ≤ 160
- `tags`: 4–8 entries
- `chapters`: 1–8, each with title/start/end, start < end
- Hard constraint: chapter titles + timestamps match `meta.md` verbatim when present
- Body `## [MM:SS] Title` headers match frontmatter chapters 1:1 in order
- Every `> *"quote"*` appears verbatim in source transcript text
- `confidence` ∈ [0, 1]; `source_quality` ∈ {high, medium, low}

Requires `pyyaml` (stdlib `argparse` / `re` otherwise).

## Secondary Path (CLI)

The CLI takes two positional args (`input`, `output`); there is no `-o`:

```bash
lai summarize caption input.json summary.md
```

Configure an LLM backend once (required for this path only):

```bash
lai config set summarization.llm.model_name gemini-3-flash-preview
# Gemini key: see /lai-transcribe

# Or OpenAI-compatible:
lai config set summarization.llm.model_name gpt-4o
lai config set OPENAI_API_KEY <your-key>
```

CLI options: `summarization.lang=zh`, `summarization.length=short`, `summarization.output_format=json`, `meta=video.meta.md`.

## Common Issues

| Problem | Fix |
|---------|-----|
| `validate.py` flags quote not in source | Quote must be verbatim — rewrite or pick another line |
| Chapter count / timestamp drift from meta.md | Hard constraint — use meta.md values exactly |
| Transcript too large for the agent | Fall back to CLI (secondary path) |
| `meta.md` chapters malformed | Remove from meta.md and let the agent generate chapters |

## Related Skills

- `/lai-transcribe` — produce the transcript first
- `/lai-align` — precise timestamps feed chapter boundaries
- `/lai-diarize` — speaker labels enable speaker-aware summaries
- `/lai-translate` — translate the summary
