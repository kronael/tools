# Building responsive, minimal OpenGL desktop apps in Go — a methodology

Research raw material for a `glgo` skill: the Go-desktop-GL analogue of the web
`tsx` skill. It fuses two bodies of public best practice — *desktop design
discipline* and *go-gl build patterns* — and grounds both in a real working
reference in this repo, `rsx-glass/` (a GPU renderer for a data-dense trading
heatmap). Every claim is tied to a named source.

**Out of scope (stated up front):** web frontends (that is `tsx`); 3D game
engines and scene graphs; mobile; and the RSX exchange domain itself. This doc
is about *pixels on a resizable desktop window driven from Go*, nothing more.

---

## 1. Scope and coherence — is this one skill?

The `tsx` skill bundles two things that a React author cannot separate: the
*build* (bundler, JSX, hydration) and the *components* (layout, a11y, visual
system). You cannot ship a good React screen while ignoring either. The claim
here is that Go desktop GL is the same shape: the *build* (go-gl/GLFW, the
render loop, alloc discipline) and the *design* (minimal, responsive, data-dense
UI) are mutually load-bearing.

They cohere for one concrete reason: **on a GPU the design decisions ARE loop
decisions.** "Responsive to a resize" is `glfwGetFramebufferSize` +
`glViewport` every frame ([GLFW Window guide](https://www.glfw.org/docs/latest/window_guide.html)).
"Feels instant" is the present mode and an alloc-free loop, not a CSS
transition. "Minimal, one visual meaning per colour" is what lets the renderer
stay a dumb rasteriser with a fixed palette. Split the skill and you get the
classic failure: a beautiful mockup that janks because the author never owned
the frame budget, or a tight loop rendering an incoherent screen. `rsx-glass`
proves the fusion — its `CLAUDE.md` lists *both* "rsx-term is the visual
template" and "the movable seam / alloc-free loop" as co-equal keeper
invariants (`rsx-glass/CLAUDE.md`).

**Verdict: one skill, two halves — like `tsx`.** The seam between them is a
plain-data cell grid: design decides what each cell *means*; the build decides
how cells become pixels within a frame budget.

---

## 2. The design guidelines (A)

The desktop HIGs converge more than they differ. The distilled ALWAYS/NEVER for
a resizable, data-dense window:

**Layout is adaptive, never pixel-pinned.** The [GNOME HIG](https://developer.gnome.org/hig/)
tells you to design for a *range* of sizes and reflow content rather than
hardcode dimensions; [Apple's macOS HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos)
requires windows be resizable and content to adapt to the available area.
Concretely: set a sensible *minimum* window size so the layout never collapses,
let content reflow, and recompute layout from the live framebuffer size — which
in `rsx-glass` is exactly `r.win.GetFramebufferSize()` read inside `Present`
(`rsx-glass/gpu/gpu.go`).

**Respect HiDPI and fractional scaling.** This is the desktop-specific twist web
authors rarely hit. Window size (screen coordinates) and framebuffer size
(pixels) diverge on HiDPI displays and can change independently when a window is
dragged between monitors ([GLFW Window guide](https://www.glfw.org/docs/latest/window_guide.html)).
[Microsoft's Windows app design](https://learn.microsoft.com/en-us/windows/apps/design/layout/screen-sizes-and-breakpoints-for-responsive-design)
frames the same idea as *effective pixels* — size to a scale-independent unit,
let the system apply the DPI factor. NEVER assume 1 screen-coordinate = 1 pixel.

**Density is a deliberate mode, not an accident.** [Microsoft's Fluent](https://fluent2.microsoft.design/)
ships explicit comfortable/compact densities; a data-dense app should pick a
density on purpose and keep spacing on a consistent scale. [Refactoring UI](https://www.refactoringui.com/)
(Wathan & Schoger) says start with *too much* white space and remove — and use a
constrained spacing scale, not arbitrary values.

**Hierarchy comes from size, weight, and colour — not borders and boxes.**
Refactoring UI's core move: de-emphasise secondary text with colour/weight
instead of shrinking it to illegibility, and let hierarchy do the work a box
would otherwise do. This is Dieter Rams' *"Weniger, aber besser"* — less, but
better — from his [Ten Principles of Good Design](https://www.vitsoe.com/us/about/good-design):
good design is as little design as possible.

**Colour is meaning, never decoration.** Refactoring UI: use *few* colours, each
carrying intent. `rsx-glass` embodies this literally — its palette comment reads
"Colour is meaning, never decoration: add a colour only for a new meaning"
(`rsx-glass/grid.go`), with eight semantic colours (live/ask/degraded/muted…)
and no others. For a data screen this is [Edward Tufte's data-ink ratio](https://www.edwardtufte.com/book/the-visual-display-of-quantitative-information/)
(*The Visual Display of Quantitative Information*, 1983): maximise the share of
pixels that encode data, erase non-data "chartjunk" — gridlines, chrome, and
gratuitous colour that compete with the signal.

**Minimalism is a usability heuristic, not taste.** [Jakob Nielsen's 10
heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) (NN/g)
name it directly — #8 *Aesthetic and Minimalist Design*: every extra unit of
information competes with the relevant units and dilutes them.

**Responsiveness is measurable.** NN/g's [response-time limits](https://www.nngroup.com/articles/response-times-3-important-limits/)
(after Miller 1968 and Card et al.): **0.1 s** feels instant, **1 s** keeps flow
unbroken, **10 s** is the attention limit. Heuristic #1, *Visibility of System
Status*, requires feedback within a reasonable time. For a 60 fps window the
0.1 s budget means a dropped frame is already a perceptible stutter — which is
why the alloc discipline in §3 is a *design* requirement, not a micro-opt.

**Accessibility is non-negotiable and cheap.** [W3C WCAG 2.1](https://www.w3.org/TR/WCAG21/)
sets contrast minimums (1.4.3: 4.5:1 body text, 3:1 large text) and — critical
for a heatmap — 1.4.1 *Use of Color*: never encode meaning by colour *alone*.
`rsx-glass` obeys this by carrying a second channel (the glyph/shape: `░▒▓█` for
density, distinct trade shapes) alongside the colour ramp, so a colour-blind
viewer still reads magnitude (`rsx-glass/atlas/atlas.go`). Dark mode is a
first-class expectation on modern desktops (Apple/GNOME/Fluent all ship it); a
data app usually lives dark-first to reduce glare, as `rsx-glass` does (`Page =
#040806`).

**Keyboard-first.** GNOME and macOS HIGs both require full keyboard operability.
(`rsx-glass` v1 is a read-only viewer and defers input to v2 — `rsx-glass/SPEC.md`
— but the guideline stands for any interactive glgo app.)

---

## 3. The build patterns (B)

**Window/context with go-gl + GLFW.** [`go-gl/glfw`](https://pkg.go.dev/github.com/go-gl/glfw/v3.3/glfw)
creates the window and GL context; [`go-gl/gl`](https://pkg.go.dev/github.com/go-gl/gl)
is the generated command bindings. Because GLFW and GL are single-threaded, the
render goroutine MUST `runtime.LockOSThread()` and do all GL work on it — see
`gpu.New` and `main` in `rsx-glass` (`rsx-glass/gpu/gpu.go`, `rsx-glass/cmd/glass/main.go`).
The event loop is `glfwPollEvents` + `ShouldClose` each frame.

**Present / vsync.** `glfwSwapInterval(1)` enables vsync — the number of screen
refreshes to wait before swapping buffers ([GLFW Context guide](https://www.glfw.org/docs/latest/group__context.html);
[Khronos OpenGL Wiki: SwapInterval](https://www.khronos.org/opengl/wiki/Swap_Interval)).
`rsx-glass` sets `glfw.SwapInterval(1)` and lets `SwapBuffers` block, which
*paces the loop*: present mode becomes the pacer, not a separate timer
(`rsx-glass/gpu/gpu.go`). **Present-mode reality:** OpenGL only offers vsync
on/off (via swap interval) — it has no Vulkan-style Mailbox mode ([Khronos
Vulkan present modes](https://registry.khronos.org/vulkan/specs/1.3-extensions/man/html/VkPresentModeKHR.html)).
For a *data-driven* UI that updates every ~100 ms, vsync-on ≈ Mailbox: you never
outrun the display, so there is nothing to gain from a tear-free
newest-frame-wins mode (`rsx-glass/SPEC.md`). It matters only for input-latency-
bound apps (games, drawing) rendering faster than refresh — not here.

**The 2D cell/quad render pattern.** Draw the whole grid as *one instanced
draw*: a unit quad, one instance per cell, via
[`glDrawElementsInstanced`](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glDrawElementsInstanced.xhtml).
Each instance carries column/row, resolved bg/fg, and a glyph tile index; the
vertex shader places the quad and picks the atlas UV, the fragment shader
composites fg over bg by the glyph's coverage. That is exactly
`rsx-glass/gpu/pipeline.go`: a glyph *atlas* texture (one R8 coverage strip) plus
per-frame instance upload, then a single `gl.DrawElementsInstanced` — **one draw
call per frame** regardless of cell count.

**Bitmap atlas vs MSDF.** For a fixed-size cell grid, a rasterised bitmap atlas
is correct and simplest — `rsx-glass` bakes Go Mono once at a fixed cell size
(`rsx-glass/atlas/atlas.go`). Reach for a multi-channel signed distance field
only when glyphs must scale/zoom continuously and stay crisp: Viktor Chlumský's
[*Shape Decomposition for Multi-Channel Distance Fields*](https://github.com/Chlumsky/msdfgen)
(2015 master's thesis; [msdfgen](https://github.com/Chlumsky/msdfgen)) gives
resolution-independent glyphs with sharp corners at minimal per-frame cost. A
fixed cell grid does not need it; a zoomable canvas does.

**The render loop is immediate-mode: render = pure function of newest state.**
No retained scene graph — each frame rebuilds from the latest model snapshot.
`rsx-glass/render.go` defines the whole contract as a two-method `Renderer`
(`Present(g *Grid) error`, `Close`); the model produces a plain-data `Grid` and
the renderer just draws it.

**Decouple data-rate from render-rate; coalesce to newest.** The producer and
the display run at different rates. The loop selects the *latest* grid and drops
stale ones — `rsx-glass/glass.go`'s `Run` is the canonical shape:
`select { case g := <-grids: latest = g; case <-tick.C: present(latest) }`, and
the producer side uses a non-blocking send so a slow renderer never backs up the
data fold (`publish` in `rsx-glass/cmd/glass/main.go`). Never queue a backlog of
frames you will only throw away.

**Alloc-free per frame (Go GC discipline).** Go's GC is concurrent and
low-pause — [sub-millisecond since ~2016](https://go.dev/blog/ismmkeynote)
([Go blog, "Getting to Go"](https://go.dev/blog/ismmkeynote); design in
[go15gc](https://go.dev/blog/go15gc)) — but *low pause is not no pause*, and a
16.6 ms frame budget has no room for a GC-induced hiccup. So the render path
allocates *zero* after warm-up: reuse the framebuffer/instance buffer, refill in
place. `rsx-glass` reuses its instance slice and uploads with `BufferSubData`
(only re-`BufferData` on a resize grow — `rsx-glass/gpu/pipeline.go`), reuses the
software framebuffer (`rsx-glass/soft/soft.go`), and **enforces it with a test**:
`testing.AllocsPerRun(...) == 0` (`rsx-glass/soft/soft_test.go`,
`TestPresentAllocFree`).

**The movable render seam.** All GPU code lives behind *one* interface so the
backend is swappable (go-gl ↔ go-webgpu) and the app never imports GL directly.
`rsx-glass` enforces this literally: `render.go`'s `Renderer` is the seam, `gpu/`
is "the ONLY package allowed to import go-gl", and `cmd/glass/main.go` is the sole
composition root that wires it in. Its invariant is testable by grep — "`grep
'go-gl\|glfw\|webgpu' *.go` outside `gpu/` must be empty" (`rsx-glass/CLAUDE.md`).
This is what makes an OpenGL→WebGPU move "one package, not a rewrite."

---

## 4. The testing protocol

The strategy: **a pure-Go software renderer is the correctness oracle; the GPU
backend is held to it by pixel parity; everything runs headless.**

1. **Software reference + golden images.** `rsx-glass/soft/` renders `Grid →
   image.RGBA` with no cgo, no GPU, no display, and byte-locks the result against
   committed PNGs (`rsx-glass/soft/soft_test.go`, comparing *decoded* pixels to
   survive PNG-encoder drift). Determinism is deliberate: glyphs come from an
   embedded pure-Go font rasteriser, so masks are byte-identical on any machine
   (`rsx-glass/atlas/atlas.go`). This is the analogue of `tsx`'s DOM snapshot
   tests.

2. **GPU pixel-parity via off-screen readback.** `rsx-glass/gpu/gpu.go`'s
   `Offscreen` renders the same `Grid` into an FBO and `glReadPixels` reads it
   back (flipping GL's bottom-up rows to top-down). `gpu/parity_test.go` compares
   GPU pixels to the soft reference within a tolerance — the only legitimate gap
   is last-bit sRGB rounding (soft blends in integer, GPU in float), so the test
   asserts `maxDiff ≤ 6`, no channel off by >8 (that would be structural), and
   ≤10 % of channels off by >1. This verifies the *shipping* draw path, not a
   stand-in.

3. **Headless under Xvfb + Mesa llvmpipe.** The parity test needs a GL context;
   on a box with no display it must *skip cleanly*, never fake a pass.
   `NewOffscreen` returns an error (via a deferred `recover` around GLFW's
   init-failure panic, `rsx-glass/gpu/gpu.go`) and the test calls `t.Skipf(...)`
   with the reason (`gpu/parity_test.go`). To actually run the pixels in CI,
   drive it under a virtual display + software GL — `xvfb-run go test ./gpu/`
   ([Xvfb](https://www.x.org/releases/current/doc/man/man1/Xvfb.1.xhtml)) with
   [Mesa's llvmpipe](https://docs.mesa3d.org/drivers/llvmpipe.html) software
   rasteriser, as `rsx-glass/README.md` documents.

4. **Alloc test** (§3) and a **model-reuse smoke test** that the real data path
   produces a valid grid round out the suite. The whole default `make test` is
   headless (`rsx-glass/Makefile`).

---

## 5. Pitfalls (top failure modes)

- **Per-frame allocation → GC jitter.** The #1 killer. Any `make`, string
  concat, or interface boxing inside `Present` will eventually trip the GC and
  drop a frame. Defence: reuse every buffer and *gate it with an
  `AllocsPerRun==0` test* (`rsx-glass/soft/soft_test.go`) — assertions, not
  vigilance.
- **HiDPI bugs.** Sizing GL to window coordinates instead of framebuffer pixels
  gives a quarter-resolution or clipped image on Retina/fractional-scaled
  displays. Always drive `glViewport` from `glfwGetFramebufferSize`, re-read on
  resize ([GLFW Window guide](https://www.glfw.org/docs/latest/window_guide.html);
  `rsx-glass/gpu/gpu.go`).
- **cgo / build-tag portability.** go-gl is cgo — it needs OpenGL + GLFW dev
  headers to build, and a headless CI box has neither a display nor a GPU
  (`rsx-glass/README.md` lists the Debian `-dev` packages). Keep the pure-Go
  path (soft) buildable and testable *without* cgo so CI is green everywhere;
  isolate GL behind a package that skips cleanly when there is no context.
- **Importing GL outside the seam.** The moment a helper deep in the app imports
  `go-gl`, the backend is no longer swappable and headless tests no longer link.
  Enforce the seam by grep in CI (`rsx-glass/CLAUDE.md`).
- **Faking a headless pass.** A parity test that "passes" because it silently
  did nothing when no GL context exists is worse than no test. Skip *loudly* with
  a reason (`t.Skipf`), and make the real pixels runnable under Xvfb+llvmpipe so
  the parity is actually exercised somewhere (`rsx-glass/gpu/parity_test.go`).
- **Fighting the present mode.** Adding a manual frame timer *and* vsync
  double-paces and stutters. Pick one pacer — for a data UI, let vsync-on
  `SwapBuffers` block and treat any software tick as a mere upper bound on
  wakeups (`rsx-glass/cmd/glass/main.go`, `renderTick` comment).

---

## 6. Sources

**Design.** GNOME Human Interface Guidelines (developer.gnome.org/hig); Apple
Human Interface Guidelines — Designing for macOS; Microsoft Windows app design /
responsive layout & Fluent 2; Wathan & Schoger, *Refactoring UI*; Jakob Nielsen /
NN/g — *10 Usability Heuristics*, *Response Times: The 3 Important Limits*; Dieter
Rams, *Ten Principles of Good Design* ("Weniger, aber besser", Vitsœ); Edward
Tufte, *The Visual Display of Quantitative Information* (1983), data-ink ratio;
W3C *WCAG 2.1* — 1.4.3 Contrast, 1.4.1 Use of Color.

**Build/test.** go-gl/gl & go-gl/glfw (pkg.go.dev/github.com/go-gl); GLFW Window
& Context guides (glfw.org/docs); Khronos OpenGL Wiki — Swap Interval; Khronos —
`glDrawElementsInstanced`; Khronos Vulkan — `VkPresentModeKHR` (Mailbox
contrast); The Go Blog — "Getting to Go" & "Go GC: Prioritizing low latency and
simplicity"; Viktor Chlumský, *Shape Decomposition for Multi-Channel Distance
Fields* (2015) / msdfgen; Mesa llvmpipe (docs.mesa3d.org); Xvfb (X.Org).

**Reference implementation (this repo).** `rsx-glass/` — `render.go` (seam),
`grid.go` (cell contract + semantic palette), `glass.go` (coalescing loop),
`gpu/gpu.go` + `gpu/pipeline.go` (go-gl backend, instanced quads, FBO readback),
`gpu/parity_test.go` (pixel parity + clean skip), `soft/soft.go` +
`soft/soft_test.go` (oracle, goldens, alloc test), `atlas/atlas.go` (deterministic
atlas), `cmd/glass/main.go` (composition root), `SPEC.md`/`README.md`/`CLAUDE.md`.
