---
name: lai-diarize
description: Identify speakers ("who said what") in aligned captions via pyannote.audio. Real speaker names come from the agent's own reasoning over transcript + context (default), with a CLI-LLM fallback for headless runs. Trigger on multi-speaker content (podcasts, interviews, meetings) or phrases like "diarize", "speaker detection", "说话人识别", "区分说话人", "label the speakers". Requires aligned captions — run `/lai-align` first.
---

# Speaker Diarization

> **Preferred model: Claude Sonnet** (cost-efficient for agent-driven naming). This skill runs on whatever model is active in the parent session — any Claude model works; no hard switch. Sonnet has no 1M-context variant, so if the parent session is Opus[1M], continuing on Opus is normal (avoids a no-op model swap).

Adds `speaker` labels to aligned captions. Speaker **detection** (who speaks when) is always CLI-based via pyannote.audio; speaker **naming** (who each one is) is agent-driven by default.

## Basic Command

`<base>` = source media stem (e.g. `podcast` from `podcast.mp3`) or YouTube ID. Files all land in the current directory:

```bash
lai diarize run podcast.mp3 podcast.aligned.json podcast.diarized.json
# shortcut:
lai-diarize podcast.mp3 podcast.aligned.json podcast.diarized.json
```

Output labels detected speakers as `SPEAKER_00`, `SPEAKER_01`, …

Speaker count is auto-detected. Override only when auto-detection is clearly wrong:

- `diarization.num_speakers=3` — exact count (when known)
- `diarization.min_speakers=N` / `diarization.max_speakers=N` — bound the search

## Giving Speakers Real Names

### Agent-driven (default)

After the basic command finishes, the agent reads the diarized output (the file you wrote with `output_caption=…`) together with any available context, and writes the named result. You may write the named version back into the same path (in-place edit) or to a separate path — depends on your project's convention.

**Two-file convention** (preferred when state matters, e.g. CI pipelines): emit the acoustic-only output as `diarized.raw.json` and let the agent write the named result to `diarized.json`. This keeps "acoustic切分 done" distinct from "named, ready for publish," and lets downstream stages hard-fail when the agent hasn't run yet. The ai-podcast-pipeline repo follows this convention (see its CLAUDE.md).

Signals the agent uses:

1. **Explicit context** the user provides in the conversation
2. **`meta.md`** beside the source (YAML frontmatter, format below)
3. **Transcript evidence** — self-introductions ("I'm Alice…"), mutual addressing ("thanks, Bob"), host/guest dynamics, topical expertise
4. **Existing inline labels** in the source text (`[Alice]`, `>> Bob:`, `SPEAKER_01:`) — preserved by the CLI and matched by the agent
5. **Speaker-change markers in `supervision.custom`** — see Forward Search below

Process:

1. Read `diarized.json` — collect unique `SPEAKER_XX` ids and sample 3–5 segments per speaker
2. Gather context (inline hints, meta.md, transcript clues)
3. Map each `SPEAKER_XX` → real name with a confidence note. If unsure, keep `SPEAKER_XX` rather than guessing
4. **Resolve ghost tiers via forward search** (next subsection) before finalizing
5. Rewrite the `speaker` field across all segments; do not touch `text`, `start`, `end`, or segment order
6. Show the user the mapping before finalizing if any mapping is uncertain

#### Forward Search via `>>` / speaker-change markers

VTT and SRT broadcast captions encode speaker turns with markers like `>>`
(usually escaped as `&gt;&gt;` in raw VTT), `<v Speaker>`, `[Speaker]`, or all-caps
lead-ins. LattifAI preserves whatever marker it found in `supervision.custom`:

```json
"custom": {
    "original_speaker": ">>",
    "speaker_change": true
}
```

