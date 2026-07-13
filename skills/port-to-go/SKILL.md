---
name: port-to-go
description: "Faithful into-Go transcode: port any source language to Go preserving behavior exactly, proven by differential traces. NOT for idiomatic Go rewrites (use go) or broad engineering runbooks (use software)."
when_to_use: "port to Go, transcode to Go, into-Go port, faithful port, 1-to-1 translation, byte-for-byte parity, differential testing, differential harness, golden trace, language parity, Python to Go, TypeScript to Go, JS to Go, RNG desync, map iteration nondeterminism, bankers rounding, floating-point 1-ULP divergence, behavioral-fidelity seams, worktree oracle, refactor mirror, crash-vs-guard, scale and tier, N-way component parity"
---

# Faithful Into-Go Transcode

Use this when a Go target must match a source program's behavior EXACTLY. Speed
is allowed; semantic redesign is not. The source language can be anything —
this skill is the language-agnostic method; the per-language behavioral quirks
live in a sibling file you load alongside it.

## Language library

The method below is generic. The seams where a source language behaves unlike
Go's naive equivalent (RNG, rounding, iteration order, serialization, strings)
are language-specific and live in cold-loaded companion files:

- **`py.md`** — Python → Go seams (bool-is-int, `enum.value`, PCG64/MT19937,
  ties-to-even `round()`, compensated `sum()`, dict insertion order, cgo-libm).
- **`ts.md`** — TypeScript/JavaScript → Go seams (all-`number`-is-float64,
  int32 bitwise coercion, `Math.round` half-up, unseedable `Math.random`,
  object integer-key ordering, string-sort default, UTF-16 strings).

ALWAYS load the companion for the source language before porting. To add a
language, copy an existing companion's section schema (Type & numeric model /
RNG / Rounding & numeric ops / Iteration & ordering / Equality & null-ish /
Serialization / Strings / Harness invocation / Seam catalogue) and fill it by
EXECUTING the source runtime, never by guessing.

## Quick map

The method is **differential testing** + **golden-trace capture**: run the
source oracle and the Go port on identical input and diff their decision traces
— captured by EXECUTING the source, never by reading source and guessing —
under a BIT-EXACT float gate (no epsilons). Phases 0–7: make the source
deterministic → translate 1-to-1 → scalar parity harness → split the source for
a swappable component → Go drop-in → trace-parity grind → scale and tier → N-way
components. Prime directives: the oracle is the source checked out in the PORT'S
OWN WORKTREE and it is untouchable; gate on decision traces, never output
equality; always fix the FIRST divergence, in execution order, one at a time.

## Phases (run them in this order)

A whole-system parity port has a fixed shape. Skipping a phase costs you days of
phantom divergence-chasing. Order, with the hard-won reason each exists:

0. **Make the source deterministic FIRST (source-side, before any Go).** Replace
   every nondeterminism source in the oracle: unseeded/global RNG → a
   project-owned reproducible generator, unordered-set-based selection →
   an explicit sort on business keys, random UUIDs/clock IDs → seeded IDs. ALSO
   add structured JSONL parity logs at every decision site. These logs ARE the
   cross-language oracle — a full run-log diff covers 100k+ decisions with no
   fixture files. NEVER start the Go port against a source that still draws from
   an unseeded RNG or iterates an unordered collection.
1. **Translate module-by-module (the bulk port).** One source file → one Go file,
   in dependency order (types → config → leaf calcs → core logic → main loop →
   I/O). Keep tests green between modules. This produces faithful *modules*; the
   *glue* that wires them is where divergence will actually live.
2. **Scalar parity harness.** A Go dispatch binary (`cmd/parity`, self-registering
   per module) + source-language tests that shell out to it with identical inputs
   and assert equal. Grow it to ~1000 cases across every module. Adversarial input
   sweeps (ties, clamp boundaries, configured-0.0, NaN/Inf, bool-as-number) find
   the behavioral-fidelity seams in the companion file. This pins leaf functions;
   it does NOT pin the graph-bound orchestrators.
