# Architecture

## Repo shape

```
.claude-plugin/             marketplace.json + plugin.json
.agents/plugins/            repo-local Codex marketplace metadata
plugins/kronael/            thin Codex plugin with one sync skill
kronael/sync/               the only plugin-exposed skill — sync procedure
skills/                     bundle — skills (languages, workflow, domain)
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
BUGS.md                     open issues
NOTICE                      upstream attribution
docs/                       research notes behind individual skills
evals/                      eval examples for the skill auto-improvement loop
lints/                      fixture harness for the ast-grep lint rules (make lints)
research/                   research behind the skill auto-improvement design
specs/                      design specs, indexed in specs/index.md
tests/                      repo-level tests (qemubox/dockbox alias drift)
.github/                    CI workflows, generated from .github/templates/
sgconfig.yml                ast-grep config listing the skill lint rule dirs
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
identical. On every path, merge-back writes live edits into the clone the
sync runs from; a plugin-cache or marketplace snapshot cannot take them.

**Codex bridge path** — Codex installs the thin plugin from
`plugins/kronael/.codex-plugin/plugin.json` via
`.agents/plugins/marketplace.json`. The only Codex skill is
`plugins/kronael/skills/kronael-sync/SKILL.md`; it reads
`kronael/sync/SKILL.md` from a clone in the current directory's ancestors,
else from the GitHub marketplace snapshot, and syncs the bundle into
`~/.claude/`. It does not duplicate the bundle into the plugin cache.

What the bridge writes for Codex — global guidance, config, skills, hooks —
is [`kronael/sync/reference.md` § Codex bridge](kronael/sync/reference.md#codex-bridge-step-6).
Its Kronael block lives in `~/.codex/AGENTS.md`, never in the wisdom file,
because a sync merges live edits to the wisdom file into source.

The procedure is documented in
[`kronael/sync/SKILL.md`](kronael/sync/SKILL.md) — the single source of
truth for all paths. Codex/non-Claude agents follow
[`AGENTS.md`](AGENTS.md).

## Why hybrid (plugin + sync step)

A pure-plugin design would register skills/agents/hooks via
`plugin.json` and skip the copy step. The hybrid design exists for
three reasons that pure-plugin doesn't provide:

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
relaxed settings, carries the owner's private skills across by the keep-list
rule (org overlays install as plugins, § Org overlays), and never touches
`settings.local.json` or `CLAUDE.local.md`. A pure-plugin update can't do
any of that — it just replaces files.

**3. Nothing stale accumulates.** Each sync rebuilds the bundle from source
plus the installed-only paths the keep-list rule keeps, and moves the old
bundle to `/tmp`, so a file the source renamed or dropped cannot keep
loading next to its replacement.

The plugin system distributes the bundle and detects updates; the sync
step merges.

## Sync strategies

| Target | Strategy |
|---|---|
| `skills/`, `agents/`, `hooks/`, `output-styles/`, `commands/` | Live edits merge three-way into source first; then rebuilt from source plus the installed-only paths that `kronael/sync/reference.md` § Keep-list keeps; the old copy moves to `/tmp` |
| `~/.claude/CLAUDE.md` | Same, against the `skills/global/SKILL.md` body |
| `~/.codex/AGENTS.md` | Merge the `codex/AGENTS.md` block (markers only) |
| `~/.claude/settings.json` | Merge from `settings-recommended.json` (diff, ask; the always-apply keys of `kronael/sync/reference.md` § Settings skip the ask) |
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
5. Skills load on dispatch (`/solve`, `/<name>`) or on a description match
6. Agents launched by a skill, or explicitly (`@improve`)
```

## Components

**Skills** load on dispatch (`/solve`, `/<name>`) or on a description
match, and provide workflow slash commands. The `global` skill becomes `~/.claude/CLAUDE.md`. Index,
rationale, and workflow diagram: [`skills/README.md`](skills/README.md).

**Agents** are task workers that skills launch;
[`skills/CLAUDE.md` § Agent definitions](skills/CLAUDE.md#agent-definitions)
owns that rule.

**Hooks** wire the lifecycle events above; the wiring is defined in
`settings-recommended.json`. Per-hook rationale and data flow:
[`hooks/README.md`](hooks/README.md),
[`hooks/ARCHITECTURE.md`](hooks/ARCHITECTURE.md).

## Org overlays

Org-specific skills live in separate repos and install as Claude Code
plugins. The org repo ships `.claude-plugin/marketplace.json`. ALWAYS add the
marketplace from its git or GitHub source, NEVER from a local path:

```
claude plugin marketplace add <owner>/<org-repo>
claude plugin install <plugin>@<marketplace>
```

Claude Code copies a plugin from a git or GitHub marketplace into
`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. A plugin from a
marketplace added by local path loads in place from the checkout, and a box
that does not mount the checkout misses it. The sync never touches
`~/.claude/plugins`, and both boxes mount it read-only, so the copied skills
load on the host and in the boxes, with two limits:

- `qemubox -U` mounts no host config and no plugins.
- dockbox writes the box's `settings.json`, which holds `enabledPlugins`, once
  when it creates the box. A box created before the install keeps the plugin
  disabled until the box is recreated.

Codex never loads a Claude plugin. It reads skills from `~/.agents/skills`,
which the Codex bridge links to `~/.claude/skills`, and installs its own
plugins (`AGENTS.md` § Codex plugin usage).

A skill copied into `~/.claude/skills` survives a sync only by a keep-list
line. A symlinked one is kept without a line, but a box resolves a skill link
only when it also mounts the link's target.
[The keep-list rule](kronael/sync/reference.md#keep-list-steps-0-1-3-4) in
`kronael/sync/reference.md` owns the sync side. Overlays never enter this repo
without the owner's yes.
