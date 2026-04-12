# lattifai-skills

Claude Code skills for the [LattifAI](https://lattifai.com) audio-text alignment platform.

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| [lai-setup](skills/lai-setup/SKILL.md) | CLI | Installation, authentication, trial, diagnostics |
| [lai-align](skills/lai-align/SKILL.md) | CLI | Precision forced alignment (Lattice-1 model) |
| [lai-transcribe](skills/lai-transcribe/SKILL.md) | CLI | Multi-model transcription (Gemini, Parakeet, SenseVoice) |
| [lai-translate](skills/lai-translate/SKILL.md) | Agent | Agent-driven caption translation |
| [lai-diarize](skills/lai-diarize/SKILL.md) | CLI | Speaker diarization with label inference |
| [lai-youtube](skills/lai-youtube/SKILL.md) | CLI | YouTube download + alignment workflow |
| [lai-caption](skills/lai-caption/SKILL.md) | CLI | Caption format conversion (30+ formats) |
| [lai-summarize](skills/lai-summarize/SKILL.md) | Agent | Agent-driven content summarization |

## Quick Start

```bash
pip install lattifai
lai auth trial          # Free trial, no sign-up
lai doctor              # Verify environment
```

## License

MIT
