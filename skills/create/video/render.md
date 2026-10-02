---
name: video-render
description: Render short-form / motion / dynamical-systems video from a script. Indexes engines (Remotion, Manim, Motion Canvas, Julia, Bevy, shaders) — loads one on demand. NOT for writing the script (use ../video.md) or static UI (use visual).
when_to_use: "render the video", "build a Remotion video", "manim", "motion canvas", "animate this script", "motion design", "make an mp4", "phase portrait", "vector field", "swarm", "coupled oscillators", "differential dynamics", "coordination animation", "captions", "voiceover"
user-invocable: true
---

# Video Render — index

Turns a prose script into an mp4: educational explanations follow
[`explainer.md`](../explainer.md); promotional scripts follow
[`video.md`](../video.md). This file indexes the bridge, house style, caption
pipeline, and engines. Pick an engine, then read only its file.

Nodes for this medium: scenes → shots → layers; see `../SKILL.md` § Principle.

## Pick a flavor (load on demand)

| flavor | file | pick when |
|---|---|---|
| Remotion | [render/flavors/remotion.md](render/flavors/remotion.md) | React stack, data-driven, any CSS/SVG; the default web path |
| Manim | [render/flavors/manim.md](render/flavors/manim.md) | math — formulae, plots, geometry, derivations |
| Motion Canvas / Revideo | [render/flavors/motion-canvas.md](render/flavors/motion-canvas.md) | timing-first choreography; license-free; automated pipelines |
| DynamicalSystems.jl | [render/flavors/dynamical-systems.md](render/flavors/dynamical-systems.md) | research-grade phase portraits, attractors, basins, bifurcations |
| Bevy headless | [render/flavors/bevy-headless.md](render/flavors/bevy-headless.md) | render a *real* ECS agent simulation (orchestration themes) |
| GPU fields & swarm | [render/flavors/fields-swarm.md](render/flavors/fields-swarm.md) | reaction-diffusion, fluids, boids, Vicsek (Taichi/nannou/VisPy/p5) |
| Shaders & declarative | [render/flavors/shaders-declarative.md](render/flavors/shaders-declarative.md) | per-pixel field shaders; LaTeX-grade solved diagrams (Penrose) |

Runnable starting points for the common engines are in [`render/examples/`](render/examples/README.md).

## Bridge: prose script → scenes

Derive structure from the script; NEVER ask the author for JSON.

- Bracketed `[direction]` line → `visual` (not spoken).
- Plain line → `vo` (spoken; drives TTS + caption timing).
- Blank line → scene boundary. Estimate `duration_s` from `vo` at ~2.5 words/sec.

## House style (every flavor)

- ALWAYS define colors/fonts/dimensions in one tokens/config unit — NEVER hardcode a hex in a scene. The project owns its palette; ask the user or use a neutral default until supplied.

For educational explainers, ALWAYS follow `../explainer.md` for motion and
reading time. The following animation rules apply to promotional videos:

- ALWAYS ease/spring entries — NEVER linear motion (reads as cheap). Clamp interpolations so values don't fly off-screen.
- ALWAYS stagger sibling reveals (~8 frames / ~0.08s) — simultaneous reveals look flat. Hold nothing perfectly still (subtle idle float/glow).
- ALWAYS communicate in bold headlines + visual flow, max 2 lines/scene — NEVER paragraphs or bullet walls on screen. Fill 80%+ of canvas.

## Voiceover + captions

For narrated deliverables, the `vo` line drives audio and caption timing.
ALWAYS honor an explicitly silent video request: omit TTS and audio checks,
and ALWAYS time any captions against the visual scenes.

1. ALWAYS use an available local TTS engine for each `vo` → wav by default.
   ALWAYS verify the installed engine and voice before choosing it; NEVER
   assume a service is free or local. ALWAYS require explicit authorization
   for paid narration; a configured key is not authorization.
2. `faster-whisper` for word-level timestamps on the *rendered* wav — ALWAYS align captions to whisper timings, NEVER to the input text (TTS pacing drifts).
3. ALWAYS emit `.srt` captions. For explainers, ALWAYS use readable phrase
   captions; for promotional shorts, use per-word highlights (1-3 words).
   ALWAYS burn captions into the mp4 when needed for silent playback.
4. NEVER speak a URL — caption/description only.

## Text overlay — cards format

Every visual `[direction]` line that names on-screen text maps to a **card** in `cards.json`.
Pass to the renderer with `--cards path/to/cards.json` (or `--text "line1" "line2"` for ≤5 quick lines, auto-positioned).

```json
[
  {"text": "Arizuko 0.49.0",           "pos": "top",    "size": 2.6, "color": [255,255,255],
   "appear": 0,  "fade_in": 1.5},
  {"text": "Colony finds shortest path","pos": "bottom", "size": 1.5, "color": [200,200,200],
   "appear": 0,  "fade_in": 1.5},
  {"text": "Now 3x faster",            "pos": "mid",    "size": 2.2, "color": [255,200,50],
   "appear": 8,  "fade_in": 0.4, "hold": 4, "fade_out": 0.6}
]
```

| field | type | default | meaning |
|---|---|---|---|
| `text` | string | — | displayed string |
| `pos` | `"top"` `"upper"` `"mid"` `"lower"` `"bottom"` or float 0–1 | `"bottom"` | vertical position |
| `size` | float | 2.0 | OpenCV font scale |
| `color` | [R,G,B] | [255,255,255] | text color |
| `thick` | int | 3 | stroke thickness |
| `appear` | float | 0 | seconds into video when card starts |
| `fade_in` | float | 1.0 | seconds to fade in |
| `hold` | float or null | null | seconds to hold at full alpha; null = until end |
| `fade_out` | float | 0.5 | seconds to fade out after hold |

**Bridge rule**: map `[direction]` lines to cards by their intent:
- `[Title: "…"]` → pos top, size 2.4–2.8, white, appear 0
- `[Tagline: "…"]` → pos bottom, size 1.4–1.6, gray, appear 0
- `[Callout: "…" at Ns]` → pos mid, size 2.0–2.4, accent color, appear N, hold 3–5, fade_out 0.5
- `[Lower-third: "…"]` → pos lower, size 1.4, white, appear 0

ALWAYS derive text from the script's `vo` lines and `[direction]` labels — NEVER add text that contradicts the spoken content.

## Pre-ship checklist

- [ ] Colors from one config; one sans font; `tabular-nums` on counters
- [ ] Motion and reading time match the selected purpose; interpolations clamped
- [ ] Non-breaking spaces; promotional headlines fill the canvas
- [ ] Type-check / build passes before the (slow) render
- [ ] No brand name, person, or internal code name on screen unless the user supplied it for THIS video
