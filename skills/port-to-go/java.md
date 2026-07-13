# Java → Go: behavioral-fidelity seams

> One-line: Java is fixed-width and mostly SPECIFIED — the danger is silent
> `int` wrap, UTF-16 strings, boxed-vs-primitive equality, spec'd library
> algorithms that must be cloned bit-for-bit (`java.util.Random`'s LCG,
> TimSort, `String.hashCode`, `Double.toString`) and the loudly UNspecified
> corners (`HashMap` order, identity `hashCode`, `Math.*` intrinsics) that
> phase 0 must pin before a single Go line is written.

The oracle is the pinned JVM program; correctness means matching it
bit-for-bit on the same seed, config, inputs, and clock. Java's semantics are
tighter than Python's or JS's — most of this file is *good news* (exactly
reproducible contracts) — but the reproducible parts are reproducible only if
you clone the exact algorithm, and the non-reproducible parts (hash order,
identity hash, default locale/charset/timezone) MUST be determinized in the
oracle first. Where behavior depends on JDK version or a JSON library, it is
flagged inline — re-verify those against the pinned oracle toolchain and fold
findings back into this file.

Terminology: **phase 0** = determinize the ORACLE (pin seeds, clocks, locales,
iteration orders) before porting. **crash-vs-guard** = Java throws where Go
would produce a value (or panics differently); decide per site: reproduce the
crash path if it is reachable business behavior, guard-and-document if it is
impossible-input territory.

## Type & numeric model

Fixed-width, two's-complement, SILENT WRAP on overflow. There are no unsigned
integer types (only unsigned *operations*: `>>>`, `Integer.toUnsignedLong`,
`compareUnsigned`, `divideUnsigned`).

- **Type mapping — memorize it, never improvise:**

  | Java      | Go twin   | Trap |
  |-----------|-----------|------|
  | `byte`    | `int8`    | Java `byte` is SIGNED (−128..127). Go's `byte` is `uint8` — the name is a false friend. `(byte)0xFF == -1`. |
  | `short`   | `int16`   | |
  | `char`    | `uint16`  | UNSIGNED 16-bit UTF-16 code unit. Widening to int ZERO-extends. |
  | `int`     | `int32`   | NEVER Go `int` (platform-width, usually 64) — kills wrap parity. |
  | `long`    | `int64`   | |
  | `float`   | `float32` | Keep arithmetic in `float32`; Go untyped constants default to float64 and silently change rounding. |
  | `double`  | `float64` | Identical IEEE-754 binary64. |
  | `boolean` | `bool`    | |

- **Overflow wraps silently.** `Integer.MAX_VALUE + 1 == Integer.MIN_VALUE`,
  `Math.abs(Integer.MIN_VALUE) == Integer.MIN_VALUE` (still negative!),
  `-Integer.MIN_VALUE == Integer.MIN_VALUE`. Go `int32`/`int64` arithmetic
  wraps identically — the parity bug is using Go `int` (64-bit) for a Java
  `int` so a value that wraps in Java doesn't wrap in Go:

  ```go
  var a, b int32 = math.MaxInt32, 1
  sum := a + b // -2147483648 — same as Java int overflow. Correct twin.
  // WRONG twin: int(a) + int(b) == 2147483648 — no wrap, silent divergence.
  ```

  `Math.addExact/multiplyExact/toIntExact` THROW `ArithmeticException` on
  overflow — crash-vs-guard sites, not wrap sites. Distinguish them when
  transcribing.
- **`Integer.MIN_VALUE / -1` wraps to `Integer.MIN_VALUE`** (no exception).
  Go's spec guarantees the same wrap for `int32`/`int64` — matches, no helper
  needed. (`%` gives 0 on both.)
- **Binary numeric promotion:** `byte`/`short`/`char` promote to `int` before
  ANY arithmetic; the result is `int`. `char + char` is `int` (`'a' + 'b'` is
  `195`, not a string, not a char). Mixed with `long` → `long`; with `float` →
  `float`; with `double` → `double`. In Go, convert operands to `int32` FIRST,
  operate in `int32`, and narrow back only where Java has an explicit cast.
  A Java expression `long x = a * b` with `int` a, b multiplies IN INT
  (wraps!) and then widens the wrapped result — reproduce the wrap, NEVER
  "fix" it by computing in `int64`. Source bugs are behavior.
- **Compound assignment hides a narrowing cast.** `byte b; b += 300;` compiles
  and wraps; `int i; i += 0.5;` compiles and truncates the double result back
  to int (`i *= 1.5` likewise). Go refuses to compile the analogue — you must
  write the promotion, the operation, and the narrowing cast explicitly, in
  Java's order.
- **Shift semantics.** Operands smaller than int promote to int first (so
  `byteVal >>> 2` sign-extends to int and THEN zero-shifts — surprising huge
  values for negative bytes). Shift count is MASKED: `& 31` for int, `& 63`
  for long — `1 << 32 == 1` in Java. Go does NOT mask (over-width shift yields
  0 / sign-fill). `>>` is arithmetic (sign-extending), `>>>` is logical
  (zero-fill), `<<` is plain. Go twins:

  ```go
  // Java: x << s      (int)  →  x << (uint32(s) & 31)
  // Java: x >> s      (int)  →  x >> (uint32(s) & 31)          // int32 x: arithmetic
  // Java: x >>> s     (int)  →  int32(uint32(x) >> (uint32(s) & 31))
  // Java: x >>> s     (long) →  int64(uint64(x) >> (uint64(s) & 63))
  ```

  ALWAYS mask; a variable shift count ≥ 32 that Java wraps and Go zeroes is a
  silent divergence.
- **Narrowing casts — three DIFFERENT rules, get each right:**
  - integral → smaller integral (`(int)aLong`, `(byte)anInt`, `(char)anInt`):
    keep the low bits, reinterpret sign. Go `int32(x)`/`int8(x)`/`uint16(x)`
    match exactly.
  - float/double → integral (`(int)d`, `(long)d`): NaN → 0; truncate toward
    zero; out-of-range SATURATES to `MIN_VALUE`/`MAX_VALUE`. Go's conversion
    is **implementation-dependent** for NaN/out-of-range (amd64 yields the
    `0x80000000...` sentinel; arm64 saturates) — ALWAYS use a helper:

    ```go
    // javaDoubleToInt mirrors Java's (int) narrowing of a double (JLS 5.1.3).
    func javaDoubleToInt(x float64) int32 {
        switch {
        case math.IsNaN(x):
            return 0
        case x >= math.MaxInt32:
            return math.MaxInt32
        case x <= math.MinInt32:
            return math.MinInt32
        }
        return int32(x) // in-range: truncation toward zero
    }
    // Same shape for (long): clamp at ±2^63 — note float64(math.MaxInt64)
    // rounds UP to 2^63, so use >= float64(math.MaxInt64) for the top clamp.
    ```
  - `double → float`: IEEE round-to-nearest-even, overflow → ±Inf. Go
    `float32(x)` matches.
- **Widening is implicit and can be LOSSY:** `int`→`float` and
  `long`→`float`/`double` round to nearest (16777217 as float is 16777216;
  longs beyond 2^53 lose low bits as double) with NO cast in the source.
  Transcribe every implicit widening as an explicit Go conversion at the same
  expression position — hoisting or delaying it changes rounding.
- **`char` ↔ int:** widening `char`→`int` ZERO-extends (0..65535); widening
  `byte`→`int` SIGN-extends; `(char)(byte)-1 == '￿'` (byte→char goes
  through int). The `b & 0xFF` idiom converts signed byte to 0..255 — in Go:
  `int32(b) & 0xFF` (with `b int8`).
