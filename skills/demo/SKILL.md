---
name: demo
description: Terminal demo GIF + MP4 recordings for READMEs and social (asciinema + agg + ffmpeg). NOT for general Makefile targets (use software) or GUI screenshots (use visual).
when_to_use: "record a demo, make demo, demo gif, demo mp4, demo video, asciinema, agg, terminal recording for README or twitter"
---

# Terminal demo recordings

Part of the `create` creative-skill family — this skill owns terminal recordings
and animated narrative shorts (see `cutout.md`).

Standard recipe: `asciinema` records a driven terminal session to a
`.cast` file, `agg` renders that to a `.gif` committed under the repo
and embedded in `README.md`. For social (Twitter/X), also transcode the
gif to an `.mp4` — autoplays, far smaller, and the only format some
platforms accept.

## Type the commands (self-narrating demos)

The strongest demos show *how* each result is produced: echo a shell
prompt and the command being typed, then run it, with a one-line `#`
comment before each step saying why. A viewer should be able to reproduce
the whole thing from the recording alone. Pattern (bash driver):

```bash
type_run() {                       # print "$ ", type the command, run it
	printf '\033[1;32m$ \033[1;37m'
	local i; for ((i=0; i<${#1}; i++)); do printf '%s' "${1:i:1}"; sleep 0.028; done
	printf '\033[0m\n'; sleep 0.9; eval "$1"
}
note() { printf '\n\033[1;36m# %s\033[0m\n' "$*"; }   # cyan narration
```

Gate the per-char delay behind an env var (`DEMO_TYPE=1`) so `make demo`
runs instantly for humans but types out char-by-char when recording.
Keep background scaffolding (starting mocks/servers) narrated, not typed —
type only the commands that are the point.

## Makefile targets

Real file targets with real prerequisites — never one phony blob, so
`make demo` skips the recording when the cast is already fresh and only
re-renders the gif:

```makefile
.PHONY: demo

tmp/demo.cast: demo/run.ts
	mkdir -p tmp
	COLUMNS=80 LINES=30 asciinema rec tmp/demo.cast --overwrite --cols 80 --rows 30 -c 'bun run demo/run.ts'

demo/demo.gif: tmp/demo.cast
	agg --theme solarized-light --font-size 16 \
	    --cols 80 --rows 30 \
	    --idle-time-limit 3 --last-frame-duration 8 \
	    tmp/demo.cast demo/demo.gif

demo/demo.mp4: demo/demo.gif
	ffmpeg -y -i demo/demo.gif -movflags faststart -pix_fmt yuv420p \
	    -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2' demo/demo.mp4

demo: demo/demo.mp4
```

`-pix_fmt yuv420p` and the even-dimension `scale` are mandatory — most
players (and Twitter) reject odd dimensions or non-4:2:0 chroma. Commit
both `demo.gif` (README embed) and `demo.mp4` (social upload).

Reference implementation: `rig/Makefile`.

- ALWAYS drive the recording from a checked-in script (`demo/run.ts`,
  `demo/script`), never manual typing — reproducible and re-runnable.
- ALWAYS put the `.cast` intermediate in `tmp/` (gitignored); ALWAYS
  commit the final `.gif` under `demo/` next to its driving script.
- NEVER flatten `demo` into one phony target — split cast-recording from
  gif-rendering as separate file targets so Make can skip either.
- ALWAYS match `--cols`/`--rows` between `asciinema rec` and `agg` — a
  mismatch crops or letterboxes the gif.
- NEVER copy `--idle-time-limit`/`--last-frame-duration` verbatim —
  ALWAYS tune per demo, they trim dead pauses in the recording.
- If the narrative claims an API exposes something, show a real `curl`
  request to that endpoint and its result. Filtering with `jq`, `grep`, or a
  small named helper is fine when the raw response is too large, but do not
  replace real endpoints with invented demo objects.

## Composed demos (opener still → terminal cast → closing still)

For a PLAIN (non-themed) shareable/social gif — no character, no narrative
world, just product + proof — leading with a title-card and ending with a
take-home line is fine. Don't hand-roll frame capture — record the terminal
with asciinema, render with agg, and concat design cards on either side via
ffmpeg. (If the short has a theme — a paper world, a character, any medium
with its own visual language — this pattern does NOT apply for the closer:
see "One themed world, entered once, exited once" below.)

- Build the opener/closing as HTML cards at the SAME canvas size as the terminal
  gif. Match the cast's cols×rows×font aspect (e.g. 90×30 @ font-18 ≈ 980×768) so
  the terminal segment barely scales and nothing letterboxes; screenshot each
  card to a PNG (`agent-browser screenshot body card.png`), commit under
  `demo/assets/` (design assets, not regenerated per run).
