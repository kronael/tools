---
name: research
description: Router for quantitative-research discipline — how experiments are organised and recorded, what makes a backtest or forecast score believable, and the traps that produce plausible wrong numbers silently. NOT for engineering (use software), exchange and bot code (use trader), or chart craft (use dataviz).
when_to_use: "backtest, walk-forward, holdout, out-of-sample, train window, overfitting, t-stat, overlapping samples, Sharpe, QLIKE, baseline, benchmark, HODL, beta, ex-market, round-trip cost, fees, slippage, edge in bp, null result, ablation, random gate, sweep, one knob, results log, run tag, experiment directory, report verdict, lineage, caveats, scratch vs report root, lookahead, right-labelled bars, header row eaten, unit bug, selector that never declines, rounded winner, mark-to-market PnL, code defaults as model"
---

# Research — runbook router

Only this file preloads. ALWAYS read exactly ONE matched file below.
Paths are relative to this directory.

| If you need | Read |
|---|---|
| what a score must be reported against and when it may be believed: baselines on the same window, holdout, overlap, beta, costs, controls, one knob, nulls, the scope of a number | `method.md` |
| how research is organised: strategy vs report naming, the model/strategy seam, the run record, the run log, the leaflet, the report page, durable vs scratch, rounds, the graveyard | `layout.md` |
| silent plausible wrong numbers: reader row-eating, bar labels, unit powers, aliased checks, degenerate models, selectors, code defaults, benchmark code, rounded winners, marked PnL, generated text, replay fixtures, stale records | `traps.md` |

NEVER duplicate these runbooks into project or language skills — link here instead.
