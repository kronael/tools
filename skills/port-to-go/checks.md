# Checks per phase

Read from `SKILL.md` at phase 2 and keep it open through phase 6.

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
  cannot drift. (Tree-selection rules live in `SKILL.md` § Parity Source Of Truth.)
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
