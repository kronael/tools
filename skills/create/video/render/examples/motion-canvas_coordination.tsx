// Coordinated activation wave across a node graph — Motion Canvas.
// Agents (nodes) light up in a propagating wave, the timing-first metaphor
// for coordination spreading through a distributed system. Motion Canvas's
// generator timeline makes choreographed propagation natural — you `yield*`
// the wave, you don't compute per-frame.
//
// Scaffold + render:
//   npm init @motion-canvas@latest    # pick the TS template
//   # drop this in src/scenes/, register in project.ts
//   npm run build  →  output/ has the mp4 (or use the editor's Render tab)

import { makeScene2D, Circle, Line } from '@motion-canvas/2d';
import { all, waitFor, createRef, range, Vector2 } from '@motion-canvas/core';

const ACCENT = '#3AC3BC';
const DIM = '#1d3a38';

export default makeScene2D(function* (view) {
  view.fill('#081211');

  // Ring of coordinating nodes.
  const n = 16;
  const radius = 320;
  const nodes = range(n).map((i) => {
    const a = (i / n) * Math.PI * 2;
    const ref = createRef<Circle>();
    view.add(
      <Circle
        ref={ref}
        size={36}
        fill={DIM}
        position={[Math.cos(a) * radius, Math.sin(a) * radius]}
      />,
    );
    return ref;
  });

  // Propagate an activation wave around the ring three times.
  for (let lap = 0; lap < 3; lap++) {
    for (let i = 0; i < n; i++) {
      yield* nodes[i]().fill(ACCENT, 0.08);
      yield nodes[i]().fill(DIM, 0.5); // fade back, not awaited → overlap
    }
  }

  // Then full sync: every node pulses together (coordination achieved).
  yield* waitFor(0.2);
  yield* all(...nodes.map((r) => r().fill(ACCENT, 0.4).to(DIM, 0.6)));
});
