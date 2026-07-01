# Changelog

## [v0.3.33] — 20260701

> kronael v0.3.33 — eval skills stay compact
>
> CEO/CTO evals now route adoption and audit work cleanly, while stop hooks enforce `/fin` follow-through.
>
> • `/ceo-eval`: adoption checklist stays default; demo audit moved to cold docs
> • `/cto-eval`: technical due diligence stays default; SLA audit moved to cold docs
> • `/create-eval`: generates project health evals without colliding with CEO/CTO audits
> • Stop hook: `/fin` sessions get one last open-items guard before stopping
> • Wisdom: repo guidance points at global wisdom; facts/refs conventions are preserved
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `/ceo-eval` and `/cto-eval` keep compact dispatch-only `SKILL.md` files:
  incoming adoption checklists remain in `checklist.md`, while local demo/SLA
  audit runbooks moved to `demo-audit.md` and `code-audit.md`.
- `/create-eval` now targets project health checks, avoiding the overloaded
  generic `eval` name and keeping adversarial audits under CEO/CTO evals.
- `hooks/stop.py` keeps the incoming throttled commit/diary nudge behavior and
  adds the local `/fin` open-items guard at stop time.
- `CLAUDE.md` remains repo-specific; global wisdom stays sourced from
  `skills/global/SKILL.md`, including the new facts/refs conventions.
- `/oracle` remains a thin alias to `/codex`; duplicated runbook content stays
  in the canonical codex skill.

## [v0.3.32] — 20260701

> kronael v0.3.32 — Codex nudges use @skills
>
> Codex hook nudges now point at installed `@skill` commands, and prompt routing covers the reasonable workflow agents.
>
> • Codex: nudges rewrite `/refine`, `/commit`, and `/py` to `@refine`, `@commit`, and `@py`
> • Prompt nudges: more workflow routes — release, specs, diagrams, security, UX, writing, model agents
> • `/fix`: bundled in source so the existing bug-fix nudge points at an installed skill
> • Hooks: adapter/pretool tests moved out of production scripts, keeping hook files under 200 lines
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Codex hook output now rewrites known Kronael nudge references from `/skill` to `@skill`, covering prompt nudges, file-extension skill nudges, and stop-time commit/diary nudges.
- Prompt keyword routing covers the reasonably nudgeable workflow, evaluation, writing, UX, release, and model-agent skills; stale `/verify` and `/schedule` routes were removed.
- Added source `skills/fix/SKILL.md` so the existing `/fix` nudge installs a bundled bug-fix workflow.
- Split `codex_hook.py` and `pretool_nudge.py` tests into dedicated pytest files, keeping production hook scripts under 200 lines.
- Codex install docs now teach `@kronael-install` and `@skill-name`, while Claude docs keep slash-command examples where they still apply.

## [v0.3.31] — 20260630

