# Changelog

## [v0.2.0] — 20260520

> kronael v0.2.0 — plugin-first install, flat layout, sharper skills
>
> Install by cloning to /tmp and saying "install" — Claude reads CLAUDE.md and runs the procedure.
>
> • Plugin renamed kronael-tools → kronael — shorter install command
> • Flat layout: skills/, agents/, hooks/ at repo root (no more assistants/ nesting)
> • "Say install" elevated as primary path — git clone + cd + claude + "install"
> • skills/global/ no longer copied as a skill — body goes only to ~/.claude/CLAUDE.md
> • browse skill replaces agent-browser — clearer name, no Agent subagent confusion
> • All 35 skills carry USE/NOT descriptions for unambiguous dispatch
> • ops skill: Python+uv patterns, per-deployable subdir layout, Dockerfile multi-stage
> • release skill: monorepo support, distill blockquote broadcast format, first-release rules
> • ARCHITECTURE: hybrid plugin+install rationale documented (evolvability basis)
> • AGENTS: full Codex bash install runbook with backup, awk frontmatter strip, jq merge
> • COOKBOOK: detached-HEAD recipes with rig and dockbox

### Added

- `browse` skill (renamed from `agent-browser`) — browser automation via CLI, never as subagent type
- `COOKBOOK.md` — detached-HEAD workflow recipes with rig
- `skills/README.md` — skill families rationale
- `ARCHITECTURE.md` § Why hybrid — evolvability and LLM-coordinated merge rationale
- Full Codex install runbook in `AGENTS.md`
- `ops` skill: uvx single-file scripts, Python+uv Makefile/Dockerfile patterns, per-deployable layout

### Changed

- Plugin renamed `kronael-tools` → `kronael`; trigger phrases: "install kronael" + "install kronael tools"
- Flat repo layout: bundle at root instead of `assistants/`
- `skills/global/` skipped during install copy — body goes only to `~/.claude/CLAUDE.md`
- README: `git clone /tmp/kronael + claude + "install"` as primary install path
- All 35 skill descriptions rewritten in USE/NOT format
- `release` skill: monorepo version files, distill blockquote broadcast format, first-release handling
- `INSTALL.md` dropped — `kronael/install/SKILL.md` is the single source of truth

### Fixed

- `agent-browser` no longer spawnable as `Agent(subagent_type=...)` — renamed + description clarified
- `ops` skill: dropped `make lint` pattern (linting belongs in pre-commit only)