- **Autoboxing + the Integer cache.** `Integer.valueOf` caches −128..127 (the
  UPPER bound is configurable: `-XX:AutoBoxCacheMax` /
  `-Djava.lang.Integer.IntegerCache.high` — JVM-config-dependent!). `Long`,
  `Short`: fixed −128..127; `Character`: 0..127; `Boolean`: both cached. So
  `Integer a = 100, b = 100; a == b` is TRUE and `Integer a = 1000, b = 1000;
  a == b` is FALSE — reference identity that flips at ±128. BUT
  `Integer x = 1000; x == 1000` is TRUE (a primitive operand forces unboxing
  → value comparison). Locate every `==` on boxed operands and decide what the
  oracle ACTUALLY computes at that site; reproduce that, even when it is a
  source bug. Unboxing `null` (e.g. `int v = map.get(missing)`) throws NPE —
  a crash path (see null-ish).
- **`BigInteger` → `math/big.Int`.** Semantics align well: division truncates
  on both; `BigInteger.mod` is always non-negative → Go `Int.Mod` (Euclidean);
  `BigInteger.remainder` → Go `Int.Rem`. `toString(radix)` lowercase both.
  Reproduce `intValue()` narrowing (low 32 bits) vs `intValueExact()`
  (throws) per site.
- **`BigDecimal` is its own world:** a value is (unscaledValue, scale) and the
  SCALE IS OBSERVABLE. `new BigDecimal("1.0").equals(new BigDecimal("1.00"))`
  is FALSE while `compareTo` says 0; `toString` switches to scientific
  notation by spec'd exponent rules (`toPlainString` never does);
  `add/multiply` produce spec'd result scales; `divide` WITHOUT a
  MathContext/scale THROWS `ArithmeticException` on non-terminating decimals;
  `setScale(n, mode)` rounds by an explicit `RoundingMode` (UP, DOWN, CEILING,
  FLOOR, HALF_UP, HALF_DOWN, HALF_EVEN, UNNECESSARY-throws);
  `new BigDecimal(0.1)` is the exact binary value
  0.1000000000000000055511151231257827…, while `BigDecimal.valueOf(0.1)`
  goes through `Double.toString` → exactly "0.1" — the two constructors are a
  classic in-oracle divergence to transcribe faithfully. Go has NO stdlib
  decimal; `shopspring/decimal` has different division precision and rounding
  defaults — do NOT map method names. Port a thin scale-tracking wrapper over
  `math/big.Int` implementing exactly the BigDecimal operations and
  RoundingModes the oracle uses, golden-tested against oracle outputs.
- **Fields default-initialize** (0 / 0.0 / false / null); array elements too.
  Go zero-values match for numerics/bool; `null` does NOT map to a Go zero
  value — see null-ish.

## RNG (reproducibility)

- **`java.util.Random` is NORMATIVELY specified** — the javadoc says
  implementations "must" use the given algorithms so seeds are portable across
  JVMs and versions. This is the best RNG news of any source language: an
  exact Go twin is straightforward. It is a 48-bit LCG: multiplier
  `0x5DEECE66D`, addend `0xB`, state masked to 48 bits, seed scrambled on
  set. Full twin (port ONLY the methods the oracle calls, but port them from
  this table, never from memory):

  ```go
  // JavaRandom is a bit-exact twin of java.util.Random.
  type JavaRandom struct {
      seed                 uint64 // low 48 bits of LCG state
      haveNextNextGaussian bool
      nextNextGaussian     float64
  }

  const (
      jrMult   = 0x5DEECE66D
      jrAddend = 0xB
      jrMask   = (1 << 48) - 1
  )

  func NewJavaRandom(seed int64) *JavaRandom {
      return &JavaRandom{seed: (uint64(seed) ^ jrMult) & jrMask}
  }

  // SetSeed mirrors Random.setSeed: re-scramble AND clear the Gaussian cache.
  func (r *JavaRandom) SetSeed(seed int64) {
      r.seed = (uint64(seed) ^ jrMult) & jrMask
      r.haveNextNextGaussian = false
  }

  func (r *JavaRandom) next(bits uint) int32 {
      r.seed = (r.seed*jrMult + jrAddend) & jrMask
      return int32(r.seed >> (48 - bits))
  }

  func (r *JavaRandom) NextInt() int32 { return r.next(32) }

  // NextIntBound mirrors nextInt(bound): power-of-two fast path,
  // then modulo with overflow-detecting rejection. Keep int32 arithmetic —
  // the rejection test RELIES on int32 wrap.
  func (r *JavaRandom) NextIntBound(bound int32) int32 {
      if bound <= 0 {
          panic("bound must be positive") // Java: IllegalArgumentException
      }
      if bound&-bound == bound { // power of two
          return int32((int64(bound) * int64(r.next(31))) >> 31)
      }
      for {
          bits := r.next(31)
          val := bits % bound
          if bits-val+(bound-1) >= 0 { // wraps negative → reject & redraw
              return val
          }
      }
  }

  func (r *JavaRandom) NextLong() int64 {
      hi := int64(r.next(32))
      lo := int64(r.next(32)) // SIGN-extended int, then ADDED — not OR'd
      return hi<<32 + lo
  }

  func (r *JavaRandom) NextBoolean() bool { return r.next(1) != 0 }

  func (r *JavaRandom) NextFloat() float32 {
      return float32(r.next(24)) / (1 << 24)
  }

  func (r *JavaRandom) NextDouble() float64 {
      return float64(int64(r.next(26))<<27+int64(r.next(27))) / (1 << 53)
  }

  // NextGaussian: Marsaglia polar method with a CACHED second value —
  // the cache is RNG state; dropping it desyncs every later draw.
  func (r *JavaRandom) NextGaussian() float64 {
      if r.haveNextNextGaussian {
          r.haveNextNextGaussian = false
          return r.nextNextGaussian
      }
      for {
          v1 := 2*r.NextDouble() - 1
          v2 := 2*r.NextDouble() - 1
          s := v1*v1 + v2*v2
          if s < 1 && s != 0 {
              m := math.Sqrt(-2 * math.Log(s) / s)
              r.nextNextGaussian = v2 * m
              r.haveNextNextGaussian = true
              return v1 * m
          }
      }
  }
  ```

  Gotchas inside the twin:
  - `nextLong` uses `+` on a SIGN-EXTENDED second half, not `|` on an
    unsigned one — `hi<<32 | uint(lo)` is a wrong twin that differs whenever
    the second draw is negative.
  - The `nextInt(bound)` rejection test `bits-val+(bound-1) < 0` detects
    int32 overflow — keep it in `int32`, never widen "for safety".
  - Java's `nextGaussian` calls `StrictMath.sqrt`/`StrictMath.log`. Go
    `math.Sqrt` is IEEE-correctly-rounded (identical everywhere); Go
    `math.Log` is FDLIBM-derived and expected bit-identical to
    `StrictMath.log` — VERIFY differentially on first use (draw 10^6
    Gaussians on both sides, compare bits), then trust it.
  - `nextBytes(buf)` fills 4 bytes per `nextInt()`, LOW byte first.
- **`Collections.shuffle(list, rnd)` is a spec'd back-to-front Fisher–Yates**:
  `for i := n; i > 1; i-- { swap(i-1, rnd.nextInt(i)) }` — draws are
  `nextInt(n), nextInt(n-1), …, nextInt(2)`. (For non-RandomAccess lists it
  copies to an array first; the draw sequence is identical.) Twin:

  ```go
  func JavaShuffle[T any](xs []T, r *JavaRandom) {
      for i := len(xs); i > 1; i-- {
          j := r.NextIntBound(int32(i))
          xs[i-1], xs[j] = xs[j], xs[i-1]
      }
  }
  ```

  NEVER substitute Go's `rand.Shuffle` (different algorithm direction AND
  different generator).
