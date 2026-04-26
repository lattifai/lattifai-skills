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

```bash
# Transcribe + Align + Convert
lai transcribe run video.mp4 transcript.json
lai alignment align video.mp4 transcript.json aligned.json
laicap-convert aligned.json output.srt

# YouTube + Align + Diarize
lai youtube align "https://youtu.be/xxx" -o aligned.json
lai diarize run video.mp4 aligned.json diarized.json

# YouTube + Align + Translate (agent-driven)
lai youtube align "https://youtu.be/xxx" -o aligned.srt
# Then invoke /lai-translate for agent-driven translation
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
- Output defaults to the current directory unless `-o` / `output=` is specified
- All CLI commands support `--help` for full option listing
