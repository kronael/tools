---
name: readme
description: Router for project-facing documentation — syncing README/ARCHITECTURE to the code, the house repo and doc layout (one question per file), the section order inside one integration or API-reference page, the public one-page summary and the HTML explainer page under docs/. NOT for design specs (use specs) or how a doc reads and looks — prose, headers, boxes, sources, links (use writing).
when_to_use: "update the readme, sync README ARCHITECTURE CHANGELOG after shipping; structure project docs, repo layout, README vs PLAN vs ARCHITECTURE vs FEATURES split, docs are one wall, how-to-read-this index, reading order, numbers ledger, verified.md, every number cites its command, feature cites its test, per-package CLAUDE.md, what to gitignore, do we need a CHANGELOG, anti-marketing docs, good docs like X quality; docs site, VitePress sidebar, status line, what it costs, region include, doc snippets compiled; structure an integration guide, INTEGRATE.md, example page, recipe page, API reference page layout, order sections in one document, examples before or after parameters, where errors go, diataxis on one page, walkthrough mixed with reference, single-page API docs; onepager, one-page summary, exec summary, public page for the project, explain this project to outsiders, tl;dr page; explainer page, doc page with diagrams, docs/*.html"
user-invocable: true
---

# Readme — project documentation router

Only this file preloads. ALWAYS read exactly ONE matched file below.
Paths are relative to this directory.
ALWAYS load the `writing` skill before drafting or editing prose in any mode.

| If you need | Read |
|---|---|
| to bring existing docs back in line with shipped code — README, ARCHITECTURE, CHANGELOG edits, the sync protocol and where it runs; the README opening order (what, link row, status line, why, how to start) and the one status wording; the cost rule (formula with every term, one figure it reproduces); doc code taken from compiled, tested files by region include, the README example copied from a guide region | `sync.md` |
| to decide WHICH file a fact belongs in, or to lay out a repo and its docs — the house layout: README, PLAN (why), ARCHITECTURE (where), FEATURES (a test per row), BUGS, the study page, the numbers ledger `verified.md`, root and per-package CLAUDE.md, the reading order, README as a docs-site hub, generated counts vs typed measured figures, the examples-index verdict column, what `make lint` checks, what is tracked and what stays local, CHANGELOG or not | `topology.md` |
| the order of sections INSIDE one integration guide, API-reference page or example page — guide vs reference shape, examples before or after parameters, where errors go, Diátaxis on one page, an example or recipe page from Status to What has been tested, and the doc-site sidebar order (guide groups, then reference) | `shape.md` |
| one self-contained public HTML page for a stranger — what it is, who it is for, what is different, what it costs, what to do next, published to the web root | `onepager.md` |
| one HTML explainer page under `docs/` for someone who will use or change the code — what it holds (sections, inline SVG flow diagrams, claims backed by tests) and the fact pass on refine; how it reads and looks is the `writing` skill | `page.md` |

Audience decides the file: `sync.md`, `topology.md`, `shape.md` and `page.md`
write for someone who will use or change the code, `onepager.md` writes for
someone deciding whether to care at all. NEVER let a onepager claim what the project's own `BUGS.md` or
`.claude/plans/critique-*.md` contradicts.
