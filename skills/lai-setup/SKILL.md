---
name: lai-setup
description: Use when the user needs to install LattifAI, authenticate, get a trial key, run diagnostics, or configure the CLI. Triggers on "install lattifai", "setup lai", "get API key", "lai auth", "lai doctor", "配置 LattifAI", or first-time LattifAI usage.
---

# LattifAI Setup

Get from zero to a working LattifAI environment in under 2 minutes.

## When to Use

- User mentions LattifAI for the first time in a project
- Need to install or update the `lai` CLI
- Authentication issues (expired key, missing key, trial expired)
- Environment diagnostics (`lai doctor`)
- Configuration management (`lai config`)

## When NOT to Use

- Already set up and authenticated -- jump to `/lai-align`, `/lai-transcribe`, etc.
- Issues with a specific feature (alignment, transcription) -- use the feature-specific skill

## Installation

### Quick Install (pip)

```bash
pip install lattifai
```

### Full Install (all optional dependencies)

```bash
pip install "lattifai[all]"
```

### From Private Index (if not on public PyPI yet)

```bash
pip install lattifai --extra-index-url https://lattifai.github.io/pypi/simple/
```

### Verify Installation

```bash
lai --version
```

## Authentication

LattifAI alignment requires an API key. Three paths to get one:

### Path 1: Free Trial (Recommended for First-Time Users)

No sign-up required. Grants 2 hours of alignment credits, valid for 7 days.

```bash
lai auth trial
```

Output shows credits remaining and expiry date. When trial expires:
- `lai auth logout` to clear, then `lai auth trial` for a new trial
- Or `lai auth login` to upgrade to a full account

### Path 2: Browser Login (Full Account)

Opens browser for OAuth login. Creates a device-bound session.

```bash
lai auth login
```

For headless / SSH environments where browser is unavailable:
1. Run `lai auth login` on the remote machine
2. Copy the printed URL to a machine with a browser
3. Complete login in the browser
4. Copy the verification code back to the terminal

### Path 3: Manual API Key

For CI/CD or when you already have a key from https://lattifai.com/dashboard/api-keys:

```bash
lai auth login --api-key
# Prompts for key input (hidden)
```

Or set the environment variable directly:

```bash
export LATTIFAI_API_KEY="your-key-here"
```

### Check Current Session

```bash
lai auth whoami
```

### Logout

```bash
lai auth logout
```

## Diagnostics

Run a full environment check:

```bash
lai doctor
```

Checks:
- OS and Python version (3.10--3.14 required)
- Package version (current vs latest)
- Editable install sync status
- GPU acceleration (CUDA, CoreML, MPS, MLX)
- Lattice-1 model cache
- API key presence and source
- Critical dependencies (k2py, onnxruntime, lattifai-core)
- Self-test (bundled data, caption roundtrip, audio loading)

**Interpreting results:**
- `OK` -- all good
- `WARN` -- non-blocking, works but suboptimal
- `FAIL` -- blocking, must fix before alignment works

Common fixes:
| Issue | Fix |
|-------|-----|
| Package outdated | `lai update` |
| Stale editable install | `lai update` or `pip install --no-deps -e .` |
| Missing dependencies | `pip install "lattifai[all]"` |
| No GPU acceleration | Install `onnxruntime-gpu` (CUDA) or use CPU (slower but works) |
| Model not cached | Runs auto-download on first `lai alignment align` |

## Configuration

Persistent settings stored in `~/.lattifai/config.toml`.

### Set a value

```bash
lai config set GEMINI_API_KEY sk-xxx
lai config set transcription.model_name gemini-2.5-flash
lai config set diarization.infer_speakers true
```

### Get a value

```bash
lai config get GEMINI_API_KEY
lai config get transcription.model_name
```

### List all settings

```bash
lai config list
```

### Key Configuration Keys

| Key | Description |
|-----|-------------|
| `LATTIFAI_API_KEY` | LattifAI API key (set via `lai auth`) |
| `GEMINI_API_KEY` | Google Gemini API key (for transcription) |
| `OPENAI_API_KEY` | OpenAI-compatible API key (for translation/summarization) |
| `OPENAI_API_BASE_URL` | Custom OpenAI-compatible endpoint |
| `transcription.model_name` | Default transcription model |
| `diarization.infer_speakers` | Auto-infer speaker names via LLM |
| `summarization.llm.model_name` | LLM model for summarization |
| `translation.llm.model_name` | LLM model for translation |

### Priority Order

For any setting: **CLI argument > config.toml > environment variable > default**

## Workflow

### Step 1 -- Check if LattifAI is installed

```bash
lai --version
```

If not installed, install with `pip install lattifai`.

### Step 2 -- Run diagnostics

```bash
lai doctor
```

Fix any FAIL issues before proceeding.

### Step 3 -- Authenticate

For new users:
```bash
lai auth trial
```

For returning users:
```bash
lai auth whoami
```

If expired or invalid:
```bash
lai auth logout
lai auth login
```

### Step 4 -- Configure API keys (if needed)

For transcription (Gemini):
```bash
lai config set GEMINI_API_KEY your-gemini-key
```

For translation/summarization (OpenAI-compatible):
```bash
lai config set OPENAI_API_KEY your-key
lai config set OPENAI_API_BASE_URL http://localhost:8000/v1  # optional
```

### Step 5 -- Verify with a quick test

```bash
lai alignment align --help
```

## Error Handling

| Condition | Action |
|-----------|--------|
| `pip install` fails | Check Python version (3.10+), try `--extra-index-url` |
| `lai auth trial` returns 429 | Trial limit reached for this device. Use `lai auth login` |
| `lai auth login` timeout | Copy URL manually to browser, paste verification code |
| `lai doctor` shows FAIL | Follow the specific fix suggestion in the output |
| API key invalid/expired | `lai auth logout` then `lai auth login` or `lai auth trial` |

## Update

```bash
lai update
```

Or force reinstall:

```bash
lai update --force
```

## Related Skills

| Skill | Use After Setup |
|-------|----------------|
| `/lai-align` | Run your first forced alignment |
| `/lai-transcribe` | Transcribe audio/video |
| `/lai-youtube` | Process YouTube videos |

## Non-Goals

- Does NOT install Python itself -- user must have Python 3.10+ pre-installed
- Does NOT manage virtual environments -- user chooses their own env manager
- Does NOT configure IDE integrations -- this is CLI-only setup
