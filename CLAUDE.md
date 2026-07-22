# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Development conventions (response style, boring-code philosophy, commit/test
> rules) live in the global wisdom file installed at `~/.claude/CLAUDE.md`
> (sourced from `skills/global/SKILL.md`). This file is **repo-specific only**.
> Keep it under 200 lines.

## What this repo is

The **kronael toolkit** — three things in one repo:

1. **Standalone CLI tools**, one directory each. Fully independent: own
   Makefile or PEP 723 inline-deps script, own README, no imports between
   them. The tool inventory lives in `README.md` — when adding a tool, add
   its row there.
2. **A Claude Code bundle** (`skills/`, `agents/`, `hooks/`,
   `settings-recommended.json`, `RECLAUDE.md`) distributed as a plugin and
   deployed into a user's `~/.claude/` by an install step.
3. **A thin Codex installer bridge** (`plugins/kronael/` plus
   `.agents/plugins/`) exposing one Codex skill that runs the same install
   procedure without duplicating bundle assets.

The bundle is Claude Code *configuration*. It does not run here — it runs in
the user's Claude Code sessions after install. When editing the bundle you are
authoring config, not application code.

## Commands

```sh
make test          # run tests across all projects in PROJECTS (hooks udfix)
make test-<dir>    # tests for one project, e.g. make test-udfix
make workflows     # regenerate PROJECTS from */Makefile (test+clean targets)
make clean         # clean projects + sweep __pycache__
```

- **Hooks** (`hooks/`): `make -C hooks test` runs pytest. Only `pretool_nudge.py`
  is collected — `stop.py`, `local.py`, `prompt_nudge.py`, `reclaude.py` read
  stdin at import time and break collection until `main()` is guarded behind
  `__name__ == '__main__'`.
- **CLI tools**: each has its own Makefile — `cd <tool> && make install`
  (installs to `~/.local/bin`). `dockbox` also has `make image`.
- **Python scripts** (`tg-fetch`, `dc-fetch`): `uv run main.py` (PEP 723
  inline deps, no separate install).
- **Lint**: pre-commit runs ruff + ruff-format + json/yaml/toml checks.
  `ruff.toml` is the config. Pre-commit reformats on first run — retry the
  commit if it does.

## Architecture: install paths, one source

`skills/`, `agents/`, `hooks/` at repo root **are** the bundle. The Claude
plugin path (`/kronael:install` from `${CLAUDE_PLUGIN_ROOT}`) and the manual
path (user opens Claude Code at the cloned root and says "install") both copy
them into `~/.claude/`.

Codex has a third, thin bridge path:
`plugins/kronael/skills/kronael-install/SKILL.md` reads the canonical
installer and runs the manual path. NEVER duplicate the bundle under
Codex-specific directories.

`kronael/install/SKILL.md` is the **single source of truth** for the
procedure (the only plugin-exposed skill); its cold data — tool commands and
the removed-skills prune list — lives in the sibling `kronael/install/reference.md`.
When you change install behavior, change those files and keep `AGENTS.md` plus
the Codex installer skill in sync.
Why the install step exists at all:
`ARCHITECTURE.md#why-hybrid-plugin--install-step`.

Critical sync rules (full table: `ARCHITECTURE.md#sync-strategies`):

- **NEVER `rm -rf`** into `~/.claude/` — replace matching files only; org
  overlays and user-added skills must survive. NEVER delete anything in
  `~/.claude/` that isn't in this source tree.
- **NEVER touch** `settings.local.json`, `LOCAL.md`, `CLAUDE.local.md`.
- `skills/global/` installs as the wisdom file (→ `~/.claude/CLAUDE.md`),
  **not** as a skill — installing it both ways would duplicate always-loaded
  content.

## The bundle

- **Skills** (`skills/<name>/SKILL.md`) auto-activate by file context
  (`.rs`→`rs`, `Dockerfile`→`ops`) and provide workflow commands (`/commit`,
  `/ship`, `/refine`, `/diary`). Skills are NOT reliably auto-triggered —
  explicit dispatch (`/resolve`) is the intended path. Index: `skills/README.md`.
- **Agents** (`agents/*.md`) — task workers, mostly invoked via
  slash-command wrappers.
- **Hooks** (`hooks/*.py`, `hooks/*.sh`) wire lifecycle events. Wiring is
  defined in `settings-recommended.json`; per-hook data flow in
  `hooks/ARCHITECTURE.md`.

## Repo-specific conventions

- **Skill naming**: creative-output generators live under the `skills/create/`
  **router** (one preloaded `SKILL.md`, cold data files per mode); engineering
  runbooks under `skills/software/`. NEVER add new `create-*` dirs. The router
  convention — flat vs router, naming law, edit procedure — is owned by
  `skills/CLAUDE.md`. Only port skills that work **locally** — no paid APIs,
  no cloud accounts, no required external apps (local CLI/lib deps like
  ffmpeg, manim, pyfiglet are fine).
- **Files under 200 lines** — overflow moves to linked sibling files loaded on
  demand (router pattern), never a longer SKILL.md. Skill/CLAUDE content uses
  **ALWAYS/NEVER** statements and targets non-obvious patterns LLMs miss — not
  generic advice.
- **NEVER put local paths, org-specific refs, or secrets in source.** Those
  live in `~/.claude/LOCAL.md` (auto-injected by the `local` hook), which is
  never committed.
- **Testing bundle changes**: re-run `/kronael:install` (or "say install") and
  use the result in a real project. There's no unit test for skill behavior.

## Release

- Canonical version = git tag + `CHANGELOG.md`; the `release:` commit adds the
  CHANGELOG entry and tags `vX.Y.Z` (patch default). Use the `release` skill.
- ALWAYS bump `.claude-plugin/plugin.json` `version` to match the new tag in
  the same release — it silently drifted (stuck at 0.3.47 across many releases).
  Keep it synced so the plugin manifest reports the shipped version.

## Docs map

The full map is `README.md#documentation`. Most-used here:
`kronael/install/SKILL.md` (canonical install), `ARCHITECTURE.md` (design
rationale), `COOKBOOK.md` (git recipes), `skills/README.md` +
`hooks/README.md` (bundle rationale by family).