- **`Math.random()`** is a lazily created SHARED `Random` seeded from entropy
  — nondeterministic. Phase 0: replace with an injected seeded `Random` in the
  oracle.
- **`SplittableRandom` / `ThreadLocalRandom`** are SplitMix64-based:
  `nextSeed()` adds a gamma (default GOLDEN_GAMMA `0x9e3779b97f4a7c15`) and
  `nextLong()` applies Stafford mix13
  (`z=(z^(z>>>30))*0xbf58476d1ce4e5b9; z=(z^(z>>>27))*0x94d049bb133111eb;
  z^(z>>>31)`); `nextInt` uses a DIFFERENT mix32. Portable in principle when
  seeded, but the javadoc contract is weaker than `Random`'s — pin golden
  vectors from the oracle JVM before trusting a twin. `ThreadLocalRandom`
  CANNOT be seeded (`setSeed` throws) and `new SplittableRandom()` /
  `new Random()` (no-arg) seed from entropy/`nanoTime` — ALL are phase-0
  items: replace in the oracle with one project-owned seeded generator.
- **Java 17+ `RandomGenerator` algorithms** (`L64X128MixRandom`, …) are
  precisely specified in the `java.util.random` package docs — portable, but
  each needs its own twin; identify the algorithm string actually requested.
- **Preserve draw ORDER, draw COUNT, stream SEPARATION, and seed lifetimes**
  exactly as in the Python playbook: separate oracle `Random` instances →
  separate Go twins with the same seeds; a reseed (`setSeed`) is a lifetime
  event that also clears the Gaussian cache; when hunting a desync, log
  per-cycle draw counts on both sides and fix the FIRST cycle where counts
  differ.
- **`java.security.SecureRandom`** is nondeterministic by design (and
  `SHA1PRNG` seeded behavior is provider-dependent) — phase 0: replace at the
  seam with the seeded twin; never try to clone a provider.

## Rounding & numeric ops

- **`Math.round(double)` is half-up toward +∞, returning `long`:**
  `Math.round(2.5) == 3`, `Math.round(-2.5) == -2`, `Math.round(-2.6) == -3`.
  NOT ties-to-even (Python), NOT ties-away-from-zero (Go `math.Round` — which
  gives −3 for −2.5). And it is NOT literally `floor(x+0.5)`:
  `Math.round(0.49999999999999994)` is 0 on JDK 8+ because the addition
  `x+0.5` would round up to 1.0 in floating point (pre-JDK-8 JVMs returned 1 —
  JDK-8010430; pin the JDK). Specials: NaN → 0; ±∞/out-of-range saturate to
  `Long.MIN/MAX_VALUE`. Twin:

  ```go
  // javaMathRound mirrors Math.round(double): half-up (ties toward +Inf),
  // NaN→0, saturating — WITHOUT the x+0.5 double-rounding bug.
  func javaMathRound(x float64) int64 {
      switch {
      case math.IsNaN(x):
          return 0
      case x >= float64(math.MaxInt64): // float64(MaxInt64) rounds up to 2^63
          return math.MaxInt64
      case x <= float64(math.MinInt64):
          return math.MinInt64
      }
      f := math.Floor(x)
      if x-f >= 0.5 { // x - floor(x) is exact in IEEE-754
          f++
      }
      return int64(f)
  }
  ```

  `Math.round(float)` returns `int` with the same rules computed in float
  domain — mirror in `float32` arithmetic (floor and compare in float32),
  saturating to `Integer.MIN/MAX`.
- **`Math.rint` IS ties-to-even** → Go `math.RoundToEven` matches exactly.
  `Math.floor`/`Math.ceil` → `math.Floor`/`math.Ceil` (exact IEEE ops, safe).
  `Math.abs(double)` clears the sign bit (`abs(-0.0)==0.0`) → `math.Abs`
  matches. Don't confuse the three rounding functions when transcribing —
  round/rint/floor at one call site each produce different streams downstream.
- **Integer `/` truncates toward zero and `%` takes the dividend's sign** —
  IDENTICAL to Go for `int32`/`int64`. `Math.floorDiv`/`Math.floorMod`
  (floor toward −∞, result sign of divisor) have no Go builtin:

  ```go
  func javaFloorDiv(x, y int64) int64 {
      q := x / y
      if x%y != 0 && (x < 0) != (y < 0) {
          q--
      }
      return q
  }
  func javaFloorMod(x, y int64) int64 { return x - javaFloorDiv(x, y)*y }
  ```
- **Divide-by-zero is a crash-vs-guard fork:** int `/0` and `%0` THROW
  `ArithmeticException` (catchable — grep the oracle for catch blocks that
  make it control flow); double `/0.0` yields ±Infinity and `0.0/0.0` yields
  NaN with NO throw. Go panics on int `/0` (different failure shape — if the
  oracle catches, Go must pre-guard and reproduce the catch-path behavior) and
  matches the double behavior. The subtle divergence: Java code where an
  `int` gets implicitly widened before the division (`i / 2.0`) never throws —
  keep the operand types exactly.
- **Double `%` is fmod-style** (truncated, sign of dividend) → Go `math.Mod`.
  `Math.IEEEremainder` → Go `math.Remainder`. Two different operations; map
  each to its twin.
- **Floating point is reproducible arithmetic:** since Java 17 (JEP 306) all
  fp is strict; on any SSE2-era JVM it effectively already was. `+ - * /`,
  `sqrt` and `fma` (`Math.fma` ↔ `math.FMA`, both correctly rounded) are
  bit-identical between Java and Go GIVEN the same expression grouping and
  evaluation order — so, as always, mirror grouping/order exactly and never
  algebraically "simplify". Pre-17 32-bit x87 JVMs are out of scope; note it
  and move on.
- **`Math.*` transcendentals are the fp minefield.** The `Math` spec allows
  ≤1-ulp error (semi-monotonic), and HotSpot uses hardware/compiler
  INTRINSICS for `sin/cos/tan/log/log10/exp/pow` — results are stable for a
  pinned JVM version+arch but NOT defined by spec. `StrictMath` is exact
  fdlibm, bit-identical on every platform and stable across JDK versions (the
  JDK 21 Java-port of fdlibm is bit-preserving). Strategy:
  - Oracle uses `StrictMath` → port/adopt fdlibm-in-Go for exactly those
    functions; gate bit-exact.
  - Oracle uses `Math.*` → target StrictMath semantics anyway IF differential
    testing shows the oracle JVM matches (often true off the intrinsic paths),
    OTHERWISE capture oracle goldens on the pinned JVM+arch and match those;
    document the JVM build in the harness.
  - Go stdlib reality check: `math.Sqrt` is correctly rounded (always safe);
    `math.Log`/`math.Exp` are FDLIBM-derived (usually bit-identical to
    StrictMath — VERIFY); `math.Pow`, `math.Sin/Cos/Tan/Atan` are Cephes or
    home-grown, NOT fdlibm — expect ulp-level divergence from StrictMath and
    plan an fdlibm twin for any of these on a gated path. `math.Hypot`,
    `math.Cbrt`, `math.Log10` likewise differ.
- **String formatting of numbers rounds differently per API** — see Strings
  (`String.format` %f is HALF_UP; `DecimalFormat` default is HALF_EVEN;
  `Double.toString` is shortest-round-trip). Never assume one Java rounding
  convention; identify the API per call site.
- **The parity gate is BIT-EXACT float equality.** Compare
  `Double.doubleToRawLongBits`/`Double.doubleToLongBits` on the Java side with
  `math.Float64bits` on the Go side (as hex strings in the harness JSON).
  NEVER epsilon — tolerance hides exactly the 1-ulp seams above. Beware
  `doubleToLongBits` CANONICALIZES NaN while `doubleToRawLongBits` does not;
  pick one convention (canonical is usually right) and use it on both sides.

## Iteration & ordering

