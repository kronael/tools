# Syncing docs to the code

Launch the @readme agent (Task tool, subagent_type: readme) to update README,
ARCHITECTURE, and documentation files. Doc prose follows the `writing` skill's
copy rules.

NEVER mention how a feature was arrived at, internal plan names, goal
codenames, or project-history references — docs describe what code does, not
how it was designed or named internally. ALWAYS write as if the reader has no
prior context on the project's decision history.

ALWAYS check which file owns the claim before editing — `topology.md` in this
directory says which question each doc answers; a fact edited into the wrong
file is doc rot even when the fact is right.
