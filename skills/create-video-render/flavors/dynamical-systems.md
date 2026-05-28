# Flavor: DynamicalSystems.jl + Makie (Julia → mp4)

**Pick when**: you need *correct* dynamical-systems math — phase portraits, strange attractors, basins of attraction, Lyapunov spectra, recurrence. The research-grade answer, not a pretty approximation.

## Setup

```julia
using DynamicalSystems, GLMakie
# build a DynamicalSystem, integrate trajectories, then:
record(fig, "out.mp4", frames; framerate=60) do i
    # mutate Observables for frame i
end
```

GLMakie needs a GPU/EGL context but renders headless. FFMPEG.jl backs `record` — emits mp4 directly, no frame-sequence juggling.

## What it covers

- `trajectory`, `lyapunov`, `basins_of_attraction`, `poincaresos`, recurrence plots — all first-class.
- Couple with **BifurcationKit.jl** for numerical continuation (Hopf, fold, period-doubling, codim-2) — the only serious open-source continuation engine. Animate a branch sweeping a parameter via Makie `record`.
- Makie `Observable`s are the animation primitive: bind plot data to an observable, mutate it per frame.

## Strengths / limits

- Strength: the math is right (built by the dynamical-systems research community); trivial mp4 export.
- Limit: Julia toolchain + first-call latency; not for UI/social-styled content.

Use for the arizuko coordination theme when you want provably-correct phase-space behavior (e.g. Kuramoto order-parameter dynamics, coupling-strength bifurcation).

Sources: [DynamicalSystems.jl visualizations](https://juliadynamics.github.io/DynamicalSystems.jl/dev/visualizations/) · [Makie animations](https://docs.makie.org/stable/documentation/animation/) · [BifurcationKit.jl](https://github.com/bifurcationkit/BifurcationKit.jl)
