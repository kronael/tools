---
name: kronael-install
description: Install/update Kronael (bundle + CLI tools rig/udfix/clp/dockbox); bridge CLAUDE.md, .claude/skills, and Kronael hooks into Codex.
---

# Kronael Install

ALWAYS install the existing Claude Code bundle from the marketplace source
snapshot. NEVER copy or port the bundle into the Codex plugin directory.

The installed Codex plugin contains only this installer skill. It does NOT
contain the Kronael Claude skills. Codex sees those skills only through the
Codex Bridge (`~/.agents/skills` or project `.agents/skills`). For install
requests from Codex, create the global bridge and install Codex hook wiring
automatically after the Claude install succeeds.

## Invocation

Users usually invoke:

```text
Use @kronael-install to install/update Kronael.
```

If the user says "install kronael" without naming this skill, still run this
workflow.

If the user asks only to make Codex see the installed skills, or says skills
are missing after install, skip the install workflow and use the Codex Bridge
section.

## Source Root

For install/update requests, find the source root by checking, in order:

1. Ancestors of `cwd`.
2. Ancestors of this skill's path.
3. Codex marketplace snapshots:
   - `$CODEX_HOME/.tmp/marketplaces/*`
   - `~/.codex/.tmp/marketplaces/*`

The source root is the first directory where all of these exist:

- `kronael/install/SKILL.md`
- `skills/`
- `agents/`
- `hooks/`
- `codex-hooks.json`
- `settings-recommended.json`
- `RECLAUDE.md`

NEVER use the installed plugin cache as the bundle source unless it contains
all files above; normal plugin installs cache only this bridge skill.

If no source root is found, ask the user to run
`codex plugin marketplace add kronael/tools` or
`codex plugin marketplace upgrade kronael` (`kronael-local` for older
installs), then start a fresh Codex thread. NEVER invent paths. The Codex
plugin is only an installer bridge; the GitHub marketplace snapshot owns the
bundle.

For Codex Bridge-only requests, discover the source root when the requested
bridge step needs source-owned files (`codex-hooks.json` or per-skill symlinks).
Skip source-root discovery only for `CLAUDE.md` config fallback or the simple
`~/.agents/skills -> ~/.claude/skills` symlink case.

## Install

1. Read `kronael/install/SKILL.md` completely.
2. Follow it as the source of truth.
3. Treat the discovered source root as the canonical install source. NEVER run
   `/kronael:install`; that is a Claude Code slash command.
4. Execute the canonical installer's steps exactly as written there — the
   new-install plan/consent questionnaire, sync protocol, backup, copy assets
   (incl. the `create-*` prune list), install wisdom, merge the Claude hooks
   block, install Codex hook wiring, external tools, CLI tools
   (rig/udfix/clp/dockbox — the marketplace snapshot carries their source
   dirs), verify. Present the questionnaire inline as numbered options. NEVER
   restate or fork those steps here; that file is the only source of truth and
   copies drift.
5. After successful install from Codex, run the **Global installed skills**
   bridge and **Codex hooks** bridge below so Codex can see the installed
   skills, scripts, and lifecycle hooks. This is part of the Codex install
   path, not an optional extra.

## Codex Bridge

Use these steps when the user asks Codex to use Claude project guidance,
Claude project skills, or the globally installed Kronael skills. NEVER copy
skills; bridge with symlinks.

### CLAUDE.md

To make Claude-only projects work in Codex, add `CLAUDE.md` as a fallback
instruction filename in `~/.codex/config.toml` by running:

```sh
python3 "$SOURCE_ROOT/kronael/install/codex_config_fallback.py"
```

This writes the top-level TOML key
`project_doc_fallback_filenames = ["CLAUDE.md"]`, preserving existing fallback
names and repairing the known bad install shape where `CLAUDE.md` was inserted
under `[tui]` or `[tui.model_availability_nux]`. NEVER hand-append this line
after the current table header; in TOML that makes it part of the table.

If a project already has `AGENTS.md`, Codex will not also load `CLAUDE.md` as a
fallback in the same directory. ALWAYS add a short `AGENTS.md` pointer that
tells Codex to read `CLAUDE.md` first.

Example pointer:

```md
# AGENTS.md

Read `CLAUDE.md` first. Those are project conventions for every coding agent,
not Claude-specific behavior.
```

