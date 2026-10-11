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

ALWAYS move `status` in the commit that approves or lands the work. Open
questions live only in a `draft` (or a `reference`); promotion answers them
or cuts them; lint: spec-open-questions (warn).

## File naming and ordering

ALWAYS number spec files — the number gives stable ordering and a short handle
("spec 3"), so two files NEVER share one. NEVER use an unnumbered by-content
name like `specs/auth.md`; lint: spec-naming (hard fail; an unpadded flat
number warns).

**Default (flat):** `specs/<NN>-<topic>.md`, NN a zero-padded integer.
- Next number: `ls specs/[0-9]*-*.md | sed 's|.*/||' | cut -d- -f1 | sort -n | tail -1` then +1 (first is `01`).
- `<topic>` is kebab-case content name: `specs/03-vote-tracking.md`.

**Phases (only for large multi-stream efforts):** `specs/<phase>/<N>-<topic>.md`,
e.g. `specs/1/2-webhooks.md`. Use phase subdirs ONLY when specs cluster into
distinct workstreams; a single-project corpus stays flat. Next N: `ls specs/<phase>/`, max + 1.

`specs/index.md` is the master table — ALWAYS add a row on create, update Status
on ship; the Spec cell links the file and Status matches its frontmatter. A
phase may keep its own `specs/<phase>/index.md`; its rows count once the
master table links it. Lint: spec-index-row, spec-index-dangling, spec-status
(hard fail):

```markdown
| Spec | Status | Summary |
|------|--------|---------|
| [01-auth.md](01-auth.md) | shipped | JWT auth flow |
| [02-webhooks.md](02-webhooks.md) | planned | Outbound webhooks |
```

## What specs contain

- **Definition first**: the body opens with one plain sentence saying what
  the thing IS, before any path, mechanism or `## Problem` — a reader hangs
  the mechanism on that handle, and a "wtf?" means it was missing
- **Problem**: why this exists — the constraint it answers
- **Approach**: the decision and its one caveat, WHY this way — NEVER an
  option space or a taxonomy for the reader to choose from; lint:
  spec-options (warn)
- **Code pointers**: WHERE code lives and WHY it's there
  (e.g. "`src/config.ts` — HOST\_\* exports computed at startup"); a pointer
  that no longer resolves, matches several files or points past the end of
  its file is stale — lint: spec-pointer (warn); a `partial` or `shipped`
  spec with no pointer at all — lint: spec-no-pointer (warn)
- **Stubs are good**: file path + one sentence of WHY; a link to another
  spec or file resolves — lint: spec-link (hard fail)
- **Tables with `file:line` anchors over prose** — a spec over 500 lines is
  prose; lint: spec-length (warn; hard fail over 1000)
- **One owner**: each table, contract and term has one owning spec the others
  link to; a schema table derives from the code type it describes, with
  `file:line`; lint: spec-table-owner (hard fail on a second `CREATE TABLE`)
- **Existing vs proposed**: existing code is cited by `file:line`; a new API
  sits under a heading that says it is proposed — NEVER present proposed code
  as existing, and NEVER call something new or absent without the search
  that found nothing
- **Measured numbers carry their commit**: a test count, coverage or line
  count is stamped with the commit it was measured at and re-measured before
  it is repeated
- **A refactor or removal spec carries a Contract**: the baseline numbers
  measured before the first edit, and the exact edit each gate performs

## What specs do NOT contain

- Step-by-step implementation details (read the code)
- Code snippets that duplicate what's in the codebase
- Completed checklists or TODO items; lint: spec-checklist (warn)
- Comments about implementation order or timeline
- A table, column, mode or abstraction no current case needs — name the case
  that would force it instead
- NEVER use "TBD" / "TODO" / "implement later" — decide now or omit; lint:
  spec-tbd (hard fail)
- NEVER write future-tense plans ("we will…") — specs describe state, not work;
  lint: spec-future-tense (warn)
- NEVER narrate history ("no longer", "formerly", "used to be", "renamed
  from", backward compatibility) — a spec states what is; git holds what was;
  lint: spec-history (warn)
- NEVER coin a term or borrow jargon — the codebase's own name, "tests" never
  "harness", and no marketing words; lint: spec-wording (warn)
- NEVER re-state function signatures already in code — link to file:line instead
- NEVER write a defect up as a spec — it goes to `BUGS.md`, linked from the spec

## After shipping

1. Update frontmatter to `status: shipped`
2. Trim implementation detail — keep problem, design, WHY, and the code pointers
3. Update `specs/index.md` status column

## Self-review before commit

ALWAYS run `spec-lint specs` from the repo root — it checks every item below
except 3, a judgement call no lint can make. `spec-lint --help` lists every
rule; the kronael sync installs it, else `cd spec-lint && make install` from
the tools clone. An explicit `specs/` directory is checked even without an
index or numbered files. Discovery from a project directory or a changed file
requires an index or numbered spec, so a test suite or the `skills/specs/`
router is excluded.

1. Frontmatter status matches reality
2. index.md row added/updated
3. No HOW (implementation steps) — only WHY + WHERE
4. No future tense; no "TBD"; no history
5. Code pointers and links resolve (paths exist, anchors inside the file)
