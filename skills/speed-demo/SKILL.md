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
   Cite the source bench (file + test name) and the commit/date the number
   came from in the project's `demo/CLAUDE.md` — never just in the video.

## Narrative arc — cold-open meme → data → flex + mascot (PROMPT for these on a new demo)
A bare bench dump under-performs. When creating a NEW demo, SUGGEST this arc and
PROMPT the user for the pieces before recording — the copy and the character are
the user's creative call, so offer options, don't silently pick:
1. **Cold-open meme (beginning).** ~2s that frames the PAIN or the design
   progression — an expanding-brain of naive→clever, a relatable "when X…" — as
   ASCII/terminal text (NOT an image card) so it stays one continuous GIF. This
   is the scroll-stopping hook that buys the ~2s of retention infra content
   needs; the numbers can't hook, they can only pay off. Flows top-down like the
   narrative act, then the ONE clear into the data. Put the meme at the START,
   not the end — a hook works harder than a victory lap (an end meme is seen
   only by the people who already stayed).
2. **The data (middle).** The real live bench — the credibility core, unchanged.
3. **Flex + a mascot signature (end).** The headline result as the payoff,
   closed by a SMALL on-brand ASCII mascot beside the wordmark. Keep it tiny and
   tasteful — a big/cheesy mascot undercuts the credible numbers it follows.

If the user asks for pictured or recognizable meme characters, route the
opener to `demo`'s versus-scoreboard workflow. NEVER downgrade it to terminal
labels, emoji/emoticons, or generic archetype portraits and call that the
requested meme.

Worked example: `rsx-book/demo/bench-live.sh` — an expanding-brain `░▒▓█`
intensity ramp (naive `BTreeMap` → slab+compression, palette worst→best) cold-
open, the live depth-invariance bench, then the rsx mascot — the neutrino's
train `····▸ rsx` (invisible particle, only its wake shows) + the CTA.

Canonical reference SET (not just one crate): every RSX per-crate demo
(`rsx-book`, `rsx-matching`, `rsx-risk`, `rsx-cast`, `rsx-term` — each a
`demo/bench-live.sh` or `demo/pitch.py` + `demo/CLAUDE.md` + tracked
`<crate>-live-opt.gif`) runs this exact arc. Read that crate's `demo/CLAUDE.md`
first as the template before writing a new script. Detail in `lessons.md`
("RSX demo family").

## Failure details

Read `lessons.md` when implementing or debugging the recording. It contains
the exact `agg` width, GIF disposal, theme, palette, typewriter-height, RSX
demo-family, and reciprocal-chart failures behind the rules below.

## ALWAYS / NEVER
- ALWAYS re-run the bench and quote the CURRENT number — NEVER a remembered one.
- ALWAYS cite the exact bench file + test name and the commit/date it ran at
  in the project's `demo/CLAUDE.md` — NEVER a number with no traceable source.
- ALWAYS, on a NEW demo, suggest a cold-open meme + a small mascot signature and
  PROMPT the user for the copy/character — NEVER default to a bare bench dump.
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
- ALWAYS leave one empty bottom line in the final frame and keep the real
  terminal cursor hidden at exit.
- ALWAYS clear only at the narrative→data transition; NEVER recenter every
  claim like a slideshow.
- ALWAYS keep per-library copy, caveats, and regeneration steps in that
  project's `demo/CLAUDE.md`.
- ALWAYS track only the optimized `*-opt.gif`; NEVER track raw `.cast` or
  unoptimized GIF intermediates.
- ALWAYS write the project-specific reveal directly; NEVER build a generic
  framework around one-off pacing and copy.
