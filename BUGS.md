# BUGS

## Bundle

- **MK-REPO-MAKEFILES-KEEP-HELP-TARGETS** (LOW, docs) — owner decision.
  `skills/mk/SKILL.md` § No help target bans a `help` target,
  `.DEFAULT_GOAL := help` and `##` descriptions, and this repo's own
  `Makefile:52` and `hooks/Makefile:11` keep `help` targets with `@echo`
  descriptions. **Fix:** drop both targets and let `README.md` § Commands carry
  the one-line descriptions, or exempt the toolkit in the skill; no test — the
  skill text and the Makefiles.

- **SERVER-INIT-HOSTNAME-MISSING** (LOW, correctness) — CONFIRMED at HEAD
  2026-10-10. `skills/server-init/SKILL.md` step 2 and its template run
  `hostname -s`, and step 3 runs `hostname -f`. A host without inetutils
  (Arch here) has no `hostname` binary: `command not found`, so the target
  name comes out empty, and step 3's `hostname -f` fails the same way.
  `uname -n` prints the stored hostname, which may be a full domain name.
  **Fix:** in step 2 and the template, `h=$(uname -n)` and `${h%%.*}`; no
  test — skill text.

- **FORM-KEEPER-SIZE-THRESHOLD-UNENFORCEABLE** (LOW, design) — proposed,
  needs sign-off. `skills/writing/page.md:195` marks "one font family, five
  sizes at most" a `keeper` (a `make lint` check that fails the build), but
  `skills/create/form.md:67` and its calibration record (`:81`) measure
  distinct rendered sizes and report the owner's accepted pages run 12–15,
  failing only at >16 (≤5 is a "watch", never failing). A keeper at five sizes
  fails every accepted page; the measurable fail sits at sixteen. No keeper
  check exists yet, so nothing breaks today. **Proposal:** the owner sets the
  enforceable number — drop the `keeper` from the five-sizes rule, or state the
  measurable threshold (distinct rendered sizes) the keeper enforces, and point
  `writing/page.md` and `form.md` at one owner for it. No test — design.

- **RECALL-UNREADABLE-TRANSCRIPT** (MED, correctness) — CONFIRMED 2026-10-06.
  `skills/recall-memories/recall.py` `read_records` (~250) opens every
  transcript under `~/.claude/projects/` and lets a `PermissionError` escape:
  one unreadable file kills every `results` search, scoped or `-a`. Here it is
  `~/.claude/projects/-/399a5e4c-d151-43d2-8aeb-292ba1c6b8a1.jsonl`, in a
  root-owned dir a session run as root from `/` left.
  Reproduce: `python3 ~/.claude/skills/recall-memories/recall.py results -t
  Agent 'NEEDS TELLING'`. A dangling symlink to a subagent transcript in a
  container home stops it the same way with `FileNotFoundError` (2026-10-21).
  **Fix:** catch `OSError`, skip the file with one stderr line naming it.

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
  `skills/global/SKILL.md:190-193` caps subagents by `subagent_type` at 2
  `sonnet` and 1 `opus` or `fable`; the bundle also launches `general-purpose`
  (`skills/dispatch/SKILL.md:8`, `skills/sweep/SKILL.md:25`), `Explore`
  (`skills/sweep/SKILL.md:17`, `skills/scavenge/SKILL.md:62`,
  `skills/recall-memories/SKILL.md:165`) and the thin
  skill agents — `improve` pins Sonnet 5.5 (`agents/improve.md:3`), the rest
  inherit the parent's model — none of which the cap names. **Options:**
  (a) count a sub under the model it runs on (`improve` as `sonnet`,
  `general-purpose` as the parent's model); (b) count only the three named
  types. **Default if nothing is decided:** (a). No test — design.

- **AGENT-ROUTING-RULES-DISAGREE** (LOW, docs) — owner decision.
  `skills/global/SKILL.md:200-202` runs every implementation as an `opus`
  plan and one `sonnet` sub per step, but `skills/sonnet/SKILL.md:21` lets
  the parent plan, and `skills/ship/SKILL.md:113` sends a step to `opus` when
  the plan leaves a design call open. `skills/fable/SKILL.md:12` sends every
  spec, architecture or skill text to `fable`, while `:19` forbids `fable`
  whenever `opus` can do the work, which covers an ordinary spec. `:210-211`
  of the global file sends a project's own library to an `opus` plan, then
  `sonnet` or `opus` steps, an `opus` step that its own `:203-204` rules out.
  **Options:**
  (a) WISDOM names the parent-plans and `opus`-step exceptions, and `fable`
  `:19` exempts the tasks `:11-14` list; (b) the skills drop the exceptions.
  **Default if nothing is decided:** (a). No test — skill text.

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
  follow neither: `hooks/stop.py:20` `git_run()`, `hooks/pretool_nudge.py:202`
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

- **SWEEP-NAMES-TWO-READONLY-AGENT-TYPES** (LOW, duplication) — CONFIRMED
  at HEAD 2026-10-10. `skills/sweep/SKILL.md:17` names its read-only subs
  "Sonnet/Explore"; `:25` launches a `general-purpose` agent. **Fix:** name
  one agent type. No test — duplication.

- **TS-BANS-MJS-BROWSE-WRITES-MJS** (LOW, duplication) — CONFIRMED at HEAD
  2026-10-10. `skills/ts/SKILL.md:21-22` bans plain JavaScript tooling
  (`.mjs`); `skills/browse/debug.md:19` has the agent write `tmp/debug.mjs`
  and run it with `node`. **Fix:** a `tmp/debug.ts` run by `bun`, or scope the
  ts rule to committed tooling. No test — duplication.

- **SOCIAL-REFS-NARRATE-HISTORY** (LOW, docs) — CONFIRMED at HEAD
  2026-10-06. `skills/create/social/references/codex-critique.md:3` frames the
  file as a "Raw adversarial pass by codex-cli 0.144.4" over an earlier draft
  of `research-social-meme.md`, whose § Where the SKILL departs from this
  research (`research-social-meme.md:196-223`) states the outcome as it stands.
  The critique is the prior-version record the wisdom file bans in permanent
  content, kept as a cold provenance file nothing reads by accident. **Fix:**
  the maintainer's call — keep it as attribution, or move it to the diary;
  no test — docs.

- **DIAGRAMS-NO-SEQUENCE-SWIMLANE-STATE** (LOW, design) — open (record only).
  `skills/diagrams/SKILL.md` (52 lines) teaches only box-and-arrow component
  layout. It carries no pattern for the three other shapes that come up
  constantly: sequence (message order and who waits), swimlane (step ownership
  and the handoffs between actors), and state (the legal transitions of one
  entity). Each needs its own ASCII template plus a one-line rule for when to
  reach for it, in the same shape as the existing layout pattern. Reproduce:
  `grep -i 'sequence\|swimlane\|state' skills/diagrams/SKILL.md` → no hits.

- **BOX-HAIKU-PIN-BEHIND-AGENT-PIN** (LOW, config) — CONFIRMED at HEAD
  2026-10-16, no test — config. `agents/haiku.md` pins the `haiku` alias,
  which Claude Code resolves to the latest Haiku (`claude-haiku-5-5` in
  2.1.301), while `qemubox haiku` starts Claude Code on the dated previous model
  `claude-haiku-4-5-20251001`; `qemubox/test-parity.sh` pins that string.
  **Fix:** the box alias takes `claude-haiku-5-5` and the test follows.

- **AGENTS-SOL-TERRA-SAME-MODEL-DIFFERENT-CAP** (LOW, design) — owner
  decision, no test — design. `skills/global/SKILL.md` § Agents counts `terra`
  as a `sonnet` and `sol` as an `opus`, yet both run `gpt-6.1-sol` at high
  (`skills/terra/SKILL.md:10`, `skills/astra/SKILL.md` § Sol), so the same
  model at the same effort takes a 2-slot or a 1-slot bucket by skill name.
  **Options:** (a) count `sol` as a `sonnet` — one bucket per model and
  effort; (b) keep the mapping by role — a second opinion is review-grade
  work and takes the scarcer slot. **Default if nothing is decided:** (b),
  the text as written.

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

- **LANG-SKILLS-RESTATE-COLD-RUNBOOKS** (LOW, duplication) — owner decision,
  no test — duplication. Hot `SKILL.md` bodies restate rules a cold
  `software/` runbook owns: `skills/py/SKILL.md:121-123,130,132-137`
  (`strict-typing.md` one mode, `ci.md` `python -m pytest`, `testing.md`
  fixtures and doubles), `skills/go/SKILL.md:38-39,42,155,159-160`
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
  clean), `skills/ts/SKILL.md:156-157` (prepare, check, right, test), WISDOM
  § House conventions (test, test-all, smoke); `ci.md:44` "NEVER add a
  `lint` target" vs `ops:47`, `mk:76,86`, `py:142`, `ts:156`; `ci.md:50`
  sets `PYTHONPATH` per target, `py:148` once. Log line:
  `software/observe.md:5` (`[LEVEL] key=value`) vs `software/code.md:186`
  (`INFO subsystem: message`); health: `service:12` (`/health`, `/ready`)
  vs `observe.md:12` (`/.well-known/live`); Python: `py:19` 3.13+ vs
  `strict-typing.md:43` 3.12; aliasing: `py:93-94` allows `heapq_merge` on
  a collision vs `code.md:26-28` NEVER rename; prose wrap:
  `skills/create/web/code-presentation.md:110` 90 chars vs `code.md:170` 100,
  which `rumdl` reflows. **Options:** one owner per
  fact, the rest point. **Default if nothing is decided:** `code.md` and
  WISDOM win where they speak; the rest stays until picked.

