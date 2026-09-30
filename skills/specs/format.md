# Spec files — naming, status, index

Design references live in `specs/`. Master index: `specs/index.md`.

## Frontmatter

Every spec file starts with YAML frontmatter:

```yaml
---
status: draft|experiment|planned|partial|shipped|reference
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
- **`reference`** — analysis doc that never ships; no lifecycle.

These six are the whole vocabulary, for the frontmatter AND the index Status
column — NEVER invent another (`proposed`, `active`, `superseded`) and NEVER
write prose in the Status cell; lint: spec-status (hard fail).

## File naming and ordering

ALWAYS number spec files — the number gives stable ordering and a short handle
("spec 3"). NEVER use an unnumbered by-content name like `specs/auth.md`;
lint: spec-naming (hard fail; an unpadded flat number warns).

**Default (flat):** `specs/<NN>-<topic>.md`, NN a zero-padded integer.
- Next number: `ls specs/[0-9]*-*.md | sed 's|.*/||' | cut -d- -f1 | sort -n | tail -1` then +1 (first is `01`).
- `<topic>` is kebab-case content name: `specs/03-vote-tracking.md`.

**Phases (only for large multi-stream efforts):** `specs/<phase>/<N>-<topic>.md`,
e.g. `specs/1/2-webhooks.md`. Use phase subdirs ONLY when specs cluster into
distinct workstreams; a single-project corpus stays flat. Next N: `ls specs/<phase>/`, max + 1.

`specs/index.md` is the master table — ALWAYS add a row on create, update Status
on ship; lint: spec-index-row, spec-index-dangling (hard fail):

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
  (e.g. "`src/config.ts` — HOST\_\* exports computed at startup"); a pointer
  that no longer resolves is stale — lint: spec-pointer (warn)
- **Stubs are good**: file path + one sentence of WHY

## What specs do NOT contain

- Step-by-step implementation details (read the code)
- Code snippets that duplicate what's in the codebase
- Completed checklists or TODO items
- Comments about implementation order or timeline
- NEVER use "TBD" / "TODO" / "implement later" — decide now or omit; lint:
  spec-tbd (hard fail)
- NEVER write future-tense plans ("we will…") — specs describe state, not work;
  lint: spec-future-tense (warn)
- NEVER re-state function signatures already in code — link to file:line instead

## After shipping

1. Update frontmatter to `status: shipped`
2. Trim implementation detail — keep problem, design, WHY, and the code pointers
3. Update `specs/index.md` status column

## Self-review before commit

ALWAYS run `python3 ~/.claude/hooks/spec_lint.py specs` from the repo root — it
checks every item below except 3, a judgement call no lint can make.

1. Frontmatter status matches reality
2. index.md row added/updated
3. No HOW (implementation steps) — only WHY + WHERE
4. No future tense; no "TBD"
5. Code pointers resolve (paths exist)
