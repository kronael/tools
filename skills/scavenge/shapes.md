# Shape skeletons — step 5 of `scavenge`

Pick one. Keep the produced artifact < 200 lines. House style: terse,
opinionated, ALWAYS/NEVER, no marketing prose, no emoji.

## SKILL — `~/.claude/skills/<name>/SKILL.md`

```markdown
---
name: <short-name>
description: <one line>. NOT for <case> (use <other-skill>).
when_to_use: <natural trigger phrases>
user-invocable: true
---

# <name> — <verb phrase>

<2–4 lines: what the skill does, methodology source path>

## When to invoke / NOT

## Persona / Setup (if applicable)

## Protocol (numbered, runnable)

## Output shape / classification

## Rules (ALWAYS/NEVER)

## Anti-patterns

## Reference
```

Main thread owns the final write — subagents may be sandbox-blocked
from writing under `~/.claude/`.

## AGENT — `~/.claude/agents/<name>.md`

```markdown
---
name: <name>
description: <what this agent does, when to spawn>
tools: <comma list or *>
model: <opus/sonnet/haiku>     # optional
---

# <name> Agent

## Mission
## Input contract
## Output contract
## Process (numbered)
## Rules (ALWAYS/NEVER)
```

## GUIDELINE — `<cwd>/docs/guidelines/<name>.md` or section in `CLAUDE.md`

No frontmatter. Plain prose. Sections:

- **Scope** — one paragraph
- **Rules** — ALWAYS/NEVER list
- **Anti-patterns** — common failures with one-line rationale each
- **Examples** — short, real
- **Reference** — citations + cross-links

For `CLAUDE.md` sections: just the four sections inline under a clear
`## <name>` header. Put critical rules at the top or bottom of
CLAUDE.md — the middle is least reliably attended to.

## RUNBOOK — `<cwd>/docs/runbooks/<name>.md`

```markdown
# <name> runbook

## Preconditions
- ...

## Steps
1. <action> — `command --flag` — expected: <output>
2. ...

## Recovery
- If step <N> fails: <action>

## Rollback
- ...

## Escalation
- Page <who> if <condition>
```

Commands literal and copy-pasteable. Expected output stated per step.

## CHECKLIST — `<cwd>/docs/checklists/<name>.md`

```markdown
# <name> checklist
Triggered by: <workflow>

- [ ] step 1 — <verb> <object>
- [ ] step 2 — ...
```

Each item binary checkable in < 30 s. Header names the triggering
workflow.

## REVIEW TEMPLATE — `<cwd>/docs/templates/review-<name>.md`

```markdown
# Review template — <name>

**Reviewer:** _________  **Date:** _________

## Context
- ...

## <Criterion 1>
- Notes:
- Verdict: pass / fail

## <Criterion 2>
...

## Pass criteria (all required)
- ...

## Fail criteria (any one)
- ...

## One-line verdict
```

Sections to fill in. Pass / fail criteria explicit.

## SPEC — `<cwd>/specs/<name>.md`

```markdown
# <name> — spec

## Context
## Goals
## Non-goals
## Design
## Alternatives considered
## Open questions
## References
```

Forward-looking. Capture alternatives considered — future readers
need to know what you rejected and why.
