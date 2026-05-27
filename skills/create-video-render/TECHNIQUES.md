# Programmatic Video — Engine Choice & Techniques

Reference for [`create-video-render`](./SKILL.md). Loads on demand. Read this when choosing an engine, when licensing matters, or when Remotion isn't the right fit for the niche.

## Niche engines — differential dynamics & coordination

When the subject is dynamical systems (phase portraits, attractors, bifurcations, reaction-diffusion) or multi-agent coordination (swarms, coupled oscillators, agent orchestration), the mainstream web engines are the wrong tool. Specialist options, ranked by niche × quality:

| tool | stack | uniquely good at | headless → mp4 | license |
|---|---|---|---|---|
| **DynamicalSystems.jl + GLMakie** | Julia | research-grade DS: trajectories, Lyapunov, basins, attractors | `record(fig, "out.mp4", frames)` | MIT |
| **BifurcationKit.jl** | Julia | only serious open-source numerical continuation (Hopf/fold/period-doubling) | via Makie `record` | MIT |
| **Bevy + wgpu headless** | Rust ECS | ECS *is* an agent-orchestration model — render the real sim, not a mock | `headless_renderer` example → PNG seq → ffmpeg | MIT/Apache |
| **Taichi Lang** | Python→GPU | massive parallel fields: reaction-diffusion, stable-fluid, MPM | `ti.tools.VideoManager` → mp4 | Apache-2.0 |
| **nannou** | Rust | reliable generative/swarm (boids, Vicsek) | `capture_frame(path)` → ffmpeg | MIT/Apache |
| **Penrose** | TS DSL | declarative LaTeX-grade math diagrams, constraint-solved layout | SVG export → frames → ffmpeg | MIT |
| **VisPy** | Python/GLSL | GPU shader field viz, millions of points @60fps | `canvas.render()` → imageio | BSD-3 |
| **ParaView (pvbatch)** | Python/MPI | cinematic 3D PDE/volumetric fields, cluster-scale | off-screen EGL → `SaveAnimation()` | BSD-3 |
| **phaseportrait** | Python/matplotlib | quick correct nullclines / 2D-3D portraits / cobweb | `FuncAnimation` → ffmpeg | MIT |
| **Bonzomatic / KodeLife** | GLSL live-coder | pure fragment-shader field dynamics (demoscene) | capture via ffmpeg/NDI | zlib / proprietary |

Picks: **DynamicalSystems.jl** for correct DS math; **Bevy headless** when the video should be driven by a real agent simulation (ECS mirrors containers/agents coordinating); **Taichi** for GPU fields; **nannou** for swarm/flocking. TouchDesigner and Houdini have high ceilings but weak headless/CLI stories — use only if already in that tool.

