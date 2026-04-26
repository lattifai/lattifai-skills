# Changelog

All notable changes to this project are documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Starting from v1.0.0, entries below are generated automatically by [semantic-release](https://github.com/semantic-release/semantic-release) from [Conventional Commits](https://www.conventionalcommits.org/).

## [Unreleased]

### Added
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` — ship the repo as both a Claude Code plugin and a plugin marketplace.
- `README.zh.md` — Simplified Chinese mirror of the README.
- semantic-release pipeline (`.releaserc.json`, `package.json`, `.github/workflows/release.yml`) — Conventional Commits → automated versioning, `CHANGELOG.md` generation, `plugin.json` / `marketplace.json` version sync, GitHub Release creation.

## [1.0.0] — 2026-04-17

### Added
- `/lai-karaoke` skill — viral-ready per-word-highlighted ASS subtitles with 5 named style presets (tiktok / douyin / cinematic / neon / minimal), adaptive font size from media resolution, and agent-driven workflow decision tree.
- `/lai-translate` §Bilingual Delivery Guide — canonical reference for dual-language captions: scenario-to-format decision table, typography conventions, four end-to-end recipes (learning SRT / social ASS / karaoke / dual-track upload), and JSON round-trip property.
- `scripts/probe_media.py` — ffprobe wrapper emitting width/height/aspect/font_size/play_res as JSON, with 8-platform fallback for audio-only inputs.

### Changed
- All `lai-*` skills — CLI argument drift corrected against real `nemo_run` syntax (non-existent `-o` flags removed; `caption.ass.*` namespace replaced with flat `render.*` / `ass.*`; `lai translate run` → `lai translate caption`).
- `/lai-caption` — enumerated 12 `karaoke_color_scheme` presets, 15 `kinetic_style` options grouped by feel (Impact / Smooth / Stylized), `ass.speaker_color` accepting `auto` / CSV, and broadcast-grade `standardization.*` profiles (Netflix / YouTube).
- `/lai-align`, `/lai-youtube` — document explicit `key=value` style; `split_sentence=true` promoted from "ask-before-enabling" to recommended default for karaoke / translate / summarize.
- `/lai-diarize` — document `diarization.llm.reasoning=true` for ambiguous-speaker cases.
- Agent-driven skills (`/lai-translate`, `/lai-summarize`, `/lai-diarize`) — removed the `model: sonnet` hard requirement from frontmatter so Opus[1M] sessions do not hit `extra-usage` errors on skill load; soft preference noted in skill body.
- All karaoke recipes — dropped redundant `render.word_level=true` on the downstream `laicap-convert` side (default is already word-scope; `=false` only needed for line-scope animations).
- `summarize/scripts/validate.py` — warn loudly when `meta.md` has no YAML frontmatter (was silently skipped); skip gracefully when frontmatter has no `chapters:` key.

### Fixed
- `ass.translation_color` rendering constraint documented — only takes effect when `ass.karaoke_effect` is set; the social-video dual-color recipe now uses `karaoke_effect=instant` for zero-animation dual-color output.

## [0.1.0] — 2026-04-12

### Added
- Initial skill set: `/lai-setup`, `/lai-align`, `/lai-transcribe`, `/lai-translate`, `/lai-diarize`, `/lai-youtube`, `/lai-caption`, `/lai-summarize`.
- Agent-first translation (`chunk.py` → agent → `merge.py` → `validate.py`) and summarization (`prepare.py` → agent → `validate.py`) pipelines.

[Unreleased]: https://github.com/lattifai/lattifai-skills/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/lattifai/lattifai-skills/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/lattifai/lattifai-skills/releases/tag/v0.1.0
