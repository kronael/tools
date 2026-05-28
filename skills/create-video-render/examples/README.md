# Example videos — coordination dynamics

Four minimal, runnable examples, one per engine, all on the same theme:
**coordination emerging in a system of many agents** (Kuramoto phase-sync +
boids flocking). The metaphor for a distributed agent/container orchestrator
finding coordination.

Each file is a single source unit with its render command in the header.
None are full scaffolds — they drop into the engine's starter project.

| file | engine | what it shows | render |
|---|---|---|---|
| [`manim_kuramoto.py`](manim_kuramoto.py) | Manim | N coupled oscillators pulling into phase sync; order parameter `r` rises 0→1 | `manim -qh manim_kuramoto.py Kuramoto` |
| [`remotion_KuramotoScene.tsx`](remotion_KuramotoScene.tsx) | Remotion | same Kuramoto model, frame-pure (any frame reproducible) | `npx remotion render src/index.ts kuramoto out.mp4` |
| [`motion-canvas_coordination.tsx`](motion-canvas_coordination.tsx) | Motion Canvas | activation wave propagating a ring of nodes, then full sync | `npm run build` (or editor Render tab) |
| [`p5_boids.js`](p5_boids.js) | p5.js | boids flocking — global order from three local rules, no leader | p5.capture addon → mp4 |

## Why these engines for this theme

- **Manim / Remotion** — same model twice: Manim is terser for the math; Remotion's frame-purity makes every frame reproducible and the React stack reusable.
- **Motion Canvas** — timing-first; the `yield*` timeline expresses a propagating wave more naturally than per-frame math.
- **p5.js** — fastest path to a live agent simulation; emergent coordination with ~40 lines.

**Lottie is intentionally absent** — it replays pre-baked After Effects keyframes, so it cannot express a live simulation. It's the wrong tool for differential dynamics; included in the engine table only for completeness.

## For the real niche (differential dynamics + coordination)

These four are starting points. For research-grade dynamical-systems math or
agent-coordination at scale, see the per-flavor files:
[`../flavors/dynamical-systems.md`](../flavors/dynamical-systems.md) for
correct phase portraits / attractors / bifurcations (Julia),
[`../flavors/bevy-headless.md`](../flavors/bevy-headless.md) when the video
should be driven by a *real* ECS agent simulation, and
[`../flavors/fields-swarm.md`](../flavors/fields-swarm.md) for GPU
reaction-diffusion / fluids / swarm.
