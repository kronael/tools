# Flavor: Motion Canvas / Revideo (TS → mp4)

**Pick when**: the animation IS the message — choreographed, timing-first sequences where you want a timeline you `yield*` through rather than per-frame math. Also when you need a license-free engine (Remotion's open-source swap).

- **Motion Canvas**: canvas scene-graph, real-time editor, truly open source. No arbitrary HTML/CSS — draw with `Circle`, `Rect`, `Txt`, `Line`, `Img`.
- **Revideo**: Motion Canvas fork that adds a Node `renderVideo()` API — first-class server-side/queue/cron rendering. Use for automated pipelines.

## Setup

```bash
npm init @motion-canvas@latest    # TS template; render via editor or build
# Revideo: npm i @revideo/core @revideo/2d ; renderVideo() from a Node script
```

## Idioms

- Scenes are generator functions: `makeScene2D(function* (view) { … })`.
- Animate by awaiting tweens: `yield* node().fill(color, 0.3)`, `yield* all(a, b)`, `yield* waitFor(t)`.
- `yield` (not `yield*`) fires a tween without awaiting → overlapping/staggered motion.
- Refs via `createRef<T>()`; `range(n).map(...)` to build many coordinated nodes.

## Strengths / limits

- Strength: pixel-accurate, fast canvas render; choreography reads naturally.
- Limit: no HTML/CSS/web fonts as DOM; everything is canvas primitives.

Example: [`../examples/motion-canvas_coordination.tsx`](../examples/motion-canvas_coordination.tsx) — activation wave around a node ring, then full sync.
