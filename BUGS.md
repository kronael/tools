# BUGS

## Bundle

- **RECALL-UNREADABLE-TRANSCRIPT** (MED, correctness) — CONFIRMED 2026-10-06.
  `skills/recall-memories/recall.py` `read_records` (~250) opens every
  transcript under `~/.claude/projects/` and lets a `PermissionError` escape:
  one unreadable file kills every `results` search, scoped or `-a`. Here it is
  `~/.claude/projects/-/399a5e4c-d151-43d2-8aeb-292ba1c6b8a1.jsonl`, in a
  root-owned dir a session run as root from `/` left.
  Reproduce: `python3 ~/.claude/skills/recall-memories/recall.py results -t
  Agent 'NEEDS TELLING'`. **Fix:** skip the file with one stderr line naming it.

- **PROMPT-NUDGE-ORACLE-WORD-SKIPS-DISPATCH** (LOW, hooks) — CONFIRMED at
  HEAD 2026-10-06. `hooks/prompt_nudge.py` sends any prompt with
  the bare word `oracle` or `second opinion` to `/astra`
  (`CODEX_PATTERNS`, `:90-94`), and checks those patterns before the
  escalation ones (`:133-136`).
  So `oracle: review this diff for bugs` skips `skills/oracle/SKILL.md`'s
  table, which sends code and plan critique to fable, and `use opus for a
  second opinion` loses the requested model. **Proposal:** route `oracle` and
  `second opinion` to `/oracle`, keep `ask codex`/`ask astra` on `/astra`, and
  test the escalation patterns first. No test yet — needs sign-off.

- **SYNC-CDPATH-NO-OPT-OUT** (LOW, design) — proposed. `kronael/sync`
  step 8 writes the CDPATH block on every sync (`SKILL.md` step 8,
  `reference.md` CLI tools table "always"), so a block the owner deleted
  comes back without a question. **Proposal:** skip the write when the
  first-sync answer declined CLI tools, recorded in the manifest. No test —
  design.

- **REFINE-PUBLIC-REPLIES-EXCEED-LOCAL-SCOPE** (MED, design) — proposed,
  needs sign-off. Step 5 of `skills/refine/SKILL.md:73-82` skips unless an
  open PR whose head is an ancestor of HEAD exists, and step 11
  (`:138-145`) already posts each reply through `gh-comment`'s sign-off gate.
  The gap: while such a PR is open, step 11's completion line (`:159-161`)
  needs every unfixed triaged thread replied to, so refine cannot complete
  for a local-only delivery unless the owner approves or declines the
  replies. **Proposal:** let a reply the owner declined, or a delivery the
  owner kept local, close step 11 as an outstanding thread action listed in
  the report. Keep approval gates in `gh-comment`. No new review mode,
  skill, saved plan or hook. No test — design.

