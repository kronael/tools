---
name: install
description: Install (or update) the Kronael toolkit into ~/.claude/ and bridge it into Codex. Two-way syncs skills, agents, hook scripts (reverse-syncing live-ahead refinements into the repo, never downgrading them); merges Claude hook wiring; installs Codex hook wiring; installs the wisdom skill body as ~/.claude/CLAUDE.md; offers the standalone CLI tools (rig, udfix, clp, dockbox). First-time installs get an explained questionnaire. USE when the user says "install kronael", "install kronael tools", "install" (in this repo), or runs /kronael:install.
---

# Install Kronael toolkit

Deploy the bundle into `~/.claude/` so skills, agents, and hook scripts live
in the user's persistent config and work bare (no `kronael:` prefix). When
running from Codex, also bridge the installed skills and hook wiring into
Codex's global guidance, `~/.agents/skills`, and `~/.codex/hooks.json` surfaces.

## Source location

Source root: `CLAUDE_PLUGIN_ROOT` if set and assets exist there; else CWD.
Stop if neither has assets — report which path to use.

Check `~/.claude/plugins/installed_plugins.json` for `kronael@*`: if absent,
note that `Skill("kronael:install")` won't resolve — user must say "install" here.

ALWAYS verify these exist at the source root before proceeding:
- `skills/` — bundle of skills
- `agents/` — bundle of agents
- `hooks/` — hook scripts (codex_hook.py, prompt_nudge.py, pretool_nudge.py, local.py, reclaude.py, stop.py, memory_nudge.py)
- `codex-hooks.json` — Codex lifecycle hook wiring that calls `hooks/codex_hook.py`
- `settings-recommended.json` — recommended permissions, sandbox, env, hook wiring
- `RECLAUDE.md` — re-injection template for the `reclaude` hook

If missing, you're in the wrong directory — stop and ask.

## Sync protocol

Install is ALWAYS a two-way sync, never a one-way deploy. It reconciles
source ↔ installed in BOTH directions: source-advanced files update the
install; installed-AHEAD files (local refinements the repo lacks) are surfaced
and reverse-synced INTO the repo, NEVER silently overwritten — overwriting a
live-ahead file downgrades the user's own work. A plain copy is only the
degenerate case where nothing has drifted.

- Manifest path: `~/.claude/kronael-install-manifest.json`. Shape:
  `{ "version": 1, "release": { "version", "gitCommit", "gitDescribe",
  "installedAt" }, "files": { "<installed-path>": { "source": "<repo-rel-path>",
  "source_sha256": "<sha256>" } } }`. Add `release` alongside the existing
  `files` map; NEVER drop or rewrite unrelated `files` entries.
- **Installed-release marker.** `release` records what was last installed:
  `version` (latest `## [vX.Y.Z]` in source `CHANGELOG.md`), `gitCommit`
  (source `git rev-parse HEAD`), `gitDescribe` (`git describe --tags`),
  `installedAt` (UTC timestamp). Preflight (step 0) reads it and reports the
  installed→source delta; a missing marker means "first tracked install" —
  fall back to a full drift scan.
- ALWAYS run a quiet checksum/manifest drift check before backup/copy.
- NEVER run recursive diffs on the happy path.
- Per source-owned path, compare source / installed / manifest sha256, then
  **determine direction automatically**:
  - installed == manifest → source-only update: overwrite silently.
  - source == manifest → local edit. If installed is a clean SUPERSET of source
    (additions only, no source lines lost), reverse-sync installed → source to
    capture the refinement; otherwise show diff and ask (sync back / overwrite /
    skip). NEVER overwrite a superset silently — that drops the user's work.
  - neither == manifest → conflict: show diff, ask; NEVER overwrite silently.
  - no manifest entry + content differs → treat as local edit: if installed is a
    clean superset, reverse-sync installed → source; else show diff and ask.
    NEVER blind-overwrite an unmanifested file — it can downgrade live-ahead work.
- ALWAYS write/update the manifest after a successful copy, recording the
  installed path and the source hash just installed, AND refresh the `release`
  marker (version, gitCommit, gitDescribe, installedAt) to the source just
  installed.
- NEVER treat a backup as permission to discard installed-side edits.
- NEVER touch installed-only files except the explicit prune list below.
- **Installed-ONLY skills (no source counterpart) are NOT auto-captured** —
  distinct from the live-ahead SOURCE-OWNED supersets above, which ARE
  reverse-synced. An installed skill
  with no source counterpart may be an org/local skill (arizuko/dashd/ant/routd,
  local paths, secrets) that must NOT enter public source. Reverse-sync
  (installed → repo) ONLY on the user's explicit ask: flag each installed-only
  skill, exclude or genericize the org-specific ones, add only the generic ones
  the user opts into.

## Plan & consent

Detect first-time vs update: a **new install** = neither `~/.claude/CLAUDE.md`
nor `~/.claude/skills/` exists yet. An **update** = either already exists.

