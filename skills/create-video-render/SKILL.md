---
name: create-video-render
description: Render short-form video from a script via Remotion (React/TS → mp4). NOT for writing the script (use create-video-script) or static UI (use visual).
when_to_use: "render the video", "build a Remotion video", "animate this script", "motion design", "make an mp4", "social video from a script", "scene composition", "captions", "voiceover"
user-invocable: true
---

# Video Render

Turns a prose script from [`create-video-script`](../create-video-script/SKILL.md) into an mp4. This skill carries house style + the script→render bridge + the voiceover/caption pipeline — NOT Remotion API reference.

- ALWAYS defer Remotion API correctness (transitions, audio, 3D, charts, perf) to the official bundle: `npx remotion skills`. NEVER duplicate its rules here.
- Engine comparison, spring presets, animation idioms, and reference pipelines live in [`TECHNIQUES.md`](./TECHNIQUES.md). Read it to pick an engine.
- Remotion needs a paid license for company use — for redistributable work, Revideo (open-source) is the swap. Surface this before standardizing.

## Bridge: prose script → scenes

Derive structure from the script; NEVER ask the author for JSON.

- Bracketed `[direction]` line → `visual` (not spoken).
- Plain line → `vo` (spoken; drives TTS + caption timing).
- Blank line → scene boundary. Estimate `duration_s` from `vo` at ~2.5 words/sec.

## Rules

- ALWAYS define colors/fonts/dimensions/durations in `tokens.ts` — NEVER hardcode a hex in a scene. The project owns its palette; ask the user or use a neutral default until supplied.
- ALWAYS animate entries with `spring()` — NEVER linear/CSS transitions (they read as cheap).
- ALWAYS clamp every `interpolate()` (`extrapolateRight`/`Left: "clamp"`) — unclamped values fly off-screen.
- ALWAYS stagger sibling reveals ~8 frames — simultaneous reveals look flat.
- ALWAYS communicate in bold headlines + visual flow, max 2 lines/scene — NEVER paragraphs or bullet walls on screen.
- ALWAYS fill 80%+ of canvas (headlines 88px+) and use `" "` to stop orphan words.

## Voiceover + captions

The `vo` line drives both audio and caption timing.

1. TTS each `vo` → wav (Edge TTS free / OpenAI / ElevenLabs with a key). One wav per scene.
2. `faster-whisper` for word-level timestamps on the rendered wav — ALWAYS align captions to whisper timings, NEVER to the input text (TTS pacing drifts).
3. Per-word highlight captions (TikTok style, 1-3 words). Burn into the mp4 for autoplay; also emit `.srt`.
4. NEVER speak a URL — it goes in the caption/description only.

## Render

```bash
npx tsc --noEmit && npx remotion render src/index.ts <CompositionId> out.mp4
```

## Pre-ship checklist

- [ ] Colors from `tokens.ts`; one sans font; `tabular-nums` on counters
- [ ] Springs on entries; every `interpolate()` clamped; ~8-frame stagger
- [ ] Non-breaking spaces; headlines fill the canvas
- [ ] `npx tsc --noEmit` passes
- [ ] No brand name, person, or internal code name on screen unless the user supplied it for THIS video
