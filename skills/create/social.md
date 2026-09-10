# Social image — one square that survives the timeline

ONE PNG (or short GIF) built for the X feed. Two modes; pick by intent:

- **MEME** — humor-first, shareable. The joke is the point. Read § Meme.
- **EXPLAINER** — concept visualization: teach ONE idea clearly (code-shot,
  before/after, delta). The insight is the point. Read § Explainer.

NOT a print poster (portrait, dense — different job), NOT a thread, carousel,
full video, or landing page (`web.md`). A short looping GIF meme IS in scope
and preferred for reach (see § Render → GIF). Methodology + citations:
`social/references/research-social-meme.md` (+ `codex-critique.md`); the
one-line takeaway from the critique: **an image validates insight, not
styling — anti-slop aesthetics on a generic claim is still slop.**

**Verdicts from the go-from-rust project** (user-judged; bias toward the ✅):
- ✅ MEME, mascot/character gag (Ferris "very proper" vs gopher sprinting
  past) — landed, the proven path (a GIF of it beats the static version).
- ⚠️ EXPLAINER (code-shot / before-after) — experimental, so far BAD: read
  flat and un-shareable ("terrible"). Use only if the code genuinely IS the
  joke; expect heavy iteration.
- ❌ Portrait "poster" (multi-section / 3-card) — BAD/slop, rejected as
  "purest AI slop." Never ship one as a social image.

Default to MEME.

## § Gate 0 — anti-slop gate (both modes, do first)
Name the ONE thing the image carries, then anchor it to something REAL:
- EXPLAINER → a checkable artifact from the repo: real code/API, a diff, LOC,
  binary size, a benchmark, a command + its output. No artifact → marketing,
  not a post. Numbers must be reproducible, never round-and-vague ("scales to 100k").
- MEME → a recognizable, TRUE pain the audience has lived. If it isn't true,
  it isn't funny to them.
If you can't name the anchor, stop and find it before designing.

## § Shared craft (both modes)
- PNG, sRGB, self-contained (embed fonts/images as base64 — no network at
  render). Export at 2× (under X's ~4096px display cap), keep file < 5 MB
  (WebP re-encodes to JPG, so PNG for text-heavy graphics).
- **Timeline-safe aspect** (`social/references/x-image-dimensions.md`): a
  single image shows uncropped in-feed from 2:1 (landscape) to 3:4 (portrait);
  composer preview equals the timeline. EXPLAINER = 1:1, 1080×1080. MEME
  (portrait) = 4:5, 1080×1350 (safe, feed-dominating) or up to 3:4, 1200×1600
  for max height. NEVER exceed 3:4 (9:16 phone screenshots centre-crop). Never
  distort a template to fit — cover-crop its dead space instead.
- ONE accent color + neutral bg + near-white/black text, accent on the single
  key word/line only.
- Legibility: headline ≥ ~90px, smallest essential text ≥ ~40px on the 1080
  canvas (a feed thumbnail is ~500px wide), contrast ≥ 4.5:1 for essential
  text. **Thumbnail test:** view the PNG at ~500px / squint — is the one idea
  obvious in ~1s? If not, cut and enlarge (never shrink type to fit — see Rules).
- Match the project's palette if it has one (krons/kronael → dark mono, bg
  `#0a0e1a`, blue `#60a5fa`, amber `#fbbf24`, mono font — see the
  krons-brand-palette memory).
- Keep the SELLING off the image (no feature list / CTA / marketing) — that's
  what reads as an ad. A small footer with the project name + a short URL
  (what it is + where to get it) IS fine and helps discovery; the primary link
  still goes in the REPLY. Post native media. Write alt text transcribing the
  on-image words.

## § Meme
Use a REAL, recognizable meme template from a reservoir — never hand-roll a
typographic "text card" and call it a meme; that reads as fake and gets
rejected. The recognizable format IS the joke's delivery.
- **Reservoir:** memegen.link — free, no-auth template API, 214 templates
  (`curl https://api.memegen.link/templates`; fields: id, name, `lines`,
  `blank`). Good dev fits: `drake` (reject/approve), `ds` (two-buttons/daily
  struggle), `gb` (Galaxy Brain / expanding brain, 4 lines — the escalating-take
  format), `gru` (4-panel plan), `bus` (two guys on a bus), `cmm` (change my
  mind), `fine` (this is fine).
  imgflip is an alt: `curl https://api.imgflip.com/get_memes` lists the top 100
  templates with direct image URLs, no auth — only *captioning* needs an
  account, so use it as a second reservoir and caption locally like memegen.
