---
name: kronael-sync
description: Sync Kronael into ~/.claude from Codex (bundle + CLI tools rig/udfix/dockbox), first setup included; bridge global/project CLAUDE.md, skills, and hooks into Codex. NOT for a sync inside Claude Code (use /kronael:sync) or bringing the git line up to date with origin (use merge).
when_to_use: "@kronael-sync, sync kronael from codex, set up kronael in codex, bridge claude skills into codex, bridge hooks into codex, kronael skills missing in codex, kronael hooks missing in codex"
---

# Kronael Sync

ALWAYS sync the existing Claude Code bundle from the marketplace source
snapshot. NEVER copy or port the bundle into the Codex plugin directory.

The installed Codex plugin contains only this sync skill. It does NOT
contain the Kronael Claude skills. Codex sees those skills only through the
Codex Bridge (`~/.agents/skills` or project `.agents/skills`). For sync
requests from Codex, create the global bridge and install Codex hook wiring
automatically after the sync succeeds.

## Invocation

Users usually invoke:

```text
Use @kronael-sync to sync Kronael.
```

If the user says "sync kronael" or "install kronael" without naming this
skill, still run this workflow.

If the user asks only to make Codex see the installed skills, or says skills
are missing after a sync, skip the sync workflow and use the Codex Bridge
section.

## Source Root

For sync requests, find the source root by checking, in order:

1. Ancestors of `cwd`.
2. Ancestors of this skill's path.
3. Codex marketplace snapshots:
   - `$CODEX_HOME/.tmp/marketplaces/*`
   - `~/.codex/.tmp/marketplaces/*`

The source root is the first directory where all of these exist:

- `kronael/sync/SKILL.md`
- `kronael/sync/reference.md`
- `skills/`
- `agents/`
- `hooks/`
- `codex-hooks.json`
- `settings-recommended.json`
- `RECLAUDE.md`
- `codex/AGENTS.md`

NEVER use the installed plugin cache as the bundle source unless it contains
all files above; normal plugin installs cache only this bridge skill.

If no source root is found, ask the user to run
`codex plugin marketplace add kronael/tools` or
`codex plugin marketplace upgrade kronael` (`kronael-local` for older
installs), then start a fresh Codex thread. NEVER invent paths. The Codex
plugin is only a sync bridge; the GitHub marketplace snapshot owns the
bundle.

For Codex Bridge-only requests, discover the source root when the requested
bridge step needs source-owned files (`codex/AGENTS.md`, `codex-hooks.json`, or
per-skill symlinks). Skip source-root discovery only for project guidance or the
simple `~/.agents/skills -> ~/.claude/skills` symlink case.

## Sync

1. Read `kronael/sync/SKILL.md` completely, plus the
   `kronael/sync/reference.md` it points to (scripts, keep-list, Codex
   bridge, tool commands).
2. Follow them as the source of truth.
3. Treat the discovered source root as the canonical sync source. NEVER run
   `/kronael:sync`; that is a Claude Code slash command.
4. Execute the canonical sync's steps exactly as written there — the
   first-sync questionnaire, classify, merge live edits into the repo,
   installed-only decisions, swap, settings, Codex bridge, external tools,
   CLI tools (rig/udfix/dockbox — the marketplace snapshot carries their
   source dirs), opted-in first-sync server memory, report. A marketplace snapshot is not the owner's clone:
   when `~/.claude/` holds live edits, the sync stops before the swap and
   asks for a run from the clone. Present the questionnaire inline as numbered options. NEVER
   restate or fork those steps here; that file is the only source of truth and
   copies drift.
5. After a successful sync from Codex, run the global guidance, installed
   skills, and hooks bridges below. This is part of the Codex sync path.

## Codex Bridge

Use these steps when the user asks Codex to use Claude global/project guidance
or installed skills. Bridge skills with symlinks, never copies; global
guidance is a real file.

### Global CLAUDE.md

Codex loads global instructions from `~/.codex/AGENTS.override.md`, or from
`~/.codex/AGENTS.md` when no override exists. It does not discover
`~/.claude/CLAUDE.md` globally. `~/.codex/AGENTS.md` is therefore a real file
holding the managed Kronael block, which tells Codex to read
`~/.claude/CLAUDE.md`. Apply the merge in canonical sync step 6. ALWAYS
back up the target first and preserve content outside the markers. NEVER report
the global bridge complete without checking that the managed block is present.

### Project CLAUDE.md

To make Claude-only projects work in Codex, add `CLAUDE.md` as a fallback
instruction filename in `~/.codex/config.toml`:

```toml
project_doc_fallback_filenames = ["CLAUDE.md"]
```

ALWAYS keep this as a top-level TOML key: insert it before the first `[table]`
header, or append `CLAUDE.md` to the existing top-level fallback array. NEVER
hand-append it after the current table header; in TOML that makes it part of the
table. NEVER leave `CLAUDE.md` under `[tui]` or `[tui.model_availability_nux]`
— move it to the top-level key.

If a project already has `AGENTS.md`, Codex will not also load `CLAUDE.md` as a
fallback in the same directory. The installed global Kronael block in
`~/.codex/AGENTS.md` therefore ALWAYS tells Codex to actively read applicable
`CLAUDE.md` files in addition to loaded `AGENTS.md` files. For repositories
shared without Kronael, ALSO add a short project `AGENTS.md` pointer.

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

Run this automatically after a successful Codex sync. It is fast:

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
- If an individual symlink there points into `~/.claude/skills/` and no
  longer resolves, `rm` it — the source dropped that skill.

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
Kronael uses `~/.codex/hooks.json` as the user-level target.

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

Codex requires changed command hooks to be reviewed and trusted. After a sync,
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

- canonical sync result from `kronael/sync/SKILL.md` if the sync ran
- Codex bridge paths changed: `~/.codex/AGENTS.md`, `~/.codex/config.toml`, project `AGENTS.md`,
  `~/.agents/skills`, `.agents/skills`, `~/.codex/hooks.json`
- whether Codex can now see global guidance, installed skills, and hook wiring; tell the
  user to start a new thread, use `/skills` or `@skill-name`, and open `/hooks`
  once to trust changed hooks

NEVER duplicate the full sync report in the bridge. Link paths and say
whether each bridge step was applied or skipped.