### Global installed skills

Codex scans `.agents/skills` and `~/.agents/skills`, not `.claude/skills` or
`~/.codex/skills`.

For global Kronael skills installed by this workflow, bridge with:

```sh
mkdir -p ~/.agents
ln -s ~/.claude/skills ~/.agents/skills
```

Run this automatically after a successful Codex install/update. It is fast:

- If `~/.agents/skills` already symlinks to `~/.claude/skills`, report
  "already bridged".
- If `~/.agents/skills` is missing and `~/.claude/skills` exists, create the
  symlink.
- If `~/.agents/skills` is a directory, add individual symlinks for each
  installed Kronael skill where the destination name is missing.
- If `~/.agents/skills` is a symlink elsewhere, ask whether to replace, leave
  it, or skip.
- If an individual destination already exists and is not the same symlink,
  leave it alone and report the conflict count.

NEVER copy the skill tree into `~/.codex/skills`. Codex's user skill location
is `~/.agents/skills`; symlinking preserves one editable installed copy,
including scripts and references.

Use the discovered source root to decide which installed skills are
source-owned: every `skills/*/` except `skills/global/`. Do not symlink
installed-only overlays from `~/.claude/skills`.

Protocol:

```sh
mkdir -p "$HOME/.agents"

if [ -L "$HOME/.agents/skills" ] &&
   [ "$(readlink -f "$HOME/.agents/skills")" = "$(readlink -f "$HOME/.claude/skills")" ]; then
  echo "already bridged"
elif [ ! -e "$HOME/.agents/skills" ]; then
  ln -s "$HOME/.claude/skills" "$HOME/.agents/skills"
elif [ -d "$HOME/.agents/skills" ]; then
  for d in "$SOURCE_ROOT"/skills/*/; do
    name="$(basename "$d")"
    [ "$name" = "global" ] && continue
    [ -e "$HOME/.claude/skills/$name" ] || continue
    [ -e "$HOME/.agents/skills/$name" ] && continue
    ln -s "$HOME/.claude/skills/$name" "$HOME/.agents/skills/$name"
  done
else
  echo "conflict: ~/.agents/skills exists but is not a directory or symlink"
fi
```

### Codex hooks

Codex supports native lifecycle hooks from `~/.codex/hooks.json`,
`~/.codex/config.toml`, project `.codex/` config, and enabled plugins.
Kronael uses `~/.codex/hooks.json` as the user-level install target.

After the Claude hook scripts are copied, install Codex hook wiring:

```sh
mkdir -p "$HOME/.codex"
cp "$SOURCE_ROOT/codex-hooks.json" "$HOME/.codex/hooks.json"
```

This config calls `~/.claude/hooks/codex_hook.py`, which normalizes Codex hook
payloads and delegates to the installed Kronael hooks. The wrapper also rewrites
Kronael nudge references from `/skill` to `@skill` and suppresses Claude-style
context-only output for Codex `PreCompact`, where Codex only accepts block
decisions. Do not point Codex directly at the Claude hook scripts unless the
wrapper is removed intentionally.

Codex requires changed command hooks to be reviewed and trusted. After install,
report that the user must open `/hooks` in a fresh Codex TUI session and trust
the Kronael hooks. Use `--dangerously-bypass-hook-trust` only for automation or
verification that already vets the source.

### Project .claude/skills

For a project that stores Claude skills under `.claude/skills`, bridge with:

```sh
mkdir -p .agents
ln -s ../.claude/skills .agents/skills
```

Use this only when `.claude/skills` exists and `.agents/skills` does not. If
`.agents/skills` already exists, ask whether to leave it alone, add individual
symlinks, or skip the bridge.

## Report

Report only:

- canonical install result from `kronael/install/SKILL.md` if install ran
- Codex bridge paths changed: `~/.codex/config.toml`, `AGENTS.md`,
  `~/.agents/skills`, `.agents/skills`, `~/.codex/hooks.json`
- whether Codex can now see the installed skills and hook wiring; tell the
  user to start a new thread, use `/skills` or `@skill-name`, and open `/hooks`
  once to trust changed hooks

NEVER duplicate the full installer report in the bridge. Link paths and say
whether each bridge step was applied or skipped.
