# LattifAI Skills

Claude Code skills for the LattifAI audio-text alignment platform.

## Skill Registry

| Skill | Type | Description |
|-------|------|-------------|
| `/lai-setup` | CLI | Installation, authentication, trial, diagnostics |
| `/lai-align` | CLI | Precision forced alignment (Lattice-1 model) |
| `/lai-transcribe` | CLI | Multi-model transcription (Gemini, Parakeet, SenseVoice) |
| `/lai-translate` | Agent | Agent-driven caption translation |
| `/lai-diarize` | CLI | Speaker diarization with label inference |
| `/lai-youtube` | CLI | YouTube download + alignment workflow |
| `/lai-caption` | CLI | Caption format conversion (30+ formats) |
| `/lai-summarize` | Agent | Agent-driven content summarization |

## Prerequisites

- Python 3.10+
- `pip install lattifai --extra-index-url https://lattifai.github.io/pypi/simple/` (or `"lattifai[all]"` for full features)
- LattifAI API key (alignment) -- free trial via `lai auth trial`
- Gemini API key (transcription) -- optional, from https://aistudio.google.com/apikey

## Typical Workflows

Pick a single `<base>` per pipeline run (video ID, media stem, or any short slug) and reuse it for every artifact. Files all land in the current directory.

```bash
# Transcribe + Align + Convert (local media named podcast.mp4)
lai transcribe run podcast.mp4 podcast.transcript.json
lai alignment align podcast.mp4 podcast.transcript.json podcast.aligned.json
laicap-convert podcast.aligned.json podcast.srt

# YouTube + Align + Diarize (video ID la0CaZ2R8EY)
lai youtube align "https://youtu.be/la0CaZ2R8EY" caption.output.path=la0CaZ2R8EY.aligned.json
lai diarize run la0CaZ2R8EY.mp4 la0CaZ2R8EY.aligned.json la0CaZ2R8EY.diarized.json

# YouTube + Align + Translate (agent-driven)
lai youtube align "https://youtu.be/la0CaZ2R8EY" caption.output.path=la0CaZ2R8EY.aligned.json
# Then invoke /lai-translate la0CaZ2R8EY.aligned.json -l zh
```

## Configuration

All `lai` CLI settings can be persisted in `~/.lattifai/config.toml`:

```bash
lai config set GEMINI_API_KEY sk-xxx
lai config set transcription.model_name gemini-2.5-flash
lai config list
```

## Conventions

- All skills use `lai` CLI commands via `Bash(lai:*)` except agent-driven skills
- Agent-driven skills (`lai-translate`, `lai-summarize`) use the agent's own LLM capability
- All CLI commands support `--help` for full option listing

### File path conventions

Every skill writes its outputs into the **current working directory** by default. No subdirectories, no hidden directories, no environment variables.

Pick a `<base>` once, reuse it for every step in the pipeline:

| Source of `<base>` | Example |
|--------------------|---------|
| YouTube URL → video ID | `la0CaZ2R8EY` |
| local media file → stem (no ext) | `podcast` (from `podcast.mp3`) |
| no media yet → user-supplied or `untitled` | `untitled` |

File names follow `<base>.<derivation>.<ext>` so a sorted `ls` shows the pipeline left-to-right:

| Stage | File | Producer |
|-------|------|----------|
| YouTube media | `<base>.mp4` / `<base>.en.vtt` / `<base>.meta.md` | `/lai-youtube`, `yt-dlp` |
| transcription | `<base>.transcript.json` | `/lai-transcribe` |
| forced alignment | `<base>.aligned.json` | `/lai-align`, `/lai-youtube align` |
| diarization | `<base>.diarized.json` | `/lai-diarize` |
| translation chunking | `<base>.chunks.json` | `/lai-translate` chunk.py |
| agent translation data | `<base>.translation.json` | `/lai-translate` (agent step) |
| merged JSON (source + translation) | `<base>.translated.json` | `/lai-translate` merge.py `--bilingual` JSON output |
| translation final SRT/VTT/ASS | `<base>.<lang>.srt` (replace) / `<base>.<lang>.translated.srt` (dual-line) | `/lai-translate` merge.py |
| summarization | `<base>.summary.md` | `/lai-summarize` |
| karaoke ASS | `<base>.karaoke.<style>.ass` | `/lai-karaoke`, `laicap-convert` |
| format conversion | `<base>.<ext>` (extension is the new format) | `/lai-caption`, `laicap-convert` |

End user runs:

```bash
cd ~/projects/podcast-ep3/
/lai-youtube https://youtu.be/la0CaZ2R8EY
/lai-translate la0CaZ2R8EY.aligned.json -l zh
/lai-karaoke la0CaZ2R8EY.aligned.json
```

Resulting `ls` (alphabetical = pipeline order):

```
la0CaZ2R8EY.aligned.json
la0CaZ2R8EY.chunks.json
la0CaZ2R8EY.en.vtt
la0CaZ2R8EY.karaoke.tiktok.ass
la0CaZ2R8EY.meta.md
la0CaZ2R8EY.mp4
la0CaZ2R8EY.translation.json
la0CaZ2R8EY.zh.srt
la0CaZ2R8EY.zh.translated.srt
```

Users can override per-command with `-o` / `output_path=` / `caption.output.path=`. The default rule above is what skills assume when the user doesn't specify.
