# speed-demo — shocking findings only

Full detail behind the ALWAYS/NEVER rules in `SKILL.md`. Read on demand — not
preloaded with the skill. Generic design advice lives in `SKILL.md` itself or
nowhere; this file is only for things that surprised us and would burn real
time again if forgotten.

## `agg` re-wraps at a DIFFERENT width than you recorded at, silently
`asciinema rec` defaults to the ambient shell's terminal size (often 80
wide) unless you pass `--cols`/`--rows`. If a script's lines fit on one row
at that width but exceed the target GIF width (e.g. 44 cols), `agg`
re-wraps them onto two physical rows when it resamples down — which breaks
any fixed `printf '\e[%dA'` cursor-up math. Not a crash: every redraw
*appends* below the last one instead of overwriting, stacking duplicate
rows in the final GIF (2026-07-06, rsx-cast demo — a 4-row race stacked
into 10+ visible rows). Fix: record at the exact `--cols`/`--rows` `agg`
renders at, always.

## A single frame extracted from an optimized GIF lies about the whole GIF
`gifsicle file.gif '#N' -o frame.gif` shows only that frame's dirty
rectangle, not the accumulated picture — it looks broken even when the
real GIF plays perfectly fine, and it can just as easily HIDE a real bug
(the stacking bug above was invisible in a naive first-frame check).
Composite properly before judging anything: Python `PIL.ImageSequence`
pasting each frame onto a running canvas with its own alpha as mask, or
`gifsicle --colors=255 file.gif -o x.gif && gifsicle --unoptimize x.gif -o
full.gif` (plain `--unoptimize` alone errors "too complex" on typical
32-color terminal palettes).

## `glow` silently renders with no reliable background under a recorded pty
`glow` never emits an explicit background-color escape — it assumes the
terminal already has one. Under a headless `asciinema rec -c "..."` pty
that assumption fails: tried plain, a `COLORFGBG` hint, explicit pre-paint
+ `clear`, and matching `--cols`/`--rows` at record time — got white
background, then a correctly-dark-but-undersized box, then zebra-striping,
across three separate attempts (2026-07-06). `rich` (called as a library
from your own script, not shelled out to) never has this problem — it
never emits background codes it wasn't asked for, so there's nothing to
guess.

## agg themes: `custom` errors, `gruvbox-dark` is LIGHT — verify bg by pixel
`agg --help` (1.9.0) lists `custom` as a valid `--theme`; passing it errors
"invalid value" at runtime — a real bug, not fixable via the `.cast` header.
So pick a built-in by ACTUAL background, not by name: `gruvbox-dark` renders
with gruvbox's LIGHT cream bg `#fbf1c7` (surprising). Sampled bgs (render a
6-row throwaway, read pixel (3,3) with PIL): `github-dark #171b21` (darkest,
cool), `monokai #272822` (warm dark — use for warm palettes), `dracula
#282a36`, `nord #2e3440` (cool). Warmth-match the theme to the palette.

## Sampling a palette from a reference photo (worked example)
When the "brand" is a photo/vibe, not a hex list: download the image, then
PIL for BOTH the dominant colors (`im.quantize(colors=12).getcolors()`) and
the most-SATURATED hue families (bucket pixels with `s>0.25, v>0.15` by
`colorsys.rgb_to_hsv` hue). Dominant alone skews to the dark/muddy bulk (a
black-subject photo returns mostly near-blacks); the saturated families are
the character colors. Then lift each hue to UI-legible brightness on a dark
base. Example — the rsx-cast "Cemani" palette from a black-rooster-in-spring
photo: iridescent-teal sheen `#57b0a3`, warm olive-gold bokeh `#c9a24e`,
earth-brown `#b0703f`, moss `#9aad4c`, warm off-white `#ece6d8`, dim
`#8f8672`, on a warm-dark `monokai` base. Full hex + semantic mapping live in
the project (`rsx-cast/demo/CLAUDE.md`), not here.

## Typewriter reveal: box height jitters unless you render the FULL structure
Revealing text character-by-character against only the text typed so far
(omitting not-yet-reached lines) makes the bordered box visibly grow taller
as typing crosses each line break. Fix: always render every line's slot
(blank for not-yet-reached ones), computed from the FULLY TYPED text once,
up front — the box is the final size from frame one, only the text inside
fills in.

## RSX demo family — the canonical reference SET, not one crate
Don't treat `rsx-book/demo/bench-live.sh` as the only worked example — by
2026-07-22 five RSX crates each ship the full arc: `rsx-book` (expanding-brain
`░▒▓█` ramp: naive `BTreeMap` → slab+compression → the depth-invariant match
bench), `rsx-matching`, `rsx-risk`, `rsx-cast` (a `pitch.py`+`rich` narrative
variant, not bash), `rsx-term`. Each lives at `rsx-<crate>/demo/` with a
`bench-live.sh` or `pitch.py`, a `demo/CLAUDE.md` (the per-crate story +
honesty caveats + regeneration steps), and exactly one tracked artifact
`<crate>-live-opt.gif` (raw `.gif`/`.cast` gitignored). All five share: the
project's canonical palette (documented once, `rsx-cast/demo/CLAUDE.md`),
warm-dark `agg --theme monokai` base, the neutrino mascot close
(`····▸ rsx`), and a single closing CTA ("Read the code." + repo URL). When
prompted for "the RSX demo," read the target crate's own `demo/CLAUDE.md` —
each has crate-specific honesty caveats (e.g. rsx-book's single-core/shared-
host variance note) that don't belong in this project-agnostic skill.

## A shorter-bar-wins comparison reads backwards to a casual viewer
A latency chart where less is better still LOOKS like the longer bar is
winning to someone skimming a feed for two seconds. Show the reciprocal
(throughput = 1/latency) as a count-up first — bigger, visibly climbing
number reads as "winning" with zero explanation needed — then cut to the
latency bars as the credibility detail underneath, labeled honestly as
derived (not a separately-measured throughput number).
