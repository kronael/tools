# AGENTS.md

Notes for Codex (and any non-Claude coding agent) working in this repo.
Repo conventions and layout live in `CLAUDE.md` — read it first. NEVER
ignore a `CLAUDE.md` because it says "Claude"; these are project
conventions, not product-specific behavior.

## What this repo contains

Three things — see `CLAUDE.md` for the shape and `README.md` for the CLI
tool inventory:

1. **CLI tools** — one independent dir each. Adding a tool: own dir, own
   Makefile (or PEP 723 inline-deps script), entry in `README.md`.
2. **Claude Code bundle** — `skills/`, `agents/`, `hooks/`,
   `settings-recommended.json`, `codex-hooks.json`, `RECLAUDE.md`,
   distributed via
   `.claude-plugin/` + `kronael/install/`.
3. **Codex installer bridge** — `plugins/kronael/` and
   `.agents/plugins/marketplace.json`.
   It exposes one Codex skill that teaches Codex to run the same manual
   install path. It does not duplicate the bundle.

## Installing the toolkit from Codex

Follow the canonical procedure in
[`kronael/install/SKILL.md`](kronael/install/SKILL.md) step by step — on a
new install present its plan/consent questionnaire first, then verify source,
backup, copy assets, install the wisdom file, merge settings, install the
opted-in CLI tools (rig/udfix/clp/dockbox via their Makefiles — the
marketplace snapshot carries their source dirs), report. Its Rules section
(backup first, never-touch list, no deletions) applies verbatim. Below are
only the Codex-specific deltas.

- `/kronael:install` is a Claude Code slash command — you can't run it
  from Codex. Run the canonical installer from the source root discovered by
  the bridge.
- The bundle installs hook scripts into `~/.claude/hooks/`. Claude Code uses
  `settings-recommended.json`; Codex uses `codex-hooks.json` plus
  `hooks/codex_hook.py` to normalize Codex hook payloads before delegating to
  those same scripts.
- The Codex plugin is a thin bridge only. Its one skill is
  `plugins/kronael/skills/kronael-install/SKILL.md`; keep install behavior in
  `kronael/install/SKILL.md` and update the bridge only when Codex-specific
  translation changes.
- Installing from Codex deploys the Claude bundle to `~/.claude/`, exposes
  those installed skills to Codex through `~/.agents/skills`, and writes
  `~/.codex/hooks.json` for Codex lifecycle hooks. It also installs
  `codex/AGENTS.md` as global Codex guidance: the same terse response policy as
  the selected `80% caveman` Claude output style. The plugin cache still
  contains only the bridge skill.

## Codex plugin usage

GitHub marketplace path:

```sh
codex plugin marketplace add kronael/tools
codex plugin add kronael@kronael
```

Then start a fresh Codex thread and invoke:

```text
Use @kronael-install to install/update Kronael.
```

Bridge-only invocation (for repair or existing installs):

```text
Use @kronael-install to bridge CLAUDE.md, .claude/skills, and hooks into Codex.
```

Global installed-skill bridge:

```text
Use @kronael-install to bridge .claude/skills and hooks into Codex.
```

After the bridge, installed Kronael skills are invoked in Codex as
`@skill-name` (for example, `@refine`). Codex hook nudges must use that form.

Codex compatibility for Claude projects:

- Symlink `~/.codex/AGENTS.md -> ~/.claude/CLAUDE.md` so Codex loads the
  installed global wisdom automatically. A non-empty `AGENTS.override.md`
  takes precedence and must be handled as a conflict.
- Add `CLAUDE.md` to `project_doc_fallback_filenames` in
  `~/.codex/config.toml` for projects without `AGENTS.md`. The key is
  top-level, not under `[tui]` or any other table.
- pi reads the same global wisdom via
  `~/.pi/agent/AGENTS.md -> ~/.claude/CLAUDE.md` (its context files are
  `AGENTS.md` then `CLAUDE.md`).
- If a project already has `AGENTS.md`, make that file tell Codex to read
  `CLAUDE.md`; fallback names do not stack with `AGENTS.md`.
- To expose project `.claude/skills` to Codex, symlink
  `.agents/skills -> ../.claude/skills` instead of copying.
- To expose globally installed Kronael skills to Codex, symlink
  `~/.agents/skills -> ~/.claude/skills` when possible; if
  `~/.agents/skills` is already a directory, add per-skill symlinks for
  source-owned Kronael skills. Codex does not scan `~/.claude/skills`
  directly.

If `@kronael-install` cannot find the source root, refresh the GitHub
marketplace with `codex plugin marketplace upgrade kronael` (or
`kronael-local` for older installs). NEVER make the bridge copy source bundle
files into `plugins/kronael/`.

Shell translations for the non-obvious steps:

**Copy skills, skipping `global/`** (its body becomes the wisdom file;
copying it as a skill too would duplicate always-loaded content). NEVER
`rm -rf ~/.claude/skills/` first. Run the sync protocol from
`kronael/install/SKILL.md` before this copy so local installed edits are
merged or explicitly overwritten, never clobbered silently:

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
hooks block and `cleanupPeriodDays` instead of overwriting (the event
wiring is whatever `settings-recommended.json` says — don't restate it).
`cleanupPeriodDays` is always applied, never asked — the 30-day default
silently deletes session transcripts at startup. For permissions and
sandbox, show the diff and ask:

```sh
jq -s '.[0].hooks = .[1].hooks | .[0].cleanupPeriodDays = .[1].cleanupPeriodDays | .[0]' \
   ~/.claude/settings.json settings-recommended.json \
   > ~/.claude/settings.json.new \
  && mv ~/.claude/settings.json.new ~/.claude/settings.json
```

**Codex hooks** — copy `codex-hooks.json` to `~/.codex/hooks.json` after the
Claude hook scripts are installed. This is part of Codex bridge-only repair,
not only full installs. In a fresh Codex TUI session, the user must open
`/hooks` once and trust changed command hooks.

**Verify** — file counts under `~/.claude/{skills,agents,hooks}` match
the source dirs (skills: minus `global/`), `~/.claude/CLAUDE.md` exists,
`~/.codex/AGENTS.md` resolves to it,
`~/.agents/skills` bridges to `~/.claude/skills`, and
`~/.codex/hooks.json` exists. Report counts and the backup path.

## Conventions

- Boring linear code over clever code.
- Files under 200 lines.
- ALWAYS/NEVER statements in skill content.
- No secrets, no local paths, no org-specific references in source.
- Commit format: `type(scope): Message` (scope optional).
- NEVER use `git add -A`, `git commit --amend`, or `git push`.
- NEVER delete files in `~/.claude/` that aren't in this source tree.
