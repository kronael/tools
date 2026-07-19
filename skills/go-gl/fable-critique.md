# Fable critique of `research-glgo.md` — the design/UX lens + what codex missed

Second adversarial pass. Codex owned the engineering lens (threading, cgo,
present modes, testing); this pass attacks the design/experience half, adds
holes codex did not find, then prioritizes everything into the rule list a
<200-line skill must keep, and splits the reference bugs into fix vs document.

Method: contrast ratios below are computed (WCAG relative-luminance formula)
from the actual palette in `rsx-glass/grid.go` and the tier math in
`rsx-glass/heat.go`; the goldens (`rsx-glass/soft/testdata/*.png`) were
inspected as images; the go-webgpu claim was checked against the live
repositories. Codex findings are numbered 1–25; new findings here are 26–35.

---

## 1. The design half of the doc is the weak half

§2 of `research-glgo.md` is a citation tour — GNOME/Apple/Fluent, Rams, Tufte,
Nielsen, Refactoring UI — and almost none of it changes what you build. "Layout
is adaptive", "hierarchy from size/weight/colour", "minimalism is a heuristic"
are true of every desktop app ever; a designer reads that section and learns
nothing they'd act on. Worse, the one *specific* design claim it makes about the
reference is **false in the rendered pixels** (findings 26–27). The doc quotes
the design system's slogans (`grid.go`: "colour is meaning, never decoration")
and never checks whether the render obeys them.

What the section is missing is exactly what a *data-dense* app needs and what
generic HIGs don't cover: scale stability under live data, the graphical-
perception channel hierarchy (position > length > luminance > hue — Cleveland &
McGill, the one piece of citable design science that decides encodings, absent
from a doc that cites Tufte twice), reserved contrast pairs, tabular numerals,
and freshness display. Those are §3 below.

### The actual experience (reading the goldens as a designer)

`soft/testdata/heatmap.png` — the image README.md calls "proof the visual
system rebuilds from spec" — reads as:

- **A flat green blob.** The log tier (`logTier`, `heat.go`) maps a 1,500-lot
  level and a 10,500-lot level to the *same* tier 2, and 40k and 110k to the
  same tier 3; with per-frame-max normalization the whole occupied book sits in
  tiers 2–4 (50–100% blend). The advertised "dark (thin) → bright (walls)"
  gradient collapses to ~3 visible states; the bid/ask *walls — the single most
  important feature of a liquidity heatmap — are not findable in the picture.*
- **Invisible texture.** The count-density glyphs (`░▒▓█`) and the persistence
  mark `▚` are imperceptible in the golden (see finding 26/27 for why, with
  numbers). The doc's claimed "second channel" exists in code and not in
  perception.
- **Unreadable numbers.** The footer ladder prints raw i64 fixed-point
  (`fmtPx`/`fmtQty`, `heat.go`) — `10008x232905` — no tick/lot scaling, no
  grouping, no fixed width, so ladder text changes length (and layout jumps)
  as prices tick. The only exact numbers on the screen are the hardest thing
  on it to read.
- **A postage stamp.** 72×24 cells at 8×17 px = a 576×408 window, hinted 14pt/
  72dpi text, `Resizable=False` (`gpu/gpu.go:220`). On a 163-dpi 4K panel
  that's ~6pt effective text in a window you cannot enlarge. The "responsive
  desktop app" reference is, experientially, a fixed thumbnail.

`degraded.png` is an entirely blank page with an amber "offline". Honest, but
see finding 35: mid-session staleness (the case that matters) keeps painting
last-known data with only the header dot flipped.

---

## 2. What codex missed (findings 26–35)

26. **The shape channel is invisible at exactly the cells that matter.**
    `bookCell` (`heat.go`) sets glyph fg to `rampColor(clampTier(sz+1))` on bg
    `rampColor(sz)`. At the top tier, `clampTier(sizeTiers+1) == sizeTiers`, so
    **fg == bg — contrast 1.00:1 — and the density/persistence glyph on a wall
    is literally rendered in its own background colour.** The `▚` persistence
    mark, whose whole purpose is flagging long-standing *large* liquidity,
    vanishes on walls by construction. A one-line encoding bug the goldens
    happily locked in (they assert stability, not visibility).

