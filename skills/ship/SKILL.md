---
name: ship
description: Ship multi-session work via the ship agent. Creates .ship/<NAME>/ with PROJECT + PLAN + PROGRESS + tasks.json. USE for work spanning >1 session with fixed acceptance. NOT for one-off edits, exploration, or <30min work — prefer TaskCreate.
user-invocable: true
---

# Ship

## Folder layout

`.ship/NN-NAME/` — NN is a zero-padded sequential number,
NAME is UPPERCASE-KEBAB.

- Chronological delivery order visible in `ls`
- Each project self-contained (own PROJECT + PLAN +
  PROGRESS + tasks.json)
- No phase grouping — each ship project IS a phase
- Next NN: `ls .ship/ | grep -E '^[0-9]' | tail -1` + 1

Example: `.ship/01-SIM/`, `.ship/02-SCENARIOS/`,
`.ship/03-CLI/`, `.ship/04-PERF-VERIFICATION/`,
`.ship/05-TRADE-UI/`, `.ship/06-PUBLISH/`

## Workflow

1. **Explore** — Explore agent to understand the task
2. **Write PROJECT.md** — goals, IO surfaces, tasks,
   acceptance criteria, out-of-scope
3. **Write PLAN.md** — file-level concrete changes per task
4. **Run** — `ship .ship/NN-NAME/PLAN.md`
5. **Verify** — `make build && make test`
6. **Update PROGRESS.md** after each session
7. **Clean** — once shipped, trim PROJECT/PLAN to keep
   history or archive (don't delete — useful for reference)

## PROJECT.md format

```markdown
# PROJECT.md — <name>

## Goal
<one paragraph>

## Non-goals
- <deferred scope>

## IO Surfaces
- <external APIs, files, ports, processes touched>

## Tasks
### 1. <title>
<what / files>

## Acceptance
- <verifiable check>
```

## Relationship to other tracking

| Location | Purpose |
|----------|---------|
| `TaskCreate` | In-session multi-step tracking, <30min |
| `TODO.md` | Light backlog — items not yet a ship project |
| `.ship/NN-NAME/` | >1-session work with fixed acceptance |
| `specs/N/*.md` | Long-lived architectural reference |

Items graduate: `TODO.md` item grows acceptance criteria →
becomes `.ship/NN-NAME/`. A shipped ship project's
learnings feed back to `specs/` if architectural.

## Notes

- Design specs (`specs/N/*.md`) can be passed directly to
  ship if they already contain concrete deliverables, file
  paths, and acceptance criteria
- ship runs adversarial verification rounds and auto-commits
- NEVER spawn readme/improve agents for work ship can handle
- Sync this skill to `~/app/tools/assistants/`
