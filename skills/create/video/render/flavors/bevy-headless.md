# Flavor: Bevy headless (Rust ECS → mp4)

**Pick when**: the video should be driven by a *real* agent simulation, not a mock. Bevy's ECS *is* an agent-orchestration model — one entity per agent/container, systems for the coordination logic. You render the actual sim's state, frame by frame. Highest niche × ceiling for an orchestration theme like arizuko.

## How it renders headless

Bevy's official [`headless_renderer`](https://github.com/bevyengine/bevy/blob/main/examples/app/headless_renderer.rs) example: render to an offscreen target → copy the GPU buffer back to CPU → write a PNG per frame, no display server. The [`bevy_headless_render`](https://crates.io/crates/bevy_headless_render) crate automates the copy-back loop. Then:

```bash
ffmpeg -framerate 60 -i frames/%05d.png -c:v libx264 -pix_fmt yuv420p out.mp4
```

## Why ECS fits coordination

- Entity = agent/container; Components = its state (phase, position, load); Systems = the coordination rules (coupling, message-passing, scheduling).
- The same code that *simulates* coordination *is* the source of the visual — no separate animation model to keep in sync with the logic.
- Compute shaders (wgpu) for field-scale effects (thousands of agents as GPU particles).

## Strengths / limits

- Strength: simulate and render in one Rust binary; deterministic; mirrors the real orchestration domain.
- Limit: Rust + wgpu setup cost; overkill for a talking-head or simple title card.

Sibling realtime options if Rust isn't wanted: **nannou** (lighter Rust generative, `capture_frame`), **Taichi** (Python GPU fields) — see [fields-swarm.md](fields-swarm.md).
