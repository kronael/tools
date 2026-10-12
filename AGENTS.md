# AGENTS.md

Notes for Codex (and any non-Claude coding agent) working in this repo.
Repo conventions and layout live in `CLAUDE.md` — read it first. NEVER
ignore a `CLAUDE.md` because it says "Claude"; these are project
conventions, not product-specific behavior.

## What this repo contains

`CLAUDE.md` § What this repo is.

## Syncing the toolkit from Codex

Follow [`kronael/sync/SKILL.md`](kronael/sync/SKILL.md); its Review
checklist applies verbatim. Below are only the Codex-specific deltas.

- `/kronael:sync` is a Claude Code slash command — you can't run it
  from Codex. Run the canonical sync from the source root discovered by
  the bridge.
- A sync puts hook scripts into `~/.claude/hooks/`. Claude Code uses
  `settings-recommended.json`; Codex uses `codex-hooks.json` plus
  `hooks/codex_hook.py` to normalize Codex hook payloads before delegating to
  those same scripts.
- The Codex plugin is a thin bridge only. Its one skill is
  `plugins/kronael/skills/kronael-sync/SKILL.md`; keep sync behavior in
  `kronael/sync/SKILL.md` and `kronael/sync/reference.md`, and update the
  bridge only when Codex-specific translation changes. NEVER make the bridge
  copy source bundle files into `plugins/kronael/`.
- NEVER copy skills into `~/.claude/skills/` by hand: a hand copy over the
  old bundle keeps every file the source dropped and loses live edits not
  yet merged into the repo. Run `kronael/sync/reference.md` § Swap as
  written.
- What the bridge writes for Codex — `~/.codex/AGENTS.md`,
  `~/.codex/config.toml`, `~/.agents/skills`, `~/.codex/hooks.json` — is
  `kronael/sync/reference.md` § Codex bridge.

## Codex plugin usage

```sh
codex plugin marketplace add kronael/tools
codex plugin add kronael@kronael
```

Then start a fresh Codex thread and invoke:

```text
Use @kronael-sync to sync Kronael.
```

After the bridge, installed Kronael skills are invoked in Codex as
`@skill-name` (for example, `@refine`). Codex hook nudges must use that form.

## Verify

§ Classify prints only `same` and `kept`, `~/.codex/AGENTS.md` holds the
Kronael block, `~/.agents/skills` bridges to `~/.claude/skills`, and
`~/.codex/hooks.json` exists. Report the class counts and the run dir.

## Conventions

`CLAUDE.md` and the wisdom file (`skills/global/SKILL.md`) own them; read both.
