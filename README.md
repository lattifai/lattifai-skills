# lattifai-skills

> Audio-text alignment, transcription, translation, karaoke, and subtitle toolkit for [Claude Code](https://code.claude.com) — powered by the [LattifAI](https://lattifai.com) Lattice-1 forced-alignment model.

**English** | [中文](./README.zh.md)

[![MIT License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-7c3aed)](https://code.claude.com/docs/en/plugins)
[![Skills](https://img.shields.io/badge/skills-9-10b981)](#skills)

One `/plugin install` → 9 composable skills covering the full pipeline from a raw YouTube URL to multilingual, per-word-highlighted, production-grade captions.

---

## Installation

This repository is both a **plugin** and a **plugin marketplace** — pick whichever flow you prefer.

### Option A — Install via marketplace (recommended)

Register the marketplace and install the plugin in one session:

```shell
/plugin marketplace add lattifai/lattifai-skills
/plugin install lattifai-skills@lattifai-skills
```

Or use the non-interactive CLI:

```bash
claude plugin marketplace add lattifai/lattifai-skills
claude plugin install lattifai-skills@lattifai-skills
```

After install, reload to pick up the skills:

```shell
/reload-plugins
```

All skills become available under the plugin namespace:

```shell
/lattifai-skills:lai-karaoke https://youtu.be/VIDEO_ID
```

### Option B — Local development (`--plugin-dir`)

For testing unpublished changes without registering a marketplace:

```bash
git clone https://github.com/lattifai/lattifai-skills.git
claude --plugin-dir ./lattifai-skills
```

### Option C — Project-level skills (drop-in `.claude/skills`)

If you only want a subset and don't need plugin namespacing, copy individual skills into your project:

```bash
mkdir -p .claude/skills
cp -r lattifai-skills/skills/lai-karaoke .claude/skills/
```

They will be invocable as `/lai-karaoke` (no namespace prefix) and scoped to the current project.

### Update

```shell
/plugin marketplace update lattifai-skills
```

---

## Requirements

Different skills have different dependencies — install what you need:

| Skill group | Required | Optional |
|-------------|----------|----------|
| Alignment / YouTube / Diarization | Python 3.10+, `pip install lattifai`, [LattifAI API key](https://lattifai.com) (`lai auth trial` for a free one) | `yt-dlp`, `ffprobe` / `ffmpeg` |
| Transcription | `pip install lattifai[transcription]` | Gemini API key (`GEMINI_API_KEY`), Parakeet / SenseVoice models |
| Caption conversion | `pip install lattifai[captions]` (or full `lattifai[all]`) | — |
| Karaoke | `ffprobe` (for adaptive font sizing); the skill falls back to platform defaults without it | — |
| Translation / Summarization | No external dependencies — these skills run on Claude Code's own LLM | — |

First-time users should start with **`/lai-setup`** — it installs the CLI, walks through authentication, and claims a free trial key.

---

## Skills

### 🚀 Workflow (end-to-end)

| Skill | One-liner |
|-------|-----------|
| [`/lai-setup`](skills/lai-setup/SKILL.md) | Install `lattifai`, authenticate, claim a free trial, verify the environment. **Start here.** |
| [`/lai-youtube`](skills/lai-youtube/SKILL.md) | YouTube URL → downloaded media + aligned captions in one command. Also covers `lai youtube download` (media only). |
| [`/lai-karaoke`](skills/lai-karaoke/SKILL.md) | Viral-ready per-word-highlighted ASS for TikTok / Reels / 抖音 / 小红书 / cinematic YouTube. **Adaptive font size** from media resolution; 5 named style presets. |

### 🔧 Core (single-purpose CLI)

| Skill | One-liner |
|-------|-----------|
| [`/lai-transcribe`](skills/lai-transcribe/SKILL.md) | Audio / video → timestamped captions via Gemini, Parakeet, or SenseVoice. |
| [`/lai-align`](skills/lai-align/SKILL.md) | Snap an existing transcript to the audio with sub-frame precision (Lattice-1 forced alignment). Produces word-level timestamps. |
| [`/lai-diarize`](skills/lai-diarize/SKILL.md) | Speaker diarization via pyannote.audio; agent-driven name inference from transcript + `meta.md`. |
| [`/lai-caption`](skills/lai-caption/SKILL.md) | Convert between 30+ caption formats (SRT / VTT / ASS / JSON / TextGrid / LRC / FCPXML / Premiere / …). Also houses the broadcast-grade `standardization.*` profiles (Netflix / YouTube). |

### 🤖 Agent-driven (LLM in the loop)

These skills do not call any external LLM API — they run on whatever model is active in your Claude Code session.

| Skill | One-liner |
|-------|-----------|
| [`/lai-translate`](skills/lai-translate/SKILL.md) | Translate captions (or produce bilingual) while preserving segment count, timing, speakers, and word-level arrays. Includes the canonical **Bilingual Delivery Guide** (format decision table + typography rules + 4 recipes for learning / social / karaoke / dual-track delivery). |
| [`/lai-summarize`](skills/lai-summarize/SKILL.md) | Turn a long transcript into structured markdown (frontmatter + chapters + verbatim quotes + entities). Validates that chapter headers align with frontmatter and all quotes exist verbatim in the source. |

---

## Quick Example

End-to-end — from a YouTube URL to a multilingual lyric video plus a summary, all in one session:

```shell
# 1. Download + word-level alignment (cleans auto-captions into sentences)
/lai-youtube https://youtu.be/la0CaZ2R8EY

# 2. Speaker diarization + real-name inference
/lai-diarize

# 3. Translate to Chinese (preserves timing, speakers, words)
/lai-translate — produce bilingual Chinese

# 4. Viral-ready karaoke for TikTok / Reels (auto-detects video resolution)
/lai-karaoke --style tiktok

# 5. Summarize the episode (EN + ZH)
/lai-summarize
```

All artifacts land next to the media file — aligned JSON, bilingual SRT / ASS, karaoke ASS per preset, summary markdown.

---

## Repository structure

```
lattifai-skills/
├── .claude-plugin/
│   ├── plugin.json          # Plugin manifest (name, version, author, …)
│   └── marketplace.json     # Marketplace catalog (so this repo can be added with /plugin marketplace add)
├── skills/
│   ├── lai-setup/SKILL.md
│   ├── lai-youtube/SKILL.md
│   ├── lai-karaoke/
│   │   ├── SKILL.md
│   │   └── scripts/probe_media.py
│   ├── lai-transcribe/SKILL.md
│   ├── lai-align/SKILL.md
│   ├── lai-diarize/SKILL.md
│   ├── lai-caption/SKILL.md
│   ├── lai-translate/
│   │   ├── SKILL.md
│   │   └── scripts/{chunk,merge,validate}.py
│   └── lai-summarize/
│       ├── SKILL.md
│       └── scripts/{prepare,validate}.py
├── evals/                   # Skill evaluations / test fixtures
├── CLAUDE.md                # Conventions for contributors using Claude Code
├── CHANGELOG.md             # Keep a Changelog format; maintained by semantic-release
├── LICENSE                  # MIT
└── README.md / README.zh.md
```

Each skill is self-contained: `SKILL.md` is the entry point, `scripts/` holds helpers the agent shells out to.

---

## Development

```bash
# Clone
git clone https://github.com/lattifai/lattifai-skills.git
cd lattifai-skills

# Iterate locally
claude --plugin-dir .

# After editing any SKILL.md, reload without restart:
/reload-plugins

# Validate the plugin + marketplace manifest
claude plugin validate .
```

Pull requests welcome. Please keep each skill's `description` frontmatter tight — it's what Claude uses to decide when to auto-invoke.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`). On every merge to `main`, semantic-release cuts a new version, generates `CHANGELOG.md`, and syncs `plugin.json` / `marketplace.json` versions automatically.

---

## License

[MIT](./LICENSE) © LattifAI
