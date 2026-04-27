# lattifai-skills

> Audio-text alignment, transcription, translation, karaoke, and subtitle toolkit for **[Claude Code](https://code.claude.com)** — and also installable in **[OpenAI Codex CLI](https://github.com/openai/codex)** and **[Gemini CLI](https://github.com/google-gemini/gemini-cli)**. Powered by the [LattifAI](https://lattifai.com) Lattice-1 forced-alignment model.

**English** | [中文](./README.zh.md)

[![MIT License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-7c3aed)](https://code.claude.com/docs/en/plugins)
[![Skills](https://img.shields.io/badge/skills-9-10b981)](#skills)

Each skill follows the [Agent Skills standard](https://agentskills.io) — a self-contained `SKILL.md` per capability that any compatible agent can discover and load. Verified install paths for Claude Code, Codex CLI, and Gemini CLI are documented below.

9 composable skills cover the full pipeline from a raw YouTube URL to multilingual, per-word-highlighted, production-grade captions.

---

## Installation

Pick the flow that matches your agent.

### Option A — Claude Code (`/plugin marketplace`)

This repo ships both a plugin manifest and a plugin marketplace at the root. Inside any Claude Code session:

```shell
/plugin marketplace add lattifai/lattifai-skills
/plugin install lattifai-skills@lattifai-skills
/reload-plugins
```

Or non-interactively:

```bash
claude plugin marketplace add lattifai/lattifai-skills
claude plugin install lattifai-skills@lattifai-skills
```

All skills become available under the plugin namespace:

```shell
/lattifai-skills:lai-karaoke https://youtu.be/VIDEO_ID
```

### Option B — OpenAI Codex CLI (`codex plugin marketplace`)

Codex CLI accepts the same `<owner>/<repo>` source format and reads the `.claude-plugin/marketplace.json` at the repo root, so registration is one command:

```bash
codex plugin marketplace add lattifai/lattifai-skills
```

The marketplace is registered in `~/.codex/config.toml` and skills become available in your next Codex session — no separate `install` step.

### Option C — Gemini CLI (`gemini skills install`)

Gemini CLI installs skills directly from a git URL. Because the skills live under `skills/<name>/SKILL.md` (not at the repo root), pass `--path skills` to install all 9 in one call:

```bash
# Install all 9 skills from the bundle
gemini skills install https://github.com/lattifai/lattifai-skills --path skills

# Or for live development against a local checkout (auto-reloads on edit)
git clone https://github.com/lattifai/lattifai-skills.git
gemini skills link ./lattifai-skills/skills
```

### Option D — Any other agent (drop-in `SKILL.md` directory)

Each `skills/<name>/` directory is a self-contained skill following the Agent Skills standard — copy whichever ones you want to wherever your agent watches:

```bash
git clone https://github.com/lattifai/lattifai-skills.git
mkdir -p .claude/skills && cp -r lattifai-skills/skills/lai-karaoke .claude/skills/
```

Common destinations:

| Agent | Drop-in path |
|-------|--------------|
| Claude Code (project) | `.claude/skills/<name>/SKILL.md` |
| Claude Code (personal) | `~/.claude/skills/<name>/SKILL.md` |
| Cursor / Continue / custom agents | wherever your agent loads skills from |

Edits to `.claude/skills/` are picked up live within the current Claude Code session — no reload command needed. Other agents follow their own conventions (`/reload-plugins` in CC for plugin-dir / marketplace sources; `gemini skills enable/disable` for Gemini; restart for agents without hot-reload).

### Update

```shell
# Claude Code:
/plugin marketplace update lattifai-skills
# Codex CLI:
codex plugin marketplace upgrade lattifai-skills
# Gemini CLI:
gemini skills install https://github.com/lattifai/lattifai-skills --path skills
```

---

## Requirements

Different skills have different dependencies — install what you need.

> **Important:** the `lattifai` package depends on `lattifai-core`, which is hosted on the LattifAI PyPI mirror. Always include `--extra-index-url https://lattifai.github.io/pypi/simple/` when installing.

```bash
# pip (default, takes 5–15 min on first install)
pip install "lattifai[all]" --extra-index-url https://lattifai.github.io/pypi/simple/

# uv — recommended for ~10–15× faster install (≈1 min on broadband)
uv pip install "lattifai[all]" --extra-index-url https://lattifai.github.io/pypi/simple/
uv pip install --reinstall-package lattifai "lattifai[all]" \
    --extra-index-url https://lattifai.github.io/pypi/simple/
# (The second uv command is a workaround for a known entry-point name
#  conflict — re-installs lattifai last so its `lai` console script wins.
#  See `/lai-setup` for details.)
```

| Skill group | Required | Optional |
|-------------|----------|----------|
| Alignment / YouTube / Diarization | Python 3.10+, `pip install lattifai --extra-index-url https://lattifai.github.io/pypi/simple/`, [LattifAI API key](https://lattifai.com) (`lai auth trial` for a free one) | `yt-dlp`, `ffprobe` / `ffmpeg` |
| Transcription | `pip install "lattifai[transcription]" --extra-index-url https://lattifai.github.io/pypi/simple/` | Gemini API key (`GEMINI_API_KEY`), Parakeet / SenseVoice models |
| Caption conversion | `pip install "lattifai[captions]" --extra-index-url https://lattifai.github.io/pypi/simple/` (or full `lattifai[all]`) | — |
| Karaoke | `ffprobe` (for adaptive font sizing); the skill falls back to platform defaults without it | — |
| Translation / Summarization | No external dependencies — these skills run on your agent's own LLM | — |

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

These skills do not call any external LLM API — they run on whatever model is active in the host agent session (Claude Code, Codex CLI, Gemini CLI, etc.).

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
├── CLAUDE.md                # Repo-level conventions (loaded automatically by Claude Code)
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
