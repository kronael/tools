---
name: port-to-go
description: "Faithful into-Go transcode: port any source language to Go preserving behavior exactly, proven by differential traces. NOT for idiomatic Go rewrites (use go)."
when_to_use: "port to Go, transcode to Go, faithful port, byte-for-byte parity, differential testing, golden trace, Python to Go, TypeScript to Go, RNG desync, map iteration nondeterminism, 1-ULP divergence, N-way component parity"
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
- **`java.md`** — Java → Go seams (silent fixed-width `int` wrap, UTF-16
  strings, boxed-vs-primitive equality, spec'd library algorithms to clone
  bit-for-bit — `java.util.Random`'s LCG, TimSort, `String.hashCode`,
  `Double.toString` — and the unspecified corners `HashMap` order, identity
  `hashCode` and `Math.*` intrinsics that phase 0 must pin).

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

## Steering patterns and seams

ALWAYS read `steering.md` in this directory before the first module: the
corrections that carry a port — the oracle is untouchable, the first
divergence first and in chain order, count-vs-value deltas, config-driven
components, subprocess proof, hollow parity tests, symmetric traces — and
the behavioral-fidelity seams rule.

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

## Checks per phase

ALWAYS read `checks.md` in this directory at phase 2 and keep it open
through phase 6: the refactor mirror, source-tree, numeric and
crash-vs-guard, order, runtime-config, missing-logic, timing and
what-stays-in-the-source checks, and the divergence root-cause catalogue.

**Integration methodology:** isolated-worktree subs commit per-link fixes; the main
tree cherry-picks / fast-forwards + re-verifies the gate before integrating; subs die
to limit/API errors but committed work is always salvaged via git ff/cherry-pick.
