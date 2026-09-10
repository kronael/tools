# Diagnosing and fixing V8 deoptimization in a Node hot path

A hot loop that "should" be fast but isn't is almost always megamorphism
(too many hidden classes at one call site) or profiler noise pointing at the
wrong phase — never guess which; measure both before changing code.

## 1. Measure hidden classes directly — never guess which side is polymorphic

`node --allow-natives-syntax` script, call `%HaveSameMap(a, b)` pairwise over a
sample of the objects hitting the hot site, and bucket them into equivalence
classes. Do this for BOTH the input objects and any accumulator/output objects
— the polymorphic side is not always the one you suspect. In one investigation
the incoming DTOs were monomorphic (1 map each) while the accumulators being
built had 9 distinct maps across only 14 instances; optimizing the DTOs would
have been wasted effort.

## 2. Confirm with the IC log, not `--trace-ic`

`--trace-ic` does not exist as a node flag and is rejected at the CLI. Use:

```
node --log-ic --logfile=x.log --no-logfile-per-isolate script.js
```

This writes CSV lines: field 1 is the IC type (e.g. `KeyedLoadIC`), fields 6
and 7 are old/new state, field 9 is the property key. State `N` is
MEGAMORPHIC, `G` is GENERIC. A repeated `N->N` transition for a given key
means every access at that site is missing the inline cache. ALWAYS attribute
hits before trusting them — re-run a build-only variant of the workload (skip
your code, keep the library calls) to see which megamorphic sites belong to a
dependency rather than the code you're changing.

## 3. Isolate the phase before profiling — a naive `--prof` run conflates phases

`node --prof` over a whole script attributes setup cost (parsing/materializing
test fixtures) to the same self-time table as the pipeline under test, and
will point at the wrong functions. Instead, drive the inspector protocol
directly around only the phase being measured, after a warmup call so JIT
tiers have already settled:

```js
const { Session } = require('inspector')
const session = new Session()
session.connect()
session.post('Profiler.enable')
session.post('Profiler.start')
// ...run only the phase under test...
session.post('Profiler.stop', (err, { profile }) => { /* self-time table */ })
```

This changed the conclusion in one case: a date-formatting library turned out
to be ~35% of the phase, more than the megamorphism it was investigating.

## 4. Root cause for accumulators: insertion order, not field count

Assigning object fields conditionally ("only when the source value is
present") makes property INSERTION ORDER vary per object instance, and V8
hidden classes are keyed by insertion order — this is what multiplies maps
even when every instance ends up with the same field set. Fix with a factory
that declares the complete field set in a fixed order on every call,
initializing absent fields to `undefined` (not `null`) whenever any consumer
tests `!== undefined`.

## 5. A `keyof T`-indexed helper cannot be specialized — unroll it

A generic helper that reads `obj[field]` where `field: keyof T` is a variable
compiles to a keyed IC regardless of how monomorphic the objects are; TurboFan
cannot specialize a computed property access. Replace it with explicitly named
field accesses. Verify the fix landed by grepping compiled output for the
computed form — `grep '\[field\]' dist/**/*.js` (or the actual variable name)
returning empty means no keyed loads survive from your code.

## 6. Cache per-calendar-day work, watch UTC/local boundary mismatches

Per-item work that only changes once per calendar day (date formatting,
bucket keys) belongs behind a cache keyed by day number. If one derived value
keys off UTC calendar fields and another off local start-of-day, the cache key
MUST combine both day numbers — a single day number is wrong on any day that
straddles a local midnight.

## 7. Don't `await` a call that's usually synchronous

`await maybeAsyncHelper()` costs a microtask tick on every call even when the
helper returns a plain (non-promise) value most of the time. Call it first,
inspect the result, and only `await` when it is actually a promise.

## 8. Prove behavior is unchanged with a golden diff, not tests alone

Dump the full output plus the raw internal values (as exact strings, not
compared numerically) across the cross-product of input configurations, run
that harness against the pre-change build, and require byte-for-byte
equality — not "close enough." A golden diff that catches nothing across a
wide input grid is what licenses touching numeric/arithmetic code paths that
unit tests alone wouldn't give confidence to change.

## 9. Know when to stop

Once megamorphism and profiler-noise costs are gone, check what dominates the
remaining self-time. If it's an arbitrary-precision or correctness-driven
library (e.g. decimal.js) rather than JIT overhead, report that boundary
instead of continuing to micro-optimize — going faster from there means
changing the data representation, not the runtime's compilation behavior.

**Calibration**: applying steps 1-7 together on a 60k-block/121k-transaction
grouping pipeline took it from 793.7ms to 244.8ms end-to-end, with output
proven byte-identical via step 8.
