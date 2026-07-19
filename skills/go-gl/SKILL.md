---
name: go-gl
description: Responsive minimal OpenGL desktop apps in Go (go-gl/gl + go-gl/glfw) — window + render loop, HiDPI/resize, alloc-free present, a movable GPU seam, data-dense screen design. NOT web (use tsx), NOT 3D game engines / scene graphs, NOT non-GL Go (use go).
when_to_use: building a native desktop OpenGL window driven from Go — go-gl/glfw window, the render loop, resize/HiDPI, an alloc-free present path, a swappable render backend, or a minimal data-dense screen
---

# go-gl — desktop OpenGL apps in Go

Requires the `go` skill for base Go rules. This is the desktop-GL analogue of
`tsx`: on a GPU the *design* decisions ARE *loop* decisions, so build and screen
are one skill. Reference: `rsx-glass/` (a fixed-size v1 heatmap viewer) — cite it
for the render architecture, NOT as resize/pacing/HiDPI proof.

## The gates — violate one, ship a broken or janky app

Ordered by damage. 1–8 are the loop; 9–12 are the data screen.

**1. ALWAYS give ONE composition root the OS thread and the GLFW lifecycle.**
Call `runtime.LockOSThread()` once, in the entry-point binary, before init. GLFW
init/terminate, event processing, and window/context create/destroy are
**main-thread-only** (not "GL is single-threaded" — a GL context is merely
current on one thread at a time). `glfw.Init`/`Terminate` are **process-global**:
one windowed renderer per process. Library constructors ASSERT/document thread
affinity — they NEVER call `LockOSThread` for the caller (a lib can't know it's
on the main thread). Make `Close` idempotent. `gl.Init()` runs only after
`MakeContextCurrent`. Pin the context: request core `3.3` minimum (a *minimum*,
not exact), forward-compatible on macOS (which deprecates GL); log the actual
version/profile/vendor. See `rsx-glass/cmd/glass/main.go`, `gpu/gpu.go`.

**2. ALWAYS pump window events EVERY loop iteration, independent of data.**
`PollEvents` must NOT live only inside `Present` — a slow/dead feed then leaves
the window uncloseable and hung. Put a `Pump()` on the loop that runs every tick,
render only when there is a grid. ALWAYS wire a quit path (Esc/q key callback →
`SetShouldClose`), not just the window chrome. `rsx-glass/glass.go`, `gpu/gpu.go`.

**3. ALWAYS keep THREE coordinate systems separate, each with an owner.**
Framebuffer **pixels** → `glViewport` ONLY. Window **screen-coords** × **content
scale** → layout and font size. NEVER assume 1 screen-coord = 1 pixel (false on
HiDPI/fractional). Read framebuffer size from the live window each frame; on a
`0×0` framebuffer (minimized) draw nothing. Record newest size/scale in resize
callbacks and rebuild once at a frame boundary — never reallocate mid-storm.

**4. ALWAYS pin the context/profile AND the binding+build matrix deliberately.**
`go-gl/glfw/v3.3` vendors a specific GLFW; cite docs for the version you import,
not "latest". go-gl is **cgo** and bundles the GLFW C source — a system
`libglfw3-dev` is NOT the dependency; you need a C toolchain + platform GL/X11
(or `wayland`-tag) dev headers. Link the binding's install matrix; don't freeze a
distro package list. `rsx-glass/README.md`, `go.mod`.

**5. ALWAYS build-tag the GPU backend behind a non-GL stub.** Tag the GL package
`//go:build cgo`; add a `//go:build !cgo` stub whose constructors return an
error. Then `CGO_ENABLED=0 go build/test ./...` is GREEN everywhere (the pure-Go
path builds; the parity test skips cleanly) instead of failing to compile on a
headless box. `rsx-glass/gpu/stub.go`.

**6. ALWAYS keep newest-state in an overwriting slot; pick ONE pacer.** The
producer must KEEP the newest and drop the stale — drain-then-send (or an atomic
latest-pointer + wake), NEVER `select{ case ch<-g: default: }` which drops the
NEW grid when the slot is full. The consumer holds only `latest`. Pick exactly
one pacer — the blocking vsync swap OR a timer, never both timing the same frame.
`rsx-glass/cmd/glass/main.go` (`publish`), `glass.go` (`Run`).

**7. ALWAYS treat `SwapInterval(1)` as a REQUEST, and measure pacing.** Drivers,
compositors, and user settings override it; a returned `SwapBuffers` does NOT
prove the frame is shown. GL lacks a *portable* Vulkan-style present-mode /
Mailbox selection (it is not "vsync on/off only" — adaptive negative intervals
exist). For a dirty-only low-rate feed vsync-on *may look like* Mailbox, but that
is a workload observation, not an equivalence (FIFO can show an older queued
frame). Gate real decisions on measured sample-age-to-present and
input-to-present p50/p99, not update cadence.

**8. ALWAYS isolate all GPU/windowing imports behind ONE interface package.**
`grep 'go-gl\|glfw\|webgpu'` outside that package must be empty (enforce in CI).
Keep a pure-Go software renderer that builds/tests with `CGO_ENABLED=0`. Honest
caveat: the seam is *designed* to swap OpenGL→webgpu but is **unproven** until a
second *windowed* backend exists — window creation, the swap-interval knob, and
event pumping still live inside the GL package, so a software-only reference does
not prove the swap. `rsx-glass/render.go`, `gpu/`.