Sources: [DynamicalSystems.jl](https://juliadynamics.github.io/DynamicalSystems.jl/dev/visualizations/) · [BifurcationKit.jl](https://github.com/bifurcationkit/BifurcationKit.jl) · [Bevy headless_renderer](https://github.com/bevyengine/bevy/blob/main/examples/app/headless_renderer.rs) · [Taichi](https://www.taichi-lang.org/) · [nannou](https://github.com/nannou-org/nannou) · [Penrose](https://penrose.cs.cmu.edu/blog/v3) · [VisPy](https://vispy.org/) · [ParaView pvbatch](https://docs.paraview.org/en/latest/Tutorials/ClassroomTutorials/pythonAndBatchPvpythonAndPvbatch.html) · [phaseportrait](https://pypi.org/project/phaseportrait/) · [Bonzomatic](https://github.com/Gargaj/Bonzomatic)

## Engine comparison

| engine | paradigm | best niche | render | licensing |
|---|---|---|---|---|
| **Remotion** | React, declarative, frame = `useCurrentFrame()` | data-driven video; anything expressible in CSS/SVG/web fonts | headless Chromium captures each frame; ~8-15s per 150 frames @1080p; memory-heavy | **paid license for companies** |
| **Motion Canvas** | TypeScript generator functions, imperative scene-graph | choreographed timing-first sequences, explainers | canvas engine, pixel-accurate, faster on complex scenes; no arbitrary HTML/CSS | truly open source |
| **Revideo** | Motion Canvas fork + Node `renderVideo()` | automated server-side pipelines, SaaS render workers | canvas, server-first; queue/cron friendly | open source, no license step |
| **Manim** | Python, OpenGL/GLSL GPU | math, formulae, data explainers (3Blue1Brown style) | GPU; presets to 4K60; real-time preview | open source |
| **Lottie** | After Effects → Bodymovin → JSON, `lottie-web` (~50KB) | designer-authored particle/morph/complex-easing assets | client-side player; near-100% AE fidelity | open source |
| **GSAP** | JS timeline, framework-agnostic | web-embedded motion (live pages, not file output) | browser playback; needs a capture step (Puppeteer/Playwright) to become a file | open source (incl. former Club plugins) |

### How to pick

- **Default to Remotion** for our use: React is the team's lingua franca, any web visual works, the official agent-skill bundle makes the agent reliable. Accept the company-license caveat or swap to Revideo for redistributable/commercial work.
- **Choreographed timing-first** (the animation IS the message, e.g. an algorithm walkthrough) → Motion Canvas / Revideo. The generator-function timeline is more natural than frame math.
- **Math / data explainer** → Manim. Nothing else matches its formula/plot rendering.
- **A designer already made it in After Effects** → Lottie. Don't re-implement AE easing by hand; export the JSON.
- **It lives on a web page, not in a file** → GSAP. If you later need a file, capture frames with a headless browser.

## The pipeline shape (proven by the field)

```
script.json ──► TTS (Edge TTS free / OpenAI / ElevenLabs) ──► per-scene wav
     │                                                            │
     │                                                            ▼
     │                                          faster-whisper ──► word-level timestamps
     ▼                                                            │
 scene specs ──► Remotion composition ◄─────────── caption track ┘
                       │
                       ▼
              npx remotion render ──► mp4 (+ burned captions, + .srt sidecar)
```

Reference implementations worth reading before building from scratch:

- [claude-video-kit](https://github.com/runesleo/claude-video-kit) — JSON script → TTS + Whisper + Remotion → vertical video. Closest match to our two-skill split.
- [remotion-superpowers](https://github.com/dojocodinglabs/remotion-superpowers) — full Claude Code plugin: voiceover, music, stock footage, image/video gen, TikTok captions, 3D, AI review loop. 5 MCP servers.
- [youtube-shorts-pipeline](https://github.com/rushindrasinha/youtube-shorts-pipeline) — news → script → visuals → VO → captions → upload; ASS burn + SRT upload split.
- [Remotion official Agent Skills](https://www.remotion.dev/docs/ai/skills) — 28 rule files; install and defer to these for API correctness.

## Captioning detail

- **Word-level, not line-level.** TikTok/Shorts retention favors 1-3 words popping in sync. Whisper gives word timings; use them.
- **ASS for burn-in** (supports per-word color/scale highlight), **SRT for platform CC** (YouTube ingest). Emit both.
- **Align to the rendered audio**, never to the script text — TTS pacing drifts from the written line.

## TTS notes

- **Edge TTS**: free, 300+ voices, cross-platform. Default for drafts.
- **OpenAI TTS / ElevenLabs**: better prosody, needs an API key. Use for final renders when the user supplies a key.
- One wav per scene → caption timing stays scene-local and a re-record only re-renders one scene.

## Motion-design principles (engine-agnostic)

From the broader motion-design literature (Disney 12 principles adapted for UI, LottieFiles' motion-design guidance):

- **Ease everything.** Linear motion reads as cheap. Cubic-bezier / spring on every transform.
- **Stagger.** Simultaneous reveals look flat; offset siblings by a few frames.
- **Anticipation + follow-through.** A tiny pre-move and overshoot sell weight.
- **One focal point per beat.** If two things move for attention, the viewer catches neither.
- **Hold nothing perfectly still.** Subtle idle float/glow keeps a held frame alive.

These hold whether you render with Remotion springs, Motion Canvas tweens, or GSAP timelines.

## Remotion specifics (quick reference)

The official bundle (`npx remotion skills`) is authoritative; this is the minimum to start.

Project layout: `Root.tsx` (composition registration) · `Video.tsx` (`TransitionSeries`) · `tokens.ts` (colors/fonts/dims/durations) · `scenes/` · `components/`. Specs: 1920×1080 (or 1080×1920 vertical), 30fps, ~12-frame fades. Scene durations: hook/CTA ~72 frames, medium 78-120, demo 120-150; social total 15-20s.

Spring presets:

| use | config |
|---|---|
| headline pop-in | `{ damping: 20, stiffness: 200 }` |
| smooth slide | `{ damping: 200 }, durationInFrames: 16` |
| bouncy emphasis | `{ damping: 14, stiffness: 180 }` |
| weighty entry | `{ damping: 200 }, durationInFrames: 16-20` |

Idioms: counting number = `interpolate(frame, [a,b], [0,target], {easing: Easing.out(Easing.quad)})` with `tabular-nums`; idle motion = `Math.sin(frame * k)` for float/glow; cursor click = eased X/Y glide then a 6-frame `1→0.96→1` button dip. Always `Math.max(0, frame - startFrame)` so a delayed element doesn't pre-animate.