- **`HashMap`/`HashSet` iteration order is UNSPECIFIED** — a function of
  capacity history, the spread hash `h ^ (h >>> 16)`, insertion/removal
  sequence, and treeification (bins ≥ 8 entries with table ≥ 64 become
  red-black trees, Java 8+, changing within-bin order). It is deterministic
  for a fixed JDK build given an identical operation sequence — which is why
  source code gets away with relying on it — but it changes across JDK majors
  and is NOT a contract. If the oracle's observable output depends on it, that
  is a latent source bug: phase-0 fix the ORACLE (swap to
  `LinkedHashMap`/`TreeMap`, or sort before emitting), or, if the oracle is
  frozen, pin the OBSERVED order as goldens and reproduce it in Go by
  cloning the bucket layout (last resort — document it). In Go, NEVER `for k
  := range m` on an output-affecting path (Go randomizes intentionally):
  thread an explicit ordered key slice alongside every such map.
- **Identity hashCode makes some orders nondeterministic PER RUN.** Any class
  that doesn't override `hashCode()` (including EVERY enum —
  `Enum.hashCode` is final and identity-based!) hashes by an
  address/PRNG-derived identity hash. `HashSet<MyEnum>` or
  `HashMap<MyObject,…>` iteration order varies run-to-run ON THE ORACLE
  ITSELF. Phase 0: replace with `EnumSet`/`EnumMap` (ordinal order,
  deterministic) or `LinkedHash*`/sorted output in the oracle before
  capturing goldens. There is nothing to mirror until this is fixed.
- **`LinkedHashMap`/`LinkedHashSet` = insertion order** (re-insertion of an
  existing key does NOT move it). Mirror with map + ordered key slice. BUT
  `LinkedHashMap(cap, load, accessOrder=true)` is access-order: every `get()`
  MUTATES iteration order (LRU) — reads are writes; mirror the reorder
  exactly, and remember `removeEldestEntry` eviction if overridden.
