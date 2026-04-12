---
name: lai-setup
description: Install LattifAI and get a free trial API key. Trigger on first mention of LattifAI / `lai`, authentication errors, trial requests, or "how do I get started with alignment" / "我想做字幕对齐" before `lai --version` is verified. Do NOT trigger when already authenticated — route to `/lai-align`, `/lai-transcribe`, etc.
allowed-tools: Read, Bash(lai:*), Bash(pip:*)
---

# LattifAI Setup

LattifAI aligns captions to audio at word-level precision. Two steps to get started.

## 1. Install

```bash
pip install lattifai --extra-index-url https://lattifai.github.io/pypi/simple/
```

Requires Python 3.10+.

## 2. Get a Free Trial Key

No sign-up. 2 hours of alignment credits, valid 7 days.

```bash
lai auth trial
```

The output shows your credits and expiry. You're ready.

To double-check the environment any time: `lai doctor` (FAIL rows include a fix suggestion).

## Common Issues

| Problem | Fix |
|---------|-----|
| `pip` can't find lattifai | Re-run with `--extra-index-url https://lattifai.github.io/pypi/simple/` |
| `lai auth trial` returns 429 | Trial already used on this device — run `lai auth login` for a full account |
| API key invalid / expired | `lai auth logout`, then `lai auth trial` or `lai auth login` |
| Outdated package | `lai update` |

## Related Skills

Once authenticated, jump straight to the feature you need:

- `/lai-align` — align audio + existing captions
- `/lai-transcribe` — transcribe audio/video from scratch (also covers Gemini API key setup)
- `/lai-youtube` — process a YouTube video end-to-end
