# Python → Go: behavioral-fidelity seams

> One-line: Python's dynamic accidents — bool-is-int, insertion-ordered dicts, banker's rounding, compensated `sum()`, libm floats, PCG64/MT19937 RNGs, NaN-tolerant JSON — are all OBSERVABLE behavior; a faithful Go port must model each one explicitly and NEVER "fix" it idiomatic.

The oracle is the pinned Python; correctness means matching it bit-for-bit on
the same seed, config, inputs, and clock. When Python relies on a
dynamic-language accident, ALWAYS model and embed that observable behavior in
Go — never import Go's cleaner behavior. Every divergence below was found the
hard way in a real parity port.

## Type & numeric model

- **`int` is arbitrary-precision.** Go `int64` overflow wraps silently. Where a
  Python value can plausibly exceed 2^63 (serial counters, hash-derived ints,
  accumulating products), prove the bound or use `math/big`. Division/modulo
  semantics also differ — see Rounding.
- **`float` is IEEE-754 float64 == Go `float64`.** Same bit patterns, so
  bit-exact parity is achievable — but only if operation ORDER, grouping, and
  library functions match (see Rounding & numeric ops).
- **bool IS int.** `isinstance(True, int)` is `True`; `float(True) == 1.0`;
  `True + True == 2`; bools flow through arithmetic, indexing, and `sum()`
  unremarked. Any Go numeric type switch over dynamic values needs an explicit
  `case bool:`:

  ```go
  func toFloat(v any) (float64, bool) {
      switch x := v.(type) {
      case bool:
          if x {
              return 1.0, true
          }
          return 0.0, true
      case int:
          return float64(x), true
      case float64:
          return x, true
      }
      return 0, false
  }
  ```

- **`isinstance` dispatch → explicit discriminator field.** Collapse a Python
  type-branch into ONE Go struct with a discriminator (e.g. a raw-map field
  whose presence selects the branch). Mirror BOTH branches' fallback values. A
  configured `0.0` is a real value, not "unset" — a Go `== 0` guard with no
  Python counterpart is a divergence, not defensive programming.
- **`enum.value` is the underlying integer.** `str(member.value)` yields
  `"1"` / `"32"`, never the member name. Mirror with `strconv.Itoa(int(v))` —
  NEVER a Go `String()` method that prints the constant name. Note `str()` /
  `format()` of int-enums changed across Python versions; test the pinned
  interpreter empirically, don't assume.
- **`None` is distinct from zero, empty, and missing.** Mirror `Optional[T]`
  with `(T, bool)` returns or `*T` — this is a forced-by-syntax deviation and
  is allowed. NEVER conflate Go zero-values with `None`, and never map a
  Python raise-on-missing (`d[k]` → `KeyError`) to a silent Go zero-value —
  that converts a crash path into a wrong value.

## RNG (reproducibility)

- **Identify the generator at EVERY call site.**
  `numpy.random.Generator(PCG64)` ≠ CPython `random.Random` (MT19937) ≠ Go
  `math/rand`. None interoperate. Each generator the oracle uses needs a
  bit-for-bit Go twin.
- **numpy shuffle: NEVER `u64 % n`.** numpy draws bounded ints via
  `random_interval`: masked **uint32** rejection sampling fed from a buffered
  `next_uint32` (each u64 draw yields two buffered u32 halves). Modulo bias
  aside, the DRAW PATTERN differs — modulo desyncs the stream immediately.
  Golden vector to pin as a Go test: **PCG64 seed 7,
  `shuffle(list(range(10))) == [8, 0, 7, 1, 3, 6, 2, 4, 5, 9]`.**
- **CPython stdlib `random`** is MT19937; `random()` builds a 53-bit double
  from two 32-bit outputs (`(a>>5)*2^26 + (b>>6)) / 2^53`). Porting it
  bit-for-bit is doable but tedious — prefer **phase-0**: before writing any
  Go, replace stdlib `random`, `uuid4()`, and every `set()`-based selection in
  the PYTHON oracle with a single project-owned seeded generator and
  `sorted()` on explicit business keys. NEVER start a port against a
  nondeterministic oracle.
- **Preserve draw ORDER, draw COUNT, and stream SEPARATION.** If Python keeps
  separate per-subsystem generator instances, Go mirrors separate
  instances with the same seed lifetimes. Sharing one stream where Python has
  several (or vice versa) desyncs everything downstream of the first extra
  draw. When hunting a desync, log per-cycle draw counts on both sides; the
  first cycle where counts differ is the bug site.