- **`TreeMap`/`TreeSet` = comparator order.** Mirror with a sorted key slice
  (re-sorted or binary-insert on mutation) or a tree; equal-compare keys
  REPLACE (a comparator inconsistent with equals silently deduplicates —
  reproduce, don't fix). Natural ordering throws NPE on null keys —
  crash path.
- **`EnumMap`/`EnumSet` = ordinal (declaration) order** — deterministic;
  mirror with the declared constant order in Go.
- **`PriorityQueue`: `poll()` order is sorted, `iterator()` order is the raw
  binary-heap array** — unspecified but deterministic per op sequence. If the
  oracle ITERATES a PriorityQueue (or serializes it), mirror the exact
  siftUp/siftDown heap layout in Go, verified by goldens; if it only polls,
  any correct heap twin with the same comparator works — EXCEPT ties: heap
  order among equal elements is arbitrary-but-deterministic; with ties
  present, clone Java's sift algorithms exactly.
- **Sorting:**
  - `Collections.sort`, `List.sort`, `Arrays.sort(T[])`, `Stream.sorted` are
    STABLE (TimSort) → Go `sort.SliceStable`/`slices.SortStableFunc` at every
    such site where equal keys can occur. Go's `sort.Slice`/`slices.SortFunc`
    are NOT stable — a classic parity break.
  - `Arrays.sort(primitive[])` is dual-pivot quicksort, UNSTABLE — for a pure
    primitive array instability is unobservable (equal values are
    indistinguishable), so plain Go sorts are fine; but if the source sorts
    PARALLEL arrays or index arrays by a primitive key with its own manual
    sort, clone that exact algorithm.
  - TimSort THROWS `IllegalArgumentException` "Comparison method violates its
    general contract!" on inconsistent comparators — sometimes reached in real
    oracles (a comparator on floats using `<` with NaN present). Go never
    checks. Crash-vs-guard: if the oracle can throw here, that is behavior;
    phase-0 fix the comparator in the oracle or reproduce the crash.
  - `Arrays.sort(double[])` and `Double.compare` use the TOTAL order:
    `-0.0 < 0.0`, NaN GREATER than everything (all NaNs equal). Go
    `slices.Sort`/`sort.Float64s` put NaN FIRST and treat ±0.0 as equal —
    opposite placements. ALWAYS sort Go floats with an explicit twin:

    ```go
    // javaDoubleCompare mirrors Double.compare: -0.0 < 0.0, NaN is greatest.
    func javaDoubleCompare(a, b float64) int {
        if a < b {
            return -1
        }
        if a > b {
            return 1
        }
        ab, bb := int64(math.Float64bits(a)), int64(math.Float64bits(b))
        // canonicalize NaN like doubleToLongBits
        if math.IsNaN(a) {
            ab = 0x7ff8000000000000
        }
        if math.IsNaN(b) {
            bb = 0x7ff8000000000000
        }
        switch {
        case ab < bb:
            return -1
        case ab > bb:
            return 1
        }
        return 0
    }
    ```
  - `Comparator.comparing/thenComparing/reversed` chains: port as composed
    comparison functions preserving each stage's exact semantics
    (`comparingDouble` uses `Double.compare`, i.e. the total order above, NOT
    `<`).
  - `Collections.min/max` and `Stream.min/max` keep the FIRST extremal
    element in encounter order on ties — encounter order must therefore match
    (which circles back to map ordering).
- **Streams:** `collect(Collectors.toMap(...))` and `groupingBy(...)` return
  HASHMAPS — the order seam re-enters exactly where results get serialized.
  `distinct()` keeps the first occurrence (ordered streams). `HashSet
  .stream()` encounter order = hash order (unspecified). `parallelStream()` /
  `.parallel()` make `forEach` order and non-associative reductions
  nondeterministic — phase 0: make the oracle sequential (or `forEachOrdered`)
  before capturing goldens. `Collectors.joining` follows encounter order.
- **Fail-fast iterators:** structurally modifying a collection during
  iteration throws `ConcurrentModificationException` — BEST-EFFORT, not
  guaranteed (single-element removal via `Iterator.remove` is legal and does
  not throw). If the oracle relies on the throw as control flow, that's a
  crash path to reproduce deliberately; otherwise mirror with an explicit
  snapshot/index loop matching what the oracle actually does.
  `Map.computeIfAbsent` that inserts recursively can also throw CME (JDK 9+).
- **File-system order:** `File.listFiles()`/`Files.list()` order is
  OS-dependent and unspecified — phase 0: sort in the oracle.

## Equality, truthiness, null-ish

- **`==` is reference identity for objects, value equality for primitives;
  `.equals()` is value equality.** Transcribing `==` on objects as Go `==` on
  values is the classic Java-port bug — and the REVERSE (transcribing a Java
  identity check as Go value equality) silently changes behavior where the
  oracle distinguished two equal-valued instances (sentinel objects,
  interning accidents). Per `==`-on-objects site, decide: sentinel identity
  (mirror with a pointer or token), interning accident (see below), or source
  bug (reproduce its actual outcome).
- **String interning:** literals and compile-time constants are interned →
  `"a" == "a"` TRUE, `("a" + var) == "a"` generally FALSE,
  `new String("a") == "a"` FALSE, `.intern()` forces TRUE. Code that
  "works" via `==` on strings works only for literal-vs-literal — find each
  site and reproduce its truth value, not its intent.
- **Boxed `==`** — the Integer cache seam (see Type & numeric model): identity
  inside −128..127, distinct outside; mixed boxed/primitive `==` unboxes to
  value comparison. Reproduce per site.
- **`boolean` is a real type — NO truthiness.** `if (x)` requires boolean;
  there is no `0`-is-false. The only truthiness-adjacent trap is
  auto-UNBOXING: `if (boxedBoolean)` NPEs when null; `cond ? someInt :
  boxedIntegerNull` NPEs (ternary numeric promotion unboxes BOTH branches).
  These are crash paths — reproduce or guard-and-document.
- **Boxed vs primitive double equality DISAGREE — model both:**
  - primitive: `NaN == NaN` FALSE, `0.0 == -0.0` TRUE (Go float64 matches).
  - boxed (`Double.equals`/`Double.compare`/`Double.hashCode`, and therefore
    ALL collections): `NaN.equals(NaN)` TRUE, `0.0 vs -0.0` NOT equal
    (`doubleToLongBits` canonicalizes NaN, distinguishes zero signs).
  - Consequence for float-keyed collections: a Java `HashMap<Double,V>` can
    STORE and RETRIEVE a NaN key, and keeps `0.0` and `-0.0` as TWO entries.
    A Go `map[float64]V` is the exact opposite: NaN keys are unretrievable
    (every insert adds a new zombie entry) and ±0.0 collapse to one key.
    ALWAYS key the Go twin by canonicalized bits:

    ```go
    // javaDoubleKey mirrors Double.equals/hashCode key semantics.
    func javaDoubleKey(x float64) uint64 {
        if math.IsNaN(x) {
            return 0x7ff8000000000000 // doubleToLongBits canonical NaN
        }
        return math.Float64bits(x) // keeps -0.0 distinct from 0.0
    }
    ```
- **`null` is the single bottom value.** Dereference → NPE (crash path;
  catchable and sometimes caught — grep for `catch (NullPointerException`).
  `Map.get(missing)` returns null (vs `containsKey` for stored nulls —
  `HashMap` PERMITS null keys and values; `TreeMap` natural order and
  `ConcurrentHashMap` do NOT). Go: `v, ok := m[k]` covers get-vs-contains;
  mirror `*T`/`(T, bool)` for nullable values and NEVER conflate Go zero
  values with Java null — a null that Java would NPE on must not become a
  silent Go `0`.
- **`switch` on a null String/enum throws NPE** (pre-Java-21 semantics; 21+
  pattern-switch may have a `case null`) — crash path at every switch whose
  selector can be null.
- **String concatenation swallows null:** `"x" + null` is `"xnull"`;
  `String.valueOf((Object)null)` is `"null"`; `println(null)` prints `null`.
  Go `fmt` prints `<nil>` — never let a formatting shim leak `<nil>` into
  gated output; emit the literal `null` text.
- **hashCode contracts are SPECIFIED for value types and sometimes leak into
  behavior** (bucketing, sharding, "order by hash", hash-mixed IDs). Reproduce
  exactly when observable: `Integer.hashCode()==value`;
  `Long.hashCode()==(int)(v^(v>>>32))`; `Double.hashCode()` = Long fold of
  `doubleToLongBits` (canonical NaN); `Boolean.hashCode()` = 1231/1237;
  `String.hashCode` (see Strings); `List.hashCode` = 31-polynomial starting
  at 1 (null element → 0); `Set.hashCode` = SUM of element hashes
  (order-independent); `Map.hashCode` = sum of `keyHash ^ valueHash`;
  `Objects.hash(...)`/`Arrays.hashCode` = the List rule; `Enum.hashCode` =
  IDENTITY (nondeterministic — phase-0 item if observable). Default
  `Object.hashCode` is per-run nondeterministic (thread-local PRNG in
  HotSpot) — never reproducible, only removable.
- **Arrays don't override equals/hashCode:** `arr1.equals(arr2)` is IDENTITY
  (`==`), `arr.hashCode()` is identity hash — code that meant
  `Arrays.equals`/`Arrays.hashCode` but called the plain ones has
  identity semantics; reproduce the outcome the oracle actually computes.

## Serialization (JSON)

Java has NO stdlib JSON. The oracle's library AND version AND configuration
are part of the oracle — pin all three in the harness
(`jackson-databind:2.x.y` / `gson:2.x.y` in the lockfile) and byte-capture
goldens. Everything below is library-specific; re-verify against the pinned
version.

- **NaN/Infinity — agree ONE convention on both sides, in the harness
  itself:**
  - Jackson: by default writes them as QUOTED strings `"NaN"`, `"Infinity"`,
    `"-Infinity"` (`QUOTE_NON_NUMERIC_NUMBERS` on by default); with that
    feature off, bare invalid-JSON tokens. Reading needs
    `ALLOW_NON_NUMERIC_NUMBERS`.
  - Gson: THROWS `IllegalArgumentException` on NaN/±Inf unless
    `serializeSpecialFloatingPointValues()` — then bare `NaN`/`Infinity`
    tokens (invalid JSON).
  - Go `encoding/json`: refuses to encode non-finite floats (error).
  - Harness rule: pre-walk both sides into string sentinels
    (`"NaN"`/`"Infinity"`/`"-Infinity"`) and drive NaN-case skips to zero;
    NEVER skip a parity case because "JSON can't carry it".
- **Integral doubles keep `.0`:** Java is typed, so `long 42` → `42` and
  `double 42.0` → `42.0` (both Jackson and Gson route doubles through
  `Double.toString`-style output). Go `encoding/json` prints `float64(42)` as
  `42` and uses different exponent thresholds (`1e21` style vs Java's
  `1.0E21`). ALWAYS install a custom Go float encoder that reproduces
  `Double.toString` (see Strings) for gated JSON; never hand json.Marshal a
  raw float64 on a gated path. JDK 19 changed `Double.toString` digits —
  the JSON output is JDK-version-dependent; pin the JDK.
- **Null fields:** Jackson INCLUDES nulls by default (`Include.NON_NULL` to
  omit); Gson OMITS nulls by default (`serializeNulls()` to include). Match
  the oracle's actual output with explicit Go struct tags / custom encoding —
  do not guess from the Java class, check the emitted bytes.
- **HTML escaping:** Gson escapes `< > & = '` as `<…` BY DEFAULT
  (`disableHtmlEscaping()` turns off). Go escapes `< > &` by default
  (`encoder.SetEscapeHTML(false)` turns off). Jackson escapes neither.
  Three different defaults — byte-diff fails until matched exactly.
- **Property order:** Jackson emits POJO properties in roughly declaration
  order (NOT guaranteed; records = declaration order;
  `@JsonPropertyOrder` / `SORT_PROPERTIES_ALPHABETICALLY` pin it); Gson uses
  reflection field order (practically declaration order, also not
  spec-guaranteed). Go structs marshal in declaration order. Pin: annotate the
  oracle or golden-capture, and keep Go struct field order matching the
  OBSERVED oracle output.
- **Map serialization order = the map's iteration order** → a `HashMap` leaks
  the unspecified-order seam straight into JSON bytes. Phase 0: make the
  oracle use `LinkedHashMap`/`TreeMap` or Jackson
  `ORDER_MAP_ENTRIES_BY_KEYS`; in Go use an ordered-map encoder (struct or
  key-slice walk), never a bare Go map (Go json SORTS map keys — yet another
  third ordering).
- **`byte[]`:** Jackson → Base64 STRING; Gson → JSON ARRAY of numbers
  (signed bytes!). Go `[]byte` → Base64 (matches Jackson only). Check which
  one the oracle emits.
- **Deserialization number typing:** Jackson reads untyped numbers into
  Integer/Long/BigInteger/Double by size; Gson (into `Object`) historically
  makes EVERYTHING a Double (`1` re-emits as `1.0` — version-dependent,
  `ToNumberPolicy` since 2.8.9). If the oracle round-trips JSON through
  untyped maps, reproduce the type mangling, not the original document.
- **Longs are exact up to 2^63** in Java JSON — but any JS consumer (or a
  float64-based comparator) corrupts beyond 2^53. Harness comparator MUST
  parse numbers as raw tokens / `json.Number`, never float64.
- **Pretty printing:** Jackson's `DefaultPrettyPrinter` writes `"key" : value`
  (spaces AROUND the colon) with 2-space indent; Go `MarshalIndent` writes
  `"key": value`. If the oracle pretty-prints gated output, mirror the exact
  separator; prefer compact output on both sides.
- **char** serializes as a 1-character string; enums as `name()` strings by
  default (ordinal only if configured) — mirror the declared constant names
  exactly, including case.
- **java.time / Date:** formats depend entirely on module registration
  (`JavaTimeModule`, `WRITE_DATES_AS_TIMESTAMPS`) — golden-capture; never
  guess an ISO format.

## Strings & text

- **`String` is a sequence of UTF-16 CODE UNITS.** (Compact strings since
  JDK 9 are invisible.) `.length()`, `charAt(i)`, `substring`, `indexOf`
  positions all count code units — a non-BMP character (emoji, some CJK) is
  TWO units. Go strings are UTF-8 bytes; `len()` is bytes, `range` yields
  runes. At every site where Java measures/indexes/slices text that can carry
  non-BMP characters, use a UTF-16 view:

  ```go
  // javaStringLength mirrors String.length(): UTF-16 code units.
  func javaStringLength(s string) int {
      n := 0
      for _, r := range s {
          if r > 0xFFFF {
              n += 2 // surrogate pair
          } else {
              n++
          }
      }
      return n
  }
  // For charAt/substring-heavy code, convert once: utf16.Encode([]rune(s))
  // and operate on the []uint16, mirroring Java indices exactly.
  ```

  `codePointAt`/`codePoints()` are code-point APIs; `chars()` streams UNITS.
  Map each to the right view.
- **Unpaired surrogates are legal in `String`** (it is not necessarily valid
  Unicode). If the oracle can split inside a pair or synthesize lone
  surrogates, a Go `string` cannot carry them faithfully — represent those
  values as `[]uint16` end-to-end. Divergence to remember:
  `getBytes(UTF_8)` on a lone surrogate emits `?` (0x3F, encoder REPLACE
  default), while a naive Go utf16→utf8 path emits U+FFFD (EF BF BD).
- **`String.hashCode()` is SPECIFIED and eternal:**
  `h = 31*h + charAt(i)` over code units, int wrap, `"" → 0`. It leaks into
  behavior via bucketing/sharding/partitioning. Twin:

  ```go
  // javaStringHashCode mirrors String.hashCode(): 31-polynomial over
  // UTF-16 code units with int32 wrap.
  func javaStringHashCode(s string) int32 {
      var h int32
      for _, r := range s {
          if r > 0xFFFF {
              r -= 0x10000
              h = 31*h + int32(0xD800+(r>>10))
              h = 31*h + int32(0xDC00+(r&0x3FF))
          } else {
              h = 31*h + int32(r)
          }
      }
      return h
  }
  ```
- **`String.compareTo` is UTF-16 code-unit order; Go string `<` is UTF-8
  byte order (= code-point order).** They DISAGREE when comparing a non-BMP
  character against a BMP character in U+E000..U+FFFF: Java sees the surrogate
  (0xD800..0xDFFF) as smaller. Example: Java `"�".compareTo("😀") > 0`;
  Go `"�" < "😀"`. Any Java-sorted string list containing emoji/rare-CJK
  needs a code-unit comparator in Go, not `slices.Sort`.
- **`String.split(regex)` drops TRAILING empty strings by default**
  (limit 0): `"a,b,,".split(",")` → `["a","b"]`; leading empties are KEPT
  (`",a"` → `["", "a"]`); all-empty results collapse to `[]`
  (`"aaa".split("a")` → length 0); `"".split(",")` → `[""]`. Negative limit
  keeps trailing empties; positive limit caps the count (last element carries
  the rest). Go `strings.Split`/`regexp.Split` keep trailing empties — wrap
  with a Java-limit shim. And the separator is a REGEX (`split("|")` splits
  between every char — a classic source bug to reproduce), unlike
  `String.replace` which is LITERAL while `replaceAll`/`replaceFirst` are
  regex with `$1` group refs and backslash escapes — three different APIs,
  never mix them up while transcribing.
- **Regex flavor is java.util.regex, a BACKTRACKING engine:** backreferences,
  lookahead/lookbehind, possessive quantifiers, `\b`, inline flags. Go
  `regexp` is RE2 — NO backreferences or lookaround. Port pattern-by-pattern
  (rewrite to RE2 where provably equivalent; otherwise implement the match
  logic manually or vendor a backtracking engine) and differential-test each
  pattern against oracle-captured cases. `matches()` anchors the WHOLE
  string; `find()` scans; `Matcher.group` numbering and `appendReplacement`
  escaping are their own details. `\d \w \s` are ASCII-only by default
  (`UNICODE_CHARACTER_CLASS` changes them); `CASE_INSENSITIVE` is ASCII-only
  unless `UNICODE_CASE`. Go RE2 `\d\w\s` are ASCII too, but its
  case-insensitivity `(?i)` IS Unicode — flag mismatch on non-ASCII input.
- **Case conversion:** no-arg `toUpperCase()/toLowerCase()` use the DEFAULT
  LOCALE — the Turkish/Azeri dotted-i and Lithuanian rules change results per
  environment. Phase 0: pin `Locale.ROOT` in the oracle (or
  `-Duser.language=en -Duser.country=US`). Even under ROOT, Java performs
  FULL case mappings: `"ß".toUpperCase()` → `"SS"`, ligature `"ﬁ"` → `"FI"` —
  LENGTH CHANGES. Go `strings.ToUpper` is a 1:1 simple mapping (ß stays ß!).
  Use `golang.org/x/text/cases` for full mappings and verify against the
  oracle: Unicode table versions differ per JDK (JDK 17 ≈ Unicode 13,
  JDK 21 ≈ 15.0) and per x/text version. `equalsIgnoreCase` is NOT full
  folding — it is per-code-unit `toUpper==` OR `toLower==`; clone that
  algorithm, don't substitute `strings.EqualFold` (which is Unicode simple
  folding — close but not identical at edge code points).
