# Changelog

## [v0.2.0] — 20260512

### Added
- `when_to_use` frontmatter field across all 33 skills — trigger phrases now separate from `description`
- oracle skill: codex CLI second-opinion, dual auth (host `~/.codex` mount or API key env)
- explore skill: read-only mode toggle (`/explore`), no code modifications
- wisdom: documents `user-invocable`, agent-launcher and mode-toggle body patterns
- global: "NEVER state factual claims without verifying first" rule
- dockbox: NVM + Node 22 pre-installed; `~/.codex` mount + `OPENAI_API_KEY`/`CODEX_API_KEY` forwarded for oracle

### Changed
- `description` trimmed to noun-phrase + NOT clause only — routing triggers moved to `when_to_use`
- dockbox: base image `node:lts`, `pnpm@latest`; claude wrapper sources nvm so Node 22 is on PATH
- dockbox: `NPM_CONFIG_PREFIX` unset before nvm (build + runtime)
- settings: dropped sandbox block (per-env, not toolkit's call)
- hooks/reinject: stop hook carries commit rules; RECLAUDE.md drops redundant copy

### Fixed
- dockbox: multiple nvm + Node version fixes across 4 commits

## [v0.1.2] — earlier

## [v0.1.1] — earlier

## [v0.1.0] — earlier
