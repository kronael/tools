# Architecture

## Repo shape

```
.claude-plugin/         marketplace.json + plugin.json
kronael-tools/install/  the only plugin-exposed skill
skills/                 bundle — auto-activating skills (languages, workflow, domain)
agents/                 bundle — specialized task agents
hooks/                  bundle — lifecycle hook scripts (Python)
settings-recommended.json  user-side settings to merge into ~/.claude/settings.json
RECLAUDE.md             template for ~/.claude/RECLAUDE.md (reclaude hook input)
INSTALL.md              manual install procedure
AGENTS.md               instructions for non-Claude agents (Codex)
WORKFLOW.md             agent hierarchy and ship/build/refine workflows
usage-patterns/         design patterns extracted from production projects
dockbox/, rig/, ...     standalone CLI tools (each independent)
```

## Two install paths, one source

The `skills/`, `agents/`, `hooks/` directories at repo root are the bundle.
Both paths copy them into `~/.claude/`.

**Plugin path** — Claude Code's marketplace clones this repo into its
plugin cache. `/kronael-tools:install` reads the cached repo at
`${CLAUDE_PLUGIN_ROOT}` and copies the bundle to `~/.claude/`.

**Manual path** — User clones the repo themselves, opens Claude Code at
the root, says "install". Same procedure, source is `cwd` instead of
`${CLAUDE_PLUGIN_ROOT}`.

## Sync strategies

| Target | Strategy |
|---|---|
| `skills/`, `agents/`, `hooks/` | Replace (preserve user-added files not in source) |
| `~/.claude/CLAUDE.md` | Merge from `skills/global/SKILL.md` body (diff, ask) |
| `~/.claude/settings.json` | Merge from `settings-recommended.json` (diff, ask) |
| `~/.claude/settings.local.json` | NEVER touch |
| `~/.claude/LOCAL.md`, `CLAUDE.local.md` | NEVER touch |

Backup `~/.claude/` to `~/.claude/backup/<timestamp>/` before overwriting.

## Runtime flow

```
1. Claude Code starts in a project
2. Loads ~/.claude/CLAUDE.md (global wisdom)
3. Loads ./CLAUDE.md (project conventions)
4. Hooks fire on UserPromptSubmit / PreCompact / Stop / SessionEnd
5. Skills auto-activate by file extension or config file
6. Agents invoked explicitly (`/refine`, `@improve`) or by delegation
```

## Components

**Skills** auto-activate by file context (`.rs` → `rs`, `Dockerfile` →
`ops`, etc.) and provide workflow commands (`/commit`, `/ship`, `/refine`,
`/diary`). The `global` skill becomes `~/.claude/CLAUDE.md`.

**Agents**: `@distill`, `@improve`, `@learn`, `@readme`, `@refine`,
`@visual`. Most are dispatched by slash-command wrappers.

**Hooks** wire lifecycle events:
- `nudge` — UserPromptSubmit fuzzy-match keywords to agents/skills
- `local` — UserPromptSubmit + PreCompact inject `~/.claude/LOCAL.md`
- `reclaude` — PreCompact re-inject critical rules across compaction
- `learn` — PreCompact + SessionEnd write flow reports for `@learn`
- `stop` — Stop block on uncommitted changes / missing diary entries

See `WORKFLOW.md` for the full agent hierarchy.