- **Whitespace sets differ THREE ways.** `String.trim()` strips chars
  `<= U+0020` only (so NOT NBSP, but yes all C0 controls). Java 11+
  `strip()` uses `Character.isWhitespace`: EXCLUDES no-break spaces
  (U+00A0, U+2007, U+202F) and NEL (U+0085), INCLUDES the file/group/record
  separators U+001C–U+001F. Go `unicode.IsSpace` INCLUDES U+00A0 and U+0085,
  EXCLUDES U+001C–U+001F. `strings.TrimSpace` therefore matches NEITHER
  `trim` nor `strip`. Implement `javaTrim`/`javaStrip` predicates explicitly.
- **`Double.toString` is a spec'd format you must clone** — it feeds string
  concatenation (`"" + d`), `String.valueOf`, `println`, log lines, and both
  JSON libraries. Rules: `"NaN"`, `"Infinity"`, `"-Infinity"`, `"0.0"`,
  `"-0.0"`; plain decimal for `1e-3 <= |x| < 1e7`, otherwise computerized
  scientific `d.dddEn` (capital `E`, no `+` on positive exponents, exactly
  one digit before the point); ALWAYS at least one fractional digit
  (`1.0`, `1.0E7`); digits are the shortest string that round-trips —
  **JDK-version seam:** exactly-shortest only since JDK 19 (JDK-4511638);
  ≤ 18 occasionally emits extra digits on specific values. Pin the oracle
  JDK and golden-test the Go twin (`strconv.FormatFloat(x, 'g', -1, 64)`
  gives shortest DIGITS but the wrong placement/format rules — write the
  placement logic around it). `Float.toString` is the analogous float32
  algorithm with different thresholds — same treatment.
