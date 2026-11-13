# Report — the HTML page a run writes, and its charts

How a page reads and is crafted — one self-contained file, layout, dark mode,
phone width, prose — is `writing` → `page.md`. This file holds what a report
adds: its order, its build and its colours.

## Order

One page, fixed order, verdict first, caveats last: Verdict (winner, its
score, runner-up, baseline — the reader gets the answer without scrolling) →
Lineage (prior tag and its conclusion, a null included, and why this run
follows; written BEFORE the run) → what is modelled → what is predicted → how
it is fitted → run configuration → results table → caveats. A first run writes
"no prior" and NEVER drops the Lineage section. A run that leaves the prior
conclusion standing says so in its verdict — NEVER re-run a comparison
silently. Prose numbers follow `traps.md`.

A report component's page (a periodic or selection report) is the exception:
ALWAYS show only what the run computed — one sentence of what was measured,
one chart, one table, then one plain line at the bottom for each measure the
page shows ("p99: 99 of 100 values are below it"). NEVER put lineage, history
or repeated caveats on the page; lineage stays in `summary.yml`. At phone width
ALWAYS move columns to `summary.yml` before the table needs to scroll.

## Build

- ALWAYS make a report its own project — NEVER put its packages into another
  component's `pyproject.toml` or run it on another component's environment.
  It is a package or one PEP 723 script as `software` → `uvx-tools.md`
  decides, where the repo allows a script. A package has its own
  `pyproject.toml` and the repo's standard component make targets (setup, type
  checks, tests), runs as its CLI with `uv run`, and NEVER has a make target
  that runs it. Its pyright level is `py` § Build's.
- ALWAYS generate a run's page in its own script, from the in-memory summary
  it writes to `summary.yml`. NEVER hand-edit a generated page.
- ALWAYS inline every figure in its page; a run with many items links one
  index page to one page per item. NEVER a figure as a loose file beside the
  page, except where the image itself is the product.
- NEVER put a secret under the report root: a served root is readable by
  anyone who has its address.
- Where the host's web server serves the report root (the host's facts,
  `server-init`), a page is online once written. NEVER publish it a second
  way. Its public address lives in the web server's deployment config and the
  host's facts (`server-init`); NEVER repeat it in a repo's docs, code or commits.
- ALWAYS pick the figure library by what the reader does with the figure:
  - reads it (the default): matplotlib, as SVG with `svg.fonttype: 'none'`
    and `font.family` set to the page's font, which matplotlib otherwise
    writes into the SVG as its own.
  - hovers, zooms or filters it: plotly, `include_plotlyjs='cdn'`.
  - a page written by hand, with no run behind it: d3.

  plotly.js and d3 load as one pinned version from a CDN — on a report page
  the one exception to the no-CDN rule in `writing` → `page.md` § Layout.

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
