# Method — what a number must carry to be believed

The evidence discipline every backtest, forecast score and signal study is
held to, whatever the repo. A project `CLAUDE.md` carries that repo's own
traps, seams and commands and points here; nothing here names a repo.

## Baselines

NEVER report a score without its baseline, on the same window, from the same
code path, in the same table — never in a footnote. The baseline is the
strongest thing a practitioner would run instead — buy-and-hold for a
strategy; persistence, seasonal-naive, an EWMA and a simple linear model for a
forecast — scored on the same dates, the same universe, the same costs, by the
same bucketing. Climatology, the unconditional mean or rate, is the floor and
NEVER the bar: beating only it proves nothing. A number on its own is not a
result; the gap to the baseline is, and a model that loses to the strongest
baseline has that loss as its verdict, never as a caveat. When the target
changes, every earlier bar is void: say so at the top of the project file and
re-baseline before scoring anything new.

ALWAYS quote an edge net of the round trip, gross beside it. 14bp per side
(taker plus slippage) is a 28bp round trip, so an 8bp-per-trade edge is a
loss whatever its t-statistic, and a strategy turning over 500 round trips a
year pays 140% of notional. Name what the cost model leaves out — funding,
impact — as a caveat, never silently.

ALWAYS strip beta before believing a cross-sectional edge. In a drifting
market every bucket comes out positive; subtract each bar's cross-sectional
mean return and score what is left. An edge that does not survive ex-market
was the market.

## Scoring rules

ALWAYS score with a loss whose minimiser is the quantity being forecast — a
proper scoring rule for a probability, a consistent loss for a mean or a
variance — and name the loss and why it fits the estimand; "we used RMSE"
with no reason is not a method.

- Probabilities: Brier score or log loss, with climatology's score beside it —
  `p(1-p)` for a binary outcome at base rate `p` — so the edge reads directly.
- Variance and volatility: QLIKE, or MSE on the variance itself. Against a
  noisy but conditionally unbiased proxy such as realized variance, these two
  rank forecasts as the true variance would (Patton 2011). MSE on log variance
  or on volatility, and every MAE form, rank partly by the proxy's noise and
  can flip two models when neither is wrong — NEVER rank variance forecasts
  with them.
- Conditional mean: RMSE, NEVER MAE. MAE is minimised by the conditional
  median, so ranking mean forecasts with it is a category error.

ALWAYS ask whether a target is forecastable by construction before scoring it.
A martingale's expected next change is zero given its past, so a near-zero
score there is the null holding, not a weak model. Label such a target "not
scored", keep it out of the winner table, and state that no model can win it,
not merely that this one did not — otherwise the next round tries to beat it.

Fit on the generative process; score on the observable the decision uses —
fit a variance process, score the barrier-touch probabilities it implies. A
nuisance parameter fixed at scoring time — barrier width, horizon, decision
threshold — NEVER enters the fitting objective. If sweeping one moves what the
fit converges to, the separation has failed.

## Holdout

A holdout is consumed once, by a future session. ALWAYS lock the window
before tuning and refuse it in code behind an explicit flag, and NEVER look at
numbers outside the locked test window while choosing knobs — seeing them is
enough to contaminate the choice. NEVER spend it on a "decisive test"; when a
critic or a brief proposes that, refuse the brief. A spent holdout is gone:
one more check needs a new holdout on data the tuning never saw, NEVER a
second look at the old one. When it is spent anyway, rename every row that
touched it TAINTED in the run log, re-derive the verdict from the untainted
rows, and NEVER cite the tainted ones; the rows stay, because deleting them
hides how the holdout was lost.

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
a swept knob are a finding: the knob is inert. An ablation that removes a term
and loses nothing is evidence the simpler model is right — ALWAYS report it
as that, plainly, NEVER hedged into ambiguity.

ALWAYS state the scope of every number — window, universe, cost, n, and
whether it is in-sample for the knob choice that produced it — and mark an
estimate as an estimate. A validation table is parity evidence, not a
deployment claim, until the holdout says otherwise.

Report a null plainly, where the verdict goes: "X did not earn its place on
this target" is a finding, and so is its reversal on the next target — report
both, and NEVER lead with the more flattering one. When a number is
retracted, ALWAYS correct it everywhere it reached — log, diary, project
file, memory — in the same pass; a retraction that misses one copy is not a
retraction.
