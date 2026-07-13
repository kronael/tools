# TypeScript / JavaScript → Go: behavioral-fidelity seams

> One-line: everything is a float64, every object is an ordered reference type
> with coercion at every boundary, and half the numeric surface (bit ops,
> rounding, number→string) is spec-pinned to rules Go's stdlib does NOT follow —
> a faithful port must model ECMAScript's observable semantics, never Go's
> cleaner defaults.

The TS/JS program is the ORACLE. Go must reproduce its observable behavior
bit-for-bit under the same bit-exact gate as the Python→Go port: goldens are
captured by EXECUTING the oracle under a pinned Node, decision traces are
co-emitted on both sides, floats compare by bits (never epsilon), and every
divergence is fixed at the FIRST diverging decision in execution order.
TypeScript's static types are ERASED at runtime — they are documentation, not
semantics. NEVER derive porting decisions from a TS annotation; a field typed
`number` can hold `undefined`, a string, or `null` at runtime (JSON.parse,
`any` leaks, `as` casts). Log `typeof` at decision sites during golden capture
and port what the values actually ARE.

---

## Type & numeric model

### number is IEEE-754 binary64 — there is no int

- Every arithmetic value of type `number` is a float64. `1`, `1.0`, and
  `0x01` are the same value. There is NO integer type, NO integer overflow, NO
  integer division.
- ALWAYS port `number` as Go `float64` by default. Using `int`/`int64` is an
  OPT-IN that requires proof, per variable, that (a) every value is an integer,
  (b) every intermediate stays within ±2^53 (`Number.MAX_SAFE_INTEGER` =
  9007199254740991), and (c) every operation applied is exact on integers
  (+, -, *, comparisons — NOT `/`). Under those conditions int64 and float64
  are bit-equivalent and int64 is safe.
- Failure mode if you skip the proof: JS silently LOSES precision above 2^53
  (`9007199254740993` becomes `9007199254740992`; `2**53 + 1 === 2**53` is
  true), while Go int64 keeps exact values → divergence that only fires on
  large IDs, timestamps-in-ns, or products of two counters. The product seam is
  the sneaky one: two safe ints can multiply to an unsafe product; JS drops low
  bits, int64 doesn't.
- Overflow: JS floats saturate to ±Infinity past ~1.8e308; Go float64 does the
  same (match), Go int64 WRAPS (divergence). Another reason float64 is the
  default.
- `-0` exists, is producible (`-1 * 0`, `Math.round(-0.4)`), compares equal to
  `+0` under `==`/`===`/`<`, and is observable via `Object.is`, `1/x`, and NOT
  via `String(-0)` (which is `"0"`). Go float64 has the same ±0 semantics in
  arithmetic — parity is natural — but Go FORMATS `-0` as `"-0"`
  (strconv) while JS prints `"0"`. See Serialization.

### Bitwise operators are int32/uint32 machines — a huge seam

- `|`, `&`, `^`, `~`, `<<`, `>>` convert BOTH operands through **ToInt32**:
  NaN/±Inf/±0 → 0; else truncate toward zero, reduce mod 2^32, reinterpret as
  signed two's-complement 32-bit. `>>>` uses **ToUint32**. The RESULT is
  converted back to a `number` (float64): `(x >>> 0)` yields a float in
  [0, 2^32).
- Shift counts are masked `& 31`: `1 << 32 === 1`, `1 << 33 === 2`.
- Concrete traps: `2**31 | 0 === -2147483648` (negative!); `-1 >>> 0 ===
  4294967295`; `~x === -(x|0) - 1`; `(a/b)|0` is trunc-div WITH int32 wrap
  (diverges from `Math.trunc(a/b)` once the quotient exceeds 2^31);
  `(2**53+1) | 0 === 0`… actually reduce-mod-2^32 of the exact double value —
  compute it, don't guess.
- `x | 0` and `~~x` are the idiomatic "to int" — they are NOT trunc; they are
  trunc + wrap. ALWAYS port through the helper, never `int32(x)` (Go's
  float→int conversion on out-of-range values is implementation-specific, and
  on in-range values it truncates without the mod-2^32 wrap).

```go
// ToInt32 / ToUint32 — exact ECMAScript abstract operations.
func ToInt32(x float64) int32 {
	if math.IsNaN(x) || math.IsInf(x, 0) {
		return 0
	}
	t := math.Trunc(x)
	m := math.Mod(t, 4294967296.0) // fmod is exact; sign of dividend
	if m < 0 {
		m += 4294967296.0
	}
	return int32(uint32(m)) // m ∈ [0, 2^32) and integral → conversion exact
}
func ToUint32(x float64) uint32 { return uint32(ToInt32(x)) }

// JS `a << b`  → float64(ToInt32(a) << (ToUint32(b) & 31))
// JS `a >> b`  → float64(ToInt32(a) >> (ToUint32(b) & 31))   (arithmetic)
// JS `a >>> b` → float64(ToUint32(a) >> (ToUint32(b) & 31))
// JS `a | b`   → float64(ToInt32(a) | ToInt32(b))            (& ^ ~ likewise)
// Go signed ints wrap on overflow by spec, so int32 arithmetic here is safe.
```

- `Math.imul(a, b)` is exact int32 wrap-multiply: Go `ToInt32(a) * ToInt32(b)`
  (Go signed overflow wraps — defined behavior). Seeded-PRNG code uses `imul`
  heavily; get this right first.
- Array indices and `length` are uint32 (`length` max 2^32-1; max index
  2^32-2). Setting `length` truncates the array. `arr[-1]`, `arr[1.5]`,
  `arr["01"]` are STRING-keyed properties, not indices — they don't affect
  `length` and don't appear in element iteration.

### bigint is a second, non-mixing numeric type

