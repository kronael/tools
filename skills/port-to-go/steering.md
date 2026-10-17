# Steering patterns and seams

Read from `SKILL.md` before the first module is ported.

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
  commit than main; see `SKILL.md` § Parity Source Of Truth. A wrong-tree diff invents
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
