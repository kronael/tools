# Monty Python cutout (Terry Gilliam)

Jerky paper-cutout animation of REAL photo pieces — the Flying Circus look. The
charm is that it's obviously cut-up photographs, hinged and yanked around, never
smooth vector motion. Load this on demand; it is NOT preloaded.

**Assets — real photos, roughly cut.**
- ALWAYS real photographs/engravings, NEVER drawn shapes. The crude part is the
  EDGE SHAPE (rough scissor cut), NOT the background: you MUST matte the source
  photo's background OUT — a real alpha matte (grabCut), never a loose CSS clip.
  A clip that leaves a ring of the original sky/bg is a HALO — the #1 tell it's a
  sliding photo sticker, not a cutout. Then ink the cut edge dark so it reads
  deliberate. (Posterize hue-preserving, per-channel — a vector quantizer like
  ELBG invents false color bands, e.g. a cyan blotch on skin; warm shadows first.)
- Cut articulated subjects into PIECES on their joints: head → skull + hinged
  jaw, a limb at the elbow, a mouth that opens. Each piece is its own layer with
  `transform-origin` at the hinge.

**Motion — hinged and jerky.**
- Author at LOW fps (8–12) with STEPPED motion — NO easing, NO tweened
  interpolation. Pieces SNAP between poses; that stutter is the look. Capture at
  that low fps too — never render 60 smooth frames and drop them.
- Move by rotating pieces around the joint pivot in coarse steps (~5–15°): mouths
  chomp by pivoting the jaw, legs stomp, things slide in flat from offscreen.
- Keep a tiny constant wobble on everything (±1–2px, ±1°) so held pieces still
  read as flapping paper.

**Paper collage look.**
- Flat lay: every cutout gets a hard offset drop-shadow (lifted off the page) and
  faint paper grain. Backgrounds are flat cut shapes or a real texture, never
  gradients. Absurd scale jumps and non-sequitur cuts are on-theme.

**Build + capture.** Position pieces as layers (HTML/Canvas), drive poses by
frame index (seeded, deterministic), Playwright-capture at the target low fps,
ffmpeg → gif.

- **Sells it:** real recognizable photos · crude cut edges · snap motion · hard
  shadow · absurd juxtaposition.
- **Kills it:** clean masks · eased tweens · high fps · drawn/vector shapes.

## Rig it — hierarchy + paths, THEN implement

NEVER hand-place frames ad-hoc. Build a puppet rig:
- **Parts hierarchy (scene graph).** Each cut piece is a node
  `{parent, x, y, rot, scale, pivot}`; children inherit the parent transform —
  e.g. `farmer{ torso → head(front|back), arm → hand }`,
  `plant{ stalk → maw{ jawTop, jawBot, teeth, drool } }`.
- **Motion paths (tracks).** Each animated property gets ONE keyframe track over
  frame index — `[[frame,value],…]`, HOLD-then-SNAP (stepped). That track is the
  piece's "path".
- **Renderer.** `renderFrame(i)` walks the hierarchy, samples each track at `i`
  (step-hold), composes parent→child transforms, draws. Deterministic in `i`.

ALWAYS define the parts + tracks FIRST as data (consts), THEN write the renderer
against them — NEVER bury motion in per-frame `if` branches.

## Swap, don't morph

Change a pose or facing by SWAPPING one cutout for another, NEVER by
rotating/warping a photo — it's the hallmark of paper cutout. A head-turn = hide
the front-face piece, show a back-of-head piece on the same pivot. A gape = swap
closed jaw for open. Keep swappable pieces as sibling nodes toggled by a
visibility track.

## Two independent pieces sharing an edge leave a seam

