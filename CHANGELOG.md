## [0.2.0](https://github.com/lattifai/lattifai-skills/compare/v0.1.2...v0.2.0) (2026-04-28)

### Features

* **skills:** adopt cwd file-path convention across all skills ([4ab9c84](https://github.com/lattifai/lattifai-skills/commit/4ab9c8432df782b86363f93bdf09b63e77f3e477))

### Bug Fixes

* **docs:** correct Gemini install path + finalize multi-agent positioning ([8d335a8](https://github.com/lattifai/lattifai-skills/commit/8d335a849a80f0f54420eac21627e2ef46c9f979))
* **translate:** defensive srt_raw_text pop + content drift check in validator ([8a4c3f4](https://github.com/lattifai/lattifai-skills/commit/8a4c3f42712d6ea137a7b4cc6108e01e3b66c029))

### Documentation

* position lattifai-skills as agent-agnostic (Agent Skills standard) ([837471c](https://github.com/lattifai/lattifai-skills/commit/837471c1dca030590dcb77ae999dea1dc6c6eb5c))

## [0.1.2](https://github.com/lattifai/lattifai-skills/compare/v0.1.1...v0.1.2) (2026-04-27)

### Bug Fixes

* **setup,readme:** document uv install path (~15× faster) with workaround ([849e193](https://github.com/lattifai/lattifai-skills/commit/849e19332fd4ae10cbbc528faccd277dc624c06e))
* **setup:** document install duration, doctor warnings, multi-env API key ([f4b2b4c](https://github.com/lattifai/lattifai-skills/commit/f4b2b4c74051447eaf46a057153e1e2bd7bd743a))

## [0.1.1](https://github.com/lattifai/lattifai-skills/compare/v0.1.0...v0.1.1) (2026-04-27)

### Bug Fixes

* **karaoke:** forbid cross-language karaoke + document KTV color direction ([84cb708](https://github.com/lattifai/lattifai-skills/commit/84cb708b6a749478956f5da15cadfaa1935ca020)), closes [#7](https://github.com/lattifai/lattifai-skills/issues/7)
* **setup:** correct trial validity to 14 days + add dangling-install rescue ([44775ff](https://github.com/lattifai/lattifai-skills/commit/44775fffd1e81230064cb0a699bcf985ac9a56e4)), closes [#1](https://github.com/lattifai/lattifai-skills/issues/1) [#3](https://github.com/lattifai/lattifai-skills/issues/3) [#4](https://github.com/lattifai/lattifai-skills/issues/4)
* **youtube:** document prefer_audio=false ⇒ output_format=mp4 + log redirection ([4f87822](https://github.com/lattifai/lattifai-skills/commit/4f87822bf928e3c5dbfefcdb9f6ab4b1c9f956d8)), closes [#5](https://github.com/lattifai/lattifai-skills/issues/5) [#6](https://github.com/lattifai/lattifai-skills/issues/6)

### Documentation

* **readme:** clarify reload semantics for project-level vs plugin skills ([853e392](https://github.com/lattifai/lattifai-skills/commit/853e39298034f29d8f2681e6eff0b9cd1fa9c35a))

## [0.1.0](https://github.com/lattifai/lattifai-skills/compare/v0.0.0...v0.1.0) (2026-04-26)

### Features

* add 8 Claude Code skills for LattifAI platform ([257645d](https://github.com/lattifai/lattifai-skills/commit/257645d2aefa6c1bae71b07bfda8eec1fa71080b))
* package as Claude Code plugin with marketplace manifest ([dcac5d4](https://github.com/lattifai/lattifai-skills/commit/dcac5d457662c5d363ae9b4d985ffadf314bc93b))
* **skills:** add /lai-karaoke with adaptive font size and named presets ([691faf4](https://github.com/lattifai/lattifai-skills/commit/691faf452d8f052deddc02dd92bf5611abf4463f))
* **skills:** agent-first summarize/translate with helper scripts ([85d3d73](https://github.com/lattifai/lattifai-skills/commit/85d3d73d76a95ca7553c5ed1db57d4705bad0939))

### Bug Fixes

* **skills:** correct CLI arg drift + soften model frontmatter ([83f6907](https://github.com/lattifai/lattifai-skills/commit/83f69079d6539ab5eb09eaf8efbee97a056444a2))

### Documentation

* **skills:** add Bilingual Delivery Guide + drop redundant word_level flag ([b0c60d0](https://github.com/lattifai/lattifai-skills/commit/b0c60d010be6597591275efd19390192ebb6feab))
* **skills:** simplify all lai-* docs; fix word-level JSON schema ([c7d541e](https://github.com/lattifai/lattifai-skills/commit/c7d541eb03e11fe9f73131817f2d07935b9f970f))

# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Versioned entries below v0.1.0 are generated automatically by
[semantic-release](https://github.com/semantic-release/semantic-release)
from [Conventional Commits](https://www.conventionalcommits.org/).
