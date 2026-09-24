---
name: readme
description: "Router for project documentation — sync docs after shipping, split a project's docs by the question each file answers, order the sections inside one integration or API-reference page. NOT for prose polish (use writing) or design specs (use specs)."
when_to_use: "sync README, ARCHITECTURE, CHANGELOG after shipping, update the readme; structure project docs, doc topology, README vs ARCHITECTURE split, docs are one wall, good docs like X quality, notes/compare/facts layout, anti-marketing docs, audit doc structure, how-to-read-this index; structure an integration guide, INTEGRATE.md, API reference page layout, order sections in one document, examples before or after parameters, where errors go, diataxis on one page, walkthrough mixed with reference, multiple strategies on one page, mode signposting, single-page API docs"
user-invocable: true
---

# Readme — documentation router

Only this file preloads. Paths are relative to this directory.

| If you need | Do |
|---|---|
| sync README, ARCHITECTURE, CHANGELOG with what shipped | launch the agent below |
| which FILE answers which question — README vs ARCHITECTURE vs `notes/` `compare/` `facts/`, a how-to-read-this index, anti-marketing | read `topology.md` |
| the order of sections INSIDE one integration guide or API-reference page | read `shape.md` |

Bare `/readme` = sync.

Sync: launch the @readme agent (Task tool, subagent_type: readme) to update
README, ARCHITECTURE, and documentation files. Doc prose follows the `writing`
skill's copy rules.

NEVER mention how a feature was arrived at, internal plan names, goal codenames, or project-history references — docs describe what code does, not how it was designed or named internally. ALWAYS write as if the reader has no prior context on the project's decision history.