- **SKILLS-RETRY-LOOPS-VS-FAIL-LOUD** (LOW, design) — owner decision, no
  test — design. `skills/rs/SKILL.md:101-122` prescribes a `main()` loop
  that sleeps and restarts on any `Err`; `skills/service/SKILL.md:14` says
  "use last available data when current unavailable"; `skills/data/SKILL.md:44`
  "Retry with exponential backoff" — `software/code.md` § System changes
  retries ONLY the transient. **Options:** (a) scope each to transient
  errors; (b) state the supervised-binary exception in `rs`. **Default if
  nothing is decided:** (b).

- **SOLANA-DEPS-VERSIONS-STALE** (LOW, docs) — CONFIRMED 2026-10-10, no test
  — docs. `skills/solana/deps.md:12` calls anchor-lang 1.1.2 the newest
  release and `:22` solana-pubkey 4.3.0; the crates index lists 1.2.1
  (depending on `solana-pubkey` v3 and v4) and 4.4.0, and `:118-121` rests
  on the 1.1.2 claim. `skills/solana/layout.md:113` is "verified at cargo
  1.97.1". **Fix:** re-verify each pin against the index and the toolchain.

- **README-ROUTER-CONTRADICTS-ITSELF** (LOW, docs) — owner decision, no test
  — docs. `skills/readme/sync.md:56` puts an "Architectural Decisions"
  section in ARCHITECTURE; `skills/readme/topology.md:86` says NEVER
  record a decision there. `sync.md:24-48` and `topology.md:44-58` give two
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
  (`skills/wisdom/SKILL.md:47` forbids a shared primary trigger);
  `skills/terra/SKILL.md:24-27` requires `--sandbox read-only` outside
  qemubox while `astra:29,57` always bypasses the sandbox. **Default if
  nothing is decided:** as written.

- **SCAVENGE-OUTPUTS-CONTRADICT-BUNDLE-RULES** (LOW, design) — owner
  decision, no test — design. `skills/scavenge/SKILL.md:25-26,136-138`
  writes new skills and agents into `~/.claude/` (an install of this repo,
  WISDOM § Environment); `:66,79,178` put research and critiques under
  `<cwd>/docs/<topic>/` (`skills/readme/shape.md:161-162` bans work records
  in `docs/`); `skills/scavenge/shapes.md:38-55` is a content-bearing agent
  skeleton (`skills/CLAUDE.md:119` forbids one). **Default if nothing is
  decided:** as written.

- **EVAL-DOGFOOD-REPORTS-ARE-WORK-RECORDS** (LOW, docs) — owner decision, no
  test — docs. `skills/eval/design/dogfood-glass.md:16,110-114` and
  `dogfood-term.md:113-116` carry dated outcomes and shortened hashes
  (`cfecd8c`, `0c16126`; WISDOM § Documentation wants them full);
  `skills/eval/novice.md:6-7,184-186` names its scavenge provenance and
  `oracle-critique.md` files that `scavenge:79` writes as
  `astra-critique.md`. **Options:** (a) move the reports to the diary; (b)
  genericise; (c) keep. **Default if nothing is decided:** (c).

- **REFINE-PY-LENS-ALLOWS-WHY-COMMENT** (LOW, docs) — owner decision, no
  test — docs. `skills/refine/py.md:41-42` keeps "one short clause only for a
  non-obvious why" — a general why comment that none of the three in-body
  exceptions in `skills/software/code.md:79-84` covers, while
  `skills/refine/software.md:29-38` hunts every comment outside them, so the
  Python lens licenses what the baseline refuses. **Options:** (a) cut
  the clause, leaving `software.md` the one comment lens; (b) keep it as a
  Python allowance and say so in `code.md`. **Default if nothing is
  decided:** as written.

- **CREATE-PORTED-HERMES-TOOL-NAMES** (LOW, docs) — CONFIRMED at HEAD
  2026-10-11, no test — docs. Ported files under `skills/create/` name Hermes
  tools this harness lacks — `write_file`, `read_file`, `patch`, `terminal`,
  `browser_navigate`, `browser_vision` (`web.md:685-692,804-808`,
  `web/popular-web-designs.md:44-47,85-86`, line 13 of all 54
  `web/popular-web-designs/templates/*.md`, `diagram/excalidraw.md:31-32,36`,
  `diagram/architecture-diagram.md:47`, `web/design-md.md:133`,
  `art/pretext.md:156`, `art.md:226` (`terminal`); also
  `skills/humanize/SKILL.md:38,94,108`) — and a
  `generative-widgets` skill (`popular-web-designs.md:42,85` and the
  templates) the bundle does not ship. **Options:** (a) one line in
  `create/SKILL.md` § Rules mapping the Hermes names to Read, Write, Edit,
  Bash and the `browse` skill; (b) rewrite each ported file. **Default if
  nothing is decided:** as written.

