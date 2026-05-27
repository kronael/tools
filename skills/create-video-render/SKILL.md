---
name: create-video-render
description: Render short-form videos with Remotion (React + TypeScript → mp4). Motion design — spring animations, scene composition, transitions. NOT for writing the script (use create-video-script) or static UI (use visual).
when_to_use: "render the video", "build a Remotion video", "animate this script", "motion design", "make an mp4", "social video from a script", "scene composition"
user-invocable: true
---

# Video Render (Remotion)

Second stage of the video pipeline: takes a script from [`create-video-script`](../create-video-script/SKILL.md) and turns it into an mp4. Pure Remotion — `spring()` + `interpolate()`, no external animation libs.

## Stack

- Remotion 4.x, React 18, TypeScript
- `@remotion/transitions` (`TransitionSeries`, `fade()`, `linearTiming`)
- `@remotion/zod-types` + `zod` for Studio parameter editing
- One sans font for all text including numbers; `tabular-nums` on counters

## Project structure

```
src/
  Root.tsx        # composition registration, dynamic frame total
  Video.tsx       # TransitionSeries orchestration
  tokens.ts       # colors, fonts, dimensions, scene durations
  scenes/         # one file per scene (HookScene.tsx, ...)
  components/      # reusable visual elements (AnimatedBackground, icons)
```

## Tokens

- ALWAYS define colors, fonts, dimensions, and scene durations in `tokens.ts`. NEVER hardcode a hex value in a scene file — a palette change must be one edit.
- The project owns its palette. Ask the user for brand colors/fonts up front, or use a neutral default (`#FFFFFF` background, near-black foreground, one accent) until they supply them.
- ALWAYS pull asset/token colors (coin icons, third-party logos) from their official brand hex, defined once in `tokens.ts`.

## Specs

```ts
export const VIDEO_WIDTH = 1920;   // 9:16 → swap to 1080x1920 for Shorts/TikTok/Reels
export const VIDEO_HEIGHT = 1080;
export const VIDEO_FPS = 30;
export const TRANSITION_DURATION = 12; // frames per fade
```

- Short scenes (hook, CTA): ~72 frames (~2.4s). Medium: 78-120. Long (demo/flow): 120-150.
- Total social video: 15-20s. Frame total = Σ scene durations − (numTransitions × TRANSITION_DURATION); `TransitionSeries` computes it.

## Scene architecture

```tsx
<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={SCENE_DURATIONS.hook}>
    <HookScene />
  </TransitionSeries.Sequence>
  <TransitionSeries.Transition presentation={fade()} timing={T} />
  ...
</TransitionSeries>
```

Every scene: `AbsoluteFill` → `AnimatedBackground` first child → content. Drive everything off `useCurrentFrame()` + `useVideoConfig().fps`.

## Animation rules

- ALWAYS animate entries with `spring()`, NEVER linear or CSS transitions — springs read as intentional, linears read as cheap.
- ALWAYS put `extrapolateRight: "clamp"` (and usually `extrapolateLeft: "clamp"`) on every `interpolate()` — unclamped values overshoot off-screen.
- ALWAYS stagger multi-element reveals by ~8 frames — simultaneous reveals look flat.
- ALWAYS `Math.max(0, frame - startFrame)` as the spring frame so a delayed element doesn't pre-animate.

### Spring presets

| use | config |
|---|---|
| Headline pop-in | `{ damping: 20, stiffness: 200 }` |
| Smooth slide | `{ damping: 200 }, durationInFrames: 16` |
| Bouncy emphasis | `{ damping: 14, stiffness: 180 }` |
| Weighty entry (coin/card) | `{ damping: 200 }, durationInFrames: 16-20` |

### Idiom: counting number

```tsx
const n = interpolate(frame, [start, start + 30], [0, target], {
  extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.quad),
});
<span style={{ fontVariantNumeric: "tabular-nums" }}>{n.toFixed(2)}</span>
```

### Idiom: idle motion

`Math.sin(frame * k)` for float/wobble/glow — never let a held element sit perfectly still.

### Idiom: cursor click (UI demos)

Glide cursor with eased `interpolate` on X/Y, then a 6-frame button scale dip (`1 → 0.96 → 1`) at the click frame.

## Content rules

- ALWAYS communicate with bold headlines and visual flow, NEVER paragraphs — max 2 headline lines per scene.
- ALWAYS use `" "` (non-breaking space) to stop orphan words at line breaks.
- ALWAYS keep content large — fill 80%+ of the canvas. Headlines 88px+.
- NEVER put body text or a wall of bullets on screen; a scene is one idea.

## Layouts

- **Two-column**: headline left, card/coin right. `flexDirection: row`, `gap: 60`, `padding: 0 80px`. The default.
- **Centered stack**: logo → title → features, vertical. For reveals and CTAs.

## Render

```bash
npx remotion render src/index.ts <CompositionId> out.mp4
npx tsc --noEmit   # ALWAYS type-check first — a render failure 30s in wastes a minute
```

## Pre-ship checklist

- [ ] All colors from `tokens.ts`, no hardcoded hex in scenes
- [ ] One sans font everywhere; `tabular-nums` on animated numbers
- [ ] Non-breaking spaces preventing orphan words
- [ ] `AnimatedBackground` (or chosen backdrop) on every scene
- [ ] Springs on all entries; `extrapolateRight: "clamp"` on every interpolate
- [ ] Scene durations defined in `tokens.ts`
- [ ] `npx tsc --noEmit` passes
- [ ] No brand name, person, or internal code name on screen unless the user supplied it for THIS video
