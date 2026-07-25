# Collage motion — real material, external judge

For memes, promo loops, and any short film with a character or a subject in it.
Read this INSTEAD of inventing artwork.

## The two rules

**1. Never draw the subject. Transplant it.** Hand-written canvas/SVG figures by
an LLM do not clear a taste bar — five days of iterating one proved it. Fetch a
real photograph, painting or engraving, cut it out, and animate the cutout. An
LLM is good at compositing and timing real material and bad at draughtsmanship;
build on the first skill, not the second.

**2. Never score your own output.** "Renders correctly", "legible at 360px" and
"another model liked it" are not quality evidence. Stand up a blind forced-choice
tournament and let it decide (below).

## Pipeline

    fetch  -> Wikimedia Commons API, exact `File:` titles pinned, licence +
              author recorded in a CREDITS.md next to the assets
    cut    -> ONE shared treatment for every piece, or the frame reads as pasted
              stock: grabCut matte -> warm grade -> posterised paper bands ->
              dilated dark ink edge (the single biggest unifier)
    stage  -> flat paper card + subject + Impact-style caption, 3-4s loop
    render -> deterministic renderFrame(f) + headless capture -> gif/mp4

Reference implementation (all four steps, ~450 lines total):
`solve/demo/collage_fetch.py`, `cutout_lib.py`, `collage.assets.py`,
`collage.html`, `collage.build.sh`.

Practicalities that cost real time to learn:
- Downscale sources to ~1200px before grabCut; it is superlinear in pixels and a
  4000px painting takes minutes per piece for no visible gain.
- Rects as FRACTIONS of the source, never pixels, so re-fetching a different
  resolution still cuts the same subject.
- Search hits drift: print the resolved `File:` title and pin the good ones.
- One rig, N variants via `?v=N`, so eight memes are eight config rows.

## Rendering contract

`window.CONFIG = {TOTAL, FPS, W, H}`, `window.renderFrame(f)` draws frame f from
nothing but f, `window._ready = true` after images decode. Capture drives it by
frame index, so nothing depends on wall-clock and a rebuild is byte-reproducible.

Motion: smoothstep on continuous tracks, hard step-hold on discrete ones
(caption swaps, pose changes). Mixing the two is what makes motion read as mush.
Entrances get overshoot — cut paper slapped down, not eased into place.

## Judging (the part that makes this different)

Build the judge BEFORE the artwork; if no judge passes its controls, the whole
plan dies cheap.

1. **Normalise** every clip to one canvas, fps, duration and encoder, or judges
   score compression instead of craft.
2. **Damage controls**: for each professional reference clip, make twins with one
   property destroyed — timing (jitter frame order), silhouette (crush to 12% and
   blow back up), framing (1.7x off-centre crop).
3. **Calibrate**: a judge's votes count only if it prefers the original over its
   own damaged twin (>=80%, both A/B orders). Discard failures, don't average.
4. **Compare**: forced choice, single-axis questions, both orders. Order-flipped
   answers are position bias — report separately, never count.
5. **Same genre only.** A UI/infographic clip cannot win "looks studio-produced"
   against character animation no matter how good it is: 19/19 losses in one run
   cited "character animation" as the reason. Judge like against like, or the
   verdict measures genre.

Reference implementation: `solve/demo/eval/{clipkit,judge,report}.py`.

## Content

Ground every factual caption in a recorded artifact and extract it with a script,
so a number that no run produced cannot reach the screen. Jokes assert nothing
and need no source. Never stage an invented "proof" card — a fabricated result is
the one defect no amount of polish survives.
