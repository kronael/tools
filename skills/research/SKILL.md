---
name: research
description: Router for quantitative-research discipline — experiment layout and records, believable backtest and forecast scores, the silent wrong-number traps. NOT for engineering (use software), bot code (use data) or charts (use dataviz).
when_to_use: "backtest, walk-forward, holdout, out-of-sample, overfitting, t-stat, Sharpe, proper scoring rule, Brier, QLIKE, baseline, benchmark, HODL, ex-market, round-trip cost, slippage, edge in bp, null result, ablation, results log, run tag, experiment directory, report verdict, lookahead, unit bug, mark-to-market PnL"
---

# Research — runbook router

Only this file preloads. ALWAYS read exactly ONE matched file below.
Paths are relative to this directory.

| If you need | Read |
|---|---|
| what a score must be reported against and when it may be believed: baselines on the same window, climatology as the floor, the scoring rule per target (Brier, QLIKE, RMSE), unforecastable targets, fit vs score target, holdout, overlap, beta, costs, controls, one knob, ablations, nulls, the scope of a number | `method.md` |
| how research is organised: strategy vs report naming, the model/strategy seam, the run record, the run log, the leaflet, the report page and its lineage, durable vs scratch, rounds, the graveyard, the two simulators | `layout.md` |
| silent plausible wrong numbers: reader row-eating, bar labels, unit powers, aliased checks, cache keys and effective windows, degenerate models, selectors, code defaults, constant curves, benchmark code, rounded winners, marked PnL, generated text, replay fixtures, stale records | `traps.md` |

NEVER duplicate these runbooks into project or language skills — link here instead.
