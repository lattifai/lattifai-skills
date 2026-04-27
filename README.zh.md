# lattifai-skills

> 面向**支持 Agent 能力的代码 LLM** 的音频-文本对齐、转录、翻译、卡拉OK 与字幕工具箱 —— 由 [LattifAI](https://lattifai.com) Lattice-1 强制对齐模型驱动。

[English](./README.md) | **中文**

[![MIT License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)
[![Agent Skills](https://img.shields.io/badge/agent--skills-standard-2563eb)](https://agentskills.io)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-7c3aed)](https://code.claude.com/docs/en/plugins)
[![Codex CLI](https://img.shields.io/badge/Codex-marketplace-10a37f)](https://github.com/openai/codex)
[![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-skills-4285f4)](https://github.com/google-gemini/gemini-cli)
[![Skills](https://img.shields.io/badge/skills-9-10b981)](#技能一览)

> 基于 [Agent Skills 开放标准](https://agentskills.io)。每个 `SKILL.md` 都是自包含的能力单元——任何监听 `skills/` 目录的 agent 都能加载（Claude Code、OpenAI Codex CLI、Gemini CLI，或任何后续遵循该标准的 agent）。

9 个可组合 skill，覆盖从 YouTube 链接到多语言、逐词高亮、生产级字幕的完整管线。

---

## 安装

按你使用的 agent 选择对应方式。

### 方式 A — Claude Code (`/plugin marketplace`)

本仓库根目录同时携带 plugin manifest 与 plugin marketplace。在 Claude Code 会话中：

```shell
/plugin marketplace add lattifai/lattifai-skills
/plugin install lattifai-skills@lattifai-skills
/reload-plugins
```

或非交互式：

```bash
claude plugin marketplace add lattifai/lattifai-skills
claude plugin install lattifai-skills@lattifai-skills
```

所有 skill 以 plugin 命名空间挂载：

```shell
/lattifai-skills:lai-karaoke https://youtu.be/VIDEO_ID
```

### 方式 B — OpenAI Codex CLI (`codex plugin marketplace`)

同一份 `marketplace.json` 也可被 Codex CLI 直接复用：

```bash
codex plugin marketplace add lattifai/lattifai-skills
```

Codex 的 `<owner>/<repo>` source 格式与 Claude Code 完全一致，因此 `.claude-plugin/marketplace.json` 元数据可零改动复用。

### 方式 C — Gemini CLI (`gemini skills install`)

Gemini CLI 直接从 git URL 安装 skills，无需 plugin manifest：

```bash
gemini skills install https://github.com/lattifai/lattifai-skills

# 或针对本地 checkout 做实时调试：
git clone https://github.com/lattifai/lattifai-skills.git
gemini skills link ./lattifai-skills/skills
```

### 方式 D — 任意其他 agent（拖入 `SKILL.md` 目录）

每个 `skills/<name>/SKILL.md` 都自包含——agent 加载它不需要 plugin manifest。把目录直接拷到 agent 监听的位置即可：

```bash
git clone https://github.com/lattifai/lattifai-skills.git
mkdir -p .claude/skills && cp -r lattifai-skills/skills/lai-karaoke .claude/skills/
```

常见目标位置：

| Agent | 拖入路径 |
|-------|----------|
| Claude Code（项目级） | `.claude/skills/<name>/SKILL.md` |
| Claude Code（个人） | `~/.claude/skills/<name>/SKILL.md` |
| Cursor / Continue / 自定义 agent | 各自约定的 skills 目录 |

`.claude/skills/` 的改动在当前 Claude Code 会话内自动生效，无需重载命令。其他 agent 按各自约定（CC 的 `/reload-plugins` 只针对 plugin-dir / marketplace 来源；Gemini CLI 用 `gemini skills enable/disable`；不支持热重载的 agent 直接重启）。

### 更新

```shell
# Claude Code:
/plugin marketplace update lattifai-skills
# Codex CLI:
codex plugin marketplace upgrade lattifai-skills
# Gemini CLI: 重新对 URL 运行 `skills install`
```

---

## 依赖要求

不同 skill 依赖不同，按需安装。

> **重要：**`lattifai` 包依赖 `lattifai-core`，后者只发布在 LattifAI 自建 PyPI 镜像。**安装时必须带上** `--extra-index-url https://lattifai.github.io/pypi/simple/`。

```bash
# pip（默认；首次安装约 5–15 分钟）
pip install "lattifai[all]" --extra-index-url https://lattifai.github.io/pypi/simple/

# uv —— 推荐！约 10–15× 加速（宽带 ≈1 分钟）
uv pip install "lattifai[all]" --extra-index-url https://lattifai.github.io/pypi/simple/
uv pip install --reinstall-package lattifai "lattifai[all]" \
    --extra-index-url https://lattifai.github.io/pypi/simple/
# （第二条是修复一个 entry-point 名称冲突的 workaround——把 lattifai
#  最后再装一次，确保它的 `lai` 命令脚本生效。详见 `/lai-setup`。）
```

| Skill 组 | 必需 | 可选 |
|----------|------|------|
| 对齐 / YouTube / 说话人分离 | Python 3.10+、`pip install lattifai --extra-index-url https://lattifai.github.io/pypi/simple/`、[LattifAI API key](https://lattifai.com)（`lai auth trial` 免费试用） | `yt-dlp`、`ffprobe` / `ffmpeg` |
| 转录 | `pip install "lattifai[transcription]" --extra-index-url https://lattifai.github.io/pypi/simple/` | Gemini API key（`GEMINI_API_KEY`）、Parakeet / SenseVoice 模型 |
| 字幕转换 | `pip install "lattifai[captions]" --extra-index-url https://lattifai.github.io/pypi/simple/`（或完整 `lattifai[all]`） | — |
| 卡拉OK | `ffprobe`（用于自适应字号探测）；没有时回落到平台默认分辨率 | — |
| 翻译 / 摘要 | 无外部依赖 —— 这两个 skill 直接使用所在 agent 会话的 LLM | — |

首次使用请先跑 **`/lai-setup`** —— 它会安装 CLI、引导鉴权、申请免费试用 key。

---

## 技能一览

### 🚀 Workflow（端到端流水线）

| Skill | 一句话说明 |
|-------|------------|
| [`/lai-setup`](skills/lai-setup/SKILL.md) | 安装 `lattifai`、鉴权、申请免费试用、诊断环境。**从这里开始**。 |
| [`/lai-youtube`](skills/lai-youtube/SKILL.md) | YouTube 链接 → 媒体 + 对齐字幕一行命令。也覆盖 `lai youtube download`（纯下载）。 |
| [`/lai-karaoke`](skills/lai-karaoke/SKILL.md) | TikTok / Reels / 抖音 / 小红书 / 电影感 YouTube 的**爆款卡拉OK 字幕**。**字号按视频分辨率自适应**，5 个命名风格预设。 |

### 🔧 Core（单步 CLI 能力）

| Skill | 一句话说明 |
|-------|------------|
| [`/lai-transcribe`](skills/lai-transcribe/SKILL.md) | 音视频 → 带时间戳的字幕，支持 Gemini / Parakeet / SenseVoice 三种后端。 |
| [`/lai-align`](skills/lai-align/SKILL.md) | 将已有文稿精确贴合到音频（Lattice-1 强制对齐，亚帧级精度）。产出词级时间戳。 |
| [`/lai-diarize`](skills/lai-diarize/SKILL.md) | 基于 pyannote.audio 做说话人分离；真名推断由 agent 从文稿 + `meta.md` 综合推理完成。 |
| [`/lai-caption`](skills/lai-caption/SKILL.md) | 30+ 字幕格式互转（SRT / VTT / ASS / JSON / TextGrid / LRC / FCPXML / Premiere / …）。同时承载广播级 `standardization.*` 档位（Netflix / YouTube）。 |

### 🤖 Agent-driven（LLM 驱动）

以下 skill **不调用任何外部 LLM API** —— 它们直接使用宿主 agent 会话的模型能力（Claude Code、Codex CLI、Gemini CLI 等）。

| Skill | 一句话说明 |
|-------|------------|
| [`/lai-translate`](skills/lai-translate/SKILL.md) | 在保留段数、时间、说话人、词级数组的前提下翻译字幕（或生成双语）。包含官方的 **Bilingual Delivery Guide**（双语场景格式选择表 + 排版规则 + 学习/社交/卡拉OK/双字幕轨 4 条 recipe）。 |
| [`/lai-summarize`](skills/lai-summarize/SKILL.md) | 把长文稿生成结构化 markdown（frontmatter + 章节 + 原文引用 + 实体）。校验章节标题与 frontmatter 对齐、所有引用都在源文本里逐字出现。 |

---

## 快速示例

端到端示范 —— 一次会话中从 YouTube 链接到多语言 lyric video + 中英摘要：

```shell
# 1. 下载 + 词级对齐（自动清理 YouTube auto-caption 的断句）
/lai-youtube https://youtu.be/la0CaZ2R8EY

# 2. 说话人分离 + 真名推断
/lai-diarize

# 3. 翻译成中文（保留时间、说话人、word-level）
/lai-translate — 生成中文双语

# 4. 生成 TikTok / Reels 爆款卡拉OK（自动探测视频分辨率）
/lai-karaoke --style tiktok

# 5. 生成中英文总结
/lai-summarize
```

所有产物都会落到媒体文件旁边 —— 对齐 JSON、双语 SRT / ASS、各预设的 karaoke ASS、摘要 markdown。

---

## 仓库结构

```
lattifai-skills/
├── .claude-plugin/
│   ├── plugin.json          # Plugin manifest（name / version / author / …）
│   └── marketplace.json     # Marketplace 目录（使仓库可被 /plugin marketplace add 直接添加）
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
├── evals/                   # Skill 评测 / 测试样本
├── CLAUDE.md                # 仓库级约定（Claude Code 会自动加载）
├── CHANGELOG.md             # Keep a Changelog 格式；semantic-release 自动维护
├── LICENSE                  # MIT
└── README.md / README.zh.md
```

每个 skill 自包含：`SKILL.md` 是入口，`scripts/` 放 agent 调用的辅助脚本。

---

## 开发指南

```bash
# 克隆
git clone https://github.com/lattifai/lattifai-skills.git
cd lattifai-skills

# 本地加载迭代
claude --plugin-dir .

# 改 SKILL.md 后无需重启，直接热重载：
/reload-plugins

# 校验 plugin + marketplace manifest
claude plugin validate .
```

欢迎 PR。请保持每个 skill 的 `description` frontmatter 紧凑 —— 它是 Claude 决定是否自动触发的唯一依据。

提交消息遵循 [Conventional Commits](https://www.conventionalcommits.org/)（`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`）—— `main` 分支合并后由 semantic-release 自动发版、自动生成 CHANGELOG、自动同步 `plugin.json` 与 `marketplace.json` 的 version。

---

## License

[MIT](./LICENSE) © LattifAI
