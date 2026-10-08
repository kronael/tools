# Changelog

## [Unreleased]

- `hooks/gh_text_lint.py`: `lint(kind, text, title, draft)` returns `Problem(line, text)` records; `command_reason(command, cwd)` finds the body a gh command posts (`--body-file`, `$(cat <path>)`, a heredoc, `--input` JSON, the inline `--body`) and returns the block reason, or the reason the body cannot be read. CLI: `python3 ~/.claude/hooks/gh_text_lint.py pr tmp/pr-body.md --draft tmp/pr-draft.md --title '<title>'`; `issue` and `comment` kinds take a file alone.
- `hooks/pretool_nudge.py` calls `command_reason` after the unsafe-command check, and `gh release create` joins that check's block list; `hooks/Makefile` runs `test_gh_text_lint.py`; `hooks/README.md` and `hooks/ARCHITECTURE.md` describe the gate.
- `skills/pr-draft/SKILL.md`: steps 3 to 5 are DISTILL into `tmp/pr-body.md` with the lint's `ok:` line as the completion criterion, REVIEW-ON-WISDOM closed by a `Review changed:` line, then the fenced draft; the PATCH of an existing PR reads `tmp/pr-body.md` by a literal path. `skills/gh-comment/SKILL.md` and `skills/gh-issue/SKILL.md` run the lint before their sign-off gates and carry NOT-for clauses.
- `settings-recommended.json` and `kronael/sync/SKILL.md` step 5: `attribution.pr` `"🤖"` and `attribution.sessionUrl` `false` join the always-apply keys.
- `hooks/skill_frontmatter_lint.py`: reachability resolves the `.md` path tokens a document contains, then names a file by its path from the skill root or by a trailing part of that path no other file under the skill shares — so a bare basename counts only while it is unique. `names_doc` is gone; one resolution path replaces the per-candidate regex.
- The `<!-- lint: allow skill-local-path -->` marker counts only on a line of its own. `skills/CLAUDE.md` quotes it in prose and was exempting itself; a planted home path in it now fails. A fenced block holding the marker alone on a line still disarms — nothing parses fences.
- `LOCAL_PATH` exempts the container accounts `dockbox` and `claude` as whole segments only. An account that merely starts with one of those names belongs to somebody and now reports.
- `skill_files()` maps a sibling `.md` to the `SKILL.md` that owns it, `.pre-commit-config.yaml` matches every `.md`, and the Lint workflow runs on push to master as well as on a pull request — it had never run, since this repo pushes straight to master.
- `evals/README.md` teaches path-stripping with a placeholder account instead of a real former one, and needs no marker. `skills/create/CLAUDE.md` states where a ported tree's `README.md` is named from.
- `BUGS.md`: `SKILL-LINT-GATE-SKIPS-SIBLING-EDITS`, `SKILL-LINT-BASENAME-HIDES-ORPHANS` and `SKILL-LINT-LEAK-SCAN-MISSES-THE-TREE` are built and removed. Recorded in their place: `SKILL-LINT-WRITE-LANDS-OUTSIDE-THE-COMMIT`, `SKILL-LINT-PRE-COMMIT-SCANS-HIDDEN-DIRS`, `LINT-CI-DISPATCH-EMPTY-REFS`, `PRE-COMMIT-ALL-FILES-RED`, and `SKILL-LINT-NO-ORG-REF-CHECK` under Ruled not a defect.
- `py`: `## Async` runs short local file I/O inline (`# noqa: ASYNC230`/`ASYNC240` with a reason) and long blocking work through the project's one shared `to_thread` helper, writes a thread's output through `.part` + `os.replace`, runs work that must stop on cancel as a subprocess, and has a retry helper `iter()` a plain backoff sequence.
- `py`, `software/strict-typing.md`: one project-wide pyright `typeCheckingMode: "strict"`, never a `basic` default with a per-file `strict` list; a test file opts down with `# pyright: basic`.
- `refine/py.md`: the Python refine lens, read only through refine step 4 — shared helpers over local copies, threads and subprocesses that end before their caller, data over lambdas at call sites, less source, one strict pyright mode.
- `py`: `## Subprocesses` starts a child with `create_subprocess_exec(..., start_new_session=True)`, never stdlib `subprocess` from async code, and runs it inside the project's one async context manager that waits and reaps on exit and sends SIGTERM, then SIGKILL, to the group on an exception or a cancel.
- `py`: dataclasses for heterogeneous records, work items and hashable keys; batches from data-fetch functions, iterators when the caller drives consumption; tests patch a symbol at its use site instead of adding a production parameter; `## Naming` keeps only the `now()`/`today()` and `iter_<items>` additions to `software/code.md` § Naming.

## [v0.4.24] — 20261008

> kronael v0.4.24 — Markdown reflow joins the tool hooks
>
> The rumdl pass is a branch of the existing tool hooks, with no hook, settings entry or Codex target of its own.
>
> • One hook less — post_tool_nudge.sh hands a .md write to pretool_nudge.py, which runs rumdl.
> • Quieter — silent when rumdl ran; one line when it is missing, fails or times out.
> • Narrower — only a Write or Edit of a .md in a repository whose root holds `.rumdl.toml`.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `pretool_nudge.py` § `format_markdown`, fed by `post_tool_nudge.sh` on a PostToolUse payload that names a `.md`: a `Write`/`Edit`/`MultiEdit` is reflowed by the repository's `node_modules/.bin/rumdl`, else `rumdl` on PATH, run as `rumdl fmt` from the repository root (the nearest `.git`) when that root holds `.rumdl.toml`, so the config's `exclude` applies. Silent when rumdl ran — Claude Code reports a file a hook changed, and an Edit over a reflowed line fails instead of applying to stale text; one line when rumdl is missing, exits non-zero or times out, and a timed-out run gets the written bytes back. A repository without the config, a file outside any repository and a clone nested in an opted-in tree are never touched.
- `hooks/md_format.py`, its `Write|Edit|MultiEdit` settings entry and its Codex `md_format` target are removed; the uvx fallback, `rumdl.toml` and `pyproject.toml` detection, leftover parsing and the re-read note go with them.
- `software/code.md` § Layout and formatting: `exclude` patterns are written `.name/`; a root-anchored `/.*/` does not match a file named on the command line (rumdl 0.2.78).

## [v0.4.23] — 20261008

> kronael v0.4.23 — Markdown wraps itself, Haiku leaves the workflows
>
> Agents stop hand-wrapping Markdown: a hook runs rumdl on each .md they write in an opted-in repo, and Haiku is batch-only.
>
> • md_format hook — each .md an agent writes is rewrapped; tables, fences and links stay.
> • Opt in per repo — `.rumdl.toml` and a pinned rumdl; `make fmt` wraps, `make lint` checks.
> • Agents — no haiku skill, agent or keyword; light work runs on sonnet or in the main thread.
> • readme — topology.md defines the repo layout: one question per file, one numbers ledger.
> • bugs, release — an owed decision carries options and a default; a CHANGELOG only if published.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `hooks/md_format.py` (PostToolUse on `Write|Edit|MultiEdit`; Codex `apply_patch`, every file it names): runs `rumdl fmt` on the written `.md` from its own directory when a directory up to the repository root holds `.rumdl.toml`, `rumdl.toml` or `[tool.rumdl]`; the binary is the repo's `node_modules/.bin/rumdl`, else PATH, else `uvx rumdl@0.2.78`. It tells Claude to re-read a file it changed and reports what rumdl could not fix or a failed run. Never blocks; a repo with no config is never touched.
- `software/code.md` § Layout and formatting owns the rule — the config (`line-length = 100`, `reflow`, tables and fenced blocks exempt), the pin, `make fmt` and `make lint`; `readme/topology.md` lists the lint gate.
- rumdl was chosen over dprint, prettier and mdformat on a real doc set: those three pad table columns and refill every paragraph; rumdl reflows only lines over the width and leaves tables, fences, frontmatter, HTML and links as they are.
- `solana/layout.md` agrees with `rs`: unit tests live in `src/<module>_test.rs`, declared beside their subject with `#[path]`.
- `global` § Agents: Haiku is batch-only, never a sub; read-only fan-out and mechanical edits go to `sonnet` or stay in the main thread. `skills/haiku`, `agents/haiku.md` and the `haiku` nudge keyword are removed and `kronael/sync` retires the installed copies; `sonnet`, `opus`, `dispatch`, `skills/CLAUDE.md`, both READMEs and `scavenge/shapes.md` drop the tier. The `dockbox`/`qemubox` `haiku` aliases stay pending BUGS.md `BOX-HAIKU-ALIAS-VS-BATCH-ONLY`.
- `readme/topology.md`: the house layout in one file — which file answers which question (README, PLAN, ARCHITECTURE, FEATURES, BUGS, the study page, `test/research/verified.md`, root and package CLAUDE.md), the README order, the numbers ledger, what `make lint` checks, what is tracked and what stays local. `agents/readme.md`, `finalize-crate`, `diary`, `wisdom`, `refine/brief.md`, `readme/shape.md`, the doc-naming hook and `global` § Documentation point to it.
- `bugs`: an owed decision has status `needs sign-off` or `owner decision` and carries `**Options:**` and `**Default if nothing is decided:**`; a gate is one more clause (`blocks go-live`, `blocks publication`). `next` § Later sends an owed decision to `bugs`.
- `release`: CHANGELOG.md is created only when the project publishes versions to outside consumers; otherwise step 3.5 writes the release text from `git log <last>..HEAD`.
- `sonnet`: `when_to_use` takes mapping and grep-and-report work and drops the find/replace and find-bugs phrases that race `astgrep` and `review`.

## [v0.4.22] — 20261007

> kronael v0.4.22 — code rules you can scan, and lints that check them
>
> The code rules are now short ALWAYS/NEVER bullets, every code edit points at them, and a lint flags misnamed predicates.
>
> • code.md — rules as ALWAYS/NEVER bullets, most-broken first; the code-file nudge names it.
> • Lints — Rust, Python and TypeScript flag a bool function without an is_/has_/can_/should_ prefix.
> • Docs rules — status line first, stated cost, code from tested files, a guide-and-reference site.
> • Codex reads the project's .claude/CLAUDE.md as well.
> • Rule pruning — a clean room with no setup at all, and a rule is cut only on observed behaviour.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `software/code.md`: every rule an ALWAYS/NEVER bullet, sections ordered by how often sessions break them; it owns naming, comments (machine-read markers such as `// #region` and lint pragmas are not comments), shutdown on SIGINT/SIGTERM and build cadence. `rs`, `py`, `go` and the other language skills keep only their additions and ALWAYS read `code.md` first; the pretool nudge names it for code skills.
- Lints `rs-bool-fn-prefix`, `py-bool-fn-prefix`, `ts-bool-fn-prefix` (warnings): test code, trait and interface implementations, overrides, getters and dunders are exempt, each proven by a fixture. `lints/check.py` fails when ast-grep fails and requires the rule to fire in every block of a bad fixture. `refine/software.md` runs them and hunts what they cannot see.
- `readme` and `writing`: README order (what, link row, status, why, how), one status line worded the same everywhere, cost as a formula with a worked figure, doc code from compiled regions, an example-page shape ending in what has been tested, a guide-and-reference site layout, the README as a hub, one name per page, explicit anchors. A reader-question heading is allowed in a doc set with navigation when its first sentence answers it.
- `global`: rules `code.md` or the harness carry are dropped; "NEVER kill a process you did not start, not even to free a port".
- `wisdom`: one clean room, `clean-room.sh` (empty home and config, no tools, no skills, pinned model), which proves isolation from the run's own transcript; `subtraction.md` runs the whole-bundle pass; a rule is cut only on behavioural evidence, never on a model's self-report.
- `codex/AGENTS.md`: Codex reads the project's `.claude/CLAUDE.md`; its fallback file names never load that path.
- Project names and a local path are gone from skill text; `should_` counts as a predicate prefix.

## [v0.4.21] — 20261007

> kronael v0.4.21 — the skill lint catches dead files and leaked paths
>
> The skill lint now fails a commit that leaves a skill file unreachable or ships an absolute home path.
>
> • `make skills-frontmatter` — errors on an unreachable skill file, a leaked home path, or a token.
> • Four files nothing could reach are named, including `port-to-go/java.md` at 1016 cold lines.
> • Tests — no expectation computed by the code under test; run an artifact instead of grepping it.
> • ship — a Gate carries its expected result; repairs stop when each fix moves the defect elsewhere.
> • BUGS.md — three proposals for the holes the new lint still has.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `hooks/skill_frontmatter_lint.py`: two error-level checks. `skill-orphan` walks the chain of names out of `SKILL.md` and reports every `.md` under the skill that no chain reaches, exempting `CLAUDE.md` at any depth; `skill-local-path` and `skill-secret` report an absolute home path or a credential shape. An illustrative path takes a one-character account segment (`/home/u/app/x`) — `skills/CLAUDE.md` states the convention.
- `port-to-go/java.md`, `refine/ts.md`, `refine/tsx.md` and `create/web/design-md/templates/starter.md` were unreachable; each owning `SKILL.md` now names it.
- `software/testing.md` § What an assertion proves: never derive the expected value from the code under test, and assert an artifact's output rather than its source text.
- `ship/runtime.md`: when each repair reveals a defect elsewhere the architecture is wrong — stop whatever the attempt count and route the redesign through Stage 3 sign-off. `ship/prompt.md`: the plan's `Gate` field and the worker brief both carry the expected result.
- `review/take.md` § 2: name which findings are still unclear after re-verification and wait, since a partial reading misfixes the items you did understand.
- `NOTICE`: credits obra/superpowers © 2025 Jesse Vincent (MIT) for the three adapted sections.
- `BUGS.md`: `SKILL-LINT-GATE-SKIPS-SIBLING-EDITS` (pre-commit and CI lint nothing on a sibling-only commit), `SKILL-LINT-BASENAME-HIDES-ORPHANS` (a duplicate basename satisfies the check; three `README.md` files still ship unreached), `SKILL-LINT-LEAK-SCAN-MISSES-THE-TREE` (the scan reads only `*.md` beside a `SKILL.md`) — all `proposed`, none built. Plus the earlier proposal to move `ship` into this repo as a step runner.

## [v0.4.20] — 20261006

> kronael v0.4.20 — the ship program runs on fable
>
> The ship skill keeps planning specs on fable; when you choose the ship program, it launches on fable because its tasks run unread.
>
> • ship CLI — launch with MODEL=fable TIMEOUT_SCALE=3; no diff is read before the next task.
> • ship -k — the validator is read-only and writes only ship's own state under .ship/.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `ship/cli.md`: a fable sub writes and re-verifies the specs; the ship program launches with `MODEL=fable TIMEOUT_SCALE=3`, since its worker takes the next task at once and WISDOM puts unread code generation on fable (the scale covers fable's ~215 s validator against the fixed 180 s).
- `ship/cli.md`: `ship -k` runs a validator restricted to `Read`, `Glob` and `Grep`; it cannot touch the repo and writes only `.ship/` state and logs.

## [v0.4.19] — 20261006

> kronael v0.4.19 — org skills install as plugins
>
> Org-specific skills now install as Claude Code plugins, so they load in dockbox and qemubox, where a symlinked skill dangles.
>
> • Org overlays — add the org marketplace from its git source, then install its plugin.
> • Boxes mount `~/.claude/plugins`, so a plugin's skills load in every box started after the install.
> • sync — settings merge never drops an `enabledPlugins` entry you added.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `ARCHITECTURE.md` § Org overlays: install an org skill set as a Claude Code plugin from a marketplace added by git source; a local-path marketplace loads in place from the checkout, so boxes miss it. Limits: a qemubox under `-U` mounts no plugins, and a dockbox created before the install keeps its creation-time `settings.json`. Codex installs the plugin separately.
- `kronael/sync`: step 5 adds the recommended `enabledPlugins` entries and never drops one; the keep-list section points at § Org overlays.
- dockbox README and `--help` list the `~/.claude/plugins` mount; `CLAUDE.md` and `ARCHITECTURE.md` route org overlays to plugins and private skills to the keep-list.

## [v0.4.18] — 20261006

