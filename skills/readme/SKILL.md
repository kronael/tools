---
name: readme
description: Router for project-facing documentation — syncing README/ARCHITECTURE to the code, the one-question-per-file doc layout, the section order inside one integration or API-reference page, the public one-page summary and the HTML explainer page under docs/. NOT for design specs (use specs) or a single doc's prose polish (use writing).
when_to_use: "update the readme, sync README ARCHITECTURE CHANGELOG after shipping; structure project docs, README vs ARCHITECTURE split, docs are one wall, notes/compare/facts layout, how-to-read-this index, anti-marketing docs, good docs like X quality; structure an integration guide, INTEGRATE.md, API reference page layout, order sections in one document, examples before or after parameters, where errors go, diataxis on one page, walkthrough mixed with reference, single-page API docs; onepager, one-page summary, exec summary, public page for the project, explain this project to outsiders, tl;dr page; explainer page, doc page with diagrams, docs/*.html, HTML slop, strip the generated look from a page, evidence pills, sources ledger"
user-invocable: true
---

# Readme — project documentation router

Only this file preloads. ALWAYS read exactly ONE matched file below.
Paths are relative to this directory.
ALWAYS load the `writing` skill before drafting or editing prose in any mode.

| If you need | Read |
|---|---|
| to bring existing docs back in line with shipped code — README, ARCHITECTURE, CHANGELOG edits, run through the @readme agent | `sync.md` |
| to decide WHICH file a fact belongs in, or to lay out a doc set from scratch — README vs ARCHITECTURE vs `notes/` vs `compare/` vs `facts/`, the how-to-read index, dated-number chain, anti-marketing rules; the house repo layout (UPPERCASE root files, `specs/`, `docs/`, `.claude/plans/`, `.diary/`, no `todos/`, no `plans/` elsewhere, root-anchored ignores) | `topology.md` |
| the order of sections INSIDE one integration guide or API-reference page — guide vs reference shape, examples before or after parameters, where errors go, Diátaxis on one page | `shape.md` |
| one self-contained public HTML page for a stranger — what it is, who it is for, what is different, what it costs, what to do next, published to the web root | `onepager.md` |
| one HTML explainer page under `docs/` for someone who will use or change the code — sections, inline SVG flow diagrams, claims linked to tests; and stripping the generated look from one: evidence pills and ledgers, legend walls, colon headings, callout walls, unfinished diagrams, light-mode contrast, stale facts | `page.md` |

Audience decides the file: `sync.md`, `topology.md`, `shape.md` and `page.md`
write for someone who will use or change the code, `onepager.md` writes for
someone deciding whether to care at all. NEVER let a onepager claim what the project's own `BUGS.md` or
`.claude/plans/critique-*.md` contradicts.