3. **Refactor the source into orchestrator / component / log_reader (source-side).**
   Before the Go component can be a drop-in, the source must split cleanly:
   an orchestrator spawns a *swappable* component subprocess + the real peers;
   reporting reads raw output files. Keep the main loop BYTE-IDENTICAL through this
   refactor (a golden test is the anchor) and prove subprocess == in-process.
4. **Build the Go component as a drop-in for the swappable source component.** Same
   config contract, same raw output format. Mirror the source's concurrency model
   exactly: if the source merges all peer streams through one ordered queue + a
   single dequeue loop, the Go component uses one min-heap (ordered key +
   barrier) and a SINGLE dequeue goroutine — NOT per-connection goroutines.
   Reporting stays source-side; the component emits raw streams only.
5. **Parity grind via matched traces (the long phase).** Run the SAME orchestrator
   with the Go component vs the source component and the SAME real peers. The gate
   is DECISION-TRACE equality, never output equality — verify it BOTTOM-UP, rung by
   rung (inputs → traces → outputs), and fail at the LOWEST diverging rung. Output
   equality is a WEAK gate: an output file can be byte-identical while the traces
   already diverged far upstream — the matching output is coincidental. Diff traces
   key-aligned, find the FIRST divergence (always far upstream of where output
   diverges), fix Go only, repeat. Verify the INPUT is byte-identical before
   chasing outputs.
6. **Verify byte-identity subprocess-vs-subprocess, then SCALE and TIER.** Prove it
   the strict way (real source-component-subprocess vs real Go-component-subprocess
   via one orchestrator), not just in-process. Then enlarge the test — longer
   horizons, higher variance, real production data, production configs — because
   short equivalence hides latent divergences (hardcoded timeouts, sparse-input
   paths, count bugs that only fire deep in a run). Tier it: short/medium/long/max
   rungs selected by config, gated by env so the fast tier runs in CI and the long
   tiers run on demand. Size tiers for ASPECT coverage (cross the periodic-reset
   boundaries, fire the dormant branches) — coverage, not raw length. Scale is not
   optional — every "achieved" result that wasn't scaled was premature.
7. **Generalize to N-way component parity (only after one component is solid).** Once
   the first component is a proven drop-in, port the NEXT the SAME way — 1-to-1,
   same trace instrumentation, same differential harness. The end-state gate runs
   ALL combinations of the swappable components: `{Go,source} × {Go,source}`, every
   combo producing byte-identical output. Each new drop-in must be a FRESH 1-to-1
   port, never a resurrected earlier in-process prototype (that drove a different
   code path and is the wrong comparison). Gate the N-way phase on the prior
   component's parity being green AND its docs being trustworthy first.

## Contract

- ALWAYS make the source the oracle. Correctness means matching the pinned source
  entry point on the same seed, config, inputs, clock, and runtime data.
- NEVER refactor, simplify, or "make idiomatic" while chasing parity — ALWAYS
  preserve the source's control flow, branch order, evaluation order, constants,
  magic numbers, edge cases, and failure paths.
- ALWAYS pin the exact source worktree/commit/path before comparing. NEVER diff
  against a nearby main checkout when the port lives in a worktree; RNGs, config,
  and behavior can differ by commit and create phantom divergences.
- ALWAYS keep decision logic single-threaded when the source is sequential.
  NEVER split step/decision/state updates across goroutines unless the source has
  the same ordering boundary.
- ALWAYS treat "shorter Go file than source" as missing logic until a structural
  comparison proves every omission is inactive or intentionally folded.
- ALWAYS leave each intentional divergence documented inline or filed in the
  port's bug list. Undocumented divergence is a bug.

## Parity Source Of Truth

The oracle is the source checked out IN THE PORT'S OWN WORKTREE, never the main
tree. The main tree is a moving target and often diverges from the port ON
PURPOSE — main optimizes for production, the worktree source is shaped for
provable parity. The worktree source deliberately differs from main on exactly
the axes a differential harness needs to be deterministic:

