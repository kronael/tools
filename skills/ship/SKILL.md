---
name: ship
description: Ship multi-session work via the ship agent. Creates .ship/<NAME>/ with PROJECT + PLAN + PROGRESS + tasks.json. USE for work spanning >1 session with fixed acceptance. NOT for one-off edits, exploration, or <30min work — prefer TaskCreate.
user-invocable: true
---

# Ship

## Workflow

1. **Explore** — use Explore agent to understand the codebase and task
2. **Write plan** — write `.ship/plan-<name>.md` with concrete tasks, file paths, and acceptance criteria
3. **Run** — `ship .ship/plan-<name>.md`
4. **Verify** — `make build && make test`
5. **Clean** — delete completed `.ship/` artifacts after shipping

## Plan format

```markdown
# Plan: <name>

## Tasks

### 1. <task title>
<what to do, which files, exact changes>

### 2. <task title>
...

## Acceptance
- <verifiable check>
- <verifiable check>
```

## Notes

- Design specs (specs/N/*.md) can be passed directly to ship if they already
  contain concrete deliverables, file paths, and acceptance criteria
- ship runs adversarial verification rounds and auto-commits
- NEVER spawn readme/improve agents for work that ship can handle
- Sync this skill across assistants repos (see LOCAL.md)