> kronael v0.3.31 — dockbox keeps parallel sessions alive, codex aliases
>
> Quitting one dockbox session no longer kills the others sharing the box, and codex runs sandbox-free with gpt/mini/spark model aliases.
>
> • dockbox: a session exiting no longer tears down the container under other live sessions — it survives until the last one leaves
> • dockbox: `codex` runs with no inner sandbox and no approval prompts, like the claude launcher
> • dockbox: new codex model aliases — `gpt` (gpt-5.5), `mini` (gpt-5.4-mini), `spark` (gpt-5.3-codex-spark)
> • rig: `rip HEAD^ ?` works — branch and commit in any order, and `?` opens the branch picker
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- dockbox: the container now runs detached with a sleeper PID 1 (`--init` reaps zombies); every session is a ref-counted `docker exec`, and the container is removed only after the last session exits. Previously the first session owned PID 1, so quitting it killed every re-entry session and `--rm` tore the box down mid-work.
- dockbox: `codex` and its aliases launch with `--dangerously-bypass-approvals-and-sandbox` — no inner bwrap, no approval prompts — matching the claude wrapper's posture inside the container.
- dockbox: added codex model aliases paralleling the claude tiers — `gpt`→gpt-5.5, `mini`→gpt-5.4-mini, `spark`→gpt-5.3-codex-spark. Fixed the usage block that still claimed the default was sonnet@medium (it's opus@high).
- rig: `rip` classifies args by role, so `rip HEAD^ ?`, `rip ? HEAD^`, `rip branch HEAD^`, and `rip branch:commit` all work; `?` opens the fzf branch picker instead of leaking into git as a bad refspec. The push command is built once, so `-n` dry-run prints exactly what runs.
- skills: synced local refinements into the repo — merge safety-gate, codex bwrap/pkill-cleanup fix, browse Playwright-debugging section, py frozen-dataclass + ruff rules, review robot-head markers, pr-draft existing-PR flow, worktree-aware diary; fixed review/humanize descriptions per wisdom (dropped workflow text, added NOT clauses).

## [v0.3.30] — 20260626

> kronael v0.3.30 — dockbox defaults to Opus, .dockboxrc sets flags
>
> dockbox now launches Claude at opus/high by default, bakes in `udfix`, and lets `~/.dockboxrc` carry default flags like `-A`.
>
> • dockbox: bare `dockbox` runs opus @ high effort (was sonnet/medium); `dockbox sonnet` now launches at high effort
> • dockbox: `~/.dockboxrc` sets dockbox flags — put `-A` there to always forward your SSH agent
> • dockbox: `udfix` (box-drawing junction repair) is now built into the image
> • rig: bare `gw` defaults to `git worktree list` instead of erroring on the missing subcommand
> • the `/sonnet` subagent drops to medium effort
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- dockbox: default Claude tool is now opus at high effort (was sonnet/medium) — `--model claude-opus-4-8 --effort high` is injected when no `--model` is given. The `sonnet` launcher alias now passes `--effort high` too.
- dockbox: `.dockboxrc` now carries dockbox flags instead of raw `docker run` args (which were injected too late to affect any dockbox flag). `~/.dockboxrc` is read before flag parsing and prepended so the command line overrides it — the full flag set, including `-A`/`-D`/`-S`. Project `.dockboxrc` runs through a gated pass that drops the privilege flags (`-A`/`-D`/`-S`) and tool/name flags (`-n`/`-d`/`-x`) so an untrusted repo can't auto-escalate. Flag reading (`read_rc`) and flag→effect (`apply_flag`) are now single shared helpers; `apply_flag` always returns 0 so a tokenless `-g` can't trip `set -e`, and `OPTARG` is defaulted for no-arg flags under `set -u`.
- dockbox: `udfix` is built into the image from its own Makefile (`make -C udfix install PREFIX=/usr/local/bin`); the build context widened to the repo root, and udfix's Makefile gained an overridable `PREFIX`.
- skills: the `/sonnet` subagent now runs at medium effort (was high) — the interactive `dockbox sonnet` launcher is the one at high effort.
- rig: bare `gw` now runs `git worktree list` instead of erroring on the missing subcommand; explicit args still pass through.
- install: the install skill detects its source root (`CLAUDE_PLUGIN_ROOT` vs CWD) and checks `~/.claude/plugins/installed_plugins.json` for `kronael@*`, explaining why `Skill("kronael:install")` fails when the plugin isn't registered (merged from origin/master).

## [v0.3.29] — 20260623

> kronael v0.3.29 — rig alias fix, dockbox re-entry, /codex restored
>
> Fixes rig's git-alias symlinks (they were passing their own name to git), re-enters a running dockbox, and restores `/codex`.
>
> • rig: `gl`/`gis`/`gig`/`gitg` symlinks now work — they were leaking their own name as a git arg
> • rig: new `gw` alias for `git worktree`; an animated terminal demo gif is embedded in the README
> • dockbox: re-running for an active project now `docker exec`s into the live box, not a new container
> • `/codex` is the canonical second-opinion skill again; `/oracle` is a thin alias for it
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- rig: fixed `gl`/`gis`/`gig`/`gitg` — invoked as symlinks they passed their own name to git (`git log gl` → unknown revision) because the dispatch arm was missing a `shift`. Added `gw` → `git worktree`, wired through every install/usage/clean surface.
- rig: committed the terminal demo as `rig/demo/demo.gif` (rendered headlessly via a virtual-clock recorder + `agg`), embedded it in the README, and pointed `make demo` at it. Demo now renders the title at t=0 and gives the graph its own screen.
- dockbox: re-running `dockbox` for a project whose container is already up now `docker exec`s the requested tool into the live box as the host user, instead of spawning a second container — model/effort ride in the command so they still apply, while run-time mounts/network stay frozen at creation. The re-entry probe runs before provisioning, so it skips the settings-merge and `find` walk it would otherwise discard.
- skills: restored `/codex` as the canonical second-opinion skill with `/oracle` as a thin alias (reverts the v0.3.26 codex→oracle rename); fixed the install prune list so reinstalls no longer delete `~/.claude/skills/codex`. Trimmed the duplicate `oracle` keyword from codex's `when_to_use`.

## [v0.3.28] — 20260622

> kronael v0.3.28 — rig demo, sonnet default
>
> rig gets an animated terminal demo, and dockbox now launches Claude at sonnet/medium by default instead of haiku.
>
> • dockbox: bare `dockbox` now runs sonnet @ medium effort — haiku is opt-in (`dockbox haiku`) for speed/cost
> • rig: scripted asciinema demo walks the detached-HEAD workflow — checkout, push, rebase, merge, fixup
> • rig demo: simulated fzf picker shows `rco ?` narrowing the branch list as you type
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- rig: added a scripted terminal demo (`rig/demo/run.ts` + `make demo`) covering the detached-HEAD workflow — orientation (`gl`/`gis`/`gig`), checkout, push, rebase, merge, fixup squash. Includes an honest fzf-picker simulation for `rco ?` that narrows the branch list by subsequence match as the query types, plus narrative framing (old-way contrast, inline jargon notes) so the detached-HEAD idea reads as intentional, not broken.
- dockbox: default tool is now sonnet at medium effort (was haiku). `--model claude-sonnet-4-6 --effort medium` is injected only when no `--model` is given; explicit `dockbox haiku` drops to the fast/cheap model, and `dockbox sonnet`/`opus`/`fable` are unchanged.

## [v0.3.27] — 20260622

> kronael v0.3.27 — dockbox haiku default, settings fix, wisdom refinements, rig aliases
>
> • dockbox: default model haiku; sandbox restart loop fixed (patches settings.json directly)
> • settings-recommended.json: rm deny glob fixed (`/)*` → `/*)`); gh-comment allow rules added
> • global wisdom: Grug rules + no-tables response style added; gh-comment ALWAYS rule
> • skills refined: oracle adversarial framing, gh-comment Codex fallback, bugs/py ALWAYS/NEVER
> • hooks: post_tool_nudge.sh stderr fixed (2>&1 → 2>/dev/null)
> • rig: git alias shortcuts gl, gis, gig, gitg, gp, gpc, gpa
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- dockbox: default model now `claude-haiku-4-5-20251001` — fast and cheap; re-select with `--model` or model alias when you need more. Sandbox restart loop fixed: dockbox now patches a merged `settings.json` with `sandbox.enabled: false` and mounts it `:ro` so the Claude Code instance never tries to restart into bubblewrap.
- settings-recommended.json: rm deny rules had glob outside parens (`Bash(rm -rf /)*` → `Bash(rm -rf /*)`); fix makes `rm -rf /home` actually denied. Added `Bash(gh pr comment*)`, `Bash(gh api repos/*/pulls/*/reviews*)`, `Bash(gh api repos/*/pulls/*/comments*)` to allow — needed for `/gh-comment` workflow.
- global wisdom (skills/global/SKILL.md → ~/.claude/CLAUDE.md): added Grug rules block (match tool to task weight, locality of behavior, Chesterton's fence); added no-tables/no-headers sentence to Response Style; added ALWAYS rule to use `/gh-comment` for PR comment/review posting.
- skills/oracle: adversarial framing rules tightened; `-s danger-full-access` flag clarified as the correct flag for skipping bubblewrap in containers.
- skills/gh-comment: Codex fallback — AskUserQuestion unavailable in Codex; replaced with explicit chat-confirmation requirement.
- skills/bugs, skills/py: SHOULD→ALWAYS/NEVER; removed duplicate global rules; added NEVER yield individual items batch rule to py.
- hooks/post_tool_nudge.sh: stderr was leaking into hook stdout (interpreted as JSON); fixed with `2>/dev/null`.
- rig: added git alias shortcuts installed as symlinks — `gl` (log), `gis` (status -uno), `gig`/`gitg` (graph log), `gp`/`gpc`/`gpa` (cherry-pick).

## [v0.3.26] — 20260622

> kronael v0.3.26 — Codex hooks, dockbox tools, caveman style, oracle skill
>
> • Codex hooks install to `~/.codex/hooks.json` through `codex-hooks.json`
> • `codex_hook.py` adapts Codex payloads before calling installed Claude hooks
> • `PreCompact` no longer returns invalid context JSON in Codex
> • dockbox: first positional arg selects tool (codex, haiku, sonnet, opus, fable, any binary)
> • `output-styles/80-caveman.md` added; activated in settings-recommended.json
> • `/codex` skill renamed to `/oracle`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Added Codex lifecycle hook wiring via `codex-hooks.json`, installed to
  `~/.codex/hooks.json`.
- Added `hooks/codex_hook.py` to normalize Codex hook payloads, translate prompt
  and tool context output, and delegate to the installed Kronael hook scripts.
- Fixed Codex `PreCompact` handling so Claude-style context output is suppressed
  instead of being returned as invalid Codex hook JSON; block decisions still
  pass through.
- Updated install docs and bridge prompts so Codex installs `~/.agents/skills`
  and `~/.codex/hooks.json`, with `/hooks` trust as the explicit review step.
- Fixed `post_tool_nudge.sh` to pass the original hook payload through to
  `stop.py` when the periodic nudge fires.
- dockbox: first positional arg is now the tool entrypoint; model aliases
  (haiku/sonnet/opus/fable) map to `claude --model <id>`; `-d` flag added as
  explicit tool selector; `-x` kept hidden for compat.
- Added `output-styles/80-caveman.md` (stripped-not-broken output style);
  `settings-recommended.json` activates it via `outputStyle`.
- Renamed `skills/codex` → `skills/oracle`; `codex` added to install prune list.

## [v0.3.25] — 20260618

> kronael v0.3.25 — /sub fully removed
>
> The old /sub skill file is deleted and its "spawn a sub" trigger cleaned from /dispatch. No stray references remain.
>
> • `skills/sub/SKILL.md` deleted from repo
> • /dispatch when_to_use: "spawn a sub" → "background agent"
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Deleted `skills/sub/SKILL.md` — the rename to `/dispatch` is now complete in git history
- Removed "spawn a sub" trigger from `/dispatch` `when_to_use`; replaced with "background agent"

## [v0.3.24] — 20260618

> kronael v0.3.24 — eval skill polish
>
> /ceo-eval and /cto-eval checklists moved to sibling files; SKILL.md bodies are now workflow-only. Minor ALWAYS/NEVER fixes across model-tier skills.
>
> • /ceo-eval and /cto-eval: checklist bodies moved to checklist.md sibling files
> • SKILL.md for each eval skill is now <10 lines — workflow dispatch only
> • haiku/sonnet/fable: REJECT/Do NOT → NEVER/ALWAYS
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `/ceo-eval` and `/cto-eval` checklists (tables, verdict templates, decision rubrics) moved to `checklist.md` sibling files; SKILL.md reduced to workflow-only dispatch per wisdom rules
- `NEVER`/`ALWAYS` discipline applied to `/haiku`, `/sonnet`, `/fable` (replaced `REJECT` and `Do NOT`)

## [v0.3.23] — 20260618

> kronael v0.3.23 — model-tier skills restored; /dispatch replaces /sub
>
> Each model now has its own skill and agent definition. /haiku, /sonnet, /opus, /fable are back. /sub is renamed /dispatch for generic fire-and-forget. CEO and CTO eval lenses added.
>
> • `/haiku` restored — uses `subagent_type: "haiku"` via new agent definition
> • `/sonnet`, `/opus`, `/fable` restored with consistent `subagent_type` dispatch
> • `/dispatch` replaces `/sub` — generic background agent, no model override
> • `/ceo-eval` and `/cto-eval` added — business and technical adoption evaluation
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Restored `/haiku`, `/sonnet`, `/opus`, `/fable` as individual skills; all use `subagent_type` (haiku now has an agent definition pinning the model)
- Added `agents/haiku.md` — consistent with sonnet/opus/fable agent definitions
- Renamed `/sub` → `/dispatch` for generic fire-and-forget background work; `/sub` added to install prune list
- Added `/ceo-eval` (business adoption: ROI, TCO, license risk, lock-in, make-vs-buy) and `/cto-eval` (technical due diligence: build quality, arch, ops readiness, maintenance forecast)

## [v0.3.22] — 20260618

> kronael v0.3.22 — /sub absorbs model-tier skills
>
> Four separate model-routing skills (haiku, sonnet, opus, fable) are gone. Use `/sub haiku`, `/sub sonnet`, `/sub opus`, or `/sub fable` instead — one skill, same dispatch.
>
> • `/sub` now accepts an optional tier prefix: haiku/sonnet/opus/fable
> • haiku uses `model: "haiku"` directly; sonnet/opus/fable use `subagent_type` to pin effort via agent definitions
> • `/haiku`, `/sonnet`, `/opus`, `/fable` skills removed
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `/sub` extended with optional model-tier prefix dispatch (haiku → `model: "haiku"`; sonnet/opus/fable → `subagent_type` pinning effort via agent definitions)
- Removed `/haiku`, `/sonnet`, `/opus`, `/fable` skills — all model routing goes through `/sub`
- `skills/README.md` updated to reflect consolidated escalation path

## [v0.3.21] — 20260614

> kronael v0.3.21 — Install reaches the CLI tools
>
> Install now also refreshes the standalone CLI tools and walks first-time users through what gets installed.
>
> • Install (re)installs rig, udfix, clp, dockbox so the binaries stop drifting from the repo
> • First-time installs get a questionnaire to opt into each group; re-runs skip it
> • Drift check updates repo-advanced files silently, asking only when you have local edits
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Install now (re)installs the standalone CLI tools (rig, udfix, clp, dockbox) via their Makefiles, so `~/.local/bin` binaries track the repo instead of going stale
- First-time installs present a plan/consent questionnaire (Claude AskUserQuestion, Codex numbered options) to opt into each install group; updates skip it
- Drift preflight auto-detects direction: source-newer files overwrite silently (normal repo-advanced update); only genuinely installed-newer edits trigger the sync-back prompt
- Codex bridge skill and AGENTS.md kept in sync with the canonical installer

## [v0.3.20] — 20260613

> kronael v0.3.20 — Codex install exposes skills
>
> Codex installs now bridge the installed Kronael skills into Codex, so `/skills` shows the toolkit instead of only the installer.
>
> • Codex install auto-links `~/.agents/skills` to installed `~/.claude/skills`
> • Existing `~/.agents/skills` dirs get per-skill symlinks instead of replacement
> • Source discovery uses Codex marketplace snapshots, not the bridge-only plugin cache
> • Installer drift preflight protects local edits before overwrite
> • PostToolUse nudge state moved into the repo git dir
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Codex install now runs the global skills bridge after the canonical Claude install, exposing installed Kronael skills and their scripts through `~/.agents/skills`
- Existing `~/.agents/skills` directories are preserved; the bridge adds per-skill symlinks for source-owned Kronael skills and reports conflicts
- `kronael-install` source discovery now checks Codex marketplace snapshots and avoids treating the bridge-only plugin cache as the bundle source
- README, AGENTS.md, ARCHITECTURE.md, and plugin metadata now state that the Codex plugin contains only `kronael-install`
- Install procedure adds a fast drift preflight before backup/copy so installed-side edits are surfaced before overwrite
- `post_tool_nudge.sh` stores throttle state in the current repo git dir instead of shared `~/.claude/tmp`

## [v0.3.19] — 20260613

> kronael v0.3.19 — Codex bridge skill polish
>
> The `kronael-install` skill now dispatches correctly before it reads install steps, local-checkout instructions are complete, and the bridge prompt is consistent everywhere.
>
> • Dispatch routing moved before source-root discovery — bridge-only users no longer wade through install steps
> • Clone instructions added for when no local checkout exists
> • Bridge prompt synced across plugin.json, AGENTS.md, and README
> • README and AGENTS.md expanded with local path, troubleshooting, and AGENTS.md pointer example
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `kronael-install` `## Invocation` section moved before `## Source Root` — dispatch (install vs bridge-only) now happens before the LLM hits install steps
- Clone hint added for users with no local checkout; AGENTS.md pointer example added to Codex Bridge section
- Bridge `defaultPrompt` in `plugin.json` synced to match `AGENTS.md` and `README` wording (`CLAUDE.md and .claude/skills`)
- README: expanded local checkout path, bridge-only usage, troubleshooting section
- ARCHITECTURE.md: noted that bridge requires full source checkout visible

## [v0.3.18] — 20260613

> kronael v0.3.18 — Codex installer bridge, codex skill, dockbox -D fix
>
> Codex can now install the toolkit, the codex second-opinion skill is in the bundle, and `dockbox -D` can finally reach the docker socket.
>
> • Codex installer bridge — one `kronael-install` skill runs the canonical installer; no bundle duplication
> • `codex` skill replaces the near-identical `oracle`, pinned to the newest model at high effort
> • `dockbox -D` socket fix — the runtime user now keeps the docker group across the privilege drop
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- Codex installer bridge — `plugins/kronael/` (thin `.codex-plugin` exposing one
  `kronael-install` skill) + `.agents/plugins/marketplace.json`. The skill
  follows the canonical `kronael/install/SKILL.md`; it never duplicates the
  bundle. Includes Codex project-compat notes (`CLAUDE.md` fallback,
  `.claude/skills` → `.agents/skills` symlink).
- `codex` skill in the bundle — drives the codex CLI for a second opinion,
  pinned to the account's newest model at high effort.

### Changed

- `codex` replaces the near-identical `oracle` as the bundle's second-opinion
  skill; `scavenge` rewired `oracle` → `codex`.

### Fixed

- `dockbox -D`: the runtime user lost the docker socket group on the `gosu`
  privilege-drop (numeric `uid:gid` skips `initgroups`). `dockbox-init` now adds
  the user to each `--group-add` gid in `/etc/group` and drops via
  `gosu "$USERNAME"`. Verified on a fresh image. Also fixed two latent
  cold-build breakers: `uv tool install` one-tool-per-call, gitleaks
  `v9.1.0`/`amd64` → `8.30.1`/`x64`.

## [v0.3.17] — 20260612

> kronael v0.3.17 — skill routers, CI, and three new skills
>
> The 15 creative skills collapse into one `create` router and the bloated `ops` skill splits into a `software` router, cutting the always-loaded skill listing while keeping every generator a read-away. Plus CI, and three skills pulled into the bundle.
>
> • `create` router — one preloaded entry dispatches to 12 cold generator files (web, video, ASCII/p5.js art, diagrams); ~65% smaller listing, 14 fewer entries
> • `software` router — Docker, CI, deploy, observability runbooks extracted from `ops`, which drops 296→53 lines
> • New skills: `scavenge` (codify public best practice), `eye-13yo` (fresh-eyes UX walkthrough), `oracle` (codex second opinion)
> • `writing` + `humanize` now in the bundle; prose skills (tweet, pr-draft, readme, diary) reference them
> • GitHub Actions CI: per-component test + lint workflows, generated by `make gen-ci`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- `create` router skill — single preloaded `SKILL.md` dispatching to cold per-mode data files (web, video, art, diagram); replaces 15 `create-*` skills. Verified ~65% smaller skill-listing footprint (1,980→685 bytes) plus 14 fewer listing entries
- `software` router skill — `docker`, `ci`, `deploy`, `observe`, `uvx-tools` runbooks extracted from `ops`
- `scavenge`, `eye-13yo`, `oracle` skills added to the bundle
- `writing` and `humanize` skills added; `tweet`/`pr-draft`/`readme`/`diary` now reference them
- `.github/workflows/` CI — `test-udfix`, `test-hooks`, `lint`, generated from `.github/templates/*.tmpl` by `make gen-ci`
- `skills/CLAUDE.md` + per-router `CLAUDE.md` — router structure + edit conventions; `BUGS.md` review queue

### Changed

- `ops/SKILL.md` slimmed 296→53 lines (deep runbooks moved to `software/`)
- `resolve` scan widened to match both `description` and `when_to_use` (the verified Claude Code preload fields, capped 1,536 chars/entry)
- Router frontmatter: `description` = summary + NOT clause, keywords in trimmed `when_to_use`
- `create-humanizer` → `humanize` (ported body + MIT LICENSE intact); install prunes removed `create-*` dirs on reinstall

### Fixed

- Hook nudge state moved off shared `/tmp` to `~/.claude/tmp`; `stop.py` only checks the diary inside a git repo
- `udfix` Makefile binary name; removed committed build artifacts
- Logged (not fixed): `dockbox -D` drops the docker socket group on the gosu privilege-drop — see `BUGS.md`

## [v0.3.16] — 20260612

> kronael v0.3.16 — udfix tool, diagrams skill, docs + security cleanup
>
> A new `udfix` CLI repairs broken box-drawing junctions in ASCII diagrams, a `diagrams` skill teaches the workflow, and the bundle's docs and hooks got a hard pass for drift and shared-host safety.
>
> • `udfix` — pipe an ASCII diagram through it and crossing/T junctions (┬ ┴ ├ ┤ ┼) get the right character
> • `diagrams` skill — how to draw box diagrams and fix them with `udfix`; `@readme` uses it for ARCHITECTURE.md
> • `credits` skill + `NOTICE` — attribution practice for ported/LLM-assisted work
> • Hooks no longer write state to shared `/tmp`, and stop only nags about diaries inside a git repo
> • Docs deduplicated to single-owner facts — deleted the fictional WORKFLOW.md
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- `udfix` — Go CLI that fixes Unicode box-drawing junction chars from neighbor connectivity (stdin → stdout); table-driven, tested
- `diagrams` skill — ASCII architecture/flow diagram authoring; pipes through `udfix`
- `credits` skill + root `NOTICE` — acknowledge upstream sources (humanizer, hermes-agent, design.md, get-shit-done) and AI-assisted provenance
- `make workflows` — auto-generates the `PROJECTS` list from subdirs exposing `test` + `clean`; `make test`/`clean` iterate it

### Changed

- Root docs deduplicated to single-owner facts: README owns the CLI inventory + docs map, ARCHITECTURE owns the install rationale, `settings-recommended.json` + hook source own hook wiring; other docs link
- `skills/README.md` replaces the drift-prone per-skill tables with categories + `ls skills/` pointer; keeps the workflow cluster diagram
- All hooks guard execution behind `if __name__ == '__main__'` so the suite can import them (59 tests collect)
- `diagram` skill renamed `diagrams` (matches `bugs`/`specs`)

### Fixed

- **Security:** hook state moved from shared `/tmp` to `~/.claude/tmp` (symlink-clobber risk on multi-user hosts)
- **Security:** install procedure installs `trufflehog` via `go install`, not `curl … | sh` to `/usr/local/bin`
- `stop.py` only checks/nudges the diary inside a git repo — no more stray `.diary/` dirs in arbitrary directories
- `udfix` Makefile built a binary named `ascfix`; removed two build artifacts that had been committed
- Doc drift: deleted `WORKFLOW.md` (described a `/ship → /build` hierarchy; `/build` never existed), corrected `reclaude.py` to PreCompact-only, `/dispatch` → `/resolve`, dropped the dead `/build` nudge route

## [v0.3.15] — 20260611

> kronael v0.3.15 — tiered model hierarchy + PostToolUse nudge
>
> Skills now route through a three-tier model ladder (sonnet → opus → fable), each tier pinned to a named agent definition that sets model and effort at the API level — not prompt text.
>
> • `/opus` re-added — fable model at default effort; slots between `/sonnet` and `/fable` for heavy-but-not-maximum tasks
> • `agents/fable.md`, `agents/sonnet.md` pin model + effort tier so skills use `subagent_type:` instead of `model:` + prompt-text nudges
> • `post_tool_nudge.sh` (PostToolUse) fires after every tool call, throttled, nudges commit + diary on stop
> • `/resolve` rewritten — recalls context via `/recall-memories` instead of diary/facts grep
> • `/review` gets a fable adversarial reverification pass that drops false positives before posting
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- `/opus` skill — fable-model background agent with prompt-based xhigh effort hint; re-introduced as mid-tier between `/sonnet` and `/fable` (was removed in v0.3.13)
- `agents/fable.md`, `agents/sonnet.md` — agent definitions that pin `model` + `effort` at the API level; `/fable` and `/sonnet` skills now use `subagent_type:` to invoke them
- `hooks/post_tool_nudge.sh` (PostToolUse hook) — throttled (100 calls/10 min), delegates to `stop.py` for commit and diary nudging
- `/hacker-eval` and `/merge` skills added to bundle

### Changed

- `/fable`: switches to `subagent_type: "fable"` (was `model: "fable"`); prefers `/opus` for tasks not requiring maximum intelligence
- `/sonnet`: switches to `subagent_type: "sonnet"` (was `model: "sonnet"`); escalates to `/opus` instead of `/fable`
- `/resolve` major rewrite — uses `/recall-memories` for context recall; description and dispatch section updated
- `/review` adds step 4 fable reverification pass — reads diff fresh, adversarially reverifies sonnet findings, drops false positives
- `/pr-draft` base detection uses `git merge-base HEAD origin/main` instead of `origin/main..HEAD`
- `skills/global/SKILL.md` synced: adds `/bugs` skill pointer and `BUGS.md` triage rule

## [v0.3.14] — 20260610

> kronael v0.3.14 — bugs skill + sharper nudges
>
> The `/bugs` issue-queue skill is finished, and the prompt nudger now points you at `/bugs` and `/specs`.
>
> • `/bugs` skill — record open issues in `bugs.md` with a fixed entry format, lifecycle, and prune-to-diary flow
> • Prompt nudger routes "bug"/"spec" mentions to `/bugs` and `/specs`
> • Fuzzy matcher matches singular/plural across a trailing "s", so 3-letter words like "bug" route too
> • CLAUDE.md rewritten as a concise repo-specific guide instead of a copy of the global wisdom
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- `/bugs` skill: the `bugs.md` open-issues queue — entry format, record/mark/prune lifecycle, optional aggregation. Policy stays in CLAUDE.md "Bug Triage Protocol", which now points to the skill
- `prompt_nudge.py` routes `bug`/`bugs` → `/bugs` and `spec`/`specs` → `/specs`

### Changed

- Root `CLAUDE.md` rewritten as a concise (123-line) repo-specific guide — what the repo is, commands, install architecture, conventions — dropping the duplicated global wisdom
- `prompt_nudge.py` fuzzy matcher normalizes a trailing `s`, matching singular/plural with one dict entry and bypassing the `len < 4` guard that blocked short keywords

## [v0.3.13] — 20260610

> kronael v0.3.13 — creative skills bundle, opus dropped
>
> Twelve `create-*` skills land for HTML mockups, SVG architecture diagrams, p5.js sketches, ASCII art, and Manim videos; `/opus` and `/oracle` removed.
>
> • 12 `create-*` skills — HTML/SVG/ASCII generators (excalidraw, p5js, ascii-art/video, manim, design-md, …)
> • `/oracle` (codex second opinion) and `/opus` removed — bundle standardizes on `/fable` for hard reasoning
> • `/sonnet` escalation now points at `/fable` instead of `/opus`
> • `prompt_nudge.py` restored — UserPromptSubmit keyword routing was deleted but not replaced in v0.3.11
> • Web one-pager landing spec drafted in `specs/5-web-onepager.md`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- 12 `create-*` creative-output skills ported from [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent/tree/main/skills/creative) under a `create-` prefix that scopes discovery and avoids collisions with engineering skills (`go`, `rs`, …). Only local-only ones bundled: `create-architecture-diagram`, `create-ascii-art`, `create-ascii-video`, `create-claude-design`, `create-design-md`, `create-excalidraw`, `create-humanizer`, `create-manim-video`, `create-p5js`, `create-popular-web-designs`, `create-pretext`, `create-sketch`. Four upstream skills needing paid APIs / cloud / external apps were dropped (Suno, ComfyUI Cloud, TouchDesigner, baoyu image-gen)
- `specs/5-web-onepager.md` — plan for terminal-native README landing (5 anchor visuals, 11-section layout, 9 implementation phases)
- README, CLAUDE.md, skills/README.md document the `create-*` naming convention

### Changed

- `/sonnet` escalation arrow now points at `/fable` instead of `/opus`
- `/fable` description and footer drop the `/opus` references

### Removed

- `/oracle` skill (codex CLI second opinion, unused)
- `/opus` skill (standardize on `/fable` for hardest reasoning)

### Fixed

- `hooks/prompt_nudge.py` restored from backup — the v0.3.11 merge intended to rename `nudge.py` → `prompt_nudge.py` but only the deletion landed, leaving `settings-recommended.json` referencing a non-existent file
- `settings-recommended.json` UserPromptSubmit hook list now wires the real script paths

## [v0.3.12] — 20260610

> kronael v0.3.12 — fable skill, effort levels wired
>
> /fable spawns the most capable model; opus, fable, and sonnet now run at the right effort level.
>
> • `/fable` skill — spawns claude-fable-5 background agent at xhigh effort
> • `/opus` effort updated to xhigh — best for coding and agentic tasks
> • `/sonnet` effort set to high
> • dockbox image: `libfontconfig1`/`libfreetype6` — t64 variants don't exist on forky
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `/fable` skill added — spawns `claude-fable-5` background agent (`model: "fable"`, `Effort: xhigh`)
- `/opus` effort updated: `Budget: max` → `Effort: xhigh`; `/sonnet` effort set to `high`
- dockbox image: `libfontconfig1t64`/`libfreetype6t64` → `libfontconfig1`/`libfreetype6` (t64 variants absent on forky)

## [v0.3.11] — 20260610

> kronael v0.3.11 — dockbox auto-resume, forky image fix
>
> Dockbox detects prior sessions automatically and the container image now builds on Debian forky with all Rust and Playwright dependencies.
>
> • `dockbox` auto-detects past session — `--resume` passed only when a `.jsonl` exists; `-N` flag removed
> • Container `/tmp` mounted as tmpfs — scratch stays ephemeral, no host writes
> • Image: `libpq-dev` + `libssl-dev` — postgres and openssl Rust crates compile cleanly
> • Image: playwright chromium deps explicit — fixes Debian forky (t64 lib rename)
> • oracle skill: pipe `/dev/null` to codex exec — unblocks stdin hang
> • Hooks: diary nudge fixed for monorepos
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `dockbox`: `/tmp` mounted as tmpfs — scratch stays ephemeral
- dockbox image: `libpq-dev` + `libssl-dev` — postgres and openssl-sys Rust crates

### Changed
- `dockbox`: auto-detects past session via `~/.claude/projects/<slug>/*.jsonl`; `--resume` only when session exists; `-N` flag removed

### Fixed
- dockbox image: chromium deps installed explicitly, `--with-deps` dropped — Playwright on Debian forky (t64 transition)
- oracle skill: `/dev/null` piped to codex exec — unblocks stdin hang
- hooks: diary nudge fixed for monorepos; `git_run` refactored

## [v0.3.10] — 20260605

> kronael v0.3.10 — dockbox -N starts a fresh session
>
> Opt out of the default resume with one flag when you want a clean slate.
>
> • `dockbox -N` — skips `--resume`, starts a new claude session
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `dockbox -N` — new-session flag; omits the default `--resume` passed to claude

## [v0.3.9] — 20260605

> kronael v0.3.9 — dockbox resumes last session by default
>
> Dockbox now picks up where you left off — no more starting from scratch each launch.
>
> • `dockbox` passes `--resume` to claude by default — last session resumes automatically
> • `fix` skill — reads `./capture.png` or `/tmp/capture.png` when the bug target is unclear
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed
- `dockbox`: passes `--resume` to `claude` by default; non-claude entrypoints unaffected
- `skills/fix/SKILL.md`: auto-loads `./capture.png` or `/tmp/capture.png` when no clear target is given

## [v0.3.8] — 20260604

> kronael v0.3.8 — dockbox sh re-enters running container
>
> `dockbox sh` now execs into the already-running container instead of erroring.
>
> • `dockbox sh` on a live container → `docker exec` into it; no need to know the container name
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed
- `dockbox sh` — if the container is already running, execs into it via `docker exec -it <name> /bin/zsh` instead of printing an error

## [v0.3.7] — 20260604

> kronael v0.3.7 — Cargo tmpfs, dockbox sh, skill fixes
>
> Rust builds no longer pollute the host; drop into a shell with one word.
>
> • `dockbox sh [dirs...]` — enter the container with zsh instead of claude
> • `CARGO_TARGET_DIR` redirected to a tmpfs — `target/` never written to host
> • Commit skill: capitalize first word after the type colon
> • Global skill: question-spending rule synced to installed CLAUDE.md
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `dockbox sh` subcommand — drops into `/bin/zsh` with the full dockbox setup; all flags (`-G`, `-S`, `-D`, etc.) still apply

### Changed
- `dockbox`: `CARGO_TARGET_DIR=/tmp/cargo-target` set unconditionally; dedicated tmpfs mounted at that path — Cargo builds stay in RAM, host `target/` untouched
- `skills/commit/SKILL.md` — subject rule: capitalize first word after the type colon (`feat: Add` not `feat: add`)
- `skills/global/SKILL.md` — added question-spending rule (synced from installed CLAUDE.md)

## [v0.3.6] — 20260604

> kronael v0.3.6 — dist/build off ephemeral mounts, commit skill simplified
>
> Build tools that rm -rf their output dir no longer hit EBUSY inside dockbox.
>
> • `dist` and `build` removed from ephemeral overmounts — `rm -rf dist` works; container writes to host path as a plain bind mount
> • Commit skill rewritten to conventional commits format with imperative mood and breaking-change rules
> • Stop prompt suggestions disabled in recommended settings
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed
- `dockbox`: `dist` and `build` removed from `EPHEMERAL_DIRS` — tmpfs-mounting them caused EBUSY when build tools did `rm -rf dist`; container now writes to host path directly
- `skills/commit/SKILL.md` — rewritten to conventional commits format (`feat:`, `fix:`, `chore:` etc.), imperative mood, breaking change rules; trimmed from 80 → 38 lines
- `settings-recommended.json` — stop prompt suggestions disabled

## [v0.3.5] — 20260531

> kronael v0.3.5 — pkg-config in dockbox
>
> hidapi and other C-binding crates now compile inside the sandbox.
>
> • `pkg-config` added to the image — Rust crates that probe `libudev` (hidapi, ledger, trezor) no longer fail at link time
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Fixed
- `pkg-config` missing from dockbox apt install — `hidapi`/`libudev`-dependent Rust crates now build inside the container

## [v0.3.4] — 20260531

> kronael v0.3.4 — gcloud in dockbox, video pipeline, throttled nudges
>
> Dockbox now ships gcloud and forwards credentials safely; the video skill becomes a full render pipeline with working ant simulations and a text card system.
>
> • `dockbox -G` mounts `~/.config/gcloud` ro — gcloud ops work inside the sandbox without leaking creds by default
> • gcloud CLI baked into the image — `gcloud storage cp` and friends available without setup
> • Dockbox ephemeral `find` capped at depth 4 — no more ARG_MAX crash on deep monorepos
> • `create-video-render` restructured: engine index + per-flavor files (Remotion, Manim, Bevy, swarm, shaders)
> • Ant stigmergy simulation — headless mp4/gif renderer with 4 variants, `--speed`, `--text`/`--cards` text overlays
> • Commit/stop hooks throttle their nudges to once per 10 min — less noise on long sessions
> • Spec skill: draft → planned → partial → shipped lifecycle; draft status blocks implementation
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `dockbox -G` flag — mounts `~/.config/gcloud` ro (opt-in, like `-g` for GH tokens); silently skipped when absent
- `google-cloud-cli` installed in dockbox image via apt; `gcloud`, `gsutil`, `bq` on PATH
- `skills/create-video-render/examples/ant_coordination.py` — headless ant stigmergy renderer: 4 variants (`default`, `race`, `bloom`, `chaos`), `--speed N` timelapse, `--gif`, `--text` / `--cards JSON` per-element text overlays with fade timing
- `skills/create-video-render/examples/p5_boids.js` → `p5_ants.js` — browser-runnable stigmergy sketch
- `skills/create-video-render/SKILL.md` — text card bridge spec: JSON schema, named positions (`top`/`upper`/`mid`/`lower`/`bottom`), per-card `appear`/`fade_in`/`hold`/`fade_out`
- `skills/specs/SKILL.md` — experiment lifecycle (`draft` → `planned` → `partial` → `shipped`); draft status blocks implementation

### Changed
- `create-video-render` skill restructured: top-level `SKILL.md` is engine index; per-engine detail in `flavors/` (Remotion, Manim, Motion Canvas, DynamicalSystems.jl, Bevy headless, GPU fields/swarm, shaders)
- Dockbox ephemeral `find` capped at `maxdepth 4` — prevents ARG_MAX overflow on deep pnpm/yarn workspaces
- Commit skill nudge throttled to once per 10 min and reworded to emphasise coherent-chunk splitting
- Stop hook commit nudge throttled to once per 10 min
- `skills/ts/SKILL.md` — if-guard style: omit braces, indent body on next line (matches project style scan)

### Fixed
- Ant simulation: food sources repositioned to midscreen (y≈0.45); scouts pre-seeded near food so trails form from frame 1, not after random discovery

## [v0.3.3] — 20260526

> kronael v0.3.3 — node_modules binaries run, brands stripped, essay shipped
>
> Permission-denied on `pnpm play` is fixed and the bundle is de-branded.
>
> • Dockbox tmpfs mounts now allow exec — `node_modules/.bin/playwright` and friends actually run
> • Oracle skill uses codex's `--dangerously-bypass-approvals-and-sandbox` (safe inside dockbox)
> • New `content-video` skill writes ≤60s scripts; brand names never appear in drafts
> • Long-form essay `research/skill-libraries-cannot-evolve-themselves.md` consolidates the auto-improvement research
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `research/skill-libraries-cannot-evolve-themselves.md` — single ~3500-word writeup merging the per-topic research notes into one publishable piece (sources, design history, eval-set recipe)
- `skills/content-video/SKILL.md` — short-form video script skill with a brand-agnostic de-branding rule

### Changed
- `skills/oracle/SKILL.md` — recommends `--dangerously-bypass-approvals-and-sandbox` for codex inside dockbox (codex's own sandbox blocks file reads silently and yields empty findings); load-bearing warning marks it host-unsafe
- `dockbox/dockbox` — both tmpfs mounts (`/home/dockbox` and ephemeral overmounts) now use `:rw,exec,mode=1777` so binaries in `node_modules/.bin` can execute (Docker's default `--tmpfs` is `noexec`)

### Removed
- `usage-patterns/` directory — not useful
- All brand-name mentions across tracked docs (`specs/1-ripclaude.md`, removed `usage-patterns/`); content-video's de-branding rule rewritten to itself be brand-agnostic

## [v0.3.2] — 20260526

> kronael v0.3.2 — make, dotnet, sudo, video scripts
>
> Dockbox grows the tools that kept missing; a new content skill lands.
>
> • `make` and `dotnet` baked in — Makefile projects and .NET apps run without setup
> • `dockbox -S` grants passwordless sudo so ad-hoc tools install mid-session
> • New `content-video` skill writes short-form video scripts (≤60s)
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `make` (GNU Make 4.4.1) in the dockbox image via apt
- `dotnet` SDK (LTS) installed under `/opt/dev-tools/dotnet/`; `DOTNET_ROOT` env set; `dotnet` on PATH; `libicu78` apt-installed so `dotnet` doesn't crash on globalization init
- `dockbox -S` flag → passes `DOCKBOX_SUDO=1` to the container; `dockbox-init` writes `/etc/sudoers.d/dockbox-<user>` with `NOPASSWD:ALL` so the runtime user can `sudo apt install X` during a session; a `/etc/shadow` entry is also added so PAM doesn't reject the account
- `skills/content-video/` — short-form video script skill (≤60s; hook + demo + payoff + CTA); follows tweet-skill terseness with bracketed direction lines + spoken lines
- `make clean` at repo root, sweeping `__pycache__/` across subdirs; per-subdir `clean` targets

### Changed
- `research/library-drift.md` cites SkillsBench (arXiv 2602.12670) as its own paper rather than a "companion benchmark"
- Root Makefile + `hooks/Makefile` get `.DEFAULT_GOAL := help` so bare `make` prints help instead of running tests
- Hook test assertions in `pretool_nudge.py` now check the exact expected skill string (was matching only the literal "follow ")

### Fixed
- `dockbox-init`: `set -eu` guard + numeric validation on `DOCKBOX_UID` / `DOCKBOX_GID` (malicious non-numeric values fall back to 1000 instead of corrupting `/etc/passwd`)
- `dockbox-init`: handles unset `DOCKBOX_EPH_PATHS` under `set -u` (was crashing with "parameter not set")
- `dotnet-install.sh` invoked via `bash`, not `sh` (the installer uses bash redirection syntax)

## [v0.3.1] — 20260525

> kronael v0.3.1 — dockbox hardened, hook tests
>
> Dockbox is safer for any host user, hooks have real tests, claude no longer auto-updates inside the sandbox.
>
> • Container start blocks malicious usernames, falls back cleanly when CMD is empty
> • Hooks ship 59 pytest cases; a bug in a hook can no longer block a tool call
> • The agent never tries to self-update inside dockbox
> • New research notes explain the upcoming offline skill-eval loop
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `yq`, `bc` packages in the dockbox image; `gh` via github-cli signed apt repo
- `DISABLE_AUTOUPDATER=1` + `CLAUDE_CODE_DISABLE_AUTOUPDATE=1` env in image — claude-code never self-updates inside dockbox
- `dockbox-init` registers the runtime user in `/etc/passwd`, defaults CMD to `/bin/zsh`, surfaces chown failures
- `make test` at repo root + `hooks/Makefile`; 59 pytest cases for `pretool_nudge.py`
- `research/` directory with 8 topic markdown files documenting the skill auto-improvement design's sources
- `specs/2-hermes-skill-autoimprove.md` rewritten to the bundle eval loop architecture (DSPy MIPROv2 style)

### Changed
- Base image: `node:lts` → `debian:forky`. Node now comes from nvm only, symlinked to `/usr/local/bin` so build-time npm/npx work without sourcing `nvm.sh`
- All dev-tool homes moved to `/opt/dev-tools/{cargo,rustup,nvm,bun,goroot,go,sdkman,uv}/` (world-readable; portable across UIDs)
- `pretool_nudge.py` refactored into orthogonal `skill_for` / `extract_path` / `process` functions; top-level swallow-all wrapper
- `DOCKBOX_USER` is sanitized inside `dockbox-init` (only `[A-Za-z0-9_-]` allowed) — prevents `/etc/passwd` injection

### Fixed
- `dockbox-init`: `gosu` no longer errors when CMD is empty (defaults to `/bin/zsh`)
- `dockbox-init`: chown failures now print warnings to stderr instead of being silent
- `pretool_nudge.py`: hook can no longer block a tool call by raising a Traceback (top-level except in `main`)

## [v0.3.0] — 20260525

> kronael v0.3.0 — one dockbox image for every host user
>
> Until v0.2.8 the image baked a `claude` user with the build-time UID; it only worked for whoever ran `make image`, and a UID mismatch (cross-host pulls, multi-user boxes, sudo invocations) silently broke `pnpm install` and friends with EACCES. v0.3.0 drops the baked user entirely: tools move into `/opt/dev-tools/` (world-readable), the image has no `USER` directive, and `dockbox-init` registers the host invoker in `/etc/passwd` at start, chowns `$HOME` (a tmpfs at `/home/dockbox`) plus every overmount, and `gosu`-drops to the host UID/GID. One image, every host UID, no rebuild.
>
> • Image is UID-agnostic — pushable to a registry, pullable on any host, works for alice/bob/ondra without per-user builds
> • Bind mounts move from `/home/claude/*` to `/home/dockbox/*`; the runtime user gets a real `/etc/passwd` entry so `whoami`, prompts, `ls -l` all show the host username
> • Tools (cargo, nvm, bun, rustup, sdkman, go, uv, pre-commit, ship, nushell, claude-code, codex, pi, agent-browser, pyright) all install to `/opt/dev-tools/`
>
> Rebuild your image (`cd dockbox && make install`) once after upgrading. Existing containers must be removed (`dockbox rm`) — they're frozen on old paths.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed
- `dockbox/Dockerfile` rewritten: no `ARG UID`, no `useradd`, no `USER` directive. Tools install to `/opt/dev-tools/{cargo, rustup, nvm, bun, go, sdkman, uv}/`, `npm-global` stays at `/usr/local/share/npm-global/`. Final `chmod -R a+rwX /opt/dev-tools` makes everything usable by any runtime UID.
- `dockbox-init` (image-baked) now reads `$DOCKBOX_UID`, `$DOCKBOX_GID`, `$DOCKBOX_USER` to register `/etc/passwd` + `/etc/group` entries, top-level-chown `$HOME` and every `$DOCKBOX_EPH_PATHS` entry, then `exec gosu $UID:$GID "$@"`.
- `dockbox` script always passes `--user 0:0` and the UID/GID/USER env vars; always mounts a tmpfs `$HOME` at `/home/dockbox`; bind-mount destinations switched from `/home/claude/*` to `/home/dockbox/*`.
- `dockbox/Makefile` drops the `UID` build arg. Only `TZ` remains.
- `claude` wrapper script moved from `/home/claude/.local/bin/claude` to `/usr/local/bin/claude`; reads `$HOME` instead of hardcoded path.
- System-wide `/etc/zsh/zshrc` replaces the per-user oh-my-zsh setup — fzf bindings + `HISTFILE` only.
- `dockbox/README.md` and `CLAUDE.md` updated to describe the new model.

### Breaking
- Old containers must be removed (`dockbox rm`) before upgrading; their bind-mount paths (`/home/claude/*`) no longer exist in the new image.
- Anything outside the dockbox script that references `/home/claude/...` paths inside the container (`.dockboxrc` extras, custom skills) must move to `/home/dockbox/...`.

## [v0.2.8] — 20260525

> kronael v0.2.8 — dockbox ephemeral overmounts: one chown path for both backends
>
> v0.2.7 had two ownership paths: tmpfs used `uid=` at mount, volume used start-as-root + chown via `dockbox-init` + `gosu` drop. The split made it possible for a stale tmpfs mount or a subtle host/container UID mismatch to leave something un-`claude`-owned and break `pnpm install`. Now both backends share the same flow: container always starts as root, `dockbox-init` chowns every overmount listed in `$DOCKBOX_EPH_PATHS` to `claude:claude`, `gosu` drops, then your command runs. Backend choice is purely the mount type — tmpfs (default, RAM) or anonymous Docker volume (`-T`, disk).
>
> • pnpm/npm/bun installs inside dockbox no longer trip over root- or ondra-owned overmount paths — every path is claude-owned before user code runs
> • Same ownership logic regardless of `-T`, fewer corners to debug
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed
- dockbox always passes `--user 0:0` and `DOCKBOX_EPH_PATHS` to the container when any ephemeral overmounts are active; `dockbox-init` chowns then `gosu`-drops to `claude` regardless of backend
- tmpfs overmounts mount with plain `--tmpfs <path>` (no `uid=`/`gid=`) — ownership is set by the entrypoint chown, not the mount option
- `dockbox/README.md` and `CLAUDE.md` updated to describe the unified ownership flow

## [v0.2.7] — 20260523

> kronael v0.2.7 — dockbox ephemeral mounts: tmpfs by default, volume on `-T`
>
> Builds inside dockbox no longer fight with the host UID. The default backend is now a kernel `tmpfs` per ephemeral dir, mounted with `uid` set so the container's `claude` user owns it from the first byte. Pass `-T` to switch to anonymous Docker volumes — the container then starts as root, a new `dockbox-init` entrypoint chowns each volume to `claude`, and `gosu` drops privilege before your command runs. Either way you stop seeing EACCES.
>
> • Default tmpfs is RAM-backed — fast for `node_modules`/`.next`/`.turbo` (lots of small files), at the cost of RAM
> • `dockbox -T` uses disk-backed Docker volumes when you'd rather not pay RAM for artifacts
> • Image grows by `gosu` + a tiny `/usr/local/bin/dockbox-init` script
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `dockbox -T` — disk-backed anonymous Docker volume backend for ephemeral overmounts (default is tmpfs)
- Dockerfile: `gosu` package and `/usr/local/bin/dockbox-init` entrypoint that chowns paths listed in `DOCKBOX_EPH_PATHS` (when running as root) then drops to `claude`

### Changed
- dockbox ephemeral overmounts default to kernel tmpfs (`--tmpfs <path>:uid=...,gid=...,mode=0755`) — no host footprint, owned by container user at mount, gone with the container
- v0.2.6 host-stash mechanism (`/tmp/dockbox-eph/<name>/`) removed; not needed since both new backends own the mount correctly
- `dockbox/README.md` "Ephemeral builds" section: two-backend model documented, trade-offs spelled out

## [v0.2.6] — 20260522

> kronael v0.2.6 — dockbox ephemeral overmounts actually writable
>
> Default-on ephemeral overmounts in v0.2.4 used anonymous Docker volumes, which are root-owned and broke `pnpm install` (and any other writer) with EACCES inside the container. Now uses a per-container host stash under `/tmp/dockbox-eph/<name>/` bind-mounted in — owned by the host user, matching the container's `claude` UID. The stash is removed by an EXIT trap when dockbox returns. Put `/tmp` on tmpfs for RAM-backed speed.
>
> • dockbox: ephemeral `node_modules`/`.next`/`dist`/`build`/`.turbo`/`.cache` are now writable by the container user (EACCES gone)
> • Stash lives at `/tmp/dockbox-eph/<container>/` on host, cleaned up on exit
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Fixed
- dockbox: anonymous-volume overmounts (v0.2.4) were owned by root, breaking `pnpm install` and similar with EACCES — switched to host-side stash dirs at `/tmp/dockbox-eph/<container>/` bind-mounted in, owned by the host user (UID-matched with container `claude`)

### Changed
- dockbox script no longer `exec`s docker; runs in foreground so an `EXIT` trap can clean up the stash
- `dockbox/README.md` "Ephemeral builds" section updated to describe the new bind-mount mechanism

## [v0.2.5] — 20260522

> kronael v0.2.5 — clippy and rustfmt in dockbox
>
> The image now installs `clippy` and `rustfmt` alongside `rust-analyzer`. Required for any serious Rust work and for the pre-commit hooks most Rust projects use. Rebuild the image to pick this up.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- dockbox: `rustup component add clippy rustfmt` (alongside existing rust-analyzer)

## [v0.2.4] — 20260522

> kronael v0.2.4 — ephemeral builds in dockbox by default
>
> Builds inside dockbox now stay inside dockbox, with zero flags. Rust and Python uv auto-redirect to a container-only cache via `CARGO_TARGET_DIR` and `UV_PROJECT_ENVIRONMENT`. For everything else, dockbox walks the workdir and overmounts every `node_modules`, `.next`, `dist`, `build`, `.turbo`, `.cache` (recursive — monorepo workspaces handled) with anonymous Docker volumes, gone on `--rm`. Opt out per-run with `dockbox -P` or `--no-ephemeral`.
>
> • dockbox: builds never write to your host workdir, no flag required
> • `dockbox -P` — opt-out for when you need host build dirs visible
> • global: ban `gh pr create/merge`, `gh pr review --approve`, `gh release create`, `gh repo create` — same protection as `git push`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- Dockerfile envs: `CARGO_TARGET_DIR=/home/claude/.cache/cargo-target` and `UV_PROJECT_ENVIRONMENT=/home/claude/.cache/uv-venv` — Rust and uv builds now go to container-ephemeral paths
- dockbox: default-on ephemeral overmount for `node_modules .next dist build .turbo .cache` — recursive under workdir, anonymous Docker volumes, gone on `--rm`
- `dockbox -P` / `--no-ephemeral` opt-out flag to bind-mount build dirs from host instead
- `dockbox/README.md` — "Ephemeral builds" section explaining the model + trade-offs + first-run surprise

### Changed
- global skill: ban `gh` push-to-remote (`gh pr create/merge`, `gh pr review --approve`, `gh release create`, `gh repo create`) alongside existing `git push` ban
- `settings-recommended.json` deny rules: same `gh` commands hard-blocked at the harness level, not just by skill text

## [v0.2.3] — 20260521

> kronael v0.2.3 — fresher dockbox, gh-token shortcut
>
> Dockbox image now pulls latest Node/pnpm/bun/rust/nushell on rebuild, and a new `-g` flag forwards your GH token into the container.
>
> • `dockbox -g` — forwards `GH_TOKEN`/`GITHUB_TOKEN` so `gh` works inside the container
> • dockbox rebuild: latest Node stable via nvm, plus bumped git-delta / nvm / zsh-in-docker / nushell pins
> • `tg-fetch users.py` — snapshots Telegram group participants to JSONL
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `dockbox -g` flag forwards `GH_TOKEN` and/or `GITHUB_TOKEN` from host env
- `tg-fetch/users.py` — group participants snapshot to JSONL

### Changed
- dockbox: `nvm install node` (latest stable, was pinned `22`)
- dockbox pinned-tool bumps: git-delta 0.18.2 → 0.19.2, nvm 0.40.1 → 0.40.4, zsh-in-docker 1.2.0 → 1.2.1, nushell 0.110.0 → 0.112.2
- dockbox auto-latest tools (pnpm, bun, rustup, go, gopls, uv, claude-code, codex, pi-coding-agent, agent-browser, pyright, typescript, ship, playwright, puppeteer) now rebuild against current upstream

## [v0.2.2] — 20260520

> kronael v0.2.2 — merge origin/master skill quality pass + browse rename
>
> • Merged v0.2.1 skill quality pass (21 skills refined against 10 external repos)
> • browse skill (renamed agent-browser) — no more Agent subagent type confusion
> • ops: container hardening rules (USER non-root, HEALTHCHECK, dumb-init)
> • oracle + explore skills from origin

### Added
- oracle skill: codex CLI second-opinion
- explore skill: read-only codebase exploration mode
- ops: container hardening (USER non-root, HEALTHCHECK, `--init`/dumb-init)

### Changed
- `agent-browser` skill renamed to `browse` — CLI is still `agent-browser`, skill name is not
- All changes from v0.2.1 skill quality pass (see below)

## [v0.2.1] — 20260513

### Changed
- Skill quality pass: 21 skills refined against 10 top-tier external repos (anthropics/skills, obra/superpowers, wshobson, voltagent, hesreallyhim, qdhenry, 0xfurai, alirezarezvani, lst97). Every change filtered through 2+ source corroboration + codex (oracle) critique + wisdom-skill terseness pass.
- meta (wisdom, global, learn, specs, sub): description=triggers; offload heavy content to references/; completion claims need evidence; verify subagent results; transcript reading + N≥2 rule for skill extraction; specs anti-pattern list + self-review checklist; sub never bare prompt.
- workflow (ship, refine, fin, recall-memories, distill, testing): refine triage substep; recall-memories freshness check; testing verify-failure-for-right-reason; distill trigger-form description; fin grind-harder framing.
- language (ts, sh, py, rs, tsx): ts satisfies/branded/discriminated/exhaustive/unknown/import-type; sh strict mode + mktemp+trap + NUL-safe iter; py Protocol over ABC; rs MIRI for unsafe + adapter DTOs.
- domain (service, data, ops, browse, oracle, cli, create-eval, diary): service correlation-IDs + stable error shape; data idempotent upsert + schema versioning + validate before persist; ops SLO+burn-rate alerts + runbook URL; browse wait-before-snapshot + locator priority + error screenshot; oracle targeted context + verify before adopting; create-eval programmatic assertions.
- visual: broadened triggers (components, landing pages, dashboards).
- improve: NOT-for-explain in description; expanded triggers.
- explore: `allowed-tools` frontmatter for mechanical read-only enforcement.

## [v0.2.0] — 20260512

> kronael v0.2.0 — plugin-first install, flat layout, sharper skills
>
> Install by cloning to /tmp and saying "install" — Claude reads CLAUDE.md and runs the procedure.
>
> • Plugin renamed kronael-tools → kronael — shorter install command
> • Flat layout: skills/, agents/, hooks/ at repo root (no more assistants/ nesting)
> • "Say install" elevated as primary path — git clone + cd + claude + "install"
> • skills/global/ no longer copied as a skill — body goes only to ~/.claude/CLAUDE.md
> • browse skill replaces agent-browser — clearer name, no Agent subagent confusion
> • All 35 skills carry USE/NOT descriptions for unambiguous dispatch

### Added

- `when_to_use` frontmatter field across skills — routing triggers separate from `description`
- oracle skill: codex CLI second-opinion, dual auth (host `~/.codex` mount or API key env)
- explore skill: read-only mode toggle (`/explore`), no code modifications
- `browse` skill (renamed from `agent-browser`) — browser automation via CLI, never as subagent type
- `COOKBOOK.md` — detached-HEAD workflow recipes with rig
- `skills/README.md` — skill families rationale
- `ARCHITECTURE.md` § Why hybrid — evolvability and LLM-coordinated merge rationale
- Full Codex install runbook in `AGENTS.md`
- `ops` skill: uvx single-file scripts, Python+uv Makefile/Dockerfile patterns, container hardening

### Changed

- Plugin renamed `kronael-tools` → `kronael`; trigger phrases: "install kronael" + "install kronael tools"
- Flat repo layout: bundle at root instead of `assistants/`
- `skills/global/` skipped during install copy — body goes only to `~/.claude/CLAUDE.md`
- README: `git clone /tmp/kronael + claude + "install"` as primary install path
- All 35 skill descriptions rewritten in USE/NOT format
- `release` skill: monorepo version files, distill blockquote broadcast format, first-release handling
- `INSTALL.md` dropped — `kronael/install/SKILL.md` is the single source of truth
- `description` trimmed to noun-phrase + NOT clause only — routing triggers moved to `when_to_use`
- dockbox: base image `node:lts`, `pnpm@latest`; NVM + Node 22 pre-installed; `~/.codex` mount
- settings: dropped sandbox block (per-env, not toolkit's call)

### Fixed

- `agent-browser` no longer spawnable as `Agent(subagent_type=...)` — renamed to `browse` + description clarified
- `ops` skill: dropped duplicate Makefile blocks; resolved lint/uvx contradictions

## [v0.1.2] — earlier

## [v0.1.1] — earlier

## [v0.1.0] — earlier
