# Architecture

## Repo shape

```
.claude-plugin/         marketplace.json + plugin.json
kronael/install/  the only plugin-exposed skill — install procedure
skills/                 bundle — auto-activating skills (languages, workflow, domain)
agents/                 bundle — specialized task agents
hooks/                  bundle — lifecycle hook scripts (Python)
settings-recommended.json  user-side settings to merge into ~/.claude/settings.json
RECLAUDE.md             template for ~/.claude/RECLAUDE.md (reclaude hook input)
AGENTS.md               instructions for non-Claude agents (Codex)
WORKFLOW.md             agent hierarchy and ship/build/refine workflows
COOKBOOK.md             daily git recipes (detached HEAD with rig)
usage-patterns/         design patterns extracted from production projects
dockbox/, rig/, ...     standalone CLI tools (each independent)
```

## Two install paths, one source

The `skills/`, `agents/`, `hooks/` directories at repo root are the bundle.
Both paths copy them into `~/.claude/`.

**Plugin path** — Claude Code's marketplace clones this repo into its
plugin cache. `/kronael:install` reads the cached repo at
`${CLAUDE_PLUGIN_ROOT}` and copies the bundle to `~/.claude/`.

**Manual path** — User clones the repo themselves, opens Claude Code at
the root, says "install". Source is `cwd`; the rest of the procedure is
identical.

The procedure is documented in [`kronael/install/SKILL.md`](kronael/install/SKILL.md) — the single source of truth for both paths. Codex/non-Claude agents follow the bash translation in [`AGENTS.md`](AGENTS.md).

## Why hybrid (plugin + install step)

A pure-plugin design would register skills/agents/hooks via
`plugin.json` and skip the copy step. The hybrid design exists for
two practical reasons that pure-plugin doesn't provide:

**1. Two-way sync, not one-way push.** The bundle in `~/.claude/`
is the user's working copy. They customize skills, fix bugs in
hooks, add personal patterns. When they want to contribute back, they
diff their `~/.claude/` against the source repo and PR the changes.
A pure-plugin install is read-only — every edit is overwritten on
update.

**2. LLM-coordinated merges, not blind overrides.** The install step
is an LLM following a procedure (`kronael/install/SKILL.md`),
not a blind `cp -r`. It diffs each destination, surfaces conflicts,
extracts user-local content to `LOCAL.md`, asks before overwriting
relaxed settings, preserves user-added skills (overlays, personal
files), and never touches `settings.local.json` / `LOCAL.md` /
`CLAUDE.local.md`. A pure-plugin update can't do any of that — it
just replaces files.

This is the basis of **evolvability and modularity** of the setup:
the user's `~/.claude/` is a working surface, not a frozen artifact.
The plugin system provides distribution and update detection; the
install step provides the smart merge. Each layer does one thing.

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

See [`WORKFLOW.md`](WORKFLOW.md) for the full agent hierarchy,
[`skills/README.md`](skills/README.md) for skill rationale by family
(memory, refinement, shortcuts), and
[`hooks/README.md`](hooks/README.md) +
[`hooks/ARCHITECTURE.md`](hooks/ARCHITECTURE.md) for hook details.

## Org overlays

Org-specific skills live in separate repos layered on top of the base
install:

```
cp -r <org-repo>/skills/<org> ~/.claude/skills/
```

The install procedure never deletes skills not in source — overlays
persist across updates.
