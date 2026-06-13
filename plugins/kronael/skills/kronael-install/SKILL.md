---
name: kronael-install
description: Install or update Kronael from Codex. NOT for installing CLI tools directly (use their Makefiles).
---

# Kronael Install

ALWAYS install the existing Claude Code bundle from this repo. NEVER copy or
port the toolkit into Codex-specific duplicate directories.

## Source Root

Find the source root by walking up from `cwd` and from this skill's path until
all of these exist:

- `kronael/install/SKILL.md`
- `skills/`
- `agents/`
- `hooks/`
- `settings-recommended.json`
- `RECLAUDE.md`

If any are missing, ask for the local `kronael/tools` clone path. The Codex
plugin is only an installer bridge; the source repo still owns the bundle.

## Install

1. Read `kronael/install/SKILL.md` completely.
2. Follow it as the source of truth.
3. Treat this as the manual path from the repo root. NEVER run
   `/kronael:install`; that is a Claude Code slash command.
4. Execute the canonical installer's steps exactly as written there —
   backup, copy assets (incl. the `create-*` prune list), install wisdom,
   merge the hooks block, external tools, verify. NEVER restate or fork those
   steps here; that file is the only source of truth and copies drift.

## Codex Bridge

Offer these optional steps only when the user asks Codex to use Claude project
guidance or Claude project skills. NEVER apply them silently.

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

### .claude/skills

Codex scans `.agents/skills`, not `.claude/skills`. For a project that stores
Claude skills under `.claude/skills`, bridge with a symlink instead of copying:

```sh
mkdir -p .agents
ln -s ../.claude/skills .agents/skills
```

Use this only when `.claude/skills` exists and `.agents/skills` does not. If
`.agents/skills` already exists, ask whether to leave it alone, add individual
symlinks, or skip the bridge.

For global personal skills, prefer native Codex skills in `~/.agents/skills`.
Only symlink `~/.agents/skills` to `~/.claude/skills` if the user explicitly
wants every Claude skill exposed to Codex and accepts the larger skill list.

## Report

Report:

- backup path
- installed skill, agent, and hook counts
- whether `~/.claude/CLAUDE.md` and `~/.claude/RECLAUDE.md` were installed
- whether settings hooks were merged
- whether Codex bridge steps were applied or skipped
