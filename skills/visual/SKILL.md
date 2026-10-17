---
name: visual
description: /visual — UI and styling via headful browser. NOT for general code (use improve).
when_to_use: "SVG/CSS/UI tweaks, components, landing pages, dashboards, improve the UI, fix the styling, beautify"
user-invocable: true
---

# Visual — render-inspect-adjust

Refine visual elements by changing one thing, rendering, reading the pixels,
and adjusting. Render commands, SVG gotchas and email constraints live in
`render.md` in this directory — ALWAYS read it before the first render.

## Where it runs

Screenshots fill a context fast. Invoked in the main thread, ALWAYS hand the
loop to a subagent and keep the conversation here: `Agent(subagent_type:
visual)`, the thin agent that loads this skill, or `opus` told to "Load the
`visual` skill (Skill tool) and follow it" when the brief needs design
judgment. Give the files, the URL or render command, and what done looks like. A
subagent that loaded this skill runs the loop itself.

## Core protocol

NEVER design blind: ALWAYS render after each change, read the image with the
Read tool, then adjust. The default drift is 3-5 blind changes before one
render.

1. Change one visual element.
2. Open it in the browser (web UI) or render it to PNG (SVG, PDF).
3. Exercise the relevant states — hover, click, scroll, focus.
4. Screenshot and Read the image. REQUIRED.
5. Criticize in measurements, never feelings — "heading sits 4px off the
   grid", not "spacing is off".
6. Adjust ONE thing.
7. Repeat from step 2.

ALWAYS render every viewport the UI claims to support; NEVER trust responsive
rules unrendered.

## Rules other skills own

- ALWAYS read `~/.claude/skills/writing/page.md` before changing the look of
  any page, document or diagram — the owner rejects every pattern it lists on
  sight as "AI slop". NEVER ship a page without checking it against that file.
- A design recommendation — UX, visual, typography, layout, colour — follows
  the `eval` skill's design lens (`eval/design.md`) sourcing rule: a named
  published source with its
  URL, or labeled as your own opinion.
- Web UI renders through the `agent-browser` CLI (`browse` skill), headful.
  NEVER `npx playwright screenshot` or ad-hoc browser tooling — it loses
  interaction and drifts from the shared browser layer.

## Anti-patterns

- Three changes, then one render.
- Skipping the render because it "should work".
- A screenshot of the static initial state when the UI has hover, focus or
  scroll states.
- A screenshot taken and never Read.
