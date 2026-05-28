---
name: create-video-render
description: Render short-form / motion / dynamical-systems video from a script. Indexes engines (Remotion, Manim, Motion Canvas, Julia, Bevy, shaders) — loads one on demand. NOT for writing the script (use create-video-script) or static UI (use visual).
when_to_use: "render the video", "build a Remotion video", "manim", "motion canvas", "animate this script", "motion design", "make an mp4", "phase portrait", "vector field", "swarm", "coupled oscillators", "differential dynamics", "coordination animation", "captions", "voiceover"
user-invocable: true
---

# Video Render — index

Turns a prose script from [`create-video-script`](../create-video-script/SKILL.md) into an mp4. This file is engine-agnostic: the bridge, house style, caption pipeline, and a flavor index. Pick a flavor, then read only its file.

## Pick a flavor (load on demand)

| flavor | file | pick when |
|---|---|---|
| Remotion | [flavors/remotion.md](flavors/remotion.md) | React stack, data-driven, any CSS/SVG; the default web path |
| Manim | [flavors/manim.md](flavors/manim.md) | math — formulae, plots, geometry, derivations |
| Motion Canvas / Revideo | [flavors/motion-canvas.md](flavors/motion-canvas.md) | timing-first choreography; license-free; automated pipelines |
| DynamicalSystems.jl | [flavors/dynamical-systems.md](flavors/dynamical-systems.md) | research-grade phase portraits, attractors, basins, bifurcations |
| Bevy headless | [flavors/bevy-headless.md](flavors/bevy-headless.md) | render a *real* ECS agent simulation (orchestration themes) |
| GPU fields & swarm | [flavors/fields-swarm.md](flavors/fields-swarm.md) | reaction-diffusion, fluids, boids, Vicsek (Taichi/nannou/VisPy/p5) |
| Shaders & declarative | [flavors/shaders-declarative.md](flavors/shaders-declarative.md) | per-pixel field shaders; LaTeX-grade solved diagrams (Penrose) |

Runnable starting points for the common engines are in [`examples/`](examples/README.md).

## Bridge: prose script → scenes

Derive structure from the script; NEVER ask the author for JSON.

- Bracketed `[direction]` line → `visual` (not spoken).
- Plain line → `vo` (spoken; drives TTS + caption timing).
- Blank line → scene boundary. Estimate `duration_s` from `vo` at ~2.5 words/sec.

## House style (every flavor)

- ALWAYS define colors/fonts/dimensions in one tokens/config unit — NEVER hardcode a hex in a scene. The project owns its palette; ask the user or use a neutral default until supplied.
- ALWAYS ease/spring entries — NEVER linear motion (reads as cheap). Clamp interpolations so values don't fly off-screen.
- ALWAYS stagger sibling reveals (~8 frames / ~0.08s) — simultaneous reveals look flat. Hold nothing perfectly still (subtle idle float/glow).
- ALWAYS communicate in bold headlines + visual flow, max 2 lines/scene — NEVER paragraphs or bullet walls on screen. Fill 80%+ of canvas.

## Voiceover + captions

The `vo` line drives both audio and caption timing.

1. TTS each `vo` → wav (Edge TTS free / OpenAI / ElevenLabs with a key). One wav per scene.
2. `faster-whisper` for word-level timestamps on the *rendered* wav — ALWAYS align captions to whisper timings, NEVER to the input text (TTS pacing drifts).
3. Per-word highlight captions (TikTok style, 1-3 words). Burn into the mp4 for autoplay; also emit `.srt`.
4. NEVER speak a URL — caption/description only.

## Pre-ship checklist

- [ ] Colors from one config; one sans font; `tabular-nums` on counters
- [ ] Eased/sprung entries; clamped interpolations; staggered reveals
- [ ] Non-breaking spaces; headlines fill the canvas
- [ ] Type-check / build passes before the (slow) render
- [ ] No brand name, person, or internal code name on screen unless the user supplied it for THIS video
