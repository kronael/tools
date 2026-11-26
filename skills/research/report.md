# Report — the HTML page a run writes, and its charts

How a page reads and is crafted — one self-contained file, layout, dark mode,
phone width, prose — is `writing` → `page.md`. This file holds what a report
adds: its order, its build and its colours.

## Order

One page, fixed order, verdict first, About last: Verdict (winner, its
score, runner-up, baseline — the reader gets the answer without scrolling) →
Lineage (prior tag and its conclusion, a null included, and why this run
follows; written BEFORE the run) → what is modelled → what is predicted → how
it is fitted → run configuration → results table → caveats → About. About
ALWAYS states how to rerun the page: the branch named like the run tag and its
commit SHA, the exact command, the data and its window. A first run writes
"no prior" and NEVER drops the Lineage section. A run that leaves the prior
conclusion standing says so in its verdict — NEVER re-run a comparison
silently. Prose numbers follow `traps.md`.

A report component's page (a periodic or selection report) is the exception:
ALWAYS show only what the run computed, in this order: one sentence with the
rule and its numbers, the short table of what to act on, the full table, a
link to that full table as CSV, then one plain line for each measure the page
shows ("p99: 99 of 100 values are below it"), then the About line; one
chart at most. NEVER put lineage, history or repeated caveats on the page;
lineage stays in `summary.yml`. At phone width ALWAYS move columns to the
CSV before a table needs to scroll. A selection page ALWAYS keeps the current
members, the new passes and the rest apart, gives every row its numbers and
states the scan counts.

## Build

- ALWAYS make a report its own project: a package with the repo's standard
  component make targets, run as its CLI with `uv run`, or one PEP 723 script
  where `software` → `uvx-tools.md` and the repo allow it. NEVER another
  component's environment, NEVER a make target that runs it. Pyright: `py`
  § Build.
- ALWAYS generate a run's page in its own script, from the in-memory summary
  it writes to `summary.yml`, rebuildable from the run's saved outputs alone.
  NEVER hand-edit a generated page.
- ALWAYS keep a report's math — formulas, thresholds, verdicts — in one module
  of plain functions, apart from reading and page code.
- ALWAYS preprocess a report's input as one task per key (a symbol; a day is
  too small a task to take time) in a process pool. A task returns a small
  result through the pool and saves a large one under `<spool>/<run tag>/` in
  a standard format, pickle or numpy `.npy`/`.npz`, NEVER a custom one; the
  main process loads the results, joins them and computes on the join. The
  spool is disposable, NEVER a source of truth: a scheduled report ALWAYS
  deletes its `<spool>/<run tag>/` after a successful run and leaves it for
  debugging after a failed one, the tag keeping it apart from the next run; a
  one-off research run MAY keep it. A report takes one data dir and one spool
  dir, both located by the shared library's standard paths.
- ALWAYS inline every figure in its page. NEVER a figure as a loose file
  beside the page, except where the image itself is the product.
- ALWAYS write `index.html` at a report's tag root, one line per page the
  report holds (what it is, its window); a run with many items links one page
  per item from it. ALWAYS open every page with one muted text line of
  relative links: the report name to `index.html`, then the sibling pages,
  the current page as plain text. NEVER buttons, boxes, icons, sidebars or
  colour blocks for it.
- NEVER put a secret under the report root: a served root is readable by
  anyone who has its address.
- Where the host's web server serves the report root, a page is online once
  written; NEVER publish it a second way. Its address lives in the deployment
  config and the host's facts (`server-init`), NEVER in a repo.
- ALWAYS pick the figure library by what the reader does with the figure:
  - reads it (the default): matplotlib, as SVG with `svg.fonttype: 'none'`
    and `font.family` set to the page's font, which matplotlib otherwise
    writes into the SVG as its own.
  - hovers, zooms or filters it: plotly, `include_plotlyjs='cdn'`.
  - a page written by hand, with no run behind it: d3.

  plotly.js and d3 load as one pinned version from a CDN — on a report page
  the one exception to the no-CDN rule in `writing` → `page.md` § Layout.

## Figures inside a table

- ALWAYS draw a delta with its interval as a dot and bar on one axis per table:
  one zero line, tick labels in the header, the interval stated once in the lead
  line. Drop tick labels near an edge and thin crowded ones on a phone, keeping
  zero. A filled dot with bold numbers marks a run that meets the rule, a ring
  the others: the second cue beside colour.
- ALWAYS draw a measure against a threshold as a bar on a track with a tick at the
  threshold: full ink at or above it, 70% muted below it, 3:1 contrast for the
  fill against the track and the track against the page.
- ALWAYS give a column the reader compares down the table a bar or a tint scaled
  to that column alone, the number on top. A tint is ONE hue of a matplotlib
  colormap (`Blues`; `RdBu_r` by sign) mixed into each theme's page colour, so
  the text keeps its contrast — NEVER a whole colormap as cell fills. ALWAYS part
  tinted cells with an inset 1px page-colour shadow, NEVER a border.
- ALWAYS keep table cells compact (12–13px text, `padding: 3px 4px`) and give
  each table's columns widths in rules scoped to that table.
- ALWAYS put the answer (the verdict) in the second column, after the row label.
  A category of several kinds is one coloured letter with a one-line legend at
  its table — NEVER a sentence per cell or a paragraph before the table.
- ALWAYS state a page's heading as a counted result computed from the summaries
  ("3 of 17 runs beat their control, the best at t 1.3"), NEVER a question or a
  typed number. ALWAYS carry the evidence strength (t or spread) beside every
  winner a heading names.
- ALWAYS hold only current results under a report root: a retired run moves to the
  spool, and a round that reads an input another run rewrites pins its own copy and
  shows the hash.

## Binned plot

- ALWAYS plot y over many x as the mean (and chosen quantiles, when spread matters)
  of y per quantile or range bin of x, one line per pre-cut group, the bin rule
  and counts stated — NEVER a dense scatter.

## Page tokens

The page's colours, as CSS tokens on `:root`; the dark column applies under
`prefers-color-scheme: dark`.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#fcfcfb` | `#1a1a19` | page |
| `--ink` | `#0b0b0b` | `#f0efec` | text |
| `--ink2` | `#52514e` | `#c3c2b7` | secondary text, captions |
| `--grid` | `#e6e5e1` | `#34332f` | rules, table borders |

## Figure colours

- ALWAYS draw every figure on a white surface (figure and axes, plotly paper
  and plot) with `#0b0b0b` text in BOTH themes — NEVER a transparent figure
  that inherits the dark page: none of `tab10`, `tableau-colorblind10`,
  `Dark2` or `Set2` (matplotlib 3.11) clears 3:1 in full on both a light and
  a dark page.
- ALWAYS reference a palette by name, a name both matplotlib and plotly ship
  — NEVER copy hex values into code:
  - categories: `Dark2`, its first four colours only (each clears 3:1 on
    white); a fifth series goes into another panel.
  - ordered magnitude (heatmap, density): `cividis`.
  - signed values around a centre (difference, PnL, error): `RdBu_r` centred
    at 0.
- A second cue beside colour (`eval/design/rubric.md` #4) is required here:
  under deuteranopia two of the four `Dark2` colours merge, and so do two of
  `tab10`'s first four. One colour per meaning: `writing` → `page.md`
  § Diagrams.
