---
name: ship
description: Ship multi-session work. NOT for one-off or <30min work.
when_to_use: "ship this feature, track this project"
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
7. **Close-out + prune** (see below) — once shipped, distill
   durable bits to their permanent homes and `git rm -rf`
   the sprint dir. The default is to delete, not archive.

## Close-out + prune (step 7)

`.ship/` is **scratch**, not an archive. Per the global
CLAUDE.md rule (`ALWAYS gitignored, ephemeral working dir
... Clean after shipping: delete completed artifacts`),
sprint dirs are temporary. When the work ships, distill
durable bits to their permanent homes, then delete.

**Distillation routing — for each thing in .ship/NN-NAME/,
ask "where does this belong long-term?":**

| Kind of content | Permanent home |
|---|---|
| Decisions, discoveries, bug post-mortems | `.diary/YYYYMMDD.md` (today's entry) |
| Architectural decisions, design choices | `specs/N/<topic>.md` (move + add `status: shipped`) |
| Release-notes-worthy changes | `CHANGELOG.md` |
| Recurring rules / preferences / patterns | project `CLAUDE.md` or `MEMORY.md` |
| Bench numbers worth tracking | `bench-baseline.json` + a short note in CHANGELOG |
| Critique / review findings | resolved → fold into diary; deferred → `TODO.md` |
| Forced-rank punch lists for "next sprint" | `TODO.md` + maybe seed `.ship/NN+1-NAME/PROJECT.md` |

**Then prune:**
```
git rm -rf .ship/NN-NAME/
git commit -m "[chore] ship NN-NAME complete: distilled + pruned"
```

**Rules:**
- Don't keep `.ship/NN-NAME/REPORT.md` "for reference."
  The repo's commit history + diary IS the reference.
- Don't keep `PROGRESS.md` after the work ships. The
  progress is `git log` now.
- Don't archive into `.ship/archive/`. That's the same
  hoarding under a different name.
- Exception: if a sprint genuinely produced a long-lived
  reference document (a spec, a runbook), move it to
  `specs/` or `docs/` before pruning the rest.

**When NOT to prune:**
- Sprint is paused mid-flight (not shipped yet) — keep
  `.ship/NN-NAME/` until it ships or is explicitly
  cancelled.
- Critique/audit doc is the input to the NEXT sprint —
  keep until that sprint starts; then fold into its
  PROJECT.md and prune the source.

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
