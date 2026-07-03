---
name: create
description: Router for creative artifact generation — web pages, videos, generative art, diagrams. NOT for code (use language skills), Unicode box diagrams in docs (use diagrams), de-AI-ing prose (use humanize), or generating eval skills (use create-eval).
when_to_use: "landing page, HTML mockup, deck, reveal.js presentation, code talk slides, knowledge-session deck, sketch UI variants, wireframe, design tokens, DESIGN.md, make it look like Stripe/Linear/Vercel, video script, shorts/reel/TikTok, render video to MP4/GIF, Remotion, Motion Canvas, Manim, 3Blue1Brown math animation, p5.js, generative art, shaders, ASCII art, figlet, ASCII video, matrix effect, audio visualizer, pretext, kinetic typography, Excalidraw, architecture diagram, flowchart, SVG infra diagram"
user-invocable: true
---

# Create — artifact router

Only this file preloads. ALWAYS read exactly ONE matched file below, then only
the subtree files it references (`<mode>/<slug>/references/...`, `scripts/`,
`templates/`). Paths are relative to this directory.

## Dispatch

| If the request is | Read |
|---|---|
| landing page, deck, HTML prototype, from-scratch design with taste | `web.md` § Claude Design |
| reveal.js slides / code talk from a feature-work doc for a knowledge session | `web/code-presentation.md` |
| throwaway mockups — 2-3 design variants to compare before building | `web.md` § Sketch |
| DESIGN.md file, design tokens, token spec, WCAG/Tailwind/DTCG export | `web/design-md.md` |
| "look like Stripe/Linear/Vercel/Notion/..." — 54 real design systems | `web/popular-web-designs.md` |
| video script: shorts, reels, TikTok, X video, voiceover (45-75s) | `video.md` |
| render a script to MP4 — Remotion, Motion Canvas, Bevy, swarm, shaders | `video/render.md` |
| math/algorithm animation, 3Blue1Brown style, Manim CE | `video/manim.md` |
| static ASCII art: figlet banners, cowsay, boxes, image-to-ascii | `art.md` |
| ASCII video/animation, audio-reactive ASCII, matrix effects | `art/ascii-video.md` |
| p5.js, generative art, shaders, canvas, interactive/3D/audio sketches | `art/p5js.md` |
| pretext demos: text flowing around obstacles, text-as-geometry games | `art/pretext.md` |
| hand-drawn-style diagram JSON for excalidraw.com | `diagram/excalidraw.md` |
| dark-themed SVG architecture/cloud/infra diagram as HTML | `diagram/architecture-diagram.md` |

## Rules

- ALWAYS load one mode file first; NEVER bulk-read a subtree — each mode file
  indexes its own `references/`, `scripts/`, `templates/`.
- NEVER combine modes unless the artifact genuinely needs both (brand look +
  landing page = `web/popular-web-designs.md` + `web.md`; ASCII look in p5.js
  stays in `art/p5js.md`).
- Manim via the script-to-video pipeline → `video/render.md` flavor table;
  Manim as the primary deliverable → `video/manim.md`.

Related, NOT in this router: `humanize` (strip AI-isms from prose),
`diagrams` (Unicode box diagrams inside docs), `create-eval` (scaffold a
project eval skill).
