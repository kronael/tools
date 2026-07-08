---
name: speed-demo
description: Show off a library's REAL benchmark speed as a short thrilling terminal recording rendered to a mobile-friendly (tall+narrow) GIF — the bench appearing to run live, numbers landing, one headline holding. NOT for static bench tables or dated reports (those go in reports/), NOT for running the benchmark itself (use the lib's bench tool), NOT for UI/product video (use create video).
when_to_use: show off library speed, benchmark demo gif, speed reveal, asciinema recording, thrilling benchmark results, animated latency/throughput, "something is happening" numbers, shareable perf gif, mobile portrait demo, present a lib's performance, per-lib demo in libs/xxxx.md
user-invocable: true
---

# speed-demo — a library's speed as a short terminal GIF

Turn a library's REAL benchmark numbers into a SHORT (~15-30 s) thrilling
terminal recording → a shareable, MOBILE-friendly GIF (**tall + narrow**, legible
on a phone). The bench appears to run live, numbers land, one headline holds.
Works for ANY speed-focused lib and any bench tool (Criterion, google-benchmark,
hyperfine, nanobench). The artifact is a terminal GIF — NOT a Remotion/product
video (that's the `create` skill).

Discipline stolen from how Jump presents Firedancer: **isolated per-core
numbers, one visceral headline, lab-vs-production honesty on screen** — separate
a lab microbenchmark from system throughput, always.

## Pipeline
`real numbers` → a scripted terminal reveal → `asciinema rec` → `agg` (portrait
GIF) → `gifsicle` (optimize). Check the tools exist first; install if missing
(`asciinema`, `agg` = asciinema-gif-generator, `gifsicle`).

Content authoring and recording are two SEPARATE, composable choices —
`asciinema` just records whatever ANSI hits the pty, it doesn't care what
produced it. Default content layer: **Python + `rich`, run via
`uv run script.py` with PEP 723 inline deps** (no separate install step, no
venv to manage):
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rich"]
# ///
```
Then `asciinema rec --cols 44 --rows 32 -c "uv run pitch.py" demo.cast` —
the recording half is unchanged either way. NEVER hand-roll cursor-up math
or char-repeat bar fills in bash — `rich.live.Live` measures its own height
and redraws correctly, `ProgressBar` does bar-fills, `Panel` handles
visible-width padding with embedded ANSI. Plain bash only for zero-animation
reveals or when `uv`/`rich` are unavailable.

## Method (every demo)
1. **Real numbers first.** Run the lib's bench, read the ACTUAL output. NEVER
   fabricate or quote a remembered figure — re-run and read the current number.
   Isolated, per-core, quiet box.
2. **One headline + 3-5 isolated supports.** The single visceral figure, backed
   by a few per-core component numbers. Not blended system throughput.
3. **Script a SHORT reveal.** The bench "running," a count-up / bar-fill, the
   headline snapping in. Dynamic, ~15-30 s. NEVER a static dump.
4. **Record MOBILE-PORTRAIT.** Narrow cols × tall rows (~40-48 cols × ~28-36
   rows), big legible figures. `asciinema rec demo.cast` → `agg --cols 44
   --rows 32 demo.cast demo.gif` → `gifsicle -O3` to shrink. This is ALSO the
   right shape for an X/Twitter feed post, not just Stories/Reels — mobile
   apps (X included) render tall vertical media full-width; landscape gets
   pillarboxed smaller. Do NOT invert to landscape for "feed-friendly."
5. **Honesty on screen.** Hardware, single-core/pinned, quiet box, n + percentile.

## Recording gotcha: pin `--cols`/`--rows` at RECORD time, not just render time
Any redraw animation (bar-fill, cursor-up-then-overwrite race) MUST be
recorded at the SAME `--cols`/`--rows` `agg` will render at — `asciinema
rec` otherwise defaults to the ambient shell size, `agg` re-wraps lines
that don't fit at resample time, and every redraw *appends* instead of
overwriting, stacking duplicate rows in the final GIF. See `lessons.md`
("Recording gotcha") for the full symptom + fix.

## Verify the recording before calling it done
NEVER judge a GIF from a single extracted frame (`gifsicle file.gif '#N'
-o frame.gif`) — it shows only that frame's dirty rectangle, not the
accumulated picture, and will hide a real stacking bug. ALWAYS composite
frames respecting disposal first (PIL `ImageSequence`, or `gifsicle
--unoptimize`) before calling a recording done. See `lessons.md`
("Verify the recording") for exact commands.

## End on ONE empty bottom line — never a pointer flush at the edge
The final frame must leave exactly one blank line at the bottom, with the
pointer (cursor) on the row above it. A cursor sitting flush against the very
bottom edge gets cropped or looks cramped in an X/Twitter feed. Two fixes,
both needed: bottom-anchor the last renderable so the pointer is the
second-to-last row (a `fill_bottom(..., bot=1)` padding, not vertical-center),
AND keep the REAL terminal cursor hidden at exit (`\x1b[?25l`) — `rich.Live`
re-shows it on exit and it parks right below the region, re-flushing the
bottom (the following shell prompt restores a visible cursor anyway). Confirm
by compositing the last frame and eyeballing it.

## Narrative FLOWS like a terminal — do NOT clear/re-center between claims
The narrative is typed to stdout and LEFT there — filling the screen top-down
like a real terminal session. Do NOT `console.clear()` + re-center each claim:
that "reshow" reads as a slideshow and kills the terminal illusion (the whole
credibility premise). Let the real terminal cursor trail the typing (show it,
type char-by-char to stdout). Plain paragraph text — no `Panel`/border/title,
a small `rich.padding.Padding` indent is plenty. Reserve `rich.panel.Panel`
(bordered) for STRUCTURED DATA only (a numbers table); prose in a box reads as
marketing. Typewriter reveal (type against the FULL final line structure so
nothing jitters) + blinking `█` cursor throughout. ALWAYS type at READING
pace, not typing-demo pace: ~45 ms/char (~250 wpm) with jittered delays, a
longer stop (~0.3-0.5s) at sentence-enders `.!?` only (never commas/colons),
and a real ~0.8s beat at each blank-line paragraph break — the viewer reads
along instead of chasing the cursor. `glow`/`slides`/`presenterm`/`patat`
were tried and rejected for cards (no reliable background under a headless
pty); `rich` sidesteps it. Detail in `lessons.md`.

## Clear ONCE, and open the reveal on a weighty beat
Narrative-act → data-act: the ONLY screen clear is that transition. After it,
don't dump numbers cold — open on a short weighty centered callout ("See for
yourself.") held ~2-3s, THEN the numbers climb in, THEN the CTA, all in ONE
`rich.Live` region (wrap each in a constant-height `Padding` block so it never
jumps). One clear keeps terminal continuity; the beat gives the reveal weight.

## Critique the recording before calling it finished
ALWAYS spawn a critique pass on a first clean cut — one `visual`-type agent
on the actual composited frames (typography/whitespace/hierarchy/color),
one `general-purpose` agent on outside best practices (colorblind-safe
comparisons: never red+green alone, ~8% of men affected, always pair color
with a shape/text cue). Run in parallel, then apply concrete fixes. See
`lessons.md` ("Critique the recording") for the specific findings this
surfaced (top-anchored cards, indistinguishable tied rows, underused bar
width) as a checklist of what to look for.

## Reframe "lower is better" data as "higher is better" first
A shorter-bar-wins latency chart reads backwards on a casual skim. Lead
with the reciprocal (throughput = 1/latency) counting UP — intuitive win —
then the latency detail, labeled on screen ("derived: 1/latency, not a
separate bench"). Full rationale in `lessons.md`.

## Match the project's real palette (design system OR reference photo)
Don't pick arbitrary ANSI names. If there's a design-system palette
(`tailwind.config.ts`, `DESIGN.md`, a rendered UI), pull exact hex via
`rich`'s `color_system="truecolor"`; group genuinely-tied comparison rows
under one hue rather than inventing a color the brand lacks. If the "brand"
is a reference PHOTO/vibe, sample it programmatically (PIL) — pull the
dominant AND the most-saturated hue families (saturated = the character
colors; dominant alone skews dark/muddy), then lift to UI-legible brightness
on a dark base. Worked example (exact hexes) in `lessons.md`.

## Card openers are claims, not section labels — and lead with the product
VC-deck guidance, not invented: titles are full sentences — reading only
the titles should give 80% of the point, phrased conversationally. So the
opening clause IS the specific insight ("It's fast because it's minimal."),
NEVER a generic section name ("why it's fast", "the problem"). Name the
PRODUCT as the subject of the resolution claim ("rsx-cast is as fast as it
goes"), not the team ("we built it to be…") — the viewer should leave
remembering the name, not the builders. Copy iterated with the user is
load-bearing: when polishing later, refine rhythm/pacing subtly — NEVER
rewrite dictated phrasings wholesale.

## One clear call to action, once, at the end
End on a single unambiguous action — one repo URL, on-screen. NEVER scatter
CTAs through cards — one closing action beats five diluted ones (mid-roll
CTAs only pay off in long-form video, not a ~30-45s demo).

## `agg` themes: `custom` broken, `gruvbox-dark` is LIGHT — pick by bg hex
`--theme custom` is listed in `--help` but errors "invalid value" at runtime
(agg 1.9.0) — not fixable by editing the `.cast` header. So pick the closest
built-in by ACTUAL background hex — and verify it, don't trust the name:
`gruvbox-dark` renders with gruvbox's LIGHT cream bg (`#fbf1c7`), not a dark
one. Sampled bgs: `github-dark #171b21` (darkest, cool), `monokai #272822`
(warm dark — right for warm palettes), `dracula #282a36`, `nord #2e3440`
(both cool). Match the theme's warmth to the palette's.

## Per-library particularities live IN the project, not here
Each lib demos differently (a latency count-up vs a throughput race vs a
vs-alternatives bar chart). Keep per-project specifics — headline, isolated
numbers, reveal script, honesty caveats — in a `demo/` folder inside THAT
project: its `demo/CLAUDE.md` is the how-to. E.g. `rsx-book/demo/CLAUDE.md`.
NOT in this general skill — it stays project-agnostic; read the project's
`demo/CLAUDE.md` before building.

Git tracks exactly ONE artifact per demo: the optimized `*-opt.gif` (the
postable). NEVER commit the raw agg `.gif` or the `.cast` recording —
ALWAYS gitignore both; they stay on disk for iteration and only
`make clean` removes them.

Write the per-project script directly (a top-to-bottom sequence of card()/
panel() calls with the actual copy inline) rather than building a generic
reusable framework of helper functions for "any demo" — each demo's content
is one-off and hand-tuned (exact wording, exact hold times, exact which-beats-
get-merged); premature generalization here just adds indirection between you
and the thing you're actually tuning.

## ALWAYS / NEVER
- ALWAYS re-run the bench and quote the CURRENT number — NEVER a remembered one.
- ALWAYS portrait (tall+narrow) + motion — NEVER landscape, NEVER a static table.
- ALWAYS keep the honesty caveat on screen — NEVER blend lab micro-numbers with
  system throughput or imply production.
- NEVER claim "faster than X" without a real same-box head-to-head.
- ALWAYS record any cursor-redraw animation at the exact `--cols`/`--rows`
  `agg` will render at — NEVER rely on the ambient shell width matching.
- ALWAYS composite frames (respecting GIF disposal) before judging a
  recording — NEVER trust a naive single-frame extraction from an
  optimized/delta GIF.
- ALWAYS prefer Python + `rich` (via `uv run` + PEP 723 inline deps) for any
  card/redraw content — NEVER hand-roll cursor-up math or char-repeat bar
  fills in bash when `rich.live.Live`/`ProgressBar` already do it correctly.
- ALWAYS flow the narrative like a terminal (typed, left on screen), bordered
  box for DATA only — NEVER clear/re-center each claim (reads as slides).
- ALWAYS open a card with the specific claim ("it's fast because it's
  minimal") — NEVER a generic section label ("why it's fast") as the lead.
- ALWAYS end on exactly one call to action, shown as on-screen text —
  NEVER several competing links/asks.
- ALWAYS type narrative at reading pace (~45 ms/char, sentence stops,
  paragraph beats) — NEVER race the reader with 15-20 ms/char typing.
- ALWAYS spawn a parallel critique pass (visual + best-practices agent) on
  composited frames before calling a recording finished — NEVER ship on
  your own first-glance judgment.
- ALWAYS lead a "lower is better" comparison with its reciprocal as a
  count-up, labeled "derived" — NEVER open on a bar chart that reads
  backwards to a casual viewer.
- ALWAYS pull exact hex from the project's real palette (or sample a
  reference photo via PIL) — NEVER invent a color it doesn't define.
- NEVER trust an agg theme by name (`custom` errors; `gruvbox-dark` is a
  LIGHT bg) — ALWAYS pick by verified background hex, warmth-matched.
