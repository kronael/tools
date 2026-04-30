# tools

Command-line utilities and Claude Code configuration.

## CLI tools

- [dockbox](dockbox/) — dockerized Claude Code sandbox
- [rig](rig/) — ripgit: smart branch checkout, push, rebase, merge
- [tw-fetch](tw-fetch/) — Twitter/X thread archiver
- [tg-fetch](tg-fetch/) — Telegram channel/group archiver (telethon, TOML config)
- [dc-fetch](dc-fetch/) — Discord channel archiver (discum, `DISCORD_TOKEN` env)
- [clp](clp/) — claude project picker (experimental; sourceable bash function)

PEP 723 inline-deps Python scripts (`tg-fetch`, `dc-fetch`) run via `uv run main.py`. `dockbox` and `rig` have their own Makefile; `cd <tool> && make install`.

External tools used by the Claude Code config:

- [ship](https://github.com/kronael/ship) — planner-worker-judge CLI
- [agent-browser](https://www.npmjs.com/package/agent-browser) — headless browser automation

## Claude Code toolkit

This repo is a [Claude Code plugin marketplace](.claude-plugin/marketplace.json). Install via:

```
/plugin marketplace add kronael/tools
/plugin install kronael@kronael
/kronael:install
```

Or open Claude Code at the repo root and say **"install"** — it auto-loads `CLAUDE.md`, which dispatches to [`kronael/install/SKILL.md`](kronael/install/SKILL.md) (the single source of truth for the install procedure).

### Why an install step (instead of pure plugin)

The plugin distributes the bundle; the install step copies it into `~/.claude/` so it's *yours*. Two reasons this matters: **(1)** your `~/.claude/` becomes a working copy you can edit, customize, and PR back upstream — a pure-plugin install would overwrite your edits on every update. **(2)** the install step is an LLM running a procedure: it diffs before overwriting, asks about conflicts, extracts your local paths/secrets to `LOCAL.md`, and never touches `settings.local.json`. Plugin-only updates can't do that.

This is the basis of evolvability — the bundle stays modular and user-owned. See [ARCHITECTURE.md](ARCHITECTURE.md#why-hybrid-plugin--install-step) for the full rationale.

### What's in the bundle

**Skills** auto-activate by file context (Rust → `/rs` patterns, Dockerfile → `/ops`, etc.) and provide workflow commands (`/commit`, `/ship`, `/refine`, `/diary`). The `global` skill carries development wisdom (startup protocol, terse response style, boring-code philosophy) and is installed as `~/.claude/CLAUDE.md`.

**Agents** are specialized task workers: `@distill`, `@improve`, `@learn`, `@readme`, `@refine`, `@visual`. Most are launched via slash commands (`/refine` → `@refine`, etc.).

**Hooks** wire lifecycle events:
- `nudge` (UserPromptSubmit) — fuzzy-match keywords to agents/skills
- `local` (UserPromptSubmit, PreCompact) — inject `~/.claude/LOCAL.md`
- `reclaude` (UserPromptSubmit, PreCompact) — re-inject critical rules across compaction
- `stop` (Stop) — block on uncommitted changes / missing diary entries

### Layout

```
.claude-plugin/                    marketplace.json + plugin.json
kronael/install/SKILL.md     plugin-exposed install procedure (source of truth)
skills/                            bundle copied to ~/.claude/skills/
agents/                            bundle copied to ~/.claude/agents/
hooks/                             bundle copied to ~/.claude/hooks/
settings-recommended.json          merged into ~/.claude/settings.json
RECLAUDE.md                        template for ~/.claude/RECLAUDE.md
usage-patterns/                    12 patterns extracted from production projects
```

## Documentation

| Doc | Purpose |
|-----|---------|
| [CLAUDE.md](CLAUDE.md) | Repo conventions for Claude Code (auto-loaded each session) |
| [AGENTS.md](AGENTS.md) | Same conventions + bash install runbook for Codex / non-Claude agents |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Repo shape, install paths, sync strategies, org overlays |
| [WORKFLOW.md](WORKFLOW.md) | Agent hierarchy: `/ship` → `/build` → `/refine` → leaf agents |
| [COOKBOOK.md](COOKBOOK.md) | Daily git recipes — detached-HEAD with `rig`, `dockbox`, and the toolkit |
| [skills/README.md](skills/README.md) | Skill rationale by family: memory, refinement, shortcuts |
| [hooks/README.md](hooks/README.md) | Hook system overview |
| [hooks/ARCHITECTURE.md](hooks/ARCHITECTURE.md) | Per-hook data flow |
| [kronael/install/SKILL.md](kronael/install/SKILL.md) | Install procedure (followed by both plugin and "say install") |

### Working on this repo

- ALWAYS keep files under 200 lines
- ALWAYS use ALWAYS/NEVER statements in skill content
- Focus on non-obvious patterns LLMs fail to grasp
- Test by re-running `/kronael:install` (or "say install") and using in a real project
- NEVER include local paths, org-specific refs, or secrets in source files (those go in `~/.claude/LOCAL.md`, auto-injected by the `local` hook)