- **`String.format`/`Formatter`:** `%f`/`%e`/`%g` round HALF-UP over the
  EXACT decimal expansion of the binary double —
  `String.format("%.1f", 0.25)` → `"0.3"` while Go `fmt.Sprintf("%.1f",
  0.25)` → `"0.2"` (Go converts correctly-rounded, ties-to-even). Java `%g`
  also differs from C/Go `%g` (Java never strips trailing zeros, precision
  counts total significant digits). No-locale `String.format` uses the
  DEFAULT locale (decimal comma in many!) — phase-0 pin `Locale.ROOT`.
  Meanwhile `DecimalFormat` defaults to HALF-EVEN (a different default than
  Formatter, inside one JDK) and takes symbols from the locale. Port
  format-string sites individually with per-site goldens; never map verbs
  1:1 to `fmt`.
- **Parsing:** `Integer.parseInt`/`Long.parseLong` throw
  `NumberFormatException` (crash path), accept a leading `+`/`-`, do NOT
  trim whitespace, radix 2..36 — and accept NON-ASCII Unicode digits (via
  `Character.digit`: `parseInt("١٢٣") == 123`) which `strconv.Atoi` rejects.
  `Double.parseDouble` DOES trim leading/trailing chars ≤ U+0020, accepts
  `"NaN"`/`"±Infinity"` (exact case — Go's `ParseFloat` accepts
  case-insensitive `inf`/`infinity`), hex-float literals (`0x1.8p1`), and a
  trailing `d/D/f/F` suffix. Write `javaParseInt`/`javaParseDouble` wrappers
  that reproduce accept/reject EXACTLY — the reject set is behavior
  (exception vs parsed value).
- **Index errors throw** (`StringIndexOutOfBoundsException`,
  `substring(begin > end)`) — Go panics with a different shape;
  crash-vs-guard per site.
- **Default charset:** no-arg `getBytes()`/`new String(byte[])` used the
  PLATFORM charset before JDK 18; JDK 18+ (JEP 400) defaults to UTF-8.
  Phase 0: make the oracle pass `StandardCharsets.UTF_8` explicitly (or pin
  `-Dfile.encoding=UTF-8`); note the JDK version either way. Decoding
  invalid bytes: `new String(bytes, UTF_8)` REPLACES malformed input with
  U+FFFD (matches Go's decoder behavior); `CharsetDecoder` with
  REPORT throws — check which path the oracle uses.
- **`Character.isDigit/isLetter/isWhitespace` are Unicode tables of the
  pinned JDK** — close to Go's `unicode` package but not identical
  (different Unicode versions, and the isWhitespace deltas above).
  Differential-test any classification that gates behavior.
- **Concatenation promotion trap:** `"" + 'a' + 'b'` is `"ab"` but
  `'a' + 'b' + ""` is `"195"` (left-assoc, char+char is int). Transcribe the
  exact association.

## Differential harness invocation

- **Pin the oracle toolchain and record it in the harness:** JDK vendor +
  exact version (e.g. Temurin 21.0.4), the JSON library + version, and the
  arch. JDK version changes observable behavior: `Double.toString`
  (JDK 19), default charset (JDK 18), always-strict fp (JDK 17), Unicode
  tables, `HashMap` internals across majors. `java -version` output belongs
  in the harness README and in the golden metadata.
- **Pin the JVM environment on EVERY invocation** — these are silent behavior
  inputs: `-Duser.timezone=UTC -Duser.language=en -Duser.country=US
  -Dfile.encoding=UTF-8`, fixed `LANG`/`LC_ALL` in the shell, assertions on
  (`-ea`). A parity harness without these reproduces only on the author's
  machine.
- **Shape:** JUnit (5) parity tests call the REAL oracle code path — never an
  inlined re-implementation of the formula in the test (hand-copy vs
  hand-copy stays green while both real paths diverge) — then spawn the Go
  parity binary via `ProcessBuilder` with JSON on stdin, JSON on stdout, and
  compare through ONE committed comparator. Floats travel as bit patterns
  (`Long.toHexString(Double.doubleToLongBits(x))` ↔
  `fmt.Sprintf("%016x", math.Float64bits(x))`), never as decimal text and
  never with epsilon. Integers > 2^53 travel as strings or are compared as
  raw JSON tokens.
- **Rebuild the Go binary every session:** a `@BeforeAll` (or a Gradle task
  the test task `dependsOn`) runs `go build -o build/parity ./cmd/parity` so
  a stale binary can never silently pass. NEVER commit the binary.
- **Build-tool foot-guns:** the Gradle daemon and incremental test selection
  can skip "up-to-date" parity tests — run with `--rerun-tasks` (or make the
  parity task never up-to-date); Maven surefire equivalently. Forked test
  JVMs REUSE static state between test classes (`forkEvery` default 0) —
  mutable static fields in the oracle become a hidden ordering dependency
  between parity cases; set `forkEvery 1` (or isolate state per case) when
  case order changes results. That reuse sensitivity is itself a finding:
  static mutable state in the oracle is a lifetime seam to mirror.
- **Phase-0 checklist for the JVM oracle** (do these IN THE ORACLE before
  capturing any golden): no-arg `new Random()` / `Math.random()` /
  `ThreadLocalRandom` / `new SplittableRandom()` → one injected seeded
  generator; `UUID.randomUUID()` → sequential IDs;
  `System.currentTimeMillis`/`nanoTime`/`Instant.now()` → injected
  `Clock.fixed`; `HashSet`/`HashMap` iteration that reaches output (ESPECIALLY
  over enums or hashCode-less classes) → `LinkedHash*`/`EnumMap`/sorted;
  `parallelStream()`/threads → sequential; directory listings → sorted;
  locale/charset/timezone → pinned flags above. Only then port.
- Heavier tiers (long horizons, big vectors) opt-in via env var; the fast
  tier runs unconditionally in CI. `--tests` filters confirm case counts
  cheaply before full runs.

## Seam catalogue

Each entry: symptom → root cause → Go fix.

1. **Large computed value differs by exactly 2^32 or flips sign** → Java
   `int` wrapped, Go `int` (64-bit) didn't → use `int32` for every Java
   `int`; audit arithmetic done in int before widening (`long x = a*b`).
2. **Comparison true in Java, false in Go (or vice versa) for small
   numbers only** → boxed `Integer ==` hits the −128..127 valueOf cache →
   reproduce the site's actual identity outcome; note the cache high bound is
   JVM-configurable.
3. **Values ending in .5 round differently** → `Math.round` is half-up
   toward +∞; Go `math.Round` is half-away-from-zero (differs on negatives),
   `math.RoundToEven` is banker's → `javaMathRound` twin; also check
   0.49999999999999994 (no `floor(x+0.5)` shortcut).
4. **Sorted output swaps equal-keyed records** → Java object sorts are
   stable TimSort; `sort.Slice` isn't → `sort.SliceStable` /
   `slices.SortStableFunc` at object-sort sites (primitive-array sorts don't
   need it).
5. **Sort crashes the oracle with "Comparison method violates its general
   contract!"** → TimSort detects an inconsistent comparator (often NaN
   under `<`) → crash path: reproduce or phase-0 fix the comparator; Go
   never throws it.
6. **Float array/list sorts put NaN at opposite ends; −0.0 vs 0.0 order
   differs** → Java `Double.compare` total order (NaN greatest, −0.0<0.0) vs
   Go `slices.Sort` (NaN first, ±0 equal) → sort via `javaDoubleCompare`.
7. **Emitted map/JSON key order differs, or flaps across JDK upgrades** →
   `HashMap` iteration order is unspecified (capacity, spread hash,
   treeify) → phase-0: LinkedHashMap/TreeMap/sort in the oracle; Go: ordered
   key slice, never bare map range (and never Go json's sorted-map-keys
   "fix").
