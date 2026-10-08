# Layout — how research is organised

The shape shared by every research tree, whatever the domain. A project
`CLAUDE.md` names its own directories and commands and points here.

## Names

A strategy directory is named for what it does — `funding_carry`,
`long_only` — never for a serial number and never for a date. A number says
nothing about the idea and collides with whatever else the run log numbers; a
date on the directory breaks the import and lies once the strategy is rerun.
The date belongs on the run's tag, which names the report
(`20260922_funding_carry`): a strategy is rerun, a report is one run.

## The seam

A model answers how much; a strategy answers whether and which way. The
import runs one way: a strategy MAY import a model's forecast classes and
NEVER its data reader, report writer or CLI; a model imports nothing from
strategies and never sees a position, an order or an equity curve. A score is
not the decision — the same split holds between evaluation and admission, and
between calibration and serving. A model is a state-bearing, replaceable unit
that is evaluated offline on its own; the strategy consumes it only once it is
warmed up.

## The run record

A run takes one config file and writes one record holding the setup AND the
metrics, so the record alone repeats the run. An unknown key in the config
raises — a typo'd knob otherwise runs with the default and reports under the
knob's name. NEVER write to a bare relative path and NEVER hardcode a tag: two
runs then overwrite each other. A tag directory that already exists is
refused, not reused; a dated record is immutable, and new state gets a new
tag however small the change. The one tag that IS re-run is the smoke target,
and it writes under scratch.

Beside the metrics the record carries what is needed to repeat and to doubt
it: the exact config (verbatim or hashed), the window actually covered beside
the one requested, universe, seed, cost assumptions, and the caveats copied in
at write time — a caveat joined live rewrites what every archived record was
said to mean.

## The run log

One log, one row per run, keyed by tag: window, universe, capital, the
required metrics (return, Sharpe, max drawdown, fills), a status word
(benchmark, refine, discard, keeper, archive) and a one-line note. A row
exists for every run, including iterations that never became a directory. A
tainted row is renamed, never deleted. A prose log beside it records, per
experiment: hypothesis, implementation, result, interpretation, verdict —
kept, dropped or refined — and what to try next.

Each experiment directory carries a leaflet: the idea in one line, the signal,
the evidence on the train window with its arithmetic, the result table with
the baseline on the same window, holdout status, how to run, caveats. Derive
it from the code's own docstring and the log row, never from memory, so
nothing in it is invented. An index README is one row per experiment plus a
section for what is NOT a research line — recoveries and archaeology, marked
"do not tune".

## The report page

One page, fixed order, verdict first, caveats last: Verdict (winner, its
score, runner-up, baseline — the reader gets the answer without scrolling) →
Lineage (prior tag and its conclusion, a null included, and why this run
follows; written BEFORE the run) → what is modelled → what is predicted → how
it is fitted → run configuration → results table → caveats. A first run writes
"no prior" and NEVER drops the Lineage section. A run that leaves the prior
conclusion standing says so in its verdict — NEVER re-run a comparison
silently. ALWAYS ship one artifact per experiment — one image or one file —
of two or three panels at most; chart mechanics belong to `dataviz`. Every
sentence derives from the summary frame or is scoped to what it measured; a
number is never hand-copied into prose.

## Durable and scratch

Durable evidence — summaries, filtered extracts, plots, the write-up — goes
under a report root outside the repo; bulky raw output (traces, logs) under a
spool; one-off drivers, caches and generated configs under the repo's
gitignored `tmp/` until they become runtime code. A repo-local `report/` is
moved out. A superseded report is deleted, not kept beside its replacement.

## Rounds

Iteration runs as numbered rounds: one question per round, its own script,
one row per round in the log, and a loop-state file that pins the locked
window and the stable knobs up front. A sweep table puts the baseline row
first and moves one column.

## The graveyard

A deleted model keeps its killing number as history, never as a baseline.
Before proposing one again, read the number that killed it AND check whether
the argument transfers to the current target — a null proved on one target is
a theorem about that target. Adding a model means deleting one and adding the
test that would have caught its predecessor's failure. Rejected config
patterns fail to parse rather than run silently; keep the outcome, not the
experiment code.

## Two simulators

A fast approximate simulator answers which family is worth researching; the
real-path replay answers what actually happens. NEVER validate a candidate on
the fast one alone, and NEVER present synthetic-price output as standalone
evidence — real data for any return or payout claim, with the command, config,
seed, window and output directory recorded.