> kronael v0.4.18 — fewer skills, qemubox logs in
>
> The bundle drops from 88 to 69 skills, and Claude Code in a qemubox VM starts logged in with the host's account.
>
> • eval — one router holds the CEO, CTO, red, design, novice, hiring and all-lenses evaluations.
> • Skill agents now load their skill, and nine small skills fold into their neighbours.
> • qemubox — session variables and agent tokens reach the VM over ssh stdin, never a command line.
> • sync — symlinked skills stay without a keep-list line, and edited retired skills are asked about.
> • Boxes — each box gets its own `.venv` and gcc, and dockbox points the agent at GitHub over HTTPS.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `eval` router replaces `ceo-eval`, `cto-eval`, `red-eval`, `design-eval`, `13yo-eval`, `hiring-eval` and `eval-all`; `assess` folds its four extra roles in; `create-eval` is removed. Nudge words route to `/eval`.
- Folded: `speed-demo` → `demo/speed.md`, `credits` → `software/credits.md`, `markdown-converter` + `media-ingest` → `ingest`, `sol` → `astra` § Sol, `finalize-crate` → `release/library.md`, `go-gl` → `go/gl.md`, `trader` → `data/trader.md`, `later` → `next` § Later. Dropped: `caveman` (the output style and command carry it), `explore`, `agent-browser` (`browse`). Every retired name is in the sync's `RETIRED` list.
- `visual`, `readme`, `improve`, `refine`, `learn`, `distill` agents only load the same-named skill, and the skills launch them; `skills/CLAUDE.md` § Agent definitions owns the rule. The five `commands/` files their skills shadowed are removed. The prompt nudge routes to `/skill`, and a test proves every route names a bundled skill.
- `writing` is a router whose `page.md` owns how a document or page reads and looks; `humanize` keeps its workflow and moves the catalogue to `patterns.md`.
- `global` § Git: squashing unpushed commits through `/squash` is allowed; a pushed commit is never squashed. `commit` reads the repo's commit-msg gate first.
- qemubox: `CLAUDE_CODE_OAUTH_TOKEN`, `OPENAI_API_KEY` and `CODEX_API_KEY` join the session env when set. Every env value (`-e`, `-g`, the tokens) goes over ssh stdin into a per-session 0600 file in the guest's `/dev/shm`, which the session sources and deletes. `-U` drops the tokens, even from a project `.qemuboxrc`.
- Boxes: a per-box `.venv` and gcc for sdists. The sandbox notes name the empty dependency dirs only when the box overmounts them, and the dockbox note gives the HTTPS form for GitHub (needs `-g`). The qemubox base build reuses dockbox's TZ argument and cache.
- sync: a symlink directly under a bundle dir is kept without a line, and a deeper one is asked about. The keep-list file is `~/.claude/.keep`, and a leftover `kronael-keep.txt` stops the sync. A live-edited file under a retired name is asked about.

## [v0.4.17] — 20261005

> kronael v0.4.17 — ship records live with plan mode's plans
>
> Ship plans and critiques now live in the project's `.claude/plans/`, where Claude Code's plan mode writes; Codex reads the same rule.
>
> • ship — `.claude/plans/plan-NN-name.md` holds the record; its first writer pins the setting.
> • Critiques (assess, eval-all, ceo/cto-eval, useless) sit beside the plans as `critique-*.md`.
> • Layout rule — `plans/` exists only as `.claude/plans/`; the doc-naming hook says the same.
> • Codex — its global Kronael instructions name the directory, the ignore line and the reuse rule.
> • release — an annotated tag carrying this broadcast is the release; never a GitHub release object.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `ship` § Work record: the record is `.claude/plans/plan-NN-name.md` in the main tree, addressed by absolute path from worktrees; the first writer adds `"plansDirectory": ".claude/plans"` to `.claude/settings.json` and the root-anchored `/.claude/plans/` line unless `git check-ignore -v` names an in-tree `.gitignore`, committed together. A project-local `plansDirectory` is outside the retention sweep, which walks `~/.claude/plans` alone. Spec: specs/06-ship-record.md.
- `assess`, `eval-all`, `ceo-eval`, `cto-eval`, `specs/useless.md`, `create-eval`, `sonnet`, `readme`, `ship/cli.md`: every record path names `.claude/plans/`; the CEO and CTO memos are flat `critique-<lens>-<YYYYMMDD>.md` files.
- `global` § Documentation, `readme/topology.md`, `hooks/prompt_nudge.py`: `.claude/plans/` is the only `plans/`; `todos/` stays banned.
- `codex/AGENTS.md`: a Work record section — the path, the ignore line, reuse the active change's record where it is.
- `release`, `global` § Git: the annotated tag (`git tag -a -F`) is the release; `gh release create` is never run. `software/docker.md`: `.dockerignore` excludes `.claude`.

## [v0.4.16] — 20261005

> kronael v0.4.16 — prepare and land a refactor stack
>
> The merge and software skills now cover bringing a pushed stack up to date and landing it on GitHub with evidence on the exact head that merges.
>
> • merge § 0c — update a pushed branch by merging its base forward, never a rebase; prove the merged tree is the tested one.
> • refactor-stack — keeping the stack mergeable, evidence before the merge, landing stacked PRs through merge-async with a pinned sha, and long runs.
> • continue — recover the survivors of a long run before starting a new one.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `merge` § 0c: fetch, detach at `origin/<b>`, merge `origin/<base>`, then gates on HEAD or an empty diff against the tested commit; a squash-merged base is merged in, `-s ours` only when the trees prove it.
- `software/refactor-stack.md`: sections Long runs, Keeping the stack mergeable, Evidence before the merge and Landing on GitHub (`.stack` probe, merge-async with `sha`, 422 on a member's base PATCH, missing merge ref behind zero runs).
- `continue`: survivors of an earlier run are found and reconciled before a relaunch.

## [v0.4.15] — 20261004

> kronael v0.4.15 — opus subagents run at high effort
>
> The opus subagent now runs at high effort like sonnet; only fable keeps xhigh, so opus design calls cost less per step.
>
> • /opus runs Opus 5.5 at high effort; the opus, sonnet and dispatch skills state the new pin.
> • /fable is the only xhigh tier — unattended code, ship plans and deep audits still go there.
> • /oracle says its opus fallback runs at high, not xhigh.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `opus` agent pins effort `high`; `skills/CLAUDE.md`, `opus`, `sonnet` and `dispatch` quote the pin, and `fable` is the only xhigh tier.
- `oracle`: the fable route's opus fallback is stated at high.

## [v0.4.14] — 20261004

> kronael v0.4.14 — the tweet skill leans on the shared voice
>
> The tweet skill defers wording to the writing and humanize rules and adds the platform facts a post needs on X.
>
> • tweet — hook, thread arc and source checks stay; voice defers to writing, caveman Language, humanize
> • tweet — plain text only since X renders markdown literally, weighted 280-char counts, no Premium fold
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `tweet`: rewritten to lean on the shared language stack instead of restating generic copy advice; keeps the hook, thread arc, claim-verification and caveat-placement discipline; adds a Platform section — plain text only, X weighted counts, no Premium long-post reliance, bare `🤖` attribution — and a DISTILL / humanize / REVIEW-ON-WISDOM close mirroring `pr-draft`.

## [v0.4.13] — 20261003

> kronael v0.4.13 — simpler sentences with clear meaning
>
> Caveman uses familiar words and simple sentence structure while preserving technical meaning, uncertainty, and conditions.
>
> • Sentences use active voice, one main clause, and clear references.
> • Rewrites keep meaningful uncertainty and every condition that controls an action.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Caveman specifies familiar words, direct sentence structure, and clear noun and pronoun references. It limits nested clauses and asides while retaining complete grammar.
- Rewrites preserve needed technical terms, meaningful uncertainty, and the scope of conditions when splitting sentences.

## [v0.4.12] — 20261002

> kronael v0.4.12 — clearer explanations and host context
>
> Explanations can use interactive pages or narrated videos, while writing rules preserve facts and sandbox notes identify where agents run.
>
> • create explains source evidence through diagrams, interactive HTML, or narrated video.
> • writing uses plain, complete sentences; humanize preserves facts and uncertainty.
> • server-init records host facts; the first sync offers it as an optional step.
> • dockbox and qemubox describe their mounts, network, and file persistence.
> • spec-lint checks spec status, index rows, filenames, and code references.
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Explainers select the requested format, verify claims and interactions, and keep draft review local unless publication is requested. Video narration uses verified local TTS by default; paid narration requires authorization. Silent captions follow scenes.
- Shared language rules apply to technical prose and documentation. The chat length and structure limits apply only to chat. Humanize preserves supplied facts and uncertainty.
- `server-init` creates or refreshes a per-host memory. The first sync offers it as an optional step; sandbox sessions cannot create host memory.
- `dockbox` and `qemubox` write sandbox notes and set `CLAUDE_SANDBOX`. Notes identify mounts, network access, and file persistence, including when edits to shared Claude configuration reach the host.
- `spec-lint` checks the closed status vocabulary, filenames, index rows, and code references. Root detection distinguishes skill guides from spec corpora and supports explicit spec directories. Pre-commit and `make test` run the relevant checks.

## [v0.4.11] — 20261002

> kronael v0.4.11 — recall-memories recovers more context
>
> recall-memories now ships a helper that digests earlier sessions and finds a prior tool or agent result to reuse.
>
> • recall.py — sessions, results, prompts, digest, show over Claude Code and Codex transcripts
> • digest — compaction summaries, recaps, each prompt with its final reply, agents, edited files
> • results, show — find an earlier tool or agent result and read it in full, not re-run
> • make test — runs the recall.py tests
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `recall-memories` digests prior sessions (compaction summaries, recaps,
  each prompt with its final reply, agents, edited files) and finds an
  earlier tool or agent result with its full output, so it is reused
  instead of re-run. The new `recall.py` helper reads Claude Code
  transcripts, subagent transcripts, spilled tool outputs and Codex
  rollouts; `make test` runs its tests.

## [v0.4.10] — 20261002

> kronael v0.4.10 — astra and sol second opinions, cd anywhere
>
> The codex second-opinion skill is now astra, sol adds a second Codex model, and sync makes `cd <project>` work from any directory.
>
> • /astra — the codex CLI pinned to gpt-6-astra, on every route codex had
> • /sol — the same adversarial second opinion from gpt-5.6-sol
> • sync — writes a CDPATH block into ~/.bashrc, so `cd <project>` finds ~/app, ~/wk and ~/sandbox
> • clp — removed; CDPATH covers it
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- **Breaking:** the `codex` skill is `astra`: the codex CLI pinned to
  `gpt-6-astra`, on every route codex had (oracle, release and ship
  critique, scavenge checkpoints). `/codex` no longer resolves; a sync moves
  an installed `skills/codex` aside. The model is a fixed slug checked in the
  Codex catalog (`$CODEX_HOME`, default `~/.codex`); a missing slug stops the
  call and asks, never substitutes.
- `sol`: the same second opinion on `gpt-5.6-sol`, run ephemeral so it never
  reads Astra's thread. Oracle routes to it only on an explicit request.
- Prompt routing: a prompt that starts with `/astra` or `/sol` goes to that
  skill; `ask codex`, `ask astra`, `oracle` and `second opinion` go to
  `/astra`.
- **Breaking:** `clp` is removed. A sync writes
  `CDPATH=:$HOME/app:$HOME/wk:$HOME/sandbox` into `~/.bashrc` in a marked
  block, so `cd <project>` works from anywhere. The empty first entry keeps a
  local `cd` silent; a marker without its pair stops the write.

## [v0.4.9] — 20261001

> kronael v0.4.9 — plan on Opus, build on Sonnet, sync clean
>
> Bigger work runs as a reviewed plan built on Sonnet, and sync rebuilds ~/.claude so stale files cannot pile up.
>
> • /sonnet — plan, brief, review, recover and close for multi-file work, with a ~200-line size gate
> • /kronael:sync — merges your ~/.claude edits into your clone first, then rebuilds ~/.claude from it
> • /refine — reviews a change by context and settles every claim it makes before a release
> • /research — one router for backtest method, report layout and silent-number traps
> • dockbox — fails a box that dies at startup; a project .dockboxrc honours --no-ephemeral
> • rig — sq and riq removed; they never found a fixup commit
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- **Breaking:** `/kronael:install` and `@kronael-install` are `/kronael:sync`
  and `@kronael-sync`. A sync merges files edited in `~/.claude` into your
  clone three-way, then swaps in a bundle built from source plus
  `~/.claude/kronael-keep.txt`; the old bundle moves to a `/tmp` run dir.
  Installed-only skills survive only when the keep-list names them; names the
  bundle dropped move aside without a question. A failed build, a bad keep-list
  entry or a symlink in the bundle stops the sync with `~/.claude` unchanged, and
  a failure during the swap restores every path already exchanged.
- **Breaking:** `rig sq`, `rig fixup` and `riq` are removed; `rig install` and
  `make clean` delete any alias missing from rig's list.
- `sonnet` owns "Plan, then execute": a change under ~200 lines stays in the
  main thread; bigger work plans top-down (end state, design, steps), researches
  the code through a sub that gets questions only, runs each step on Sonnet
  against a recorded snapshot SHA, and discards a step whose design is wrong.
  `opus`, `fable`, `haiku`, `dispatch` and `oracle` state the model and effort
  their agent files pin; `improve` runs on Sonnet 5.5 at high.
- `refine` cuts a change into contexts, briefs one read-only sub per context and
  re-derives every finding, launching each review by agent type; release step
  1.5 and `oracle` fall back to opus or fable when codex cannot run.
- `research` (method, layout, traps) absorbs `research-analysis`; its QLIKE rule
  follows Patton 2011.
- The wisdom file sits at its 200-line cap, with the repo doc layout in
  `readme/topology.md`. New rules: an unverified negative is not a finding, and
  a mechanism that swallows errors gets replaced, not instrumented.
- dockbox: a box that exits or never becomes ready fails the launch with its
  last log lines; a project `.dockboxrc` honours `--no-ephemeral`, an empty one
  leaves command-line flags alone, an unknown `--flag` in either rc is an
  error, and the help lists the flags a project rc ignores.
- hooks and diary: the diary resolves from the repo toplevel on the UTC date,
  and its main tree in submodules and separate-git-dir repos; the Stop hook
  stays silent in ship's judging roles; `make -C hooks test` runs through
  `uvx --with pyyaml`.
- qemubox: `build-base` finds `mke2fs` in `/usr/sbin`, the README states the
  `mke2fs -d` tarball requirement, and the build tests run without host tools.
- tw-fetch surfaces driver errors instead of archiving the wrong tab.
- About 100 comment lines that restated the code are gone.

## [v0.4.8] — 20261001

> kronael v0.4.8 — ship runs a change end to end
>
> /ship asks once what to hammer, then plans, builds, refines and delivers a change without stopping for routine approval.
>
> • /ship — one opening question batch, including what to hammer, then plan, build, refine and deliver
> • dockbox — bridge boxes follow the host's resolver, so DNS keeps working after a Wi-Fi change
> • dockbox, qemubox — each box keeps its own Claude session registry, so boxes cannot message each other
> • Install — sessions refuse messages from your other sessions and ask before one leaves the machine
> • /readme — a doc-page mode for HTML explainer pages, with a fact pass before any style pass
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `ship` asks the answers the result depends on in one opening batch, what to
  hammer included, and states open preferences as defaults. A fresh planner
  writes one work record in the main tree's `.ship/`. Each step passes its
  own gate, and `refine` and the chosen hammer checks run before acceptance.
  Redesigns still need sign-off, and push and release keep their gates.
- `dockbox` passes `--dns <bridge gateway>` when a resolver listens there
  (for example systemd-resolved with `DNSStubListenerExtra=172.17.0.1`), and
  prints a note when the host uses a loopback stub without one. An
  unreachable Docker daemon stops the launch with docker's own error.
- `dockbox` and `qemubox` mount a private tmpfs over `~/.claude/sessions`.
  A box keeps the mounts it was created with until `dockbox rm`.
- Install always applies `crossSessionInbound: "refuse"` and
  `isolatePeerMachines: true`. Subagent reports still arrive.
- `readme` gains `page.md` for HTML explainers. `writing` and `humanize` add
  rules for links on the claim's words, colon headings, semicolon chains and
  symbols standing in for words. `refine` routes project docs to a `readme`
  lens that checks facts first.
- `BUGS.md` records the shared Claude runtime state, NAT flows on a carrier
  blip, the docker socket crossing boxes, two qemubox output defects and two
  refine cleanup proposals.

## [v0.4.7] — 20261001

> kronael v0.4.7 — qemubox becomes a daily sandbox
>
> qemubox now boots the same image as dockbox and keeps each VM's disk, so you can reuse a VM every day.
>
> • qemubox — boots the dockbox image as your own user and stops idle VMs after 4 h, keeping the disk
> • qemubox — shares ~/.claude and ~/.codex, puts build dirs on tmpfs, reads dockbox-style rc files
> • dockbox — boxes allow io_uring, and sessions get nice, mlock and ptrace
> • Git skills and rig — every checkout detaches, so no local branch appears; gco joins rco
> • Install — turns off the Bash edit diff and the IDE diff viewer
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `qemubox build-base` exports the Dockerfile's new `vm` stage into a qcow2
  base named by image id; VMs boot it directly as the host user (same name,
  uid, gid, home): 16 GiB RAM, 4 vCPUs, 40G sparse disk.
- qemubox disks persist: the last session powers the VM off. One lock covers
  setup, session markers, stop and remove; a dead session does not keep a VM
  busy. `ls` shows RAM/DISK/USE; `prune` stops VMs idle past 4 h, removes
  stopped ones past `[hours]` and deletes unused bases; `rm` takes patterns.
- qemubox matches dockbox: rc files, worktree mount, tool table, tmpfs build
  dirs (`-P`/`-T`), PAM limits, the host time zone, a `docker` CLI for `-D`.
  The guest cannot edit the project rc or the plugins.
- qemubox security: a disk made by a trusted launch refuses `-U`, because it
  holds `~/.claude.json`. Missing `-G`/`-v` sources fail loud. `-D`/`-K`
  forwards bind again after a relaunch.
- `dockbox` boxes run Docker's default seccomp profile plus io_uring (the moby
  profile ships with its Apache-2.0 notice); sessions enter through setpriv
  with SYS_NICE, IPC_LOCK and SYS_PTRACE ambient. Another user's box is refused
  with a pointer to `-n`. Both tools resume sessions for project paths with
  any non-alphanumeric character.
