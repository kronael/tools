# Flavor: Shaders & declarative diagrams

Two ends of the spectrum that don't fit the others.

## Fragment-shader field dynamics

**Pick when**: the whole frame is a continuous field computed per-pixel (flow, plasma, distance-field morphs) — demoscene aesthetic, maximum visual ceiling.

- **Bonzomatic** — open-source (zlib) GLSL live-coder; a compute-shader fork exists. No built-in export; capture via FFmpeg or NDI.
- **KodeLife** — polished GLSL live-coder (proprietary, free tier). Same capture story.
- **Raw WebGPU/GLSL** — render to an offscreen FBO per tick → read back → frame seq → ffmpeg. Browser path: `CCapture.js` / `webm-writer` then ffmpeg. Highest ceiling, most bespoke; agents as GPU particles in SSBOs, coordination as force fields.

## Declarative math diagrams

**Pick when**: you want LaTeX-grade figures where layout should be *solved*, not hand-placed.

- **Penrose** — describe a diagram in a notation DSL + constraints; it optimizes the layout and exports SVG (incl. SVG-TeX). Script `roger trio` → SVG → frames → ffmpeg for morphing figures. Not an imperative timeline like Manim — you state relationships, it solves positions.

## Picking

- Continuous per-pixel field, demoscene look → Bonzomatic/KodeLife or raw shaders.
- Million-agent GPU particle field with full control → raw WebGPU/GLSL.
- Constraint-solved math figure / commutative diagram → Penrose.

Sources: [Bonzomatic](https://github.com/Gargaj/Bonzomatic) · [Bonzomatic + ffmpeg capture](https://blog.totetmatt.fr/posts/2021-06-05_bonzomatic_ffmpeg/) · [KodeLife](https://hexler.net/kodelife) · [Penrose](https://penrose.cs.cmu.edu/blog/v3)
