---
name: show-me
description: Explain the current conversation topic with the smallest visual — pseudocode, call tree, component/file tree, mermaid, or a diff. NOT for permanent architecture docs (use diagrams), generated decks/pages (use create), or CSS/UI implementation (use visual).
when_to_use: "show me, draw this, diagram this, visualize this, sketch this, explain visually, show the call tree, show the component tree, quick diagram mid-conversation"
user-invocable: true
license: MIT
metadata:
  author: HumanLayer (https://github.com/humanlayer/skills)
  homepage: https://github.com/humanlayer/skills/tree/main/plugins/show-me
---

# Show Me

Explain the CURRENT conversation topic — not a permanent doc, not a
generated artifact. Pick the smallest visual that makes the point, then stop.

## Choosing the form

- Logic or an algorithm → pseudocode.
- Runtime control flow → an indented call tree, caller above callee.
- UI or module structure → a component tree annotated with the owning file
  path.
- Cross-service or async interaction → a mermaid sequence/flow diagram.
- File layout or ownership → a shallow directory tree, one-line role per
  entry.
- A change to any of the above → a `diff`-shaped block matching that same
  shape (+/- lines), not prose describing the change.
- Layout, visual state comparison, or anything too dense for text/mermaid →
  one local HTML file matching the project's real colors/type/spacing,
  opened with `Bash(open <path>)`.

## ALWAYS

- ALWAYS pick one form, rarely two — never stack every form for the same
  question.
- ALWAYS use real identifiers from the codebase (files, functions,
  components) — never placeholder names.
- ALWAYS trim to only the calls/props/states/boundaries the current question
  needs.
- ALWAYS keep prose to one or two sentences next to the visual — the visual
  does the explaining.
- ALWAYS write the HTML fallback to a scratch path and open it locally.

## NEVER

- NEVER publish the HTML fallback as a claude.ai Artifact — this repo is
  local-output only (root `CLAUDE.md`); ALWAYS use `open` on a local file
  instead.
- NEVER reach for the HTML form first — ALWAYS try text or mermaid before
  falling back to HTML for density.
- NEVER let the visual outlive the conversation turn as a checked-in doc —
  persistent diagrams belong to `diagrams` or `specs`, not here.
- NEVER build a multi-artboard deck or long-form asset here — that's
  `create`'s job.

Ported and adapted from [humanlayer/skills](https://github.com/humanlayer/skills)
`show-me` (MIT, © 2026 HumanLayer).
