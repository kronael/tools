---
name: specs
description: Design specs in specs/. NOT for in-flight work (use ship).
when_to_use: "spec this out", document architecture, "write a spec", "write a design doc"
---

# Specs

Design references in `specs/`. Master index: `specs/index.md`.

## Frontmatter

Every spec file starts with YAML frontmatter:

```yaml
---
status: shipped|partial|spec|planned|draft
---
```

Lifecycle: `draft` -> `spec` -> `partial` -> `shipped`.
`reference` for analysis docs that don't ship.

## File naming and ordering

`<phase>/<N>-<topic>.md` — N is a plain integer, ordered within the phase.

- Phases group related work: `specs/1/`, `specs/2/`, `specs/3/`, ...
- N within a phase is sequential — next spec gets the next available number
- To find the next N: `ls specs/<phase>/` and take max + 1
- Phase directories are created as needed; no predefined list

`specs/index.md` is the master table:

```markdown
| Spec | Status | Summary |
|------|--------|---------|
| [1/1-auth.md](1/1-auth.md) | shipped | JWT auth flow |
| [2/1-webhooks.md](2/1-webhooks.md) | planned | Outbound webhooks |
```

Add a row when creating a spec. Update status when it ships.

## What specs SHOULD contain

- **Problem**: why this exists, what was wrong before
- **Approach**: design decisions, tradeoffs, WHY this way
- **Code pointers**: WHERE code lives and WHY it's there
  (e.g. "`src/config.ts` — HOST\_\* exports computed at startup")
- **Stubs are good**: file path + one sentence of WHY

## What specs should NOT contain

- Step-by-step implementation details (read the code)
- Code snippets that duplicate what's in the codebase
- Completed checklists or TODO items
- Comments about implementation order or timeline
- NEVER use "TBD" / "TODO" / "implement later" — decide now or omit
- NEVER write future-tense plans ("we will…") — specs describe state, not work
- NEVER re-state function signatures already in code — link to file:line instead

## After shipping

1. Update frontmatter to `status: shipped`
2. Trim implementation details — keep problem, design, WHY
3. Keep code pointers (WHERE + WHY), remove HOW
4. Update `specs/index.md` status column

## Self-review before commit
1. Frontmatter status matches reality
2. index.md row added/updated
3. No HOW (implementation steps) — only WHY + WHERE
4. No future tense; no "TBD"
5. Code pointers resolve (paths exist)
