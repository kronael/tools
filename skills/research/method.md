# Method — what a number must carry to be believed

The evidence discipline every backtest, forecast score and signal study is
held to, whatever the repo. A project `CLAUDE.md` carries that repo's own
traps, seams and commands and points here; nothing here names a repo.

## Baselines

NEVER report a score without its baseline, on the same window, from the same
code path. The baseline is the strongest thing a practitioner would run
instead — buy-and-hold for a strategy; persistence, climatology and an EWMA
for a forecast — scored on the same dates, the same universe, the same costs,
by the same bucketing. A number on its own is not a result; the gap to the
baseline is. When the target changes, every earlier bar is void: say so at
the top of the project file and re-baseline before scoring anything new.

ALWAYS quote an edge net of the round trip, gross beside it. 14bp per side
(taker plus slippage) is a 28bp round trip, so an 8bp-per-trade edge is a
loss whatever its t-statistic, and a strategy turning over 500 round trips a
year pays 140% of notional. Name what the cost model leaves out — funding,
impact — as a caveat, never silently.

ALWAYS strip beta before believing a cross-sectional edge. In a drifting
market every bucket comes out positive; subtract each bar's cross-sectional
mean return and score what is left. An edge that does not survive ex-market
was the market.

## Holdout

A holdout is consumed once, by a future session. ALWAYS lock the window
before tuning and refuse it in code behind an explicit flag, and NEVER look at
numbers outside the locked test window while choosing knobs — seeing them is
enough to contaminate the choice. NEVER spend it on a "decisive test"; when a
critic or a brief proposes that, refuse the brief. When it is spent anyway,
rename every row that touched it TAINTED in the run log, re-derive the verdict
from the untainted rows, and NEVER cite the tainted ones; the rows stay,
because deleting them hides how the holdout was lost.

## Samples

Overlapping samples inflate t-statistics. An hourly sample scored against a
72h horizon counts each outcome about 72 times; the same rule sampled one
position per name at a time went from t=5.2 to t=2.6. ALWAYS report the
non-overlapping number and NEVER let the overlapping one be the headline — it
is the figure that gets retracted. Step a walk-forward by the full horizon,
and skip a window that straddles a data gap rather than reading the gap as one
return.

A smoke run is plumbing, not a result: a 10-day margin shrank six-fold over
the full window, and a single-seed run's small win is noise. ALWAYS sample at
the cadence the claim needs and state n beside every score.

## Controls

NEVER celebrate a gate or a signal before its null. A random mask matched to
the active fraction scored most of a "smart" gate's Sharpe, so the model's
real contribution was the difference; the same values time-shuffled must lose
what the real timing gains. ALWAYS run the symmetric split (fit on each half,
score on the other) and the prior regime — a model at +12% on the year it was
tuned on and -24% on the year before is a regime fit. When a covariate model
loses, sweep its FIXED loading before rebuilding the selector: one run
separates "picks badly" from "no loading helps".

ALWAYS reconcile two independent computations before trusting either — the
backtest's round-trip count against the study's trade count, the strategy
against its observe-only sibling. Agreement is the cheapest evidence there is.
A surprise is first a question about the instrument: confirm it on a
known-good baseline before believing the system moved.

## Runs

Change ONE knob between runs, from a pinned baseline row. A run that moves
two settings attributes its delta to neither; separate hypotheses are
separate experiments, never one model with three terms. Identical rows across
a swept knob are a finding: the knob is inert.

ALWAYS state the scope of every number — window, universe, cost, n, and
whether it is in-sample for the knob choice that produced it — and mark an
estimate as an estimate. A validation table is parity evidence, not a
deployment claim, until the holdout says otherwise.

Report a null plainly, where the verdict goes: "X did not earn its place on
this target" is a finding, and so is its reversal on the next target. When a
number is retracted, ALWAYS correct it everywhere it reached — log, diary,
project file, memory — in the same pass; a retraction that misses one copy is
not a retraction.
