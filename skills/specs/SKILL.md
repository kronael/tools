---
name: specs
description: Design specs in specs/ — numbered files, status frontmatter, index.md. NOT for in-flight tracking (use ship) or code/API docs (use readme).
when_to_use: "write a spec, spec this out, write a design doc, design document, architecture doc, technical design, RFC, ADR, proposal, SPEC.md, specs/ directory, spec out a feature, spec before coding, number a spec, add a spec, spec numbering, update the specs index"
---

# Specs

Design references in `specs/`. Master index: `specs/index.md`.

## Frontmatter

Every spec file starts with YAML frontmatter:

```yaml
---
status: draft|experiment|planned|partial|shipped
---
```

Lifecycle: `draft` → `planned` → `partial` → `shipped`.

- **`draft`** — idea captured, NOT approved. Implementation is blocked.
  A draft spec must never be started. Promote to `planned` only when
  the work is explicitly approved to begin.
- **`experiment`** — live prototype in a preview branch; validates the idea
  before committing to production. Must not merge to production until
  explicitly promoted to `planned` AND any stated gates are cleared.
- **`planned`** — approved and ready to implement in production.
- **`partial`** — in progress.
- **`shipped`** — complete; trim HOW, keep WHY + code pointers.

`reference` for analysis docs that don't ship (no lifecycle).

## File naming and ordering

ALWAYS number spec files — the number gives stable ordering and a short handle
("spec 3"). NEVER use an unnumbered by-content name like `specs/auth.md`.

**Default (flat):** `specs/<NN>-<topic>.md`, NN a zero-padded integer.
- Next number: `ls specs/[0-9]*-*.md | sed 's|.*/||' | cut -d- -f1 | sort -n | tail -1` then +1 (first is `01`).
- `<topic>` is kebab-case content name: `specs/03-vote-tracking.md`.

**Phases (only for large multi-stream efforts):** `specs/<phase>/<N>-<topic>.md`,
e.g. `specs/1/2-webhooks.md`. Use phase subdirs ONLY when specs cluster into
distinct workstreams; a single-project corpus stays flat. Next N: `ls specs/<phase>/`, max + 1.

`specs/index.md` is the master table — ALWAYS add a row on create, update Status on ship:

```markdown
| Spec | Status | Summary |
|------|--------|---------|
| [01-auth.md](01-auth.md) | shipped | JWT auth flow |
| [02-webhooks.md](02-webhooks.md) | planned | Outbound webhooks |
```

## What specs contain

- **Problem**: why this exists, what was wrong before
- **Approach**: design decisions, tradeoffs, WHY this way
- **Code pointers**: WHERE code lives and WHY it's there
  (e.g. "`src/config.ts` — HOST\_\* exports computed at startup")
- **Stubs are good**: file path + one sentence of WHY

## What specs do NOT contain

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

## Spec-first changes

The spec is the source of truth; code conforms. Every non-trivial change starts here.

- ALWAYS find the governing spec BEFORE editing code — `specs/index.md`, or grep `specs/` for the topic.
- ALWAYS reconcile code↔spec: when they disagree, the divergence IS the bug — fix both in one pass, never just the code.
- When the design is unspecced, ALWAYS draft the MINIMAL spec edit in the same change; code that adds an unspecced structure is incomplete.
- ALWAYS read neighboring specs first; NEVER contradict them — keep cross-references and status consistent.
- NEVER drift a spec unless the drift makes the code more minimal/orthogonal/simpler.
- ALWAYS leave code more minimal, orthogonal, and simpler than before — "it works" is not "done".
