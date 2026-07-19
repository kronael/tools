# Design-systems research for `go-gl` data-dense desktop apps

The design half of a `go-gl` skill. Not a citation tour: every rule below is an
operational decision a GL renderer or its token table makes, grounded in a named
system, and tied to concrete bugs the RSX reference already shipped
(`fable-critique.md` findings 26–28, 35). Read against the artifacts it extends:
`rsx-glass/grid.go` (resolved 8-colour palette), `rsx-term/VISUALS.md` (encoding
laws), `rsx-playground/CLAUDE.md` (colour = meaning). Web CSS and the go-gl
threading/cgo engineering are out of scope.

## 1. The encoding law comes first: channel hierarchy (Cleveland & McGill)

Every "which colour / glyph / bar" decision is downstream of one 1984 result
(Cleveland & McGill, *Graphical Perception*): humans decode quantitative values
most accurately by **position, then length, then angle/area, then luminance,
then hue**. This is the single piece of citable design *science* that decides
encodings, and it is what generic HIGs (Rams, Nielsen, Refactoring UI) never
give you. It dictates the build:

- **Exact values → text** (position on a page is perfect); magnitudes the eye
  compares → **length/position** (the rsx-term NOW-row micro-bars do this
  right); **luminance → overview texture only**; **hue → category only, never
  magnitude, and never a category's *sole* carrier.** rsx-glass violates the
  last clause twice (finding 27): the size ramp asks *hue+luminance* to carry a
  magnitude the eye can't rank, and trade **side** rides on hue alone.

Rule this yields: **primitive follows data topology.** A cell grid is correct
for text/status planes; a continuous price×time field wants per-datum instances
or a data texture so magnitude reads as position/length, not ~3 visible
luminance steps (findings 28–29).

## 2. Design tokens: the three-tier model (Salesforce/Jina Anne → W3C DTCG)

The term "design token" and the tiered structure come from Salesforce Lightning
(Jina Anne + Jon Levine, ~2014) and are now standardised by the **W3C Design
Tokens Community Group** (Format Module 2025.10: `$value`/`$type`, `{alias}`
references). Fluent 2 ships the same idea as **global** vs **alias** tokens
(fluent2.microsoft.design/design-tokens). The three tiers:

1. **Primitive / global** — raw values: the ramp stops, `space.4 = 4px`,
   `green.500 = #22f5a1`. Change rarely.
2. **Semantic / alias** — intent: `color.live`, `color.bg.page`, `space.gutter`.
   Carries the brand; this is where a theme swap happens.
3. **Component** — context: `cell.bg`, `ladder.padding`, `heading.fg`.

Why this changes the build: **the shader and Grid builder consume tiers 2–3
only; a raw hex never appears in render code.** `grid.go` already half-does this
— "Colours are RESOLVED here … so a Renderer is a dumb rasteriser." Name the
tiers and that resolve-at-build step *becomes* the semantic layer. **Dark /
colourblind mode = rebinding tier 2, nothing else** — precisely what
`UseTheme("colorblind")` does by swapping only the bid/ask bindings
(`VISUALS.md`). Raw hex scattered through shader code is the anti-pattern the
whole methodology exists to kill.

## 3. Colour roles and reserved contrast pairs (Material 3)

Material 3's key move (m3.material.io/styles/color/roles) is **role pairs**:
every container colour ships with a guaranteed-legible `on-` companion
(`primary`/`on-primary`, `surface`/`on-surface`). You never pick a text colour
that "looks fine on" a background — the pair is defined and contrast-tested
together. This is the direct fix for **finding 26**: `bookCell` derives glyph fg
as `rampColor(tier+1)`, so on a wall `fg == bg` (1.00:1) and the glyph renders
in its own background. Replace it with a reserved `on-ramp` ink role, one high-
contrast colour tested against *every* tier it can sit on.

Two more M3 mechanisms map onto a GL build:

- **Tonal palette (13 tones, 0–100).** M3 builds a ramp as perceptually-even
  *tones*, not a linear sRGB lerp. `grid.go`'s `blend()` is a straight sRGB
  interpolation, which is why the heatmap collapses to a "flat green blob"
  (finding 28 context): equal `t` steps are *not* equal perceived steps near
  black. Define ramp stops as a tonal palette spaced by perceptual lightness
  (APCA Lc, §4), so each tier is a visibly distinct step.
- **State layers.** Interaction states (hover/focus/pressed/selected) are a
  single semi-transparent overlay at a **fixed opacity token** over the content
  colour — M3 opacities hover 8%, focus/pressed ~10–12%, dragged 16%. For GL:
  one alpha-blended quad, opacity from a state token — never author N "hover
  colour" hexes.

## 4. Contrast done right: WCAG 2.2 *and* APCA

Two gates, because the RSX base (`#040806`, near-black) is exactly the case
where they diverge.