- `bigint` (`1n`) is arbitrary precision → Go `math/big.Int`. Mixing with
  `number` in arithmetic throws TypeError (the oracle can't have done it), but
  comparisons DO mix (`1n == 1` true, `1n < 2` true).
- `bigint` division truncates toward zero (`-7n / 2n === -3n`) → `big.Int.Quo`
  (NOT `Div`, which floors). `%` takes the sign of the dividend → `big.Int.Rem`
  (NOT `Mod`). Bitwise ops are infinite two's-complement → big.Int
  And/Or/Xor/Not match. `BigInt.asIntN/asUintN` wrap to n bits — port
  explicitly.
- `JSON.stringify` of a bigint THROWS. `typeof 1n === "bigint"`.

### undefined vs null — two distinct bottoms, three states

- `undefined` and `null` are DIFFERENT values with different observable
  behavior: JSON.stringify omits `undefined` object properties but emits
  `null`; default parameters trigger on `undefined` ONLY (`f(null)` does NOT
  take the default); `??` treats both as nullish; `typeof null === "object"`
  while `typeof undefined === "undefined"`.
- A Go `*T` nil can model only ONE bottom. Wherever the oracle distinguishes
  missing/undefined from null (any JSON boundary does), ALWAYS use a tri-state:

```go
type Val[T any] struct {
	V       T
	Null    bool // JS null
	Present bool // false ⇒ JS undefined / absent property
}
```

- `k in obj` vs `obj.k !== undefined` vs `obj.hasOwnProperty(k)` are three
  different tests (prototype chain, set-to-undefined, own). Identify which one
  the oracle uses per site and port THAT test against the tri-state.

### Objects are ordered reference types — aliasing is semantics

- Every object/array is a heap reference; assignment aliases, `===` is
  reference identity, mutation through one alias is visible through all.
  ALWAYS port mutable ported objects as Go POINTERS (`*T`); a value-struct copy
  silently forks state the oracle shares — a classic invisible divergence.
- Arrays: JS `b = a; b.push(9)` — `a` sees the 9. Go `append` may REALLOCATE
  and detach aliases. Port shared mutable arrays as `*[]T` (or a small Vec
  struct) whenever more than one reference mutates; plain `[]T` only for
  locally-owned arrays. `arr.slice()` copies; bare assignment aliases —
  mirror which one each site does.
- `sort`/`reverse` mutate in place AND return the receiver (aliased);
  `toSorted`/`toReversed`/`with` copy. Don't swap one for the other.
- Object literal property order, spread (`{...a, ...b}` — later wins,
  insertion order preserved), `Object.assign` — all follow the property-order
  rule in the Iteration section.

### TypeScript-specific runtime shapes

- TS types are erased; `enum` is NOT. A numeric `enum E { A }` compiles to an
  object with REVERSE mappings: `E.A === 0` AND `E[0] === "A"`, so
  `Object.keys(E)` is `["0", "A"]` — iteration/serialization over an enum
  object sees both directions. String enums have no reverse mapping. `const
  enum` inlines under tsc but is a plain object under some transpilers
  (esbuild/tsx) — pin the production transpiler (see Harness).
- `useDefineForClassFields` changes class-field init from assignment (invokes
  inherited setters) to defineProperty (shadows them) — observable if the
  oracle has accessor interplay. Port the behavior of the PRODUCTION tsconfig.
- Numeric enum members are plain numbers at runtime → port as typed Go
  constants, but remember any stringification of the member prints the NUMBER
  (`String(E.A) === "0"`), mirroring the Python `enum.value` seam:
  `strconv.Itoa(int(v))`, never the Go constant name.

---

## RNG (reproducibility)

- `Math.random()` is xorshift128+ in V8, but the state is seeded from OS
  entropy per context, there is NO seeding API, values are batch-generated
  (cache of 64) with engine-version-dependent consumption order, and other
  engines use other generators. It is EXACTLY Python's unseeded-RNG problem:
  **phase-0 MUST replace every `Math.random()` call with a project-owned
  seeded PRNG before any Go is written.** There is no seeded RNG in the JS
  standard library, and `crypto.getRandomValues` / `crypto.randomBytes` are
  CSPRNGs — also non-reproducible.
- Choosing the project PRNG — pick one with a portable public spec and a
  trivially-verifiable Go twin, and mind JS's numeric limits:
  - JS `number` cannot do native 64-bit integer ops. A 64-bit-state PRNG in JS
    needs either `BigInt` (exact but slow; mask every op with
    `& 0xFFFFFFFFFFFFFFFFn`) or hand-rolled 32-bit lane emulation
    (error-prone). PREFER a 32-bit-arithmetic PRNG built from `Math.imul` and
    `>>>`: **sfc32**, **mulberry32**, or PCG32 with explicit hi/lo lanes.
    `Math.imul` ↔ Go int32 wrap-multiply; `>>>` ↔ uint32 shift — both exact
    twins.
  - If the oracle already uses a library (`seedrandom` — ARC4-based, plus its
    `alea`/`xor128`/`xorshift7` variants; `chance.js`; `faker` seeding), port
    THAT exact algorithm variant; each has a published reference.
- Double derivation is part of the spec: document the EXACT bits-to-[0,1)
  formula and mirror it. Common JS forms and their Go twins:
  - `(u >>> 0) / 4294967296` → `float64(u32) / 4294967296.0`
  - `((hi >>> 5) * 67108864 + (lo >>> 6)) / 9007199254740992` (53-bit) →
    same expression in float64; the multiply-add is exact below 2^53.
  - NEVER "improve" to a bit-trick (`| 0x3FF…` mantissa fill) if the oracle
    divides — different low-bit distribution, instant desync.
- Golden vector: before porting anything downstream, pin seed → first 1000
  draws, compared as `Float64bits` hex on both sides (JS:
  `Buffer.allocUnsafe(8).writeDoubleBE(x)` → hex; Go:
  `fmt.Sprintf("%016x", math.Float64bits(x))`). A perturb-to-fail check
  (change the seed, assert mismatch) proves the test has teeth.
- ALWAYS preserve draw ORDER and stream separation, exactly as in the Python
  port: separate PRNG instances per subsystem (e.g. one per RNG-consuming
  subsystem) with mirrored seed lifetimes; log per-step draw counts on both
  sides; when counts diverge, fix the first step where one side draws extra.
- Draw-order landmines specific to JS:
  - `arr.sort(comparator)` — the NUMBER and ORDER of comparator invocations is
    engine-defined. If a comparator (or any callback with engine-defined call
    sequence) draws from the RNG or has side effects, phase-0 rewrite it to be
    pure BEFORE capture; Go cannot mirror V8's TimSort call sequence.
  - Shuffle idiom `arr.sort(() => Math.random() - 0.5)` is both biased AND
    engine-defined — phase-0 replace with Fisher-Yates over the project PRNG,
    then mirror Fisher-Yates (including the exact index formula, e.g.
    `Math.floor(rand() * (i + 1))` — floor of a float product, NOT a modulo).
- `uuid`/`crypto.randomUUID()` → phase-0 replace with seeded IDs, same rule as
  Python's `uuid4()`.

---

## Rounding & numeric ops

### The easy part — say it once, then trust it

- `+ - * /` on `number` are bare IEEE-754 double ops, bit-identical to Go
  float64 ops. `0.1 + 0.2` produces the SAME 0.30000000000000004 double in
  both languages. There is no Python-3.12-`sum()`-Neumaier surprise: JS has no
  builtin sum; `reduce((a, b) => a + b, 0)` is a plain left fold → a Go
  `for` loop accumulating in the same order is bit-equal.
- BUT reductions still depend on ORDER: mirror the exact iteration order of
  every accumulation (see Iteration), and never re-associate, vectorize, or
  parallelize a sum.
- `Math.sqrt` is IEEE correctly-rounded (hardware) in every engine; Go
  `math.Sqrt` too → bit-equal, safe.
- NaN comparison semantics match Go: all of `< <= > >=` with NaN are false,
  `NaN !== NaN`. Same audit as the Python port: a gate written `if (x > limit)`
  silently NOT-taken on NaN must stay not-taken in Go — never add a NaN guard.

### Math.round — half toward +Infinity, and two extra traps

- `Math.round` rounds ties toward **+∞** (NOT ties-to-even like Python, NOT
  ties-away-from-zero like Go `math.Round`): `Math.round(2.5) === 3`,
  `Math.round(-2.5) === -2`, `Math.round(0.5) === 1`,
  `Math.round(-0.5)` is `-0` (negative zero, spec-mandated).
- Do NOT implement it as `math.Floor(x + 0.5)`: the addition rounds —
  `Math.round(0.49999999999999994) === 0` per spec, but `0.49999999999999994
  + 0.5 === 1.0` in double arithmetic. Engines special-case this; your Go twin
  must too:

```go
// JSRound — ECMAScript Math.round: nearest integer, ties toward +Inf.
// Preserves ±0, NaN, ±Inf; never computes x+0.5.
func JSRound(x float64) float64 {
	if math.IsNaN(x) || math.IsInf(x, 0) || x == math.Trunc(x) {
		return x // integers, ±0, NaN, ±Inf pass through
	}
	if x > 0 && x < 0.5 {
		return 0
	}
	if x < 0 && x >= -0.5 {
		return math.Copysign(0, -1) // -0, per spec
	}
	f := math.Floor(x)
	if x-f >= 0.5 { // x-f is exact (Sterbenz): no double-rounding
		return f + 1
	}
	return f
}
```

- `Math.trunc` ↔ `math.Trunc`, `Math.floor` ↔ `math.Floor`, `Math.ceil` ↔
  `math.Ceil`, `Math.abs` ↔ `math.Abs` — direct, including ±0 behavior
  (`Math.ceil(-0.5)` is `-0` in both). `Math.sign` returns ±0 for ±0 and NaN
  for NaN — 3-line helper.
- `Math.min`/`Math.max`: NaN-propagating (any NaN arg → NaN) and `-0 < +0`
  for the purpose of min/max — Go 1.21 `math.Min`/`math.Max` and builtin
  `min`/`max` on floats match both rules. `Math.max()` with ZERO args is
  `-Infinity`, `Math.min()` is `+Infinity` — port the reduce identity.

### % is float remainder, / is float division, int-div doesn't exist

- JS `%` operates on DOUBLES and takes the sign of the dividend (C `fmod`):
  `-5 % 3 === -2`, `5 % -3 === 2`, `5.5 % 2 === 1.5`, `x % 0` is NaN.
  ALWAYS port as `math.Mod(a, b)`. NEVER Go integer `%` (panics on zero,
  int-only), NEVER `math.Remainder` (IEEE round-to-nearest remainder —
  different function: `math.Remainder(5, 3) == -1`).
- Integer division idioms — three DIFFERENT semantics; identify per site:
  - `Math.trunc(a / b)` → `math.Trunc(a / b)` (toward zero, no wrap)
  - `Math.floor(a / b)` → `math.Floor(a / b)` (toward -∞)
  - `(a / b) | 0` → `float64(ToInt32(a / b))` (toward zero WITH int32 wrap)
  A naive Go `int(a) / int(b)` matches none of them on negatives or large
  quotients.

### Exponentiation — a genuine spec divergence from C99/Go

- `**` and `Math.pow` are identical (Number::exponentiate). The spec DIVERGES
  from C99 `pow` (which Go `math.Pow` follows) in one family:
  `(±1) ** ±Infinity` is **NaN** in JS; `math.Pow(1, Inf) == 1` and
  `math.Pow(-1, Inf) == 1` in Go. Everything else (NaN exponent → NaN;
  exponent ±0 → 1 even for NaN base; 0/∞ cases) matches C99. Wrap it:

```go
func JSPow(x, y float64) float64 {
	if math.IsNaN(y) {
		return math.NaN()
	}
	if y == 0 {
		return 1 // even for NaN base — both specs agree
	}
	if (x == 1 || x == -1) && math.IsInf(y, 0) {
		return math.NaN() // ES diverges from C99/Go here
	}
	return math.Pow(x, y)
}
```

- Confidence: high — the ±1^±∞ NaN rule is explicit in the ES spec and a
  documented C99 divergence. Verify with a golden anyway (pow implementations
  also carry ULP risk, next item).

### Transcendentals — implementation-approximated, golden-vector every one

- `Math.sin/cos/tan/exp/log/log2/log10/log1p/expm1/atan2/asin/acos/atan/
  sinh/cosh/tanh/…/cbrt/pow/hypot` are spec'd as "implementation-approximated".
  V8 ships a port of **fdlibm** (`ieee754.cc`). Go's `math` package is ALSO
  largely fdlibm-derived, so many functions agree bit-for-bit — but nothing
  guarantees it, and `pow`, `hypot`, `cbrt`, `tanh` are historically the
  divergent ones (V8's hypot uses a different compensation scheme than Go's).
- ALWAYS: for each transcendental the oracle actually calls, run a golden
  sweep (a few thousand inputs covering subnormals, near-1, huge, negative,
  ±0, ±Inf, NaN) comparing `Float64bits`. Functions that match: use Go `math`.
  Functions that differ by even 1 ULP: vendor a Go transliteration of V8's
  `ieee754.cc` for that function and golden-pin it. A 1-ULP difference is a
  real divergence under the bit-exact gate — a long run amplifies it, exactly
  like the Python port's runtime-constant lesson.
- `Math.fround(x)` (round to float32) → `float64(float32(x))` — exact twin.
- NEVER hardcode a pre-computed constant where the oracle computes it at
  runtime — same rule as Python: mirror the exact multiply order from the same
  source values.

### toFixed / toPrecision / toString(radix)

- `toFixed(f)`: spec says choose integer n minimizing |n/10^f − x| computed on
  the EXACT binary value, and on an exact tie choose the **larger n**
  (toward +∞). Two consequences:
  - `(1.005).toFixed(2) === "1.00"` — not a bug; 1.005 is really 1.00499…
    (exact-value rounding). Go `strconv.FormatFloat(x, 'f', 2, 64)` also
    rounds the exact value → agrees here.
  - `(2.5).toFixed(0) === "3"` and `(-2.5).toFixed(0) === "-2"` (larger n),
    but Go FormatFloat rounds ties-to-even: `"2"` and `"-2"`. DIVERGENCE at
    exact decimal ties. Twin: detect the exact tie (x*10^f exactly halfway —
    do it in `big.Rat`) and bump toward +∞, else defer to FormatFloat.
  - `f` outside [0,100] throws RangeError; |x| ≥ 1e21 falls back to
    `toString`. Historic engine deviations from the spec existed; the pinned
    Node IS the oracle — golden-capture the sites that matter.
- `toPrecision(p)`: same family, same tie rule, plus its own
  positional-vs-exponential switch — golden-capture and mirror per site.
- `Number.prototype.toString(radix)` for radix ≠ 10: integers are exact
  (portable); FRACTIONS are implementation-approximated by spec — if the
  oracle formats fractional binaries/hex, golden-capture V8's output and
  replicate its digit-generation loop.

---

## Iteration & ordering

**THE BIGGEST SEAM. Read this section twice.** Go maps iterate in randomized
order — a naive port is nondeterministic on day one. But the fix is NOT
"insertion order" either: JS objects have their OWN spec-pinned order that
matches neither Go maps nor Python dicts.

### Object property order: integer keys first, ascending; then insertion

- For ordinary objects, own-property order is: (1) keys that are **array
  indices** — the CANONICAL string form of an integer in [0, 2^32-2] — in
  **ascending numeric order**; then (2) all other string keys in **insertion
  order**; then (3) symbol keys in insertion order. This governs `for...in`,
  `Object.keys/values/entries`, `Reflect.ownKeys`, object spread,
  `Object.assign`, and **`JSON.stringify`**.
- Concrete: `{b:1, "2":2, a:3, "1":4}` enumerates as `["1", "2", "b", "a"]`.
- Canonicality matters: `"01"`, `"1.0"`, `"+1"`, `"-1"`, `" 1"`, `"1e0"`,
  `"NaN"`, `"Infinity"` are STRING keys (insertion order). `"4294967295"`
  (2^32-1) exceeds the max array index — also a string key. `"0"` is an index.
- Property keys are ALWAYS strings (or symbols): `obj[1]` and `obj["1"]` are
  the same property; `obj[true]` is `obj["true"]`; `obj[1.5]` is
  `obj["1.5"]` (a string key!); `arr[2]` and `arr["2"]` are the same element.
  Port the key domain as `string` and coerce numeric keys through the
  number→string algorithm (Serialization section).
- Re-assigning an EXISTING key keeps its position; `delete` then re-add moves
  it to the end. Mirror exactly.
- Go twin — ordered object with the ES key rule:

```go
// JSObject: map + insertion order, enumerating per OrdinaryOwnPropertyKeys.
type JSObject struct {
	m     map[string]Value
	order []string // string-key insertion order (indices filtered at read)
}

func isArrayIndex(k string) (uint32, bool) {
	if k == "" || (len(k) > 1 && k[0] == '0') {
		return 0, false // non-canonical: "01", ""
	}
	n, err := strconv.ParseUint(k, 10, 64) // rejects "+1", "-1", "1.0", " 1"
	if err != nil || n >= 4294967295 {     // max array index is 2^32-2
		return 0, false
	}
	return uint32(n), true
}

// Keys reproduces Object.keys ordering: indices ascending, then insertion.
func (o *JSObject) Keys() []string {
	var idx, rest []string
	for _, k := range o.order {
		if _, ok := isArrayIndex(k); ok {
			idx = append(idx, k)
		} else {
			rest = append(rest, k)
		}
	}
	sort.Slice(idx, func(i, j int) bool {
		a, _ := isArrayIndex(idx[i])
		b, _ := isArrayIndex(idx[j])
		return a < b
	})
	return append(idx, rest...)
}
// Set: if key absent, append to order; if present, keep position.
// Delete: remove from order; a later Set re-appends (moves to end). Mirror JS.
```

- NEVER iterate a bare Go `map` anywhere in ported logic — same iron rule as
  the Python port. Every iteration goes through an ordered structure or an
  explicit sort on a business key.
- `for...in` additionally walks the PROTOTYPE chain (enumerable, non-shadowed)
  — rare in application code, but if the oracle does it, flatten the chain at
  port time. `Object.keys` is own+enumerable+string only.

### Map and Set: pure insertion order

- `Map`/`Set` iterate in insertion order; re-`set` of an existing key keeps
  position; `delete` + `set` moves to end — i.e. Python-dict-like. Mirror with
  the same slice+map ordered structure (no index sorting).
- Map keys use **SameValueZero**: `NaN` IS a usable key equal to itself; `+0`
  and `-0` are the same key; NO string coercion (`m.set(1, …)` and
  `m.set("1", …)` are DIFFERENT entries — the opposite of plain objects).
  Go trap: a `map[float64]V` with a NaN key is cursed — every NaN insert
  creates a new unreachable ghost entry. Normalize the key:

```go
func f64Key(x float64) uint64 {
	if x == 0 {
		x = 0 // collapse -0 into +0 (SameValueZero)
	}
	if math.IsNaN(x) {
		return math.Float64bits(math.NaN()) // one canonical NaN
	}
	return math.Float64bits(x)
}
```

- Entries added DURING iteration of a Map/Set are visited (iteration is live);
  deleted entries are skipped. If the oracle mutates while iterating, mirror
  the live semantics (iterate by index over the order slice, re-checking).
- Object keys in a Map compare by reference identity → Go pointer keys.

### Array.prototype.sort — three traps in one method

1. **Default comparator stringifies.** With no comparator, elements are
   converted via ToString and compared by UTF-16 code units:
   `[10, 9, 2, 1].sort()` → `[1, 10, 2, 9]`; `[-5, 1, -10].sort()` →
   `[-10, -5, 1]` only by accident of string order — compute it, don't assume.
   ALWAYS identify the ACTUAL comparator semantics per call site; a numeric
   sort in JS requires an explicit `(a, b) => a - b`.
2. **Stability.** Sort is required stable since ES2019 (V8 TimSort). ALWAYS
   `slices.SortStableFunc` / `sort.SliceStable` in Go — plain `slices.SortFunc`
   (pdqsort, unstable) reorders equal keys and diverges.
3. **Comparator return handling.** The spec uses the SIGN of the returned
   number: `v < 0` → a first, `v > 0` → b first, else equal; **NaN is treated
   as 0** (equal). Fractional returns work by sign (`-0.5` means "a first") —
   note: some references claim the return is "truncated toward zero"; the
   current spec does NOT truncate, it sign-tests, and for every consistent
   comparator the two readings agree (confidence: high, spec-verified
   behavior; the distinction is unobservable except through NaN, which is
   pinned to "equal" either way). The REAL traps:
   - `(a, b) => a - b` yields NaN when both are Infinity (or any NaN input) →
     "equal" → order falls back to stability, and an INCONSISTENT comparator
     makes the result implementation-defined. Phase-0: make comparators total
     and consistent (compare with explicit `<`), then mirror in Go returning
     -1/0/1.
   - `a - b` on huge doubles can underflow to ±0 for unequal values (precision)
     — same phase-0 fix.
   - Undefined elements sort to the END (before holes) regardless of
     comparator; the comparator is never called with undefined. Holes sort
     after everything. Model only if the oracle has sparse/undefined arrays —
     better: phase-0 eliminate them.
4. Comparator CALL ORDER is engine-defined — see RNG section: no side effects,
   no draws, in comparators, ever.

### Arrays: holes, sparse semantics, uint32 length

- `[1, , 3]` has a HOLE at index 1; `new Array(3)` is all holes,
  `delete arr[i]` creates one. Holes are OBSERVABLE: `forEach`/`filter`/`some`
  SKIP them; `map` skips but PRESERVES them in the output; `for...of` and
  spread yield `undefined` for them; `join` renders them (and `null`/
  `undefined`) as empty string; `JSON.stringify` renders them as `null`;
  `k in arr` is false for a hole; `includes(undefined)` FINDS a hole but
  `indexOf(undefined)` does NOT.
- Go slices cannot hold holes. If the oracle's data can be sparse, model
  presence explicitly (`[]Val[T]` with the tri-state) — or, strongly
  preferred, phase-0 the oracle to dense arrays and prove it with an
  `Object.keys(arr).length === arr.length` assert at decision sites.
- Method arguments that are indices go through **ToIntegerOrInfinity** —
  truncation toward zero, THEN negative-from-end handling: `arr.slice(1.9)`
  === `arr.slice(1)`, `arr.at(-1)` is the last element, `slice(-2)` counts
  from the end, NaN → 0. Port the coercions per call site.
- `arr.length = n` truncates or extends-with-holes. `push` returns the NEW
  LENGTH, `pop` returns the element (or undefined on empty — no panic; a Go
  pop on an empty slice must return the modeled undefined, not crash — this is
  the crash-vs-guard boundary: JS RETURNS a value here, so Go must too).
- Iterating `for (const k in arr)` yields STRING index keys plus any non-index
  props, in the object order rule; `for (const v of arr)` yields values.
  `forEach` reads `length` ONCE up front — elements appended during the loop
  are NOT visited; elements deleted before their visit are skipped. Mirror
  the snapshot-length semantics if the oracle mutates inside the loop.

---

## Equality, truthiness, null-ish

### Strict, loose, SameValueZero, Object.is — four equality relations

- `===`: no coercion; `NaN !== NaN`; `+0 === -0`; objects by reference.
  This is Go `==` on float64 (NaN, ±0 behavior matches) and pointer equality
  for objects. The DEFAULT port target.
- `==` performs type coercion. Phase-0: lint the oracle to `===` where
  behavior-preserving; where `==` sites remain load-bearing, port the exact
  algorithm. The trap table (memorize the shape, verify each site by
  execution):
  - `null == undefined` → true; each `==` NOTHING else (`null == 0` FALSE,
    `undefined == 0` false, `null == false` false).
  - number vs string → ToNumber(string): `"" == 0` true, `"0" == 0` true,
    `" \n" == 0` true, `"0x10" == 16` true.
  - boolean is ToNumber'd FIRST: `"0" == false` true, `[] == false` true
    (`[] → "" → 0`, `false → 0`), `"1" == true` true, `"2" == true` FALSE.
  - object vs primitive → ToPrimitive(obj) then retry: `[5] == 5` true,
    `[] == ![]` true (the classic).
  - `NaN == anything` false.
- **SameValueZero** (NaN equals NaN, ±0 equal): used by `Array.includes`, Map
  keys, Set membership. **`===`** used by `indexOf`/`lastIndexOf`. So
  `[NaN].includes(NaN)` is true but `[NaN].indexOf(NaN)` is -1 — port the
  matching predicate per method, don't unify.
- `Object.is`: NaN equals NaN AND ±0 distinguished — `math.Float64bits(a) ==
  math.Float64bits(b)`... careful: that exact-bits test also distinguishes NaN
  payloads; use `(a == b && signbit matches) || (IsNaN(a) && IsNaN(b))`.

### Truthiness — the falsy set is exactly eight values

- Falsy: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`.
  EVERYTHING else is truthy, including `"0"`, `"false"`, `[]`, `{}`,
  `new Boolean(false)`, and any non-empty string of whitespace.
- Go failure mode, spelled out: porting `if (x)` on a number as
  `if x != 0` is WRONG — `NaN != 0` is TRUE in Go, but NaN is FALSY in JS.
  Twin per type:

```go
func TruthyF(x float64) bool { return x != 0 && !math.IsNaN(x) } // -0 handled: -0 == 0
func TruthyS(s string) bool  { return len(s) > 0 }
// objects/arrays: ALWAYS truthy (even empty) — never port `if (arr)` as len>0!
// null/undefined: falsy via the tri-state tags.
```

- `if ([])` takes the branch; `if ([].length)` does not. Read carefully which
  one the oracle tests — `if (arr)` vs `if (arr.length)` is a real-world bug
  seam, and the port must reproduce whichever is written.

### || and && return operands; ?? is nullish; ?. short-circuits the chain

- `a || b` returns `a` if truthy, else `b` — returns the OPERAND, not a
  boolean. `x = cfg.timeout || 5000` treats a CONFIGURED 0 as missing. This is
  the JS twin of the Python port's configured-0.0 seam, inverted: here the
  oracle's own semantics drop the zero, so the Go port MUST also drop it —
  `if !TruthyF(v) { v = 5000 }` — NEVER "fix" it to a presence check. Port the
  truthiness fallback exactly as written; document it as intentional.
- `a ?? b` substitutes only for null/undefined — 0, "", NaN, false pass
  through. `??` and `||` sites port to DIFFERENT Go conditions; never conflate.
- `a && b` returns `a` if falsy else `b` — same operand-value rule.
- `a?.b.c()` — one `?.` short-circuits the ENTIRE remainder of the chain to
  `undefined` when `a` is null/undefined (the bare `.c()` after it does not
  throw). The result is always `undefined`, never `null`, even for `a === null`.
  Port as an early-return of the modeled undefined.
- Default parameters fire on `undefined` ONLY: `function f(x = 5)` — `f()`
  and `f(undefined)` give 5; `f(null)` gives null; `f(0)` gives 0. Port
  against the tri-state's Present/Null flags, not truthiness.
- Relational quirk: `null >= 0` is TRUE and `null > 0` is false (relational
  coerces null → 0) while `null == 0` is FALSE (equality doesn't). If the
  oracle compares possibly-null numbers, capture and mirror per site.
- Mixed-type `<`: string-vs-string compares UTF-16 code units
  (`"10" < "9"` true); anything else goes ToNumber (`"10" < 9` false).
  Identify the operand types per site — the two regimes flip results.

---

## Serialization (JSON)

`JSON.stringify` output is often the parity log itself — every rule here is a
gate rule.

### Value mapping

- **NaN / Infinity / -Infinity → `null`.** Silently — NOT an error (Python
  raises with allow_nan=False, emits `NaN` otherwise; JS does neither). A
  parity harness that lets stringify null NaNs will HIDE NaN divergences
  behind indistinguishable nulls. ALWAYS adopt the same convention as the
  Python port on BOTH sides: string sentinels `"NaN"`, `"Infinity"`,
  `"-Infinity"` emitted by an explicit replacer in JS and by the custom writer
  in Go. Better for floats that matter: co-emit hex bits
  (`%016x` of Float64bits) alongside the decimal.
- `-0` stringifies as `0` (ToString of -0 is "0"). Go's strconv would print
  `-0` — the custom number writer below handles it.
- `undefined`, functions, symbols: as an object property value → property
  OMITTED entirely; as an array element → `null`; as the top-level value →
  `JSON.stringify` returns `undefined` (not a string — anything printing it
  writes the literal text `undefined`). The tri-state drives all three.
- `bigint` → TypeError. `Map`/`Set` → `"{}"` (no own enumerable props — their
  contents are NOT serialized; a naive Go `json.Marshal(map…)` emitting
  contents is a divergence). `Date` → its `toJSON()` → ISO-8601 with
  MILLISECOND precision always: `"2026-07-13T12:00:00.000Z"`. Go twin:
  `t.UTC().Format("2006-01-02T15:04:05.000Z")` — Go's default time.Time
  marshaling (RFC3339, variable precision, offset form) does NOT match.
- Any object with a `toJSON` method is replaced by its result — audit for
  custom ones.
- Key order: exactly the object property order rule (integer-index keys first
  ascending, then insertion) — reuse `JSObject.Keys()` in the Go writer.
- Duplicate keys on PARSE: last one wins — Go encoding/json agrees (match).
- `JSON.parse` produces float64 for EVERY number: `JSON.parse("9007199254740993")`
  is 9007199254740992 — precision silently lost. Go decoding into int64 KEEPS
  it → divergence. ALWAYS decode ported-JSON numbers as float64 (or replicate
  the loss deliberately).

### Number formatting — implement ES ToString, don't approximate it

- JS number→string is the shortest-round-trip decimal PLUS fixed layout rules:
  positional notation for exponents in (-7, 21), exponential outside, with
  `e+`/`e-` and NO zero-padded exponent. Divergences from Go
  `strconv.FormatFloat(f, 'g', -1, 64)`:
  - `1e20` → JS `"100000000000000000000"`, Go 'g' `"1e+20"`.
  - `0.00001` → JS `"0.00001"`, Go 'g' `"1e-05"`.
  - `1e-7` → JS `"1e-7"`, Go `"1e-07"` (Go pads the exponent to 2 digits).
  - `-0` → JS `"0"`, Go `"-0"`.
  This is the single highest-traffic formatting seam: it appears in
  JSON.stringify, template literals, `String(x)`, `.join()`, string
  concatenation — everywhere. One Go function, used EVERYWHERE:

```go
// JSNumberToString implements ECMAScript Number::toString (radix 10).
func JSNumberToString(f float64) string {
	switch {
	case math.IsNaN(f):
		return "NaN"
	case f == 0:
		return "0" // covers -0
	case math.IsInf(f, 1):
		return "Infinity"
	case math.IsInf(f, -1):
		return "-Infinity"
	}
	neg := math.Signbit(f)
	mant := strconv.FormatFloat(math.Abs(f), 'e', -1, 64) // shortest "d.ddde±dd"
	e := strings.IndexByte(mant, 'e')
	digits := strings.Replace(mant[:e], ".", "", 1)
	exp10, _ := strconv.Atoi(mant[e+1:])
	n, k := exp10+1, len(digits) // spec's n (point position) and k (digit count)
	var s string
	switch {
	case k <= n && n <= 21: // integer with trailing zeros: 1e20
		s = digits + strings.Repeat("0", n-k)
	case 0 < n && n <= 21: // 123.456
		s = digits[:n] + "." + digits[n:]
	case -6 < n && n <= 0: // 0.00001
		s = "0." + strings.Repeat("0", -n) + digits
	default: // exponential: 1e+21, 1.5e-7 — sign always, no zero padding
		exp := n - 1
		m := digits[:1]
		if k > 1 {
			m += "." + digits[1:]
		}
		sign := "+"
		if exp < 0 {
			sign, exp = "-", -exp
		}
		s = m + "e" + sign + strconv.Itoa(exp)
	}
	if neg {
		s = "-" + s
	}
	return s
}
```

  (Shortest-digit generation itself — Ryū in both V8 and Go — agrees; only
  the LAYOUT rules differ, which is what this wrapper fixes. Golden-sweep it
  against Node anyway.)

### String escaping — Go encoding/json does NOT match JSON.stringify

- JSON.stringify escapes: `"` `\` and control chars, using shorthands
  `\b \t \n \f \r` and `\u00XX` for the rest. It does NOT escape `<`, `>`,
  `&`, and does NOT escape U+2028/U+2029 (valid in JSON strings, and legal in
  JS strings since ES2019). Since ES2019 it emits WELL-FORMED output: lone
  surrogates become `\udXXX` escapes.
- Go encoding/json by default escapes `<` `>` `&` to `\u003c…` AND escapes
  U+2028/U+2029 → `SetEscapeHTML(false)` fixes both. Remaining mismatches
  even then: Go emits `\u0008`/`\u000c` where JS emits `\b`/`\f`; Go replaces
  invalid UTF-8 with U+FFFD where JS escapes the lone surrogate. If the gate
  is byte-level log equality, write a small custom string escaper mirroring
  the ES QuoteJSONString table; otherwise normalize both sides before diff.
- Compact separators MATCH by default (`,` and `:`, no spaces) — unlike
  Python's `", "` default; one seam you don't have. `JSON.stringify(x, null,
  2)` indented form also matches Go MarshalIndent's `"key": value` shape
  closely, but ALWAYS keep parity logs compact — indentation is a diff-noise
  liability.

---

## Strings & text

### The model mismatch: UTF-16 code units vs UTF-8 bytes/runes

- A JS string is an immutable sequence of **UTF-16 code units** and may
  contain LONE SURROGATES (it need not be valid Unicode). A Go string is
  bytes (conventionally UTF-8); `len` is BYTES; `range` yields RUNES (code
  points); there is no unit-indexed access. Three different length notions:
  `"𝄞x".length === 3` (JS units), `utf8.RuneCountInString("𝄞x") == 2`
  (points), `len("𝄞x") == 5` (bytes).
- EVERY `.length`, `s[i]`, `charAt`, `charCodeAt`, `indexOf`, `slice`,
  `substring`, `padStart`, regex index, etc. is in code UNITS. When ported
  code indexes or measures strings and non-BMP input is possible (emoji,
  CJK-extension, any user text), ALWAYS operate on an explicit `[]uint16`:

```go
// UTF16Len — JS s.length.
func UTF16Len(s string) int {
	n := 0
	for _, r := range s {
		n++
		if r > 0xFFFF {
			n++ // astral code point = surrogate pair = 2 units
		}
	}
	return n
}

// Unit-faithful ops: convert once, operate on units, decode at the edge.
units := utf16.Encode([]rune(s)) // the JS string model
_ = units[i]                     // s.charCodeAt(i) (one unit, may be half a pair)
sub := string(utf16.Decode(units[a:b])) // s.slice(a, b) — may split pairs!
```

  Caveat: `s.slice` CAN split a surrogate pair, yielding a lone surrogate that
  does not survive a round-trip through a Go `string` (utf16.Decode → U+FFFD).
  If the oracle manipulates possibly-split strings, keep `[]uint16` as the
  PRIMARY representation and only decode for display.
- `for...of`, spread `[...s]`, `Array.from(s)`, `codePointAt` iterate code
  POINTS (Go `range` matches). But `s.split("")` splits into code UNITS
  (breaks pairs) — the two idioms differ on astral chars; port the one the
  oracle used.
- String comparison (`<`, sort order) is by UTF-16 code unit. Go string `<` is
  byte order, which equals CODE POINT order for valid UTF-8. These DIVERGE for
  astral characters: surrogates (0xD800–0xDFFF) sort BELOW 0xE000–0xFFFF, so
  in JS `"\u{10000}" < "｡"` is true, while Go says the opposite. Any
  ported sort over strings that can contain astral chars must compare via
  utf16 units. Confidence: high — this is the documented UTF-16-vs-code-point
  ordering wart.

### Case, trim, normalize — table mismatches

- `toUpperCase`/`toLowerCase` use Unicode FULL case mappings:
  `"ß".toUpperCase() === "SS"` (length changes), `"İ".toLowerCase()` is
  `"i̇"`. Go `strings.ToUpper` uses SIMPLE per-rune mappings —
  `strings.ToUpper("ß") == "ß"`. DIVERGENCE. Twin: `golang.org/x/text/cases`
  (`cases.Upper(language.Und)`), then golden-verify on the oracle's actual
  data. `toLocaleUpperCase` adds locale tables (Turkish dotless-i) — phase-0
  eliminate locale-sensitive ops or pin the locale AND the ICU build.
- `trim()` removes the ES WhiteSpace ∪ LineTerminator set, which includes
  U+FEFF (BOM) and U+00A0 (NBSP) and all Zs. Go `strings.TrimSpace` uses
  `unicode.IsSpace`: includes NBSP but NOT U+FEFF. A BOM-prefixed input trims
  clean in JS and survives in Go — build the exact cutset for the twin.
- `normalize("NFC"/"NFD"/…)` → `golang.org/x/text/unicode/norm`. JS strings
  are NOT auto-normalized; neither is Go — match, just port explicit calls.
- `localeCompare`, `Intl.*` (NumberFormat, DateTimeFormat, Collator) are
  ICU-and-version dependent — NOT reproducible even across two Node builds
  (small-icu vs full-icu). Phase-0: replace with project-owned formatting, or
  pin Node version + full-icu and treat the output as opaque goldens.

### String coercions (`String(x)`, templates, concat)

- `+` with any string operand concatenates after ToString of the other side:
  `1 + "1" === "11"` but `1 - "1" === 0` (`-` always numbers). `String(null)`
  → `"null"`, `String(undefined)` → `"undefined"`, arrays → `join(",")` with
  null/undefined/holes rendered EMPTY (`String([null]) === ""`,
  `String([1,[2,3]]) === "1,2,3"`), plain objects → `"[object Object]"`,
  numbers → JSNumberToString. Every implicit ToString in the oracle routes
  through these tables in the Go port — never through `fmt.Sprint`.

### Regex — a different engine family; treat every regex as a seam

- JS RegExp is a backtracking engine with backreferences, lookahead/lookbehind,
  sticky/global `lastIndex` STATE on the regex object (a stateful `/g` regex
  shared across calls is a real-world bug the port must reproduce), named
  groups, and `u`/`v` flag semantics. Go `regexp` is RE2: leftmost-first
  matching like Perl, but NO backreferences and NO lookaround, and it always
  operates on UTF-8 runes while a non-`u` JS regex matches UTF-16 code units
  (surrogate halves are matchable!).
- Rules: inventory every regex in the oracle. For each: (a) if it's a simple
  pattern with no backrefs/lookaround and `u`-flag-clean input, port to Go
  regexp and GOLDEN-VECTOR it (matches, groups, indices — remember JS indices
  are code units); (b) if it uses backrefs/lookaround, either rewrite it away
  in phase-0 or vendor a backtracking engine (`dlclark/regexp2` is
  .NET-flavored, NOT JS-flavored — golden-verify every pattern; do not assume).
  `replace`/`replaceAll` replacement patterns (`$1`, `$&`, `$'`, `` $` ``,
  `$<name>`) and function-replacers with their argument protocol are ported by
  hand.

---

## Differential harness invocation

- **Pin the oracle's runtime.** Node version drives V8 version drives
  transcendental bits, `Intl`/ICU tables, and occasionally sort internals.
  Pin via `.nvmrc` + `package.json` `engines` (+ volta/asdf), install with a
  frozen lockfile (`npm ci` / `pnpm install --frozen-lockfile`). Record the
  exact `node --version` inside every golden file header; a golden captured
  under a different Node is a wrong-tree oracle (the JS twin of "compare
  against the RIGHT worktree").
- **Pin the transpiler and target.** ts-node/tsx/esbuild/vitest-transform and
  `tsc` can produce DIFFERENT runtime behavior from the same TS: `target: es5`
  without `downlevelIteration` turns `for...of` over strings into a
  code-UNIT loop (astral chars split); `useDefineForClassFields` flips
  field-init semantics; `const enum` inlining differs. ALWAYS run the oracle
  through the SAME toolchain and tsconfig as production — ideally execute the
  compiled production JS, not a per-test transpile.
- **Kill ambient nondeterminism in the environment.** `TZ=UTC` (Date methods
  are TZ-sensitive; Node honors `$TZ`), fixed locale usage (no `toLocale*`),
  full-icu decision pinned, `NODE_OPTIONS` empty or pinned. Inject the clock
  (`Date.now`, `new Date()`, `performance.now`, `process.hrtime`) and the RNG
  in phase-0 — same as Python's phase-0.
- **Single-threaded, sequential test execution.** vitest/jest parallelize by
  default; parallel workers interleave logs and reorder side effects. Run the
  harness single-worker (`vitest --no-file-parallelism` / jest `--runInBand`,
  `testEnvironment: "node"`), no fake timers unless they ARE the injected
  clock.
- **Async is a determinism seam.** Microtask (Promise) ordering is
  spec-deterministic and `Promise.all` preserves input order, but timer-vs-IO
  interleavings are not reproducible. Phase-0: make the oracle's decision path
  effectively synchronous or drive it from ONE explicit job queue. In Go,
  NEVER port `async` to concurrent goroutines — mirror with a single
  goroutine / single dequeue loop, exactly like the Python port's concurrency
  rule. Awaits that interleave observable side effects must have their
  interleaving frozen (queue order logged and mirrored).
- **Harness shape** (mirror of the Python pytest harness): the JS test runner
  shells out to a Go parity binary — `go build -o <tmp> ./cmd/parity` in a
  globalSetup/pretest hook so a STALE Go BINARY CANNOT PASS, then per-case
  `execFileSync(bin, [component], { input: JSON.stringify(args) })`, compare
  outputs with the single committed comparator. Foot-guns, analogous to the
  Python "wrong venv" trap:
  - In a monorepo, run from the package that owns the oracle (its
    node_modules, its tsconfig); invoking from the Go module's dir or the
    workspace root resolves different deps/ESM-CJS modes and dies with
    module-resolution errors (or, worse, runs a different version).
  - ONE comparator, committed, used by every test. NaN/±Inf cross the pipe as
    the agreed string sentinels; floats co-emitted as Float64bits hex on both
    sides (`Buffer.writeDoubleBE` ↔ `math.Float64bits`) — the gate compares
    BITS, never epsilons, never decimal re-parses.
  - Keep decision-trace parity logs (JSONL, one record per decision, keys in
    a FIXED order via the JS number/string writers) co-emitted by oracle and
    port; diff key-aligned; fix the FIRST divergence in execution order.
    Aggregate-output equality remains a weak gate here too.
  - Adversarial input sweeps for the scalar harness: ±0, NaN, ±Inf,
    2^53±1, 2^31±1 (bit-op wrap), empty string, lone surrogate, astral
    string, integer-like object keys ("1" vs "01"), undefined-vs-null, holes.

---

## Seam catalogue

Each entry: **symptom → root cause → Go fix.**

1. **Number goes negative after `|0` / `>>>` result looks huge** → bitwise ops
   coerce through ToInt32/ToUint32 with mod-2^32 wrap, result back to float64
   → use `ToInt32`/`ToUint32` helpers; never raw Go casts; mask shifts `& 31`.
2. **Halves round the wrong way on negatives (−2.5 → −3 in Go, −2 in JS)** →
   `Math.round` is ties-toward-+∞ and Go `math.Round` is ties-away-from-zero →
   `JSRound` helper (and note `-0` results); never `Floor(x+0.5)`.
3. **Sorted numbers come out `[1,10,2,9]`** → default `sort()` stringifies and
   compares UTF-16 units → mirror the ACTUAL comparator; numeric sort only if
   the oracle passed `(a,b)=>a-b`; ALWAYS `slices.SortStableFunc` (ES2019
   stability); comparator NaN → treat as equal.
4. **JSON key order differs / map iteration nondeterministic** → JS objects
   enumerate integer-index keys first ascending then insertion order; Go maps
   randomize → `JSObject` ordered structure + `Keys()`; NEVER range a bare Go
   map in ported logic.
5. **Map/Set contents ordered differently** → Map/Set are insertion-ordered
   with delete+re-add moving to end, keys by SameValueZero (NaN usable, ±0
   merged, no coercion) → ordered map keyed by `f64Key` normalized bits /
   pointers.
6. **Runs differ run-to-run** → `Math.random()` unseedable engine PRNG (and
   `crypto.randomUUID`, `Date.now`) → phase-0 replace with project-owned
   seeded PRNG (sfc32/mulberry32 via `Math.imul` or BigInt splitmix64/PCG) +
   injected clock + seeded IDs; identical Go twin; golden vector of 1000 draws
   compared by bits; preserve draw order and stream separation.
7. **Time-dependent decisions unreproducible / TZ-dependent** → `new Date()`,
   `Date.now()`, TZ-sensitive getters → inject epoch-ms clock (a DOUBLE of
   ms — mirror precision), `TZ=UTC` in harness, port date math on epoch ms;
   `toISOString` twin format `"2006-01-02T15:04:05.000Z"` (always
   milliseconds).
8. **Array has "missing" slots that behave inconsistently across methods** →
   sparse arrays / holes (skipped by forEach/filter, preserved by map, `null`
   in JSON, empty in join, found by `includes(undefined)` not `indexOf`) → Go
   slices can't hold holes: phase-0 densify the oracle, else model presence
   with tri-state elements and port each method's hole rule.
9. **Type dispatch misbehaves on null** → `typeof null === "object"`,
   `typeof NaN === "number"`, `typeof []` is `"object"` (use Array.isArray) →
   explicit discriminator field in Go (same fix as Python's isinstance seam);
   port the oracle's actual dispatch test, quirks included.
10. **Parsed numbers differ from Go's strconv** → `parseInt` (greedy prefix,
    radix sniffing `0x`, `parseInt(0.0000001)` → 1 via `"1e-7"`,
    `parseInt(1e21)` → 1), `parseFloat` (greedy prefix, ignores trailing
    junk), `Number()` (`""`/whitespace → 0, `"0x10"` → 16, `"0b101"` → 5,
    `null` → 0, `undefined` → NaN, `[7]` → 7, `[1,2]` → NaN) → three distinct
    hand-written Go coercion helpers, one per function; NEVER a bare
    `strconv.Parse*`.
11. **Unary `+x` / arithmetic on non-numbers** → ToNumber coercion table
    (booleans → 0/1, strings trimmed then parsed, objects via
    ToPrimitive/valueOf) → port through one `ToNumber` helper; `+ ` with a
    string operand CONCATENATES — check operand types per site.
12. **Configured 0 / "" silently replaced by a default** → `x || fallback`
    tests truthiness, not presence → mirror EXACTLY
    (`if !Truthy(x) { x = fallback }`); this is oracle behavior, not a bug to
    fix; contrast `??` sites which pass 0/""/NaN through (tri-state test).
13. **NaN takes a branch in Go it never took in JS** → `if (x)` is falsy for
    NaN but Go `x != 0` is true for NaN → `TruthyF` helper; audit every
    ported numeric condition.
14. **`0.1+0.2`, plain arithmetic, `Math.sqrt`** → IEEE doubles both sides →
    bit-equal for free — the rare EASY case; do NOT add tolerance, keep the
    bit-exact gate; only ORDER of reductions matters.
15. **`%` wrong on negatives or floats, or Go panics on `% 0`** → JS `%` is
    float fmod, sign of dividend, `x % 0` = NaN → ALWAYS `math.Mod`; int-div
    idioms map: `Math.trunc(a/b)` → `math.Trunc(a/b)`, `Math.floor(a/b)` →
    `math.Floor(a/b)`, `(a/b)|0` → `float64(ToInt32(a/b))` — three different
    functions.
16. **`Math.pow(1, Infinity)` mismatch** → ES pins `(±1)**±∞` to NaN; C99/Go
    return 1 → `JSPow` wrapper.
17. **1-ULP drift in sin/exp/log/pow/hypot amplifying over a run** →
    transcendentals are implementation-approximated (V8 fdlibm vs Go math) →
    golden-sweep every used function by Float64bits; vendor a Go port of V8's
    `ieee754.cc` for any that differ; `Math.fround` → `float64(float32(x))`
    exactly.
18. **Numbers print differently (`1e+20` vs `10000000000000000000 0`, `1e-07`
    vs `1e-7`, `-0` vs `0`)** → ES Number::toString layout rules vs Go
    'g'-format thresholds and 2-digit exponents → `JSNumberToString`
    everywhere a number becomes text (JSON, templates, join, concat).
19. **`toFixed` ties differ (`(2.5).toFixed(0)`: JS "3", Go "2")** → ES picks
    the LARGER n at exact ties; Go FormatFloat is ties-to-even → custom
    helper: exact-tie detection via big.Rat, bump toward +∞; remember
    `(1.005).toFixed(2)==="1.00"` is exact-value behavior BOTH sides share.
20. **NaN/Inf silently become null in logs; divergences vanish** →
    `JSON.stringify` maps non-finite to `null` without error → harness
    convention: string sentinels + Float64bits hex co-emission on BOTH sides
    (same rule as the Python port).
21. **Property present-as-null vs absent confused** → `undefined` props are
    OMITTED by stringify, `null` props emitted; array `undefined` → `null`;
    top-level undefined → non-string → tri-state `Val[T]` with
    Present/Null; encode omission rules in the custom writer; default params
    fire on undefined ONLY.
22. **String lengths/indices off by one on emoji** → JS strings are UTF-16
    code units; Go len is bytes, range is runes → `UTF16Len`; unit-faithful
    ops on `utf16.Encode` output; `slice` can split surrogate pairs — keep
    `[]uint16` primary if the oracle does.
23. **String sort order flips for astral characters** → UTF-16 code-unit order
    (surrogates < 0xE000) vs Go's byte/code-point order → compare via utf16
    units in ported comparators.
24. **`"ß".toUpperCase()` length change missing; BOM survives trim** → JS full
    case mappings and ES whitespace set (incl. U+FEFF) vs Go simple mappings
    and unicode.IsSpace → `x/text/cases` for case; explicit cutset for trim;
    golden-verify on real data.
25. **Regex matches differ / Go regexp rejects the pattern** → JS backtracking
    engine (backrefs, lookaround, `lastIndex` state, unit-based indices) vs Go
    RE2 → inventory every regex; golden-vector matches+groups+indices; rewrite
    or vendor a backtracking engine, verified per pattern; port `$1`-style
    replacement templates by hand; watch stateful `/g` regexes shared across
    calls.
26. **Go JSON output has `<`, `\u0008`, escaped U+2028** → encoding/json
    HTML-escaping defaults and no `\b`/`\f` shorthands vs ES QuoteJSONString →
    `SetEscapeHTML(false)` plus a custom escaper if the gate is byte-level;
    Date fields via the toISOString twin, never Go's RFC3339 default.
27. **Map with float keys leaks unreachable entries / NaN lookups fail** → Go
    map + NaN key = ghost entries; JS Map uses SameValueZero → key by
    normalized bits (`f64Key`): collapse -0, canonicalize NaN.
28. **`arr["2"]` vs `arr[2]`, `obj[1]` vs `obj["1"]` treated as different** →
    property keys are strings; numeric keys canonicalize through
    Number::toString; `arr[1.5]`/`arr[-1]` are string props invisible to
    length/iteration → string key domain + `isArrayIndex` canonical test;
    `length` is uint32 with truncating setter.
29. **IDs/timestamps exact in Go, off-by-one in JS** → values past 2^53 lose
    precision in JS (including through JSON.parse) → keep float64 end-to-end,
    or prove the range; NEVER int64 "because it's an ID".
30. **`null >= 0` branch taken** → relational operators coerce null → 0 while
    `==` does not → port the site's exact operator semantics; add a
    capture-time assert if it looks unintended.
31. **TS enum iteration yields ghost numeric keys** → numeric enums emit
    reverse mappings (`{"0":"A","A":0}`) → if the oracle iterates/serializes
    an enum object, mirror BOTH directions; member stringification prints the
    NUMBER (`strconv.Itoa`), never the Go constant name.
32. **Behavior changes between dev runner and production build** → transpiler
    semantics (es5 for...of over strings = code units; class-field mode;
    const-enum inlining) → oracle == production toolchain, pinned tsconfig,
    ideally run compiled output.
33. **Two variables mysteriously in lockstep (or should be and aren't)** → JS
    objects/arrays are references; Go structs are values and `append` detaches
    aliases → port shared mutables as `*T`/`*[]T`; audit every `b := a` copy
    of a ported object; `slice()` copies, assignment aliases — mirror per
    site.
34. **Exception paths** → JS throws catchable errors on things Go panics on
    (nil deref) or handles silently (`pop()` on empty → undefined) → if the
    oracle CATCHES it, it's a reachable value-path: model with explicit error
    returns along the same path; if the oracle would crash uncaught, apply the
    crash-vs-guard boundary from the Python skill: pick keep-guard or
    undefined-input, document it, never let the guard leak onto reachable
    inputs; NEVER match engine-specific error message TEXT, match the control
    flow.
35. **Locale/Intl output differs across machines** → ICU version and small-icu
    vs full-icu → phase-0 remove `toLocale*`/`Intl` from decision paths or pin
    Node+ICU and quarantine the output as display-only.
36. **Async side effects interleave differently** → event-loop
    microtask/macrotask scheduling vs goroutines → phase-0 single explicit job
    queue in the oracle; single goroutine + ordered queue in Go; never "just
    use goroutines".
37. **`forEach` misses appended elements** → forEach snapshots `length` at
    start; deleted-before-visit skipped → mirror snapshot-length loop
    semantics when the oracle mutates during iteration.
38. **Labeled break/continue** → JS labels ≡ Go labels — direct map, EASY
    case; ASI (automatic semicolon insertion) has no residual runtime
    semantics to port: whatever ASI did (e.g. `return\nx` returning undefined)
    is already baked into the oracle's observable behavior — port the
    observed behavior and skip the syntax story.
39. **`[NaN].includes(NaN)` true but `indexOf` −1** → includes uses
    SameValueZero, indexOf uses `===` → per-method predicate, don't unify.
40. **`Math.max()` of an empty list** → identity values −Infinity/+Infinity
    (and NaN args propagate) → port the reduce identity; Go 1.21
    math.Min/Max NaN and ±0 semantics match JS for the binary case.
41. **Date parsing differs by format** → `new Date("2026-07-13")` is UTC
    midnight but `new Date("7/13/2026")` is LOCAL; month is 0-indexed;
    `getTimezoneOffset` sign is inverted; invalid dates are NaN-valued
    `Invalid Date` objects that propagate NaN through getters → phase-0
    replace parsing with explicit epoch-ms; if unavoidable, golden-capture the
    exact parse results under pinned TZ.
42. **`JSON.stringify(map)` is `{}`** → Map/Set have no own enumerable
    props → the twin serializes to `{}` too — do NOT helpfully serialize
    contents; audit for code that "worked by accident" this way.
43. **Comparator/callback draws RNG or mutates** → engine-defined call
    order/count in sort (and spec-defined-but-subtle in others) → phase-0
    purify callbacks BEFORE golden capture; Go cannot mirror V8's TimSort
    invocation sequence.
