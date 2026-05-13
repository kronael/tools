# Changelog

## [v0.2.1] — 20260513

### Changed
- Skill quality pass: 21 skills refined against 10 top-tier external repos (anthropics/skills, obra/superpowers, wshobson, voltagent, hesreallyhim, qdhenry, 0xfurai, alirezarezvani, lst97). Every change filtered through 2+ source corroboration + codex (oracle) critique + wisdom-skill terseness pass.
- meta (wisdom, global, learn, specs, sub): description=triggers; offload heavy content to references/; completion claims need evidence; verify subagent results; transcript reading + N≥2 rule for skill extraction; specs anti-pattern list + self-review checklist; sub never bare prompt.
- workflow (ship, refine, fin, recall-memories, distill, testing): refine triage substep; recall-memories freshness check; testing verify-failure-for-right-reason; distill trigger-form description; fin grind-harder framing.
- language (ts, sh, py, rs, tsx): ts satisfies/branded/discriminated/exhaustive/unknown/import-type; sh strict mode + mktemp+trap + NUL-safe iter; py Protocol over ABC; rs MIRI for unsafe + adapter DTOs.
- domain (service, data, ops, agent-browser, oracle, cli, create-eval, diary): service correlation-IDs + stable error shape; data idempotent upsert + schema versioning + validate before persist; ops SLO+burn-rate alerts + runbook URL; agent-browser wait-before-snapshot + locator priority + error screenshot; oracle targeted context + verify before adopting; create-eval programmatic assertions.
- visual: broadened triggers (components, landing pages, dashboards).
- improve: NOT-for-explain in description; expanded triggers.
- explore: `allowed-tools` frontmatter for mechanical read-only enforcement.

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