- A `demo/compose.sh` holds each card ~2.5s, scales the terminal gif to the
  canvas, concats, palette-optimizes the gif (`palettegen`+`paletteuse`,
  `fps=10`, bayer dithering keeps flat-color gifs small), then gif→mp4
  (`-pix_fmt yuv420p`, even dims).
- Make the driver REPRODUCIBLE: replay real recorded data (an action sequence,
  `results.json`) through the ACTUAL code — never call a live API/LLM from the
  demo, or the `.cast` can't be rebuilt from a clean tree.

### Animated narrative shorts (Canvas beats → capture → mixed compose)

For a story/character piece (not just static cards), animate in Canvas and
capture deterministically. For a specific reusable look, read `cutout.md` —
**Monty Python cutout**, real photo pieces with hinged jerky motion (its rig
is this medium's instance of `create/SKILL.md` § Principle: graph as data,
then render):

- One self-contained HTML exposing `window.renderFrame(t)`, `t∈[0,1)`, a seamless
  loop, with **seeded** randomness so frame `t` is reproducible (never
  `Math.random()` per call — it breaks frame-exact capture). Storyboard the beats
  as `t`-ranges.
- Capture with Playwright headless (`chromium-headless-shell`, cached at
  `~/.cache/ms-playwright`, works with the command sandbox ON): loop
  `page.evaluate(t => renderFrame(t), i/N)` and screenshot each to
  `tmp/<name>_frames/` (a per-demo dir — two concurrent captures sharing
  `tmp/frames` clobber each other), then ffmpeg palettegen/paletteuse → gif.
- **Mix media, keep the real parts real.** Compose stills/animation with a real
  asciinema cast of the product running (the "germinal" pattern). The terminal is
  ALWAYS the real cast; narrative beats are best as real sourced imagery (meme,
  photo) over hand-drawn Canvas. ffmpeg-concat all segments at ONE canvas size
  (record the cast at that size) so the terminal never scales/letterboxes.

### Publication-grade bar (the designer's test)

A first render that "looks fine" is not done. Iterate: extract frames from every
beat, **Read them, and critique like a designer** — proportions, color harmony,
contrast, spacing, silhouettes (no blobby art) — then fix and re-render. But the
MAKER never signs off — gate ship on an INDEPENDENT critic per `create/SKILL.md`
§ Quality gate. Two specifics that repeatedly fail the bar:

- **Terminal beats must be a REAL recording, raw.** NEVER Canvas-mock a terminal,
  and NEVER draw window chrome (title bar, traffic-light dots, rounded frame) — a
  dressed-up terminal reads as a web viz and fails the "is it real?" test. ALWAYS
  record the program with asciinema; for a deterministic beat replay recorded
  data (`run.jl`) through a styled truecolor-ANSI renderer — designed tiles, a
  tasteful value→color ramp, near-black theme, cursor hidden, empty cells still
  framed (never a "broken" board), terminal sized to content (`--cols`/`--rows`).
- **Recognizable references: use the real image, NEVER a hand-drawn copy.** Fetch
  the real meme/photo and compose it (crop, re-caption) — a Canvas imitation
  reads cheap. Reserve hand-drawn Canvas for original characters; clean confident
  shapes beat detailed-but-blobby.

A sparse sample tile (every Nth frame) catches gross beat-level problems but
CAN MISS a hairline defect that's present in every frame — a 1-2px seam reads
as noise at thumbnail scale and only shows up in a full-resolution crop at the
suspect boundary (a clip edge, a layer join). When something is contact-sheet
"fine" but feels off, contact-sheet ALL frames (not a sample) at once, or crop
tight and zoom on the specific seam/edge across a few frames spanning the
motion range — a static-looking artifact can still change (or vanish) as
things rotate relative to each other.

The **`visual` agent** is the right tool for this iterate-render-critique loop.

### Environment gotchas (hard-won)

- **`agg`'s prebuilt `-gnu` release is glibc-pinned — use the `-musl` release
  instead of downgrading.** `agg-x86_64-unknown-linux-gnu` (v1.9+) needs
  `GLIBC_2.38`; on an older box (Debian 12 = glibc 2.36) it fails with
  `GLIBC_2.38 not found`. Don't vendor an old agg version to dodge this — grab
  `agg-x86_64-unknown-linux-musl` from the SAME latest release
  (github.com/asciinema/agg/releases/latest/download/agg-x86_64-unknown-linux-musl),
  `chmod +x`, done: a static musl binary has no glibc dependency at all, so you
  keep the current version instead of pinning old.
