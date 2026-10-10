---
name: research
description: Router for quantitative-research discipline — experiment layout and records, believable backtest and forecast scores, the silent wrong-number traps. NOT for engineering (use software), bot code (use data) or chart craft (use dataviz).
when_to_use: "backtest, walk-forward, holdout, out-of-sample, train window, overfitting, t-stat, overlapping samples, Sharpe, proper scoring rule, Brier, QLIKE, unforecastable target, baseline, climatology, benchmark, HODL, beta, ex-market, round-trip cost, fees, slippage, edge in bp, null result, ablation, random gate, one knob, results log, run tag, experiment directory, report verdict, lineage, caveats, scratch vs report root, lookahead, right-labelled bars, header row eaten, unit bug, selector that never declines, rounded winner, mark-to-market PnL, code defaults as model"
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
