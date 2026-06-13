---
name: kronael-install
description: Install/update Kronael; bridge CLAUDE.md/.claude/skills into Codex. NOT for CLI tools (use Makefiles).
---

# Kronael Install

ALWAYS install the existing Claude Code bundle from the marketplace source
snapshot. NEVER copy or port the bundle into the Codex plugin directory.

The installed Codex plugin contains only this installer skill. It does NOT
contain the Kronael Claude skills. Codex sees those skills only through the
Codex Bridge (`~/.agents/skills` or project `.agents/skills`). For install
requests from Codex, create the global bridge automatically after the Claude
install succeeds.

## Invocation

Users usually invoke:

```text
Use $kronael-install to install/update Kronael.
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

For Codex Bridge-only requests, skip source-root discovery and perform only the
requested bridge step.

## Install

1. Read `kronael/install/SKILL.md` completely.
2. Follow it as the source of truth.
3. Treat the discovered source root as the canonical install source. NEVER run
   `/kronael:install`; that is a Claude Code slash command.
4. Execute the canonical installer's steps exactly as written there —
   sync protocol, backup, copy assets (incl. the `create-*` prune list),
   install wisdom, merge the hooks block, external tools, verify. NEVER
   restate or fork those steps here; that file is the only source of truth and
   copies drift.
5. After successful install from Codex, run the **Global installed skills**
   bridge below so Codex can see the installed skills and their scripts.
   This is part of the Codex install path, not an optional extra.

## Codex Bridge

Use these steps when the user asks Codex to use Claude project guidance,
Claude project skills, or the globally installed Kronael skills. NEVER copy
skills; bridge with symlinks.

### CLAUDE.md

To make Claude-only projects work in Codex, add `CLAUDE.md` as a fallback
instruction filename in `~/.codex/config.toml`:

```toml
project_doc_fallback_filenames = ["CLAUDE.md"]
```

If fallback names already exist, preserve them and append `CLAUDE.md` only if
missing.

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
  `~/.agents/skills`, `.agents/skills`
- whether Codex can now see the installed skills; tell the user to start a new
  thread and use `/skills` or `$skill-name`

NEVER duplicate the full installer report in the bridge. Link paths and say
whether each bridge step was applied or skipped.
