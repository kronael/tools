# tools

Command-line utilities and Claude Code configuration.

## CLI tools

- [dockbox](dockbox/) — dockerized Claude Code sandbox
- [rig](rig/) — ripgit: smart branch checkout, push, rebase, merge
- [tw-fetch](tw-fetch/) — Twitter/X thread archiver

Each has its own Makefile. `cd <tool> && make install`.

External tools used by the Claude Code config:

- [ship](https://github.com/kronael/ship) — planner-worker-judge CLI
- [agent-browser](https://www.npmjs.com/package/agent-browser) — headless browser automation

## Claude Code toolkit

This repo is a [Claude Code plugin marketplace](.claude-plugin/marketplace.json). Install via:

```
/plugin marketplace add kronael/tools
/plugin install t@kronael-tools
/t:install
```

Or install manually — see [INSTALL.md](INSTALL.md).

### What's in the bundle

**Skills** auto-activate by file context (Rust → `/rs` patterns, Dockerfile → `/ops`, etc.) and provide workflow commands (`/commit`, `/ship`, `/refine`, `/diary`). The `global` skill carries development wisdom (startup protocol, terse response style, boring-code philosophy) and is installed as `~/.claude/CLAUDE.md`.

**Agents** are specialized task workers: `@distill`, `@improve`, `@learn`, `@readme`, `@refine`, `@visual`. Most are launched via slash commands (`/refine` → `@refine`, etc.).

**Hooks** wire lifecycle events:
- `nudge` (UserPromptSubmit) — fuzzy-match keywords to agents/skills
- `local` (UserPromptSubmit, PreCompact) — inject `~/.claude/LOCAL.md`
- `reclaude` (PreCompact) — re-inject critical rules across compaction
- `learn` (PreCompact, SessionEnd) — write flow reports for `@learn`
- `stop` (Stop) — block on uncommitted changes / missing diary entries

### Layout

```
.claude-plugin/         marketplace.json + plugin.json
t/install/SKILL.md      the only plugin-exposed skill (installer)
skills/                 bundle copied to ~/.claude/skills/
agents/                 bundle copied to ~/.claude/agents/
hooks/                  bundle copied to ~/.claude/hooks/
settings-recommended.json   merged into ~/.claude/settings.json
RECLAUDE.md             template for ~/.claude/RECLAUDE.md
INSTALL.md              manual install procedure
ARCHITECTURE.md         component details
WORKFLOW.md             agent hierarchy
usage-patterns/         12 patterns extracted from production projects
```

### Working on this repo

- ALWAYS keep files under 200 lines
- ALWAYS use ALWAYS/NEVER/SHOULD statements in skill content
- Focus on non-obvious patterns LLMs fail to grasp
- Test by re-running `/t:install` (or "say install") and using in a real project
- NEVER include local paths, org-specific refs, or secrets in source files (those go in `~/.claude/LOCAL.md`, auto-injected by the `local` hook)
