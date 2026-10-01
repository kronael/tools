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
2. **Claude Code bundle** — `skills/`, `agents/`, `hooks/`, `output-styles/`,
   `settings-recommended.json`, `codex-hooks.json`, `RECLAUDE.md`,
   distributed via
   `.claude-plugin/` + `kronael/sync/`.
3. **Codex sync bridge** — `plugins/kronael/` and
   `.agents/plugins/marketplace.json`.
   It exposes one Codex skill that teaches Codex to run the same manual
   sync path. It does not duplicate the bundle.

## Syncing the toolkit from Codex

Follow the canonical procedure in
[`kronael/sync/SKILL.md`](kronael/sync/SKILL.md) step by step — on a first
sync present its plan/consent questionnaire first, then preflight, classify,
merge live edits into the repo, decide installed-only paths, swap, merge
settings, bridge Codex, install the opted-in CLI tools (rig/udfix/dockbox
via their Makefiles — the marketplace snapshot carries their source dirs),
report. Its Review checklist (merge before swap, never-touch list, no
recursive removal) applies verbatim. Below are only the Codex-specific
deltas.

- `/kronael:sync` is a Claude Code slash command — you can't run it
  from Codex. Run the canonical sync from the source root discovered by
  the bridge.
- A sync puts hook scripts into `~/.claude/hooks/`. Claude Code uses
  `settings-recommended.json`; Codex uses `codex-hooks.json` plus
  `hooks/codex_hook.py` to normalize Codex hook payloads before delegating to
  those same scripts.
- The Codex plugin is a thin bridge only. Its one skill is
  `plugins/kronael/skills/kronael-sync/SKILL.md`; keep sync behavior in
  `kronael/sync/SKILL.md` and update the bridge only when Codex-specific
  translation changes.
- Syncing from Codex deploys the Claude bundle to `~/.claude/`, exposes
  those installed skills to Codex through `~/.agents/skills`, and writes
  `~/.codex/hooks.json` for Codex lifecycle hooks. It also merges the marked
  block from `codex/AGENTS.md` into global Codex guidance. That block tells
  Codex to read `~/.claude/CLAUDE.md` and applicable project `CLAUDE.md` files
  in addition to `AGENTS.md`, and to take its response style from the
  installed `caveman` output style. The plugin cache still contains only the
  bridge skill.

## Codex plugin usage

GitHub marketplace path:

```sh
codex plugin marketplace add kronael/tools
codex plugin add kronael@kronael
```

Then start a fresh Codex thread and invoke:

```text
Use @kronael-sync to sync Kronael.
```

Bridge-only invocation (for repair or an existing sync):

```text
Use @kronael-sync to bridge CLAUDE.md, .claude/skills, and hooks into Codex.
```

Global installed-skill bridge:

```text
Use @kronael-sync to bridge .claude/skills and hooks into Codex.
```

After the bridge, installed Kronael skills are invoked in Codex as
`@skill-name` (for example, `@refine`). Codex hook nudges must use that form.

Codex compatibility for Claude projects:

- `~/.codex/AGENTS.md` is a real file holding the `codex/AGENTS.md` block,
  which tells Codex to read the installed `~/.claude/CLAUDE.md`. A non-empty
  `AGENTS.override.md` takes precedence and must be handled as a conflict.
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

If `@kronael-sync` cannot find the source root, refresh the GitHub
marketplace with `codex plugin marketplace upgrade kronael` (or
`kronael-local` for older installs). NEVER make the bridge copy source bundle
files into `plugins/kronael/`.

Shell translations for the non-obvious steps:

**Classify, merge, swap** — run `kronael/sync/reference.md` § Classify,
§ Merge and § Swap as written; the swap is ONE shell command, and it also
writes the wisdom file (the `skills/global/SKILL.md` body, never a
`skills/global/` skill). NEVER copy skills into `~/.claude/skills/` by hand
and NEVER `rm -rf` it: a hand copy over the old bundle keeps every file the
source dropped, and live edits not yet merged into the repo would be lost.

**Codex guidance** — merge the marked `codex/AGENTS.md` block into a real
`~/.codex/AGENTS.md`, replacing a symlink to the wisdom file. NEVER write the
block into `~/.claude/CLAUDE.md`.

**Merge settings** — if `~/.claude/settings.json` exists, splice the
hooks block, `cleanupPeriodDays`, `outputStyle`, `attribution.commit`,
`bashEditDiffEnabled`, `crossSessionInbound`, `isolatePeerMachines` and the
four `Bash(rm …)` deny entries instead of overwriting (the event wiring is
whatever `settings-recommended.json` says — don't restate it). These are
always applied, never asked — the 30-day default silently deletes session
transcripts at startup, an unset `attribution.commit` asks for a
`Co-Authored-By` trailer on every commit, an unset `bashEditDiffEnabled`
diffs the working tree around every Bash command in `auto` and
`bypassPermissions` modes, an unset `crossSessionInbound` lets Claude Code decide per message
by permission class, and the deny guard holds even when the rest of the permissions block is
declined. For the rest of permissions and sandbox, show the diff and ask:

```sh
jq -s '.[0].hooks = .[1].hooks
  | .[0].cleanupPeriodDays = .[1].cleanupPeriodDays
  | .[0].outputStyle = .[1].outputStyle
  | .[0].attribution.commit = .[1].attribution.commit
  | .[0].bashEditDiffEnabled = .[1].bashEditDiffEnabled
  | .[0].crossSessionInbound = .[1].crossSessionInbound
  | .[0].isolatePeerMachines = .[1].isolatePeerMachines
  | (.[0].permissions.deny // []) as $d
  | .[0].permissions.deny = $d + ([.[1].permissions.deny[] | select(startswith("Bash(rm "))] - $d)
  | .[0]' \
   ~/.claude/settings.json settings-recommended.json \
   > ~/.claude/settings.json.new \
  && mv ~/.claude/settings.json.new ~/.claude/settings.json
```

**Diff panel and IDE diff viewer off** — `diffSidebarOpen` and `diffTool` are
global config, not settings keys, so `settings-recommended.json` cannot carry
them. Pin both in `~/.claude.json`, keeping every other key; they apply on the
next Claude Code start:

```sh
jq '.diffSidebarOpen=false | .diffTool="terminal"' ~/.claude.json > ~/.claude.json.new \
  && mv ~/.claude.json.new ~/.claude.json
```

**Codex hooks** — copy `codex-hooks.json` to `~/.codex/hooks.json` after the
Claude hook scripts are in place. This is part of Codex bridge-only repair,
not only full syncs. In a fresh Codex TUI session, the user must open
`/hooks` once and trust changed command hooks.

**Verify** — § Classify prints only `same` and `kept`,
`~/.codex/AGENTS.md` holds the Kronael block,
`~/.agents/skills` bridges to `~/.claude/skills`, and
`~/.codex/hooks.json` exists. Report the class counts and the run dir.

## Conventions

- Boring linear code over clever code.
- Files under 200 lines.
- ALWAYS/NEVER statements in skill content.
- No secrets, no local paths, no org-specific references in source.
- Commit format: `type(scope): Message` (scope optional).
- NEVER use `git add -A` or `git commit --amend`.
- ONLY `git push` when the user asked in that message, and NEVER to
  `master`/`main` without a second approval naming the branch.
- NEVER delete files in `~/.claude/` — a sync moves the old bundle to
  `/tmp`, and installed-only files come back through the keep-list.
