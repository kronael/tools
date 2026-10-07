# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Skill routing, the map of where things live, and the safety NEVER list live
> in the global wisdom file installed at `~/.claude/CLAUDE.md` (sourced from
> `skills/global/SKILL.md`); each rule lives in the skill that owns it
> (`commit`, `software`, `ops`, …). This file is **repo-specific only**.
> Keep it under 200 lines.

## What this repo is

The **kronael toolkit** — three things in one repo:

1. **Standalone CLI tools**, one directory each. Fully independent: own
   Makefile or PEP 723 inline-deps script, own README, no imports between
   them. The tool inventory lives in `README.md` — when adding a tool, add
   its row there.
2. **A Claude Code bundle** (`skills/`, `agents/`, `hooks/`, `output-styles/`,
   `commands/`, `settings-recommended.json`, `RECLAUDE.md`) distributed as a
   plugin and deployed into a user's `~/.claude/` by a sync step.
3. **A thin Codex sync bridge** (`plugins/kronael/` plus
   `.agents/plugins/`) exposing one Codex skill that runs the same sync
   procedure without duplicating bundle assets.

The bundle is Claude Code *configuration*. It does not run here — it runs in
the user's Claude Code sessions after a sync. When editing the bundle you are
authoring config, not application code.

## Commands

```sh
make test          # every project in PROJECTS, then tests/drift_test.sh
make test-<dir>    # one project, e.g. make test-udfix
make workflows     # regenerate PROJECTS from */Makefile (test+clean targets)
make gen-ci        # regenerate .github/workflows/ from .github/templates/
make clean         # clean projects + sweep __pycache__
```

- **Hooks** (`hooks/`): `make -C hooks test` runs pytest over the explicit
  `TEST_FILES` list in `hooks/Makefile`, never the directory. A new
  `test_*.py` does not run until it is added to that list — the suite passes
  while silently skipping it. `local.py` and `reclaude.py` carry no tests.
- **CLI tools**: each has its own Makefile — `cd <tool> && make install`
  (installs to `~/.local/bin`). `dockbox` also has `make image`.
- **Python scripts** (`tw-fetch`, `tg-fetch`, `dc-fetch`): `uv run main.py`
  (PEP 723 inline deps, no separate install).
- **Lint**: pre-commit runs ruff + ruff-format + json/yaml/toml checks.
  `ruff.toml` is the config. Pre-commit reformats on first run — retry the
  commit if it does.

## Architecture: sync paths, one source

`skills/`, `agents/`, `hooks/`, `output-styles/`, `commands/` at repo root
**are** the bundle. The Claude plugin path (`/kronael:sync`, from a CWD clone
that holds the assets, else `${CLAUDE_PLUGIN_ROOT}`) and the manual path
(user opens Claude Code at the cloned root and says "sync") both put them
into `~/.claude/`.

Codex has a third, thin bridge path:
`plugins/kronael/skills/kronael-sync/SKILL.md` reads the canonical sync and
runs the manual path. NEVER duplicate the bundle under Codex-specific
directories.

`kronael/sync/SKILL.md` is the **single source of truth** for the procedure
(the only plugin-exposed skill); its scripts, keep-list format and tool
commands live in the sibling `kronael/sync/reference.md`. When you change
sync behavior, change those files and keep `AGENTS.md` plus the Codex sync
skill in step.
Why the sync step exists at all:
`ARCHITECTURE.md#why-hybrid-plugin--sync-step`.

Critical sync rules (full table: `ARCHITECTURE.md#sync-strategies`):

- **Sync is source ↔ live, nothing else**: **source** (this repo tree),
  **live** (`~/.claude/` on a host — the running bundle). **Push** reaches
  **upstream** (the `origin` remote); **merge origin** brings upstream into
  the git line. NEVER conflate the three — live can be ahead of, behind, or
  forked from upstream.
- **Live edits merge into the repo first, then live is rebuilt** — a file
  edited in `~/.claude/` since the last sync merges three-way into the repo
  BEFORE the swap; the bundle is then rebuilt from source plus the
  installed-only paths that `kronael/sync/reference.md` § Keep-list keeps,
  and the old bundle moves to `/tmp`. Nothing the source dropped survives a
  sync.
- **NEVER `rm -rf`** into `~/.claude/` — sync moves the old bundle aside with
  `mv`. Private skills come back only by that keep-list rule. Org overlays
  install as plugins (`ARCHITECTURE.md#org-overlays`). NEVER let either
  enter this repo without the owner's yes.
