---
name: readme
description: /readme — update docs via agent. NOT for new docs (write directly) or design specs (use specs).
when_to_use: "sync README, ARCHITECTURE, CHANGELOG after shipping, update the readme"
user-invocable: true
---

Launch the @readme agent (Task tool, subagent_type: readme) to update README, ARCHITECTURE, and documentation files. Doc prose follows the `writing` skill's copy rules.

README opens **what → why → how**: one jargon-free sentence a 13-year-old understands, then the gap it fills, then a runnable quick start — in that order, before anything else. ARCHITECTURE is written for a senior engineer changing the code: diagrams are mandatory (component + data flow for the primary write and read paths), no fluff, and every decision names the alternative it rejected. See the `doc-topology` skill for the one-question-per-file split.

NEVER mention how a feature was arrived at, internal plan names, goal codenames, or project-history references — docs describe what code does, not how it was designed or named internally. ALWAYS write as if the reader has no prior context on the project's decision history.