- **WCAG 2.2** is the legal floor: **4.5:1** body text (1.4.3), **3:1**
  large text and **non-text/UI** including chart marks and focus rings (1.4.11).
  Every glyph fg must clear 3:1 against every bg it can sit on. Finding 27:
  rsx-glass ramp pairings are 1.77–2.23:1 — all below 3:1.
- **APCA** (git.apcacontrast.com) is the perceptual model WCAG 2 replaces for
  dark UIs: WCAG 2.x **overstates contrast for dark colours — 4.5:1 can be
  functionally unreadable when one colour is near black.** APCA's Lc is
  perceptually uniform: **Lc 75** min for body columns, **Lc 60** for secondary
  text, **Lc 45** for headlines/large, **Lc 30** for placeholder/disabled and
  semantic non-text marks, **Lc 15** for dividers/thick outlines. On a
  near-black exchange theme, gate the palette on APCA Lc, not just the WCAG
  ratio, or you ship pairings that "pass AAA" and are unreadable.

Operational form: **a palette unit test iterates the tier × ink matrix and
asserts both 3:1 (WCAG) and an Lc floor (APCA).** This is a cheap test that
would have caught findings 26 and 27 mechanically.

## 5. The always-on redundant channel (Okabe-Ito, ColorBrewer, Carbon)

Colour must never be a meaning's only carrier (WCAG 1.4.1; ~8% of men have
red-green CVD). Named tools:

- **Okabe-Ito** (Color Universal Design; Nature Methods default): an 8-colour
  qualitative palette distinguishable under all common CVD — `#E69F00 #56B4E9
  #009E73 #F0E442 #0072B2 #D55E00 #CC79A7 #000000`. Use it (or **ColorBrewer**
  "colorblind-safe" sets, or **IBM Carbon**'s categorical palette applied
  *strictly in sequence* to maximise neighbour contrast) for categorical
  channels — venues, series, order-types — capping at ~8 before you switch
  encoding, not add a ninth hue.
- **Direction/side is never hue-alone.** Grafana and Carbon both say avoid
  red/green as the sole signal; buy/sell and ±PnL need a redundant **shape,
  position, or sign** channel. rsx-term is right that side is *position* (bids
  left/asks right) and adds `B`/`S`, `▲`/`▼`; the sharpen is that trade side on
  the heatmap is still hue-only (finding 27) and the colourblind fix is gated
  behind a theme flag. **The redundant channel should be always-on, not opt-in.**

## 6. Numbers: tabular figures, right-aligned, fixed precision, unit-scaled

The exact figures are the hardest-working pixels, and rsx-glass renders them
worst (`10008x232905`: raw i64, variable width, layout jumps per tick). The
cross-industry rule set:

- **Tabular (fixed-advance) figures** so columns align and don't reflow as
  digits change (Matthew Ström, *Design Better Data Tables*; OpenType `tnum`).
  In an atlas renderer this means digit glyphs share one advance width.
- **Right-align** numerics (compared right-to-left, ones digit first).
- **Fixed precision** — constant decimal places per column, thousands grouping.
- **Unit-scale at the edge** — convert raw i64 fixed-point to tick/lot/human
  units at the API boundary, never render raw ticks. A number that changes width
  per update makes the whole layout jump per update.

## 7. Stable scales — never autoscale per frame (Grafana, terminals)

Grafana thresholds are **absolute pinned values**, and financial terminals hold
a **fixed or slow-moving scale** precisely so the picture doesn't strobe.
rsx-glass's `bases()` normalises the ramp to the current frame's max, so one
large order landing re-brightens every cell at once (finding 28). Rule:
**ramp/axis references decay slowly or pin; never re-normalise to the current
frame.** This is a *model-API* decision — reference state must be carried across
frames (rsx-term's rise-fast/decay-slow `foldBasis` is the reference doing it
right) — and it needs a **sequence test** (N deterministic frames, assert
bounded inter-frame change); single-frame goldens are temporally blind to strobe.

## 8. Density as a chosen mode on a spacing scale (Fluent 2, Ant Design)

Density is not per-component hand-tuning; it's **one multiplier over a spacing
ramp.** Fluent 2 exposes `baseHeightMultiplier` / `baseHorizontalSpacingMultiplier`
(+1 comfortable / −1 compact) over a **4px base ramp**; Ant Design ships
`small`/`middle`/`default` table sizes for the same reason. So: spacing lives on
a 4px modular scale (token tier 1), type on a modular scale, and **cell size /
padding derive from a single `density` token** — a data-dense desktop app then
ships a compact mode by flipping one value, not editing every panel.

## 9. Freshness at the point of reading

rsx-term/rsx-glass honesty markers (`—` unknown, `~` estimate) cover *absence*,
not *age*: when the feed dies mid-session rsx-glass keeps painting last-known
data in full colour with only a header dot flipped (finding 35). Data-dense
screens need staleness **where the eye is** — the value dims / gets `~` after N
ms without an update — not in a corner. This needs a clock plumbed through the
model (`Scene`), so it's a data-flow decision, not styling.