- **Deterministic IDs vs random IDs.** The worktree encodes reproducible keys
  (e.g. `{step}-{peer}-{item}`) into IDs that main randomizes (`uuid4`/hex).
  Porting main's random IDs into Go would make every ID differ run-to-run and
  DESTROY byte-for-byte trace diffing.
- **Seeded global RNG vs fresh instance.** The worktree binds a module-global
  seeded generator reseeded per step so Go can mirror the exact draw stream; main
  keeps the same generator class but different seeding ergonomics.

RULES:
- ALWAYS diff Go against the SOURCE IN THE WORKTREE. NEVER the main repo, even
  when the relative path looks identical.
- NEVER "sync" a main-tree change into the port without asking whether it breaks
  determinism. A change that is correct for production (random IDs, OS-entropy
  RNG) can be CATASTROPHIC for the parity harness. Determinism-shaping divergences
  in the worktree source are LOAD-BEARING, not stale — treat them like
  Chesterton's fence.
- Confirm the tree with `git rev-parse HEAD` and `git diff -- <file>` in the
  ACTUAL worktree before believing any "divergence."

## Steering patterns (hard-won)

The corrections that actually carry a port. Bake them in from day one.

- **The source is the oracle — NEVER touch it.** Fix Go only. The single allowed
  source edits are non-behavioral parity-trace emits and deterministic-prep
  (phase 0). If you think the bug is in the source, you are wrong about the bug;
  re-trace. (The handful of needed source refactors — the phase-3 split — must
  stay byte-identical, proven by the golden.)
- **Find the FIRST divergence, not where the OUTPUT diverges.** Outputs diverge at
  row 5 because a weight diverged at step 1. ALWAYS diff matched,
  key-aligned traces top-to-bottom and fix the earliest divergent decision. NEVER
  theorize an aggregate gap ("variance artifact", "architecture gap") — trace to
  the exact site.
- **Parity is a CHAIN; fix divergences in execution order, one at a time.** Each
  later divergence surfaces only after the prior is fixed and re-run. NEVER fix
  out of order: an earlier divergence MASKS later ones, and you cannot trace-verify
  a step-N fix while any step-M (M<N) still diverges. Fix the first, re-run, let
  the next surface.
- **A trace mismatch may be a COUNT delta, not a value delta.** A function that
  never emits/calls a sub-path makes a positional trace-diff MISALIGN — it looks
  like a value divergence at record k but is really "Go emitted 6 records, source
  7". Localize by adding RICHER trace fields to BOTH sides (shared keys) to pin the
  exact sub-computation; then you can tell a value bug from a count bug.
- **Verify the INPUT byte-identical before chasing the output.** Feeds/inputs come
  first; prove they match. An "output divergence" is often a feed-timing or
  feed-interleaving divergence one layer down.
- **Read the config/data/code before explaining a number; concede fast when
  challenged.** NEVER defend a plausible mental model — do the arithmetic against
  the real config and code path. Confident-wrong explanations burn trust. When
  challenged, drop the framing and re-derive from source.
- **Always option A: model the source's behavior, even its bugs.** When the source
  relies on a dynamic-language accident (loose typing, NaN propagation,
  bool-as-number, enum-value coercion), embed that observable behavior in Go.
  NEVER "fix" it idiomatic or import Go's cleaner behavior — that breaks parity.
  See the companion file's seams.
- **Compare against the RIGHT tree.** The port lives in a worktree at a different
  commit than main; see "Parity Source Of Truth". A wrong-tree diff invents
  phantom divergences (the classic one is a false RNG-mismatch finding).
- **A shorter Go file is a red flag, not clean code.** Treat every "much shorter
  than source" file as missing logic until a structural pass proves otherwise. A
  `return 0` / `:= 0` stub can silently disable a whole gate.
- **Mirror the source's concurrency model, don't improve it.** Single-threaded
  sequential source → single goroutine / single dequeue loop. NEVER parallelize
  for speed; nondeterministic interleaving destroys parity.
- **Make the Go component fully config-driven — no hardcoded knobs, no hidden
  requirement.** Build state from config like the source's no-external-deps path.
  Hardcoded timeouts/defaults that "work" on the small test are latent divergences
  that fire at scale (production sample periods, sparse replay).
