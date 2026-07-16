# Architecture

## Repo shape

```
.claude-plugin/             marketplace.json + plugin.json
.agents/plugins/            repo-local Codex marketplace metadata
plugins/kronael/            thin Codex plugin with one installer skill
kronael/install/            the only plugin-exposed skill — install procedure
skills/                     bundle — auto-activating skills (languages, workflow, domain)
agents/                     bundle — specialized task agents
hooks/                      bundle — lifecycle hook scripts
settings-recommended.json   user-side settings to merge into ~/.claude/settings.json
RECLAUDE.md                 template for ~/.claude/RECLAUDE.md (reclaude hook input)
AGENTS.md                   notes for non-Claude agents (Codex)
COOKBOOK.md                 daily git recipes (detached HEAD with rig)
udfix/, dockbox/, rig/, ... standalone CLI tools (each independent; inventory in README.md)
```

## Install paths, one source

The `skills/`, `agents/`, `hooks/` directories at repo root are the bundle.
All install paths copy them into `~/.claude/`.

**Claude plugin path** — Claude Code's marketplace clones this repo into its
plugin cache. `/kronael:install` reads the cached repo at
`${CLAUDE_PLUGIN_ROOT}` and copies the bundle to `~/.claude/`.

**Claude manual path** — User clones the repo themselves, opens Claude Code at
the root, says "install". Source is `cwd`; the rest of the procedure is
identical.

**Codex bridge path** — Codex installs the thin plugin from
`plugins/kronael/.codex-plugin/plugin.json` via
`.agents/plugins/marketplace.json`. The only Codex skill is
`plugins/kronael/skills/kronael-install/SKILL.md`; it reads
`kronael/install/SKILL.md` from the GitHub marketplace snapshot and deploys the
bundle to `~/.claude/`. It does not duplicate the bundle into the plugin cache.

Codex does not discover `~/.claude/CLAUDE.md` as global guidance. The bridge
exposes it with `~/.codex/AGENTS.md -> ~/.claude/CLAUDE.md`; an existing
`AGENTS.override.md` or unrelated `AGENTS.md` is a merge conflict.

Codex does not scan `~/.claude/skills`. If the user wants the installed Claude
skills available inside Codex, the install bridge exposes them with
`~/.agents/skills -> ~/.claude/skills` when possible. If
`~/.agents/skills` already exists as a directory, it adds per-skill symlinks
for source-owned Kronael skills. Codex invokes those bridged skills as
`@skill-name`, and `codex_hook.py` rewrites installed hook nudges from
Claude-style `/skill` to Codex-style `@skill`.

The procedure is documented in
[`kronael/install/SKILL.md`](kronael/install/SKILL.md) — the single source of
truth for all paths. Codex/non-Claude agents follow
[`AGENTS.md`](AGENTS.md).

## Codex guidance bridge

Codex can be configured to consume Claude project conventions without copying
them:

- `~/.codex/config.toml`: add `CLAUDE.md` to
  top-level `project_doc_fallback_filenames` for Claude-only projects.
- Global installed wisdom: expose it with
  `~/.codex/AGENTS.md -> ~/.claude/CLAUDE.md`.
- Projects that already have `AGENTS.md`: keep a short `AGENTS.md` pointer to
  `CLAUDE.md`, because Codex loads at most one instruction file per directory.
- Project `.claude/skills`: expose them to Codex with
  `.agents/skills -> ../.claude/skills` symlinks when requested.
- Global installed Kronael skills: expose them to Codex with
  `~/.agents/skills -> ~/.claude/skills` when requested.

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
| `~/.codex/AGENTS.md` | Symlink to `~/.claude/CLAUDE.md` (conflict, ask) |
| `~/.claude/settings.json` | Merge from `settings-recommended.json` (diff, ask) |
| `~/.claude/settings.local.json` | NEVER touch |
| `~/.claude/LOCAL.md`, `CLAUDE.local.md` | NEVER touch |

Backup `~/.claude/` to `~/.claude/backup/<timestamp>/` before overwriting.

## Runtime flow

```
1. Claude Code starts in a project
2. Loads ~/.claude/CLAUDE.md (global wisdom)
3. Loads ./CLAUDE.md (project conventions)
4. Hooks fire on UserPromptSubmit / PreToolUse / PostToolUse / Stop / PreCompact
5. Skills auto-activate by file extension or config file
6. Agents invoked explicitly (`/refine`, `@improve`) or by delegation
```

## Components

**Skills** auto-activate by file context and provide workflow slash
commands. The `global` skill becomes `~/.claude/CLAUDE.md`. Index,
rationale, and workflow diagram: [`skills/README.md`](skills/README.md).

**Agents** are task workers, mostly dispatched by slash-command wrappers.

**Hooks** wire the lifecycle events above; the wiring is defined in
`settings-recommended.json`. Per-hook rationale and data flow:
[`hooks/README.md`](hooks/README.md),
[`hooks/ARCHITECTURE.md`](hooks/ARCHITECTURE.md).

## Org overlays

Org-specific skills live in separate repos layered on top of the base
install:

```
cp -r <org-repo>/skills/<org> ~/.claude/skills/
```

The install procedure never deletes skills not in source — overlays
persist across updates.
