# software/ — edit reference

Router for deep engineering runbooks; `../ops/SKILL.md` keeps only terse hot
rules + a pointer table. Convention: `../CLAUDE.md`.

## What lives where

The dispatch table in `SKILL.md` is the one index of these files — it names
each runbook and what it holds. `code.md` is the base every language skill
reads first (its ALWAYS Read line).

## Editing rules

- A runbook (>10 lines, code blocks, procedures) goes HERE; a one-line
  ALWAYS/NEVER rule goes in `../ops/SKILL.md`. NEVER both — no duplication.
- New runbook → new `<topic>.md` + dispatch row in `SKILL.md` + keywords in
  its `when_to_use` (trimmed — it preloads).
- ops' pointer table mirrors ONLY the devops runbooks (docker/ci/deploy/
  observe/uvx-tools). A non-devops page
  (e.g. `code.md`, `strict-typing.md`) gets NO ops row; it routes via this
  SKILL.md only.
- When you do add/rename a devops runbook, keep ops' table in sync:
  ops links here as `../software/<topic>.md`.