- **New install**: BEFORE any copy, explain what install does in 2-3 lines,
  then present a questionnaire so the user opts into each group. On Claude use
  AskUserQuestion (multiSelect); on Codex list numbered options and ask the
  user to reply with their picks. Groups:
  - **Bundle** (skills + agents + hooks + wisdom file → `~/.claude/`) — the
    core; default on. Nothing else is useful without it.
  - **Settings restrictions** — permissions, sandbox, env (step 4).
  - **External tools** — ship, agent-browser, codex, pi, pyright, LSP servers,
    pre-commit (step 6 core batch).
  - **CLI tools** — rig, udfix, clp (step 7).
  - **dockbox** — dockerized Claude Code sandbox; needs Docker (step 7).
  - **Heavy/optional** — security-audit + video tools (step 6 separate asks).
  Run ONLY the opted-in groups. ALWAYS still back up (step 1) before any write.
- **Update**: skip the first-time questionnaire, but ALWAYS still run steps 6–7
  — NEVER silently skip tools or dockbox on a re-run (a stale binary or an
  un-offered dep is the failure this prevents). Detect external tools + install
  missing core, ask once for the heavy security/video batch, offer CLI-tools +
  dockbox (re)install. Settings still confirm before applying.

## Steps

0. **Preflight**. Run `make skills-frontmatter` (then `-fix` if it reports files)
   before copying skills. Read the manifest's `release` marker and REPORT the
   installed→source delta (installed version/commit vs source now, and the
   intervening `## [vX.Y.Z]` CHANGELOG sections). Then run the sync-protocol
   drift check for `~/.claude/{skills,agents,hooks,CLAUDE.md,RECLAUDE.md}`, the
   Kronael-managed block in `~/.codex/AGENTS.md`, and `~/.codex/hooks.json`.

1. **Backup**. ALWAYS copy current
   `~/.claude/{skills,agents,hooks,CLAUDE.md,settings.json,RECLAUDE.md}` and
   `~/.codex/{AGENTS.md,AGENTS.override.md,config.toml,hooks.json}` to
   `~/.claude/backup/<timestamp>/`
   before overwriting.

2. **Copy assets** (replace strategy):
   - `skills/*` → `~/.claude/skills/` **but skip `skills/global/`** — its body is the wisdom file, deployed in step 3. Copying it as a skill would duplicate the always-loaded content.
   - `agents/*` → `~/.claude/agents/`
   - `hooks/*.py`, `hooks/*.sh`, `hooks/lib/` → `~/.claude/hooks/`
   - `output-styles/*` → `~/.claude/output-styles/`
   - **Prune renamed hooks**: delete `~/.claude/hooks/nudge.py` and `~/.claude/hooks/extnudge.py` if present (renamed to `prompt_nudge.py` / `pretool_nudge.py`). Backup first per step 1.
   - **Prune removed kronael skills**: AFTER backup (step 1), delete the dirs
     listed in `reference.md` § "Removed kronael skills to prune" from
     `~/.claude/skills/` if present (consolidated or renamed — orphans keep
     preloading their descriptions). NEVER delete a dir not on that list —
     user-added skills stay.
   - **Prune legacy nested skill copies**: AFTER backup, follow
     `reference.md` § "Legacy nested skill copies". These stale copies preload
     duplicate skill definitions.
   - `RECLAUDE.md` → `~/.claude/RECLAUDE.md`
   - NEVER delete user-added files not in source.

3. **Install wisdom**. The `global` skill body (file: `skills/global/SKILL.md`, minus YAML frontmatter) becomes `~/.claude/CLAUDE.md`. Single destination — NEVER also write to `~/.claude/skills/global/`. If `~/.claude/CLAUDE.md` already has content, show diff and ask before overwriting. Extract any local paths / repo names / secrets references into `~/.claude/LOCAL.md` (auto-injected by `local.py`).

4. **Merge settings**. Read `settings-recommended.json` and merge into `~/.claude/settings.json`:
   - **Hooks block** (UserPromptSubmit, PreToolUse, PostToolUse, Stop, PreCompact) — replace existing matching events with the recommended wiring (paths use `~/.claude/hooks/*.py`).
   - **`cleanupPeriodDays`** — ALWAYS apply the recommended value, never ask. The 30-day default silently deletes session transcripts at startup; the toolkit keeps all history. If the user's value is lower, raise it to the recommended one; never lower it.
   - **`outputStyle`** — set live `~/.claude/settings.json` `outputStyle` to the recommended value (`80% caveman`). Without this key the style file in `output-styles/` is defined but never activated (the style silently does nothing).
   - **Recursive-removal deny guard** — `Bash(rm -r*)`, `Bash(rm -R*)`,
     `Bash(rm -fr*)`, `Bash(rm --recursive*)`. ALWAYS apply all four, never ask,
     and keep them even when the user declines the rest of the permissions
     block; they enforce the wisdom file's no-recursive-removal rule. Narrower
     forms like `Bash(rm -rf /*)` only cover two literal paths and still allow
     `rm -rf build/`. NEVER write the glob outside the parens
     (`Bash(rm -rf /)*`) — it matches nothing and silently disables the guard,
     so verify the four entries are present and paren-closed after merging.
   - **Sandbox / permission posture is loosen-only.** NEVER tighten what the
     user already chose — ALWAYS leave a looser installed value in place.
     Concretely: never flip `sandbox.enabled` false → true, never narrow
     `sandbox.excludedCommands`, never move `permissions.defaultMode` from
     `bypassPermissions` toward `default`, never drop an installed `allow`
     entry. Install may only widen (add `allow` entries, relax the sandbox).
     The recursive-removal deny guard is the one exception — it always applies.
   - **Permissions, sandbox, env** — show diff, ask which restrictions to apply.
     The deny guard above is exempt from this ask.
   - NEVER overwrite `~/.claude/settings.local.json`.

