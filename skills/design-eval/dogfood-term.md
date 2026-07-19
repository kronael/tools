# design-eval: rsx-term (TUI — the visual-language template)  (mode: review)
Pixels seen: `rsx-term/ui/testdata/book_view.golden`, `dom_view.golden` (the
byte-locked rendered frames — NOTE: goldens are ANSI-STRIPPED, see finding 7)
Palette source: `ui/styles.go`; glyph channels/ramps: `ui/stream.go`; language:
`VISUALS.md`
Measured: WCAG 2.1 + APCA-W3 0.1.9 over every ink×bg pair incl. both themes
(script: scratchpad `measure.py`, 2026-07-19); glyph ink coverage measured with
the repo's own glyphbank method against DejaVuSansMono.

Reserve scope: a TTY exposes text to the terminal, so screen readers *can* read
it — better than raw GL — but colour/contrast semantics still end at the
emulator. The colourblind theme and `modePlain` ladder are the real a11y
surface; findings below are scoped to that.

## Scores (1–5)

hierarchy 4 · colour+tokens 4 · contrast 2 · redundant-channel 3 ·
typography/numerics 4 · spacing/density 4 · layout/responsive 4 ·
consistency 4 · data-density/minimalism 5 · feedback/honesty 5

## Findings (most-damaging first)