- **Prove it subprocess-vs-subprocess, not just in-process.** The strict harness is
  real-source-subprocess vs real-Go-subprocess through ONE orchestrator with the
  SAME real peers. In-process equivalence is weaker evidence — a "passing" harness
  that isn't subprocess-vs-subprocess is a finding.
- **Once short equivalence holds, ENLARGE the test — don't declare victory.**
  Byte-identical output at a short horizon can hide a whole divergence chain that
  scaling exposes. Longer horizons, higher variance, real data, production configs.
  Tier short/medium/long/max via config, gate by env. Parity on real data beats
  synthetic.
- **Agent/second-opinion success reports are NOT evidence.** Confirm every claimed
  fix against the diff AND a test that fails on the old code. Use a second-opinion
  tool to PLAN the port (adversarial framing, grounded in real source) and to sweep
  for divergences; never to certify done. A subagent green in an isolated worktree
  proves nothing about the integration tip: cherry-pick its fix onto the current
  tip and RE-RUN the harness there.
- **A parity test that compares two hand-copies is HOLLOW — the dual blind spot.** A
  scalar test comparing a hand-copied formula to a re-implemented Go expression
  passes even when the REAL functions diverge. The oracle MUST exercise the REAL
  source function AND the REAL Go function — dispatch Go through the parity binary
  (never inline the arithmetic in `cmd/parity`), and anchor the source oracle to
  the real function's source (a getsource + guard assert that fails if it drifts).
  Length/range/sign-only asserts pass on broken code; pin exact values, perturb-to-
  fail every pin. And know the limit: per-function/scalar tests CANNOT catch
  orchestration or count divergences — only a full differential RUN can.
- **Comparison machinery is ONE committed module, never a tmp-script duplicate.** The
  test gate and the iteration CLI both import the same trace-comparator; a second
  copy in `tmp/` silently drifts and lies. Trace comparison = shared-key +
  exact-float + skip only asymmetric instrumentation. Track the ignore-set HONESTLY:
  a genuinely-diverging field parked in "ignore" is a false green — only ignore
  truly asymmetric instrumentation, and write down why for each entry. Test-runner
  SKIPs are their own false-green: a skipped case is un-verified — drive skips to
  zero, and every surviving skip needs a written reason.
- **Keep a port diary.** Log each phase, the first-divergence chain for every fix
  (symptom → upstream cause → exact site → commit), and intentional residuals. The
  chain is the reusable asset; "fixed it" is not.
- **Parity instrumentation must be TYPE-SAFE — a crashing emit is not pure.** A debug
  field that raises on a real input (e.g. a hex-format of a value that is
  sometimes an int because a sum returned an all-int `0`) crashes the step, fails a
  downstream phase, and REGRESSES the chain — looking like a new divergence. ALWAYS
  coerce before emitting, and treat any instrumentation that changes control flow as
  a bug, not a probe.