- **Match reseed keys EXACTLY, including increment order.** If Python bumps a
  cycle counter BEFORE seeding `seed + counter`, Go must not seed from
  `seed + 0` or run an extra step-0 cycle. A module-global generator reseeded
  per cycle is a LIFETIME contract — mirror the lifetime, not just the
  algorithm. The oracle's seeding ergonomics (module-global vs fresh-instance)
  are part of the oracle; never "improve" them.

## Rounding & numeric ops

- **Python 3 `round()` is ties-to-even (banker's).** Go `math.Round` is
  ties-AWAY-from-zero — NEVER use it for a Python `round()` site. For
  `round(x)` use `math.RoundToEven` (and note Python returns an *int* here).
  For `round(x, n)` Python rounds via correctly-rounded decimal conversion —
  naive `RoundToEven(x*10^n)/10^n` diverges on some inputs. Go's `strconv`
  formatting is also correctly rounded ties-to-even, so this mirrors it:

  ```go
  // RoundN mirrors Python 3 round(x, n): correctly-rounded
  // decimal rounding, ties-to-even.
  func RoundN(x float64, n int) float64 {
      s := strconv.FormatFloat(x, 'f', n, 64)
      r, _ := strconv.ParseFloat(s, 64)
      return r
  }
  ```

- **Integer division and modulo.** Python `//` FLOORS (toward −inf) for ints
  and floats; `%` takes the sign of the divisor. Go `/` truncates toward zero;
  `%` takes the sign of the dividend. They agree only when both operands are
  non-negative — provide `FloorDiv`/`FloorMod` helpers and use them at every
  `//`/`%` site that can see a negative operand.
- **Divide-by-zero.** Python raises `ZeroDivisionError` for int and float
  `/`, `//`, `%`. Go panics on int division by zero and silently yields
  ±Inf/NaN on float division. Resolve per the crash-vs-guard rule: if the zero
  is a CONFIGURED real value whose result Python propagates, propagate it; if
  Python would crash on input that cannot legitimately occur, pick
  guard-or-undefined deliberately and DOCUMENT it. Audit every Go `== 0` /
  `<= 0` guard — most treat a configured zero as "unset" and are divergences.
- **CPython `sum()` (3.12+) is Neumaier compensated summation for floats.**
  Naive Go `+=` diverges by 1 ULP on accumulated values (e.g. an accumulated
  value summed over many items) and a long run amplifies it. Provide
  a twin and apply it ONLY at Python `sum()` call sites — an explicit Python
  `+=` loop IS naive, so Go stays naive `+=` there; over-applying the
  compensated sum is its own divergence:

  ```go
  // Sum mirrors CPython 3.12+ sum() over floats (Neumaier).
  func Sum(xs []float64) float64 {
      var s, c float64
      for _, x := range xs {
          t := s + x
          if math.Abs(s) >= math.Abs(x) {
              c += (s - t) + x
          } else {
              c += (x - t) + s
          }
          s = t
      }
      return s + c
  }
  ```

- **CPython `math.pow/exp/log` call the platform libm; pure-Go `math`
  differs by ~1 ULP on a meaningful fraction of inputs** (measured in one port:
  roughly a fifth of `pow` inputs, ~15% of `exp`, ~7% of `log`). If the gate is
  bit-exact, build a cgo shim to libm with a pure-Go `!cgo` fallback
  (`CGO_ENABLED`-driven), and budget the C-toolchain dependency in CI — the
  parity gate requires the cgo build; the fallback exists only for
  environments without a compiler.
- **IEEE-754 grouping and evaluation order matter.** `a - (b + c)` is not
  `(a - b) - c`. A "harmless" algebraic regroup, hoist, or common-subexpression
  fold is a 1-ULP divergence. Mirror Python's exact expression grouping,
  operand order, and evaluation order.
- **NEVER bake a pre-multiplied rounded constant where Python computes it at
  runtime.** `0.1 * 3` is `0.30000000000000004` at runtime, not the literal
  `0.3` you'd transcribe. Mirror the runtime multiply from the same source
  values in the same order — a Go `var` block computing the constant at init
  from the same factors, never the baked product.
- **The parity gate is BIT-EXACT float equality.** NEVER
  `assertAlmostEqual`/epsilon — tolerance hides exactly the 1-ULP seams this
  file lists. Compare bits: `float(x).hex()` on the Python side,
  `strconv.FormatFloat(x, 'x', -1, 64)` (or `math.Float64bits`) on the Go
  side. Reserve tolerance only for genuinely non-reproducible external inputs,
  and prefer eliminating that nondeterminism in phase 0.
- **Audit computed thresholds for NaN.** In both languages every comparison
  with NaN is false — Python code often *relies* on this (a `draw > threshold`
  gate that silently never fires when the threshold is NaN). Mirror the NaN
  propagation; NEVER add a defensive skip or early return that Python lacks.

## Iteration & ordering

- **`dict` preserves insertion order (language guarantee, 3.7+), and it is
  load-bearing.** It determines serialization order, RNG draw order (iterating
  entities to decide who consumes the next draw), first-match-wins scans, and
  the input order to stable sorts. Go map iteration is deliberately
  RANDOMIZED — NEVER `for k := range m` on any output-affecting path. Thread
  an insertion-ordered key slice alongside every such map
  (`keys []K` + `m map[K]V`), and pass the key slice through context objects
  so every downstream consumer iterates identically.
- **`sorted()` / `list.sort()` are STABLE (Timsort).** Go `sort.Slice` is not
  → use `sort.SliceStable` wherever equal keys can occur. Mirror Python's
  key-tuple comparison exactly (lexicographic over the tuple elements, not
  concatenated strings).
- **`set()` iteration is nondeterministic across runs** (string hash
  randomization). There is nothing deterministic to mirror — phase-0 replace
  set-based selection in the PYTHON oracle with `sorted()` over explicit keys
  before porting.
- **`min`/`max` return the FIRST extremal element** — tie behavior depends on
  iteration order, which must therefore be the insertion order.

## Equality, truthiness, None

- **Falsy set:** `0`, `0.0`, `-0.0`, `""`, `[]`, `{}`, `set()`, `None`,
  `False`. `if not x:` on a float treats a CONFIGURED `0.0` as falsy — mirror
  that exact predicate. NaN is TRUTHY (`bool(float('nan')) is True`) — a Go
  "is it zero?" check is not a truthiness mirror for floats.
- **Signed zero survives.** `-0.0 == 0.0` and `-0.0` is falsy, but repr/JSON
  print `-0.0` — preserve the sign bit through Go arithmetic
  (`math.Copysign`) and formatting.
- **Containers use identity-then-equality.** `nan in [nan]` is `True` (the
  `in` operator short-circuits on identity before `==`); a Go slice-contains
  via `==` returns false for NaN. Mirror at any membership test over floats.
- **`is` vs `==`.** `is None` is identity and maps to a nil/ok check. Any
  other `is` on values may work only via CPython interning accidents (small
  ints, short strings) — locate each `is` site and decide whether the code
  meant identity (a sentinel object) or accidentally relied on interning.
- **None vs missing key.** `d.get(k)` → `None`; `d[k]` → `KeyError`. Go's
  `v, ok := m[k]` covers both, but choose per site: the raising form is a
  crash path (see crash-vs-guard), not a default-value path.

## Serialization (JSON)

- **Python `json` emits and accepts `NaN`/`Infinity`/`-Infinity` by default**
  (`allow_nan=True` — technically invalid JSON). Go `encoding/json` REFUSES to
  encode non-finite floats (error). For a parity harness, serialize
  NaN/±Inf as string sentinels on BOTH sides:

  ```go
  func jsonFloat(x float64) any {
      switch {
      case math.IsNaN(x):
          return "NaN"
      case math.IsInf(x, 1):
          return "Infinity"
      case math.IsInf(x, -1):
          return "-Infinity"
      }
      return x
  }
  ```

  Mirror in Python with a pre-walk (or `default=`). NEVER skip a NaN parity
  case because "the transport can't carry it" — that skip masks a real seam;
  fix the transport with sentinels and drive parity-case skips to zero.
- **Float text formatting differs.** Both sides use shortest-round-trip
  digits, but placement rules differ: Python repr switches to exponent form
  only at `>= 1e16` or `< 1e-4` and appends `.0` to integral floats
  (`1e+15` formats as `1000000000000000.0`, `1.0` as `1.0`); Go `%g`/
  `FormatFloat(-1)` switches to exponent form much earlier and prints `1`,
  `-0`. Gate on float BITS (hex) wherever possible; where a text output file
  is itself the byte-diffed artifact, implement Python's repr placement rules
  in Go — do not hope `%g` matches.
- **Key order.** `json.dumps` preserves dict insertion order; Go
  `encoding/json` SORTS map keys alphabetically. For parity output use structs
  (field order = declaration order) or an ordered-map encoder that mirrors
  insertion order.
- **Separators.** Python default is `", "` / `": "` (spaces); compact needs
  `separators=(',', ':')`. Go emits compact. Match explicitly on one side.
- **Large ints.** Python serializes arbitrary-precision ints exactly; Go
  unmarshalling into `float64`/`int64` silently loses precision — use
  `json.Number` when big ints can appear.

## Strings & text

- **`str` is a sequence of Unicode code points; Go `string` is UTF-8 bytes.**
  Python `len`/index/slice count code points; Go `len` is bytes, `s[i]` is a
  byte, `range` yields runes at byte offsets. Convert to `[]rune` at every
  site where Python indexes, slices, or measures a string that can carry
  non-ASCII.
- **`bytes` vs `str` is a hard type split in Python** (mixing raises). Go has
  no such wall — keep the distinction by convention, and mirror every
  encode/decode site. Decoding errors are a crash-vs-value seam: Python raises
  `UnicodeDecodeError`; Go silently substitutes U+FFFD.
- **Byte-wise comparison of valid UTF-8 equals code-point order**, so Go string
  sorting matches Python string sorting for valid text — safe, but only for
  valid UTF-8.
- **Formatting is not interchangeable.** `f"{x:.2f}"`, `{:g}`, `%`-format have
  exact CPython semantics (padding, sign handling, exponent digit count) that
  `fmt.Sprintf` does not replicate verb-for-verb. Pin a format golden for
  every formatted string that lands in gated output; port the format
  mini-language semantics per site, not by verb analogy.
- **Whitespace semantics differ in edge cases.** Python `str.split()` with no
  args (split on runs, strip ends) is `strings.Fields`-LIKE but the whitespace
  sets differ at exotic code points; `str.strip()` default set likewise.
  Mirror semantics and pin goldens; don't map method names.

## Differential harness invocation

- Shape: Python pytest shells out to ONE Go parity binary built from
  `cmd/parity` (self-registering per-module dispatch; JSON on stdin → JSON on
  stdout). The tests must exercise the REAL Python function and the REAL Go
  function — NEVER inline a re-implemented formula in the test or in
  `cmd/parity`; a hand-copy-vs-hand-copy comparison stays green while both
  real paths diverge. Anchor the Python side with `inspect.getsource(fn)` plus
  a guard assert so the test fails if the oracle function drifts.
- ALWAYS invoke from the PYTHON component's directory under its venv with the
  project PYTHONPATH:
  `cd <worktree>/<py-component> && PYTHONPATH=<shared-lib>:src uv run python -m pytest <path-to-parity-tests>`.
- NEVER invoke from the Go module directory. The classic foot-gun is
  `Failed to spawn: pytest, No such file or directory` — the Go dir has no
  Python venv, and the fixtures need numpy plus the real project packages on
  PYTHONPATH.
- The conftest fixture REBUILDS the Go binary from `cmd/parity` each session
  (`go build -o <tmp> ./cmd/parity`), so a stale Go build can never silently
  pass. `--collect-only -q` cheaply confirms the case count before a full run.
- Heavier tiers (longer horizons) are opt-in via an env var; the fast tier
  runs in CI unconditionally.

## Seam catalogue

Each entry: symptom → root cause → Go fix.

1. **1-ULP drift in a derived constant** → a hand-transcribed rounded literal
   where Python multiplies source values at runtime → compute the constant in
   a Go `var` block from the same factors in the same multiply order.
2. **1-ULP drift on accumulated totals** → CPython `sum()` is Neumaier
   compensated, Go `+=` is naive → use the compensated `Sum` twin at `sum()`
   sites ONLY; keep naive `+=` where Python loops with `+=`.
3. **1-ULP on `pow`/`exp`/`log` outputs** → pure-Go `math` vs CPython's
   platform libm → cgo-libm twin with a pure-Go `!cgo` fallback; the parity
   gate requires the cgo build (CI pays the C-toolchain cost).
4. **1-ULP on a composite expression** → IEEE-754 regrouping
   (`a-(b+c)` vs `(a-b)-c`) introduced while "cleaning up" → restore Python's
   exact grouping and evaluation order.
5. **Emitted record/candidate order flaps run-to-run** → Go map-range
   nondeterminism where Python iterates dict insertion order → thread
   insertion-ordered key slices (e.g. a per-cycle context carrying the ordered
   keys of a per-key aggregate map) through every consumer.
6. **One subsystem returns plausible numbers; all scalar tests green; full run
   diverges** → a hand-simplified stub (e.g. a flat cap) replacing the real
   computed path with its gates → grep for `return 0`, `:= 0`, "approximation",
   `TODO`, `stub` near behavior comments; only a full differential RUN catches
   this class — scalar tests cannot.
7. **Values correct within a day, wrong after midnight** → missing periodic
   (daily) counter/balance reset → audit every state-holding field for its
   reset site; size test horizons by how many reset boundaries they CROSS, not
   by raw length.
8. **A connected peer silently freezes in long runs** → the WebSocket
   library's default read limit (e.g. tens of KiB) silently drops larger frames →
   raise or disable the read limit; audit every transport-layer default the
   Python stack didn't have.
9. **Duplicate-ID crash or barrier deadlock hundreds of cycles in** → an ID's
   time component wraps and reuses a live ID; Python gates dispatch on a
   dispatch lock (`if not locked:`), the Go port dispatched unconditionally →
   mirror the lock gate exactly (the collector still records, so the output
   file stays byte-identical — only the dispatch is gated).
10. **IDs diverge by one serial long after an error; output differs much
    later** → Python's error handler clears inflight-request bookkeeping; Go
    reset only the lock and kept stale inflight IDs, so the used-ID set — and
    the next serial chosen after an ID wrap — differs. Non-causal for ages,
    then surfaces in output. Mirror EVERY state mutation an error/disconnect
    path performs, not just the obvious one.
11. **Parity green for days, diverges only at week/month horizons** → a
    multi-day accumulator (running totals) crossing many
    boundaries, or a capped-vs-uncapped total → long-running accumulators are
    their own divergence tier; run the long tiers before claiming parity.
12. **Output files byte-identical, yet wrong** → weak gate: output equality
    was coincidental; decision traces had already diverged far upstream →
    gate on decision traces across ALL feeds, verified bottom-up
    (inputs → traces → outputs), and always fix the FIRST divergence in
    execution order — earlier divergences mask later ones.
13. **Trace diff misaligns at record k, looks like a value bug** → a COUNT
    delta: one side skipped a sub-path emit, so positional alignment broke →
    add richer shared-key fields to BOTH sides to distinguish value bugs from
    count bugs.
14. **Harness crashes after adding instrumentation** → a debug emit that isn't
    type-safe (`float.hex(x)` where `x` is an int because `sum()` of an
    all-int/empty sequence returns int `0`) → coerce before emitting
    (`float(x).hex()`); instrumentation that changes control flow is a bug,
    not a probe.
15. **A divergence stays invisible until far downstream** → a feed
    instrumented on one side only; the un-instrumented stream hides the
    upstream divergence while outputs still coincide → require symmetric
    co-emission: every trace feed present on BOTH sides, the
    only-Python/only-Go feed sets both empty, before claiming full parity.
16. **A configured zero behaves as "unset" in Go** → a defensive Go
    `== 0` / `<= 0` guard with no Python counterpart → drop the guard and
    propagate the value (or NaN) exactly as Python does; keep guards only for
    true crash-only inputs, each documented inline and in the port's bug list.
17. **Go config literals wrong despite matching the constructor** → the Python
    loader applies bundled defaults even when the caller passes "no config" →
    dump the EFFECTIVE runtime config from the running Python process; never
    trust constructor literals or module defaults.
18. **Off-by-one sample counts per cycle** → Python's transport delivered the
    cycle-N data to a monitor AFTER cycle N (so cycle N sees N−1 samples); the
    Go port fed it same-cycle → preserve each feed's actual delivery timing
    separately; verify feed ordering with timestamps and sample counts before
    chasing downstream values.
19. **A Go file much shorter than its Python source** → missing logic, not
    clean code → structural comparison until every omission is proven inactive
    or intentionally folded; a zero stub can silently disable a whole gate.