**9. ALWAYS keep the render path steady-state alloc-free — scoped HONESTLY.**
Reuse instance/frame buffers, refill in place, `BufferSubData` (re-`BufferData`
only on a resize grow). Gate with `testing.AllocsPerRun(...) == 0` **per shipping
backend, with stated exclusions** — claim "steady-state soft rasterization
allocs==0", NOT a blanket "zero allocations" (resize grows; the model may alloc;
any goroutine's GC can still pause the render one). Low pause ≠ no pause; verify
p99 frame time, don't recite GC folklore. `rsx-glass/soft/soft_test.go`.

**10. ALWAYS hold the GPU backend to the software reference by pixel parity.**
Software renderer = **regression** oracle (it locks that the render didn't
*change*, NOT that it's *correct* — both backends share the atlas/cell
assumptions, so parity can't catch a shared-wrong encoding). Off-screen FBO
readback verifies shader arithmetic; the tolerance MUST match the measured bound
(if you measured maxDiff≤1, gate at 1 — not a slack 6 with unreachable asserts).
A `t.Skipf` on no-context reads `ok` in a plain run: add a **required** GPU CI
job (xvfb + llvmpipe) that FAILS, not skips, and asserts renderer/version.
`rsx-glass/gpu/parity_test.go`, `soft/soft_test.go`.

**11. ALWAYS pick ONE colour policy and never mix.** Author sRGB, blend sRGB, NO
sRGB framebuffer — OR linear end-to-end. Enabling `GL_FRAMEBUFFER_SRGB` on one
side only makes the GPU linearize while software doesn't: parity breaks and
goldens don't catch it. This is a load-bearing invariant, state it. (finding 31)

**12. Data-screen design gates** (each testable; generic HIG advice is not; the
methodology is `design-systems-research.md` — Material 3 / Fluent / Carbon / DTCG):
- **Tokens, not raw hex; reserved contrast pairs.** Author a 3-tier palette —
  primitive stops → semantic roles → component inks (W3C DTCG); the render reads
  only semantic/component tiers, a theme swap rebinds tier 2. Every glyph fg is a
  palette ink ≥3:1 on every bg — NEVER derive fg as "bg one tier up" (collapses to
  fg==bg). Gate the FULL ink×bg matrix, EVERY theme, on WCAG 3:1 AND **APCA Lc** (a
  near-black base makes WCAG lie) — not one measured pair. A rule that is a
  LANGUAGE decision (colour meaning, encoding) lives in the token layer, NEVER
  forked into a renderer — else backends diverge (a template kept an fg==bg bug its
  own downstream had already fixed). `rsx-glass/heat.go`, `heat_test.go`.
- **Encode by channel rank** (Cleveland-McGill): exact→text, magnitude→length/
  position, overview→luminance. Colour is meaning, never decoration. NEVER let hue
  be a meaning's sole carrier (the deuteranopia trap) — a category needs a
  redundant NON-colour channel: encode by SHAPE/direction (e.g. up/down triangles
  = buy/sell), not red-vs-green on one shape.
- **Perceptually-even ramps.** Space a magnitude ramp on perceptual lightness
  (M3 tonal / APCA), NOT a raw linear-sRGB blend — equal data steps must LOOK
  equal or the eye misreads magnitude.
- **Stable scales.** Ramps/axes decay slowly or pin; NEVER re-normalize to the
  current frame's max — the whole screen strobes on every data spike. Verify with
  a multi-frame sequence test, not a single golden.
- **Density is ONE multiplier over a spacing scale** (Fluent/Ant comfortable vs
  compact), chosen on purpose — never per-element spacing fiddling.
- **Fixed-width unit-scaled numbers.** Exact values are tabular (right-aligned,
  fixed precision, tick/lot-scaled at the edge); a number that changes width per
  update makes the layout jump.
- **Freshness at the point of reading.** Data that stops updating ages visibly in
  place (dims / `~` after N ms); a degraded state keeps marked last-known data,
  never a silent last-known value with only a corner dot flipped.

## NEVER assume (honest caveats — the reference is v1)

- **Autoscale strobe:** per-frame max normalization strobes; the stable-scale fix
  is upstream (rsx-term's decaying basis), v2 in glass.
- **HiDPI text:** a 1× bitmap atlas nearest-scaled is crisp-*chunky*, not
  re-hinted; size-bucketed atlases per content scale are the real fix.
- **Cell grid is a compatibility layer, not a resolution cap** — for a continuous
  field the GPU payoff is sub-cell (per-datum instances / data texture). Primitive
  follows data topology; a cell grid teaches chunky terminal emulators.
- **go-webgpu:** the maintained binding is `cogentcore/webgpu`; the archived
  `rajveermalviya/go-webgpu` is read-only. The swap is designed-for, not proven.
- **Wayland:** go-gl/glfw builds X11 by default; under XWayland fractional scaling
  blurs the 1:1 pixel text a cell grid exists for.
- **Accessibility:** raw GL exposes NO accessibility tree, focus, screen-reader
  text, selection, or IME — pixels only. Scope it as a canvas; an accessible
  table is a separate layer. Don't claim "WCAG covered" from contrast alone.

## Reference

Skill-local: `research.md` (build/test methodology + sources),
`design-systems-research.md` (the token/contrast/channel design methodology),
`codex-critique.md` + `fable-critique.md` (the adversarial audit trail this skill
was rectified against). And `rsx-glass/`:
`render.go` (the seam), `glass.go` (loop), `gpu/gpu.go`+`pipeline.go` (go-gl
backend, instanced quads, letterbox, FBO readback), `gpu/stub.go` (non-cgo),
`gpu/parity_test.go` (parity + clean skip), `soft/` (oracle, goldens, alloc
test), `heat.go` (`glyphFg`/palette), `atlas/atlas.go`, `cmd/glass/main.go`
(composition root), `SPEC.md` "Known v1 deviations".
