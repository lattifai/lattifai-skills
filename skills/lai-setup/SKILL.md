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

Requires Python 3.10+. **First install takes 5–15 minutes** on a typical broadband connection — `torch` (~80 MB), `onnxruntime`, `scipy`, `transformers`, and friends are all sizeable wheels. Subsequent installs in fresh envs are usually faster (pip wheel cache).

You may see a cosmetic `WARNING: No metadata found ... Can't uninstall 'setuptools'` line during install — this is a known anaconda + pip interop quirk and is **safe to ignore**; the install still succeeds.

## 2. Get a Free Trial Key — `lai auth trial`

> **For new users this is the only command you need.** It claims a no-sign-up trial (2 hours of alignment credits, valid 14 days). There is **no** `lai login` command — it's `lai auth trial` (new user) or `lai auth login` (existing paid account).

```bash
lai auth trial
```

The output shows your credits and expiry. You're ready.

> **API key is user-level, not env-level.** The credentials live in `~/.lattifai/config.toml` and are shared across every Python / conda env on the same machine. Switching to a fresh env does not require re-authenticating; running `lai auth trial` in a new env on a machine that already has an active trial returns *"You already have an active trial (expires …)"*. To rotate, run `lai auth logout` first.

To double-check the environment any time: `lai doctor` (FAIL rows include a fix suggestion).

**On `lai doctor` warnings:**
- *Model cache: Stale – update needed* → not actionable; the alignment models are auto-prefetched on first `lai alignment` / `lai youtube align` run. The warning lifts itself once the prefetch completes.
- *Package version: outdated* → run `lai update` to grab the latest CLI. Recommended monthly, or whenever a feature you need is in a newer release.

## Common Issues

| Problem | Fix |
|---------|-----|
| `pip` can't find lattifai or its dependency `lattifai-core` | Re-run with `--extra-index-url https://lattifai.github.io/pypi/simple/` (lattifai-core ships only on the LattifAI mirror) |
| `lai auth trial` returns 429 | Trial already used on this device — run `lai auth login` for a full account |
| API key invalid / expired (trial expires after 14 days) | `lai auth logout`, then `lai auth trial` (new device) or `lai auth login` (paid account) |
| `Couldn't load entrypoint <name>: No module named 'lattifai'` on `lai` startup | Stale editable install — `pip show lattifai` reveals `Editable project location: /path/that/no-longer-exists`. Run `pip uninstall -y lattifai lattifai-core lattifai-run k2py` then reinstall non-editable per Step 1 |
| `lai` command runs but outputs `EXPIRES_AT` warning past today | Trial key expired — re-run `lai auth trial` (new key) |
| Outdated package | `lai update` |

## Related Skills

Once authenticated, jump straight to the feature you need:

- `/lai-align` — align audio + existing captions
- `/lai-transcribe` — transcribe audio/video from scratch (also covers Gemini API key setup)
- `/lai-youtube` — process a YouTube video end-to-end
