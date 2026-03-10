---
name: specs
description: Spec-driven development workflow. Use when working with specs/ directories, phase-based specs (1/, 2/, 3/...), TODO.md, or when asked to organize/prioritize work.
---

# Spec-Driven Development

## Phase Scheme

Specs live in `specs/` organized by phase. Each milestone
gets its own phase directory. Files use base58 prefixes
(0-9, A-H, J-N, P-Z, a-k, m-z) for stable sort order.

```
specs/1/   phase 1 — core gateway (shipped base)
specs/2/   phase 2 — milestone 1 (permissions, capabilities)
specs/3/   phase 3 — milestone 2 (channels, pipelines, memory)
specs/4/   phase 4 — milestone 3 (media awareness)
specs/5/   phase 5 — milestone 4 (evangelist)
specs/6/   phase 6 — milestone 5 (cheerleader)
specs/res/ resources (examples, research)
```

Naming: `<phase>/<base58>-<topic>.md` e.g. `1/0-actions.md`,
`2/5-permissions.md`. New specs get the next available prefix.

The user controls releases and tags. TODO.md may suggest which
specs a version should cover, but the user decides what ships.

## Workflow

1. **Survey** — read TODO.md + scan specs/ dirs to understand current state
2. **Spec first** — write `specs/<phase>/<prefix>-<name>.md` before implementing
3. **Iterate** — specs start rough, get refined through discussion
4. **Promote** — when a spec is partially shipped, note status at top
5. **TODO.md** — single source of truth for what's next

## Spec File Format

```markdown
# Feature Name

**Status**: not started | partial (what's done) | shipped

## Problem
Why this exists.

## Design
How it works.

## Open Questions
What's unresolved.
```

Keep specs concise. No marketing. Describe what the system does,
not what it could do. If a section has open questions, say so.

## Rules

- NEVER implement without a spec (even a rough one)
- ALWAYS check TODO.md before starting work
- Lower phases ship before higher phases
- When shipping a spec, update TODO.md to mark it done
