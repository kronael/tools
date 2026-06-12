# create/ — edit reference

Router for creative artifact generation. `SKILL.md` is the only preloaded
file; everything else is cold data. Convention: `../CLAUDE.md`.

## What lives where

| File | Holds | Origin |
|---|---|---|
| `web.md` | Claude Design process/taste + § Sketch (2-3 throwaway variants) | create-claude-design, create-sketch |
| `web/design-md.md` + `web/design-md/` | Google DESIGN.md token specs | create-design-md |
| `web/popular-web-designs.md` + `web/popular-web-designs/templates/` | 54 brand design systems | create-popular-web-designs |
| `video.md` | short-form video script writing | create-video-script |
| `video/render.md` + `video/render/{flavors,examples}/` | script→mp4 engine index | create-video-render |
| `video/manim.md` + `video/manim/` | Manim CE pipeline | create-manim-video |
| `art.md` | static ASCII art (pyfiglet, cowsay, boxes) | create-ascii-art |
| `art/ascii-video.md` + `art/ascii-video/` | ASCII video pipeline | create-ascii-video |
| `art/p5js.md` + `art/p5js/` | p5.js generative art pipeline | create-p5js |
| `art/pretext.md` + `art/pretext/` | pretext text-layout demos | create-pretext |
| `diagram/excalidraw.md` + `diagram/excalidraw/` | Excalidraw JSON diagrams | create-excalidraw |
| `diagram/architecture-diagram.md` + `diagram/architecture-diagram/` | dark SVG infra diagrams | create-architecture-diagram |

## Editing rules

- New light mode → flat `<mode>.md`; heavy ported tree → `<mode>/<slug>.md`
  + `<mode>/<slug>/` moved intact. Then: dispatch row in `SKILL.md` +
  keywords in its `when_to_use` (trimmed — it preloads).
- Paths inside `<mode>/<slug>.md` are prefixed with `<slug>/`
  (e.g. `p5js/references/core-api.md`); paths inside the subtree stay
  subtree-relative. Keep that invariant when editing.
- Ported files keep their frontmatter (author/license) — attribution;
  `../../NOTICE` points at it. Update NOTICE when adding/removing a port.
- Only port generators that run locally — no paid APIs, no cloud accounts;
  local CLI/lib deps (ffmpeg, manim, pyfiglet) are fine.
- `humanize` and `create-eval` are NOT in this router — leave them flat.