A part cut into two rig nodes at a shared line — e.g. a body split into
`torso` (below the neck) and `head` (above it) so the head can carry its own
rotation independent of the body — are two SEPARATE, independently
transformed, independently `filter:drop-shadow`'d elements that must abut
pixel-perfectly. They won't. Each filtered layer is its own GPU-composited
texture; the shared edge doesn't reliably land on the same device pixel even
when both sides use the identical clip percentage, and clip-path masks on two
such layers rasterize independently (can desync further). The tell is a
hairline of the PAGE BACKGROUND showing clear across the frame at the join,
not just over the piece — worse, once the two nodes' rotations diverge (a
head-tilt track independent of the torso), the "shared" edge isn't even
parallel anymore: it's a wedge that widens with distance from the rotation
pivot (a 3° relative tilt opens ~14px at 270px from the pivot).

Fix: clip via an `overflow:hidden` wrapper around an unclipped, filtered img
(cleaner than `clip-path` directly on the filtered element, though not
sufficient alone), AND give whichever layer paints on top (per z-index) a few
px of BLEED on its clip window — sized to the worst relative rotation the two
pieces can reach before something else (a hand, a prop) occludes the seam
anyway, not just enough to cover the zero-rotation case. Bleeding re-paints
the SAME source photo over the gap, so it's invisible at rest and only a
few-px ghost at the worst rotation — far less visible than an open seam.
Verify across the FULL rotation range the two pieces actually use, not just
frame 0 (see SKILL.md § Publication-grade bar).

## The closer stays in the same paper world — reuse the rig, don't re-scene it

A narrative cutout short must end INSIDE the paper world (see SKILL.md § One
themed world, entered once, exited once) — never cut to a flat title-card in
a different visual language for the payoff. The cheapest way to guarantee the
closer matches the opener's grade/grain/ink/shadow exactly is to not build a
second scene at all: extend the SAME rig HTML with a second, non-adjacent
frame range (append new PARTS/TRACKS entries; existing frames are unaffected
as long as every new track's first keyframe is `[0, <the old default>]`, so
`step()`'s lookup for early frames still resolves to the old value). Capture
the two ranges into separate gifs with the frame-index capture driver (it
already takes an explicit index list, e.g. `74,75,...,103`, not just `0..N`),
and let the real terminal proof sit between them in the compose script. Sanity
check after extending: re-render the ORIGINAL frame range and diff — it should
be byte-identical to the previous build, proving the new beat didn't perturb it.

**Spelling a word without a photo of one.** The medium's rule is "every piece
gets the same treatment," not "every piece must come from a photograph" — this
rig already has non-photographic pieces (a drawn crop/sprout, a built plaid
sleeve, a built cap) that fit right in because they get the same ink-edge +
drop-shadow as the photo pieces. A cut-paper wordmark is the same move: render
bold glyphs with a real font, colorize (per-letter color is fine — e.g. a
value ramp borrowed from another beat so the payoff visually rhymes with the
proof instead of needing a caption to explain it), then `ink_edge()` the WHOLE
word as ONE alpha silhouette. Inking each letter separately makes them read as
six stickers glued to the page; inking the composed word once gives it a
single rim, like a real cut-paper sign.

## Why it reads amateur — the craft (fixes, by impact)

It fails when pieces clash like clipart, not because of the tool.
- **Unify the material — #1.** Every piece must read as ONE physical world.
  Same treatment on all: INK/darken the cut edges (Gilliam's actual trick — a
  dark outline makes a cutout look deliberate and sit ON the page), ONE shadow
  direction+depth, ONE grain/paper texture over the whole frame, ONE color grade.
  Mismatched light/edges/grade = clipart.
- **Silhouette test.** Each piece must read instantly as a bold BLACK silhouette;
  if you can't tell what it is in solid black, recut it.
- **Stage in TIME.** One clear action per beat, pieces entering in ORDER; primary
  moves, secondary + shadow LAG. Everything moving at once is the amateur tell.
- **Restraint — hold.** Not everything moves; a strong STILL composition per beat
  beats constant motion. Motion NEVER saves weak design.
- **Timing is the comedy.** anticipation → HOLD → snap → settle. The joke lives
  in the holds and the snap, not the assets.