- **Multi-panel templates: measure the panels, never assume equal slices.**
  Blanks with stacked panels (gb, gru) have uneven panel heights and black
  divider rules. Find the rules by scanning the blank's caption side for dark
  rows (`gb` is 600×848: captions in the LEFT half, art in the right, dividers
  at y≈211/428/626 — not quarters), then crop each art panel from the measured
  band.
- **Retarget a fixed-panel template by DROPPING a middle panel, never the last
  one.** Asked for 3 escalating tiers on the 4-panel `gb`, use panels 1, 2 and
  4: the final panel is the visual payoff and cutting it flattens the joke.
  Padding an unused panel with an invented tier is worse — it dilutes the
  punchline and pushes the canvas past the 3:4 crop limit.
- **Multi-character templates (IQ bell-curve / midwit, and similar): measure
  each character's bounding box by pixel-scanning the blank, then center each
  caption on that box's x-center, hugging a small fixed gap (~15-25px at
  source scale) directly above its topmost pixel.** "Find an empty zone near
  the character" is not enough — a caption placed in whatever whitespace is
  available (a top corner, a gap beside the curve) reads as randomly floating
  even when it technically avoids overlapping a face; the fix that actually
  reads as "this caption belongs to this character" is proximity + centering
  on the character's own geometry, not proximity to empty space. Scan for the
  darkest-pixel bounding box of each character in ISOLATION — a narrow x-range
  straight through their own body, not a wide region that also catches a
  neighboring label or a different character:
  ```python
  from PIL import Image
  im = Image.open("blank.jpg").convert("L"); px = im.load()
  def bbox(x0, x1, y0, y1, thresh=235):
      xs = [x for y in range(y0,y1) for x in range(x0,x1) if px[x,y] < thresh]
      ys = [y for y in range(y0,y1) for x in range(x0,x1) if px[x,y] < thresh]
      return (min(xs), min(ys), max(xs), max(ys)) if xs else None
  ```
  Then separately scan for the first/last dark pixel in each caption's target
  ROW BAND (scanning inward from each canvas edge) to find where a curve, axis,
  or label actually starts encroaching at that height — a character's bbox
  alone doesn't tell you that, since other art can intrude at a different y
  than the character's own top. Eyeballing coordinates from a rendered
  screenshot does not converge as reliably as measuring first, then rendering
  once to confirm.
  A caption whose ideal centered width would clip past the canvas edge (e.g. a
  character sitting near the left/right border) has two honest fixes: wrap to
  two lines at the SAME font size as the other captions (keep sizing uniform —
  mismatched caption sizes read as sloppier than one short wrapped line), or
  anchor the box toward the character instead of true-centering it, whichever
  wastes less of that character's own clear space.
- **Mascot/character memes** are a valid alternative to macro templates —
  stage the projects' mascots in a gag (e.g. Rust's Ferris, very proper,
  still proving soundness at the START line vs Go's gopher zooming past the
  FINISH). Use official/CC0 art so licensing is clean: **Ferris** —
  rustacean.net (CC0); **gophers** — github.com/egonelbre/gophers (CC0, has
  flying/running/superhero poses). The official Go gopher by Renée French is
  CC-BY-3.0 (needs attribution) — prefer the CC0 egonelbre set to avoid that.
  Record provenance even for CC0.
- **Scanned/hand-drawn art on a white background:** don't fight the white
  box — put that side on a light/white panel so it blends (a dark-heavy vs
  light-airy split can itself carry the joke). Only key out the white if you
  have Pillow/ImageMagick.
- **Anchor:** per Gate 0 — affectionate/self-deprecating, never punch down; a
  meme they retweet *about themselves* wins.
- **Pick the template that fits the joke** — never force a format onto an
  unrelated idea (the cringe failure mode). If no template fits, the idea
  isn't meme-shaped yet.
