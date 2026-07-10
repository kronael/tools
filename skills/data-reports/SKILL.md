---
name: data-reports
description: "Data visualization report scripts. NOT for general ETL or scraping (use data)."
when_to_use: "Vega-Lite charts, report generator, chart script, multi-panel PNG, structured data visualization, Bun report script, data presentation script"
---

# Data Report Scripts

Reference example: `scripts/report-chart.ts` (validator-bonds).

## Stack

- `bun` runtime, `vega-lite` (spec), `vega` (render), `sharp` (SVG→PNG), `yaml` (input).
- Render chain: `compile(spec).spec` → `vega.parse` → `new vega.View(parsed, {renderer:'none'})` → `await view.toSVG()` → `sharp(Buffer.from(svg)).png().toFile(out)`.
- ALWAYS shell out with `Bun.spawn` + `await proc.exited` — NEVER `Bun.spawnSync`.
- Args positional: `[report.yml] [out.png]` with defaults (out = report with `.png`). `-h`/`--help` writes usage to stderr, then `process.exit(2)`.

## Script Structure

- `load()` — read YAML, map to typed row objects, derive computed fields there (e.g. `actualFeeBps = feeAdj * maxFeeBps / feeMax`). NEVER compute in the spec.
- `loadConfigTarget()` — read sibling config (e.g. `settlement-config.yaml`) for reference lines; return `null` if missing so the chart still renders without the target line.
- `async function main()` — all chart math, spec construction, render.
- Series names and colors are string constants at the top of the file.

## Title

- `title.text` = what + range (e.g. `'… Simulation · Epochs 885–985'`).
- `title.subtitle` = the run SETUP so the chart is self-describing: input tag + key config bounds (e.g. `'r200-x1600 · min fee 200 bps · max fee 1600 bps'`). Derive the tag from the input filename basename (`<tag>.yml` → `<tag>`; suppress the bare default `report`). Style with `subtitleFontSize: 11`, `subtitleColor: '#666'`.

## Chart Structure

Panels stacked in `vconcat`; `hconcat` for side-by-side pairs.

1. Main time-series panel (full width, e.g. 960) — layered: gap bands, area bands (delta green/red), reference lines, main line with points, value labels, delta labels.
2. Legend-only row (`height: 20`, invisible mark, `legend.orient: 'top'`) — separates legend from the panel above.
3. Bar chart (full width) — grouped bars per period, target reference line.
4. `hconcat` of two half-width panels (e.g. 460 each).
5. Footer (`height: 1`, `type:'text'` mark) — config params + source file.

## Conventions

- Units ALWAYS in `[brackets]` in axis and panel titles: `'Fee Payable [SOL]'`, `'fee [%]'`, `'APY [%]'`. ALWAYS name the quantity before the unit — `'[SOL]'` alone is not enough; write `'Fee Payable [SOL]'` or `'Stake [SOL]'`.
- Y-axis domains ALWAYS derived from data, NEVER hardcoded: bps → `Math.ceil(max * 1.1 / 100) * 100`; SOL → `Math.ceil(max * 1.1 / 10) * 10`.
- Tidy data for every multi-series chart: one row per observation+series.
- Ordinal x-axis with FULL domain: `range(lo, hi)` → `scale: { domain: epochDomain }`, so missing slots stay visible instead of collapsing.
- Period aggregation auto-derived from timestamps: monthly when span > 60 days, weekly otherwise. NEVER hardcode the period.
- Label stride for dense axes: extract a `mkLabel(s)` helper → `s > 1 ? \`...% ${s} === 0...\` : 'datum.label'`. Full-width panel (960px): `mkLabel(Math.ceil(n/40))`. Half-width panels (460px): double the stride → `xEncSmall = { ...xEnc, axis: { ...xEnc.axis, labelExpr: mkLabel(stride*2) } }`.
- Legend `offset`: all lower panels `4` (tight); dedicated legend row (owns its row) uses `0`.
- Series names in legends ALWAYS all-lowercase: `'adjusted'`, `'at max fee'`, `'at min fee'`, `'max-fee cap'`. Acronyms only: keep uppercase (e.g. `'SSR baseline'`).
- `resolve: { scale: { color: 'independent' } }` on the top level AND on any `hconcat` panel with its own color encoding.
- Incomplete boundary periods (first AND last) → hollow bars. Detect by epoch count, NOT `Date.now()` (which mislabels historical reports): a boundary period holding fewer epochs than its neighbour is partial → `cnt(0) < cnt(1)` and `cnt(last) < cnt(last-1)`. Factor `fillOpacity`/`strokeWidth`/`strokeDash` conditionals into a `hollowBar` object, spread into the bar layer's `encoding`. Incomplete = `fillOpacity:0`, `strokeWidth:1.5`, `strokeDash:[4,2]`.
- The vega-lite WARN about conflicting legend properties is expected and harmless — NEVER suppress it.

## Reference Line Labels

- `rule` mark at `{ datum: target }` for the line itself.
- Label is a separate `text` mark pinned to an edge, NEVER centered: left edge → `x: { value: 0 }`, `align: 'left'`, `dx: 4`; right edge → `x: { value: width }`, `align: 'right'`.

## Gap Handling

- For missing x positions, draw an amber `rule` mark plus a rotated `text` label.
- Insert explicit null rows so the main line breaks across the gap instead of interpolating over it.

## Color Palette

Define as top-of-file constants:

- `C_ACTUAL = '#4682b4'` (blue — actual/observed)
- `C_REF = '#708090'` (gray — reference line)
- `C_CAP = '#2e8b57'` (green — cap/ceiling)
- `C_MINFEE = '#9370db'` (purple — floor/min)
- `C_COST = '#b22222'` (red — cost/risk/shortfall)

## What NOT to do

- NEVER hardcode y-axis domain limits — ALWAYS derive from data.
- NEVER use `(unit)` in labels — ALWAYS `[unit]` (so `[SOL]`, not `(SOL)`). NEVER use bare `[unit]` as an axis title — always prepend the quantity name.
- NEVER center a reference-line label — ALWAYS pin to an edge with `align` + `x: { value }`.
- NEVER `Bun.spawnSync` — ALWAYS `Bun.spawn` + `await .exited`.
- NEVER compute derived fields inside the Vega-Lite spec — ALWAYS in `load()`.