27. **The doc's WCAG claim is refuted by its own reference.** Research §2 says
    rsx-glass obeys WCAG 1.4.1 because glyph shape is a redundant channel.
    Computed: every fg-on-bg glyph pairing on the ramp is 1.77–2.23:1 — all
    below the 3:1 non-text minimum (WCAG 1.4.11) — and adjacent bg tiers are
    ~2:1, so the ramp steps themselves don't reliably separate. And trade
    **side** (buy/sell aggressor) is encoded by hue alone — the *same* shape set
    `○◆●■` in `Live` green vs `Ask` red (`bookCell` + `aggressor`, `heat.go`) —
    the textbook deuteranopia trap, a literal 1.4.1 violation. Shape encodes
    magnitude, not side; the doc conflates the two. (Distinct from codex #22,
    which was about the missing accessibility tree.)

28. **Per-frame autoscale = a strobing map, and the whole test protocol is
    temporally blind.** `bases()` (`heat.go`) normalizes the ramp to the
    current frame's max, so one large order landing or cancelling re-brightens
    or re-dims *every cell on screen* at once. The code comment admits rsx-term
    uses a slow-decaying basis "to stop the map strobing" and punts it to v2 —
    but neither the research doc's design section nor codex names **scale
    stability** as a rule at all. Deeper: goldens and parity are all
    single-frame; strobe, shimmer, and layout jumping — the worst UX defects of
    a live data app — are invisible to every test in the protocol. A sequence
    golden (N frames of the deterministic Synth, assert bounded inter-frame
    change) is the missing test class.

