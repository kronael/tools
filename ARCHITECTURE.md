# Architecture

## Repo shape

```
.claude-plugin/             marketplace.json + plugin.json
.agents/plugins/            repo-local Codex marketplace metadata
plugins/kronael/            thin Codex plugin with one sync skill
kronael/sync/               the only plugin-exposed skill — sync procedure
skills/                     bundle — auto-activating skills (languages, workflow, domain)
agents/                     bundle — specialized task agents
hooks/                      bundle — lifecycle hook scripts
output-styles/              bundle — response output style (caveman)
commands/                   bundle — slash commands (caveman)
settings-recommended.json   user-side settings to merge into ~/.claude/settings.json
codex-hooks.json            Codex hook wiring, copied to ~/.codex/hooks.json
codex/AGENTS.md             Kronael block merged into ~/.codex/AGENTS.md
RECLAUDE.md                 template for ~/.claude/RECLAUDE.md (reclaude hook input)
AGENTS.md                   notes for non-Claude agents (Codex)
COOKBOOK.md                 daily git recipes (detached HEAD with rig)
udfix/, dockbox/, rig/, ... standalone CLI tools (each independent; inventory in README.md)
```

## Sync paths, one source

The `skills/`, `agents/`, `hooks/`, `output-styles/` and `commands/`
directories at repo root are the bundle.
Every sync path puts them into `~/.claude/`.

**Claude plugin path** — Claude Code's marketplace clones this repo into its
plugin cache. `/kronael:sync` syncs the bundle into `~/.claude/` from CWD
when it holds the repo's assets, else from the cached `${CLAUDE_PLUGIN_ROOT}`.

**Claude manual path** — User clones the repo themselves, opens Claude Code at
the root, says "sync". Source is `cwd`; the rest of the procedure is
identical. Only this path can take live edits back: merge-back writes into
the owner's clone.

**Codex bridge path** — Codex installs the thin plugin from
`plugins/kronael/.codex-plugin/plugin.json` via
`.agents/plugins/marketplace.json`. The only Codex skill is
`plugins/kronael/skills/kronael-sync/SKILL.md`; it reads
`kronael/sync/SKILL.md` from the GitHub marketplace snapshot and syncs the
bundle into `~/.claude/`. It does not duplicate the bundle into the plugin cache.

Codex does not discover `~/.claude/CLAUDE.md` as global guidance. The bridge
writes the `codex/AGENTS.md` block into a real `~/.codex/AGENTS.md`, and the
block tells Codex to read the wisdom file. The block stays out of the wisdom
file, because a sync merges live edits to it into source.
An existing `AGENTS.override.md` is a conflict.

Codex does not scan `~/.claude/skills`. If the user wants the installed Claude
skills available inside Codex, the sync bridge exposes them with
`~/.agents/skills -> ~/.claude/skills` when possible. If
`~/.agents/skills` already exists as a directory, it adds per-skill symlinks
for source-owned Kronael skills. Codex invokes those bridged skills as
`@skill-name`, and `codex_hook.py` rewrites installed hook nudges from
Claude-style `/skill` to Codex-style `@skill`.

The procedure is documented in
[`kronael/sync/SKILL.md`](kronael/sync/SKILL.md) — the single source of
truth for all paths. Codex/non-Claude agents follow
[`AGENTS.md`](AGENTS.md).

## Codex guidance bridge

Codex can be configured to consume Claude project conventions without copying
them:

- `~/.codex/config.toml`: add `CLAUDE.md` to
  top-level `project_doc_fallback_filenames` for Claude-only projects.
- Global installed wisdom: the Kronael block in `~/.codex/AGENTS.md` tells
  Codex to read `~/.claude/CLAUDE.md`.
- Projects that already have `AGENTS.md`: keep a short `AGENTS.md` pointer to
  `CLAUDE.md`, because Codex loads at most one instruction file per directory.
- Project `.claude/skills`: expose them to Codex with
  `.agents/skills -> ../.claude/skills` symlinks when requested.
- Global installed Kronael skills: expose them to Codex with
  `~/.agents/skills -> ~/.claude/skills` when requested.

## Why hybrid (plugin + sync step)

