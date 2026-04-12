---
name: lai-summarize
model: sonnet
description: Summarize a transcript, podcast, or long caption file into structured markdown (TL;DR, chapters with timestamps, quotes, entities). Trigger on "summarize", "生成摘要", "总结", "TL;DR", "episode summary", "what was discussed", or when the user has a long caption and wants key points. Agent reads the file directly; falls back to `lai summarize caption` CLI for very large files.
---

# Content Summarizer

Agent-driven summary of transcripts and captions. Output is markdown with YAML frontmatter — chapters, quotes, entities, SEO metadata.

## Inputs

Accepts JSON (`supervisions[]` from `/lai-align` or `/lai-diarize`), SRT, VTT, ASS, Gemini-style markdown, or plain text.

Optional `meta.md` beside the source enriches the summary. **If `meta.md` defines `chapters:`, those titles and timestamps are hard constraints** — no merge, split, or rename.

## Parameters

- `<source>` — caption/transcript file (required)
- `--output <path>` — default `<source>.summary.md`
- `--meta <path>` — episode metadata (auto-detected beside source)
- `--lang <code>` — summary language (default: source language)
- `--length short|medium|long` — ≈ 200–400 / 500–1000 / 1000–2000 words (default `medium`)
- `--format markdown|json` — default `markdown`

## Output Schema

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

## Validation Before Writing

- Frontmatter is valid YAML
- Chapter headers match `chapters[]` in order
- Hard-constraint `start` / `end` unchanged
- No empty chapter bodies
- Every quote appears verbatim in the source
- `tags[]` has 4–8 items; SEO fields within limits

## CLI Fallback (large files)

For transcripts too large for the agent (> ~500 segments):

```bash
lai summarize caption input.json -o summary.md
```

Configure an LLM backend once:

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
| Source file not found | Fail loud — check the path |
| Too large for agent | Fall back to CLI `lai summarize caption` |
| `meta.md` chapters malformed | Agent generates chapters instead |
| Validation fails | Fix and retry before writing |

## Related Skills

- `/lai-transcribe` — produce the transcript first
- `/lai-align` — precise timestamps feed chapter boundaries
- `/lai-diarize` — speaker labels enable speaker-aware summaries
- `/lai-translate` — translate the summary
