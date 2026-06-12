# AGENTS.md

Notes for Codex (and any non-Claude coding agent) working in this repo.
Repo conventions and layout live in `CLAUDE.md` — read it first. NEVER
ignore a `CLAUDE.md` because it says "Claude"; these are project
conventions, not product-specific behavior.

## What this repo contains

Two things — see `CLAUDE.md` for the shape and `README.md` for the CLI
tool inventory:

1. **CLI tools** — one independent dir each. Adding a tool: own dir, own
   Makefile (or PEP 723 inline-deps script), entry in `README.md`.
2. **Claude Code bundle** — `skills/`, `agents/`, `hooks/`,
   `settings-recommended.json`, `RECLAUDE.md`, distributed via
   `.claude-plugin/` + `kronael/install/`.

## Installing the toolkit from Codex

Follow the canonical procedure in
[`kronael/install/SKILL.md`](kronael/install/SKILL.md) step by step —
verify source, backup, copy assets, install the wisdom file, merge
settings, report. Its Rules section (backup first, never-touch list, no
deletions) applies verbatim. Below are only the Codex-specific deltas.

- `/kronael:install` is a Claude Code slash command — you can't run it
  from Codex. Run the manual path from the repo root.
- The bundle is Claude Code config: hooks fire on Claude Code lifecycle
  events, skills use Claude Code auto-activation. Codex doesn't use it —
  Codex is the installer, deploying to `~/.claude/` for the user's
  Claude Code sessions.

Shell translations for the non-obvious steps:

**Copy skills, skipping `global/`** (its body becomes the wisdom file;
copying it as a skill too would duplicate always-loaded content). NEVER
`rm -rf ~/.claude/skills/` first — `cp -r` overwrites matching files and
leaves user-added ones alone:

```sh
for d in skills/*/; do
  [ "$(basename "$d")" = "global" ] && continue
  cp -r "$d" ~/.claude/skills/
done
```

**Install the wisdom file** — strip the YAML frontmatter from
`skills/global/SKILL.md`; if `~/.claude/CLAUDE.md` already has user
content, diff and ask first:

```sh
awk 'BEGIN{n=0} /^---$/{n++; next} n>=2{print}' \
  skills/global/SKILL.md > ~/.claude/CLAUDE.md
```

**Merge settings** — if `~/.claude/settings.json` exists, splice the
hooks block instead of overwriting (the event wiring is whatever
`settings-recommended.json` says — don't restate it). For permissions
and sandbox, show the diff and ask:

```sh
jq -s '.[0].hooks = .[1].hooks | .[0]' \
   ~/.claude/settings.json settings-recommended.json \
   > ~/.claude/settings.json.new \
  && mv ~/.claude/settings.json.new ~/.claude/settings.json
```

**Verify** — file counts under `~/.claude/{skills,agents,hooks}` match
the source dirs (skills: minus `global/`), and `~/.claude/CLAUDE.md`
exists. Report counts and the backup path.

## Conventions

- Boring linear code over clever code.
- Files under 200 lines.
- ALWAYS/NEVER statements in skill content.
- No secrets, no local paths, no org-specific references in source.
- Commit format: `[section] Message`.
- NEVER use `git add -A`, `git commit --amend`, or `git push`.
- NEVER delete files in `~/.claude/` that aren't in this source tree.