- **GLOBAL-AGENT-CAP-NAMES-THREE-TYPES** (LOW, design) — owner decision.
  `skills/global/SKILL.md:180-182` caps `sonnet`, `fable` and `opus` subagents
  by `subagent_type`; the bundle also launches `general-purpose`
  (`skills/dispatch/SKILL.md:8`, `skills/sweep/SKILL.md:25`), `Explore`
  (`skills/sweep/SKILL.md:17`, `skills/scavenge/SKILL.md:62`,
  `skills/recall-memories/SKILL.md:161`) and the thin
  skill agents — `improve` pins Sonnet 5.5 (`agents/improve.md:3`), the rest
  inherit the parent's model — none of which the cap names. **Options:**
  (a) count a sub under the model it runs on (`improve` as `sonnet`,
  `general-purpose` as the parent's model); (b) count only the three named
  types. **Default if nothing is decided:** (a). No test — design.

- **REFINE-STEP11-REMOVES-OTHER-TASKS-WORKTREE** (MED, design) — owner
  decision. `skills/refine/SKILL.md:146-155` removes every worktree after the
  first whose HEAD is on a remote-tracking ref and whose status is clean,
  whoever made it; `skills/worktree/SKILL.md:57` says "NEVER remove another
  task's worktree". A clean checkout at a pushed commit that another session
  is about to use goes under the first rule and is protected by the second.
  **Options:** (a) step 11 removes only worktrees this run created, listing
  the rest; (b) `worktree` allows removing an integrated, clean worktree.
  **Default if nothing is decided:** step 11 as written. No test — design.

- **CODE-RUN-WRAPPER-VS-PREDICATE-PREFIX** (LOW, docs) — owner decision.
  `skills/software/code.md:14-17` names a function wrapping one external
  command `run_<command>`; `:10-13` names a predicate `is_`/`has_`/`can_`/
  `should_`. A bool-returning wrapper (one around `git diff --quiet`) is
  claimed by both and neither states precedence. The bundle's own wrappers
  follow neither: `hooks/stop.py:19` `git_run()`, `hooks/pretool_nudge.py:202`
  `format_markdown()`, `lints/check.py:59` `matches()`,
  `skills/recall-memories/recall.py:899` `git()`. **Options:** (a) the
  predicate prefix wins and the body says which command runs; (b)
  `run_<command>` wins and returns the result, a predicate wraps it.
  **Default if nothing is decided:** (a). No test — docs.

- **RELEASE-FULL-DETAIL-VS-100-CHAR-BULLET** (LOW, docs) — owner decision.
  `skills/release/SKILL.md:110-111` makes every Pass B bullet one sentence of
  at most 100 characters; `:116-118` says to preserve security fixes, breaking
  changes, env renames and schema migrations "at full detail (never trim)". A
  breaking change whose migration needs two sentences cannot satisfy both.
  **Options:** (a) the preserve list is exempt from the cap; (b) the cap holds
  and the detail goes to a `### Operator note`. **Default if nothing is
  decided:** (b). No test — docs.

- **SOCIAL-REFS-NARRATE-HISTORY** (LOW, docs) — CONFIRMED at HEAD
  2026-10-06. `skills/create/social/references/codex-critique.md:3` frames the
  file as a "Raw adversarial pass by codex-cli 0.144.4" over an earlier draft
  of `research-social-meme.md`, whose § Where the SKILL departs from this
  research (`research-social-meme.md:196-223`) states the outcome as it stands.
  The critique is the prior-version record the wisdom file bans in permanent
  content, kept as a cold provenance file nothing reads by accident. **Fix:**
  the maintainer's call — keep it as attribution, or move it to `.diary/`;
  no test — docs.

- **DIAGRAMS-NO-SEQUENCE-SWIMLANE-STATE** (LOW, design) — open (record only).
  `skills/diagrams/SKILL.md` (52 lines) teaches only box-and-arrow component
  layout. It carries no pattern for the three other shapes that come up
  constantly: sequence (message order and who waits), swimlane (step ownership
  and the handoffs between actors), and state (the legal transitions of one
  entity). Each needs its own ASCII template plus a one-line rule for when to
  reach for it, in the same shape as the existing layout pattern. Reproduce:
  `grep -i 'sequence\|swimlane\|state' skills/diagrams/SKILL.md` → no hits.

- **BOX-HAIKU-ALIAS-VS-BATCH-ONLY** (LOW, design) — owner decision, no test —
  design. `skills/global/SKILL.md` § Agents makes Haiku batch-only, NEVER a
  sub, while `dockbox haiku` (`dockbox/dockbox:412`) and `qemubox haiku`
  (`qemubox/qemubox:1104`) start an interactive Claude Code session on
  `claude-haiku-4-5-20251001`; `tests/drift_test.sh:22` and
  `qemubox/test-parity.sh:8` pin the alias in both. **Options:** (a) drop the
  `haiku` alias from both launchers, their usage text, qemubox's README and
  the two tests; (b) keep it as a typed model flag the rule does not govern —
  the user picks it, no skill routes to it. **Default if nothing is
  decided:** (b).

- **BUGS-SIGN-OFF-ENTRIES-PREDATE-OPTIONS** (LOW, docs) — owner decision, no
  test — docs. `skills/bugs/SKILL.md` § Entry format requires `**Options:**`
  and `**Default if nothing is decided:**` on every entry whose status is
  `needs sign-off`; the entries in this file with that status predate the
  rule — none carries a default, and only `LINT-PACK-NOT-INSTALLABLE`
  sketches options. **Options:** (a) backfill each entry when its subject is
  next touched; (b) backfill them all in one pass; (c) grandfather them.
  **Default if nothing is decided:** (a).

- **SYNC-OLD-MANIFEST-KEYS** (LOW, correctness) — CONFIRMED 2026-10-05. A
  manifest the install step wrote keys `files` by bare path (`CLAUDE.md`,
  `skills/commit/SKILL.md`); § Classify and § Merge look up
  `.claude/<path>` (`kronael/sync/reference.md` § Classify). On the first
  sync over such a manifest every live-edited file reads `no-base` (43 on
  this host) instead of `edited`/`both`, and step 2 asks about each. Swap
  rewrites the manifest with prefixed keys, so it bites once per host.
  **Fix:** read both key forms in § Classify and § Merge, or rewrite the keys
  in step 0.
- **SYNC-JUNK-NAMED-KEPT-SYMLINK** (LOW, correctness) — CONFIRMED 2026-10-05.
  `keep.expand` keeps a symlink named like junk (`hooks/__pycache__`,
  `skills/.claude`); § Classify counts it `junk` and prints no `shadow`, but
  § Swap runs its shadow check on it and refuses (`kept ['hooks/__pycache__']
  shadow the source`) whenever the source tree holds that cache dir. Classify
  exits 0 and step 3 has nothing to settle. Reproduce: scratch HOME,
  `ln -s <dir> ~/.claude/hooks/__pycache__` with `hooks/__pycache__` in `SRC`.
  **Fix:** have `expand` skip junk names, so both readers agree.
- **SYNC-MANIFEST-SYMLINK-UNREPORTED** (LOW, correctness) — CONFIRMED
  2026-10-05. A symlinked `~/.claude/kronael-install-manifest.json` passes
  § Classify (it reads through the link and prints no `SYMLINK`), while § Swap
  refuses with `live ['kronael-install-manifest.json'] are symlinks (Classify:
  SYMLINK)` — citing a line Classify never printed. **Fix:** add the manifest
  to the roots § Classify checks with `os.path.islink`.

- **LINT-PACK-NOT-INSTALLABLE** (MED, design) — needs sign-off. The lint pack
  (`skills/<lang>/lints/`, aggregated by `sgconfig.yml`, proven by
  `make lints`) enforces code rules only in THIS repo. Getting it into a user's
  project is a new install contract. Options: **A (recommended)** an
  opt-in install step — "wire kronael lints into this repo?" writes/updates the
  project's `sgconfig.yml` + `.pre-commit-config.yaml` and references the pack,
  matching the opt-in-skills posture; **B** publish the pack as a standalone
  `pre-commit` repo referenced by URL; **C** document a `sgconfig.yml`
  reference only, no installer. Also: CI enforcement here needs an
  ast-grep-provisioned job (`make lints` is not in pre-commit because the lint
  CI runner has no ast-grep).

- **COMMIT-EVALS-BRACKET-FORMAT** (LOW, docs) — CONFIRMED at HEAD 2026-09-25.
  `evals/commit/0[1-5].json` `must_use_format` expects `[fix] …`-style
  subjects (`01.json:13`, `03.json:18`), and `research/eval-sets.md:196`
  shows the same, while `skills/commit/SKILL.md:33` prescribes
  `type(scope): …`. A run scores a skill-compliant commit as a format
  failure. **Fix:** rewrite the regexes and rubric lines to the
  `type(scope):` form; no test — docs.

- **LANG-SKILLS-RESTATE-COLD-RUNBOOKS** (LOW, duplication) — owner decision,
  no test — duplication. Hot `SKILL.md` bodies restate rules a cold
  `software/` runbook owns: `skills/py/SKILL.md:121-123,130,132-137`
  (`strict-typing.md` one mode, `ci.md` `python -m pytest`, `testing.md`
  fixtures and doubles), `skills/go/SKILL.md:38-39,42,147,151`
  (`strict-typing.md` linters, `dynamic-analysis.md` `-race`, goleak,
  govulncheck), `skills/rs/SKILL.md:74-76,85,137` (`testing.md`, `cli`,
  `dynamic-analysis.md` miri). `skills/software/SKILL.md:29` says NEVER
  duplicate the runbooks into language skills; the copies are what a session
  sees without a dispatch. **Options:** (a) cut each to a pointer; (b) keep
  the hot summaries and let `software/SKILL.md:29` allow a one-line summary.
  **Default if nothing is decided:** (b).

- **SKILLS-DISAGREE-ON-MAKE-TARGETS-AND-FORMATS** (LOW, docs) — owner
  decision, no test — docs. Four canonical Make target sets:
  `skills/software/ci.md:47-48` (prepare, build, test, right, image, clean),
  `skills/mk/SKILL.md:71-78` (prepare, check, right, test, integration,
  clean), `skills/ts/SKILL.md:120-121` (prepare, check, right, test), WISDOM
  § House conventions (test, test-all, smoke); `ci.md:44` "NEVER add a
  `lint` target" vs `ops:48`, `mk:76,86`, `py:125`, `ts:120`; `ci.md:50`
  sets `PYTHONPATH` per target, `py:131` once. Log line:
  `software/observe.md:5` (`[LEVEL] key=value`) vs `software/code.md:183`
  (`INFO subsystem: message`); health: `service:12` (`/health`, `/ready`)
  vs `observe.md:12` (`/.well-known/live`); Python: `py:19` 3.13+ vs
  `strict-typing.md:43` 3.12; aliasing: `py:93-94` allows `heapq_merge` on
  a collision vs `code.md:26-28` NEVER rename. **Options:** one owner per
  fact, the rest point. **Default if nothing is decided:** `code.md` and
  WISDOM win where they speak; the rest stays until picked.

- **SKILLS-RETRY-LOOPS-VS-FAIL-LOUD** (LOW, design) — owner decision, no
  test — design. `skills/rs/SKILL.md:101-122` prescribes a `main()` loop
  that sleeps and restarts on any `Err`; `skills/service/SKILL.md:14` says
  "use last available data when current unavailable"; `skills/data/SKILL.md:44`
  "Retry with exponential backoff" — WISDOM § System-change discipline
  retries ONLY the transient. **Options:** (a) scope each to transient
  errors; (b) state the supervised-binary exception in `rs`. **Default if
  nothing is decided:** (b).

- **SOLANA-DEPS-VERSIONS-STALE** (LOW, docs) — CONFIRMED 2026-10-10, no test
  — docs. `skills/solana/deps.md:12` calls anchor-lang 1.1.2 the newest
  release and `:22` solana-pubkey 4.3.0; the crates index lists 1.2.1
  (depending on `solana-pubkey` v3 and v4) and 4.4.0, and `:118-121` rests
  on the 1.1.2 claim. `skills/solana/layout.md:123` is "verified at cargo
  1.97.1". **Fix:** re-verify each pin against the index and the toolchain.

- **README-ROUTER-CONTRADICTS-ITSELF** (LOW, docs) — owner decision, no test
  — docs. `skills/readme/sync.md:56` puts an "Architectural Decisions"
  section in ARCHITECTURE; `skills/readme/topology.md:104` says NEVER
  record a decision there. `sync.md:24-48` and `topology.md:43-57` give two
  README section orders. `skills/release/library.md:115` wants README line 2
  "technical"; `sync.md:26-28` "a 13-year-old understands". **Options:**
  (a) topology owns layout and order, sync points; (b) sync owns. **Default
  if nothing is decided:** (a).

- **RELEASE-TAG-COLLISION-RULES-CONFLICT** (LOW, docs) — owner decision, no
  test — docs. `skills/release/SKILL.md:151-153` bumps past an existing tag,
  `:154-157` deletes and re-tags it, and `skills/merge/SKILL.md:22-24` never
  re-points a colliding tag. **Default if nothing is decided:** bump past —
  re-pointing a pushed tag is the failure.

- **SECOND-OPINION-ROUTING-SPLIT** (LOW, docs) — owner decision, no test —
  docs. `skills/astra/SKILL.md:14-16` allows direct use only on request or
  via `oracle`, but `skills/release/SKILL.md:34` and
  `skills/scavenge/SKILL.md:56,75,132` call astra directly; `oracle` never
  routes to `pi`; `astra`, `pi` and `oracle` share the triggers "second
  opinion", "sanity check" and "disagreement after reasoning"
  (`skills/wisdom/SKILL.md:48` forbids a shared primary trigger);
  `skills/terra/SKILL.md:24-27` requires `--sandbox read-only` outside
  dockbox while `astra:29,57` always bypasses the sandbox. **Default if
  nothing is decided:** as written.

- **SCAVENGE-OUTPUTS-CONTRADICT-BUNDLE-RULES** (LOW, design) — owner
  decision, no test — design. `skills/scavenge/SKILL.md:25-26,136-138`
  writes new skills and agents into `~/.claude/` (an install of this repo,
  WISDOM § Environment); `:66,79,178` put research and critiques under
  `<cwd>/docs/<topic>/` (`skills/readme/topology.md:95-96` bans work records
  in `docs/`); `skills/scavenge/shapes.md:38-55` is a content-bearing agent
  skeleton (`skills/CLAUDE.md:119` forbids one). **Default if nothing is
  decided:** as written.

- **EVAL-DOGFOOD-REPORTS-ARE-WORK-RECORDS** (LOW, docs) — owner decision, no
  test — docs. `skills/eval/design/dogfood-glass.md:16,110-114` and
  `dogfood-term.md:113-116` carry dated outcomes and shortened hashes
  (`cfecd8c`, `0c16126`; WISDOM § Documentation wants them full);
  `skills/eval/novice.md:6-7,184-186` names its scavenge provenance and
  `oracle-critique.md` files that `scavenge:79` writes as
  `astra-critique.md`. **Options:** (a) move the reports to `.diary/`; (b)
  genericise; (c) keep. **Default if nothing is decided:** (c).

- **RECLAUDE-TMP-BAN-VS-SYNC-RUN-DIR** (LOW, docs) — owner decision, no test
  — docs. `RECLAUDE.md:4` "NEVER use `/tmp` — ALWAYS `./tmp`" is re-injected
  at compaction; `kronael/sync/SKILL.md:34` puts the run dir under
  `${TMPDIR:-/tmp}` by design. **Default if nothing is decided:** the sync
  rule wins inside a sync; RECLAUDE scopes project work.

## Codex bridge

- **CODEX-SKILL-SIGIL-AT-VS-DOLLAR** (LOW, docs) — owner decision, no test —
  docs. Codex's own skill instructions say a user names a skill "with
  `$SkillName` or plain text" (the `codex` 0.162.0 binary's prompt text),
  and `plugins/kronael/.codex-plugin/plugin.json` `defaultPrompt` uses
  `$kronael-sync`; the bundle writes `@skill-name` everywhere else
  (`README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `kronael/sync/reference.md`
  § Codex bridge, `hooks/README.md`, `hooks/ARCHITECTURE.md`) and
  `hooks/codex_hook.py:124` rewrites `/skill` to `@skill`. Both forms loaded
  the `refine` skill in an ephemeral Codex session on 2026-10-10, so `@` works
  through the plain-text path. **Options:** (a) switch the docs, the rewrite
  and `hooks/test_codex_hook.py:91` to `$`; (b) keep `@`. **Default if nothing
  is decided:** (b).

- **CODEX-PRECOMPACT-ENTRIES-NO-OP** (LOW, config) — owner decision, no test
  — config. `codex-hooks.json:58-74` wires `local` and `reclaude` on Codex
  `PreCompact`, but `hooks/codex_hook.py:155-162` returns nothing for any
  non-block PreCompact output, so both entries spawn a process whose output is
  discarded; the only effect left is `local.py`'s `local-{sid}` stamp.
  **Options:** (a) drop the two entries; (b) keep them for when the adapter
  can carry context. **Default if nothing is decided:** (b).

## Hooks

- **PROMPT-NUDGE-FIRST-KEYWORD-WINS** (MED, correctness) — needs sign-off.
  `explicit_route` returns the route of the first `SKILL_KEYWORDS` word in
  prompt order. Measured over every session transcript (2026-09-05): of 51
  user-typed prompts that say "ship it" / "and ship" / "then ship" / "ship the
  …", 18 routed to `/ship` and 30 elsewhere, most often `/specs` (7),
  `/fable` (6) and `/fix` (4), because an earlier word matched.
  "spec this and build it" is in ship's own `when_to_use` and still routes
  `/specs`. Reproduce: `echo '{"prompt":"spec this and ship it"}' | python3
  hooks/prompt_nudge.py`. **Fix:** a precedence rule (workflow verbs before
  nouns, or all matches listed) — a routing redesign.

- **LEARN-HOOK-WIRED-NOWHERE** (LOW, dead code) — CONFIRMED at HEAD 2026-09-25.
  `hooks/learn.py` is a complete lifecycle hook that no event invokes:
  `settings-recommended.json` wires `local.py`, `prompt_nudge.py`,
  `pretool_nudge.py`, `post_tool_nudge.sh`, `stop.py`, `memory_nudge.py` and
  `reclaude.py`, and none of them is it. Reproduce:
  `grep -c learn.py settings-recommended.json` → 0. **Fix:** the maintainer's
  call — wire it to an event, or drop it.

- **SMOKE-SUITE-TESTS-THE-INSTALL** (LOW, tests) — CONFIRMED at HEAD 2026-09-25.
  `hooks/test_hooks.py` resolves its subjects under `Path.home()/'.claude'/
  'hooks'` (`:20`), so it exercises whatever is installed rather than the tree
  it ships in, and its docstring and cases name `nudge.py`, which no longer
  exists — the file split into `prompt_nudge.py` and `pretool_nudge.py`. It is
  also absent from the Makefile's `TEST_FILES`, and pytest collects nothing from
  it (`pytest -q test_hooks.py` → "no tests ran"), so nothing runs it either
  way. Reproduce: `ls hooks/nudge.py` → no such file. **Fix:** the maintainer's
  call — point it at the repo tree and rename the subjects, or drop it.

- **HOOKS-SYSTEMMESSAGE-NEVER-REACHES-MODEL** (MED, correctness) — CONFIRMED.
  `local.py`, `reclaude.py` and `memory_nudge.py` emit `systemMessage`, the
  channel defect `prompt_nudge` had. `hook_system_message` maps to no API
  message in Claude Code 2.1.261 (`hook_system_message:()=>[]` in the
  attachment table; the docs define `systemMessage` as "a message shown to the
  user in the transcript"). Measured: 2409 `hook_system_message` attachments
  across all transcripts, 0 model-visible copies. So `local.py`'s LOCAL.md
  injection and its RULES re-injection on UserPromptSubmit never reach the
  model. The PreCompact paths (`local.py`, `reclaude.py`, `memory_nudge.py`)
  are the same field; whether Claude Code carries a PreCompact `systemMessage`
  across compaction is not measured. **Fix:** for UserPromptSubmit,
  `hookSpecificOutput.additionalContext` as in `prompt_nudge.emit`; PreCompact
  needs its own measurement first.

- **STOP-CLAUDE-EVAL-NO-PRODUCER** (LOW, config) — needs sign-off.
  `hooks/stop.py:171` suppresses the commit/diary block when `CLAUDE_EVAL` is
  set. Nothing sets it: its other hits are `hooks/test_stop.py:16`, which
  strips it from the test env, and `hooks/ARCHITECTURE.md:208,213`, which
  documents the clause — none in `Makefile`, `.github/`, `evals/`, or any
  `settings*.json` env block. Effect is the opposite of the intent: eval runs
  get the block messages injected into their transcripts. **Fix:** one line
  either way — set it in the eval runner, or delete the clause — but which
  one is a scope call; no test — config.

- **HOOK-STATE-STAMPS-ACCUMULATE** (LOW, design) — needs sign-off. Four
  stamps per session are named at their call sites — `local-`
  (`local.py:36`), `solve-nudge-` (`prompt_nudge.py:150`),
  `memory-nudge-start-` and `memory-nudge-done-` (`memory_nudge.py:105-113`)
  — plus a second per-session store `pretool_nudge.py:285-292` keeps at
  `~/.claude/tmp/extnudge/{sid}.txt`, and no hook deletes one or expires a
  session id, so `~/.claude/state` gains up to four files per session.
  Harmless in bytes; the question is whether stamps should self-prune on
  write past N days. **Options:** (a) prune on write past N days; (b) leave.
  **Default if nothing is decided:** (b). No test — design.

- **STOP-DUPLICATES-HOOK-EVENT-READER** (LOW, duplication) — CONFIRMED at HEAD
  2026-09-29. `hooks/stop.py:81-89` defines its own `hook_event`: the same
  three-key loop as `hooks/lib/state.py:33-42`, behind a `KRONAEL_HOOK_EVENT`
  override (`:82-84`, set by `post_tool_nudge.sh:20`). `stop.py` imports
  nothing from `lib.state`, so a spelling added to one reader misses the
  other. **Fix:** import `hook_event` from `lib.state` and keep the override
  in `stop.py`, or fold the override into the shared reader; no test —
  duplication.

- **SKILL-LINT-WRITE-LANDS-OUTSIDE-THE-COMMIT** (MED, design) — proposed. The
  pre-commit entry (`.pre-commit-config.yaml:11`) runs
  `hooks/skill_frontmatter_lint.py --write --fail-on-write` over every staged
  `.md`, and `skill_files()` maps a sibling to the `SKILL.md` that owns it, so
  a commit that stages only `skills/x/data.md` can rewrite `skills/x/SKILL.md`,
  a file it never staged. The run exits 1 and prints `fixed:`, so it is loud,
  but the write lands in the working tree outside the commit. **Proposal:**
  repair only the paths the caller named and report, never write, an owner
  reached through a sibling. Changes the `--write` contract — needs sign-off;
  no test — design.

- **SKILL-LINT-PRE-COMMIT-SCANS-HIDDEN-DIRS** (LOW, design) — proposed.
  Pre-commit hands the scan every staged `.md` (`files: \.md$`), so it reaches
  the 21 tracked `.diary/*.md`, while `make skills-frontmatter` and CI walk the
  tree through `visible_files()`, which skips hidden directories. The two
  scopes disagree on a real file: `.diary/20261007.md` quotes an illustrative
  home path with a two-segment account name at `:19` and `:99`, so `python3
  hooks/skill_frontmatter_lint.py .diary/20261007.md` exits 2 with two
  `skill-local-path` findings while the tree target passes; `/.diary/` is
  gitignored, so pre-commit meets the file only when it is force-added, and a
  tracked diary that quotes such a path blocks its commit while the tree
  target and CI stay green.
  **Proposal:** one scope for both — the script drops hidden paths it is
  handed, or the pre-commit pattern excludes them. Changes the scan's input
  contract — needs sign-off; no test — design.

- **LINT-CI-DISPATCH-EMPTY-REFS** (LOW, config) — CONFIRMED 2026-10-07.
  `.github/templates/lint.yml.tmpl` passes
  `--from-ref ${{ github.event.pull_request.base.sha || github.event.before }}`
  and the matching `--to-ref` to pre-commit; on `workflow_dispatch` both are
  empty, and `pre-commit run --from-ref --to-ref HEAD` exits 2 with "expected
  one argument", so a manual run fails before any hook. **Fix:** drop
  `extra_args` so every trigger runs `--all-files` (`pre-commit run
  --all-files` passes at HEAD 2026-10-10), or drop the trigger.

- **GH-GATE-READS-DIRECT-GH-ONLY** (LOW, hooks) — CONFIRMED at HEAD
  2026-10-08. `hooks/gh_text_lint.py` `GH` matches a `gh` word at the head of
  a command segment, after `VAR=value` assignments and one wrapper (`env`,
  `timeout`, `sudo`, `command`, a path). `bash -c 'gh pr create ...'`,
  `g=gh; $g pr create ...` and `xargs gh pr create` post without a check.
  No proposal: each is a way around the gate an agent has to choose, and a
  shell parser is the wrong size for a hook.

- **GH-LINT-FLAGS-RANGES-AND-FLAG-NAMES** (LOW, hooks) — CONFIRMED at HEAD
  2026-10-08. `SHORTENED` in `hooks/gh_text_lint.py` reads a git range
  `c98c2da...c1bcf64` as a shortened hash, and `MARKETING` reads the flag
  name in "drop the `--robust` flag" as a marketing word, so a comment or
  body naming either is refused with the wrong reason. **Proposal:** skip a
  match inside backticks. No test yet.

- **PRETOOL-IMPORTS-OUTSIDE-SUPPRESS** (LOW, hooks) — CONFIRMED at HEAD
  2026-10-08. `hooks/pretool_nudge.py:16-17` imports `gh_text_lint` and
  `lib.state` at module level, outside the `suppress(Exception)` around
  `main()`. An install that lacks either file, or `python3 -I`, tracebacks on
  every tool call and no
  unsafe-command block fires (exit 1, shown to the user, not blocking). Same
  shape as the `lib.state` imports in `local.py` and `memory_nudge.py`;
  `hooks/ARCHITECTURE.md` § lib states the install contract.

- **GH-GATE-REGEX-SHELL-PARSE** (MED, design) — proposed, needs sign-off.
  `hooks/gh_text_lint.py` reads the command with regexes (`GH`, `QUOTED`,
  `BODY_TEXT`, `BODY_FILE`, `HEREDOC`, `JSON_BODY`), so its parse and bash's
  disagree. Measured at 63ad23b. Posts unchecked: `gh pr edit 5 -b"…"` (the
  attached flag; a required kind is refused as body-not-found instead),
  `--body "…""…"` adjacent strings (only the first is read), `--body "🤖
  $BODY"` (the shell expands it after the lint), `--input` JSON with
  `{"body":""}` (empty bodies are skipped — the review-submit event needs it)
  or a `body` key, `gh api -X PATCH …/pulls/1 -f "body=…"` (quoted key),
  and `gh pr close`/`gh issue close --comment "…"` (not in `POSTS`). Refused
  wrongly: `printf 'x; gh pr create --fill'` (a `;` inside quotes opens a
  segment), `--body '🤖 Run $(make test)'` (single quotes never substitute),
  `-F "per_page=5"` read as a body file (a quoted key fails the `[\w-]+=`
  lookahead) — a GET `search/issues` whose query names `pulls/5` is allowed
  on its own and becomes a false block the moment such a `-F` follows — and a
  `<<\EOF` heredoc (`HEREDOC` accepts only `'`/`"` quoting) whose contents
  are read as commands. **Options:** (a) split segments and tokenize each
  with `shlex`, then read flags from tokens; (b) keep the regexes and add a
  case per miss. **Default if nothing is decided:** (a). No test — design.

- **PRETOOL-UNSAFE-SCAN-READS-QUOTED-TEXT** (LOW, design) — the maintainer's
  call. `unsafe_command_reason` (`hooks/pretool_nudge.py:136-142`) runs
  `UNSAFE_COMMAND_PATTERNS` over the whole command text, so a commit message
  that names a blocked command is blocked as that command: `git commit -m
  "docs: record the gh release create ask entry"` → `gh release create`, and
  `git commit -m "docs: never killall by name"` → `killall` (measured at
  63ad23b). Masking heredocs before the scan would let `bash <<EOF` through,
  and the `Co-Authored-By` pattern (`:28`) must keep reading the message, so
  the scope is a judgment call. Also `settings-recommended.json:23` keeps a
  `Bash(gh release create*)` `ask` entry for a command the hook denies first
  (`:33`), so that ask never fires. **Options:** (a) skip quoted text for the
  patterns that name a bare command, and drop the dead ask entry; (b) leave
  both — phrase commit messages around the words. **Default if nothing is
  decided:** (b). No test — design.

- **SKILL-LINT-PATH-TOKEN-SKIPS-SPACED-NAMES** (LOW, correctness) — CONFIRMED
  at 63ad23b. `PATH_TOKEN` (`hooks/skill_frontmatter_lint.py:72`) admits only
  `[\w.-]` and `/` in a written path, so a sibling named `user guide.md` or
  `guide(v2).md` is named by no token, and `check_reachable` (`:344`) reports
  it as a `skill-orphan` however SKILL.md spells it. Measured:
  `hooks/test_skill_frontmatter_lint.py::test_named_sibling_with_a_space_or_parens_is_reachable`.
  **Fix:** search the text for each doc's own name forms instead of
  tokenizing the text.

- **SKILL-LINT-LOCAL-PATH-EXEMPTS-MACOS-ACCOUNTS** (LOW, correctness) —
  CONFIRMED at 63ad23b. `LOCAL_PATH` (`hooks/skill_frontmatter_lint.py:79`)
  applies the `dockbox`/`claude` container-HOME exemption under `/Users/` as
  well as `/home/`, so the macOS account paths `/Users/claude/x` and
  `/Users/dockbox/x` pass the leak scan; the container HOME is only ever
  under `/home/`. Measured:
  `hooks/test_skill_frontmatter_lint.py::test_leak_scan_flags_a_macos_account_named_like_the_container`.
  **Fix:** exempt the two names under `/home/` only.

- **GH-LINT-DISTILL-COUNTS-THE-TITLE** (LOW, correctness) — CONFIRMED at
  63ad23b. `lint` (`hooks/gh_text_lint.py:213`) flags `DISTILL cut nothing`
  only when the body is at least as long as the whole draft, and pr-draft
  step 2 writes the title into `tmp/pr-draft.md` above the body, so a body
  the cut left untouched passes by the title's length:
  `lint(Kind.PR, body, draft='fix: X\n\n' + body)` → `[]`. Measured:
  `hooks/test_gh_text_lint.py::test_lint_pr_draft_ratio_ignores_the_draft_title`.
  **Fix:** compare against the draft below its title line, or require a
  real cut ratio (the `ok:` line already prints one).

- **STYLE-RULES-NUDGE-RESTATES-CAVEMAN** (LOW, duplication) — owner
  decision, no test — duplication. `hooks/prompt_nudge.py:9-15`
  `STYLE_RULES` is emitted on every prompt (`:204`, meta prompts too,
  `:190`) and restates `output-styles/caveman.md` with one line cap (~17,
  max 20) where caveman has tiers (`:15`) and "no tables or headers" where
  caveman allows them for tabular content (`:26`); neither `hooks/README.md`
  nor `hooks/ARCHITECTURE.md` names it. `COMMIT_RULES` (`:21-27`),
  `stop.py:124-132` and `local.py:11-16` `RULES` restate WISDOM § Git and
  `code.md`. **Default if nothing is decided:** as written — the nudges are
  deliberate re-injection.

- **RECLAUDE-KEYWORD-PATH-UNWIRED** (LOW, dead code) — CONFIRMED 2026-10-10.
  `hooks/reclaude.py:33-41` carries a continue/recap keyword path (the same
  two regexes as `local.py:61-62`); the wiring runs the hook on PreCompact
  only (`settings-recommended.json`, `codex-hooks.json`), no test names the
  path, and `hooks/ARCHITECTURE.md` says it is unwired. **Fix:** the
  maintainer's call — delete it with the ARCHITECTURE lines, or wire it.

- **HOOKS-ENV-NAMES-UNDOCUMENTED** (LOW, docs) — CONFIRMED 2026-10-10, no
  test — docs. `KRONAEL_IN_CODEX` is stripped in `hooks/test_stop.py:16` and
  read by no hook; `KRONAEL_CODEX_HOOK_DEBUG` (`codex_hook.py:111`) and
  `KRONAEL_HOOK_STATE` (`lib/state.py:10`) appear in no doc. **Fix:** drop
  the first; name the other two in `hooks/ARCHITECTURE.md`.

- **CI-SKIPS-RECALL-LINTS-AND-SKILL-DRIVEN-HOOK-TESTS** (LOW, config) —
  CONFIRMED 2026-10-10, no test — config. No workflow runs
  `skills/recall-memories/test_recall.py`, `make lints` or `make spec-lint`
  (`grep -rn recall .github` is empty); `test-hooks.yml` triggers on
  `hooks/**` only while `hooks/test_prompt_nudge.py:40,48` reads
  `skills/*/SKILL.md`, so a push touching only `skills/` skips it. **Fix:**
  add the three to `lint.yml.tmpl` and `skills/**` to the hooks path filter.

- **AGENTS-TASK-IS-A-LEGACY-ALIAS** (LOW, config) — owner decision, no test
  — config. `agents/distill.md:4`, `agents/refine.md:4` and
  `agents/visual.md:4` list the `Task` tool and `settings-recommended.json:4`
  allows `Task(*)`; Claude Code renamed it to `Agent` in 2.1.63 and keeps
  `Task` as an alias. **Default if nothing is decided:** keep `Task` until
  the alias goes.

- **SETTINGS-ALLOW-GIT-BRANCH** (LOW, config) — owner decision, no test —
  config. `settings-recommended.json:10` allows `Bash(git branch*)` while
  WISDOM § Git bans `git branch <name>`; `unsafe_command_reason` returns
  None for `git branch foo`, `git push --force`, `git push -f` and `git
  clean -fd`. Four keys (`alwaysThinkingEnabled`,
  `skipDangerousModePermissionPrompt`, `promptSuggestionEnabled`,
  `spinnerTipsEnabled`) fall under step 5's diff-and-ask with no rule naming
  them. Policy over enforcement is the house rule. **Default if nothing is
  decided:** as written.

## rig

- **RIG-DEMO-GIF-STALE** (LOW, docs) — CONFIRMED 2026-10-01. `rig/demo/demo.gif`
  still plays the removed `riq` section; `rig/demo/run.ts` no longer has it,
  and `run.ts:252` still says the reflog keeps commits 90 days (30 for an
  unreachable entry, `gc.reflogExpireUnreachable`; `rig/README.md` says 30).
  `make -C rig demo` needs `asciinema` and `agg`, which this host lacks.
  **Fix:** fix the line, then re-record with `make -C rig demo` on a host
  that has both.

- **RIG-PUSH-BYPASSES-ASK-RULE** (MED, config) — open (record only). The
  `Bash(git push*)` ask rule (`settings-recommended.json:18`) matches the
  command string, so it never matches `rig push`, `rig p` or the `rip`
  symlink, though each runs `git push origin …` (`rig/rig:179`, dispatch at
  `rig/rig:244`). An unlisted command still gets the default prompt, but an
  allow rule that admits them pushes with no ask gate left. **Fix:** an ask
  rule for the rig push forms; which forms, and whether to gate them at all,
  is the maintainer's call.

- **RIG-HELP-EXITS-1** (LOW, ux) — CONFIRMED 2026-10-10. `rig/rig:267`
  routes `-h|--help|help` to `usage()`, which ends in `exit 1` (`:237`), so
  `rig --help` fails in a pipeline. **Fix:** exit 0 on an explicit help
  request.

- **RIG-MAKEFILE-STALE-NAME-CLEANUP** (LOW, dead code) — owner decision.
  `rig/Makefile:7-12` removes retired `gt*`/`gb`/`gpo` symlinks under
  `~/.local/bin` and `~/bin`; `cmd_install` (`rig/rig:193-204`, proven by
  `rig/test.sh:162-168`) already removes every stray symlink to `rig` in the
  install dir, so only the `~/bin` line and non-symlink entries do anything.
  **Default if nothing is decided:** keep until a host without the old names
  is confirmed.

## dockbox

- **BOX-CODEX-DUPLICATE-MODEL-FLAG** (MED, config) — CONFIRMED 2026-10-08,
  no test — config. `dockbox/dockbox:445,462` and
  `qemubox/qemubox:1101,1341` prepend `-m` and forward the user's model flag.
  An explicit `-m` or `--model` then prevents Codex from starting.
  Reproduce with Codex 0.160.0:
  `codex -m gpt-6.1-sol --model gpt-6-astra --version` exits 2 with
  "the argument '--model <MODEL>' cannot be used multiple times".
  **Fix:** inject the alias model only when the user supplies no model flag.

- **DOCKBOX-EXPLICIT-CODEX-SKIPS-DEFAULTS** (MED, config) — CONFIRMED
  2026-10-08, no test — config. `-d codex` and `-x codex` skip the alias
  defaults at `dockbox/dockbox:435,445`; `:502` adds only the sandbox bypass.
  Reproduce: compare `dockbox -d codex .` with `dockbox codex .`.
  The explicit route omits `-m gpt-6.1-sol` and
  `-c model_reasoning_effort=xhigh`, despite the equivalence claim at `:306`.
  **Fix:** apply the alias defaults to the explicit Codex route.

- **DOCKBOX-DEFAULTMODE-TOP-LEVEL** (LOW, config) — CONFIRMED 2026-10-06.
  The box settings override sets `d['defaultMode'] = 'bypassPermissions'`
  (`dockbox/dockbox:609`), a top-level key Claude Code does not read; the
  setting is `permissions.defaultMode`. No effect today: the image's `claude`
  wrapper passes `--dangerously-skip-permissions` (`dockbox/Dockerfile:167`).
  **Fix:** set `permissions.defaultMode`, or drop the line.

- **DOCKBOX-LIFECYCLE-UNSERIALIZED** (MED, design) — needs sign-off. Nothing
  serializes creating, entering and removing a box, so two invocations for
  the same project can remove each other's box. (a) A leaving session drops
  its marker and lists the marker dir (`dockbox/dockbox:552-553`), then
  force-removes the box on an empty listing (`:554-555`). A second invocation
  that passed the running check (`:565`) and writes its marker (`:535`)
  between that listing and the removal has its box removed under it; one
  that writes it just after the removal exits with no message, since `:535`
  discards the error. (b) Two launchers for a project with no box both pass
  the same check (`:565`), and the second's pre-run `docker rm -f -v`
  (`:755`) removes the box the first just started (`:762`), with any session
  already in it. `prune` probes an idle box and removes it in two steps
  (`:267-270`), so a session entering between them is removed the same way.
  **Fix:** a per-box host lock (e.g. `flock`) held across marker
  registration, the empty-listing-to-removal step, and creation — a new
  lifecycle contract; no test — design.

- **BOXES-SHARE-CLAUDE-RUNTIME-STATE** (MED, design) — needs sign-off.
  Both boxes bind the whole `~/.claude` rw (`dockbox/dockbox:14`,
  `qemubox/qemubox` `assemble_mounts`), which holds persistent state the
  contract wants shared (`projects/`, `memory`, `skills`, `settings.json`,
  `.credentials.json`) and per-process runtime state it does not: besides
  `sessions/` (a private tmpfs per box) the installed Claude Code
  2.1.286 keeps `tasks/`, `session-env/`, `bridge-spawn/`, `ccr/`,
  `server.lock`, `server-sessions.json` and `ide/*.lock` there (names from
  the binary's config-dir list). Through those, one box's agent can read
  another box's or the host's background-task outputs and IDE lock files
  (port and auth token of a host IDE server, reachable from a `-H` box),
  and the host's `claude agents` daemon state mixes with box state.
  **Proposal:** split the bind — persistent dirs stay shared, runtime dirs
  become per-box tmpfs like `sessions/` — in both tools. Tradeoffs: the
  host's agent view stops listing box background sessions (it already
  cannot attach to them: their sockets are box-private), `tasks/` output of
  a box's subagents dies with the box, and the list is version-bound, so it
  needs re-checking on Claude Code upgrades. A contract change; not shipped.

- **DOCKBOX-NAT-FLOWS-ON-CARRIER-BLIP** (LOW, design) — open (unverified).
  The journal shows the Wi-Fi link dropping and re-acquiring the same DHCP
  lease within 2-5 s several times a day (`journalctl -u systemd-networkd`,
  "wlan0: Lost carrier" then "DHCPv4 address 192.168.0.153/24"). networkd
  removes the address on carrier loss; the kernel's MASQUERADE target then
  flushes every conntrack entry NATed to it (`nf_nat_masquerade.c`,
  `masq_inet_event`). A host socket survives the blip (TCP retransmits once
  the address is back); a bridge box's flow survives only if its next packet
  is outbound, so a fresh NAT entry with the same port is created. If the
  server speaks first — a streaming API response — the packet finds no entry
  and no local socket, the host answers RST and the box's connection dies.
  Reproducing needs a Wi-Fi toggle, which this audit did not do. `-H` has
  no NAT and none of this. **Fix:** none in dockbox short of host network;
  document, or test and close.

- **BOX-OPUS-XHIGH-RATIONALE-GONE** (LOW, design) — proposed.
  `dockbox/dockbox:443,491` and `qemubox/qemubox:1105,1109` launch the
  `opus` alias and the bare default at `--effort xhigh`; the help text
  (`dockbox:290`, `qemubox:53,58`, `qemubox/README.md:63`) and
  `dockbox/test.sh:357,366` pin it. The one reason on record (CHANGELOG
  v0.3.35: the launcher matches the opus subagent) contradicts
  `agents/opus.md:4`, which pins `high`. **Proposal:** either align the
  launchers to `high` (scripts, help, READMEs, test) or state the box's own
  reason for xhigh. Owner's call.

- **DOCKBOX-HELP-OMITS-X-AND-IMAGE-PACKAGES-UNUSED** (LOW, docs) — CONFIRMED
  2026-10-10, no test — docs. `dockbox/dockbox:430` accepts `-x` and
  `README.md:69` documents it, but the `--help` Options list (`:304-317`)
  shows only `-d`. `dockbox/Dockerfile:20` installs `iptables ipset iproute2
  dnsutils aggregate`, which no script in the repo uses (`grep -rnw` over
  dockbox, qemubox and the docs finds nothing); the egress lockdown they
  served was rejected. **Fix:** add the `-x` help line; the packages are the
  owner's call.

## qemubox

- **QEMUBOX-NO-EGRESS-FILTER** (HIGH, hardening) — needs sign-off.
  `qemubox/README.md:180-186` states the gap plainly — live `~/.claude` /
  `~/.codex` tokens are shared read-write with the guest, outbound is open unless `-H`,
  and "the path for exfiltration is open". `-H` is all-or-nothing: an agent
  that needs `api.anthropic.com` gets the whole internet with it. An in-guest
  sandbox cannot close this: the guest mounts agent config read-write at
  the host paths (`qemubox/README.md:128-132`) and the guest user has
  passwordless sudo (`:189`), so anything in the guest can widen its own
  limits. Only a host-side wall holds, and qemubox already sits on one: slirp,
  with `restrict=on` at `qemubox:596`. **Fix (proposal):** a fixed-at-boot
  flag `-p host1,host2` alongside `-H`: start a host proxy on
  `127.0.0.1:$pport` with the allowlist, add
  `,restrict=on,guestfwd=tcp:10.0.2.100:3128-tcp:127.0.0.1:$pport` to the
  `-nic` at `qemubox:617`, and put `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` into
  `envs` so `send_envs` (`qemubox:1155-1161`) carries them.
  Claude Code honours those variables. `stop_box` kills the pid, `remove_box`
  removes the files. Roughly 40-60 lines of shell plus docs and three parse
  assertions in `test.sh`. Under `restrict=on` the guest cannot reach slirp's
  DNS, so the host proxy resolves names and there is no UDP/53 side channel.
  Unmeasured: that slirp actually drops guest DNS under `restrict=on` — the
  documentation says the guest is "not able to contact the host", and no one
  has tested it here, because this box has no `/dev/kvm` access.

- **QEMUBOX-POWEROFF-CLAIMS-RUNNING** (LOW, ux) — CONFIRMED 2026-10-01.
  `qemubox -n x -N exec sudo poweroff` ends with ssh's
  "kex_exchange_identification: Connection reset by peer" and
  `qemubox:326` "cannot remove session marker; keeping qemubox-x running",
  while `qemubox status x` already reports `process=stopped`. `running` at
  `:320` still sees the QEMU process during shutdown; the marker ssh then
  fails. **Fix:** re-check `running` before printing the note; say the VM is
  shutting down instead.
- **QEMUBOX-FIRST-BOOT-SYSTEMCTL-NOISE** (LOW, ux) — CONFIRMED 2026-10-01.
  First boot prints systemctl's two "Removed '/etc/systemd/system/...
  systemd-timesyncd.service'" lines into the user's terminal from
  `sync_guest_clock` (`qemubox:528`). **Fix:** `systemctl disable --now
  --quiet`.
- **QEMUBOX-TEST-NEGATION-NO-OP** (LOW, tests) — CONFIRMED 2026-10-06.
  Bash exempts a `!`-negated command from `set -e`, so a `! cmd` line that is
  not the last in its `set -e` block asserts nothing: `qemubox/test.sh:162`
  `! flock -n "$ROOT/.locks/identitybox" true` in the identity and boot
  block passes whatever it finds. **Fix:** `if cmd; then exit 1; fi`.

- **QEMUBOX-UNDOCUMENTED-ALIASES-AND-ENV** (LOW, docs) — CONFIRMED
  2026-10-10, no test — docs. `destroy` (`qemubox/qemubox:1261`),
  `-f`/`rebuild` (`:1266`) and `QEMUBOX_QEMU` (`:10`) appear in neither the
  usage text nor `qemubox/README.md`. **Fix:** document them or drop them.

## bhctl

- **BHCTL-HELP-NEEDS-PAIRED-DEVICE** (LOW, ux) — CONFIRMED 2026-10-10. The
  MAC lookup (`bhctl/bhctl:33-36`) runs before the `case` at `:52`, so
  `bhctl -h` with no paired headphones prints "no paired headphones" and
  exits 1; the README says `-h` prints help. **Fix:** parse `-h` before the
  lookup.
- **BHCTL-LDAC-LABEL-HARDCODED** (LOW, ux) — CONFIRMED 2026-10-10.
  `bhctl/bhctl:62` prints `hifi (LDAC)` for any `a2dp*` profile; the README
  § Limits says the codec is not chosen here, so an AAC link is labelled
  LDAC. **Fix:** print the profile, not a codec.

## Root Makefile

- **ROOT-MAKE-CLEAN-UNINSTALLS** (LOW, docs) — CONFIRMED 2026-10-10, no
  test — docs. Root `make clean` runs each project's `clean`; `bhctl`,
  `qemubox` and `rig` delete their installed binaries (and rig's symlinks),
  `dockbox` also runs `docker rmi dockbox`; `udfix` and `gloww` only clean
  the build. `CLAUDE.md` § Commands and the READMEs do not say so. **Fix:**
  say it in `CLAUDE.md` § Commands.

## Fetchers (dc-fetch, tg-fetch, tw-fetch)

- **DC-FETCH-LIMIT-WRITES-WHOLE-BATCH** (LOW, correctness) — CONFIRMED
  2026-10-10. `dc-fetch/main.py:44-51` loops `while total < limit`, always
  requests 100 and writes the whole batch, so `-l 10` writes up to 100
  messages; `README.md` says `-l` stops after N messages total. **Fix:**
  request `min(100, limit - total)` or truncate the batch.
- **TG-FETCH-NO-FLUSH** (LOW, correctness) — CONFIRMED 2026-10-10.
  `tg-fetch/README.md:53` says every message is flushed before the next is
  fetched; `tg-fetch/main.py:103-108` writes to a block-buffered
  `open(p, 'a')` with no `flush()` (`tw-fetch/main.py:136` and
  `dc-fetch/main.py:52` do), so a kill loses the buffered tail. **Fix:**
  `f.flush()` after the write.
- **TW-FETCH-DUPLICATED-SCROLL-LOOP** (LOW, duplication) — CONFIRMED
  2026-10-10. `tw-fetch/main.py:192-212` (`collect_round`) and `:286-306`
  (`user`) are the same 21-line scroll-parse-append loop, differing only in
  `range(30)`/`range(200)` and `stale >= 3`/`>= 5`. **Fix:** one helper with
  the two bounds as parameters.
- **TG-FETCH-DUPLICATED-MAIN** (LOW, duplication) — CONFIRMED 2026-10-10.
  `tg-fetch/main.py:118-139` and `tg-fetch/users.py:63-84` (`run`, `main`,
  the `__main__` guard) differ only in two strings. **Fix:** one entrypoint
  in `main.py`, imported by `users.py`.

## ship

- **SHIP-INTO-TOOLS-AS-STEP-RUNNER** (MED, design, proposed) — keep the ship
  program, move it into this repo as `ship/` (`git subtree add --prefix=ship
  https://github.com/kronael/ship e417572`, keeping its 114 commits) and make
  it a runner of steps: each step has a role, a shell gate and a review mode
  (pause or auto), and the spec planner becomes one producer of steps beside
  the ship skill's plan file. Ship's pipeline (validate, plan, run, judge,
  replan, verify) is the owner's workflow model; Claude Code's Workflow tool
  is a script per job inside one session and does not replace it. Ship runs
  outside a session, with state on disk across usage-limit outages. Order: (1) a usage
  limit or a lost login exits with state kept (today 3 verifier failures
  reach `mark_complete`, `ship/judge.py:381-389`); (2) a per-step shell gate
  decides COMPLETED (the judge's verdict is discarded, `judge.py:98`); (3) a
  `--step` pause so a sonnet run is read step by step (WORKER-NO-STEP-PAUSE
  in kronael/ship); (4) a plan-file producer; (5) `-n 1` by default and
  `depends_on` enforced, since workers share one cwd; then cost in the trace
  and the move hygiene (ruff, CI template for Python 3.14, stale `--help`).
  `skills/ship/cli.md` keeps `MODEL=fable` until (2) and (3) land. Waits for
  the owner's sign-off. Recorded 2026-10-06.

## Ruled not a defect

- **QEMUBOX-DOCKBOX-UX-DUP** (LOW, duplication) — not a defect. The two tools
  duplicate flag parsing, the tool/model table, `ls`/`rm`/`prune`, and the
  lifecycle block. A shared sourced file would violate the repo's "tools are
  independent, no imports" rule (`CLAUDE.md`); `tests/drift_test.sh` is the
  accepted lightweight guard instead.

- **DOCKBOX-PROJECT-ENV-REACHES-ROOT** (MED, security) — not a defect. A
  project `.dockboxrc` `-e` variable reaches root in the box (dockbox-init runs
  as root with the container env, and sessions enter as root before `setpriv`),
  so `-e LD_PRELOAD=<repo file>` runs code as root there. dockbox is a decently
  isolated env, not a jail: root inside the box is within its design.

- **BOXES-DOCKER-SOCKET-CROSSES-BOXES** (MED, isolation) — not a defect. `-D`
  binds `/var/run/docker.sock` into a dockbox and forwards it into a qemubox
  over SSH; either agent can then `docker exec` into every dockbox on the
  host. That is the flag's purpose (building images, running containers)
  and the project `.dockboxrc`/`.qemuboxrc` cannot set it, so it is an
  explicit per-box grant. Both READMEs say it crosses the box wall.

- **DOCKBOX-CREDS-MOUNTED-RW** (MED, hardening) — not a defect. dockbox mounts
  `~/.claude` and `~/.codex` rw, API tokens included (`dockbox/dockbox:14,20`).
  Claude Code and Codex both rewrite their token files on login refresh, so a
  ro or redacted token breaks auth inside the box. The README already says
  dockbox is not a boundary for hostile code.

- **SKILL-LINT-NO-ORG-REF-CHECK** (LOW, coverage) — not a defect. `CLAUDE.md`
  bans local paths, org-specific refs and secrets in source;
  `hooks/skill_frontmatter_lint.py` checks the first and the last, and nothing
  checks the second: a pattern for an org ref would have to name the org,
  which is the string the rule exists to keep out of the repo. The rule stays
  a review check.
