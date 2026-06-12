# Flavor: Remotion (React/TS → mp4)

**Pick when**: React is the stack, the video is data-driven, or you need any CSS/SVG/web-font visual. The default web path.

Defer API correctness to the official bundle: `npx remotion skills` (28 maintained rule files). This file is the house minimum.

**License**: paid for company use. For redistributable work swap to Motion Canvas/Revideo ([motion-canvas.md](motion-canvas.md)).

## Setup

```bash
npm create video@latest    # pick Blank
npx remotion render src/index.ts <CompositionId> out.mp4
```

Layout: `Root.tsx` (register compositions) · `Video.tsx` (`TransitionSeries`) · `tokens.ts` (colors/fonts/dims/durations) · `scenes/` · `components/`.

Specs: 1920×1080 (or 1080×1920 vertical), 30fps, ~12-frame fades. Durations: hook/CTA ~72 frames, medium 78-120, demo 120-150; social total 15-20s.

## Idioms

- Video is a pure function of `useCurrentFrame()` — NEVER `useState` for animation.
- Spring presets: headline pop `{damping:20,stiffness:200}`; smooth slide `{damping:200},durationInFrames:16`; bouncy `{damping:14,stiffness:180}`.
- Counting number: `interpolate(frame,[a,b],[0,target],{easing:Easing.out(Easing.quad)})` + `tabular-nums`.
- Idle motion: `Math.sin(frame*k)` for float/glow. Cursor click: eased X/Y glide then 6-frame `1→0.96→1` dip.
- ALWAYS `Math.max(0, frame-startFrame)` as spring frame so a delayed element doesn't pre-animate.

Example: [`../examples/remotion_KuramotoScene.tsx`](../examples/remotion_KuramotoScene.tsx) — frame-pure Kuramoto sync.