- **Copy:** ≤ ~15 words total. Specific > general — name the actual tool,
  error, or ceremony. Hyperbole is fine (it's a joke); the premise must be
  true or it gets roasted. NO hedges.
- **Truth test before shipping:** would the audience laugh *and* nod? If it
  only flatters your project, it's an ad, not a meme.
- **Render a clean meme (no watermark):** memegen stamps a watermark on
  rendered images, so composite the caption yourself:
  1. `curl` the template's **blank** image (the `blank` URL from the
     templates JSON), embed as base64.
  2. Overlay caption text in HTML: `font-family: Anton, Impact` (Anton woff2
     is a free Impact substitute —
     `https://cdn.jsdelivr.net/npm/@fontsource/anton/files/anton-latin-400-normal.woff2`),
     UPPERCASE, white fill, `-webkit-text-stroke: ~2px #000; paint-order: stroke fill`,
     centered over each panel's blank area.
  3. Frame to a timeline-safe aspect (§ Shared craft) — e.g. Drake's native
     ~9:14 is taller than 3:4 and would centre-crop; cover-crop the template's
     dead space onto the chosen MEME canvas, keeping every panel + caption
     inside the frame.

## § Explainer (concept visualization) — ⚠ EXPERIMENTAL, so far BAD
Teach ONE concept, clearly and beautifully. Rigor is the brand. In practice
this has produced flat, un-shareable results — prefer MEME unless the code
IS the joke.
- **Pick the hero element:**
  - **CODE-SHOT** — the code/API is the point. Syntax-highlighted mono on a
    dark card (Carbon/ray.so look), ≤ ~10 focused lines, one token/line in
    the accent.
  - **DELTA / BEFORE-AFTER** — a concrete change is the point. Two panels;
    muted "before", accent "after"; the delta (LOC, ms, deps, steps) is the
    largest element.
- **No strawman:** if you compare two things, write BOTH idiomatically — a
  skeptic will check. Fastest way to lose a technical audience.
- **Copy:** one-line caption stating the task/takeaway; ≤ ~20 words on-image
  excluding code. Concrete/falsifiable, project-specific. Kill marketing
  hedges ("helps", "designed to"); keep technical qualifiers (version,
  workload) — precision is not hedging.
- **Transferability test:** could a competitor paste their name into the
  caption? If yes, it's not specific enough.
- **Layout:** asymmetric, left-aligned/offset hero; never center-everything,
  never a three-card/pillar grid or gradient-glow bg (those ARE the AI-slop
  template).

## § Render (both modes)
Design at logical size, export at 2× (§ Shared craft). Prefer a real mono for
code (JetBrains Mono/Fira Code), embedded as base64.
- **Which renderer (researched):** this HTML→screenshot→Pillow path is the RIGHT tool for one-off, text/layout-heavy meme GIFs — CSS gives the best typography and Pillow's adaptive-palette GIF beats MoviePy/imageio for flicker-free loops. For smooth/longer motion, easing, or MP4, do NOT grow a MoviePy pipeline — route to `video/render.md`: Remotion keeps the same CSS/web-font typography and adds a declarative timeline (`interpolate`/`spring`) with GIF+MP4 export (paid tier for big orgs — verify before commercial use); Motion Canvas for pure vector; Manim for vector/math EXPLAINER animation.
- **Primary:** wrap the design in
  `.scale{transform:scale(2);transform-origin:top left}` sized to the box,
  then via the `browse` skill: `agent-browser set viewport 2160 2160` →
  `open file://…` → `screenshot out.png`. Proven; no deviceScaleFactor needed.
  Set the viewport to exactly 2× the design box so the shot needs no cropping.
  - **If every `agent-browser` command dies with `EPERM … chmod`,** its platform
    binary sits on a read-only mount and cannot mark itself executable. Copy it
    into the scratchpad and run that copy (the error message names the path, or
    resolve it):
    `cp "$(dirname "$(readlink -f "$(command -v agent-browser)")")/agent-browser-linux-x64" ./ab && chmod +x ./ab`
    Do this in the idempotent build script — it survives scratchpad resets.
  - Screenshot each variant with its OWN viewport height; a batch loop that
    reuses one height silently produces cropped or padded PNGs.
- **Alt:** `node social/render.mjs <in.html> <out.png> 1080 1080 2` (ships
  beside this file; playwright-core + system chromium via `CHROME=…`; WARNs
  on canvas overflow).