A pure-plugin design would register skills/agents/hooks via
`plugin.json` and skip the copy step. The hybrid design exists for
three practical reasons that pure-plugin doesn't provide:

**1. Live is a working copy, and its edits come home.** Three sides:
**source** (this repo), **live** (`~/.claude/` on a host — the running
bundle), and **upstream** (the `origin` remote). The user customizes skills,
fixes bugs in hooks and adds personal patterns in live. The next sync merges
those edits into their clone, where they can be committed and PR'd upstream,
then rebuilds live from the clone. A pure-plugin install is read-only — every
edit is overwritten on update. Sync reconciles source ↔ live; push reaches
upstream, and live never assumes it matches upstream.

**2. LLM-coordinated merges, not blind overrides.** The sync step is an LLM
following a procedure (`kronael/sync/SKILL.md`), not a blind `cp -r`. It
merges live edits three-way, surfaces conflicts, keeps local paths and
secrets out of the public repo (into `LOCAL.md`), asks before overwriting
relaxed settings, carries the owner's installed-only files (overlays,
private skills) across by the keep-list rule, and never touches
`settings.local.json` or `CLAUDE.local.md`. A pure-plugin update can't do
any of that — it just replaces files.

**3. Nothing stale accumulates.** Each sync rebuilds the bundle from source
plus the installed-only paths the keep-list rule keeps, and moves the old
bundle to `/tmp`, so a file the source renamed or dropped cannot keep
loading next to its replacement.

This is the basis of **evolvability and modularity** of the setup:
the user's `~/.claude/` is a working surface, not a frozen artifact.
The plugin system provides distribution and update detection; the
sync step provides the smart merge. Each layer does one thing.

## Sync strategies

| Target | Strategy |
|---|---|
| `skills/`, `agents/`, `hooks/`, `output-styles/`, `commands/` | Live edits merge three-way into source first; then rebuilt from source plus the installed-only paths that `kronael/sync/reference.md` § Keep-list keeps; the old copy moves to `/tmp` |
| `~/.claude/CLAUDE.md` | Same, against the `skills/global/SKILL.md` body |
| `~/.codex/AGENTS.md` | Merge the `codex/AGENTS.md` block (markers only) |
| `~/.claude/settings.json` | Merge from `settings-recommended.json` (diff, ask; the always-apply keys of `kronael/sync/SKILL.md` step 5 skip the ask) |
| `~/.claude/settings.local.json`, `CLAUDE.local.md` | NEVER touch |
| `~/.claude/LOCAL.md` | Receives only the private hunks a merge keeps out of source |

The old bundle and backups of `settings.json`, `~/.claude.json` and the
`~/.codex/` guidance, config and hook files go to a run dir under `/tmp`,
which the OS clears on reboot.

## Runtime flow

```
1. Claude Code starts in a project
2. Loads ~/.claude/CLAUDE.md (global wisdom)
3. Loads ./CLAUDE.md (project conventions)
4. Hooks fire on UserPromptSubmit / PreToolUse / PostToolUse / Stop / PreCompact
5. Skills auto-activate by file extension or config file
6. Agents launched by a skill, or explicitly (`@improve`)
```

## Components

**Skills** auto-activate by file context and provide workflow slash
commands. The `global` skill becomes `~/.claude/CLAUDE.md`. Index,
rationale, and workflow diagram: [`skills/README.md`](skills/README.md).

**Agents** are task workers that skills launch;
[`skills/CLAUDE.md` § Agent definitions](skills/CLAUDE.md#agent-definitions)
owns that rule.

**Hooks** wire the lifecycle events above; the wiring is defined in
`settings-recommended.json`. Per-hook rationale and data flow:
[`hooks/README.md`](hooks/README.md),
[`hooks/ARCHITECTURE.md`](hooks/ARCHITECTURE.md).

## Org overlays

Org-specific skills live in separate repos layered on top of the base
sync:

```
ln -s <org-repo>/skills/<org> ~/.claude/skills/<org>
```

A sync keeps an overlay symlinked directly under `skills/`, as above,
without a keep-list line, and a copied one only by a keep-list line.
[The keep-list rule](kronael/sync/reference.md#keep-list-steps-0-1-3-4) in
`kronael/sync/reference.md` owns this. Overlays never enter this repo
without the owner's yes.
