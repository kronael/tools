# AGENTS.md

Instructions for Codex (and any non-Claude coding agent) working in this
repository. The same conventions live in `CLAUDE.md`; this file makes them
accessible to agents that don't pick up `CLAUDE.md` automatically.

## Startup

ALWAYS read before making changes:

1. Root `CLAUDE.md` — repo conventions and layout.
2. `INSTALL.md` — manual install procedure for the Claude Code toolkit.
3. Nearest nested `CLAUDE.md` for the area being changed (if any).

NEVER ignore a `CLAUDE.md` because it says "Claude". These are project
conventions, not product-specific behavior.

## What this repo contains

1. **CLI tools** — `dockbox/`, `rig/`, `tw-fetch/`, `tg-fetch/`, `dc-fetch/`.
   Each is independent. Adding a new tool: own dir, own Makefile (or
   PEP 723 inline-deps script), entry in `README.md`.
2. **Claude Code plugin** — `.claude-plugin/` + `kronael-tools/install/`.
   Only `/kronael-tools:install` is exposed; running it copies the bundle
   into `~/.claude/`.
3. **Bundle** — `skills/`, `agents/`, `hooks/`, `settings-recommended.json`,
   `RECLAUDE.md`. Source for both install paths.

## Installing the toolkit (manual path, for Codex users)

If you want the bundle deployed to `~/.claude/` without using the Claude
Code plugin marketplace, follow `INSTALL.md`. Summary:

```
cp -r skills/*  ~/.claude/skills/
cp -r agents/*  ~/.claude/agents/
cp -r hooks/    ~/.claude/hooks/

# wisdom file (strip YAML frontmatter from skills/global/SKILL.md):
sed '1{/^---$/,/^---$/d}' skills/global/SKILL.md > ~/.claude/CLAUDE.md

# settings: review settings-recommended.json and merge into
# ~/.claude/settings.json by hand. NEVER overwrite settings.local.json.
```

Backup `~/.claude/{skills,agents,hooks,CLAUDE.md,settings.json}` to
`~/.claude/backup/<timestamp>/` before overwriting.

## Conventions

- Boring linear code over clever code.
- Files under 200 lines.
- ALWAYS/NEVER statements in skill content.
- No secrets, no local paths, no org-specific references in source.
- Commit format: `[section] Message`.
- NEVER use `git add -A`, `git commit --amend`, or `git push`.
- NEVER delete files in `~/.claude/` that aren't in this source tree.
