# Logo / emblem / badge design

Validated 2026-07 on the gothic-emblem set (procedural PIL renderer, 8
candidates): each rule below moved the result from clip-art tier to
professional tier. Applies to any medium — procedural raster, SVG, p5.js.

## Method

1. **One motif per mark.** The name must be readable in the silhouette
   (key → bow+stem+teeth, crown → band+peaks). NEVER decorate a weak center
   with texture — cut elements until the silhouette carries it.
2. **Deterministic symmetric geometry.** NEVER random scatter, jitter,
   cracks, or floating debris — randomness reads as noise, not craft.
   Seeded randomness is for backgrounds only, never the mark.
3. **Stroke tokens.** Define one base unit (≈2.4% of mark radius); every
   stroke is a small multiple (1u regular, 2u bold). Gaps between strokes
   ≥ 1u or they fuse at small sizes.
4. **Icon over frame.** Frame band ≤ 16% of radius; motif fills 65–70%.
   Micro-detail (ticks, studs, marks) becomes dirt below 64px — keep ≤ 8
   such elements, or none.
5. **Grayscale first.** The design must work in one color: window/backdrop
   ~10 luminance, body fills 40–120, outlines 220+. Color is decoration,
   never structure.
6. **Palette: black + one metal + ONE accent.** Accent goes on exactly one
   focal element per mark (seam, core, pupil, jewels). A neutral family
   with a single hot accent beats per-mark accent colors.
7. **Optical corrections.** Circles among flat-edged shapes overshoot
   2–3%. Triangle visual center sits below the mathematical center —
   nudge. Light-on-dark strokes look fatter (irradiation) — thin them.
8. **Raster = supersample.** PIL/Pillow draws have no antialiasing:
   render geometry at 3–4× on a transparent layer, LANCZOS downsample,
   composite onto the background rendered at final size. Glow: duplicate
   shapes on a separate layer, gaussian-blur at 2 radii, composite under
   the ink.

## Acceptance tests (automate, don't eyeball)

- **64px strip**: all marks at 64px over light AND dark backgrounds.
- **Grayscale strip**: same strip through `convert('LA')` — every motif
  must still read.
- **Transparent export**: corner pixel alpha == 0, center alpha > 0;
  composite over mid-gray and inspect.
- Iterate render → strip → fix until all three pass.

## Deliverables

Per candidate: labelled dark card (`NN_name.png`) + transparent flat
emblem (`NN_name_flat.png`). Comparison sheet with all candidates labelled.

## Pitfall

Image-preview pipelines (including the Read tool) contrast-normalize:
near-black background detail can display as bright white. ALWAYS verify
suspicious background artifacts with pixel probes before "fixing" them.
