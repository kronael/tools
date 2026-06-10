// Kuramoto sync in Remotion — frame-driven, deterministic (no useState).
// Each frame re-derives every phase from the closed-form-ish Euler rollout
// seeded once, so any frame is reproducible. This is the Remotion idiom:
// the video is a pure function of `frame`.
//
// Scaffold + render:
//   npm create video@latest   # pick Blank
//   # drop this file in src/, register <Composition id="kuramoto" .../> in Root.tsx
//   npx remotion render src/index.ts kuramoto out.mp4
//
// Composition: durationInFrames=300, fps=30, width=1080, height=1920.

import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';

const N = 60;
const K = 1.6;
const DT = 0.04;

// Deterministic seed → natural frequencies + initial phases.
function seed() {
  let s = 7;
  const rand = () => ((s = (s * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff);
  const omega = Array.from({ length: N }, () => (rand() - 0.5) * 1.2);
  const theta0 = Array.from({ length: N }, () => rand() * Math.PI * 2);
  return { omega, theta0 };
}

const { omega, theta0 } = seed();

// Roll the ODE forward to `frame` steps. Cheap enough to redo per frame at N=60.
function phasesAt(frame: number): number[] {
  const theta = [...theta0];
  for (let step = 0; step < frame; step++) {
    let re = 0;
    let im = 0;
    for (const t of theta) {
      re += Math.cos(t);
      im += Math.sin(t);
    }
    const r = Math.hypot(re, im) / N;
    const psi = Math.atan2(im, re);
    for (let i = 0; i < N; i++) theta[i] += DT * (omega[i] + K * r * Math.sin(psi - theta[i]));
  }
  return theta;
}

export const KuramotoScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const theta = phasesAt(frame);
  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.min(width, height) * 0.32;

  let re = 0;
  let im = 0;
  for (const t of theta) {
    re += Math.cos(t);
    im += Math.sin(t);
  }
  const order = (Math.hypot(re, im) / N).toFixed(2);

  return (
    <AbsoluteFill style={{ background: '#081211' }}>
      <svg width={width} height={height}>
        <circle cx={cx} cy={cy} r={radius} fill="none" stroke="#3AC3BC" strokeOpacity={0.4} strokeWidth={2} />
        {theta.map((t, i) => (
          <circle key={i} cx={cx + radius * Math.cos(t)} cy={cy + radius * Math.sin(t)} r={7} fill="#3AC3BC" />
        ))}
        <text x={cx} y={cy} fill="#F6F9F9" fontSize={64} fontFamily="sans-serif" textAnchor="middle" style={{ fontVariantNumeric: 'tabular-nums' }}>
          r = {order}
        </text>
      </svg>
    </AbsoluteFill>
  );
};
