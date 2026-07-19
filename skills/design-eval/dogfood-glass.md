# design-eval: rsx-glass (desktop GPU renderer)  (mode: review)
Pixels seen: `rsx-glass/soft/testdata/heatmap.png`, `degraded.png` (read as images)
Palette source: `rsx-glass/grid.go` (Ayam Cemani subset) + `heat.go` (`glyphFg`, `rampColor`, `aggressor`)
Measured: WCAG 2.1 ratio + APCA-W3 0.1.9 Lc over every ink×bg pair (script: scratchpad `measure.py`, 2026-07-19)

Reserve scope: raw-GL pixels-only surface — no accessibility tree, focus order,
screen-reader text, or IME exists or can exist here. Contrast + redundant
channel is the CEILING of any a11y claim below; nothing is "covered".

## Scores (1–5)

hierarchy 4 · colour+tokens 4 · contrast 2 · redundant-channel 2 ·
typography/numerics 3 · spacing/density 4 · layout/responsive 3 ·
consistency 3 · data-density/minimalism 3 · feedback/honesty 4

## Prior-critique reconciliation (go-gl codex/fable audits, checked against pixels)

- **fg==bg wall glyph (fable #26): FIXED.** `glyphFg` picks the higher-contrast
  reserved ink (TextBright or Page); `TestGlyphContrast` gates the tier matrix.
  Confirmed in `heatmap.png`: density texture and `▚` are visible on bright
  cells (dark ink) and dark cells (bright ink). Worst pair now 3.97:1 (Page on
  ramp2); rest ≥ 4.3:1.
- **Hue-only trade side (fable #27): OPEN.** Confirmed in pixels: the print
  column shows the same `○◆●■` shapes in green vs salmon only.
- **Per-frame autoscale strobe (fable #28): OPEN**, documented in SPEC.md
  "Known v1 deviations". A single-frame golden cannot show it; `bases()`
  confirms per-frame max.
- **Raw numerics: OPEN.** Footer prints raw i64 (`10008x232905`) — honest,
  documented v1 (`fmtPx`).
- **No freshness aging (fable #35): OPEN**, documented in SPEC.md.
- Codex engineering items (resizable, always-pump, drain-then-send coalescer,
  parity gate at measured maxDiff≤1): all FIXED in code (`gpu.go:275`,
  `glass.go:29`, `cmd/glass/main.go:148`, `parity_test.go`).

## Findings (most-damaging first)

1. **[system] Trade SIDE is hue-only** — buy vs sell aggressor is green
   `Live` vs red `Ask` on the *same* `○◆●■` shapes (`heat.go aggressor` +
   `tradeRamp`). Under deuteranopia the most important event on the screen
   (a print) loses its direction; WCAG 1.4.1. Fix: side-by-shape in the
   upstream language (rsx-term VISUALS.md) — mirrored triangle ramps
   `▵▴△▲` (buy, up = lifts) / `▿▾▽▼` (sell, down = hits) — then mirror
   in `heat.go` + `atlas/`. (evidence: heatmap.png print column; both hue
   pairs measured identical-shape)
2. **[system] Trade ink collapses on bright ramp tiers** — a buy print ON a
   wall is invisible: Live on ramp4 = **1.00:1 / Lc 0** (fg==bg), Live on
   ramp3 = 1.77:1 / Lc −29.7; Ask on ramp3 = **1.09:1 / Lc 0**; colorblind
   pair same class (CbBid on ramp3 = 1.14:1). `TestGlyphContrast` covers only
   `glyphFg` inks, not the aggressor inks. Fix: cap the trade-overlay
   background at ramp tier 1 (worst pair becomes Ask/ramp1 = 4.10:1,
   Lc −40.8; all pairs ≥3:1 and ≥Lc 30 in both themes) + extend the test to
   the aggressor-ink×overlay-bg matrix.
3. **[system] Per-frame autoscale strobe** — `bases()` normalizes to the
   current frame's max; one large order re-brightens/dims every cell.
   Deferred with cause: the fix is cross-frame reference state (rsx-term's
   `stableBases` rise-fast/decay-slow) plumbed through the seam — a model
   change, not a styling one. Already documented in SPEC.md; keep it there.
4. **[screen] No colorblind theme in glass** — `grep UseTheme rsx-glass/` is
   empty, yet `rsx-glass/CLAUDE.md` claims "`UseTheme` rebinds tier 2
   (bid/ask) only". The upstream language has the seam (`RSX_TUI_THEME`);
   glass never wired it. Fix: add the same two-var rebind to `grid.go` +
   read the env in `cmd/glass`.
5. **[system] Muted ink is APCA-sub-floor** — `#586b62` on Page = WCAG
   3.54:1 (passes 1.4.3 large/1.4.11) but **Lc −23.3**, under the Lc 30
   any-text floor; carries gutter time labels, `~mark`, ladder labels.
   WCAG-vs-APCA divergence on a near-black base — exactly the case the
   ratio lies about. Debt, not a local fix: the hex is verbatim-shared with
   the dashboard, spec 55, and rsx-tui; a bump must be a coordinated
   palette rev.
6. **[screen] Raw i64 footer numerics** — `10006x9741`, no tick/lot scale,
   variable width. Honest and documented ("viewer has no per-symbol
   config") but stays a rubric-5 finding until a live adapter supplies
   scaling. Debt, documented.
7. **[screen] Mid-session staleness** — feed death keeps painting last-known
   data at full colour; only the header dot flips. Documented in SPEC.md
   (needs clock plumbing through `Scene`); v2.
8. **[screen] HiDPI atlas + cell-grid ceiling** — 14 pt/1× nearest-scaled
   atlas, 72×24 information resolution at any window size. Documented in
   SPEC.md as deliberate v1; keep documented.

## Keep (already strong — do not regress)

- Hierarchy: the liquidity field dominates, chrome is one thin header +
  two footer lines, no boxes/borders anywhere (pure Tufte data-ink).
- Token discipline: three named tiers, render reads semantic only,
  reserved-ink rule now gated by test.
- Honesty: `—`/`~` asserted by `TestHonestyMarkers`; degraded.png is an
  honest empty state, not fabricated data.
- Spacing/density: single cell-grid module, one density, stable regions.

## Sharpen (the ranked fix list)

1. Side-by-shape trade ramps (upstream fix mirrored here: `heat.go`,
   `atlas/` triangle primitives, re-bless `heatmap.png` with cause).
2. Overlay-bg cap + aggressor-ink contrast gate in `TestGlyphContrast`.
3. Wire `UseTheme` (or fix CLAUDE.md to stop claiming it).
4. Leave 3/5/6/7/8 as documented debt (SPEC.md already carries most).

## Verdict

The language glass renders is sound where it was fixed (reserved inks,
honesty, hierarchy) and still broken where it inherited hue-only side and
uncapped overlay backgrounds — both are upstream (rsx-term) defects that
must be fixed there and mirrored, not forked. This screen applies the
language faithfully; its own gaps (theme seam, autoscale, raw numerics)
are honest, documented v1 scope — except the missing `UseTheme`, which the
docs claim exists.

---
Outcome (2026-07-19, post-eval): findings 1–2 + 4 FIXED in rsx repo commit
cfecd8c [glass] (mirrored triangle ramps + atlas primitives, overlay cap,
UseTheme wired, TestGlyphContrast both themes + aggressor inks); 3/5/6/7/8
remain documented debt in SPEC.md "Known v1 deviations" (Muted APCA bullet
added). heatmap.png re-blessed with visual confirmation; parity maxDiff=1.