- **GIF (animated meme, no ffmpeg needed):** author the animation as an in-page
  pure **`seek(frame)`** JS function — it deterministically sets every element's
  state (position, rotation, caption, opacity) for a given frame index. Keep it
  a PURE function of the frame — NO `requestAnimationFrame`/wall-clock during
  capture, or screenshots race the clock (a RAF loop calling `seek` is fine for
  LIVE preview only). This makes the HTML self-contained + previewable and the
  capture driver dumb; it's the lightweight version of Remotion's frame=f(time).
  Capture: `open` once, then loop `agent-browser eval "seek(N)"` → `screenshot
  frame_NN.png`. Encode with Pillow via `uv run --with pillow python`: ONE shared
  adaptive palette (`master = frames[mid].quantize(colors=128)`, then
  `f.quantize(palette=master, dither=NONE)` per frame — avoids flicker) →
  `pal[0].save(out, save_all=True, append_images=pal[1:], loop=0, duration=<list>, disposal=2, optimize=True)`.
  ~720px (or a short 16:9 for horizontal action — no dead vertical space), keep < 15 MB (X GIF cap). Ship a matching still PNG (a mid-action frame) too.
  - **Choreograph, don't just slide:** stagger it — one mascot acts, the other enters at the midpoint (e.g. Ferris scuttles, THEN the gopher rockets past). Add a walk bob (small per-frame `top` offset) so a static mascot reads as moving. Let props REACT to the action — the blast knocks the crab's hat off — reactions sell impact. Freeze a bystander once the fast action starts (a mascot that keeps moving at the fast frame-rate looks like it sped up — bad).
  - **Two-beat caption:** swap the text at the turn for a setup→punchline (e.g. "you already know the hard part" → "now ship it faster" as the gopher launches). BLINK a key word (red, on/off alternating frames) several times — ≥5, starting on frame 0 through the setup, not one flash. Set per-frame via `eval` rewriting `.cap` innerHTML / element styles.
  - **Flutter baked-in detail (cape, flag) cheaply:** alternate a transform between TWO values on odd/even frames ("two rotations blinking") — a ~4–6° rotation swing per frame reads as flutter without separating the art.
  - **Pace with per-frame duration — timing carries meaning.** Pillow `duration` takes a LIST (ms per frame). Make the setup labored (long frames, e.g. ~260ms — evokes slowness) and the payoff snappy (short, e.g. ~45ms — evokes speed); a slow blink is a slow beat, a fast shimmer is a fast one. Same frames, opposite feel.
  - **Frame 0 = the static poster.** X (and any no-autoplay view) shows the first frame as the still, so frame 0 must be a strong standalone (setup line + one mascot), never a blank or mid-transition frame. Ship a matching still from a mid-payoff frame separately.
- The session scratchpad RESETS between turns — write the whole render as ONE idempotent script (re-fetch fonts/art if missing, re-copy the agent-browser binary, inject base64, render frames, assemble) so a reset never loses work. Assets embed as base64; nothing depends on prior-turn state.
- **Iterate in BATCHES — NEVER one-at-a-time.** EARLY (divergent) phase: generate ~10 variants across DIFFERENT concepts / styles / templates / layouts — maximise variance so the widest field is on the table, not 10 tweaks of one idea. LATER (convergent): 4–6 variants sweeping the parameters in play (size, tilt, timing, colour, caption) around the chosen direction. Read the batch together — a grid converges far faster than edit→render→ask→repeat. Number variants 0–9 within a round; name the surviving pick as a growing digit-string — ONE digit per round (e.g. `meme-2233.gif` = round1 #2, round2 #2, round3 #3, round4 #3). Keep the whole tree under gitignored `tmp/`.
- ALWAYS iterate on the rendered PNG/GIF (Read it), never on the HTML in
  your head.

## § Rules
- ALWAYS pass Gate 0 first (artifact for EXPLAINER, true pain for MEME).
- ALWAYS one idea, one accent; run the thumbnail test; link in a reply.
- NEVER a three-card grid, gradient-glow, or centered-everything layout (slop).
- NEVER a strawman comparison (EXPLAINER) or a false/forced-template premise (MEME).
- NEVER shrink type to fit — cut words instead.
