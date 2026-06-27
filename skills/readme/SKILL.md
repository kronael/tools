---
name: readme
description: /readme — update docs via agent. NOT for new docs (write directly) or design specs (use specs).
when_to_use: "sync README, ARCHITECTURE, CHANGELOG after shipping, update the readme"
user-invocable: true
---

Launch the @readme agent (Task tool, subagent_type: readme) to update README, ARCHITECTURE, and documentation files. Doc prose follows the `writing` skill's copy rules.

NEVER mention how a feature was arrived at, internal plan names, goal codenames, or project-history references — docs describe what code does, not how it was designed or named internally. ALWAYS write as if the reader has no prior context on the project's decision history.
