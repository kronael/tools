# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Development conventions (response style, boring-code philosophy, commit/test
> rules) live in the global wisdom file installed at `~/.claude/CLAUDE.md`
> (sourced from `skills/global/SKILL.md`). This file is **repo-specific only**.
> Keep it under 200 lines.

## What this repo is

The **kronael toolkit** — two things in one repo:

1. **Standalone CLI tools** (`dockbox/`, `rig/`, `tw-fetch/`, `tg-fetch/`,
   `dc-fetch/`, `clp/`). Each is fully independent: own dir, own Makefile or
   PEP 723 inline-deps script, own README. They do not import from each other.
2. **A Claude Code bundle** (`skills/`, `agents/`, `hooks/`,
   `settings-recommended.json`, `RECLAUDE.md`) distributed as a plugin and
   deployed into a user's `~/.claude/` by an install step.

The bundle is Claude Code *configuration*. It does not run here — it runs in
the user's Claude Code sessions after install. When editing the bundle you are
authoring config, not application code.

## Commands

```sh
make test          # run tests across subdirs (currently: hooks)
make test-hooks    # tests for one subdir
make clean         # clean subdirs + sweep __pycache__
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

## Architecture: two install paths, one source

`skills/`, `agents/`, `hooks/` at repo root **are** the bundle. Both install
paths copy them into `~/.claude/`:

- **Plugin path** — marketplace clones the repo into Claude Code's plugin
  cache; `/kronael:install` copies from `${CLAUDE_PLUGIN_ROOT}`.
- **Manual path** — user clones, opens Claude Code at root, says "install";
  source is `cwd`.

`kronael/install/SKILL.md` is the **single source of truth** for the
procedure (the only plugin-exposed skill). `AGENTS.md` is the bash translation
for Codex / non-Claude agents. When you change install behavior, change
`kronael/install/SKILL.md` and keep `AGENTS.md` in sync.

### Why hybrid (plugin + install step), not pure plugin

The install step is an LLM running a merge procedure, not a `cp -r`. It diffs
before overwriting, surfaces conflicts, extracts user-local paths/secrets to
`LOCAL.md`, and preserves user-added skills. This makes the user's `~/.claude/`
a **working copy** they can edit and PR back — a pure plugin would overwrite
edits on every update. See `ARCHITECTURE.md#why-hybrid-plugin--install-step`.

### Sync rules (enforced by the install procedure)

| Target | Rule |
|---|---|
| `skills/`, `agents/`, `hooks/` | Replace matching files; **never `rm -rf`** (preserves org overlays / user skills) |
| `~/.claude/CLAUDE.md` | Merge from `skills/global/SKILL.md` body (frontmatter stripped) — diff and ask |
| `~/.claude/settings.json` | Merge from `settings-recommended.json` — diff and ask; the `hooks` block is the minimum required |
| `settings.local.json`, `LOCAL.md`, `CLAUDE.local.md` | **NEVER touch** |
| Anything in `~/.claude/` not in this source tree | **NEVER delete** |

`skills/global/` is copied as the wisdom file (→ `~/.claude/CLAUDE.md`), **not**
as a skill — installing it both ways would duplicate always-loaded content.

## The bundle

- **Skills** (`skills/<name>/SKILL.md`) auto-activate by file context
  (`.rs`→`rs`, `Dockerfile`→`ops`) and provide workflow commands (`/commit`,
  `/ship`, `/refine`, `/diary`). Skills are NOT reliably auto-triggered —
  explicit dispatch (`/dispatch`, `/resolve`) is the intended path.
- **Agents** (`agents/*.md`): `@distill`, `@improve`, `@learn`, `@readme`,
  `@refine`, `@visual`. Mostly invoked via slash-command wrappers.
- **Hooks** (`hooks/*.py`) wire lifecycle events:
  - `prompt_nudge` / `pretool_nudge` (UserPromptSubmit / PreToolUse) — fuzzy-match keywords to agents/skills
  - `local` (UserPromptSubmit, PreCompact) — inject `~/.claude/LOCAL.md`
  - `reclaude` (PreCompact) — re-inject critical rules across compaction
  - `stop` (Stop) — block on uncommitted changes / missing diary entries

  See `hooks/ARCHITECTURE.md` for per-hook data flow.

## Repo-specific conventions

- **Skill naming**: `create-*` is **reserved** for creative-output skills
  (HTML/SVG/ASCII artifacts, ported from NousResearch/hermes-agent under
  `skills/creative/`). Keep the prefix when porting. Only port skills that work
  **locally** — no paid APIs, no cloud accounts, no required external apps
  (local CLI/lib deps like ffmpeg, manim, pyfiglet are fine).
- **Files under 200 lines.** Skill/CLAUDE content uses **ALWAYS/NEVER**
  statements and targets non-obvious patterns LLMs miss — not generic advice.
- **NEVER put local paths, org-specific refs, or secrets in source.** Those
  live in `~/.claude/LOCAL.md` (auto-injected by the `local` hook), which is
  never committed.
- **Testing bundle changes**: re-run `/kronael:install` (or "say install") and
  use the result in a real project. There's no unit test for skill behavior.

## Docs map

| Doc | Purpose |
|-----|---------|
| `README.md` | User-facing overview + install paths |
| `ARCHITECTURE.md` | Repo shape, install paths, sync strategies, org overlays |
| `AGENTS.md` | Conventions + bash install runbook for Codex / non-Claude agents |
| `WORKFLOW.md` | Agent hierarchy: `/ship` → `/build` → `/refine` → leaf agents |
| `COOKBOOK.md` | Daily git recipes (detached-HEAD with `rig`) |
| `kronael/install/SKILL.md` | Canonical install procedure (both paths) |
| `skills/README.md`, `hooks/README.md` | Bundle rationale by family |
| `CHANGELOG.md` | Release history |