---

## The 6–10 rules that change the build

1. **Encode by channel rank** (Cleveland-McGill): exact→text, magnitude→
   length/position, luminance→overview, hue→category only and never a category's
   sole carrier. Primitive follows data topology (cell grid ≠ your resolution cap).
2. **Three-tier tokens; render code reads only tiers 2–3.** No raw hex in shader
   or Grid code. Theme/dark/colourblind = rebind the semantic tier only.
3. **Role-paired colours with reserved contrast** (M3 `on-` roles): glyph fg is a
   defined ink tested against every bg — never "bg one tier up."
4. **Gate the palette on WCAG 3:1 *and* APCA Lc** in a unit test over the
   tier×ink matrix (near-black base makes WCAG alone lie).
5. **Perceptually-even ramps** (M3 tonal palette / APCA-spaced stops), not a
   linear sRGB `blend()` — or distinct magnitudes collapse to one visible tier.
6. **Always-on redundant channel** for direction/category (Okabe-Ito / shape /
   position / sign); colour never the sole signal, not even behind a theme flag.
7. **Tabular, right-aligned, fixed-precision, unit-scaled numbers** — fixed
   advance width so layout never jumps per tick.
8. **Stable scales** — references decay/pin across frames, never per-frame
   autoscale; verify with a sequence (multi-frame) test.
9. **Density is one multiplier over a 4px spacing scale** (Fluent/Ant), not
   per-component tuning.
10. **Freshness at the point of reading** — stale data ages in place; never a
    full-colour last-known frame with only a corner dot flipped.

## Recommended token structure for `rsx-glass/CLAUDE.md` + a `tokens.go`

A flat, testable table the Grid builder resolves and the shader reads dumb —
formalising what `grid.go` already gestures at:

- **Tier 1 — primitives** (`tokens.go`): the ramp stops (perceptually spaced,
  §3/§5), the 4px spacing ramp, the type scale, the Okabe-Ito categorical
  sequence.
- **Tier 2 — semantic** (the current `grid.go` vars, renamed by *meaning*):
  `Live/Ask/Heading/Text/Muted/Degraded` + `BgPage/BgPanel` + **reserved inks**
  `OnRamp`, `OnPanel`. A `Theme` selects the tier-2 binding (default vs
  colourblind = only `Live/Ask` swap; the seam already exists).
- **Tier 3 — component roles**: `cell.bg = rampTier(size)`, `cell.glyph.fg =
  OnRamp`, `ladder.fg`, state-overlay opacities.
- **Contrast-pair guarantee**: a `palette_test.go` over every (bg-tier × ink)
  pair asserting **≥3:1 (WCAG 1.4.11) and ≥Lc 60 (APCA)** — catches findings 26/27.
- **Redundant-channel note**: for each colour-coded meaning, the second
  (shape/position/sign) channel carrying it without colour.
- **Density + scales**: the one `density` multiplier and its spacing/type scales.
- **Freshness**: the age threshold and the in-place stale treatment.

GL mapping: the shader consumes a **flat resolved `Cell`** (RGBA + glyph,
exactly `grid.go`) — all token resolution happens at Grid-build time, so the
renderer stays a dumb rasteriser and the design system is unit-testable off-GPU.

## Keep vs sharpen: the existing RSX system

**Keep (already strong, mirror it):**

- **colour = meaning, never decoration**, one hue per meaning (`VISUALS.md`,
  `playground/CLAUDE.md`) — this *is* the semantic-token discipline, ahead of
  most HIGs.
- **Glyph = shape channel co-equal to colour** (count/trade/persistence) and
  **side = position** — textbook Cleveland-McGill and CVD-safety.
- **Honesty markers** (`—`/`~`/dim-italic derived/hard-block cap) — a data-honesty
  layer most systems lack.
- **The `UseTheme` seam** — a working tier-2 rebind; the model for theme swaps.
- **Resolve-colour-at-build** (`grid.go`) — already the semantic-token boundary.

**Sharpen (where it falls short of Carbon/M3/APCA):**

- **fg == bg on walls** (finding 26): M3 role pairs — a reserved `OnRamp` ink,
  not `tier+1`.
- **Ramp collapses** (finding 28): perceptually-space the stops (M3 tonal /
  APCA), not a linear sRGB `blend()`.
- **Contrast below floor** (finding 27): gate on WCAG 3:1 **and** APCA Lc — the
  near-black base needs APCA.
- **Hue-only trade side** (finding 27): redundant shape/position always-on, not
  gated behind `colorblind`.
- **Per-frame autoscale** (finding 28): carry a decaying basis across frames
  (port `foldBasis`); add a sequence test.
- **Raw i64 numbers**: unit-scale + tabular + fixed-precision at the edge.
- **No freshness** (finding 35): age stale data in place via a clock in `Scene`.
