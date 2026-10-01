---
name: sync
description: Sync the Kronael toolkit between this repo and ~/.claude on this host, first setup included, and bridge it into Codex. NOT for bringing the git line up to date with origin (use merge), pushing to origin (git push, gated), or vendoring skills into another project (use sync-tools-skills).
when_to_use: "sync kronael, sync kronael tools, sync (in this repo), /kronael:sync, install kronael, set up kronael, update kronael, ~/.claude out of date, stale or leftover skills in ~/.claude, bring ~/.claude edits back into the repo"
---

# Sync Kronael toolkit

**Sync** is this repo ↔ `~/.claude/` on this host, and nothing else: work done
in `~/.claude/` since the last sync merges into the repo, then `~/.claude/`
gets the repo's bundle fresh plus the owner's keep-list, so a file the source
dropped cannot linger. The old bundle moves to a run dir under `/tmp`; nothing
is deleted. A first setup is a sync into an empty `~/.claude/`. NOT sync —
NEVER run either as part of it: **push** (repo → `origin`, `git push` under
WISDOM § Git) and **merge origin** (`origin` → the repo's git line, `merge`).

## Terms

- **source** (`SRC`) — the repo working tree: CWD if it holds the assets
  below, else `CLAUDE_PLUGIN_ROOT`. Merge-back writes here, so a live edit
  survives only in the owner's clone — NEVER a plugin or marketplace snapshot.
- **live** — `~/.claude/`. **bundle** — the live paths sync owns and replaces:
  `skills/ agents/ hooks/ output-styles/ commands/ CLAUDE.md RECLAUDE.md
  kronael-install-manifest.json`. NOTHING else in `~/.claude/` moves:
  credentials, `settings*.json`, `LOCAL.md`, `CLAUDE.local.md`, `projects/`,
  `plugins/`, history and hook `state/` stay put.
- **manifest** — `kronael-install-manifest.json`: `release` (`version`,
  `gitCommit`, `gitDescribe`, `installedAt`) and `files`
  (`".claude/<path>": {source, source_sha256}`), the sha of each file as the
  last sync wrote it (`CLAUDE.md`: the wisdom body).
- **keep-list** — `~/.claude/kronael-keep.txt`, the owner's list of
  installed-only paths a sync carries over (`reference.md` § Keep-list). It
  lives outside the bundle and NEVER enters the repo.
- **run dir** (`RUN`) — `${TMPDIR:-/tmp}/kronael-sync-<UTC stamp>/`: scratch,
  backups for steps 5-6, and `old/`, the moved-aside bundle.

## Order of operations

`/tmp` is cleared on reboot, so the run dir MUST never hold the only copy of
work the owner wants. ALWAYS merge live edits into the repo (step 2) BEFORE
the swap (step 4) — NEVER swap first and merge from `/tmp` afterwards. What
ends only in the run dir is what the owner chose not to carry: unkept
installed-only paths and declined edits. Stopping anywhere before step 4
leaves `~/.claude/` untouched.

## Plan & consent

A **first sync** = neither `~/.claude/CLAUDE.md` nor `~/.claude/skills/`
exists. Before any write, explain sync in 2-3 lines and ask which groups to
run (Claude: AskUserQuestion multiSelect; Codex: numbered options): **Bundle**
(default on — nothing else works without it), **Settings** (step 5),
**External tools** (step 7 core), **CLI tools** rig/udfix/clp, **dockbox**
(needs Docker), **Heavy** security-audit + video, **ripwire**. Run ONLY the
opted-in groups.

Every later sync skips the questionnaire but ALWAYS still runs steps 7-8 —
NEVER skip tools or dockbox silently; a stale binary or an un-offered dep is
the failure. Settings still confirm before applying.

## Steps

0. **Preflight.** Verify at `SRC`: `skills/ agents/ hooks/ hooks/lib/
   output-styles/ commands/ codex-hooks.json settings-recommended.json
   RECLAUDE.md codex/AGENTS.md` — missing means the wrong directory: stop and
   ask. No `kronael@*` in `~/.claude/plugins/installed_plugins.json` → note
   `/kronael:sync` won't resolve; the user says "sync" in this repo. A leftover
   `~/.claude/.kronael-sync-new` or `.kronael-sync-old` is a killed swap or a
   failed rollback: STOP, show both, ask — NEVER delete or reuse either; `-new`
   holds new copies not swapped in, `-old` old copies swapped out (those live
   paths are new). Export `SRC` and `RUN`, `mkdir "$RUN"`, write `reference.md`
   § Keep-list's `keep.py` there. Read the manifest `release` and report
   installed → source (commit, version, the `## [vX.Y.Z]` CHANGELOG sections
   between); no manifest means "first tracked sync".
   Completion criterion: assets verified, `RUN` printed, release delta
   written down, no leftover swap dir.

1. **Classify.** Run `reference.md` § Classify (read-only). Every live bundle
   file lands in one class, compared by sha256 — live `I`, source `S`, manifest
   `M`: `same` (I = S), `stale` (I = M, or I is a committed source version: an
   older install), `edited` (S = M: only live changed), `both` (all three
   differ), `merged` (a `both` already in the repo), `no-base` (no `M`),
   `kept`, `shadow`, `retired` (a name the bundle dropped), `only-live` (no
   source counterpart, not kept), `junk` (caches, a session's `.claude/`).
   Exit 1 = a `BADKEEP`, `SYMLINK` or `UNRESOLVED` line; step 3 settles each.
   Completion criterion: the class counts and every decision line printed.

2. **Merge live edits into the repo.** `SRC` is the owner's clone only if
   `git -C "$SRC" rev-parse --show-toplevel` = `realpath "$SRC"` and it is
   not under `~/.claude/plugins/` or `~/.codex/`. A snapshot and any
   `edited`/`both`/`no-base` line → STOP: list them, rerun from the clone
   (`LOCAL.md` names it); NEVER swap them away.
   - `edited` → copy the live file over the repo file.
   - `both` → three-way merge per `reference.md` § Merge; a clean result goes
     into the repo; conflicts → show the hunks, ask: hand-merge, take repo, or
     take live. A base whose sha ≠ `M` is no base.
   - `no-base` → show `diff -u <repo> <live>`, ask: take live, move it to
     `LOCAL.md` (a first sync over a personal `CLAUDE.md`), or keep repo.
   - `CLAUDE.md` is the body of `skills/global/SKILL.md` — keep its
     frontmatter. NEVER merge the Codex block (`codex/AGENTS.md` markers) in.
   - The repo is public: ALWAYS read every incoming hunk for local paths, host
     or org names and secrets, and move those to `~/.claude/LOCAL.md`
     (auto-injected by `local.py`) or drop them — NEVER into the repo.
   - A declined edit ends in `RUN/old` with the old bundle: name it.
   - Then `make skills-frontmatter` (`-fix` if it reports YAML).
   Completion criterion: each such path has an outcome (merged, LOCAL.md,
   declined); `git -C "$SRC" diff --stat` shows the merged files; no
   `^<<<<<<<` line in them; the lint exits 0.

3. **Decide installed-only paths.** For each `only-live` entry show what it is
   and ask: **keep** (append it to the keep-list), **repo** (generic content
   only, on the owner's explicit yes — copy it into `SRC`), or **leave** (the
   default; it ends in `RUN/old`). NEVER put an installed-only path in the repo
   without that yes — it may be an org or private skill — and NEVER drop one
   unlisted. Each `shadow` or `BADKEEP`: the owner fixes or deletes the line.
   Each `SYMLINK`: the owner keeps it (keep-list, under a bundle dir) or `mv`s
   it into `RUN`. Each `UNRESOLVED` hook path MUST be kept or unwired first: a
   missing hook script makes `python3` exit 2, which Claude Code treats as
   blocking — every prompt and tool call in every session fails.
   Completion criterion: rerun § Classify exits 0 with no `shadow` line, and
   every `only-live` line has an answer or the stated default.

4. **Swap.** Re-run § Classify first: exit 1 → back to step 3; an `edited`,
   `both` or `no-base` line the owner did not decline → back to step 2. Then
   run `reference.md` § Swap as ONE Bash command — NEVER split it. It builds
   the new bundle in `~/.claude/.kronael-sync-new` (source, wisdom body, fresh
   manifest, then the keep-list entries copied from live), exchanges each
   bundle path with its new copy atomically, and moves the old bundle to
   `RUN/old`. A failure leaves `~/.claude/` as it was; `ROLLBACK FAILED` →
   step 0. Why: hooks fire at any moment, in any session, and one whose
   script is missing blocks its call — a split swap cannot even finish.
   Completion criterion: it printed `swap ok`; § Classify now shows only
   `same` and `kept`; manifest `gitCommit` = `git -C "$SRC" rev-parse HEAD`.

5. **Merge settings.** Copy `settings.json` and `~/.claude.json` into `RUN`
   first. Merge `settings-recommended.json` into `~/.claude/settings.json`:
   - **Hooks block** — replace each event it names with the recommended
     wiring (`~/.claude/hooks/*.py`).
   - ALWAYS apply, never ask: `cleanupPeriodDays` (raise to the recommended
     value, never lower — the 30-day default deletes transcripts at startup);
     `outputStyle` (else the style file never activates); `attribution.commit`
     `""` (unset, Claude Code asks for a `Co-Authored-By` trailer; NEVER
     `attribution: false` — versions before v2.1.281 reject it and skip the
     whole file); `bashEditDiffEnabled` `false` (unset, `auto` and
     `bypassPermissions` modes diff the tree around every Bash command;
     `CLAUDE_CODE_BASH_EDIT_DIFF` overrides it); `crossSessionInbound`
     `"refuse"` and `isolatePeerMachines` `true` (v2.1.224+; unset, delivery
     between sessions follows their permission class — `SendMessage` stays
     allowed, it is also the subagent channel).
   - **Recursive-removal deny guard** — `Bash(rm -r*)`, `Bash(rm -R*)`,
     `Bash(rm -fr*)`, `Bash(rm --recursive*)`: ALWAYS all four, even when the
     rest of permissions is declined. NEVER put the glob outside the parens
     (`Bash(rm -rf /)*` matches nothing); verify the four after merging.
   - **Loosen-only** — NEVER tighten the owner's posture: never flip
     `sandbox.enabled` to true, narrow `sandbox.excludedCommands`, move
     `permissions.defaultMode` off `bypassPermissions`, or drop an `allow`.
     Only the deny guard, `crossSessionInbound` and `isolatePeerMachines`
     override. An installed `deny` the source lists under `ask`: remove the
     `deny` and add the `ask` (deny evaluates first).
   - Rest of permissions, sandbox, env: show the diff, ask.
   - `diffSidebarOpen` `false` and `diffTool` `"terminal"` are global config,
     not settings keys: set them in `~/.claude.json`, keeping every other key;
     they apply on the next start.
   Completion criterion: reading `settings.json` back shows every
   always-apply key at its value and the four deny entries paren-closed.

6. **Codex bridge** — when running from Codex or asked: follow
   `reference.md` § Codex bridge, after copying
   `~/.codex/{AGENTS.md,AGENTS.override.md,config.toml,hooks.json}` into `RUN`.
   NEVER write the Kronael block into `~/.claude/CLAUDE.md`.
   Completion criterion: `~/.codex/AGENTS.md` holds the block, the symlinks
   resolve, and `~/.codex/hooks.json` equals `codex-hooks.json`.

7. **External tools.** `which` each; install the missing **Core** batch from
   `reference.md` § External tool commands (ask once), then ask separately for
   **Security-audit** and **Video**. Offer **ripwire** (§ ripwire) on its own
   ask: SHOW the curl-pipe one-liner and let the user run it.
   Completion criterion: each tool is present, installed, or declined.

8. **CLI tools.** (Re)install per `reference.md` § CLI tools — rig, udfix,
   clp always, dockbox on its own ask — when their dirs exist at `SRC`; else
   point to `cd <tool> && make install` from a clone. One missing toolchain
   skips that tool, never the sync.
   Completion criterion: each tool installed or skipped with the reason.

9. **Report.** Release delta (installed → source, or "first tracked sync");
   class counts; files merged into the repo (uncommitted — the owner reviews
   and commits; push is separate) and hunks moved to `LOCAL.md`; kept paths;
   every path left in `RUN/old`, with "cleared on reboot — copy out what you
   want now"; settings, Codex bridge, tools and CLI tools applied or skipped.
   A `~/.claude/backup/` dir: sync writes nothing there — give its size and
   offer to `mv` it into `RUN`. Claude skills invoke bare (`/commit`), Codex
   ones as `@commit` after `/hooks` trust.
   Completion criterion: every item above is stated, "none" included.

## Review checklist

- Live edits reached the repo (or the owner declined them) BEFORE the swap,
  and the swap ran as one command with no `.kronael-sync-*` dir left.
- Nothing outside the bundle moved; NEVER write `settings.local.json` or
  `CLAUDE.local.md`, and `LOCAL.md` only with step 2's private hunks.
- No installed-only path entered the repo without the owner's yes, and every
  path left in `RUN/old` is named in the report.
- NEVER `rm -r` anything — `mv` moves aside; the OS clears `/tmp`.
- NEVER commit, push or merge origin as part of a sync.
- NEVER copy skills into `~/.codex/skills` — Codex reads `~/.agents/skills`.