1. **[system] Trade SIDE is hue-only on the map and tape rail** — prints use
   one magnitude ramp `○◆●■` coloured `Live` green (buy) vs `Ask` red (sell)
   (`aggressorStyle`, `tradeCellStr`). WCAG 1.4.1 / deuteranopia trap, and
   **`modePlain` loses side entirely** (the bare glyph is returned — the
   degradation ladder's own floor drops the meaning). The language already
   solves side elsewhere without colour (`B`/`S` DOM tape, `LONG`/`SHORT`,
   bid-left/ask-right, `▲`/`▼` own-order ruler shapes) — the map's trade
   layer is the one place hue is the sole carrier. Fix: split the trade
   ramp per side using the language's own up=buy/down=sell convention:
   buy `▵▴△▲` / sell `▿▾▽▼`. Measured in DejaVuSansMono (glyphbank
   method): 0.079/0.110/0.144/0.263 and 0.083/0.110/0.169/0.262 — two
   mirrored, ascending-ink, tofu-free 4-step ladders. Hue stays as the
   second channel; shape now carries side in every degradation mode.
2. **[system] Trade/own overlay ink collapses on bright ramp tiers** —
   `tradeCellStr`/`ownCellStr` put the aggressor/accent ink over
   `rampColor(sz)`: Live on ramp4 = **1.00:1 / Lc 0** (an invisible buy
   print on a wall — the most information-dense event on the screen),
   Ask on ramp3 = 1.09:1, Accent (own `◇`) on ramp3 = **1.00:1**;
   colorblind theme identical class (CbBid on cbramp4 = 1.00:1). Fix: cap
   the overlay background at ramp tier 1 — worst pair becomes CbBid/ramp1
   3.91:1 / Lc −38.8; every aggressor/accent pair ≥3:1 and ≥Lc 30 in both
   themes. The print outranks the wall it lands on.
3. **[system] Density/persistence glyph fg is "bg one tier up"** —
   `cellStr` modeTrue sets fg `rampColor(sz+1)` on bg `rampColor(sz)`:
   adjacent tiers measure 1.77–2.23:1, and at sz=4 the clamp makes
   **fg==bg (1.00:1)** — the `▚` persistence mark vanishes exactly on
   walls. This is the bug class already FIXED downstream in rsx-glass
   (`glyphFg` reserved-contrast pick + `TestGlyphContrast`) but still live
   in the template — the two frontends have diverged on the language's own
   rule. Fix: adopt the reserved-ink pick upstream (TextBright on dark
   tiers, Page ink on bright tiers; worst pair 3.97:1) + port the palette
   contrast test.
4. **[system] NOW-row micro-bar fg is the ramp tint** — `microCellStr`
   modeTrue draws the bar in `rampColor(sizeTier)` on the page: a tier-1
   bar is 1.78:1 / Lc ≈ −8, near-invisible. Same reserved-ink fix (glass
   already renders NOW bars in the reserved bright ink — blessed pixels
   exist).
5. **[system] Muted `#586b62` is APCA-sub-floor** — WCAG 3.54:1 on Page
   (passes) but **Lc −23.3**, under the Lc 30 any-text floor; it carries
   labels, captions, help, the time gutter, and every `~` derived value.
   Near-black-base WCAG/APCA divergence, exactly what the rubric warns
   about. Debt, not a local fix: hex verbatim-shared with the dashboard,
   spec 55, and rsx-tui — needs a coordinated palette rev.
6. **[screen] ARMED banner is 2.35:1 by WCAG** — TextBright on Ask bg
   (`StyleArmed`); APCA says Lc −45.7 (borderline pass) — the two models
   disagree. Bold + `⚠` + the red field itself carry redundancy, so this
   is not hue-only; recorded as debt with numbers (a dark-on-red ink would
   clear both models) for a deliberate decision, not a drive-by change.
7. **[screen→system] The golden discipline is colour-blind** —
   `goldenCompare` byte-locks `stripANSI(m.View())`: glyphs and layout are
   locked, colour is not, which is why every contrast defect above lived
   under green goldens ("goldens assert stability, not visibility"). Fix:
   a palette contrast test (the WCAG+APCA matrix as a unit test) — closes
   the class, not just the instances.

## Keep (already strong — do not regress)

- **Feedback/honesty (5/5)** — `~`+StyleDerived, `—` unknown, `·· pending`,
  hard-block fat-finger cap, SLA amber/red thresholds, md-stale tag. The
  strongest honesty layer this reviewer has scored.
- **Data-density/minimalism (5/5)** — stable bases (rise-fast/decay-slow —
  the D1 rule done right, upstream of glass's v1 gap), three nonlinear
  compressions each documented with exact boundaries, no chartjunk.
- Typography/numerics — display-precision fixed-point (`0.010001×6.0000`),
  monospace tabular by construction, exact numbers confined to ladder/tape.
- Tokens + theme seam — meaning-named roles, `UseTheme` swaps only the
  bid/ask pair, doc-sync tests (`TestGlyphVocabularyDocumented`) keep the
  legend honest.
- The calibrated-glyph methodology (glyphbank) — measure, don't guess.

## Sharpen (the ranked fix list = the improvement work)

1. Side-by-shape trade ramps (finding 1) — `ui/stream.go` + VISUALS.md +
   notes/, re-bless `book_view.golden` after visual confirmation.
2. Overlay-bg cap (finding 2) — one clamp in `tradeCellStr`/`ownCellStr`.
3. Reserved glyph inks for density/persistence/micro (findings 3–4) —
   adopt glass's `glyphFg` upstream.
4. Palette contrast test (finding 7) — the WCAG+APCA matrix in `ui`.
5. Document 5–6 as tracked debt (coordinated palette rev).

## Verdict

The language is sound in structure — channel separation, honesty, stable
scales, and token discipline are exemplary — but its contrast layer has one
systemic bad rule (derive-fg-from-ramp) and one hue-only meaning (trade
side), both measurable and both already half-fixed downstream in glass.
Fix them here, in the template, and let glass mirror; the screens apply
the language faithfully and need no independent repair.

---
Outcome (2026-07-19, post-eval): findings 1–4 + 7 FIXED in rsx repo commit
0c16126 [term] (side-by-shape trade ramps, overlay cap, reserved glyph inks,
TestPaletteContrast); 5–6 recorded as measured debt in VISUALS.md "Known
design debt". book_view.golden re-blessed with visual confirmation.