- **CREATE-DEAD-POINTERS** (LOW, docs) — CONFIRMED at HEAD 2026-10-11, no
  test — docs. House file: `skills/create/divergence.md:54` names `tmp/inspiration.py`,
  which exists neither in the repo (`find` over the tree) nor in an install. Ported
  files: `art/ascii-video/README.md:278` → `design-patterns.md` (absent; the
  patterns are in `references/scenes.md`); `art/p5js/README.md:40`,
  `art/p5js/scripts/setup.sh:3`, `video/manim/README.md:22` →
  `skills/creative/...` (the upstream layout); `art/ascii-video.md:69` →
  `composition.md § Adaptive Tonemap` (the heading is "The `tonemap()`
  Function"); `art/pretext.md:39-40` names `ascii-art`, `ascii-video` and
  `p5js` as skills (now `art.md`, `art/ascii-video.md`, `art/p5js.md`);
  `video/render/examples/README.md:25` cites a Lottie row `video/render.md`
  lacks. **Fix:** the house file names the project that holds the implementation
  or drops the pointer; the ported files are the owner's call per
  `software/credits.md`.

- **CREATE-PORTED-TREES-RESTATE-THEMSELVES** (LOW, duplication) — owner
  decision, no test — duplication. Each ported mode file restates rules its
  own `references/` and `README.md` carry. manim: monospace-only font in 4
  files, opacity layering 1.0/0.4/0.15 in 4, `buff >= 0.5` in 5, raw-string
  LaTeX in 4, `self.wait()` in 6, the timing table, palette, quality presets
  and stitch command in 2-3 each. ascii-video: the ffmpeg `stderr=PIPE`
  deadlock in 5, font cell height in 4, `tonemap()` in 6, and `README.md`
  repeating the mode table, pipeline and catalogs. p5js: seeded randomness,
  FES off, HSB, `fbm`, `createGraphics`, WebGL gotchas, key bindings,
  `noLoop()` capture and fxhash each in the mode file and 1-3 references,
  plus two SVG Export sections in `references/export-pipeline.md:330-361,491-519`
  pinning `p5.js-svg` 1.5.1 and 1.6.0. pretext: real-prose, prepare-once and
  pin-the-version each 2-3 times inside `art/pretext.md`. excalidraw: the
  `label` warning in 4 places. design-md: the anatomy example against
  `templates/starter.md`. popular-web-designs: the Hermes block at line 13 of
  all 54 templates, and the three-mode decision table in `web.md:22-36`,
  `popular-web-designs.md:27-35` and `design-md.md:34-37`. `web.md` against
  itself: self-contained HTML 4 times, verification 3, "2-3 variants" at
  `:646` against "at least three options" at `:326-346`. **Options:** (a)
  keep — a reference file loads alone, so a restatement there is what its
  reader sees; (b) cut the mode files to pointers. **Default if nothing is
  decided:** (a).

- **SQUASH-MAPPING-SHORT-SHAS-AND-WIDTH** (LOW, docs) — open (record only),
  no test — docs. The mapping example in `skills/squash/SKILL.md:59-76`
  shows 6-character SHAs (`abc111`) against WISDOM's full-hash rule and the
  skill's own "A full SHA goes on a line of its own" (`:56-57`); and `:54`
  promises a 40-column read while a block line is `1. ` plus a subject of up
  to 72 characters, 75 columns. **Fix:** full SHAs on their own lines in the
  example; state that the subject line may wrap, or drop the 40-column claim.

- **REFACTOR-MANIFEST-UNCHECKED** (LOW, docs) — open (record only), no test
  — docs. `skills/software/refactor-stack.md:324-327` requires a port's
  manifest to account for every source file, but nothing diffs its rows
  against `git ls-tree -r --name-only <source SHA>`, so a file missing from
  both the manifest and the port passes. The `software/SKILL.md:26` row for
  `refactor-stack.md` does not name the manifest, and the port row (`:27`)
  routes to `credits.md`, so a port request does not reach it. **Fix:** add
  the `ls-tree` diff to the manifest bullet and "port manifest" to a row.

- **TESTING-VS-REFACTOR-COMMIT-CADENCE** (LOW, docs) — open (record only), no
  test — docs. `skills/software/testing.md:34-36` runs the full `make test`
  tier "once before the commit"; `skills/software/refactor-stack.md:113-114`
  commits after every edit, which makes that a full run per edit. **Fix:**
  scope one of the two — e.g. refactor-stack commits on the focused run and
  runs the full tier per pushed layer.

- **WISDOM-BODY-OVER-200-LINES** (LOW, docs) — CONFIRMED 2026-10-13, no test
  — docs. `skills/global/SKILL.md` body is 202 lines: `make skills-frontmatter`
  warns `[skill-length]` (> 200) while `CLAUDE.md` § Under 200 lines holds the
  wisdom file to the cap. The body measures 195 lines at origin/master and 202
  at HEAD (`git show <rev>:skills/global/SKILL.md | awk 'n>=2 && (p || NF)
  {p=1; c++} /^---$/{n++} END{print c}'`); the range changed only § Git (the
  `rip -g` bullet and the approval sentence) and § Agents (the cap wording).
  **Fix:** cut two lines — the owner's
  wording, so the owner's call which.

- **PY-RECORD-ROW-KEEPS-SMALLINT-INT** (MED, docs) — owner decision. Three
  rules are jointly unsatisfiable: `skills/py/SKILL.md:91` builds a record from
  its own SQL row as `Record(**row)`; `skills/sql/SKILL.md:43` stores a closed
  set as `SMALLINT` behind an `IntEnum` and passes the enum;
  `skills/py/SKILL.md:32` compares enum members with `is`. A dataclass does not
  coerce, so the field holds the row's `int`: for `Record(**{'status': 1})`,
  `r.status is Status.DONE` is `False` while `== Status.DONE` is `True`
  (`python3 -c` over a two-line `IntEnum` and a frozen dataclass). No rule names
  the place where the int becomes the enum. **Options:** (a) the db function
  that runs the SELECT converts each enum column before the record:
  `Record(**row | {'status': Status(row['status'])})`; (b) the record converts
  in `__post_init__` (`object.__setattr__` on a frozen dataclass); (c) the
  project's one codec (`from_dict`) takes own rows too and the `Record(**row)`
  rule goes. **Default if nothing is decided:** as written; a reader compares an
  enum column from a row with `==` until the owner picks. No test — docs.

- **RELEASE-COLLISION-CHECK-READS-LOCAL-TAGS** (MED, docs) — CONFIRMED at HEAD
  2026-10-16. `skills/release/SKILL.md` step 6 calls a version taken when
  `git rev-parse -q --verify vX.Y.Z` succeeds, which reads local tags only, and
  no step fetches `origin` first (WISDOM § Git: read the remote through its
  tracking refs after `git fetch origin`). A release cut on a line that has not
  fetched mints a version another host already published: a session tagged
  `v0.4.42` locally while `origin` carried `v0.4.42` through `v0.4.48` on 56
  commits past the shared `v0.4.41`. The CLAUDE.md § Release leak scan runs
  over `git diff <last tag>..HEAD`, which the same stale view misreads.
  **Fix:** step 1 fetches `origin` (SSH, else `rif -g
  '+refs/heads/*:refs/remotes/origin/*'`, whose default tag auto-follow also
  brings the remote's tags) and checks `git ls-remote --tags` for the version
  before step 6; a line behind `origin/<default head>` stops for `merge`
  before the version bump. No test — docs.

- **HOOKS-UPSTREAM-REDESIGN-HELD-BACK** (MED, design) — owner decision. Upstream
  v0.4.42–v0.4.48 rebuilt the hook layer: `hooks/lib/reminder.py` emits one XML
  pointer shape, `hooks/lib/kvs.py` and the `kvs` tool hold session memory,
  `hooks/style_nudge.py` measures each reply against the caveman budget and
  escalates, `local.py`, `reclaude.py` and `post_tool_nudge.sh` are gone, and
  `gh_text_lint.command_decision` asks before a review submit with a PR cap of
  1800 (`skills/pr-draft`, `skills/gh-comment` follow). This line keeps the
  v0.4.41 hooks, wiring, gate and skills on the owner's word that the caveman
  style and its hooks stay as refined here; the merge commit names every path.
  The redesign lives at `origin/master` 3f4c9be77383943d79eaea51c3bff4858a431807.
  **Options:** (a) adopt the redesign with this line's `caveman.md` as the
  measured source (`style_nudge` caps 20/5/2 already match; drop its 25-line
  report tier); (b) stay on the v0.4.41 hooks. **Default if nothing is
  decided:** (b). No test — design.

- **WRITING-STE-RULES-DUPLICATE-CAVEMAN** (LOW, docs) — owner decision.
  `skills/writing/SKILL.md` § Language (upstream) and
  `output-styles/caveman.md` § Language both carry the ASD-STE100 rule list;
  v0.4.41's `writing` pointed at caveman instead. Two copies drift. The owner
  keeps the rules in `caveman.md`. **Options:** (a) `writing` points at
  caveman again; (b) caveman points at `writing`. **Default if nothing is
  decided:** both stand. No test — docs.

## Codex bridge

- **CODEX-STATUSLINE-PARITY-LIMITS** (LOW, config) — deliberate limit,
  no test — config. `codex/config.toml:2` selects the closest native fields
  to `hooks/statusline.py:27-38`: model, context used, five-hour and weekly quota.
  Codex CLI 0.162.1 shows quota remaining, without reset times or Claude's compact
  model names, labels and separators. Its status line accepts built-in identifiers,
  with no command renderer for the shared Python logic. **Fix:** requires upstream
  support for reset fields or a command renderer; use `/status` for reset times.
  Sources: [config reference](https://developers.openai.com/codex/config-reference#tui-status_line),
  [schema](https://developers.openai.com/codex/config-schema.json),
  [built-in items](https://developers.openai.com/codex/cli/slash-commands#configure-footer-items-with-statusline).

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
  `settings-recommended.json` wires `prompt_nudge.py`, `pretool_nudge.py`,
  `style_nudge.py`, `stop.py` and `memory_nudge.py`, and none of them is it. Reproduce:
  `grep -c learn.py settings-recommended.json` → 0. **Fix:** the maintainer's
  call — wire it to an event, or drop it.

- **STOP-CLAUDE-EVAL-NO-PRODUCER** (LOW, config) — needs sign-off.
  `hooks/stop.py:163` suppresses the commit/diary block when `CLAUDE_EVAL` is
  set. Nothing sets it: its other hits are `hooks/test_stop.py:19`, which
  strips it from the test env, and `hooks/ARCHITECTURE.md:217,222`, which
  documents the clause — none in `Makefile`, `.github/`, or any
  `settings*.json` env block. Effect is the opposite of the intent: eval runs
  get the block messages injected into their transcripts. No eval runner
  exists in this tree, so nothing here can set it. **Options:** (a) delete
  the clause and its `hooks/ARCHITECTURE.md` mention; (b) keep it for an
  external runner that sets `CLAUDE_EVAL` itself. **Default if nothing is
  decided:** (b); no test — config.

- **DIARY-SLUG-EDGES** (LOW, design) — proposed, no fix without the owner.
  The diary slug (`hooks/stop.py:50-52`, `skills/diary/SKILL.md` § Where it
  lives) and the ship record slug (`skills/ship/SKILL.md` § Work record)
  differ from Claude Code's project dir in three cases: a submodule or
  `--separate-git-dir` repo keys on its git dir, not the checkout; a path
  over 200 characters, which Claude Code truncates and suffixes with a hash;
  and a non-BMP character, one `-` against Claude Code's two. 0 of 156 dirs
  under `~/.claude/projects` hit the last two. Hook and skills agree, so only
  co-location with that tree's transcripts breaks. **Options:** (a) leave
  it; (b) mirror Claude Code's truncation and UTF-16 replacement in the hook
  and both skills. **Default if nothing is decided:** (a). No test — design.

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
  Pre-commit hands the scan every staged `.md` (`files: \.md$`,
  `.pre-commit-config.yaml:14`), while `make skills-frontmatter` and CI walk
  the tree through `visible_files()`, which skips hidden directories
  (`hooks/skill_frontmatter_lint.py:145`). A tracked `.md` in a hidden dir is
  scanned on commit and skipped by the tree target. Latent: no tracked `.md`
  sits in a hidden dir. **Proposal:** one scope for both — the script drops
  hidden paths it is handed, or the pre-commit pattern excludes them.
  Changes the scan's input contract — needs sign-off; no test — design.

- **SKILL-LINT-ORPHAN-WALKS-HIDDEN-DIRS** (LOW, correctness) — CONFIRMED at
  HEAD 2026-10-10. `sibling_docs` (`hooks/skill_frontmatter_lint.py:365`)
  collects a skill's docs with `rglob('*.md')`, hidden dirs and git-ignored
  paths included, while `visible_files()` skips both for the tree walk
  (`:145,150`). Pytest run from inside the skill leaves an ignored
  `.pytest_cache/README.md` there, and `make skills-frontmatter` and the
  pre-commit lint exit 2 on it as a `skill-orphan`; an ignored
  `skills/<x>/tmp/notes.md` fails the same way. Reproduce: `cd
  skills/recall-memories && uvx pytest -q test_recall.py`, then `make
  skills-frontmatter`. **Fix:** skip hidden path parts and git-ignored paths
  in `sibling_docs`, as `visible_files()` does. No test yet.

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

- **SETTINGS-PR-ATTRIBUTION-SAYS-LAST** (LOW, config) — proposed, needs
  sign-off. `settings-recommended.json` sets `attribution.pr` to `"🤖"`, so
  every session's harness reminder reads "End pull request descriptions
  with: 🤖" while WISDOM § Git puts the robot first and the lint refuses it
  last; WISDOM wins by precedence and the hook enforces it, at the cost of a
  contradicting reminder in every session. **Proposal:** set `attribution.pr`
  to `""` once a logged-in `claude -p --settings '{"attribution":{"pr":""}}'`
  shows the reminder drops its PR line rather than falling back to the
  `Generated with [Claude Code]` footer (unverified here: the nested probe
  was not logged in); then `kronael/sync/reference.md` § Settings and
  `kronael/sync/SKILL.md` step 5 name the new value. No test — config.

- **GH-GATE-REST-CREATE-UNCHECKED** (LOW, hooks) — CONFIRMED at HEAD
  2026-10-14. `POSTS` in `hooks/gh_text_lint.py` matches a `gh api` call on
  `pulls/<N>` or `issues/<N>` but not the create routes, so `gh api -X POST
  repos/<o>/<r>/issues -f body=…` and `… /pulls -f body=…` post a body the
  lint never sees (`command_reason` returns None). **Fix:** two `POSTS`
  entries for `API + r'\b(?:issues|pulls)(?![\w/])'`, kind by the path, body
  required; test in `REFUSED` with a body lacking the opener.

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
  the scope is a judgment call. Also `settings-recommended.json:22` keeps a
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

- **GH-LINT-DISTILL-COUNTS-THE-TITLE** (LOW, correctness) — CONFIRMED at
  63ad23b. `lint` (`hooks/gh_text_lint.py:213`) flags `DISTILL cut nothing`
  only when the body is at least as long as the whole draft, and pr-draft
  step 2 writes the title into `tmp/pr-draft.md` above the body, so a body
  the cut left untouched passes by the title's length:
  `lint(Kind.PR, body, draft='fix: X\n\n' + body)` → `[]`. Measured:
  `hooks/test_gh_text_lint.py::test_lint_pr_draft_ratio_ignores_the_draft_title`.
  **Fix:** compare against the draft below its title line, or require a
  real cut ratio (the `ok:` line already prints one).

- **HOOKS-ENV-NAMES-UNDOCUMENTED** (LOW, docs) — CONFIRMED 2026-10-16, no
  test — docs. `KRONAEL_IN_CODEX` is stripped in `hooks/test_stop.py` and read
  by no hook; `KRONAEL_CODEX_HOOK_DEBUG` (`codex_hook.py`) appears in no doc.
  **Fix:** drop the first; name the second in `hooks/ARCHITECTURE.md`.

- **RECLAUDE-MD-UNREAD** (LOW, dead file) — proposal, needs sign-off. No hook
  reads `RECLAUDE.md`: Claude Code discards a PreCompact hook's
  `systemMessage` (hooks reference, PreCompact) and the hook that injected it
  is gone, yet the file stays in the bundle because `kronael/sync/SKILL.md`
  § Steps 0 and `reference.md` § Classify and § Swap name it as a bundle path.
  **Proposal:** drop `RECLAUDE.md` from the repo, the sync's bundle list, the
  classify loop and the swap tar in one commit; the sync then moves the live
  copy to `RUN/old`.

- **KVS-SESSIONS-NEVER-PRUNED** (LOW, design) — needs sign-off. Every hook
  session leaves its keys (`prompted`, `caveman`, `memory:*`, `pointed:*`)
  in `kvs` for good; only TTL keys expire. `kvs sessions` lists them, nothing
  removes a session whose Claude Code transcript is gone. **Options:** (a) a
  `kvs` sweep of sessions older than N days; (b) leave; the rows are small.
  **Default if nothing is decided:** (b).

- **CI-SKIPS-RECALL-LINTS-AND-SKILL-DRIVEN-HOOK-TESTS** (LOW, config) —
  CONFIRMED 2026-10-12, no test — config. Root `make test` runs
  `skills/recall-memories/test_recall.py` (`Makefile:66`), but no workflow
  runs root `make test` or `make lints` (`grep -rn recall .github` is empty);
  `test-hooks.yml` triggers on `hooks/**` only while
  `hooks/test_prompt_nudge.py:40,48` reads `skills/*/SKILL.md`, so a push
  touching only `skills/` skips it. `make spec-lint` stays out of CI: it
  needs `SPECS=<dir>` and this repo keeps no specs. **Fix:** add
  `test_recall.py` and `make lints` to `lint.yml.tmpl` and `skills/**` to
  the hooks path filter.

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

- **SETTINGS-ASK-RULES-VS-WISDOM-GIT-TEXT** (LOW, config) — owner decision,
  no test — config. (i) `skills/global/SKILL.md:131-138` gates a push to
  `<default head>`, a merge and an approval, and says opening a PR needs no
  approval; `settings-recommended.json` has no `allow` rule for `rip -g` or
  `gh pr create`, and with `"defaultMode": "default"` (`:37`) any Bash command
  outside `allow` still prompts, so removing `gh pr create*` from `ask`
  changed nothing in that mode. (ii) The ask rules hard-code
  `refs/heads/master` and `refs/heads/main` (`:25-26`) while the text resolves
  `<default head>` from `git ls-remote --symref origin HEAD`
  (`skills/global/SKILL.md:117`), so a repo whose default head is `trunk` is
  unguarded, and the trailing `*` makes `refs/heads/master-fix` ask (a dated
  `refs/heads/20261013_master-fix` does not match). (iii) `rip -g
  v1:refs/tags/v1`, the tag push `skills/release/SKILL.md:131` calls the
  publication, matches no ask rule. (iv) The permissions docs state a Bash rule matches the
  command text as written, after wrapper stripping, so `~/.local/bin/rip -g …`
  or `env X=1 rip -g …` meets no rule either. **Options:** (a) add `allow` rules for
  `Bash(rip -g *)` and `Bash(gh pr create*)`, an `ask` rule for `rip -g
  *refs/tags/*`, and the default-head rule per repo in project settings;
  (b) leave the rules and let the WISDOM text say the settings default
  prompts. **Default if nothing is decided:** as written.

- **PROMPT-NUDGE-UNNUMBERED-SPEC-EXAMPLE** (LOW, docs) — open (record only),
  no test — docs. `hooks/prompt_nudge.py:18` gives `specs/multi-tenancy.md`
  as the example of a lowercase doc name, which teaches an unnumbered spec
  file against the `NN-topic.md` numbering in `skills/specs/format.md`.
  **Fix:** a numbered example, or a non-spec path such as `docs/setup.md`
  alone.

- **GH-GATE-SUBMIT-REVIEW-READS-CLAUDE-TRANSCRIPTS-ONLY** (LOW, correctness) —
  open (record only). `prompt_text` in `hooks/gh_text_lint.py` accepts only a
  Claude Code transcript record (`type: user`, `message.content` text blocks),
  so under Codex a review submit is refused even after the user typed SUBMIT
  REVIEW: a Codex `response_item` record with `payload.role: user` and
  `input_text` content yields `None`, and `command_reason` answers `review
  submit refused`. Upstream v0.4.42–v0.4.48 replaced the transcript read with a
  permission dialog (`command_decision`, see HOOKS-UPSTREAM-REDESIGN-HELD-BACK).
  **Fix:** read the Codex record shape too, keeping the newest-message check;
  or adopt the dialog with the redesign. Measured by hand with
  `iter_lines_reversed` stubbed to one Codex record; the test is still to write.

- **HOOKS-TEST-HOOKS-PY-STALE** (LOW, dead code) — CONFIRMED at HEAD 2026-10-16.
  `hooks/test_hooks.py` is a standalone script, not in `hooks/Makefile`
  `TEST_FILES`, so `make -C hooks test` never runs it; run by hand it ends
  16/27 with 11 `nudge.py` cases failing because `hooks/nudge.py` is a retired
  name (`kronael/sync/reference.md` § Classify `RETIRED`). Its `local.py`
  cases pass and `hooks/test_local.py` now covers that hook in the suite.
  **Fix:** delete the script, or cut it to the cases no listed test covers and
  list it. No test — dead code.

- **HOOKS-PRECOMPACT-HAS-NO-CONTEXT-CHANNEL** (HIGH, correctness) — needs
  sign-off. `local.py` (compaction branch), `reclaude.py:177` and
  `memory_nudge.py:227` answer PreCompact with `{"ok": true, "systemMessage":
  ...}`. The hooks reference gives PreCompact only `decision: "block"` and
  `reason`, lists `hookSpecificOutput.additionalContext` for SessionStart,
  UserPromptSubmit, the tool events, Stop and PostModelSwitch but not
  PreCompact, and sends every other event's stdout to the debug log; so the
  re-injection of LOCAL.md and RECLAUDE.md at compaction and the compaction
  memory nudge reach neither the model nor the user. Worse, `memory_nudge.py:105`
  then writes the `memory-nudge-done` marker, so the Stop fallback (`:128`)
  stays silent for the rest of any session that compacted. `codex_hook.py
  PreCompact local|reclaude` prints nothing either, so the two Codex PreCompact
  entries are no-ops. `hooks/test_local.py` and `hooks/test_memory_nudge.py:35`
  pin the discarded shape. **Options:** (a) move the three to a SessionStart
  hook with matcher `compact`, which the reference says reads
  `additionalContext` and plain stdout; (b) drop the PreCompact entries and the
  claims in `hooks/README.md` and `hooks/ARCHITECTURE.md`. Either way the
  PreCompact branch stops writing the `done` marker. **Default if nothing is
  decided:** as written, with this entry as the warning. Measured by hand with
  the PreCompact payload; no test asserts delivery.

- **HOOKS-PRETOOL-BLOCK-USES-TOP-LEVEL-DECISION** (MED, correctness) — open
  (record only). `pretool_nudge.py:152,157,277` block an unsafe command or a
  failing GitHub text with top-level `{"decision": "block", "reason"}`; the
  hooks reference documents PreToolUse control as
  `hookSpecificOutput.permissionDecision` (`allow|deny|ask|defer`) with
  `permissionDecisionReason`, and the top-level pair only as a deprecated alias
  that maps `block` to `deny`. The gate works while the alias lives. **Fix:**
  emit the `hookSpecificOutput` form and update the `decision` check and the
  tests; Codex accepts both.

- **HOOKS-CODEX-APPLY-PATCH-READS-PATCH-KEY** (MED, correctness) — open
  (record only), unverified live. `pretool_nudge.py:106` reads
  `tool_input["patch"]` for `apply_patch`, and `test_codex_hook.py:43-50` and
  `test_pretool_nudge.py:73-104` fixture the same key; the Codex hooks
  reference says `Bash` and `apply_patch` carry `tool_input.command`. A Codex
  patch payload with `command` produces no nudge. **Fix:** read `command`,
  keep `patch` while a Codex build still sends it, fixture both; one probe hook
  under a throwaway `CODEX_HOME` settles which key arrives.

- **HOOKS-STATE-TWO-PATHS** (LOW, duplication) — open (record only).
  `pretool_nudge.py:284-286` keeps its once-per-session cache at
  `~/.claude/tmp/extnudge/<sid>.txt` and ignores `lib/state.py` and
  `KRONAEL_HOOK_STATE`, which the other hooks use; `stop.py:79-87` re-implements
  `hook_event`. A test that sets `KRONAEL_HOOK_STATE` still writes under the
  real home. **Fix:** `session_state('extnudge', sid)` and `lib.state.hook_event`.

- **HOOKS-UNWRITABLE-STATE-DEFAULTS-DIFFER** (LOW, correctness) — open (record
  only). With an unwritable state dir `local.py:50` treats every prompt as the
  first and injects LOCAL.md each time, while `prompt_nudge.py:152` stays
  silent. **Fix:** one rule for both; injecting every prompt is the loud one.

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
  `rig/rig:328`). An unlisted command still gets the default prompt, but an
  allow rule that admits them pushes with no ask gate left. **Fix:** an ask
  rule for the rig push forms; which forms, and whether to gate them at all,
  is the maintainer's call.

- **RIG-HELP-EXITS-1** (LOW, ux) — CONFIRMED 2026-10-10. `rig/rig:353`
  routes `-h|--help|help` to `usage()`, which ends in `exit 1` (`:321`), so
  `rig --help` fails in a pipeline, and the unknown-command error (`rig/rig:389`)
  goes to stdout, not stderr. **Fix:** exit 0 on an explicit help
  request.

- **RIG-MAKEFILE-STALE-NAME-CLEANUP** (LOW, dead code) — owner decision.
  `rig/Makefile:7-12` removes retired `gt*`/`gb`/`gpo` symlinks under
  `~/.local/bin` and `~/bin`; `cmd_install` (`rig/rig:268-287`, proven by
  `rig/test.sh:296-312`) already removes every stray symlink to `rig` in the
  install dir, so only the `~/bin` line and non-symlink entries do anything.
  **Default if nothing is decided:** keep until a host without the old names
  is confirmed.

- **RIG-PUSH-G-USER-RULE-TIES-ON-FULL-URL** (LOW, correctness) — open
  (record only). `rip -g` passes `-c url.<url>.insteadOf=<url> -c
  url.<url>.pushInsteadOf=<url>` (`rig/rig:291`) and its help promises to beat
  only a rule on a shorter base (`rig/rig:247`, `rig/README.md:172-174`). A
  user rule whose base is the exact full HTTPS URL ties with them, and the
  user's rule wins. Measured: `GIT_CONFIG_GLOBAL` holding `[url
  "git@github.com:o/r.git"] pushInsteadOf = https://github.com/o/r.git`, origin
  set to that HTTPS URL, then `git -c url.<url>.insteadOf=<url> -c
  url.<url>.pushInsteadOf=<url> remote get-url --push origin` printed
  `git@github.com:o/r.git`. The xfail test in `rig/test.sh` is still to write.
  **Fix:** a lookup that refuses when the URL comes back rewritten.
  `git ls-remote --get-url <url>` applies `insteadOf` only: it printed the
  unrewritten HTTPS URL in the same setup, so the push side needs
  `git remote get-url --push` against a remote set to the URL.

- **RIG-FETCH-G-REFSPEC-UNCHECKED** (LOW, design) — owner decision. The refspec
  shape check in `cmd_gh_op` runs only for push (`rig/rig:272`), so `rif -g`
  forwards any refspec: `rif -g -n ':refs/heads/x'`, `'+refs/heads/*:refs/heads/*'`
  and `''` all print a fetch command and exit 0, and `git fetch <url> :refs/heads/x`
  creates a local branch, which WISDOM § Git forbids. `GH_HELP` (`rig/rig:242-251`)
  says both commands refuse "deletes", which reads as the refspec form but means
  the `-d`/`--delete` flags; `rig/README.md` § Push and fetch with the gh token
  states the push-only shape check correctly. **Options:** (a) `rif -g` refuses an
  empty source and a destination outside `refs/remotes/`; (b) keep fetch open and
  reword `GH_HELP` to "the force, --tags, --all, --mirror and delete flags".
  **Default if nothing is decided:** (b), the wording. No test — design.

- **RIG-INSTALL-REPORTS-FAILED-LINK** (LOW, correctness) — open (record only).
  `cmd_install` (`rig/rig:303-322`) has no `set -e` and echoes after each
  `ln -sf` (`:306`) and `rm -f --` (`:319`) whatever they returned. In a directory
  made read-only, `rig install` printed `installed 24 symlinks` and `removed
  <dir>/ghpush` beside 25 `Permission denied` lines and exited 0, with the stale
  link still present. **Fix:** fail loud — exit non-zero on the first failed
  `ln`/`rm`, and echo only after success. Measured by hand; the test is still
  to write.

- **RIG-INSTALL-CLEANUP-TARGET-SHAPES** (LOW, correctness) — open (record
  only). The stray-link sweep (`rig/rig:313-321`) matches a link only when
  `readlink` returns exactly `rig` or `$dir/rig`: links written as `./rig`,
  `../<dir>/rig`, `rig/`, or through a symlinked parent directory survive, while
  any unlisted link to rig is deleted — a user's own `rig2 -> rig` too — and
  neither `rig/README.md` nor the help says so (`README.md` § How It Works says
  only that `rig install` owns the symlink list). The comments at `rig/rig:310`
  and `rig/test.sh:321` narrate history ("leftovers of a dropped alias", "no
  longer ships") where WISDOM § Documentation wants the present rule. **Fix:**
  compare `readlink -f "$l"` with `readlink -f "$dir/rig"`, document that every
  unlisted link to rig in the install dir is removed, and reword the two
  comments. `rig/test.sh` covers the relative and the absolute shape only.

- **RIG-URL-EMPTY-PATH** (LOW, correctness) — open (record only).
  `github_https_url` (`rig/rig:218-234`) accepts an origin whose path is empty:
  `git@github.com:` and `ssh://git@github.com:22/` both yield
  `https://github.com/.git`, so `rip -g -u` prints a URL no push can use and
  `rip -g` fails inside git instead of at the parser. **Fix:** refuse an empty
  `path` after the `case`, with the "not a GitHub remote" error.

## kvs

- **KVS-PARALLEL-INCR-SQLITE-BUSY** (MED, correctness) — CONFIRMED at HEAD
  2026-10-16. `kvs/main_test.go::TestParallelIncrLosesNoUpdate` runs 16
  processes doing 25 `incr` each; 3 runs in 8 here fail with `kvs: database is
  locked (5) (SQLITE_BUSY)` (exit 9) and `make test` goes red with it; upstream
  CI passed one run at v0.4.48. `TestTTL` (`main_test.go:174`) sets a key with
  a 1 s TTL and reads it back after two more commands; under load (the race
  detector plus other work on the host) the read came back absent once in 8
  runs. **Fix:** the store waits on `SQLITE_BUSY` (a busy timeout or a retry
  around the write in `kvs/store.go`) so parallel writers queue instead of
  failing; the TTL test uses a margin wider than its command latency.
  Measured: `kvs/main_test.go::TestParallelIncrLosesNoUpdate`,
  `kvs/main_test.go::TestTTL`.

## spec-lint

- **SPEC-LINT-PHASED-CORPUS-NO-INDEX-INVISIBLE** (LOW, correctness) —
  CONFIRMED 2026-10-13. `is_spec_corpus` (`spec-lint/spec_lint.py:151-159`)
  globs top-level `*.md` only, so a `specs/` that keeps its files in phase
  directories and has no `specs/index.md` is no corpus to discovery or to a
  changed-file run. Measured in a fresh repo holding `specs/1/2-webhooks.md`:
  `spec-lint specs/1/2-webhooks.md` prints "no spec corpus" and exits 0, while
  `spec-lint specs` exits 1 with `spec-index-row`. A pre-commit hook that
  passes changed files passes a corpus the explicit run fails. The xfail test
  in `spec-lint/test_spec_lint.py` is still to write. **Fix:** count a
  numbered file one phase directory down (`*/*.md`) as well.

- **SPEC-LINT-INDEX-ROW-SHAPE-NOT-STATED** (LOW, correctness) — owner
  decision. `check_one_index` (`spec-lint/spec_lint.py:489-491`) skips a row
  with fewer than three cells and reads the spec link from the first cell. An
  index row `| 2 | [2-webhooks.md](1/2-webhooks.md) | planned | hooks |`
  under a `| # | Spec | Status | Summary |` header, or a two-column index,
  yields a false `spec-index-row` "no row" (`:533-536`) while the row exists
  (measured). `skills/specs/format.md` § Naming and index shows only the
  three-column shape. **Options:** (a) widen the reader to find the link and
  the Status cell in any column; (b) state the three-column shape, link
  first, as the contract in `format.md`. **Default if nothing is decided:** as
  written. The xfail test for (a) in `spec-lint/test_spec_lint.py` is still to
  write.

- **SPEC-LINT-POINTER-NOISE-SLASH-TOKENS** (LOW, correctness) — measured on a
  160-warning corpus 2026-10-13, 43 of them new since the pointer rule
  accepted extension-less slash paths. `pointer_path`
  (`spec-lint/spec_lint.py:296-313`) takes any slash token, so prose such as
  `turn/start`, `3/7`, `net/http.Server` and `kronael/candle` warns
  `spec-pointer`. `AT_LINE` (`:76`) accepts only `-`, so `src/file.tsx:96–106`
  with an en-dash warns "does not resolve" while `src/file.tsx:96-106`
  resolves (measured against a 200-line file). The xfail test in
  `spec-lint/test_spec_lint.py` is still to write. **Fix:** treat an
  extension-less slash token as a pointer only when its first segment is an
  existing directory of the repo, and let `AT_LINE` take `-` or `–`.

- **SPEC-LINT-UNREADABLE-TARGET-RAISES** (LOW, correctness) — open (record
  only). On Python 3.13 and older `Path.exists()` and `read_bytes()` raise
  `PermissionError` on a target under an unreadable directory (measured on
  Python 3.11.2: a `chmod 000` directory and a spec citing `locked/x.py` end
  in `PermissionError: [Errno 13]`). `walk` skips such directories
  (`is_skipped_dir`, `spec-lint/spec_lint.py:163-167`), but `resolve_pointer`'s
  `(base / pointer).exists()` (`:368`), a link's `named.exists()` (`:480`,
  `:545`) and `line_count`'s `read_bytes()` (`:348`) still raise when a spec
  points into one. The xfail test in `spec-lint/test_spec_lint.py` is still to
  write. **Fix:** catch `PermissionError` at those four sites and report the
  pointer as unresolved.

## qemubox

- **BOXES-SHARE-CLAUDE-RUNTIME-STATE** (MED, design) — needs sign-off.
  VMs bind the whole `~/.claude` rw (`qemubox/qemubox` `assemble_mounts`). It holds persistent state the
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
  become per-box tmpfs like `sessions/`. Tradeoffs: the
  host's agent view stops listing box background sessions (it already
  cannot attach to them: their sockets are box-private), `tasks/` output of
  a box's subagents dies with the box, and the list is version-bound, so it
  needs re-checking on Claude Code upgrades. A contract change; not shipped.

- **BOX-OPUS-XHIGH-RATIONALE-GONE** (LOW, design) — proposed.
  `qemubox/qemubox` launches the
  `opus` alias and the bare default at `--effort xhigh`; the help text
  (`qemubox/qemubox`, `qemubox/README.md`) and
  `qemubox/test-parity.sh` pin it. The one reason on record (CHANGELOG
  v0.3.35: the launcher matches the opus subagent) contradicts
  `agents/opus.md:4`, which pins `high`. **Proposal:** either align the
  launcher to `high` (script, help, README, test) or state the box's own
  reason for xhigh. Owner's call.

- **QEMUBOX-IMAGE-PACKAGES-UNUSED** (LOW, design) — owner decision, no test —
  design. `qemubox/Dockerfile` installs `ipset` and `aggregate`;
  no script in the repo calls them. `iptables` supports guest Docker;
  `iproute2` and `dnsutils` give the guest `ip`, `ss` and `dig`.
  **Options:** (a) drop `ipset aggregate` at the next image rebuild;
  (b) keep both. **Default if nothing is decided:**
  (b).

- **QEMUBOX-MAN-CACHE-OWNERSHIP** (LOW, ops) — confirmed in the production
  guest, no test — ops. The rootfs export collapses every image owner to
  guest root in `qemubox/qemubox:900`. The man-db trigger runs as `man` and
  cannot update the root-owned directories under `/var/cache/man`; package
  installation succeeds but prints permission errors. **Fix:** give the
  manual cache its service ownership on the writable guest filesystem.

- **QEMUBOX-ACCELERATION-LOG-USES-LAUNCHER-GROUPS** (LOW, ops) — open,
  no test — ops. `start_box` checks KVM access in the launcher while
  `run_qemu` checks it in the user manager at `qemubox/qemubox:623,723`.
  When only the manager has a newly added KVM group, the launcher says
  software emulation but QEMU runs with `-enable-kvm`. **Fix:** report
  acceleration from the process that starts QEMU. Deferred as a temporary
  group-membership mismatch.

- **QEMUBOX-KERNEL-PRUNE-DURING-LAUNCH** (LOW, ops) — open, no test — ops.
  `run_qemu` reads `base/kernel/current` before it waits for share sockets
  at `qemubox/qemubox:708`. A concurrent kernel rebuild can publish a new
  pointer and `prune_bases` can delete the selected artifacts before QEMU
  opens them at `qemubox/qemubox:1131`. Source review only; no runtime
  reproduction. A launch then fails with a missing kernel or initrd.
  **Fix:** retain the selected artifacts through launch. This rare race
  remains deferred under the disposable-VM policy.

- **QEMUBOX-SSH-READS-TERMINAL** (LOW, ux) — open (record only), no test.
  `ssh_plain_box` (`qemubox/qemubox:548`) runs `ssh` without `-n`, so every
  helper SSH call reads the terminal. A `qemubox rm <box> &` job stops on
  SIGTTIN at the `fstrim` call and looks like it waits for input until `fg`.
  On 2026-10-21 both the `fstrim` and the `poweroff` SSH calls then failed,
  cause not found, and `rm` sat the full 90 s guest wait before QMP `quit`.
  Part 3 runs the shutdown as `ExecStop` with no terminal; the other helper
  calls (`ls`, start-up) keep the read. **Fix:** `ssh -n` in `ssh_plain_box`,
  except the calls that feed a heredoc.

- **QEMUBOX-9P-TO-VIRTIOFS** (MED, design) — needs sign-off.
  Host paths reach the guest over 9p (`qemubox/qemubox:596`, `:761`,
  mount at `:805-808`). 9p is slow on many small files and weak on locks and
  mmap, so the Codex SQLite DB must live in the guest `/tmp`. virtiofs fixes
  both; `virtiofsd` is installed here at `/usr/lib/virtiofsd`. **Fix
  (proposal):** per share, start one `virtiofsd --socket-path=<box>/<tag>.sock
  --shared-dir=<src>` (plus `--readonly` for ro), add
  `-chardev socket,id=<tag>,path=<sock> -device vhost-user-fs-pci,chardev=<tag>,tag=<tag>`,
  and back guest RAM with `-object memory-backend-memfd,id=mem,size=$MEM,share=on
  -numa node,memdev=mem` (vhost-user needs shared memory); the guest mounts
  `-t virtiofs <tag> <dest>`. `stop_box` kills the daemons; the base kernel
  needs `CONFIG_VIRTIO_FS`. Open: the guest identity mapping that
  `security_model=none` gives 9p, and memfd with a 64 GiB guest.
  Mac: QEMU's virtiofs needs `virtiofsd`, which is Linux-only (unverified);
  on macOS virtiofs comes from Virtualization.framework, a second backend.

- **QEMUBOX-NO-SERVICE-MANAGER** (MED, design) — needs sign-off.
  A VM lives as a detached QEMU process that qemubox starts on first attach;
  nothing restarts it after a pause, a crash or a reboot, and stop/start go
  through the qemubox CLI only. **Fix (proposal):** a systemd user template
  `qemubox@.service` (`ExecStart` = qemubox boot-only for `%i`, `ExecStop` =
  `qemubox stop %i`, `Restart=on-failure`), plus `qemubox enable|disable
  <name>`; the CLI attach then only connects over SSH. A path or timer unit
  could resume `io-error` guests when free space returns. With
  QEMUBOX-9P-TO-VIRTIOFS, each share becomes `qemubox-fs@<box>-<tag>.service`
  (one `virtiofsd`) that `qemubox@<box>` Requires and orders After, so
  systemd starts and stops the daemons with the VM and qemubox drops its PID
  and kill logic; a `-v` share on a running VM goes through
  `systemd-run --user`. Open: the 4h idle prune and `qemubox stop` must stop
  the unit, never kill the process, or systemd restarts the VM. Linux only;
  a Mac port would need launchd.

- **QEMUBOX-NO-EGRESS-FILTER** (HIGH, hardening) — needs sign-off.
  `qemubox/README.md:227-233` states the gap plainly — live `~/.claude` /
  `~/.codex` tokens are shared read-write with the guest, outbound is open unless `-H`,
  and "the path for exfiltration is open". `-H` is all-or-nothing: an agent
  that needs `api.anthropic.com` gets the whole internet with it. An in-guest
  sandbox cannot close this: the guest mounts agent config read-write at
  the host paths (`qemubox/README.md:174-179`) and the guest user has
  passwordless sudo (`:236`), so anything in the guest can widen its own
  limits. Only a host-side wall holds, and qemubox already sits on one: slirp,
  with `restrict=on` at `qemubox:713`. **Fix (proposal):** a fixed-at-boot
  flag `-p host1,host2` alongside `-H`: start a host proxy on
  `127.0.0.1:$pport` with the allowlist, add
  `,restrict=on,guestfwd=tcp:10.0.2.100:3128-tcp:127.0.0.1:$pport` to the
  `-nic` at `qemubox:734`, and put `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` into
  `envs` so `send_envs` (`qemubox:1326-1332`) carries them.
  Claude Code honours those variables. `stop_box` kills the pid, `remove_box`
  removes the files. Roughly 40-60 lines of shell plus docs and three parse
  assertions in `test.sh`. Under `restrict=on` the guest cannot reach slirp's
  DNS, so the host proxy resolves names and there is no UDP/53 side channel.
  Unmeasured: that slirp actually drops guest DNS under `restrict=on` — the
  documentation says the guest is "not able to contact the host", and no one
  has tested it here, because this box has no `/dev/kvm` access.

- **QEMUBOX-TMP-BOX-LINGERS** (LOW, design) — owner decision. A `-T` box
  (`qemubox/qemubox:1491`) lingers like any other: after its session exits,
  `qemubox-tmp` keeps `/tmp/work` on the guest tmpfs for `QEMUBOX_LINGER`
  seconds (default 1200), and a second `qemubox -T` in that window joins the
  VM and finds the earlier scratch files, while `qemubox/README.md:71-74`
  says only that power-off clears `/tmp/work`. **Options:** (a) `LINGER=0`
  for `-T` unless `QEMUBOX_LINGER` is set explicitly; (b) document the
  window in README § Usage. **Default if nothing is decided:** (b). No test
  — design.

- **QEMUBOX-TMP-STACKED-TMPFS** (LOW, ops) — open (record only), no test —
  ops. `setup_guest_tmp` (`qemubox/qemubox:591-594`) mounts a tmpfs over
  `/tmp` on every boot, and systemd's `tmp.mount` already mounted one there,
  so guest `/tmp` is two stacked tmpfs mounts and the first is hidden.
  Unverified here: no VM was booted. Check with `findmnt /tmp` in a guest.
  **Fix:** size the existing mount with `mount -o remount,size=75% /tmp`
  instead of stacking a second one.

- **QEMUBOX-CODEX-MEMORIES-PRIVATE-DB** (MED, correctness) — open (record
  only), unverified, no test — correctness. Each session sets
  `CODEX_SQLITE_HOME=/tmp/codex-sqlite` (`qemubox/qemubox`, where `envs` is
  built), so a guest Codex reads a private `memories_1.sqlite` but writes the
  memory files in the shared `~/.codex/memories`. With Codex memories
  enabled, consolidation syncs those files to its own database and deletes
  summaries the database lacks (Codex 0.162.0,
  `codex-rs/memories/write/src/storage.rs`), so a guest can delete memories
  the host wrote. Inert while memories are off: no `config.toml` key enables
  them and `~/.codex/memories` is empty. **Fix:** turn memories off for the
  guest Codex, or keep its memory files on the guest disk too.

## diskclean

- **DISKCLEAN-LINKED-TOOLCHAIN** (HIGH, data loss) — level 2 uninstalls a
  linked rustup toolchain whose name starts with a version. The filter
  `^[0-9.]+-[^ ]+$` in `level2` (`diskclean/diskclean`) matches a toolchain
  such as `1.89.0-sbpf-<vendor>-v1.54`, which is a symlink into another
  tool's install; `rustup toolchain uninstall` then breaks that tool.
  **Fix:** skip every toolchain whose dir under `$(rustup show home)/toolchains`
  is a symlink (`-L`), and cover it in `test.sh` with a symlinked fixture.

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

- **ROOT-MAKE-FORCED-CI-TREATS-TEMPLATE-AS-PROJECT** (LOW, config) — open,
  no test — config. `make -B gen-ci` selects the root `test-%` pattern
  while remaking `.github/templates/test-go.yml.tmpl`. The recipe runs
  `make -C .github/templates/go.yml.tmpl test` and fails before generating CI.
  **Fix:** constrain project test targets so template names cannot match them.

- **ROOT-MAKE-CLEAN-UNINSTALLS** (LOW, docs) — CONFIRMED 2026-10-10, no
  test — docs. Root `make clean` runs each project's `clean`; `bhctl`,
  `qemubox` and `rig` delete their installed binaries (and rig's symlinks),
  `udfix` and `gloww` only clean
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
  `skills/ship/cli.md` has the owner read the whole diff after a run until (2) and (3) land. Waits for
  the owner's sign-off. Recorded 2026-10-06.

- **SHIP-CLI-ONE-MODEL-FOR-ALL-ROLES** (LOW, ship) — RECORDED 2026-10-13.
  `skills/ship/cli.md` states that the `ship` CLI runs every role (spec
  validator, planner, worker, judge) on one `--model` (env `MODEL`, default
  `sonnet`). WISDOM § Agents routes planning to `opus`, steps to `sonnet` and
  specs or red reviews to `fable`, so the CLI cannot follow the routing: a
  run on `sonnet` plans and judges on the implementer tier, and a run on
  `fable` makes it the implementer. **Fix:** in kronael/ship, a model per role
  (planner `opus`, worker `sonnet`, validator and judge `fable` or `opus`).
  The CLI default stays `sonnet` until then. No test — the model is a CLI flag.

- **SHIP-CLI-TRACE-LOG-IN-TREE** (LOW, ship) — RECORDED 2026-10-10. The
  `ship` CLI (kronael/ship) writes its trace log under the working
  directory's `.ship/`: `ship/claude_code.py:333` hard-codes
  `.ship/log/trace.jl` apart from `DATA_DIR` and `LOG_DIR`
  (f6b4859614e8cc33af347ec687994f17e28a96d7; `ship.log` and the lock follow
  `DATA_DIR`, `config.py:165-166`). With
  `DATA_DIR` moved out of the tree (`skills/ship/cli.md`), that log is the
  one `.ship/` a repository still acquires. **Fix:** in kronael/ship, write
  the trace log under `DATA_DIR`; then drop `/.ship/` from this repository's
  `.gitignore`. Waits for the owner.

## Ruled not a defect

- **QEMUBOX-DOCKER-VM-BOUNDARY** (LOW, design) — not a defect. Guest Docker
  uses the VM's process and network boundaries. It needs no extra isolation
  mode or flag. `-D` explicitly selects host Docker through socket forwarding.

- **BOXES-DOCKER-SOCKET-CROSSES-BOXES** (MED, isolation) — not a defect.
  Qemubox's `-D` forwards the host Docker socket over SSH. The agent can then
  manage host containers. Project `.qemuboxrc` cannot set `-D`; the flag is an
  explicit grant of host access. Guest Docker uses its own socket without `-D`.

- **QEMUBOX-CREDS-MOUNTED-RW** (MED, hardening) — not a defect. Qemubox shares
  `~/.claude` and `~/.codex` rw, API tokens included (`qemubox/qemubox` `assemble_mounts`).
  Claude Code and Codex both rewrite their token files on login refresh, so a
  ro or redacted token breaks auth inside the box. The README already says
  qemubox is not a boundary for hostile code with shared credentials.

- **SKILL-LINT-NO-ORG-REF-CHECK** (LOW, coverage) — not a defect. `CLAUDE.md`
  bans local paths, org-specific refs and secrets in source;
  `hooks/skill_frontmatter_lint.py` checks the first and the last, and nothing
  checks the second: a pattern for an org ref would have to name the org,
  which is the string the rule exists to keep out of the repo. The rule stays
  a review check.