8. **Oracle output order flaps RUN-TO-RUN with no code change** →
   identity `hashCode` (enums! hashCode-less classes) feeding
   `HashSet`/`HashMap` → phase-0 only: EnumSet/EnumMap/LinkedHash*/sorted in
   the oracle; there is nothing deterministic to mirror.
9. **RNG stream matches for a while then desyncs at some bound-dependent
   draw** → `nextInt(bound)` rejection loop (extra draws near the bias
   threshold) replaced by naive `%` in Go → clone the power-of-two fast path
   + int32 rejection loop exactly.
10. **Every second Gaussian differs (or one extra draw appears after a
    reseed)** → `nextGaussian` caches its second polar value;
    `setSeed` clears the cache → carry
    `haveNextNextGaussian`/`nextNextGaussian` as state; clear on SetSeed.
11. **`nextLong` values differ only when the low half is "negative"** → Java
    ADDS a sign-extended second `next(32)`; the Go twin OR'd unsigned
    halves → `hi<<32 + int64(int32(lo))`.
12. **Shuffles differ despite identical LCG** → `Collections.shuffle` is
    back-to-front Fisher–Yates with `nextInt(i)` draws; Go `rand.Shuffle`
    differs → `JavaShuffle` twin over the twin RNG.
13. **Hash-derived bucketing/sharding differs** → `String.hashCode` (or the
    boxed-type hash specs) reimplemented loosely → clone the 31-polynomial
    over UTF-16 units with int32 wrap (`javaStringHashCode`).
14. **String lengths/indices differ on emoji input** → Java counts UTF-16
    code units, Go counted bytes or runes → UTF-16 view (`[]uint16`) at every
    length/index/substring site.
15. **String sort order differs on emoji vs U+E000..FFFF text** →
    `compareTo` is code-UNIT order; Go byte order is code-POINT order →
    UTF-16 code-unit comparator.
16. **Split results differ in empty-string tails** → Java `split` (limit 0)
    drops trailing empties (keeps leading), collapses all-empty to `[]` → Java
    split shim over `regexp.Split`; also verify the pattern survives RE2.
17. **A regex behaves differently or won't compile in Go** → java.util.regex
    backtracking features (backrefs, lookaround, possessive) vs RE2 →
    per-pattern port + differential pattern tests; never "close-enough" a
    pattern on a gated path.
18. **Uppercased text differs in length or Turkish/German content** →
    locale-sensitive full case mapping (default locale; ß→SS) vs Go 1:1
    simple mapping → pin Locale.ROOT in the oracle; x/text `cases` in Go;
    goldens per JDK Unicode version.
19. **Trim/strip removes different characters (NBSP, U+001C–1F, NEL)** →
    three different whitespace sets (`trim` ≤0x20, `Character.isWhitespace`,
    Go `unicode.IsSpace`) → explicit `javaTrim`/`javaStrip` predicates,
    never `strings.TrimSpace`.
20. **`%.2f`-style output differs on ties (0.25 → 0.3 vs 0.2)** → Java
    Formatter rounds HALF-UP on the exact decimal expansion; Go formats
    ties-to-even → per-site formatter twin (exact big.Float/big.Rat decimal
    expansion + HALF_UP); DecimalFormat sites are HALF-EVEN instead — check
    which API each site uses.
21. **Doubles print as `42.0`/`1.0E7` in Java but `42`/`1e+07` in Go (JSON
    or logs)** → `Double.toString` format rules + Jackson/Gson reuse of
    them vs Go's `%g`/json encoder → `javaDoubleToString` twin (thresholds
    1e-3/1e7, capital E, mandatory fractional digit); pin JDK ≥19 vs ≤18
    for shortest-digit behavior.
22. **JSON bytes differ in `<` escapes, missing nulls, or `"NaN"`** →
    library defaults: Gson HTML-escapes and omits nulls and throws on NaN;
    Jackson includes nulls and quotes NaN; Go escapes HTML and errors on
    NaN → pin library+version+config in the harness; sentinel convention for
    non-finite; match escaping and null-inclusion explicitly.
23. **Integer JSON field re-emits as `1.0` after a round-trip** → Gson
    deserializes untyped numbers to Double (version/ToNumberPolicy-
    dependent) → reproduce the oracle's type mangling; compare as raw
    tokens in the harness.
24. **Go computes a value where Java crashed (or vice versa) on zero
    input** → int `/0` throws ArithmeticException in Java (catchable,
    sometimes caught) but double `/0.0` yields ±Inf/NaN → keep operand
    types exact; where Java catches, pre-guard in Go and reproduce the
    catch-path; NEVER add a Go zero-guard Java lacks.
25. **Casted floats differ wildly on NaN/overflow inputs** → Java
    float→int narrowing is NaN→0 + saturating; Go conversion is
    implementation-dependent (amd64 sentinel vs arm64 saturate) →
    `javaDoubleToInt`/`javaDoubleToLong` helpers at every cast site.
26. **A value differs only for shift counts ≥ 32** → Java masks shift
    counts (`&31`/`&63`); Go doesn't → mask explicitly; and remember `>>>`
    = unsigned shift via `uint32`/`uint64` round-trip.
27. **Negative bytes decode differently from a byte stream** → Java `byte`
    is signed and widens with sign-extension; Go `byte` is uint8 → use
    `int8` and transcribe every `& 0xFF` exactly.
28. **BigDecimal totals differ in trailing zeros, or Go divides where Java
    threw** → scale is observable; `equals` includes scale; bare `divide`
    throws on non-terminating expansion → scale-tracking big.Int wrapper
    cloning the exact RoundingMode per operation; transcribe
    `new BigDecimal(double)` vs `valueOf(double)` faithfully.
29. **Float-keyed map lookups: Java finds NaN / keeps ±0 separate, Go
    doesn't (zombie NaN entries)** → `Double.equals/hashCode`
    (bit-canonical) vs Go IEEE `==` map keys → key by `javaDoubleKey`
    (canonicalized Float64bits).
30. **Missing-key reads yield 0 in Go where Java NPE'd** → unboxing
    `map.get(missing)` throws; Go zero-value is silent → `v, ok :=` +
    explicit crash-vs-guard decision per site; never let Java null become
    Go 0.
31. **Concatenated log/string output shows `195` instead of `ab` (or
    "xnull")** → char+char promotes to int before string concat;
    `"x"+null` is `"xnull"` → transcribe association order; emit literal
    `null`, never Go's `<nil>`.
32. **Transcendental results off by 1 ulp, platform-dependent** → `Math.*`
    HotSpot intrinsics vs StrictMath fdlibm vs Go Cephes-derived
    `Pow/Sin/Cos/Tan` → target StrictMath; fdlibm-Go twins for the
    functions on gated paths; `math.Sqrt` (and likely `Log`/`Exp`, verify)
    are safe.
33. **Parse accepts/rejects differently ("١٢٣", " 1.0 ", "infinity",
    "0x1.8p1")** → `parseInt` takes Unicode digits & no whitespace;
    `parseDouble` trims, is case-sensitive on "Infinity", takes hex floats
    and d/f suffixes → `javaParseInt`/`javaParseDouble` wrappers; the
    exception-vs-value outcome is behavior.
34. **Iteration crashes the oracle with ConcurrentModificationException**
    → fail-fast iterator saw a structural modification (best-effort!) →
    reproduce the crash if reachable business behavior; otherwise mirror
    the oracle's actual snapshot/index pattern.
35. **Parity green on dev machine, red in CI (or after JDK bump)** →
    unpinned default locale/charset/timezone/JDK version leaking through
    `String.format`, `getBytes`, case mapping, `Double.toString` →
    pin `-Duser.*`, `-Dfile.encoding`, TZ, and the exact JDK in the
    harness; record versions in golden metadata.
