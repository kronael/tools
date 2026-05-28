# Flavor: Manim (Python → mp4)

**Pick when**: the subject is math — formulae, plots, geometry, step-by-step derivations (3Blue1Brown style). Nothing else renders LaTeX-grade math motion as cleanly.

## Setup

```bash
uv run --with manim manim -qh scene.py SceneName
# -ql draft 480p · -qh 1080p60 · -qk 4k
```

## Idioms

- A `Scene.construct()` is imperative: `self.play(Create(obj), run_time=…)`, `self.wait(dt)`.
- `always_redraw(fn)` re-renders a mobject every frame — the hook for live simulation state.
- Animate values with `ValueTracker` + `.add_updater`, or drive a closure off an external frame list.
- `MathTex`/`Tex` for LaTeX; `Axes`, `NumberPlane`, `ParametricFunction`, `StreamLines` for dynamics.
- Quality is a render flag, not code — keep scenes resolution-agnostic.

## Strengths / limits

- Strength: correct math, vector fields, transforms, LaTeX labels.
- Limit: not for UI demos or web-styled content; no CSS/HTML.

Example: [`../examples/manim_kuramoto.py`](../examples/manim_kuramoto.py) — coupled oscillators converging to phase sync, order parameter on screen.
