# Money and exact arithmetic

For any quantity where being off by one unit is a defect: currency, token
amounts, ledger entries, invoices, tax, interest.

## The one rule

**NEVER represent money as a float.** Not `float`, not `double`, not `number`,
not a JSON number that decodes to one. `0.1 + 0.2 != 0.3` is the least of it —
the real failure is silent: a value past 2^53 loses its low bits with no error,
so a large amount is quietly wrong rather than rejected.

That includes the decode step. `json.Unmarshal` into `any`, `JSON.parse`, and
`strconv.ParseFloat` all produce floats. ALWAYS decode a monetary field from its
literal text (Go: `Decoder.UseNumber` then `ParseInt`; JS: keep the string).

## Reach for big decimal LAST, not first

The instinct is "money is decimal, so use BigDecimal / decimal.js everywhere."
That is usually wrong and always expensive. Work down this list and stop at the
first row that fits — most domains stop at row 1 or 2.

| Situation | Use | Why |
|---|---|---|
| The domain HAS an atomic unit (cents, lamports, satoshi, wei) | plain integer of that unit | Exact by construction. There is no sub-unit quantity to lose — you are not approximating a decimal, you are counting. |
| A rate or price at a known fixed scale | scaled integer (`price x 1e8`), REJECT deeper input | Fixed scale is exact and comparable; rejecting surfaces a feed change instead of silently rounding it. |
| A product or sum of the above | a WIDER fixed-width integer, with a checked add | This is the row people miss. See below. |
| Accumulation with no provable bound, or division whose remainder must survive | arbitrary precision | Genuinely unbounded. Rare. |

**Row 3 is the one that gets skipped, and skipping it is what sends people to
BigDecimal unnecessarily.** Multiplying two 64-bit scaled integers needs 128
bits to stay exact — the result is wider than either input. That is a *width*
problem, not a *precision* problem, and the fix is a wider integer, not an
arbitrary-precision library. Go has `math/bits.Mul64`/`Add64`; Rust has `i128`;
Java has `Math.multiplyHigh`.

ALWAYS derive the bound explicitly before choosing the width, and write the
derivation into the code:

```
per-term max = maxAmount x maxRate
terms before overflow = typeMax / per-term max
```

If that count exceeds anything the domain can produce by several orders of
magnitude, a fixed-width integer is correct and an arbitrary-precision type is
just cost. If you cannot derive a bound, that is row 4 and you have earned your
BigDecimal.

## Round exactly once, at the edge

ALWAYS accumulate exact and round at the display, export, or wire boundary —
never in the middle, never twice.

Quantising per row loses value when amounts are small: at $100/unit a single
atomic unit is worth 0.1 micro-dollars, so ten 1-unit rows each floor to zero
and sum to zero, while one 10-unit row correctly yields 1 micro-dollar. Round
once at the end and the two paths agree.

Corollaries:
- NEVER cast to float "just before formatting" — write a formatter that does
  integer division and remainder. One `float64` cast one line early once turned
  an exact `$98,765,432,109,876.54` into `...56`.
- NEVER re-round an already-rounded value. It moves half-cents the wrong way.
- ALWAYS state the rounding mode. Half-away-from-zero and half-to-even give
  different money; pick one deliberately and test the negative side.
- Float IS legitimate for chart geometry and layout, where approximation is the
  point. Keep it downstream of the exact value, never upstream.

## Overflow must fail, not wrap

ALWAYS route accumulation through a checked add that returns an error. A
wrapped total is a silently wrong balance; a rejected one is a bug report. This
is what makes a fixed-width choice safe by construction rather than by argument
— you no longer have to prove the bound holds, you detect it if it does not.

## Test what actually breaks

- Values past 2^53, to catch a float sneaking into the decode path.
- The type's exact limit, one past it, and the negative mirror.
- A large positive and a large negative that cancel — must NOT trip overflow.
- Split/merge invariance: the same total accumulated in one chunk and in many
  must produce identical output. This is what pins round-once-at-the-end.
- Many tiny amounts that each round to zero individually.

MUTATION-CHECK the rounding invariant: make the code round per row instead of
at the end and confirm tests fail. A comment claiming "rounds once" that no
test enforces is decoration.

## Worked example

A Solana rewards service: amounts are `int64` lamports (row 1 — a lamport is
atomic, nothing to lose), prices are `int64` scaled 1e8 rejecting deeper input
(row 2), and the USD accumulator is their product at scale 1e17 (row 3). The
product needs 128 bits; profiling showed an arbitrary-precision accumulator
costing 27% of pipeline CPU and 94% of its allocations for precision the domain
could not use. The bound was derivable — a bucket's lamport sum cannot exceed
int64 because the checked add errors first — so a fixed-width 128-bit integer
with an overflow check was provably sufficient, with ~7e8x headroom.

The temptation to widen the *lamport* side too was wrong for the same reason
row 1 exists: an atomic count is already exact, and no width buys precision
that is not there to lose.