**Key insight**: `>>` alone (no trailing name) is still a strong signal — the
captioner asserts a *new speaker starts here*. When the resolved `speaker` for
such a segment is still `SPEAKER_XX` / `Unknown` / empty (typically a 1–3 segment
"ghost tier" that pyannote couldn't merge into a main cluster), don't leave it
unnamed. Run **forward search**:

1. **Walk forward** from this segment through same-`SPEAKER_XX` neighbors *and*
   onwards through later segments after `>>` boundaries.
2. **Stop at the first identity anchor**, in priority order:
   - **Self-introduction** — "I'm X", "My name is X", "I'm a Y at Z" (match
     Z against `meta.md` `affiliation` fields)
   - **Cross-address** — an adjacent speaker says "Thanks, X", "X, what do
     you think?", "Let me hand it to X"
   - **Topic ownership** — domain reference that pins exactly one speaker
     in `meta.md` (e.g. "in my RNA work…" → host with `affiliation: "Atomic AI"`)
3. **Backfill** the anchor's real name into the originating `>>` segment.
4. **Fallback** — if no anchor is found before the speaker turn ends (next
   `>>` or end of file), keep the segment as `SPEAKER_XX` rather than guessing.

**Dominant-neighbor merge** (when `>>` is absent): tiers with ≤3 segments and no
speaker-change marker are usually pyannote boundary artifacts. If such a
segment is sandwiched between two segments of the same real speaker, attribute
it to that speaker — short interjections ("Yes.", "Yeah.", "Right.") don't
carry identity, and the acoustic edge is more likely segmentation noise than a
third party.

**meta.md** (optional but strong signal — drives both `num_speakers` and forward-search topic anchors). All fields below are parsed by both the agent-driven path and the CLI-LLM fallback (`lai diarize naming` / `diarize run`):

```yaml
---
title: "Deep Dive into LLMs"
speakers:
  - name: Alice Chen
    role: host
    affiliation: "Anthropic (research engineer)"   # self-introduction & topic-ownership anchor
    aliases: ["Alice"]                              # short forms LLM should fold back to full name
    bio: "Host of the show. Background in distributed systems."
  - name: Bob Smith
    role: guest
    affiliation: "Stanford AI Lab"
    aliases: ["Bob", "Bobby"]
    bio: "PhD candidate working on RLHF and scaling laws."
topics: ["RLHF", "scaling laws", "alignment"]       # episode-level keyword hints
prior_episodes:
  - "Episode 42: pretraining — same guest, covers scaling laws"
---
```

Keep `name` clean (no `", OpenAI"` suffix) — put organizations in `affiliation` so
the agent can match self-introductions ("I'm a researcher at Stanford" → Bob) to
exactly one speaker, and downstream slug resolvers don't break on commas. `aliases`
let the LLM map cross-references like "thanks, Swyx" back to the full legal name
instead of inventing a third speaker; `bio` and `topics` give the LLM
episode-specific expertise to anchor topical references against.

### CLI-LLM fallback (headless / automated runs)

When the agent is not in the loop (batch pipelines, CI, unattended scripts), let the CLI do name inference with its own LLM backend:

```bash
lai config set diarization.llm.model_name gemini-3-flash-preview    # one-time
# Gemini key: see /lai-transcribe
lai diarize run --direct -Y \
    podcast.mp3 podcast.aligned.json podcast.diarized.json \
    diarization.infer_speakers=true \
    diarization.llm.reasoning=true
```

- `diarization.infer_speakers=true` — enable CLI-side name inference (requires LLM config above)
- `diarization.llm.reasoning=true` — ask the LLM to show its reasoning before committing to a name; trades latency for accuracy on ambiguous speakers

You can also pass hints at invocation time without any LLM:

```bash
lai diarize run podcast.mp3 podcast.aligned.json podcast.diarized.json \
    context="Host: Alice Chen (tech journalist), Guest: Bob Smith (AI researcher)"
# or point at a meta.md (first positional `context` arg also accepts a file path):
lai diarize run podcast.mp3 podcast.aligned.json podcast.diarized.json context=podcast.meta.md
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
| Too many speakers detected (ghost tiers) | Pre-empt: pass `diarization.num_speakers=N` from `meta.md`. Post-hoc: dominant-neighbor merge (see Forward Search section) |
| Tiny tier (1–3 segments) of short interjections | Pyannote boundary noise — dominant-neighbor merge into the surrounding speaker, don't treat as a real third party |
| `>>` segment left as `SPEAKER_XX` | Run forward search (see above); only keep `SPEAKER_XX` if no anchor exists within the speaker turn |
| Agent can't confidently name a speaker | Keep `SPEAKER_XX` and ask the user — don't guess |
| `name` field contains org (e.g. "Alex Lupsasca, OpenAI") | Split into `name: "Alex Lupsasca"` + `affiliation: "OpenAI"` — comma in name breaks slug resolution downstream |
| Headless run, no LLM configured | `lai config set diarization.llm.model_name gemini-3-flash-preview` |

## Related Skills

- `/lai-align` — produce the aligned input (required)
- `/lai-transcribe` — transcript from scratch
- `/lai-translate`, `/lai-summarize` — run on diarized output for speaker-aware results