- **NEVER touch** `settings.local.json` or `CLAUDE.local.md`; `LOCAL.md`
  receives only the private hunks a merge keeps out of the repo.
- `skills/global/` becomes the wisdom file (→ `~/.claude/CLAUDE.md`),
  **not** a skill — shipping it both ways would duplicate always-loaded
  content.

## The bundle

- **Skills** (`skills/<name>/SKILL.md`) auto-activate by file context
  (`.rs`→`rs`, `Dockerfile`→`ops`) and provide workflow commands (`/commit`,
  `/ship`, `/refine`, `/diary`). Skills are NOT reliably auto-triggered —
  explicit dispatch (`/solve`) is the intended path. Index: `skills/README.md`.
- **Agents** (`agents/*.md`) — task workers that skills launch;
  `skills/CLAUDE.md` § Agent definitions owns that rule.
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
- **Testing bundle changes**: re-run `/kronael:sync` (or say "sync") and
  use the result in a real project. There's no unit test for skill behavior.

## Conformance — mandatory, and checked

The bundle is worthless if Claude Code, Codex or pi silently fail to load it.
All three are verifiable; ALWAYS verify rather than assume.

**Skills match what Claude Code actually reads**
(code.claude.com/docs/en/skills), not what looks reasonable:

- SKILL.md frontmatter uses ONLY recognised keys. An unrecognised key is
  ignored locally and rejected by other Agent Skills consumers, so it is a
  defect, not a harmless extra. Free-form provenance — author, version,
  homepage, upstream tags — goes under `metadata`, whose contents Claude Code
  ignores. Keep those values flat strings: the Agent Skills spec defines
  string keys and values, so a nested map may not travel.
- The DIRECTORY name is the slash command; frontmatter `name` is display only.
  ALWAYS keep them equal so the two never disagree about what a skill is called.
- `description` + `when_to_use` are concatenated into the always-on listing and
  truncated past 1,536 characters, which drops a router's later triggers
  without any error. ALWAYS leave headroom; NEVER write to the limit.
- Only `SKILL.md` loads. Sibling files are cold until something reaches them
  from it — a dispatch row, or a reference in a file a dispatch row already
  named, as `create/` does. A file no such chain reaches is unreachable.

`make skills-frontmatter` enforces all four and MUST pass before a commit
touching `skills/`; pre-commit runs the same lint on every `.md` in a commit,
linting the skill that owns a sibling, and CI runs the tree-wide target on
every PR. The fourth is an error: the lint walks the chain of names
out of `SKILL.md` and reports every `.md` under the skill that no chain
reaches. A bare basename names a file only while it is unique under the
skill; a duplicate needs a directory in front of it. `CLAUDE.md` is exempt
at any depth. The same target scans every `.md` in the tree, hidden
directories aside, for an absolute home path or a credential shape.

**Both bridges work, proven by running them**

- Codex: `codex exec --ephemeral "name one rule from the Kronael block in your
  global guidance, and one skill you can see"`. A correct bridge quotes the
  block and names a skill from `~/.agents/skills`.
- pi, two separate claims. That it RUNS: `pi --version`, which exits before
  loading any guidance, so it proves only the binary starts — it ships a
  `#!/usr/bin/env node` shebang and needs Node 20+, and `reference.md` carries
  the bun wrapper for older system nodes. That it is BRIDGED: check
  `~/.pi/agent/AGENTS.md` resolves to `~/.claude/CLAUDE.md`, or ask it for a
  rule from the wisdom file from a neutral directory.

NEVER report either bridge installed on the strength of a symlink existing —
the wiring being right and the tool running are different claims.

## Release

- Canonical version = git tag + `CHANGELOG.md`; the `release:` commit adds the
  CHANGELOG entry and tags `vX.Y.Z` (patch default). Use the `release` skill.
- ALWAYS bump `.claude-plugin/plugin.json` `version` to match the new tag in
  the same release. Nothing enforces it, and the drift is invisible: the
  manifest keeps reporting a version the bundle no longer is.
- ALWAYS bump `plugins/kronael/.codex-plugin/plugin.json` `version` too. Codex
  caches plugins by version, so a stale version keeps serving the old bridge
  skill.

## Docs map

The full map is `README.md#documentation`. Most-used here:
`kronael/sync/SKILL.md` (canonical sync), `ARCHITECTURE.md` (design
rationale), `COOKBOOK.md` (git recipes), `skills/README.md` +
`hooks/README.md` (bundle rationale by family).
