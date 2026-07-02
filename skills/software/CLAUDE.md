# software/ — edit reference

Router for deep engineering runbooks extracted from `../ops/SKILL.md`
(which keeps only terse hot rules + a pointer table). Convention:
`../CLAUDE.md`.

## What lives where

| File | Holds |
|---|---|
| `code.md` | language-agnostic code baseline: naming, layout, design, boring-code, grug — the base every language skill pulls in via `requires: software` |
| `docker.md` | Python+uv two-layer Dockerfile, m4 monorepo Dockerfile generation |
| `ci.md` | Makefile pattern for Python+uv (prepare/build/test/right/image/clean) |
| `deploy.md` | Ansible docker-service role, per-deployable subdir layout |
| `observe.md` | logging format, monitoring, alerting, error-handling hierarchy |
| `uvx-tools.md` | PEP 723 single-file scripts, uvx distribution, package layout |

## Editing rules

- A runbook (>10 lines, code blocks, procedures) goes HERE; a one-line
  ALWAYS/NEVER rule goes in `../ops/SKILL.md`. NEVER both — no duplication.
- New runbook → new `<topic>.md` + dispatch row in `SKILL.md` + keywords in
  its `when_to_use` (trimmed — it preloads) + row in ops' pointer table.
- ops links here as `../software/<topic>.md` — keep both tables in sync.