- **`agg` font-size ↔ output-dimension math.** Output width ≈ `cols × font-size
  × ~0.6` (a DejaVu Sans Mono cell is ~0.6 chars wide per pt); output height =
  `rows × font-size × line-height`. e.g. 72 cols × font-size 20 ≈ 888px wide;
  28 rows × 20 × 1.4 ≈ 812px tall. Solve this BEFORE recording so the cast's
  `--cols`/`--rows` land on the canvas size the compose already uses — avoids a
  second resize pass (which softens crisp terminal text).
- **Recording needs the command sandbox OFF.** `asciinema rec` needs a real pty
  and `agent-browser` needs a writable socket dir — both fail sandboxed. Install
  asciinema with `uv tool install asciinema`.
- **`uv run` may fail on a read-only uv cache under the sandbox** — record with
  `.venv/bin/python` directly to dodge uv, or disable the sandbox for the `uv`
  invocation.
- **Real-image assets: outbound HTTPS usually works** (via a proxy even on
  locked-down sandboxes) — `curl`/WebFetch pull memes/photos. Wikimedia 400s
  without an allowed thumb width. Save sources under `demo/assets/` and
  regenerate the matted/posterized cutouts from them via a checked-in asset
  script (reproducible, never hand-edited).
- Split targets `cast → terminal.gif → gif+mp4`; group the two final outputs
  with GNU Make 4.3 `&:` so a no-op rerun skips work.

## Pacing and transition patterns

- **Announce, then realize.** For a beat that reports a discrete decision
  (a move, a step, a diff), don't paint the result in the same frame as the
  intent — show the intent FIRST against the still-unchanged prior state (e.g.
  "MOVE 3/5 → LEFT" over the board as it stood before the move), hold briefly,
  THEN update the state to reflect it. One frame carrying both intent and
  result reads instantly but doesn't let the viewer register the decision;
  splitting it into two beats makes each step legible without slowing down
  the aggregate pace much (each beat can still be well under a second).
- **Crossfade an end card whose background matches the prior beat's
  background**, rather than hard-cutting into a held static frame — for a
  PLAIN, non-themed demo only (see below for a themed short). If the terminal
  beat's bg is `#0f130f`, make the end card the SAME `#0f130f` — the wordmark
  then dissolves INTO the frame it's replacing (materializes) instead of the
  viewer perceiving a scene change. A card with a different bg always reads
  as a hard cut even under a crossfade, because the whole frame changes color
  at once.

### One themed world, entered once, exited once

A themed narrative short (a paper-cutout world, a character, any medium with
its own visual language) must END INSIDE THAT WORLD — never crossfade or cut
to a flat title-card in a different language (a plain dark background +
sans-serif wordmark) just because the colors match. However well the bg color
is matched, a flat card is a THIRD visual world the viewer has never seen
before; it reads as leaving the story to show a poster, undoing the very
immersion the theme built. (Caught late: an earlier germinal cut shipped
exactly this — cut-paper farmer/flytrap opener, real terminal proof, then a
crossfade to a plain `#0f130f` + sans-serif "schema" wordmark card. The fix
was NOT a better crossfade; it was building the closer as a THIRD paper beat —
same rig, same asset pipeline, a payoff sprout growing into cut-paper letters —
so the short never leaves its own world.)

- **Keep the whole short to the fewest deliberate worlds.** Two is usually
  right: the themed medium (carries the joke/story) and one real proof (a raw
  terminal recording, a real screenshot) — never a third "generic demo card"
  language bolted on for the ending. If you can't build the payoff in the
  theme's own medium, that's a sign the short doesn't need a title card at
  all (a hard cut to black and out is more honest than a mismatched card).
- **A themed closer can reuse the opener's rig instead of a new scene.** One
  HTML rig can serve two non-adjacent beats (opener + closer) by giving the
  same PARTS/TRACKS a second frame range — capture the two ranges into
  separate gifs (the frame-index capture driver takes an explicit index list,
  not just `0..N`) and let the real proof sit between them in the compose
  script. This guarantees the closer matches the opener's grade/grain/shadow
  exactly, because it *is* the opener's asset pipeline, not a re-creation of it.
- **A themed medium can still spell out words without breaking its rules.**
  You don't need a photo of text to stay "in medium" — construct letters the
  same way you'd construct any non-photographic paper piece already in the
  rig (a flat-color cut shape + the same dark ink-edge stroke + the same
  drop-shadow direction as everything else): render bold glyphs, colorize,
  ink-edge the WHOLE word as one silhouette (one rim around the word, not one
  rim per letter — six separately-inked letters read as stickers, not a sign).
  Tying the wordmark's colors to another beat's palette (e.g. the same
  value-ramp hex stops the terminal's tiles use) makes the payoff rhyme with
  the proof beat instead of needing a tagline to explain the connection.
