---
name: research-analysis
description: How to run and report a quantitative experiment honestly — baselines, proper scoring rules, holdout discipline, lineage between runs. Methodology, not chart code. NOT for ETL/scraping (use data), NOT for report/chart scripts (use data-reports), NOT for chart visual design (use dataviz).
when_to_use: "backtest, baseline comparison, is this beating a baseline, climatology, proper scoring rule, Brier score, QLIKE, MSE-log, holdout discipline, walk-forward, look-ahead bias, null result, negative result, experiment lineage, model comparison, ablation, overfitting a metric, p-hacking a backtest"
---

# Research Analysis

The question this skill answers: **is this result true, and did we report it
honestly?** Not "does the chart look good" (dataviz), not "how do I write the
report script" (data-reports), not "how do I get the data" (data). This is
the methodology gate those skills sit downstream of.

## Experiment lineage

- Every run has a tag and references the PRIOR run's tag and conclusion —
  including when the prior conclusion was a null result. "First run of this
  line" is itself a lineage statement ("Baseline experiment — no prior"),
  not an excuse to omit the section.
- Lineage goes at the TOP of the writeup, not the bottom. A reader should
  know why this run exists before they see a single number.
- If a run doesn't change the conclusion, say so explicitly instead of
  silently re-running the same comparison.

## Baselines are mandatory — and picking the right one is the skill

- Climatology (the unconditional mean/rate) is the FLOOR, not the bar.
  Reporting "we beat climatology" when climatology is a strawman proves
  nothing.
- The real bar is the strongest baseline a practitioner would actually run:
  EWMA, persistence (last-period value), seasonal-naive, a simple linear
  model. Beating a weak baseline is not evidence; beating the strong one is.
- Report every serious baseline alongside the model, in the same table, not
  in a footnote. If the model doesn't beat the strong baseline, that's the
  headline finding, not a caveat.

## Proper scoring rules, matched to the target

- **Probabilities** → Brier score (or log loss). Always alongside the
  climatology baseline (`p(1-p)` for a binary outcome) so the reader can see
  the edge, not just the raw score.
- **Variance / volatility** → QLIKE or MSE on log-variance (Patton 2011) —
  the only common loss functions whose model ranking is provably robust to a
  noisy realized-variance proxy. A loss that isn't robust to proxy noise can
  flip the ranking of two models even when neither is wrong.
- **Conditional mean** → RMSE, not MAE. MAE is minimized by the conditional
  MEDIAN — using it to rank forecasts of a mean is a category error, not a
  stylistic choice.
- Whatever the target, name the loss and justify why it matches the
  estimand. "We used RMSE" without saying why is not a methodology.

## Forecastable vs. structurally unforecastable

- Before scoring anything, ask: can this quantity be predicted at all, by
  construction? A martingale's direction, for instance, cannot be — no
  amount of modeling produces a real edge, and a near-zero score there is
  not a weak result, it's the null hypothesis holding.
- When a target is structurally unforecastable, say so and refuse to score
  it as if it were a live comparison. Report it as a derived/illustrative
  quantity if it's still useful downstream, but label it "not scored" and
  keep it out of the winner table.
- This is a stronger claim than "the model didn't do well here" — it's "no
  model could do well here," and the writeup should make the distinction
  explicit so a reader doesn't waste time trying to beat it.

## Fit/score separation

- Fit parameters on the raw generative process. Score on the decision or
  observable target the user actually cares about — these are not always
  the same quantity (e.g. fit a variance process, score the resulting
  barrier-touch probabilities).
- Nuisance parameters fixed at scoring time (barrier width, horizon, decision
  threshold) must NEVER leak into the fitting objective. If sweeping one of
  them changes what the fit converges to, the separation has failed.

## Null and negative results are first-class

- "X did not earn its place on this target" is a finding — write it into the
  results section with the same weight as a positive result, not into a
  caveats afterthought.
- Two experiments on related targets can legitimately disagree (a feature
  helps target A, hurts target B). Report both; do not silently pick the
  more flattering one to lead with.
- A negative ablation result is evidence the simpler model is correct — say
  that plainly instead of hedging it into ambiguity.

## Holdout discipline

- A holdout is a boundary (date, id range, fold) fixed BEFORE any tuning
  touches it, used for scoring exactly once.
- Contamination begins at VIEWING, not at fitting. Printing a metric on
  holdout data during iteration burns it even if no parameter is touched
  afterward — the human doing the next round of tuning is now conditioning
  on it whether or not they intend to.
- Enforce the boundary programmatically (a hard-coded date/id constant plus
  a code path that refuses to score past it without an explicit override
  flag), not just as a promise to self. A guard that can be silently skipped
  is not a guard.
- Once consumed, the holdout is gone. The fix for "we need one more check" is
  a new holdout on fresh data, never a second look at the old one.

## Report shape

- Table first — it's the headline, not an appendix. Minimal panels (2-3),
  one artifact (one image, one file) per experiment. See `data-reports` /
  `dataviz` for the actual chart mechanics once the content is decided.
- Every reported number needs its baseline sitting next to it in the same
  table. A score without a baseline is not interpretable.
- Caveats section goes LAST, not first — state the finding, then the honest
  limits on believing it.