- **Co-emit every feed on BOTH sides — an un-instrumented stream HIDES divergences.**
  A "trace-gap" (records one side emits and the other doesn't) is itself a gate
  dimension: as long as Go omits a feed, a value divergence that lives in that feed
  is invisible and masks downstream gaps. Symmetric instrumentation (every trace
  feed present on both sides, `only_source` and `only_go` both empty) is REQUIRED
  before you can claim full parity — closing the trace-gap both completes the gate
  AND localizes the next bug.
- **"Green run" ≠ "aspect covered" — parity proves only the paths that FIRED.** A
  passing differential run certifies parity over the decisions that actually
  executed in that config, nothing more — and only for the entry point it drives; a
  sibling production entry point has un-verified glue. A whole gate/branch can be
  dead in the test input and silently un-verified. ALWAYS enumerate the aspects
  (every gate, every feed, every branch) and confirm each is EXERCISED — pick
  configs/seeds/horizons that fire the dormant ones, or the port has "parity" only
  over the happy path.

## Behavioral-fidelity seams

When the source relies on a dynamic-language accident, ALWAYS option A: model and
embed the source's observable behavior in Go — do NOT "fix" it idiomatic. The
concrete, language-specific seams (numeric model, RNG, rounding, iteration order,
serialization, strings) live in the companion file — **load `py.md` / `ts.md`
before porting.** The generic rule: any place the source's runtime does something
Go's naive equivalent does not is a seam; enumerate them up front from the
companion, don't discover them one divergence at a time.

## Port Loop

1. ALWAYS map one source file to one Go counterpart before editing.
2. ALWAYS capture goldens by EXECUTING the source, not by reading source and guessing.
3. ALWAYS port one module at a time and keep tests passing between modules.
4. ALWAYS run `go build ./...`, `go test -count=1 ./...`, and `go vet ./...`.
5. ALWAYS run a differential harness against the real source entry point. Compare
   aggregate counts first, then per-cycle traces.
6. NEVER explain an aggregate gap by theory alone — ALWAYS trace both sides to the
   first divergent decision and fix that site.
7. NEVER accept a subagent/second-opinion "fixed" report as evidence. Confirm every
   claimed fix against the diff AND a parity case that FAILS on the old code
   (perturb-and-fail teeth check) before marking it done.

## Running The Differential Harness

The harness is a source-language test that shells out to a Go parity binary
(`go build -o <tmp> ./cmd/parity`, then `<bin> <component>` over stdin JSON). It
must run under the SOURCE component's toolchain/venv, not the Go module's.

- ALWAYS invoke from the SOURCE component dir with its runtime and dependency path
  (its real package deps must be importable). The exact command is language-
  specific — see the companion file.
- NEVER invoke the harness from the Go module dir; it resolves the Go module's
  (empty) environment and cannot even spawn the source test runner.
- The conftest/fixture rebuilds the Go binary from `cmd/parity` each session, so a
  stale Go build cannot silently pass. A cheap collect-only run confirms the suite
  count before a full run. Tiers opt in by env.

## Behavior-Preserving Refactor Mirror

When a refactor lands in the source oracle that claims to preserve behavior
(extract a value object, rename a log helper, split a function), you must mirror
it without regressing parity. A green harness is the only proof the refactor was
actually behavior-preserving — on EITHER side.

1. NEVER trust the commit message. A large diff can be byte-identical behavior OR a
   hidden arithmetic change. Audit every arithmetic quantity and every branch order
   line-by-line; "observability/log-only" is a conclusion you EARN by reading, not a
   label you accept.
2. Mirror as ONE atomic change set: the worktree source AND the Go port (and the
   parity fixtures if a value object's shape changed). A one-sided mirror desyncs
   the oracle from the port — that desync is the hazard, not the number of commits.
3. Keep compute ORDER identical. A frozen-per-step value object (compute the verdicts
   once at step start, read them everywhere after) must freeze at the SAME point on
   both sides; moving the freeze changes RNG/draw timing even if every formula is
   unchanged.
4. Go-idiomatic mirrors of an `Optional` ARE allowed and preferred: a
   `func() (T, bool)` nilable return mirrors `Optional[T]`; a discriminator struct
   mirrors dynamic type dispatch. These are syntax-level deviations, not behavioral.
5. PROVE it: the full parity harness must stay green with the SAME case count before
   and after. A changed count without a deliberate new pin means the refactor moved
   behavior.
6. Commit message states which source files and which Go files it mirrors, and that
   the parity harness is unchanged/green, so the next syncer sees the contract.

## Source-Tree Checks

- ALWAYS state the pinned source path in task prompts and project docs so subagents
  cannot drift. (Tree-selection rules live in "Parity Source Of Truth".)
- ALWAYS maintain a source-to-Go file map for sync work. When the source changes,
  inspect `git log --oneline <file>`, sync only the changed behavior, and recapture
  any broken golden by running the source.

## Numeric Checks

- ALWAYS gate on BIT-EXACT float equality. `assertAlmostEqual`/epsilon tolerance is
  the WRONG gate for a faithful port — it hides the exact 1-ULP divergences the port
  exists to catch, and those amplify over a long run. Reserve tolerance ONLY for
  genuinely non-reproducible external inputs, and prefer ELIMINATING that
  nondeterminism (phase 0) over tolerating it.
- ALWAYS audit computed probability/threshold gates for NaN. In Go, comparisons with
  NaN are false; a gate like `rng > NaN` can silently stop rejecting.
- Language-specific rounding, division, summation, and libm parity rules live in the
  companion file — load it. (Ties-to-even vs half-up vs half-away-from-zero, naive
  `+=` vs compensated sum, pure-Go vs cgo libm, IEEE-754 op-order grouping.)
- NEVER hardcode a pre-multiplied/rounded constant where the source computes it at
  runtime from source values — a runtime multiply and a baked product can differ by
  1-ULP that a long run amplifies. Mirror the exact multiply order in a runtime
  var-block from the same source values.
- For the crash-vs-guard boundary on degenerate input, see below.

## Crash-vs-Guard Boundary (degenerate input)

Two different cases hide behind "the source raises on bad input" — the recurring
anti-pattern is a Go `== 0` / `<= 0` guard that treats a CONFIGURED zero as "unset":

- **The source returns/propagates a VALUE (NaN, a configured 0.0).** This IS
  mirror-able. ALWAYS option A: drop the Go guard and propagate the value
  (substitute `math.NaN()`, return the configured `0.0` verbatim). A configured
  zero is a real value, not "unset".
- **The source CRASHES (divide-by-zero) on input that cannot legitimately occur.** A
  crash has no value to mirror, so exact parity is undefined there. Two defensible
  resolutions — pick one deliberately and DOCUMENT it inline + in the port's bug
  list: KEEP a defensive Go guard as the safe behavior on impossible input, or DROP
  the guard and leave the impossible input undefined while mirroring the reachable
  range exactly. NEVER "fix" the source to crash-match, and NEVER let a crash-input
  guard leak onto reachable inputs.

Audit every `== 0` / `<= 0` guard: most are the first case, and a configured-zero
guard with no source counterpart is a divergence — fix it. Only crash-input guards
may stay, and only documented.

## Order Checks

- ALWAYS preserve source iteration order where it affects output, RNG draw order,
  "first match wins", or downstream stable sorting. NEVER range a Go map directly on
  an output-affecting path. (The source's exact ordering rule — insertion order,
  integer-key-first, etc. — is language-specific; see the companion file.)
- ALWAYS use `sort.SliceStable` / `slices.SortStableFunc` when porting a stable
  source sort where equal keys can occur.
- ALWAYS sort or preserve an explicit key slice before iterating "all X" for
  accumulation, output emission, traces, or snapshots.

## Runtime Config And Feeds

- ALWAYS dump effective runtime config from the RUNNING source process. NEVER trust
  constructor literals or module defaults when loaders mutate state.
- ALWAYS account for loaders that apply bundled defaults even when the caller passes
  "no config". A loader that applies bundled weights with `dir=None` will make Go
  literals wrong.
- ALWAYS pass the same subconfig the source uses. If the source constructs a
  calculator from a loaded state's mapping, do not use the module's default
  constants.
- ALWAYS verify live feed ordering with timestamps and sample counts. A one-step
  sample-timing difference (the source delivers step-N's input to a monitor AFTER
  step N, so step N sees N-1 samples) changes a rolling window's size. Preserve each
  feed's actual timing separately.
- NEVER assume a "not ported" setup/runtime layer is inactive. ALWAYS prove it is
  not fed in the target run; if it drives decisions every step, port it or load its
  runtime data.

## Missing-Logic Checks

- ALWAYS grep the Go port for `TODO`, `stub`, `not yet`, `return 0`, and `:= 0` near
  behavior comments. A zero stub can disable a whole gate. A hand-SIMPLIFIED stub is
  worse than a zero one: it returns plausible numbers, so only a differential RUN
  (not scalar tests) exposes it.
- ALWAYS check exported functions and new types are wired at the call site. Presence
  of `CalculateX` is not evidence the path uses it.
- NEVER replace a source horizon/wait calculation with a binary flag. ALWAYS port the
  full calculation and all its reasons.
- ALWAYS model pending/timeout stateful modules before flattening them. Missing
  trackers, pending queues, or pending-decision trackers usually mean missing gates.

## Architecture Timing

- ALWAYS model the source's visible latency boundaries: async queues, round trips,
  locks, output timing, and state-insertion timing.
- NEVER make an in-process Go runner synchronous if the source observes results one
  or more steps later. Add a delay queue or document a proven architecture gap.
- NEVER claim "architecture gap" or "intentional omission" for a residual without a
  trace proving the first divergent decision and its cause.

## What To Leave In The Source

- ALWAYS leave offline optimizers and huge numeric searches in the source when the Go
  port only consumes their output data.
- ALWAYS stub sidecars only at their interface boundary: scraping, dashboards,
  external sync, derived computations, and reporting can stay out of the hot port if
  their outputs are provided.
- NEVER skip high-frequency per-step logic as a sidecar. If it participates in the
  decision path being matched, port it fully.
- ALWAYS port low-frequency config loaders when their loaded data changes runtime
  decisions; the generator can stay in the source, but the effective data cannot
  vanish.

## Divergence Root-Cause Catalogue

Concrete divergence CLASSES a faithful port will recognize. Use as a checklist when
chasing mysterious 1-ULP / count / state gaps. Language-specific instances (which
rounding mode, which RNG, which sum) are in the companion file.

- **Hardcoded rounded constant vs runtime float multiply (1-ULP)** — a baked product
  differs from the source's runtime multiply. Mirror the exact multiply order in a
  runtime var-block.
- **Naive `+=` vs compensated summation (1-ULP)** — if the source language's `sum`
  is compensated/pairwise, provide a matching Go summation and apply it ONLY at those
  sites; over-applying it is its own divergence.
- **Pure-Go libm vs the source runtime's libm (1-ULP)** — transcendentals
  (`pow/exp/log/sin/...`) differ by ~1-ULP on a fraction of inputs. A matching-libm
  twin (cgo or a ported fdlibm) may be required; budget the toolchain cost and keep a
  pure-Go fallback.
- **IEEE-754 op-order/grouping** — `a-(b+c) != (a-b)-c`. Match the source's evaluation
  order exactly.
- **Map/collection iteration nondeterminism** — Go random map range vs the source's
  ordered iteration. Thread insertion-ordered (or language-rule-ordered) key slices
  through context.
- **Hand-simplified STUB returning plausible numbers** — a flat cap where the source
  runs the full computed path with its gates and filters. Only a differential RUN catches it.
- **Missing periodic reset** — a daily/window counter not reset at the boundary. Audit
  state-holding fields for reset sites; multi-boundary accumulators can be identical
  for many cycles and still drift at long horizons — a divergence tier of their own.
- **Transport read-limit dropping large frames** — a websocket/stream default read
  limit silently drops oversized messages once state grows, freezing a peer. Raise the
  limit.
- **Lock/dispatch dedup gate (dup-id collision)** — an ID generator's time component
  wraps and reuses a live id; the source gates dispatch on a lock, the port didn't →
  dup-id crash → barrier deadlock. Gate on the same lock (the collector still records,
  so output stays byte-identical).
- **State not cleared on an error path (ID-serial divergence)** — the source's error
  handler clears more state (e.g. an inflight map) than the port did; the id generator
  then picks a different serial, non-causal for a long time, surfacing much later.
  Mirror EVERY state mutation an error/disconnect path performs, not just the obvious
  lock.
- **Output byte-identity is a WEAK gate** — output can match while decision traces
  already diverged, and this holds at ANY scale. Gate on decision traces + ALL streams
  (inputs/traces/outputs/final-state), never just the outputs.

**Integration methodology:** isolated-worktree subs commit per-link fixes; the main
tree cherry-picks / fast-forwards + re-verifies the gate before integrating; subs die
to limit/API errors but committed work is always salvaged via git ff/cherry-pick.