29. **The cell grid is an inherited ceiling sold as a GPU payoff.**
    `SPEC.md` promises "arbitrary resolution … scale to high refresh"; what the
    GPU actually renders is the same 72×24 = 1,728 cells as the terminal, drawn
    as 8×17 constant-colour blocks — the information resolution of a 1985
    terminal at any monitor size. The doc's §1 verdict bakes "the seam is a
    plain-data cell grid" into the skill as *the* primitive. For text/status
    screens a cell grid is right; for the heatmap plane itself (a continuous
    price×time field) the GPU's actual payoff is sub-cell resolution — per-datum
    instances or a data texture. The skill must teach *primitive follows data
    topology*, or it teaches everyone to build chunky terminal emulators.
    (Sharpens codex #24 from the design side.)

30. **The "go-webgpu is one package swap" claim cites an archived project and
    is unproven by construction.** [rajveermalviya/go-webgpu](https://github.com/rajveermalviya/go-webgpu)
    was archived March 2025 (read-only); the maintained lineage is
    [cogentcore/webgpu](https://github.com/cogentcore/webgpu). And the seam has
    never held a second *windowed* backend: `soft` proves the Grid contract,
    not the windowing/DPI/event surface a webgpu backend must also replace
    (window creation, swap-interval knob, and event pumping currently live
    inside `gpu/`, not behind `Renderer`). Downgrade to "designed for,
    unproven", and name the maintained fork.

31. **sRGB consistency is load-bearing and stated nowhere as a rule.** Parity
    holds *only* because both renderers blend in non-linear sRGB (`soft.lerp`,
    `soft/soft.go`; "soft's straight-sRGB blend", `gpu/pipeline.go` fragment
    shader) and no sRGB framebuffer is used. Follow standard GL advice — enable
    `GL_FRAMEBUFFER_SRGB` or allocate an sRGB FBO — and the GPU silently
    linearizes while soft doesn't: parity breaks, goldens don't. The skill
    needs one explicit line: pick ONE colour policy (author sRGB, blend sRGB,
    no sRGB framebuffer — or go linear end-to-end) and never mix. Codex #18
    grazed "color management" but missed that the *absence* of GL colour
    management is a deliberate, fragile invariant here.

32. **Linux-desktop reality: Wayland.** go-gl/glfw builds the X11 backend by
    default; on today's Wayland-default distros the app runs under XWayland,
    where fractional scaling blurs exactly the crisp 1:1 pixel text this whole
    methodology exists for (a `wayland` build tag exists and changes the build
    matrix — grazes codex #7, but the *runtime UX* consequence is unstated).
    One sentence in the skill prevents a "why is my text blurry on Fedora" day.

33. **Zero desktop citizenship.** No keyboard input at all (not even Esc/q to
    quit — the close button is the app's entire input surface, and codex #8
    shows even that breaks without a feed), no window icon, no WM_CLASS/app_id,
    no .desktop entry — alt-tab shows an anonymous window. The doc's
    "keyboard-first" guideline (§2) has literally no grounding in the cited
    reference. Fine as v1 scope; not fine unstated.

34. **The exemplar's own docs are internally false.** The skill will cite these
    files as the model of crate documentation, and: `rsx-glass/CLAUDE.md` says
    the reuse is `replace rsx-term => ../rsx-term` but `go.mod` says
    `rsx-core => ../rsx-core`; `SPEC.md`'s layout lists a root `main.go` that is
    actually `cmd/glass/` (plus an empty committed `cmd/rsx-glass/` dir);
    `atlas.Version` claims "the goldens are pinned to it" and is referenced
    nowhere; `README.md` states parity "must match … measured maxDiff = 1
    level, no channel off by more than 1" while the test gate is 6 (extends
    codex #20 into the docs). Doc drift in a doc-topology exemplar is a
    self-defeating citation.

35. **No freshness at the point of reading.** When the feed dies mid-session,
    `Feed` keeps its last state and `Compose` keeps painting it: last-known mid
    in full `Text` colour, heatmap unchanged — only the header dot flips. The
    honesty rules (`~` estimate, `—` unknown) cover *absence*, not *age*. A
    data-dense screen needs staleness where the eye is (mid dims / gets `~`
    after N ms without an update), not in a corner. Codex #25 named
    "freshness/status visibility" as an abstract gate; this is the concrete
    hole in the reference.

---

## 3. The design rules that actually change the build

Replace research §2 wholesale with these six. Each is specific to data-dense
desktop apps, testable, and violating it produces a broken screen — the test
generic HIG material fails.

- **D1 — Stable scales.** Ramp/axis references decay slowly or pin; NEVER
  re-normalize to the current frame (else the whole screen strobes on every
  data spike). Requires carrying reference state across frames — a model API
  decision, not a styling one. (Finding 28.)
- **D2 — Channel hierarchy.** Exact values are text; magnitudes are
  length/position (the NOW-row micro-bars are the reference doing this right);
  luminance is overview texture only; hue is category only — never magnitude,
  and never a category's *sole* carrier. (Findings 27, 29.)
- **D3 — Reserved contrast pairs.** Every glyph fg is a palette colour with
  ≥3:1 against every bg it can sit on; NEVER derive fg as "bg one tier up".
  This is unit-testable: iterate the palette×ramp matrix, assert contrast — a
  cheap test that would have caught findings 26 and 27 mechanically.
- **D4 — Fixed-width, unit-scaled numbers.** All comparable numbers are
  tabular and tick/lot-scaled at the edge; a number that changes width per
  update makes the layout jump per update.
- **D5 — Freshness at the point of reading.** Data that stops updating must
  visibly age in place; degraded states keep last-known data marked stale,
  never a blank page. (Finding 35.)
- **D6 — Primitive follows data topology.** Cell grid for text/status planes;
  per-datum instances or data textures for continuous fields; the terminal's
  cell is a compatibility layer, not your resolution cap. (Finding 29.)

---

## 4. The keeper rules — ranked, for the <200-line skill

Codex #25 is right: cut the thesis defense, the `tsx` analogy, the
bibliography prose. These twelve survive, in this order; each one, violated,
ships a broken or janky app:

1. **ALWAYS** lock the startup OS thread in the composition root and keep every
   GLFW lifecycle/event call and (single-window) GL call there — one owner,
   locked once; library constructors assert, never lock. (codex 3/4/5)
2. **ALWAYS** process window events every loop iteration, independent of data —
   a window that cannot close or repaint while the feed is down is broken.
   (codex 8)
3. **ALWAYS** keep the three coordinate systems separate: framebuffer pixels →
   `glViewport`; window coords × content scale → layout and font size; and
   handle 0×0 (minimized) plus scale changes from resize callbacks, coalesced
   to a frame boundary. (codex 2/9/21)
4. **ALWAYS** hold newest-state in a slot that overwrites the *old* value
   (drain-then-send or atomic pointer), and pick exactly one pacer — blocking
   swap or a timer, never both. (codex 13/14)
5. **ALWAYS** keep the render path steady-state alloc-free and gate it with
   `AllocsPerRun == 0` scoped to what you actually claim — per shipping
   backend, stated exclusions. (codex 15/16)
6. **ALWAYS** put every GPU/windowing import behind one interface package with
   a grep-enforced boundary, and keep a pure-Go software renderer that builds
   and tests with `CGO_ENABLED=0`. (research §3 + codex 7)
7. **ALWAYS** hold the GPU backend to the software reference by pixel parity,
   in at least one required CI job that FAILS (not skips) without a context,
   at the tolerance you measured — not a slacker one. (codex 19/20)
8. **ALWAYS** pick one colour policy — author sRGB, blend sRGB, no sRGB
   framebuffer (or linear end-to-end) — mixing the two silently breaks
   soft/GPU parity. (finding 31)
9. **NEVER** re-normalize a live ramp or axis per frame; scale references decay
   or pin. (finding 28 / D1)
10. **NEVER** let hue be a meaning's only carrier, and **NEVER** pair glyph fg
    with an adjacent-tier bg — every fg/bg pair ≥3:1, asserted in a palette
    unit test. (findings 26/27 / D3)
11. **ALWAYS** render exact values as fixed-width unit-scaled text, magnitudes
    as length/position, luminance as overview only. (D2/D4)
12. **ALWAYS** show freshness at the point of reading — stale data ages in
    place; degraded states keep marked last-known data. (finding 35 / D5)

Cut without mercy: the one-skill-or-two verdict, Rams/Tufte/Nielsen name
checks, response-time folklore, MSDF history, dark-mode aside, GC-marketing
paragraphs, and every repeated statement of the seam and alloc claims.

---

## 5. rsx-glass: fix vs document (for the opus rectify pass)

The split criterion: **fix what the skill will cite as a canonical pattern**
(a reference that contradicts its own rule teaches the bug), **document what is
honest v1 scope** (and make the docs say so out loud).

### Fix (before the skill cites it)

1. **Coalescer keeps the OLD grid** (codex 14): `publish` in
   `cmd/glass/main.go` must drain-then-send so the *new* grid wins. ~3 lines;
   this is the skill's centerpiece "newest-state" pattern and it is currently
   backwards.
2. **Events only pump inside `Present`, which never runs before the first
   grid** (codex 8): make the loop pump events unconditionally (event pump in
   `glass.Run`'s tick arm via the renderer, `Present(nil)`-tolerant or a
   separate `Pump()` on the windowed backend). The word "responsive" in the
   skill title demands this one.
3. **Wall-glyph fg==bg** (finding 26): stop deriving glyph fg as `tier+1`;
   give glyphs a reserved contrasting colour at the top tier (encoding change →
   re-bless goldens deliberately, per the crate's own re-bless rule).
4. **Parity tolerance vs measurement** (codex 20 + finding 34): gate at the
   measured `maxDiff <= 1`, delete the unreachable `over8` assert, and make
   `README.md`'s numbers match the test.
5. **Resizable, the honest minimum** (codex 1): drop `Resizable=False`; set a
   minimum size; letterbox the fixed grid at an integer atlas multiple,
   centred, from framebuffer size. True reflow (re-deriving W×H) stays v2 —
   but a never-resizable window cannot anchor a "responsive" skill, and the
   letterbox exercises the window-vs-framebuffer split the skill teaches.
6. **Lock/lifecycle ownership, cheap part** (codex 4/5): remove
   `runtime.LockOSThread` from `gpu.New`/`NewOffscreen` (assert or document
   instead — the root already locks), make `Close` idempotent, and state that
   `glfw.Init`/`Terminate` are process-global (one windowed renderer per
   process in v1).
7. **Doc drift** (finding 34): `rsx-term` → `rsx-core` replace line in
   CLAUDE.md, SPEC layout → `cmd/glass/`, delete empty `cmd/rsx-glass/`, wire
   `atlas.Version` into the golden filenames or delete it, quit-key note.
8. *(Cheap, optional)* **Esc/q to close** via a key callback — four lines that
   give "keyboard-first" its first grounding.

### Document as v1 limitations (in SPEC.md "known v1 deviations" + README)

- **Per-frame autoscale strobe** (finding 28): already admitted in a `heat.go`
  comment; elevate to SPEC, name rsx-term's decaying basis as the v2 fix, and
  make sure the skill's rule cites rsx-term's behaviour, not glass's.
- **Hue-only trade side** (finding 27): the visual language is rsx-term's
  ("rsx-term is the template — ALWAYS"); fix belongs upstream in
  `rsx-term/VISUALS.md` first, then flows down. Document, don't fork the
  language here.
- **Fixed 14pt/1x atlas, no HiDPI text** (codex 21): document that letterboxed
  integer scaling is crisp-chunky by design; size-bucketed atlases per content
  scale are v2.
- **Cell-grid resolution ceiling** (finding 29): state that v1 deliberately
  renders the terminal's picture; sub-cell data planes are the actual GPU
  payoff and are v2.
- **go-webgpu swap** (finding 30): reword to "designed for, unproven"; cite
  cogentcore/webgpu (maintained) instead of the archived rajveermalviya repo.
- **Wayland/XWayland scaling** (finding 32): one README line.
- **Mid-session staleness display** (finding 35): v2, needs clock plumbing
  through `Scene`.
- **No accessibility surface** (codex 22): pixels-only canvas; name the
  boundary rather than implying WCAG coverage.

Sources for finding 30: [rajveermalviya/go-webgpu](https://github.com/rajveermalviya/go-webgpu)
(archived 2025-03-20), [cogentcore/webgpu](https://github.com/cogentcore/webgpu).
