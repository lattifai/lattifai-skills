---
name: lai-diarize
description: Identify speakers ("who said what") in aligned captions via pyannote.audio. Real speaker names come from the agent's own reasoning over transcript + context (default), with a CLI-LLM fallback for headless runs. Trigger on multi-speaker content (podcasts, interviews, meetings) or phrases like "diarize", "speaker detection", "说话人识别", "区分说话人", "label the speakers". Requires aligned captions — run `/lai-align` first.
---

# Speaker Diarization

> **Preferred model: Claude Sonnet** (cost-efficient for agent-driven naming). This skill runs on whatever model is active in the parent session — any Claude model works; no hard switch. Sonnet has no 1M-context variant, so if the parent session is Opus[1M], continuing on Opus is normal (avoids a no-op model swap).

Adds `speaker` labels to aligned captions. Speaker **detection** (who speaks when) is always CLI-based via pyannote.audio; speaker **naming** (who each one is) is agent-driven by default.

## Basic Command

```bash
lai diarize run audio.mp3 aligned.json diarized.json
# shortcut:
lai-diarize audio.mp3 aligned.json diarized.json
```

Output labels detected speakers as `SPEAKER_00`, `SPEAKER_01`, …

Speaker count is auto-detected. Override only when auto-detection is clearly wrong:

- `diarization.num_speakers=3` — exact count (when known)
- `diarization.min_speakers=N` / `diarization.max_speakers=N` — bound the search

## Giving Speakers Real Names

### Agent-driven (default)

After the basic command finishes, the agent reads `diarized.json` together with any available context and rewrites `SPEAKER_XX` in-place with real names.

Signals the agent uses:

1. **Explicit context** the user provides in the conversation
2. **`meta.md`** beside the source (YAML frontmatter, format below)
3. **Transcript evidence** — self-introductions ("I'm Alice…"), mutual addressing ("thanks, Bob"), host/guest dynamics, topical expertise
4. **Existing inline labels** in the source text (`[Alice]`, `>> Bob:`, `SPEAKER_01:`) — preserved by the CLI and matched by the agent

Process:

1. Read `diarized.json` — collect unique `SPEAKER_XX` ids and sample 3–5 segments per speaker
2. Gather context (inline hints, meta.md, transcript clues)
3. Map each `SPEAKER_XX` → real name with a confidence note. If unsure, keep `SPEAKER_XX` rather than guessing
4. Rewrite the `speaker` field across all segments; do not touch `text`, `start`, `end`, or segment order
5. Show the user the mapping before finalizing if any mapping is uncertain

**meta.md** (optional, strong signal):

```yaml
---
title: "Deep Dive into LLMs"
speakers:
  - name: Alice Chen
    role: host
  - name: Bob Smith
    role: guest
---
```

### CLI-LLM fallback (headless / automated runs)

When the agent is not in the loop (batch pipelines, CI, unattended scripts), let the CLI do name inference with its own LLM backend:

```bash
lai config set diarization.llm.model_name gemini-3-flash-preview    # one-time
# Gemini key: see /lai-transcribe
lai diarize run --direct -Y \
    podcast.mp3 aligned.json diarized.json \
    diarization.infer_speakers=true \
    diarization.llm.reasoning=true
```

- `diarization.infer_speakers=true` — enable CLI-side name inference (requires LLM config above)
- `diarization.llm.reasoning=true` — ask the LLM to show its reasoning before committing to a name; trades latency for accuracy on ambiguous speakers

You can also pass hints at invocation time without any LLM:

```bash
lai diarize run podcast.mp3 aligned.json diarized.json \
    context="Host: Alice Chen (tech journalist), Guest: Bob Smith (AI researcher)"
# or point at a meta.md (first positional `context` arg also accepts a file path):
lai diarize run podcast.mp3 aligned.json diarized.json context=episode.meta.md
```

## Output

Each supervision gains a `speaker` field:

```json
{ "text": "Welcome to the show.", "start": 0.0, "end": 2.5, "speaker": "Alice Chen" }
```

## Common Issues

| Problem | Fix |
|---------|-----|
| `No aligned segments` | Run `/lai-align` first |
| Too many speakers detected | `diarization.max_speakers=N` |
| Agent can't confidently name a speaker | Keep `SPEAKER_XX` and ask the user — don't guess |
| Headless run, no LLM configured | `lai config set diarization.llm.model_name gemini-3-flash-preview` |

## Related Skills

- `/lai-align` — produce the aligned input (required)
- `/lai-transcribe` — transcript from scratch
- `/lai-translate`, `/lai-summarize` — run on diarized output for speaker-aware results
