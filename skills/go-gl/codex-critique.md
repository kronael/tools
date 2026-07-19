# Adversarial critique of `research-glgo.md`

Fresh checks: `go test -count=1 ./...` passed; `CGO_ENABLED=0 go test
-count=1 ./...` failed because `gpu` and `cmd/glass` still import cgo-only
go-gl; Xvfb + forced llvmpipe parity passed with `maxDiff=1` over 705,024 RGB
channels. The last result proves one Mesa raster path, not the desktop claims.

1. **The cited reference is not resizable.** The methodology calls
   `rsx-glass` proof of a responsive window, but `gpu/gpu.go:220` sets
   `glfw.Resizable` false; the app is a fixed 72×24 grid. `GetFramebufferSize`
   plus `glViewport` only stretches that grid and distorts cells at a different
   aspect ratio. **Fix:** enable resize, set logical minimums, and recompute or
   letterbox the grid; stop citing this backend as resize proof until tested.

2. **It collapses three coordinate systems into one.** Window size is in
   screen coordinates, framebuffer size is in pixels, and content scale is a UI
   scaling factor. Only the framebuffer size belongs in `glViewport`; layout
   and font sizing need window size plus content scale. The [GLFW window
   guide](https://www.glfw.org/docs/latest/window) states these separately.
   **Fix:** teach all three and assign each one an explicit owner.

3. **“GLFW and GL are single-threaded” is wrong.** GLFW initialization,
   termination, event processing, and window/context creation/destruction are
   main-thread-only; a GL context may be current on any one thread at a time.
   See GLFW's [thread-safety rules](https://www.glfw.org/docs/latest/intro) and
   [context rules](https://www.glfw.org/docs/latest/context_guide.html).
   **Fix:** lock the startup thread in `init`, keep all GLFW lifecycle/events and
   simple-app GL work there, and send immutable/bounded state from workers.

4. **`LockOSThread` ownership is misplaced.** `main` locks once and `gpu.New`
   locks again; error returns and `NewOffscreen` leave nested locks to caller
   lifetime. A library constructor cannot guarantee it was called on the
   process main thread. **Fix:** make the composition root own one startup-thread
   lock and the whole GLFW lifecycle; constructors assert/document thread
   affinity rather than silently locking their caller.

5. **GLFW lifecycle is treated as per-renderer when it is process-global.**
   Every `New` calls `glfw.Init` and every `Close` calls `glfw.Terminate`, so two
   windows/renderers or parallel GPU tests can invalidate one another.
   Destruction and cleanup also require the right current context. **Fix:** one
   app object owns `Init`/`Terminate`; windows own only window/context resources,
   with explicit current-context and idempotent-close rules.

6. **Version/profile pinning is incomplete and source-mismatched.** The module
   imports `glfw/v3.3` (vendored GLFW 3.3.10) while citing unversioned latest
   GLFW 3.4 docs. GLFW version hints request a *minimum*, not an exact version,
   while `go-gl/gl/v3.3-core/gl` fixes the loaded API surface. macOS additionally
   permits only forward-compatible core contexts for modern GL and deprecates
   OpenGL. **Fix:** choose v3.3 or v3.4 deliberately, cite matching docs, request
   core 3.3 minimum, call `gl.Init` only after making it current, and log/assert
   actual version/profile/vendor; document macOS's deprecated-GL status.

7. **The cgo/build statement is materially wrong.** go-gl and go-gl/glfw need
   cgo and a C toolchain, but go-gl/glfw bundles GLFW C source; a system
   `libglfw3-dev` is not the dependency. Platform headers/libraries and build
   tags differ by binding version, OS, X11/Wayland, and GL/GLES. The claimed
   cgo-free default fails today. **Fix:** put the GPU backend and desktop command
   behind an explicit build tag with a non-GL stub or separate module; test
   `CGO_ENABLED=0`; link to the pinned binding's [installation
   matrix](https://github.com/go-gl/glfw) instead of freezing a Debian package
   list in the skill.

8. **Event processing incorrectly depends on having render data.** `PollEvents`
   lives inside `Present`, but `glass.Run` never calls `Present` before the first
   grid. A slow/dead feed therefore makes the window uncloseable and visibly
   hung. Polling only around blocking swaps also inflates input latency.
   **Fix:** the locked main loop always processes events; use
   `WaitEventsTimeout`/`PostEmptyEvent` or bounded polling, then render only when
   dirty or needed.

9. **Resize storms and minimization are absent.** Reading framebuffer size every
   frame neither coalesces layout/atlas reallocations nor handles a 0×0
   framebuffer while minimized. GLFW may also block event processing during
   interactive move/resize on some platforms. **Fix:** callbacks only record the
   newest window/framebuffer/content-scale state; rebuild once at a safe frame
   boundary, skip zero-sized draws, and cover move-between-monitors and resize
   storms in tests.

10. **`SwapInterval` semantics are overstated.** It sets a minimum retrace
    interval for the *current context*. Drivers, user settings, extensions, and
    compositors may override it or make it ineffective; negative adaptive
    intervals exist on GLX/WGL extensions. `SwapBuffers` returning does not prove
    the frame is physically visible. See GLFW's [buffer swapping
    contract](https://www.glfw.org/docs/latest/window#buffer_swap).
    **Fix:** describe interval 1 as a request, check extension/platform behavior,
    and measure pacing rather than declaring the swap “shown.”

11. **“OpenGL only offers vsync on/off” is false.** Portable GLFW exposes an
    integer interval; some platforms expose adaptive negative intervals. What
    OpenGL lacks is a portable Vulkan-style present-mode selection and portable
    Mailbox guarantee. **Fix:** use that narrower statement.

12. **“Vsync-on approximates Mailbox” is an unsafe equivalence.** A 10 Hz data
    average says nothing about burst rate, phase relative to vblank, input
    updates, render time, driver queue depth, or compositor buffering. FIFO can
    block or display an older queued image; Mailbox replaces the pending image.
    **Fix:** say they may look equivalent only for a measured, dirty-only,
    low-rate viewer; gate the decision on sample-age-to-present and
    input-to-present p50/p99, not update cadence.

13. **The pacer advice contradicts the reference.** The doc says not to combine
    a timer with vsync, while `glass.Run` waits on a 16 ms ticker and
    `SwapBuffers` may wait again. It also redraws identical 10 Hz data at roughly
    60 Hz and caps high-refresh displays near 62.5 Hz. **Fix:** either run
    continuously with swap pacing and always poll events, or use dirty/event
    wakeups with a latency deadline; do not prescribe both mechanisms.

14. **The “newest-state” channel preserves stale state.** `publish` drops the
    *new* grid when its one-slot channel contains an old grid. This is the
    opposite of Mailbox and can add another 100 ms bin before freshness recovers.
    **Fix:** overwrite the pending slot (drain stale then send), or publish an
    atomic latest pointer plus generation and wake the main loop.

15. **The alloc-free proof is scoped far below the claim.** Only soft
    `Present` has `AllocsPerRun`; the GPU path is untested, resize growth
    allocates, and the producer explicitly calls `NewGrid` every 100 ms. A GC
    triggered by any goroutine can stop the render goroutine even if that
    goroutine allocates nothing. **Fix:** either claim only “steady-state soft
    rasterization allocates zero,” or measure the full app/GPU path with
    allocs, runtime traces, frame-time p99, and resize/input scenarios; use
    owned double buffers/pools if measurements justify it.

16. **The GC rhetoric is generic filler presented as causality.** One `make`,
    string concatenation, or interface value does not necessarily allocate,
    trigger GC, or drop a frame; escape analysis and heap pacing decide that.
    The 100 ms interaction heuristic also does not prove one missed 16.6 ms
    frame is perceptible. **Fix:** replace “#1 killer” and old Go-GC marketing
    with a budget: no unexpected steady-state allocations, benchmarked on the
    shipping workload, with explicit p99 frame and input-latency limits.

17. **The software renderer is a regression oracle, not a correctness oracle.**
    Both backends share the same atlas and cell assumptions, so parity can lock
    in the same wrong glyph, layout, color-space, or accessibility behavior.
    Two synthetic scenes do not establish data-dense UI correctness.
    **Fix:** call goldens regression tests; add independent layout invariants,
    adversarial grids, semantic assertions, and human/platform visual review.

18. **Off-screen FBO parity does not verify the shipping presentation path.**
    It bypasses the default framebuffer, swap, compositor, color management,
    actual window scaling, occlusion, tearing, and resize behavior; it tests at
    exactly the atlas's native pixel size, hiding the reference's stretching
    bug. **Fix:** retain FBO parity for shader arithmetic, then add windowed
    smoke tests across scale factors/aspect ratios and pacing telemetry on each
    supported OS/GPU class.

19. **A skipped GPU test still gives a green gate.** Normal `go test` reports
    the package `ok`; the individual `t.Skipf` reason is not loud without
    verbose/JSON output. Xvfb+llvmpipe proves Linux Mesa software rendering, not
    vendor drivers or presentation. **Fix:** make a required `test-gpu` CI job
    fail if context creation or parity is skipped, assert/log renderer/version,
    and keep separate optional hardware/platform smoke jobs.

20. **The parity tolerance contradicts its model.** The comment says rounding
    differs by at most one, but the test permits `maxDiff=6` and 10% of channels
    over one; the `over8` assertion is unreachable once `maxDiff<=6` passes.
    **Fix:** require the demonstrated bound of one, or justify a perceptual
    metric per platform; remove redundant thresholds and add structural checks
    that pixel tolerances cannot mask.

21. **Text and HiDPI guidance is missing where it matters.** The reference bakes
    printable ASCII once at 14 pt/72 DPI with full hinting, then nearest-scales
    that bitmap. Fractional/HiDPI scaling therefore makes hinted text uneven or
    pixelated; unknown Unicode silently becomes blank. **Fix:** define the text
    scope. For ASCII cell grids, rebuild size-bucketed atlases from content
    scale and preserve logical metrics; for real UI text, add shaping, fallback,
    bidi/script handling, and DPI-aware hinting/rasterization (for example
    HarfBuzz-backed shaping), then cache shaped runs.

22. **“Accessibility is cheap” is dangerously false for raw GL.** Contrast and
    redundant glyphs help color vision but pixels expose no accessibility tree,
    focus semantics, screen-reader text, selection, or IME. Keyboard-first is
    also deferred by the reference. **Fix:** scope raw GL to a canvas and use
    native/toolkit controls or provide an accessible text/table representation;
    specify focus, keyboard navigation, text input/IME, clipboard, and OS
    scaling before claiming desktop accessibility.

23. **Context loss and GL diagnostics are omitted.** Context creation success
    is treated as permanent; there is no debug callback, reset detection,
    resource-recreation policy, or operator-visible driver/version record.
    **Fix:** request a debug context in development, enable GL debug output,
    check framebuffer/context errors, and choose an explicit reset policy:
    recreate every GPU object from CPU-owned state or fail fast with actionable
    diagnostics. Test teardown/recreation and suspend/resume where supported.

24. **Reference-specific choices masquerade as universal design rules.** One
    draw call, a fixed bitmap atlas, no retained state, and a two-method renderer
    seam fit this cell-grid demo; they are not prerequisites for responsive Go
    desktop apps. Upload bandwidth, sync, text shaping, and layout can dominate,
    and retained caches are often the right answer. **Fix:** keep batching,
    bounded newest-state transfer, and backend isolation as principles; make draw
    count, atlas type, and immediate/retained structure measurement-driven.

25. **The document cannot become a useful sub-200-line skill without deleting
    its thesis defense.** The `tsx` analogy, “one skill” verdict, Rams/Tufte/
    Nielsen/Refactoring UI tour, dark-mode aside, response-time folklore, MSDF
    history, repeated alloc claims, repeated seam claims, and bibliography prose
    are not operational. **Fix:** cut them. Keep only: startup-thread/lifecycle;
    pinned context/profile/build matrix; logical/window/framebuffer/content-scale
    sizing; event/input/resize loop; newest-state ownership; measured pacing;
    DPI-aware text scope; cgo/build tags; required software/FBO/platform tests;
    context-loss diagnostics; and five data-screen design gates—degradation
    priorities, semantic color plus a redundant channel, contrast, keyboard/
    focus, and freshness/status visibility.