5. **Install Codex bridge**. When running from Codex (or the user asks for Codex
   support), install every bridge:
   - Global wisdom: if neither `~/.codex/AGENTS.override.md` nor
     `~/.codex/AGENTS.md` exists, symlink `~/.codex/AGENTS.md` →
     `~/.claude/CLAUDE.md` (leave it if already resolved). Any other existing
     global Codex guidance is a conflict — show and ask. NEVER rely on project
     fallback names for global guidance.
   - AFTER installing wisdom and resolving the global guidance path, merge
     the marked block from `codex/AGENTS.md` into `~/.codex/AGENTS.md`.
     Replace only the existing Kronael block; otherwise append it. NEVER
     overwrite content outside the markers. The path may symlink to the
     wisdom file, so ALWAYS perform this merge after the wisdom write.
   - `~/.codex/config.toml`: ensure top-level `project_doc_fallback_filenames`
     contains `CLAUDE.md` (before the first `[table]`; NEVER under `[tui]` etc.).
   - Symlink `~/.agents/skills` → `~/.claude/skills` (per-skill symlinks only if
     it is already a directory). If pi is installed, symlink
     `~/.pi/agent/AGENTS.md` → `~/.claude/CLAUDE.md` (skip if a real file exists).
   - Copy `codex-hooks.json` → `~/.codex/hooks.json` (after the drift preflight).
     It wires Codex's lifecycle events into `~/.claude/hooks/codex_hook.py`, which
     normalizes Codex payloads before delegating to the Kronael hooks (and drops
     context-only output for Codex `PreCompact`, which only accepts block decisions).
   - Tell the user to open `/hooks` in the next Codex TUI session and trust the
     changed hooks. One-shot verify only: `--dangerously-bypass-hook-trust`.

6. **External tools** — detect with `which <tool>`; skip if present and recent.
   Install the missing ones from `reference.md` § "External tool commands":
   the **Core** batch (ask once), then the **Security-audit** and **Video**
   batches (each ask separately — large/heavy, rarely needed).

7. **CLI tools** — (re)install the repo's standalone CLI tools per `reference.md`
   § "CLI tools": rig/udfix/clp always (idempotent Makefiles refresh a stale
   binary), dockbox only on its separate ask (needs Docker). Present only when
   the source dirs exist at the source root; else point to `cd <tool> && make
   install` from a clone and continue. NEVER fail the whole install on one
   missing toolchain — report that tool skipped.

8. **Report**: summary — **release delta** (installed vX.Y.Z → source vX.Y.Z,
   or "first tracked install"), fast drift result, X skills, Y agents, Z hooks,
   RECLAUDE.md, **pruned dirs/hooks** (name every stale skill/hook removed per
   step 2 — renamed, consolidated, or dead; say "pruned: none" when nothing
   matched so the user knows removal ran), Claude settings merged, Codex global
   guidance + skills + hooks bridge
   installed/skipped, W external tools, CLI tools installed/skipped. Claude skills are invocable
   bare (`/commit`, `/ship`, `/refine`, ...). Codex bridged skills are
   invocable as `@commit`, `@ship`, `@refine`, ...; remind the user that hook
   commands require `/hooks` trust after install/update.

## Rules

- ALWAYS backup before overwriting
- ALWAYS treat install as a two-way sync — reverse-sync a clean live-ahead
  superset (source-owned file, additions only) into the repo; NEVER overwrite a
  live-ahead file with older source, it downgrades the user's work
- NEVER delete files in `~/.claude/` not in source (org overlays, user customizations live there)
- NEVER touch `~/.claude/settings.local.json`, `~/.claude/LOCAL.md`, `~/.claude/CLAUDE.local.md`
- ALWAYS replace skills/hooks with current versions on name conflict only after drift preflight clears installed-side edits
- NEVER sync `skipDangerousModePermissionPrompt` from user back into the template
- NEVER copy Kronael skills into `~/.codex/skills`; Codex uses
  `~/.agents/skills`
- NEVER duplicate global wisdom into Codex — symlink it, or surface a conflict

## Update flow

Re-run `/kronael:install` (or "say install" in this repo) after `claude /plugin update`. Same steps; backup directory grows.