- Git rules: detached HEAD only, never a local branch; reads go through
  `git fetch origin` and `origin/<default head>`; pushes go by SHA. Review
  fixes push to the open PR's head; fixed threads resolve silently.
- `rig`: `gco` is `rco` without the fetch, plus `--` file restore, and new
  diff/stash/rebase aliases; `rco` takes refs and hashes.
- Install pins `bashEditDiffEnabled: false` and the `diffTool` `terminal`.

## [v0.4.6] — 20260929

> kronael v0.4.6 — dockbox ls sees every box
>
> `dockbox ls` now reports a real tmpfs number for boxes whose worktrees were deleted, and the wisdom file points at `/solve`.
>
> • dockbox ls — skips build dirs the host deleted, so those boxes show their RAM instead of `?`
> • Wisdom — routes through `/solve`, the new name of `/resolve`
> • /fin — sends resumes to `/continue`, the new name of `con`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `dockbox ls` passes `df` only the overmount paths that still exist in the
  box; a host-deleted worktree detaches its mounts, and `df` exiting on the
  missing path made the whole row `?`. `dockbox/test.sh` runs the real probe
  against a fake box, under dash when installed (the box's `/bin/sh`).
- `skills/global/SKILL.md` names `/solve` (renamed from `/resolve`, which
  install prunes); `fin` names `continue` (renamed from `con`).
- `BUGS.md` drops the `doc-shape` entry; `doc-topology` is folded into
  `readme`.

## [v0.4.5] — 20260929

> kronael v0.4.5 — saying release now means a full refine first
>
> A bare `release` runs the most thorough refine over every unreleased change before it bumps anything, and Sonnet moves to 5.5.
>
> • /release — refines every change since the last tag first: all lenses, fable on correctness, a codex second opinion
> • /release — a late change reruns the refine, so nothing ships unreviewed
> • Models — Sonnet is claude-sonnet-5-5 in the sonnet agent, dockbox, qemubox and the Emacs setup
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `release` step 1.5 runs `/refine` over `git diff <last>..HEAD` (the whole
  tree on a first release) at full depth whatever the diff size — every lens,
  extra passes past refine's 3-lens cap, `correctness` on `fable`, and a
  `codex` second opinion fed through refine's triage and apply. Any later
  change other than the refine's own commits and the release commit reruns
  it. Step 2 also bumps version strings in `README.md`/`CLAUDE.md`; `refine`
  names the `/release` exceptions to its scale-to-the-diff and model rules.
- Sonnet pins move to `claude-sonnet-5-5` (`agents/sonnet.md`, `dockbox`,
  `qemubox`); the Emacs gptel snippet registers it so gptel does not fall back
  to a model it knows.
- `dockbox/test.sh` pins prune's 4-hour idle grace on both sides.

## [v0.4.4] — 20260929

> kronael v0.4.4 — dockbox prune cleans up idle boxes
>
> `dockbox prune` now removes boxes nobody uses anymore, and a session that fails no longer leaves its box running.
>
> • dockbox ls — USE column shows busy or idle, so you see which boxes are safe to remove
> • dockbox prune — removes idle boxes 4+ hours old and never touches a busy one
> • dockbox — a session that errors out or loses its terminal still removes its box
> • dockbox rm — takes several names and deletes the box's volumes too
> • release — version parts never carry: after 0.3.99 comes 0.3.100
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `dockbox` sessions tear down from an EXIT trap (HUP and TERM too), so a
  non-zero exit or a closed terminal leaves no stale marker; the teardown keeps
  the box when the marker dir cannot be listed.
- `dockbox ls` adds USE (`busy`/`idle` from `docker top`, `-` stopped, `?`
  probe failed). `dockbox prune [hours]` also removes idle boxes created 4+
  hours ago, parses Docker's `CreatedAt` under GNU date, and exits non-zero
  when a removal fails.
- `dockbox rm` takes several names or globs, matches `dockbox-`-prefixed names
  literally, rejects unknown options, and exits non-zero on no match or
  failure. Every teardown passes `-v`, so `-T` volumes go with the box.
- `release`: MAJOR, MINOR and PATCH never carry — `0.3.99` → `0.3.100`.
- Docs: dockbox `--help` and README match the code (`-T`, default model,
  overmount lifetime); `hooks/ARCHITECTURE.md` names `stop.py`'s own event
  reader; `BUGS.md` logs the dockbox lifecycle races and that duplicate reader.

## [v0.4.3] — 20260929

> kronael v0.4.3 — see which dockbox holds your RAM
>
> `dockbox ls` now shows how much tmpfs and disk each box holds, so you know which one to remove.
>
> • dockbox ls — TMPFS column: RAM-backed files in each running box, every mount counted once
> • dockbox ls — DISK column: the box's writable layer, volumes not included
> • hooks — the test suite passes on a fresh checkout, with no bundle installed
> • commands — /improve, /learn, /readme, /refine and /visual ship with the bundle
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `dockbox ls` adds TMPFS (`/tmp`, `/tmp/cargo-target`, `/dev/shm`, `$HOME`
  and the build-dir overmounts of a running box, each mount once; `-` when
  stopped, `?` when the probe fails) and DISK (writable layer, volumes
  excluded). `dockbox/test.sh` runs `ls` against a stub docker.
- hooks: `local`, `memory_nudge`, `prompt_nudge` and `reclaude` import
  `lib.state` from their own directory, the codex rewrite tests build their own
  skills dir, and CI installs PyYAML, so `Test — hooks` runs without an install.
- `commands/` ships the `improve`, `learn`, `readme`, `refine` and `visual`
  wrappers.
- Docs: the dockbox README explains the `ls` columns and what `-T` covers; the
  hooks docs say the diary nudge repeats on every Stop. `BUGS.md` logs the stale
  installed hook docs and the dockbox `--help` drift.

## [v0.4.2] — 20260927

> kronael v0.4.2 — two lines become one
>
> The upstream and local development lines are reconciled into a single master, and the three sync sides are named.
>
> • merge — upstream's line (its v0.3.98) merged with the local ripwire/codex/wisdom work; the Stop recap stays gone (Claude Code ships its own)
> • install — the sync docs now name source, live (~/.claude), and upstream (origin) explicitly
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Reconciled `upstream/master` (its `v0.3.98`) with the local release line: kept the local subtracted wisdom shape and the removed Stop recap, took upstream's readme/specs router restructure, unioned the bug queue and skill rules.
- `install` / `CLAUDE.md` / `ARCHITECTURE.md`: name the three sync sides — source (this repo), live (`~/.claude`), upstream (`origin`) — so a live sync is never confused with an upstream push.

## [v0.4.1] — 20260927

> kronael v0.4.1 — codex knows when it's logged out
>
> A revoked codex token now reads as unavailable, and you get the one command that fixes it.
>
> • codex — a revoked token counts as unavailable despite `login status`; hands you `! codex login`, never retries
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `codex`: a revoked refresh token now reads as unavailable — `codex login status` exits 0 and prints "Logged in" without exercising the credential, so `token_revoked`/401 in the real call is the signal; hand the user the interactive `! codex login`, never retry.

## [v0.4.0] — 20260925

> kronael v0.4.0 — one recap, not two
>
> Claude Code already generates a recap of its own, so the Stop hook stops writing a second one and goes back to the commit and diary nudges.
>
> • hooks — the Stop turn recap is removed; the built-in recap is left at its default
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Removed

- `stop.py`'s turn recap, and with it the per-session stamp, the
  `RECAP_BUDGET` deadline, the `RECAP_COMMITS`/`RECAP_PATHS` caps and the
  landed/dirty/stuck builders. Claude Code generates its own recap from the
  conversation — the away summary, keyed `awaySummaryEnabled` and shown as
  *recap* in `/config`, with `/recap` as the on-demand form — so a second one
  meant two summaries at every stop, and the git one spoke even on a quiet turn
  (`since 07:48Z: no commits`). The hook is back to the commit and diary nudges.
  `awaySummaryEnabled` is deliberately left unset, at Claude Code's default.

## [v0.3.99] — 20260925

> kronael v0.3.99 — Codex gets the turn recap, and the installer can copy again
>
> The Stop recap now runs in Codex sessions too, and the rsync the install protocol prescribes is no longer refused by the toolkit's own deny rule.
>
> • hooks — the turn recap is no longer withheld under Codex
> • settings — `rsync` moves from deny to ask, so the narrow `~/.claude` allow can take effect
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Fixed

- `stop.py` withheld the recap whenever `KRONAEL_IN_CODEX` was set, so a Codex
  session got the commit and diary nudges but never the turn summary. The bridge
  already routed `stop`'s `systemMessage` through the nudge rewrite, so the
  exclusion was the only thing in the way.
- `codex_hook.py` returned the raw hook stdout for a Stop carrying a
  `systemMessage`, skipping both the `ok` strip and the `/skill` → `@skill`
  rewrite every other nudge gets.
- `settings-recommended.json` denied `Bash(rsync *)` while allowing
  `Bash(rsync * ~/.claude/*)`. Deny wins, so the install protocol's own copy step
  was refused and had to fall back to `cp`. The blanket rule is now `ask`, the
  narrow allow stands, and a dry-run to `~/.claude` runs without a prompt.

## [v0.3.98] — 20260926

> kronael v0.3.98 — two lines, one bundle, Bun for new TypeScript
>
> The local hooks-and-lints line and upstream through v0.3.97 are one bundle again, and a new TypeScript project starts on Bun with Biome.
>
> • TypeScript — a new project runs on Bun with Biome and tsc; an existing one keeps its tooling
> • Sync — the merge skill defines it: fetch, size, preview, merge origin/master into the detached HEAD
> • Hooks — Stop recaps the turn, blocks on an unreadable tree, nudges the diary once per session
> • Prompt nudge — the first prompt of a session gets a /solve nudge on the channel the model reads
> • Wisdom — push only when asked, dated review branches, commit by default, in a 128-line routed file
> • Tools — tw-fetch reads a post keyless, tg-fetch takes groups as arguments, gloww fits the terminal
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- `ts` skill § Tooling: a new TypeScript project runs on Bun (runtime, package manager, test runner) with Biome (lint, format) and `tsc --noEmit`; `prepare`/`check`/`right`/`test` map to `bun install`/`biome check`/`tsc --noEmit`/`bun test`; an existing project keeps its tooling until asked. `software/strict-typing.md` carries the `biome.json` floor (verified against Biome 2.5.14) and a Biome column in the escape-hatch table; `tsx` scaffolds with `create-next-app --biome`; `astgrep`, `refine/ts.md` and the `software` router follow.
- `merge` skill § Sync: fetch origin, size and preview the merge, merge `origin/master` into the detached HEAD with zdiff3, trace deletions against both parents, verify, commit. Distinct from the install's file sync and from `sync-tools-skills`.
- `tw-fetch/mirror.py` reads X posts by id or url through `api.fxtwitter.com`, no key; `tw-fetch/README.md` states what the mirror cannot do.
- `gloww` reads markdown with glow at the terminal's real width.
- Co-located ast-grep lint packs (ts, rust, python) with a fixture harness and `make lints`; `learn` extracts lint rules from sessions.
- `caveman` skill wraps the output style; the style budgets rendered lines by question shape and takes ASD-STE100 as the language floor.
- `emacs` skill, `software/js-perf.md`, `software/lsp.md`, `create` collage mode, `demo/composed.md` and `demo/cutout.md`, `rs/cranelift.md`.
- SKILL.md lint: a missing key, an unknown key, a name that is not the directory, and SHOULD hard-fail; NOT-for, length, listing budget and router hygiene warn.
- The pretool guard also blocks squash merges, interactive rebases, branch creation, `worktree add` without `--detach`, `killall` and Co-Authored-By trailers.

### Changed

- Carries upstream v0.3.94–v0.3.97: push, PR and release commands ask instead of being denied, `readme` router with `shape.md`, `pr-draft` shape, the `attribution.commit` setting, `bugs` entries pinned by a failing test. The local v0.3.94 became this release after the tag collision.
- `skills/global/SKILL.md` (the wisdom file) routes instead of restating — 128 lines: routing, conduct, map, the NEVER list; each rule lives in the skill that owns it. It carries upstream's policy: push only when the user asks in that message, never to `master` without a second approval, dated `YYYYMMDD_<tag>` review branches, commit finished work by default, write in the idiom around it.
- `resolve` is `solve` and user-invocable; every reference follows.
- `bugs` skill: two sections (open defects, ruled not a defect), grouped by subject, fixed entries leave the file; it owns the Bug Triage Protocol. `BUGS.md` follows that shape.
- `tg-fetch`: groups are positional arguments, each resumed from its own `.jl`; credentials come from `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE` or `TELEGRAM_BOT_TOKEN`; the TOML config and its template are gone.
- dockbox: `codex` target runs `gpt-5.6-sol` at xhigh beside upstream's `claude-opus-5-5`, `claude-fable-5-1` and `gpt-6-astra` pins; the `opus` agent names Opus 5.5.
- `refine` (upstream's runbook with PR-thread intake) keeps the cross-boundary lens and the code.md sign-off pointer; `review give` keeps the opus fallback for the fable pass.

### Fixed

- `hooks/stop.py`: a failed `git status` blocks with its stderr instead of reading as clean; the diary nudge fires once per session (session-keyed stamp in `~/.claude/state`) and never writes a header; a timed-out git call no longer kills the hook; when nothing blocks, a compact turn recap is shown.
- `hooks/prompt_nudge.py`: output goes through `hookSpecificOutput.additionalContext`, the only UserPromptSubmit field the model reads; the Codex guard reads the payload `harness`, not a dead env var.
- `hooks/local.py`, `hooks/reclaude.py`: read the `hook_event_name` Claude Code sends, so LOCAL.md and RECLAUDE.md re-inject on PreCompact again; `hook_event()` lives once in `hooks/lib/state.py`.
- `git push` is not blocked by the pretool guard (upstream's call); the stale test case moved to the non-blocking set.
- Four orphan hooks withdrawn again and named in the install prune list, so a resync cannot vendor them back.
- gloww: an explicit glow style skips the terminal query that ate pager keystrokes; `-wN` parses as a width flag.
- `software` frontmatter fits the 1,536-char listing cap (1,274), so its last keywords route again.

## [v0.3.97] — 20260925

> kronael v0.3.97 — bugs come with a failing test
>
> Every recorded bug now cites a skipped test that fails on today's code, and commits stop getting a Co-Authored-By trailer.
>
> • `/bugs` — each defect ships a skipped test that asserts the right behaviour and fails today
> • `/bugs` — docs, ops, config and design-style entries say `no test`; a fix un-skips its test
> • Settings — `attribution.commit` is empty, so Claude Code stops asking for the trailer
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `bugs` pins each entry with a test that asserts the correct behaviour, is
  run and seen failing, and is skipped with the entry id in its reason;
  `docs`, `ops`, `config`, `design`, `duplication`, `traceability` and
  infra-bound `perf` entries state `no test — <type>`. A fix un-skips it.
- `settings-recommended.json` sets `attribution.commit` to `""` and install
  applies it on every run, so Claude Code stops requesting a `Co-Authored-By`
  trailer. `commit` and its evals drop the prose rule the setting replaces;
  README and ARCHITECTURE name every key install applies without asking.

## [v0.3.96] — 20260925

> kronael v0.3.96 — one Co-Authored-By rule, where commits are written
>
> The no-trailer rule now sits once in `/commit`, right where the message is written, instead of in seven places.
>
> • `/commit` — skip the Co-Authored-By trailer even when the harness reminder asks for it
> • Wisdom file, `/ship`, `/squash` and the commit nudges — their copies are gone
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `commit` states the Co-Authored-By rule once, in Format, and names the
  harness attribution reminder it overrides. The wisdom file, `ship`,
  `squash`, and the `stop.py` / `prompt_nudge.py` / `local.py` commit rules
  drop their copies.

## [v0.3.95] — 20260925

> kronael v0.3.95 — PR descriptions that read like a map
>
> `/pr-draft` now opens with the shape of the change and keeps each concern to one short paragraph.
>
> • Lead sentence — names every part touched and the file to start from
> • One paragraph per concern — lists folded into the sentence, no header or bullet walls
> • `Also:` line — every behaviour change gets named, even one-liners
> • Size budget — a bump stays a few sentences; big PRs cap near 3,000 chars
> • Titles — follow the repo's convention, ticket prefix kept
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed

- `pr-draft` reads the full diff, opens on a lead naming each layer and its
  entry file, gives each concern a bold-led paragraph, sweeps minor changes
  into `Also:`, points at the weakest spot instead of claiming safety, and
  closes on contract / known-deferred / ⚠️ merge-order lines. Bodies scale to
  ~400 / 1,500 / 3,000 chars; file tables, effort estimates, diagrams, test
  plans and session URLs are out. Titles follow the repo's own convention.

## [v0.3.94] — 20260924

> kronael v0.3.94 — push and PRs ask instead of failing
>
> Push, PR and release commands now prompt you instead of being denied, and Codex now loads the Kronael guidance block.
>
> • Settings — push, PR and release commands ask first; recursive `rm` stays denied
> • Codex — its global guidance file carries the Kronael block, which points at your wisdom file
> • `/readme` — one router for docs sync, doc file layout and single-page section order
> • Hooks — nudges point at skills that exist, and Codex gets them rewritten
> • TypeScript — annotate types only where inference cannot reach them
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed

- `settings-recommended.json` moves `git push`/`pull`, `ssh`, `rsync`,
  `gh pr create`/`merge`/`review --approve`, `gh release create` and
  `gh repo create` from `deny` to `ask`. An ask rule prompts in every mode,
  bypass included. Recursive `rm`, `chmod 777` and `SendFeedback` stay denied.
- Codex global guidance: install writes the `codex/AGENTS.md` block into a real
  `~/.codex/AGENTS.md`, replacing a symlink to the wisdom file; any other
  symlink is a conflict. dockbox's Codex bridge does the same.
- `readme` is a router: bare `/readme` syncs docs; `topology.md` (the former
  `doc-topology` skill) and `shape.md` load on demand. Reinstalls prune
  `doc-topology`.
- `ts`: annotate types only for recursion, overloads, widening and
  `isolatedDeclarations` exports.
- `plugins/kronael/.codex-plugin/plugin.json` tracks the release version.

### Fixed

- Hook nudges sent prompts to pruned skills (`/testing`, `/eye-13yo`,
  `/hacker-eval`). The Codex rewrite list named `credit`, missed `browse`,
  `continue` and `resolve`, and skipped names starting with a digit.
- Docs match the code: push is not among the hook's blocks, the go sink example
  keeps comments out of its body, the social research doc states where the
  SKILL departs from it, and the repo maps, sync table and AGENTS.md settings
  merge match the installer.

### Operator note

An existing `~/.claude/settings.json` keeps its `deny` entries for push and PR
commands until you reinstall; install step 4 removes a `deny` entry the source
moved to `ask`.

## [v0.3.93] — 20260923

> kronael v0.3.93 — boxes run Opus 5.5
>
> dockbox and qemubox now launch Claude on Opus 5.5 by default, and reviewers judge code without the author's reasoning.
>
> • dockbox / qemubox — default and `opus` alias pinned to `claude-opus-5-5` at xhigh
> • Review — every reviewer is a fresh agent, never a fork of the author's session
> • doc-topology — which-file questions kept apart from section order inside one page
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- dockbox and qemubox pin `claude-opus-5-5` for the default tool and the
  `opus` alias; the `opus` agent description names Opus 5.5.
- `review` give mode hands each reviewer the change goal in one neutral
  sentence, the target and the house rules — never a fork carrying the
  author's reasoning.
- `doc-topology` separates which file answers a question from section order
  within one integration or API-reference page.

## [v0.3.92] — 20260921

> kronael v0.3.92 — run one command in a box you already have
>
> dockbox and qemubox gained `exec`, which hands your whole command to the box instead of splitting it into dirs and args.
>
> • `dockbox exec make test` — the box is keyed off the current dir, and starts if none is up
> • Paths survive — `dockbox exec ls /` keeps the `/` that a bare tool name loses to the dir split
> • `qemubox exec make test` — the same, over SSH, in the project's VM
> • Shells — `bash` / `zsh` / `sh` are login shells in dockbox now, matching qemubox; `sh` is an alias for bash
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- `dockbox exec <cmd>` and `qemubox exec <cmd>` run a command in the box,
  passing every later argument through untouched. They reuse the existing
  resolve-then-enter path, so the box is keyed off the current directory like
  every other invocation and provisions when none is running.

### Changed

- `dockbox bash`, `zsh` and `sh` start login shells, so the guest profile
  applies; `sh` is an alias for bash. `qemubox` already did this.

### Fixed

- dockbox resolved `bash`/`zsh` in two places — the pre-getopts dispatch and
  the tool case — which drift as soon as one changes. getopts passes a bare
  `bash` through untouched, so the tool case alone covers it.

## [v0.3.91] — 20260920

> kronael v0.3.91 — the go skill stops overflowing its budget
>
> The goroutine rules stay, but they stop costing every session.
>
> • Go — `concurrency.md` sibling holds goroutine sizing and the single-sink I/O pattern; `SKILL.md` drops 212 → 126 lines with an ALWAYS-read dispatch line
> • Routing — `when_to_use` gains goroutine keywords, so `/resolve` reaches the concurrency rules at all

## [v0.3.90] — 20260920

> kronael v0.3.90 — the goroutine rules come home
>
> A section that only ever lived in one machine's `~/.claude` is now in the repo, where the next install cannot overwrite it.
>
> • Go — fixed goroutine sets sized at startup: one owner per subsystem, one reader per connection, a worker pool with a configured width; never a goroutine per event, request, write or queued item
> • Reverse-sync — captured through a three-way merge against the v0.3.65 base, so the repo's stronger comment-placement wording supersedes the older deployed phrasing

## [v0.3.89] — 20260918

> kronael v0.3.89 — the comment rules stop contradicting each other
>
> The comment ban and the four skills that mandate comments now agree, and five more skills can reach the policy at all.
>
> • Comments — `code.md` names its three exceptions: a test's scenario intro, `// SAFETY:` on `unsafe`, the why on a suppression
> • Reach — `cli`, `data`, `htmx`, `service` and `trader` route to the code baseline, and every pointer names comments
> • Python — no docstring on a private function, method or class; the public-API exception is the whole allowance
> • PR threads — `gh-comment` fetches, replies to and resolves them; `review take` and `refine` point at it instead of restating the calls
> • `BUGS.md` — open defects and what was ruled not one, grouped by component, with the audit narrative in `.diary/`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- `gh-comment` owns the GraphQL `reviewThreads` calls — fetch a thread's id,
  resolution state and author, reply to it, resolve it. REST carries the body
  but neither the id nor whether the thread is already closed.
- `py` bans a docstring on a private function, method or class.
- `cli`, `data`, `htmx`, `service` and `trader` carry the
  `Requires software/code.md` pointer; every such pointer now names comments.

### Changed

- `code.md`'s comment ban names the three exceptions owned by `testing.md`,
  `rs` and `go`, so loading it alone no longer deletes comments the bundle
  requires. Each owner stays inside what it owns: `ts` defers its test-block
  content to `testing.md`, `rs` keeps `// SAFETY:` to `unsafe`, and `go`'s
  placement rule is shown on a suppression rather than a private field.
- The `improve` agent removes every comment `code.md` bans, not only the ones
  that restate the obvious, and carries the pointer needed to load that rule.
- `review take` references `gh-comment` § Setup for the auth fallback instead
  of repeating the command.
- `BUGS.md` holds two sections — defects still true of the code, and what was
  ruled not a defect — grouped by component, with no dated status blocks.
- `review take` sources its worklist from every open thread, human and bot,
  and treats `isResolved` or a bot's "Addressed in" banner as a claim to
  re-verify at HEAD.
- `pr-draft` keeps the reasoning behind a non-obvious decision when cutting to
  essence; narration and restatement still go.
- `improve` ranks a banned comment left standing as Important, matching the
  baseline that calls it a defect.
- The wisdom file bans overriding `CARGO_TARGET_DIR`, `TMPDIR` or any other
  configured build or temp path.

### Fixed

- `make test-<dir>` ran nothing: the pattern targets were listed in `.PHONY`,
  which stops `%` from matching.
- dockbox wrote the Codex bridge symlinks absolute, so they dangled on the
  host once the container's home differed.
- `hooks/Makefile` names the real constraint — a `test_*.py` missing from
  `TEST_FILES` never runs and the suite still passes.
- The skill map listed `testing`, which is on the install prune list; its
  content lives in the `software` router.

## [v0.3.88] — 20260915

> kronael v0.3.88 — the docs say what the code does
>
> Three documents claimed things the code does not do; `tw-fetch` gained the README it shipped without.
>
> • Stop hook — nudges for a diary in any git repo, with or without a `.diary/` directory
> • `software` router — its what-lives-where table lists `testing.md`, which the dispatch table already reached
> • `tw-fetch` — a README covering the cookie login, the three commands, and what a dumped tweet holds
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- `tw-fetch/README.md` — the cookie login flow, the `timeline`/`user`/`login`
  commands, output paths and record fields, and the Chrome requirement.

### Fixed

- `hooks/ARCHITECTURE.md` claimed the stop hook gates its diary check on a
  `.diary/` directory existing; it nudges in any git repo.
- `skills/software/CLAUDE.md`'s what-lives-where table had no row for
  `testing.md`.

## [v0.3.87] — 20260915

> kronael v0.3.87 — you have to ask before it pushes
>
> Pushing and PR-creating now need you to say so in that message, and comments are gone from code unless a caller reads them.
>
> • Push — only on a direct instruction, and `master`/`main` needs a second approval naming the branch
> • Comments — banned outside doc comments on exported items; touching a file means sweeping the ones already in it
> • Refine — reads a PR's unresolved threads, fixes what is real, replies and resolves, and every step closes on an observable criterion
> • New skills — `squash`, `solana`, `create/social`, `refactor-stack`, plus per-language refine lenses
> • dockbox — `-n` keys the directory basename, so a renamed box is still found by `ls`, `rm` and prune
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- Skills: `squash`, `solana` (+ its onchain/layout/deps/review data files), the
  `create/social` mode with its render script, `software/money.md`,
  `software/refactor-stack.md`, `ts/node-cluster.md`, `ts/v8-deopt.md`, and
  `refine/{ts,tsx}.md` — the language lenses `refine` step 3 reads.
- `show-me` skill ported from humanlayer/skills: smallest useful visual for the
  current conversation topic.
- `prompt_nudge` nudges `/resolve` once per session, behind a `.claude/tmp`
  marker; `/resolve` itself is now a slash command.
- The stop hook emits a turn recap — commits landed, what is still uncommitted,
  and any merge/rebase/cherry-pick left in progress.
- `wisdom`: `<important if>` guidance for project `CLAUDE.md`, the runbook body
  pattern, skills-as-first-class rules and the `/learn` pairing.

### Changed

- `git push`, `gh pr create/merge` and `gh release create` run only on a direct
  instruction in that message; `master`/`main` needs a second approval that
  names the branch, given after the exact refspec is shown.
- Comments are banned outside a doc comment on an exported item, and touching a
  file means reading every comment already in it and deleting the banned ones.
- Code and prose are written in the idiom of what surrounds them — mirror the
  neighbours rather than adding scaffolding they do not use.
- Committing finished, verified, user-directed work is part of doing the work —
  no separate "should I commit?" question.
- `refine` runs as a runbook: each step closes on an observable criterion, the
  correctness lenses are seeded from the defaults models confess to, and PR
  review threads are triaged, fixed, replied to and resolved.
- `review give`/`take` and `gh-comment` distill each finding to at most two
  lines before posting; a filed issue and a patched PR body open with a robot
  marker so a reader knows Claude wrote it.
- `merge` covers rebasing onto a squash-merged main by tree boundary; `next`
  parks items via `TodoWrite` instead of a file.
- Rust unit tests are declared at the top of the source file, with the imports.
- dockbox and qemubox pin `claude-fable-5-1`, `gpt-6-astra`, and default to
  `claude-opus-5`.

### Fixed

- `dockbox -n` keys the directory basename instead of replacing the whole
  container name, which hid a renamed box from `ls`, `rm` and prune.
- The install step pins `diffSidebarOpen` off in `~/.claude.json`, where the key
  actually lives — `settings-recommended.json` cannot carry it.
- The stop hook reports a missing or stale diary instead of appending an empty
  `## HH:MM` header.
- The pretool hook routes `SKILL.md`/`CLAUDE.md`/`AGENTS.md` edits to `/wisdom`.
- The sandbox drift guard extracts each script's own default model and compares
  them, instead of grepping one hardcoded model literal.
- `software/money.md`, `ts/node-cluster.md` and `ts/v8-deopt.md` are reachable
  from their owners' dispatch tables, so they actually load.
- Published skill content carries no pointers to notes or services a reader
  cannot reach.

## [v0.3.86] — 20260913

> kronael v0.3.86 — what you asked for is what ships
>
> Skills stop quietly swapping a requested result for a convenient one, and stop refusing art work on copyright grounds.
>
> • `demo` gains a versus-scoreboard intro — meme, original and placeholder art are distinct deliverables, locked from the brief
> • Copyright is a sourcing and NOTICE check now, not a blanket reason to refuse a feasible asset
> • `fin` keeps a scope ledger — rereads every message since the goal, so a deferred item can't be reported as done
> • `credits` describes copyleft neutrally — read the actual LICENSE; never call a license "contamination"
> • `speed-demo` routes meme openers to `demo` and moves ~120 lines of failure detail into `lessons.md`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed

- `skills/demo/SKILL.md` documents the versus-scoreboard intro: a Pillow
  compositor plus ffmpeg concat, four art slots replaceable by filename, and
  an asset-class lock taken from the brief before composing.
- Refusing feasible asset work on copyright grounds is replaced by a
  provenance/NOTICE check. Substituted art keeps the item open until the user
  accepts it.
- `skills/fin/SKILL.md` gains **Scope ledger** — completion is semantic, and
  "everything is done" is barred while any item is deferred or blocked.
- `skills/credits/SKILL.md` gains **License compatibility** — compatibility
  depends on the exact licenses and linkage, so surface the narrow uncertainty
  rather than a blanket prohibition.
- `skills/speed-demo/SKILL.md` drops ~120 lines of failure narration for a
  pointer to `lessons.md` and routes recognizable-meme openers to `demo`.

## [v0.3.85] — 20260912

> kronael v0.3.85 — a rule you can recite is not a rule you follow
>
> The wisdom sweep is reverted — the rules it cut as already-known are ones the models confess to breaking.
>
> • Wisdom rules restored — fail-loud, no-duplication and fix-causes stay in every session
> • `wisdom` asks the behaviour question per rule now — a long cut list means it was skipped
> • Run a probe you expect to fail first; a broken check and a passing one look the same when green
> • `refine` rewritten as a runbook — 9 steps, each closing on an observable pass/fail
> • Its correctness lenses seed from what models admit they do, not a frozen checklist
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Operator note — the minimization criterion was wrong

"The model reproduces this rule unprompted" does not mean the rule is
redundant. Asked about their own defaults, both models named logging-and-
swallowing, degrading where crashing is correct, inventing a second logging
path without grepping for the first, over-mocking, and commenting above
almost every block — each while able to recite the rule against it.

Cuts made on that criterion are reverted in `skills/global/SKILL.md` and
`skills/software/code.md`. Two unrelated fixes from the same sweep stay: the
`./tmp` removal and the false `requires:` claim.

### Changed

- `skills/refine/SKILL.md` follows the runbook pattern — every step closes on
  an observable criterion (`git status --porcelain` empty, test target exits 0,
  no file in two buckets, `git worktree list` shows only the main tree).
- Refine's correctness lenses seed from a **Confessed defaults** section —
  the error, test and comment habits models report as their own first pass.
- `skills/wisdom/SKILL.md` gains the method the sweep cost to learn: ask the
  behaviour question per candidate rule, re-examine every earlier cut when the
  criterion changes, and run a probe you expect to fail before trusting one
  that passes. Expect a nearly empty cut list.
- `CLAUDE.md` test and hooks notes match the repo: PROJECTS is five projects
  and `make test` also runs `tests/drift_test.sh`; `make gen-ci` is listed.
  The hooks note explains the real trap — `hooks/Makefile` names its test
  files explicitly, so a new `test_*.py` is skipped in silence.

### Fixed

- The no-duplication rule is back in the wisdom file. Both models report
  reaching for the mainstream idiom over a repo-local helper they never
  grepped for, which is the rule's whole subject.

## [v0.3.84] — 20260912

> kronael v0.3.84 — skills that conform, bridges that are proven
>
> Skill frontmatter now matches what Claude Code actually reads, and the check runs in `make skills-frontmatter` instead of living in someone's memory.
>
> • Only recognised frontmatter keys — `arg` was silently doing nothing, and four provenance keys travel badly
> • `name` must equal its directory, and `description` + `when_to_use` must stay inside the 1,536-char listing budget
> • Both checks enforced by the linter; a repaired file is re-checked rather than passed
> • pi runs again — its shebang picked a Node too old for its own regex
> • `CLAUDE.md` mandates conformance and bridge verification, with the command for each
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Operator note — frontmatter conformance is now enforced

`make skills-frontmatter` fails on an unrecognised key, a `name` that differs
from its directory, or a `description` + `when_to_use` over 1,536 characters.
All three previously failed silently at runtime: an unknown key is ignored, an
over-budget listing is truncated mid-keyword, and a wrong name simply disagrees
with the command. Run it before any commit touching `skills/`.

### Added

- `CLAUDE.md` gains a Conformance section: skills must use only the frontmatter keys Claude Code reads, keep `name` equal to the directory, stay inside the listing budget, and be reachable from `SKILL.md` — directly or through a file it already names. Both bridges must be proven by running them, and a symlink existing is explicitly not the same claim as the tool working.

### Changed

- `skills/software` trigger list cut from 1,520 characters to 1,068. It sat 16 short of the listing cap, where any edit would have truncated its later modes out of the always-on listing without an error.
- `skills/wisdom/clean-room.sh` reduced from 50 lines to 18. Cleanup needed a `find` pipeline only because recursive removal is banned, so the room is left in `/tmp` and the trap that failed good runs is gone; reading the prompt into a variable lets `set -e` catch a missing file without a check.
- Ported skills keep their provenance under `metadata` as flat strings, since the Agent Skills spec defines string keys and values.

### Fixed

- `recall-memories` declared `arg`, which is not a key — the autocomplete hint is `argument-hint`, so it was declaring nothing.
- `credits` declared `name: credit` against its own directory, the only such mismatch in the bundle.
- The linter returned success for a file whose YAML it had only repaired, leaving a wrong name and an unknown key in place, and raised `AttributeError` on frontmatter that was not a mapping.
- The pi wrapper called bare `bun`, so pi died with `exec: bun: not found` whenever `~/.bun/bin` was off PATH.
- `skills/software`'s dispatch table had one row listing fourteen sub-topics where every other row names a handful.

## [v0.3.83] — 20260912

> kronael v0.3.83 — guidance measured against a model that cannot see it
>
> The wisdom skill can now tell whether a rule earns the context it costs, by asking a model with no access to the file to write that guidance itself.
>
> • `wisdom` gains `clean-room.sh` — a throwaway HOME and empty cwd, so the model answers from training, not from your config
> • Rules two clean models produce unprompted are cut; rules they state and then break are kept and stressed
> • The four pre-kronael language skills are pruned; `sh`, `py`, `rs`, `ts`/`tsx` supersede them
> • `tsx` gains the theme-variable rule: never hardcode a colour, fix `globals.css`
> • The `./tmp` scratch-location rules are gone — the log path is the caller's choice
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Operator note — pruned language skills

`bash`, `python`, `rust` and `typescript` never existed in this repo; they came
from a pre-kronael install and their descriptions collide with `sh`, `py`, `rs`
and `ts`/`tsx`, which is a routing race. Install now prunes them. Their content
was checked line by line against the successors first — everything was already
covered, usually more precisely, except the Tailwind theme-variable rule, which
moved to `tsx`.

### Added

- `skills/wisdom/` gains the minimize method and `clean-room.sh`. A rule in an always-loaded file earns its place only when the model would not already behave that way, so the harness runs a prompt against a throwaway `HOME` (no wisdom file to load) in an empty working directory (no project `CLAUDE.md` to discover), and the skill requires verifying the room with a probe before any answer is trusted. It refuses an unknown model rather than silently answering from a resolved one, refuses an empty or missing prompt, keeps errors on stderr, and never prints an empty answer as a result.
- `tsx`: theme variables are mandatory — `bg-card text-foreground border-border`, never `bg-[#1C1C1C]`; a wrong colour is fixed in `globals.css`, never worked around at the call site.

### Changed

- Guidance that two clean models produce unprompted is cut from `skills/global/SKILL.md` and `software/code.md`: the generic git safety mechanics, mock boundaries and test-file locations, subagent briefing and spawn thresholds, the no-duplication and fail-loud paragraphs, the rule of three and state minimisation. Workflow content stays regardless of reproducibility — make targets, the commit format, slash-command triggers, the `.ship/` and `.diary/` layout, the `BUGS.md` protocol, `/resolve` and `/gh-comment`.
- Rules the models recite and then confess to breaking are kept and stressed with the pull that defeats each: never claim done before running the verification command, never state a claim unverified, never improve beyond what was asked, fix causes rather than the reported instance, and zero comments by default.
- The `./tmp` scratch-location rules are removed from the wisdom file, `code.md`, `software/observe.md`, `software/testing.md`, `review/take.md`, `browse` and `agent-browser`. Capture-once, the failure screenshot and the heartbeat stand without a prescribed directory.

### Fixed

- The push rule had been rewritten from a prohibition into an unconditional order to push, which contradicted commit-only-when-asked and commanded an action `settings-recommended.json` denies outright. Restored, with the force-push ban.
- `clean-room.sh` deleted only regular files, so a symlink or fifo in the room left `rmdir` with a non-empty directory and turned a successful run into exit 1 with the room leaked.
- A heading whose rule had been cut is renamed to what sits under it; the subagent-report rule no longer appears twice in the wisdom file; the `review` skill no longer cites a rule that was removed; `code.md` no longer claims language skills carry a `requires: software` frontmatter hint, which none of them do.

## [v0.3.82] — 20260912

> kronael v0.3.82 — Stop recaps the turn
>
> Every Stop with nothing to block on now recaps what landed, what is still uncommitted, and any git operation left mid-flight.
>
> • Stop recap — commits landed, what is still uncommitted, and any merge/rebase in progress
> • Output style renamed to `caveman` — installs prune the old file and repoint `outputStyle`
> • show-me — ask for the smallest visual: pseudocode, call tree, mermaid, or a diff
> • Codex bridge — the managed block now survives install instead of being overwritten
> • dockbox + qemubox agree on claude-opus-5, claude-fable-5-1 and gpt-6-astra
> • A dated feature branch, its push and `gh pr create` are permitted for review
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Operator note — output style renamed

The response style is `caveman`: `output-styles/caveman.md`, frontmatter
`name: caveman`, and `"outputStyle": "caveman"` in settings. Install repoints
`outputStyle` and deletes `~/.claude/output-styles/80-caveman.md`; a hand-edited
`settings.json` that still names the old style activates nothing, because no
file answers to that name.

### Added

- `stop.py` emits a turn recap on a real Stop with nothing to block: commits landed since the session's previous Stop, tracked changes with `+added -deleted`, untracked paths touched inside the window, and any merge/rebase/cherry-pick/revert/bisect in progress. Capped at `RECAP_COMMITS` commits and `RECAP_PATHS` paths, bounded by one `RECAP_BUDGET` deadline, never emitted from periodic `PostToolUse` or under Codex.
- `show-me` skill — the smallest visual for the current topic: pseudocode, call tree, component tree, mermaid, or a diff. Ported from humanlayer/skills (MIT, attributed in `NOTICE`).
- `software` router gains the refactor-stack runbook: unreviewable-branch triage, tests before refactor, mutation-proven vs tautological tests, the dead-code oracle, and diffstat splitting.
- `tsx`: prop-narrowing rules. `wisdom`: `<important if>` guidance for project `CLAUDE.md` and the runbook body-pattern. `diary`: named companion entries `YYYYMMDD-<name>.md`.

### Changed

- The `caveman` output style is the single source of the response rules for both Claude and Codex; the wisdom file and the Codex managed block point at it instead of carrying their own copies.
- Wisdom permits a dated `YYYYMMDD_<tag>` review branch, `git push -u origin` to it, and `gh pr create` after showing title and body. `master`/`main` checkout, force push, `gh pr merge`, `gh pr review --approve`, `gh release create` and `gh repo create` stay forbidden; `settings-recommended.json` no longer denies `gh pr create`.
- `codex` skill inherits the newest model rather than pinning a literal, confirms it against `models_cache.json` priority 1, and pins `-m` only when the resolved default is not that entry. It also never hands codex a list of suspected weaknesses.
- `ship` requires re-research against current code in a subagent before planning.

### Fixed

- `stop.py`: a failed `git status` read as a clean tree, dropping the commit block and replacing it with a confident recap — an unreadable tree is now reported.
- `stop.py`: a partial git failure emitted half a recap and advanced the session stamp past work the user never saw. Any required call failing now drops the whole recap with the stamp untouched, which also makes the spent-budget and timeout paths agree. The git-dir probe runs under the same deadline.
- `stop.py`: status parses `-z` records, so non-ASCII and spaced paths reach the recap and a rename counts once; with no window the tree line reports what it can judge.
- Install merges the Codex managed block after the wisdom write. The Codex guidance path may symlink to the wisdom file, so merging during asset copy was overwritten.
- `qemubox` model aliases and default matched `dockbox`, turning `tests/drift_test.sh` green.

## [v0.3.81] — 20260902

> kronael v0.3.81 — install skill can rsync without prompting
>
> The recommended permission set now allows the install skill's rsync into `~/.claude/`, so setup doesn't stop for a permission prompt.
>
> • Allows `rsync * ~/.claude/*` in `settings-recommended.json`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Adds `Bash(rsync * ~/.claude/*)` to the recommended permission allowlist so the install skill's rsync step to `~/.claude/` runs without a manual approval.

## [v0.3.80] — 20260901

> kronael v0.3.80 — cleaner skills, safer installs
>
> Kronael now removes duplicate skill copies, preserves safe live edits during installs, and adds mold to both sandboxes.
>
> • Install — prunes stale skill/skill copies without touching newer or user-added files
> • TypeScript — exported functions declare return types; obvious locals still use inference
> • dockbox + qemubox — mold is preinstalled; existing qemubox bases reprovision
> • Two-way sync — safe live-ahead additions flow back to source instead of being overwritten
> • Agent workflows — restored clean prompts, Go comment guidance, and review-body distillation
> • Feedback — blocks unsupported SendFeedback and /feedback paths
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added

- `dockbox`, `qemubox`: install the `mold` linker; qemubox bumps its package marker so existing base images reprovision and receive it.
- `gh-comment`: add a distillation pass that keeps posted review comments concise and actionable.

### Changed

- Install is now a two-way sync: clean live-ahead additions in source-owned files flow back into the repository instead of being overwritten.
- TypeScript guidance requires explicit return types on exported functions while retaining inference for obvious locals and callbacks.
- Subagent launchers pass raw task context without the parent agent's diagnosis; Go guidance points comment decisions back to the shared baseline.
- Recommended settings and wisdom block unsupported `SendFeedback` and `/feedback` paths.

### Fixed

- Install safely prunes legacy `skill/skill` copies only when every nested file has a current root counterpart and no live-ahead content would be lost.

## [v0.3.79] — 20260827

> kronael v0.3.79 — zero-comments baseline, sharper reviews
>
> The code baseline now bans redundant comments outright, and the review skills gained an invariant lens plus mandatory finding re-verification.
>
> • Comments — `software/code.md` carries a zero-comments policy; Claude stops narrating what names and types already say
> • `/review` — new invariant/topology lens catches changes that read correct hunk-by-hunk but drop a structural guarantee
> • `/review take` — re-verifies each finding against current code before editing; PR replies carry fixed/deferred/declined
> • Wisdom file now mandates loading `code.md` before writing code, so the style rules can't be silently skipped
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `software/code.md`: new § Comments — zero by default, one line only for a non-obvious WHY, redundancy test (a comment restating a neighbouring log/error is the canonical bug), no multi-line blocks, no line numbers or ticket IDs. Adapted from @ochaloup/claude (credited in NOTICE).
- `review` (give/take): added an invariant/topology lens, stable tier IDs (C1/I2/M3), mandatory re-verification of each finding against current code, and per-thread PR reply dispositions (fixed/deferred/declined). Adapted from @ochaloup's PR-review pipeline.
- `global` wisdom (→ `~/.claude/CLAUDE.md`): the code.md pointer is now a load-mandate — code.md is cold, so it names it, orders `/resolve` (or the software skill) before writing/reviewing code, and states unloaded rules only hide, not relax. Removed two inline comment-policy restatements now canonical in code.md.
- `rs`: dropped its § Comments (pure duplicate of the new base); `go` keeps its inline-vs-above rule.
- `review/give.md`: fixed a stale `gh-review` reference (folded into the router) that contradicted the file's own GitHub-PR section.

## [v0.3.78] — 20260825

> kronael v0.3.78 — psql in both boxes
>
> Both sandboxes now ship the Postgres client, so `psql` works inside dockbox and qemubox without a manual install.
>
> • dockbox + qemubox — `psql` (postgresql-client) preinstalled; DB work no longer starts with an apt install
> • qemubox — guest package marker bumped, so boxes provisioned earlier pick up psql on next boot
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `dockbox`, `qemubox`: add `postgresql-client` (the `psql` CLI) to the base package set — dockbox's image apt layer and qemubox's guest provisioning. dockbox already carried `libpq-dev`; this adds the client binary.
- `qemubox`: guest package marker bumped `packages-v1` → `packages-v2`, so already-provisioned boxes and the prebuilt base re-run apt and pick up psql.

## [v0.3.77] — 20260824

> kronael v0.3.77 — bhctl: bluetooth headphones in three words; -K gpg fixes
>
> New `bhctl` CLI drives bluetooth headphones from the terminal, and `-K` gpg forwarding actually works now in both boxes.
>
> • `bhctl` — `hifi` / `mic` / `off` over bluetoothctl + pactl; auto-finds the first paired audio sink, bare invocation prints name/connection/battery/mode
> • dockbox `-K`: chowns `~/.gnupg` in the container so gpg can write its trustdb (was root-owned, gpg failed)
> • qemubox + dockbox `-K`: probe gpg-agent liveness and warn instead of forwarding a dead socket
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `bhctl`: new standalone CLI for bluetooth headphones. Three commands — `hifi` (A2DP playback, mic dead), `mic` (HFP headset mic, narrowband playback), `off` (disconnect) — plus a bare invocation that reports name/connection/battery/active mode. Finds the headphones itself (first paired device advertising an audio sink; no MAC to configure). Stubbed `test.sh` runs the full matrix with no adapter or daemon; wired into `make test` + CI.
- `dockbox`: `-K` now chowns `/home/dockbox/.gnupg` during init — Docker auto-creates the gpg mount-parent as root, so gpg could not write its trustdb and signing failed silently.
- `qemubox` + `dockbox`: `-K` probes `gpg-connect-agent /bye` before forwarding; a dead host agent now prints a clear "not forwarding, run gpgconf --launch gpg-agent" warning instead of mounting an unresponsive socket.

## [v0.3.76] — 20260821

> kronael v0.3.76 — safer rm, sticky ports, fresher toolchain
>
> qemubox/dockbox `rm` now needs an explicit target, qemubox boxes keep a stable SSH port, and the dockbox image toolchain is bumped.
>
> • `rm` with no argument refuses (no more accidental wipe); `rm -a` (or `'*'`) removes all
> • qemubox persists each box's SSH port in `$dir/port` — stable across re-entry, auto-reallocates on collision
> • dockbox image toolchain: nvm 0.40.7, nushell 0.115.0
> • Internal simplification: dropped an `eval` and a one-arm `case`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `qemubox` + `dockbox`: `rm` with no argument now exits non-zero instead of removing every box; an exact name, a `*`/`?` glob, or `-a`/`--all` (or `'*'`) is required. Bare `rm` was a footgun that wiped all VMs.
- `qemubox`: each box persists its SSH port in `$dir/port` — `start_box` walks up from the name-hash to the first free port and saves it, so re-entry and ssh reuse it and a name-hash collision reallocates instead of failing.
- `dockbox`: image toolchain bumped — nvm 0.40.4→0.40.7, nushell 0.112.2→0.115.0 (rebuild with `make image`); git-delta/gitleaks already current and node/bun/go/dotnet/uv/claude/codex track latest/LTS at build time.
- `qemubox`: internal cleanup — `add_env` uses `${!var}` indirect expansion instead of `eval`; dropped a one-arm `case` around `tool_cmd`.

## [v0.3.75] — 20260821

> kronael v0.3.75 — qemubox hardened: kill-switch, untrusted mode, locking, tests
>
> qemubox gets a network kill-switch, a credential-free untrusted mode, lifecycle hardening, and a no-VM bash test suite.
>
> • `-H` egress kill-switch and `-U`/`--untrusted` (no creds, no network) for poking at code you don't trust
> • `-K` makes gpg-agent forwarding opt-in (was always on); `-n` rejects path-traversal names
> • Lifecycle hardened — per-box `flock`, port bind-test, orphan-kill on failed start, teardown that won't nuke a live box
> • `qemubox status <name>`, base-image checksum, and a bash test suite (qemubox + dockbox) wired into CI
> • `rm` exact-match+glob in both tools; security-audit skill `/hacker-eval` → `/red-eval`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `qemubox`: confinement flags — `-H` now disables outbound network (was a no-op; the `restrict=on` path is live), `-U`/`--untrusted` injects no host config/credentials and forces network off while still mounting the project (for shells/builds on untrusted code — the agent can't auth without creds), `-K` gates gpg-agent forwarding opt-in (both tools; was unconditional), `-n` rejects `.`/`..`/`base`/empty/slashed names (path traversal).
- `qemubox`: lifecycle hardening — per-box `flock` around start (no same-name races), wider SSH ports + `/dev/tcp` bind-test with a clear "port busy" error, the daemonized qemu is killed if SSH never comes up, ref-count teardown is conservative on an ssh flake (won't tear down a live box), and re-entry is race-free (derived inside the lock). `prune` no longer aborts when a box dir vanishes mid-loop.
- `qemubox`: `status <name>` (process/SSH/boot readiness without a shell) and base-image SHA512 verification (`QEMUBOX_BASE_SHA512` or Debian's `SHA512SUMS`).
- `qemubox` + `dockbox`: `rm` matches exactly, `*`/`?` = glob (was substring). A no-VM bash test suite (`test.sh` each) asserts the security-load-bearing matrix (name guard, mount ro/rw per flag, `-U` injects nothing), plus a drift test guarding the shared model-alias table; both wired into `make test` + CI.
- Install: security tools renamed `/hacker-eval` → `/red-eval` (table + `eval-all`); `trufflehog` installs from a release binary (not `go install`); the renamed/folded skill dirs added to the install prune list.

## [v0.3.74] — 20260821

> kronael v0.3.74 — qemubox grows up: fast boot, auto-shutdown, honest about what it protects
>
> qemubox now prebuilds its image so boxes boot in seconds, auto-shuts-down when done, and stops overselling what it isolates.
>
> • Prebuilt base image at install — boxes boot in seconds, not 1-2 min of first-boot `apt-get`
> • Auto-shutdown when the last session exits (ref-counted, like dockbox); concurrent sessions keep it up
> • `rm` matches exactly in both qemubox and dockbox — `*`/`?` glob only; no more accidental over-match
> • Streamed, gutter-prefixed provisioning output (ASCII `>>>` / `>`) so you can tell the script from the guest
> • Honest READMEs + ELI13: confines host-filesystem blast radius + disposability, NOT a jail for hostile code
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `qemubox`: prebuilt base image — `build-base` (run once by `make install`, non-fatal without KVM/network) bakes the guest apt layer into `provisioned.qcow2` via a throwaway `.build` box; new boxes overlay it and skip first-boot apt.
- `qemubox`: ref-counted lifecycle — a per-session marker in `/run/qemubox/sess` (dropped right after boot, before provisioning); the VM is torn down when the last session exits, concurrent sessions keep it up. `stop_box` escalates poweroff→SIGTERM→SIGKILL (90s systemd wait) so a wedged VM is killed not orphaned, and `remove_box` never deletes a live VM's disk.
- `qemubox` + `dockbox`: `rm` matches box names exactly; a pattern with `*` or `?` is treated as a glob (was substring `grep -F`, so `rm staking-rewards` also removed `staking-rewards-facade`).
- `qemubox`: provisioning/guest output streams behind a dim `>` gutter, distinct from the `>>>` script voice; both ASCII, TTY-guarded (plain text when piped).
- `qemubox` + `dockbox`: rewritten READMEs with an ELI13 section and an honest security-posture statement — the tools confine host-filesystem blast radius and give a disposable env, but inject real agent credentials and leave outbound network on, so they are not a boundary against hostile code. Tracked hardening (network kill-switch, gpg opt-in, `--untrusted` mode, behavioral tests) is in `BUGS.md`.

## [v0.3.73] — 20260820

> kronael v0.3.73 — qemubox actually mounts now
>
> qemubox now boots Debian's generic cloud image, whose kernel ships the 9p module the disposable VM needs to mount your project.
>
> • Base image is Debian `generic`, not `genericcloud` (whose trimmed kernel omits 9p — the mounts silently failed)
> • If a guest kernel ever lacks 9p, you get a clear message and the fix, not a cryptic "unknown filesystem type '9p'"
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `qemubox`: default base image `genericcloud` → `generic`. The genericcloud kernel omits `CONFIG_9P_FS`, so every `mount -t 9p` failed with "unknown filesystem type '9p'" regardless of `modprobe`. Added a guest preflight (`grep 9p /proc/filesystems`) that fails with actionable guidance instead of the raw mount error. Existing VMs must be recreated (`qemubox rm <name>`) to rebuild on the new base.

## [v0.3.72] — 20260820

> kronael v0.3.72 — qemubox: a disposable VM that shares only what a run needs
>
> New tool: qemubox runs agents in a throwaway QEMU VM that mounts your project and tool config — not your whole home.
>
> • Agent config (`~/.claude`/`~/.codex`/`~/.agents`) is copied in — guest edits never touch the host
> • Only the active project's transcripts + auto-memory persist back; other projects stay private
> • Your home is never mounted — no `~/.ssh`, cloud creds, or other repos reach the guest
> • Loads the guest 9p modules and fixes first-boot setup so it runs on stock Debian cloud images
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- New `qemubox` CLI — a disposable QEMU + 9p VM wrapper mirroring dockbox's agent surface for inspecting untrusted repos.
- Mount confinement: no blanket `$HOME` mount; single-file config (`.claude.json`, `.gitconfig`, gpg pubrings) staged read-only; `~/.claude`/`~/.codex`/`~/.agents` copied into the guest's own home (host read-only) so guest config edits never reach the host; session data scoped to the active project's slug (`~/.claude/projects/<slug>`, incl. auto-memory) mounted rw so recall persists without exposing other projects.
- Guest boot fixes: `modprobe 9p 9pnet_virtio` before the first 9p mount (stock Debian cloud images don't auto-load it); `~/.gnupg` created by the sandbox user rather than root (a `sudo`+chmod mismatch aborted `setup_guest_runtime` under `set -e`); staging dir `chmod 700`.
- Further hardening (gpg-agent forwarded unconditionally, predictable SSH ports, `-H`/network confinement, stuck-VM lifecycle) and the dockbox config-copy mirror are tracked in `BUGS.md`.

## [v0.3.71] — 20260811

> kronael v0.3.71 — Codex sees your skills inside dockbox
>
> dockbox now wires the installed Claude skills into Codex on every container start, so `@skill` and global guidance just work.
>
> • Symlinks `~/.agents/skills` → your `~/.claude/skills` so Codex lists every bundle skill
> • Points `~/.codex/AGENTS.md` at `~/.claude/CLAUDE.md` for global guidance
> • Idempotent and safe — no-op until the bundle is installed; never clobbers your own AGENTS.md
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `dockbox`: the container entrypoint (`dockbox-init`) now runs a small idempotent `dockbox-codex-bridge` on every start. When `~/.claude/skills` exists it creates `~/.agents/skills → ~/.claude/skills` (Codex's skill root) and repoints `~/.codex/AGENTS.md → ~/.claude/CLAUDE.md`; it no-ops until the bundle is installed and leaves a real (non-symlink) `AGENTS.md` untouched. Rebuild with `make image`.

## [v0.3.70] — 20260810

> kronael v0.3.70 — udfix can check diagrams, not just fix them
>
> udfix gains a --lint mode that reports broken box-drawing junctions with line:col and exits non-zero, so docs diagrams can gate CI.
>
> • `--lint` reports `row:col` for each junction missing a segment that touches it, plus the right glyph
> • Flags ASCII arrows `->` and `<-`, and points you at `► ◄ ▲ ▼`
> • Tree-safe — tolerates a `├──` branch with nothing above, so it lints file trees too
> • Exits 1 on any defect, 0 when clean; `-l` is short for `--lint`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `udfix`: new `--lint`/`-l` mode checks a diagram instead of rewriting it — prints `row:col: message` per defect and exits 1 if any. Flags underspecified junctions (a glyph missing a segment that touches it, naming the expected glyph) and ASCII `->`/`<-` arrows; tolerates overspecified junctions so file-tree listings (`├──`) pass clean. Shares `touching`/`splitDiagram` with fix mode, which is unchanged. Adds `TestLint`/`TestLintPosition`.

## [v0.3.69] — 20260808

> kronael v0.3.69 — codex remembers your project
>
> The codex second-opinion skill now resumes your project's existing codex thread instead of starting cold every call.
>
> • codex — second opinions resume this project's codex session instead of starting cold each call
> • first call in a project cold-starts cleanly — no setup, no first-run special case
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `codex`: second-opinion calls launch via `codex exec resume --last`, continuing the current cwd's most recent codex session (cold-starts cleanly when none exists). Dropped `--ephemeral` from the default (incompatible with resume); it stays as the escape hatch for isolated batch loops.

## [v0.3.68] — 20260806

> kronael v0.3.68 — stricter recall + dockbox protoc
>
> Recall now insists on grepping session transcripts, not just diary and memory, and dockbox images can build protobuf code.
>
> • recall-memories — every recall MUST grep the session JSONLs; diary + memory alone no longer counts
> • dockbox — the image ships protoc (protobuf-compiler) so protobuf-generating builds work
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `recall-memories`: every recall now hard-gates on grepping the project's session transcripts (`~/.claude/projects/<slug>/*.jsonl`); diary + memory alone is no longer a recall.
- `dockbox`: the image build installs `protoc` (protobuf-compiler) so builds that compile `.proto` files work.

## [v0.3.67] — 20260804

> kronael v0.3.67 — three wisdom rules the bundle was missing
>
> The global wisdom file gains three rules that had only ever lived in a running install.
>
> • no claude.ai publishing — produce local files, never upload reports/pages via the Artifact tool
> • comments earn their place — never restate the code; never reference an earlier version (history lives in .diary/)
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `global`: back-port three rules that had drifted into a running `~/.claude/CLAUDE.md` but never into source — never publish to claude.ai hosting (local files only), never write a comment that restates the code, and never reference an earlier version in comments/docs/skills (state what is true now; history lives in `.diary/`).

## [v0.3.66] — 20260725

> kronael v0.3.66 — dockbox uses one package manager
>
> The dockbox image now installs both Claude Code and Codex with bun; npm is gone.
>
> • dockbox — claude-code installs via bun like codex; ripgrep is embedded in claude's compiled binary (verified in-image), so nothing regresses
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `dockbox`: install `@anthropic-ai/claude-code` via `bun install -g --trust` instead of npm, so both CLIs use one package manager. claude-code 2.x ships a compiled binary with ripgrep embedded, so the bun install is identical to npm's; the `claude` wrapper now points at `$BUN_INSTALL/bin/claude` and the final chmod is narrowed to the bun tree.

## [v0.3.65] — 20260722

> kronael v0.3.65 — skills quality wave + self-describing installs
>
> Reinstalls now tell you which releases they're about to apply, five new skills land, and the eval lenses get sharper.
>
> • install records the installed release — a reinstall reports the version/commit delta before touching anything
> • new skills: doc-topology, finalize-crate, go-gl, speed-demo, port-to-go
> • eval lenses sharpened — hacker-eval → red-eval, anti-fabrication guards, best-practice grounding
> • merge skill now drives rebases and cherry-picks to completion, not just merges
> • Codex loads applicable CLAUDE.md alongside AGENTS.md, with the terse caveman reply policy
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `doc-topology` skill: structure project docs by the question each file answers (README/ARCHITECTURE/notes/compare/facts) plus a how-to-read index and anti-marketing discipline.
- New skills `finalize-crate`, `go-gl` (native OpenGL desktop apps in Go), `speed-demo` (benchmark-reveal GIFs), and `port-to-go` (faithful into-Go transcode with differential traces).
- install: an installed-release marker in `~/.claude/kronael-install-manifest.json` (version, git commit/describe, timestamp) with a per-file sha baseline; preflight reports the installed→source delta and which releases a reinstall will apply.
- Global wisdom: a mobile-terminal reply cap (~17 lines, bottom-line last), a System-change discipline section (no-duplication, fail-loud, retry-only-transient, fix-causes, redesign sign-off), and a no-recursive-`rm` rule.
- Codex: global guidance now loads every applicable `CLAUDE.md` alongside `AGENTS.md` and applies the `caveman` response policy without replacing user rules.

### Changed
- Eval family: `hacker-eval` → `red-eval`, `eye-13yo` → `13yo-eval`; added LLM-behavior / anti-fabrication guards and best-practice grounding.
- `merge` skill (renamed from `merge-trivial`) now drives merges, rebases, and cherry-picks to completion, finishing by operation type.
- `software` router folded `testing` in as `software/testing.md`; `release` tagging is collision-safe and re-points tags orphaned by a rebase.
- install runbook: tool tables + removed-skills prune list moved to `kronael/install/reference.md`, keeping `SKILL.md` under the 200-line rule.
- `ship` skill rewritten as a fable-plan → sonnet-ship → refine pipeline; `oracle` routing consolidated through high-effort critics; subagent effort defaults set.
- `bugs` skill reconciled to real practice: dated blocks, kebab IDs, inline resolution.
- Plugin manifests (`.claude-plugin`, `.codex-plugin`) bumped to 0.3.65 to track the release.

### Fixed
- `finalize-crate` / `red-eval` frontmatter: quoted colons so YAML parses the real description (they were loading with an H1 fallback).
- `udfix`: 64 KB line-limit and trailing-newline handling; strengthened tests.

## [v0.3.64] — 20260721

> kronael v0.3.64 — tighter specs + learn dispatch
>
> The specs skill gets flat numbered filenames, a per-spec index row, and a clean 4-state status; "learn" now routes to @learn.
>
> • specs — flat `NN-topic.md` names + an index.md row per spec; phases only for multi-stream efforts
> • specs — status trimmed to draft → planned → partial → shipped (dropped experiment/reference)
> • prompt nudge — "learn" now dispatches to the @learn agent
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `specs`: default flat `specs/NN-topic.md` numbering (phase subdirs only for large multi-stream efforts); ALWAYS add an `index.md` row on create and update Status on ship.
- `specs`: status enum trimmed to the four lifecycle states `draft → planned → partial → shipped`; dropped `experiment` and `reference`.
- `prompt_nudge`: `learn` keyword routes to the `@learn` agent.
- `plugin.json`: version synced to the release tag (was stale at 0.3.47); CLAUDE.md now requires this bump on every release.

## [v0.3.63] — 20260720

> kronael v0.3.63 — collision-safe releases + refinements
>
> The release skill now guards against tag collisions, plus fixes to eval-all logging and a leaner install runbook.
>
> • release — picks an untagged version, recreates tags that collide or point at orphaned commits, re-points after a rebase renumber
> • eval-all — the run prompt owns the per-lens memo save (the eval skills don't all persist by default)
> • install runbook trimmed 232→209 lines (sync protocol, Codex bridge, preflight)
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `release`: tag step is now collision-safe — pick a version not already tagged (bump past collisions), recreate (`git tag -d` + re-tag) any tag that collides or points at an orphaned commit, and re-point every tag after a rebase renumbers releases. Commit format `release: vX.Y.Z`.
- `eval-all`: corrected the logging note — the individual eval skills don't all write `.ship/critique-*` memos, so eval-all's run prompt instructs each subagent to save its own (and verify it landed).
- `install`: re-compressed the sync protocol, Codex bridge, and preflight (232 → 209 lines); the duplicate `0.` preflight steps merged. Full <200 still needs a structural split (deferred).

## [v0.3.62] — 20260720

> kronael v0.3.62 — eval panel + sharper caveman
>
> Adds /eval-all to run every review lens and log the verdict, sharpens the caveman style with ADHD-friendly patterns, and trims two skills that duplicated existing ones.
>
> • /eval-all — runs ceo/cto/security/ux lenses as subagents, logs memos + a diary pointer for later context
> • caveman gains multi-turn patterns: restate progress, cap-5 + do-now/later, minute estimates, first/last-line check
> • drops assess (dup of ceo/cto-eval) and sweep-fix-verify (its discipline already in the wisdom + worktree)
> • commit format is now type(scope): everywhere; reverse-sync flags local skills before adding to source
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `eval-all`: new skill — runs every applicable eval lens (`ceo-eval`, `cto-eval`, `hacker-eval`, `hiring-eval`, `eye-13yo`) as independent subagents, then persists each memo to `.ship/`, a consolidated roll-up, a `/diary` pointer, and real defects to `BUGS.md` — so a later session has the eval context.
- `caveman` output style: folded in multi-turn / low-cognitive-load patterns — restate progress ("step 3 of 5"), cap lists at ~5 with a do-now/later split, minute-level effort estimates, one-thread-at-a-time, first/last-line pre-send check, action-first. Adapted from `i-have-adhd` by Ayoub Ghriss (MIT), attributed in `NOTICE`.
- Dropped `assess` (redundant with `ceo-eval`/`cto-eval`/`hiring-eval`) and `sweep-fix-verify` (discipline already in the wisdom, `commit`, `worktree`, `refine`) — both were installed-only and org-tinged. `worktree` + `later` stay.
- Commit convention finalized as `type(scope):` across the bundle (AGENTS.md + COOKBOOK.md were the last `[section]` holdouts).
- Install sync protocol: installed-only skills are not auto-captured into source; org/local ones are flagged and added only on explicit opt-in.

## [v0.3.61] — 20260720

> kronael v0.3.61 — four skills back in source
>
> Four skills that lived only in local installs are now in the repo: adversarial assessment, a defer-to-later verb, a multi-step audit checklist, and subagent worktree isolation.
>
> • /assess — adversarial product/code critique from a ceo/cto/ciso/buyer lens, saved to .ship/
> • /later — defer an idea or follow-up to TODO.md; recurring items route to /schedule
> • /sweep-fix-verify — gating checklist so large multi-subagent changes don't silently break HEAD
> • /worktree — isolate every code-editing subagent in its own git worktree
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Captured four skills that existed only in local installs into source, org-specific examples genericized: `assess` (adversarial ceo/cto/ciso/buyer/investor/competitor critique → `.ship/critique-*.md`), `later` (defer to `TODO.md`; recurring items point at `/schedule`), `sweep-fix-verify` (gating checklist for multi-step / multi-subagent changes — verify writes not just runs), `worktree` (per-subagent git-worktree isolation).

## [v0.3.60] — 20260720
> kronael v0.3.60 — tighter replies, tougher discipline
>
> Replies cap at ~17 lines with the point last, /merge now finishes rebases and cherry-picks, and a fail-loud engineering discipline joins the wisdom.
>
> • Replies default to ~17 lines and end on the single most important point (mobile-terminal friendly)
> • /merge now detects and finishes a rebase or cherry-pick, not just a merge — with --skip/--abort
> • New wisdom: fail loud to the user, retry only transient errors, fix causes, sign-off redesigns
> • refine derives review lenses from the live wisdom and tags each simplify or correctness
> • install activates the output style and propagates the wisdom to pi via ~/.pi/agent/AGENTS.md
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Response style: the global wisdom and the `caveman` output style now cap a normal reply to ~17 lines (ideal 12, max 20) and close on the single most important point — on a mobile terminal the last line is what stays visible.
- `merge`: detects the in-flight operation (merge / rebase / cherry-pick / revert) from `.git` state and drives it to completion — `--continue` in a loop, `--skip` for an obsolete replayed commit, `--abort` to bail. Documents that in a rebase the conflict sides are reversed (`HEAD` is the base, `>>>>>>>` is the replayed commit).
- Wisdom: new **System-change discipline** section — amend the original (no parallel second path), fail loud to the user (never swallow errors), retry only transient errors, fix causes not symptoms, and record redesigns in `BUGS.md` as `proposed` for sign-off before shipping.
- `refine`: review lenses are now derived from the live wisdom (1-3 per sub), tagged `simplify` / `correctness` with model-by-tag routing; redesign findings route to `BUGS.md`. `bugs`: adds the `proposed` status to the entry format.
- `install`: sets the live `~/.claude/settings.json` `outputStyle` (without the key the shipped style never activates) and symlinks `~/.pi/agent/AGENTS.md` → `~/.claude/CLAUDE.md` so the wisdom reaches pi.
- Known issue logged (`BUGS.md`): `uv tool install faster-whisper` fails — it's a library with no CLI entrypoint.

## [v0.3.59] — 20260720

> kronael v0.3.59 — richer linter + runtime-checker guidance for go/rust/python
>
> The software skill now says which linters to run and which runtime checkers to wire as test targets — race detectors, sanitizers, fuzzing, Miri, memory/leak — across Go, Rust, and Python.
>
> • strict-typing — adds the Go golangci-lint set (errcheck, staticcheck, nolintlint …) alongside the existing py/ts config
> • dynamic-analysis — new runbook: runtime checkers as make/CI targets, not pre-commit (go -race/fuzz/goleak, rust Miri/sanitizers/loom, python -X dev/hypothesis/memray)
> • go / rs / py — each links to the runbooks for its linter set and test-target checkers
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `software/dynamic-analysis.md`: new runbook for runtime/dynamic checkers wired as `make test`/CI targets (never pre-commit) — Go (`-race`, `-shuffle`, `-fuzz`, goleak, `-asan`/`-msan`, govulncheck), Rust (Miri, `-Zsanitizer`, cargo careful, loom, cargo-fuzz, nextest, cargo-mutants), Python (`-X dev -W error`, faulthandler, pytest-randomly, hypothesis, pytest-memray, free-threaded ThreadSanitizer).
- `software/strict-typing.md`: Go section — golangci-lint v2 set (`errcheck` with `check-type-assertions`, `staticcheck`, `govet`, `errorlint`, `bodyclose`, `exhaustive`, `nolintlint` `require-specific`/`require-explanation`, …) with the escape-hatch→linter table.

### Changed
- `go` / `rs` / `py` skills link to the `strict-typing` and `dynamic-analysis` runbooks for their linter set and test-target checkers; `software` router dispatch table, `when_to_use`, and edit-reference updated to route on them.

## [v0.3.58] — 20260719

> kronael v0.3.58 — commits must be detached-HEAD
>
> The commit skill and its nudge now explicitly require a detached HEAD, and two skills that assumed branch-backed worktrees were corrected.
>
> • commit — refuses a commit unless `git branch --show-current` is empty; the commit nudge says the same
> • commit / refine — worktree cleanup no longer runs `git branch -D` (worktrees are `--detach`, so there's no branch)
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `commit`: explicit detached-HEAD requirement at the commit-time enforcement points — the `commit` skill Rules and the `prompt_nudge` commit reminder. The principle stays canonical in the global wisdom file, not restated across skills.
- `commit` / `refine`: dropped `git branch -D` from worktree cleanup in both — worktrees are created `--detach` and carry no branch to delete.

## [v0.3.57] — 20260719

> kronael v0.3.57 — readable slice ops in the go skill
>
> The go skill now points at `samber/lo` for filter/map/reduce so those read as intent, while stdlib `slices` stays the answer for insert/delete/sort.
>
> • go — use `samber/lo` (`lo.Filter`/`lo.Map`) for functional slice work; stdlib `slices` for mutate/sort/search, no dep
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `go`: added a Slices section — stdlib `slices` for insert/delete/sort/search (never add a dep for those), `samber/lo` for filter/map/reduce/group where a manual loop hurts readability.

## [v0.3.56] — 20260719

> kronael v0.3.56 — session-memory nudge + safer defaults
>
> A new nudge reminds you to save durable memory before the context is lost, and Go builds now land in `dist/`.
>
> • memory_nudge — new hook: at Stop/PreCompact, prompts you to persist session-worthy facts, throttled so it isn't every turn
> • go — always `go build -o dist/<name>`, matching GoReleaser so one gitignore covers dev + release
> • global — NEVER recursive-remove (`rm -r`): delete named files only, or leave cleanup to the user
> • hooks — pinned to py39 so autoformat never emits 3.14-only syntax that breaks older Python
> • dockbox — rebuilds against the latest claude + codex in a cache-busted layer
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- `memory_nudge` hook: low-frequency Stop/PreCompact nudge to evaluate the session for memory-worthy facts and persist them; wired into `settings-recommended.json` (Stop + PreCompact), with tests.
- `go`: always build binaries into `dist/` — GoReleaser's default output, so dev and release builds share one gitignored dir.

### Changed
- `global` wisdom: added a hard "NEVER recursive removal (`rm -r`/`-rf`/`-R`)" rule — delete explicitly named files or leave cleanup to the user.
- `codex`: load the global wisdom file by default.
- `dockbox`: build the latest claude + codex in a cache-busted final layer.
- bundle sync: back-ported runtime-only skill edits into source; dropped deprecated skills (`create-code-presentation`, `gh-fix`, `gh-review`) now folded into the create/review routers.

### Fixed
- `ruff`: pin `hooks/**` to the py39 target so `ruff-format` never rewrites to 3.14-only syntax (paren-free `except A, B:`, PEP 758) that SyntaxErrors on older interpreters.

## [v0.3.55] — 20260713

> kronael v0.3.55 — install keeps all transcripts
>
> Install now always sets `cleanupPeriodDays` so Claude Code stops deleting your session history — the 30-day default silently drops old transcripts at startup.
>
> • install — applies the transcript-retention setting on every install, never asks; raises a lower value, never lowers it
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `install`: always apply `cleanupPeriodDays` (recommended value 3650000) when merging settings — the 30-day default deletes session transcripts at startup, and the toolkit keeps all history. Added to `settings-recommended.json`; install/`AGENTS.md` merge splices it alongside the hooks block, no prompt.

## [v0.3.54] — 20260713

> kronael v0.3.54 — SKILL.md 200-line rule sharpened
>
> A skill's `SKILL.md` never grows past 200 lines — overflow moves to linked sibling files loaded on demand, which the skill can force-read.
>
> • wisdom — 200-line cap is firm; deep content lives in adjacent siblings, not a longer preloaded file
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `wisdom` / `CLAUDE.md`: sharpened the 200-line rule — a `SKILL.md` never grows past 200; overflow (>50 lines: API docs, tables, deep dives) moves to adjacent sibling files linked from the `SKILL.md` and loaded on demand (router pattern), which the `SKILL.md` may direct the LLM to force-read.

## [v0.3.53] — 20260713

> kronael v0.3.53 — dockbox forwards the GH token on re-entry
>
> `gh` stopped working inside a re-entered dockbox because the GitHub token wasn't carried in; now `-e`/`-g` env forwards into every session.
>
> • dockbox — re-entering a running box with `-g` (or `-e`) now forwards the token, so `gh` works even if the box was first started without it
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `dockbox`: forward run-time env (`-e`, `-g`) into re-entry `docker exec` sessions. A box first started without `-g` never received `GH_TOKEN`, so `gh` failed inside it; env (unlike mounts/network) can be set per-exec. Tip: put `-g` in `~/.dockboxrc` to forward on every launch and re-entry.

## [v0.3.52] — 20260713

> kronael v0.3.52 — port-to-go transcode skill + language library
>
> A language-agnostic "faithful into-Go transcode" skill lands with a per-language quirk library (Python, TypeScript, Java) modelling the seams where each source language behaves unlike Go's naive equivalent.
>
> • port-to-go — new skill: differential-testing + golden-trace method, 0–7 phase model, and a divergence root-cause catalogue for byte-for-byte Go ports
> • port-to-go/py.md, ts.md, java.md — cold-loaded companions: RNG reproducibility, rounding, iteration order, serialization, and string seams per language
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `port-to-go` skill: faithful into-Go transcode of any source language, proven by differential decision traces under a bit-exact float gate. Carries the language-agnostic method — make the source deterministic → 1-to-1 module port → scalar parity harness → swappable-component split → Go drop-in → trace-parity grind → scale/tier → N-way parity — plus the Parity-Source-Of-Truth (worktree oracle), Behavior-Preserving-Refactor-Mirror, Crash-vs-Guard, and running-the-harness sections, and a genericized divergence root-cause catalogue (1-ULP constants, compensated-sum, libm, map-iteration, missing-reset, transport read-limits, dup-id gates, error-path state clears).
- `port-to-go/py.md`, `port-to-go/ts.md`, `port-to-go/java.md`: cold-loaded per-language behavioral-fidelity references (type/numeric model, RNG reproducibility, rounding, iteration & ordering, equality/null-ish, JSON serialization, strings, harness invocation, seam catalogue). TypeScript and Java are modelled from first principles; all three refine as more porting experience accrues.

## [v0.3.51] — 20260713

> kronael v0.3.51 — CV authoring mode, PR-title guard
>
> The create router gains a CV mode for evidence-led resume revision, and PR drafting no longer overwrites a PR's existing title.
>
> • create — new CV mode: revise a resume against evidence, keep its visual style, validate the rendered file
> • pr-draft — leaves an existing PR's title alone unless you ask; only the description is updated
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `create`: new CV authoring mode in the router — evidence-led revision, visual-style preservation, metric semantics, and rendered-artifact validation, cold-loaded as `cv.md`.
- `pr-draft`: never rewrite an existing PR's title — the PATCH updates the body only; rewrite the title solely when the user explicitly asks.

## [v0.3.50] — 20260712

> kronael v0.3.50 — dockbox worktree docs
>
> Explains how to get working git in a dockbox when the project is a git worktree — run in the repo root, or mount the root with `-v`.
>
> • dockbox — new "Git worktrees" README section: mount the root and the shared `.git` (plus every worktree under it) comes along
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `dockbox`: documented the git-worktree workflow in the README. Auto-detect already covers a worktree used as the project dir; for worktrees reached via `-v` (not auto-detected), run dockbox at the repo root or add the root as a `-v` mount so the backing `.git` is present.

## [v0.3.49] — 20260710

> kronael v0.3.49 — new skills, dockbox worktrees
>
> New skills ingest media, convert files, evaluate hiring candidates, and design logos; dockbox now works inside git worktrees.
>
> • media-ingest — pull a transcript, audio, or video from a YouTube (or most-site) URL with yt-dlp
> • markdown-converter — turn a PDF, Office doc, EPub, or webpage into Markdown via markitdown
> • /hiring-eval — evaluate an engineer from their repo, demo, or resume against an evidence bar
> • create — new logo/emblem mode designs brand marks with a validated method
> • data-reports — conventions for Vega-Lite multi-panel PNG report scripts
> • dockbox — git worktrees now work inside the box (backing git dir is mounted)
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `media-ingest` skill: ingest media from a URL (YouTube + most sites) via `yt-dlp`/`ffmpeg` — transcript, audio, video, subtitles, or format listing; encodes rolling-VTT dedup and human-subs-first. Adapted from steipete/agent-scripts (credited in README).
- `markdown-converter` skill: convert a local file (PDF, Office, HTML, EPub, data, image, audio, ZIP) to Markdown via `uvx markitdown`. Adapted from steipete/agent-scripts.
- `create`: new logo/emblem design mode in the `create` router — generates brand marks and favicons with a validated method.
- `hiring-eval` skill: evaluate an engineer from artifacts, repo, demo, or resume — evidence order, judgment dimensions, HFT/low-latency addendum, and an explicit "what would change my mind" bar. Deployed for weeks but never in source until now.
- `data-reports` skill: conventions for Vega-Lite multi-panel PNG report scripts (Bun + vega + sharp). Deployed but previously uncommitted.
- `dockbox`: mount the backing git dir so host-created worktrees resolve inside the container; strip host install-topology keys from the injected Claude config.
- `refine`: scale the number of review lenses to diff size and pick the review model by tag. `hooks/commit`: emit the standard `type(scope): message` format.

## [v0.3.48] — 20260707

> kronael v0.3.48 — install always offers tools + dockbox on re-run
>
> Re-running install now reliably offers the external-tool and CLI-tool/dockbox steps instead of silently skipping them, and stops trying to install faster-whisper as a CLI.
>
> • install: every update runs the tool + dockbox asks — a stale binary or an un-offered dep is the failure this prevents
> • install: faster-whisper is documented as a library pulled via `uv run --with`, not a broken `uv tool install`
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- install: on an update, ALWAYS run the external-tools (step 6) and CLI-tools/dockbox (step 7) asks — detect and install any missing core tools, ask once for the heavy security/video batch, and offer the CLI-tool + dockbox (re)install. Previously a re-run could silently skip these, leaving a stale binary or an un-offered dependency.
- install: corrected the `faster-whisper` entry — it is a library with no CLI entrypoint (so `uv tool install` fails), pulled by the render script via `uv run --with faster-whisper`.

## [v0.3.47] — 20260707

> kronael v0.3.47 — /con becomes /continue
>
> The continue-mode skill is now /continue; typing "continue" nudges you to it, and it asks what to resume when nothing's half-finished.
>
> • /con renamed to /continue — the full word, matching how you actually ask for it
> • typing "continue" or "cont" now nudges to /continue (like "fin" → /fin)
> • /continue with nothing unfinished confirms you're in a clean state, suggests /recall-memories, and lays out where to go next
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Renamed the `con` skill to `continue` (it was briefly `cont`) — the full word reads as the verb and matches the nudge trigger. Old `con`/`cont` dirs added to the install prune list so reinstalls drop the orphans.
- `/continue` now handles the empty case as a forward-looking mode: when nothing is interrupted, it confirms the session/repo is in a clean state, suggests `/recall-memories`, then reads the diary + `TODO.md`/`BUGS.md` + recent commits and presents where to go from here as candidate directions instead of guessing or stalling.
- `prompt_nudge` routes `continue`/`cont` → `/continue` (parallel to `fin` → `/fin`), with a guard test.

## [v0.3.46] — 20260706

> kronael v0.3.46 — reconciled the diverged local and remote lines
>
> Local and remote both branched from v0.3.40 and minted colliding v0.3.41/42 tags; this merges them with nothing dropped and renumbers the local releases to sit after remote's.
>
> • merged origin (strict-typing, /pi, /astgrep, model-tier) with local (sweep, /con, fin, stop hook) — no content lost from either side
> • local releases renumbered to v0.3.43/44/45; remote keeps v0.3.41/42; duplicate tags removed
> • indexed the merged-in /pi skill in the README second-opinion group
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Reconciled the two histories that had diverged from v0.3.40: origin/master
  (v0.3.41 strict-typing + /pi + /astgrep + model-tier framing, v0.3.42 pi
  gpt-5.5) and local (sweep, /con, fin/con goal scopes, stop-hook cut). Merge
  kept all content from both sides; only `CHANGELOG.md` and `skills/README.md`
  needed hand-resolution.
- Removed the duplicated v0.3.41/42 tags: remote's now own v0.3.41/42, local's
  three releases were renumbered to v0.3.43 (sweep/con), v0.3.44 (con/fin
  scopes), v0.3.45 (con-toggle/stop) on their original commits — lineage
  preserved, no history rewrite.
- Indexed the `pi` skill in `skills/README.md` (it arrived in the merge but was
  missing from the index).

## [v0.3.45] — 20260706

> kronael v0.3.45 — con cut to a real mode-toggle; stop hook simplified
>
> con went through two more rounds of trimming down to its actual reference shape, and the stop hook dropped logic that duplicated skill-level behavior.
>
> • `con` cut from a 40-line procedure doc to a 16-line explore/ans-style mode-toggle (title, one-line intent, short Behavior list) — matches the actual reference pattern for this skill shape instead of re-deriving a bespoke structure
> • `hooks/stop.py`: removed `/fin` transcript-detection nudging (`is_fin_text`/`fin_recent`/`mark_fin_seen`/`get_fin_stamp` and their tests) — that discipline now lives in the `fin`/`con` skills themselves, not externally enforced by the stop hook; the hook's unrelated commit-nudge and diary-freshness checks are untouched
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- skills: `con` rewritten twice more — first to a plain 5-step recall-and-resume procedure (dropped the `/fin`-style "NEVER stop early / self-correct harder" coaching that just re-derived fin's job inside con, and the CLAUDE.md constraints restatement), then cut further to match `explore`/`ans`'s actual mode-toggle shape: title, one-line description, short `## Behavior` list. 79 → 40 → 16 lines.
- hooks: `stop.py`'s `/fin`-session-detection logic removed entirely (transcript scanning for `/fin`/`/con` invocation, one-shot-per-session stamp file). This was originally going to be broadened to also detect `/con`, then reconsidered: goal-mode discipline is internal to the skills now, the stop hook doesn't need to know about it at all. `test_stop.py` updated to match (4 tests removed, 3 `emit`-behavior tests kept).

## [v0.3.44] — 20260706

> kronael v0.3.44 — con/fin: separate goal scopes
>
> con and fin are now framed as distinct goal-scoped modes instead of con reading as "fin plus a context-recovery step."
>
> • `con` reframed as goal mode: recall every interrupted/paused/abandoned task, plan, or goal from the session (not just live agent processes) and drive each to actual completion — its own persistence requirement, not borrowed `/fin` semantics
> • `fin` reframed to pair with it: drive the *current* goal to completion, explicitly narrower in scope than `con`'s multi-goal recall
> • mechanics of both skills unchanged — description/intro wording only
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- skills: `con`'s description and intro rewritten to lead with "goal mode" — recall-then-resume across every interrupted/paused/abandoned task or goal this session, not a subordinate mode of `fin`. Step 5 ("Run to completion (/fin semantics)") renamed to "Pursue every recalled goal to actual completion," framed as con's own requirement.
- skills: `fin`'s description updated to pair with con's new framing — "drive the current goal to completion" — and its `NOT for` clause now points at "con, the multi-goal recall mode." Procedure/mechanics unchanged.

## [v0.3.43] — 20260706

> kronael v0.3.43 — sweep audits, /con session resume
>
> Adds two workflow skills: a background bug-category sweep and a session-resume macro.
>
> • new skill `sweep`: dispatches a background audit for one bug CATEGORY across the whole repo, filing each real instance in `BUGS.md` (record-only, never fixes — see CLAUDE.md Bug Triage Protocol)
> • new skill `con`: resumes every interrupted, paused, or unfinished agent and task from the current session, then drives everything to completion (context recovery + `/fin` semantics)
> • de-collided `con`'s "keep going" trigger from `fin`'s pre-existing one — cross `NOT for ...` clauses added to both descriptions, `con`'s `when_to_use` reworded
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- skills: added `sweep` (background agent audits the entire codebase for one bug category and files each real instance as its own `BUGS.md` entry per `/bugs`'s format/ID rules; record-only) and `con` (resumes every interrupted/paused/unfinished agent and task from the current session — memory + diary + in-flight agent inventory — then drives everything to completion under `/fin` semantics). Indexed in `skills/README.md`'s Shortcuts section.
- skills: de-collided `con`'s "keep going" `when_to_use` trigger from `fin`'s pre-existing "keep going" trigger (fin already owns continuing the current in-flight task without stopping; con is specifically about resuming interrupted/paused work). Added cross `NOT for ...` clauses to both descriptions; reworded `con`'s trigger to "resume the paused work".
- `.claude-plugin/plugin.json`: version bump `0.3.33` → `0.3.43` (had drifted since the last bump at v0.3.33; brought back in step with the release version).
## [v0.3.42] — 20260706

> kronael v0.3.42 — pi upgraded to gpt-5.5
>
> The /pi second-opinion agent now defaults to gpt-5.5 instead of the older gpt-5.2-codex.
>
> • pi — default model is now gpt-5.5 (newest served; gpt-5.6 does not exist yet)
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Changed
- pi: default model `gpt-5.2-codex` → `gpt-5.5` — skill doc + `~/.pi/agent/settings.json`.

## [v0.3.41] — 20260706

> kronael v0.3.41 — strict-typing runbook, /pi + /astgrep skills
>
> A new software page pins the linter settings that stop an LLM from typing `Any` past the checker; /pi and /astgrep join.
>
> • strict-typing.md — settings that turn `Any`, `# type: ignore`, `as any` into hard errors (Python + TS)
> • /pi — a second-opinion coding agent, alongside /codex
> • /astgrep — structural (AST) search and rewrite across a codebase
> • model tiers: sonnet = investigation, opus = implementation; /sub auto-picks the tier
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

### Added
- software: `strict-typing.md` — config-only settings that make effective
  typing un-circumventable. Python via basedpyright (`reportAny`,
  `reportExplicitAny`, `enableTypeIgnoreComments = false`) + ruff (`ANN401`,
  `PGH003/004`, `RUF100`); TypeScript via `tsconfig` strict-plus +
  typescript-eslint (`consistent-type-assertions: never`, `no-unsafe-*`,
  `ban-ts-comment`). Escape-hatch→setting tables + residual-holes section.
- pi: `/pi` second-opinion skill (pi coding agent) alongside `/codex`;
  installer provisions pi.
- astgrep: `/astgrep` structural search/rewrite skill; installer provisions
  ast-grep.

### Changed
- skills: model-tier routing — sonnet = investigation, opus = implementation;
  `/sub` auto-tier router with haiku/sonnet/opus proactive triggers.

### Fixed
- pi: auth check no longer treats `settings.json` presence as being logged in.

## [v0.3.40] — 20260703

> kronael v0.3.40 — review give/take router, GitHub/utility skills, hook safety, dockbox 2.1.199
>
> Unifies code review into one give/take router, adds GitHub + utility skills, hardens the hooks, and pins dockbox's Claude Code.
>
> • `/review` is now a give/take router: `review give` produces findings, `review take` applies them — local by default, or a GitHub PR with `gh` (supersedes /code-review for local work)
> • new skills: gh-issue, ans, next, htmx, mk, agent-browser
> • Stop hook: real Stop blocks, the periodic post-tool nudge is advisory; /fin is detected from the command and nags once
> • unsafe-command PreToolUse blockers + Codex self-invocation suppression
> • dockbox pins Claude Code to 2.1.199 — rebuild the image to pick it up
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- skills/review: now a give/take router — `SKILL.md` dispatch + `give.md` (the review engine + a GitHub-PR section) + `take.md` (apply findings from a local list or a PR's comments). `review give [gh]` produces findings; `review take [gh]` applies them; supersedes the built-in `/code-review` for local work. Absorbs the short-lived `gh-review`/`gh-fix` (removed, pruned on reinstall). `gh-comment`/`gh-issue` stay as GitHub primitives.
- skills: added `gh-issue` (file an issue with an approval gate), `ans` (answer-only read-only mode toggle), `next` (park a bug/TODO without stopping), `htmx` (server-rendered HTML + htmx), `mk` (Makefiles), `agent-browser` (browser automation). Indexed in `skills/README.md`.
- skills: removed the inert `requires:` frontmatter field from 8 skills — it is not a real Claude Code field (the engine ignores it; verified against code.claude.com/docs/en/skills). The in-body "read `software/code.md`" pointer is the actual mechanism; fixed `mk`, which pointed at the removed `software-engineering` skill.
- skills: `create-code-presentation` (reveal.js code-talk deck) folded into the `create/` router as `web/code-presentation.md` (no standalone `create-*` dir); org-specific paths genericized. Added to the install prune list.
- skills: rule additions synced from local — `dispatch` gains `sub` triggers, `py` gains a tuple-vs-list rule, `software/code.md` gains a concept-naming rule and a stdout/stderr-only logging rule.
- hooks: synced the installed hook safety work back to source: exact prompt
  routing, Codex self-invocation suppression, command blockers for unsafe shell
  commands, Codex `exec_command`/Claude `Bash` PreToolUse wiring, and tests.
- hooks: restored the installed Stop hook to the v0.3.38 dual-mode behavior:
  real Stop emits top-level `decision: block`; periodic PostToolUse emits
  advisory context only.
- install: drift detection now uses a checksum manifest instead of mtimes, so
  future reinstalls do not silently overwrite installed-side fixes.
- hooks/stop.py: `/fin` is parsed from transcript user messages (an exact `/fin` or its `<command-name>` marker, not a raw substring, so the hook's own "finish mode" wording never re-triggers it) with a per-session one-shot stamp; the transcript tail is read via `deque(maxlen=60)`. Adds `test_stop.py`.
- dockbox: pin `claude-code` to `2.1.199` (was `@latest`). Rebuild the image (`cd dockbox && make image`) to install it.

## [v0.3.39] — 20260703

> kronael v0.3.39 — skills route to the right place
>
> A discoverability pass across the bundle: sibling skills no longer fight over the same trigger words, and the language skills are correctly wired to the shared code baseline.
>
> • go/rs now declare `requires: software` and point at the shared `code.md` baseline (they claimed to, but didn't)
> • De-collided trigger words: wisdom vs scavenge, cto-eval vs hacker-eval, sonnet vs explore
> • hacker-eval and browse keywords moved into `when_to_use` where routing scans them
> • README index: `credits` re-bucketed as ambient context, `code-review` marked built-in
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `go` and `rs` skills now carry `requires: software` plus a body pointer to
  `software/code.md`, matching py/ts/sh/sql; `code.md` no longer claims a
  nonexistent `mk` skill reads the baseline.
- De-collided sibling primary triggers that risked routing races: `wisdom` vs
  `scavenge` ("create a skill"), `cto-eval` vs `hacker-eval` ("audit"), and
  `sonnet` vs the `explore` skill ("explore") — via cross NOT-clauses and
  reworded keywords.
- `hacker-eval` and `browse` moved their retrieval keywords out of
  `description` into `when_to_use` (both fields are scanned, but the split is
  the convention); `resolve` gained a `when_to_use` and a tightened description.
- `skills/README.md` index: `credits` moved from Evaluation lenses to Shared
  references (it's ambient attribution context, not a judgment lens);
  `code-review` annotated as built-in (not in `skills/`); the eval family added
  to the Evaluation-lenses bullet.

## [v0.3.38] — 20260703

> kronael v0.3.38 — demo skill polish
>
> The `demo` skill's cross-references now match the bundle's own conventions.
>
> • demo: NOT-clause points at the `software` skill, not a data file
> • skills index: `demo` listed as a build-task Domain skill, not a Workflow verb
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- `demo` skill: `description` NOT-clause now names the `software` skill slug
  instead of the `software/ci.md` data file, per the wisdom NOT-for convention.
- `skills/README.md`: `demo` moved from the Workflow category (verb-macros) to
  Domain (a build/tooling pattern, alongside `diagrams` and `browse`).

## [v0.3.37] — 20260701

> kronael v0.3.37 — Codex fallback repair stays in the installer
>
> Codex config repair now lives as skill guidance instead of a one-off helper script.
>
> • install: `CLAUDE.md` fallback repair is inline guidance, not a Python helper
> • codex: installers keep `project_doc_fallback_filenames` top-level
> • docs: AGENTS/README/ARCHITECTURE explain the top-level TOML rule
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- install: removed `kronael/install/codex_config_fallback.py`; the installer
  skills now directly say to keep `project_doc_fallback_filenames` top-level.
- codex: bridge-only repair no longer needs source-root discovery just to run a
  config helper; agents edit the TOML key in place.
- docs: AGENTS, README, and ARCHITECTURE keep the top-level TOML warning.

## [v0.3.36] — 20260701

> kronael v0.3.36 — engineering baseline consolidated into the software skill
>
> The language baseline moves into the software router (`code.md`), de-duping always-loaded wisdom; Codex config repair is more robust.
>
> • skills: the code baseline (naming, style, design, boring-code, grug) now lives in `software`'s `code.md`; language skills require it
> • wisdom: dropped the duplicated code philosophy from the always-loaded file — it now points to `software`/`code.md`
> • install: its report names pruned/removed skills so stale-file removal is visible
> • codex: the `CLAUDE.md` config fallback is kept a top-level key in `config.toml`, never buried under a table header
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- skills: folded the `software-engineering` baseline into the `software` router as `software/code.md` (naming, layout, design, boring-code, grug). Language skills (`py`/`ts`/`sh`/`sql`) now carry `requires: software`. The standalone `software-engineering` skill is removed and pruned on reinstall.
- wisdom: the always-loaded global wisdom no longer inlines the code-style/design/philosophy sections (they duplicated the baseline) — it points to `software`/`code.md`. Verified lossless.
- skills: synced back local refinements — Codex-scope search in `recall-memories`, test-typing rules in `testing`/`py`/`ts`, a `pr-draft` GitHub-markdown rule, `gh-comment`'s bare `🤖` prefix, `py` frozen-dataclass rules.
- install: the report step now names every pruned dir/hook so removal of outdated files is visible; the prune list includes `software-engineering`.
- codex: config repair keeps `project_doc_fallback_filenames = ["CLAUDE.md"]` a top-level key in `~/.codex/config.toml` — never appended under a `[table]` header.

## [v0.3.35] — 20260701

> kronael v0.3.35 — dockbox effort/model tuning
>
> dockbox opus now thinks at xhigh, and the sonnet launcher moves to claude-sonnet-5.
>
> • dockbox: `opus` (alias + bare default) now runs at xhigh reasoning effort
> • dockbox: `dockbox sonnet` launches claude-sonnet-5
> • /dispatch help now lists `/sonnet` as medium, matching the sonnet subagent
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- dockbox: the `opus` alias and the bare default inject `--effort xhigh` (was high); the opus subagent was already xhigh, so the launcher now matches it.
- dockbox: `dockbox sonnet` launches `claude-sonnet-5` (was claude-sonnet-4-6). The sonnet subagent stays at medium effort.
- skills: `/dispatch`'s tier hint reads `/sonnet (coding/medium)` — was stale at `high`, now matches `agents/sonnet.md`.

## [v0.3.34] — 20260701

> kronael v0.3.34 — demo recording gets its own skill
>
> Terminal-demo GIF recording moves out of the always-loaded wisdom file into a standalone skill, release respects a project's own release rules, and Go gets error-suppression guidance.
>
> • New `/demo` skill: asciinema + agg recipe for README demo GIFs
> • `/release`: reads a project's `CLAUDE.md` `## Release` section as an override before running defaults
> • Go: explicit rules for suppressing errors with `_ =` and `//nolint:errcheck`, always with a reason
>
> Full notes: github.com/kronael/tools/blob/master/CHANGELOG.md

- Added `skills/demo/SKILL.md`: a flat, directly-invocable skill for recording
  terminal demo GIFs (`asciinema` → `.cast` → `agg` → `.gif`), with the
  Makefile-target recipe pulled from `rig/Makefile`.
- Removed the `make demo` targets rule from the global wisdom file
  (`skills/global/SKILL.md`) — it was too niche to load into every session;
  it now lives only in the `demo` skill.
- `/release` gained a step 0: read the project's `CLAUDE.md` for a
  `## Release` section and apply any overrides (skip tagging, custom
  checklist, pinned version file) before running the default process.
- `go` skill: new Error Suppression section — intentionally dropped errors
  must carry an explicit reason (`_ =` with a comment, or
  `//nolint:errcheck` with the reason above it), never a bare linter-config
  exclusion for a specific call site.

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
> • `output-styles/caveman.md` added; activated in settings-recommended.json
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
- Added `output-styles/caveman.md` (stripped-not-broken output style);
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
