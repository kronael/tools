---
name: specs
description: How to write and manage project specs.
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

## File naming

`<phase>/<base58>-<topic>.md` — base58 chars
(0-9, A-H, J-N, P-Z, a-k, m-z) for stable sort.

Phases:

- `specs/1/` core gateway (shipped)
- `specs/2/` social channels (shipped)
- `specs/3/` permissions, cleanup, gaps (active)
- `specs/4/` dashboards, memory, products (deferred)
- `specs/5/` agent extensions & workflows (future)
- `specs/6/` products (deferred)
- `specs/res/` resources (research, examples)

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

## After shipping

1. Update frontmatter to `status: shipped`
2. Trim implementation details — keep problem, design, WHY
3. Keep code pointers (WHERE + WHY), remove HOW
4. Update `specs/index.md` status column
