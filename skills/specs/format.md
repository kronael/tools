# Spec files — naming, status, index

A spec drives one change: what to build and why, written before the code. It
NEVER documents the system; current state belongs to the docs (`readme` →
`topology.md`).

## Status

Every spec starts with frontmatter `status:` — one of `draft`, `experiment`,
`planned`, `partial`, `shipped`, `reference`; the index Status cell carries the
same word. NEVER invent another (`implemented`, `superseded`) or write prose
there; lint: spec-status (hard fail).

- **`draft`** — not approved. NEVER start its work; promote to `planned` only
  on explicit approval.
- **`experiment`** — prototype on a preview branch. NEVER merge it to
  production before it is promoted to `planned` and its gates clear.
- **`planned`** → **`partial`** → **`shipped`** — approved, in progress, done.
- **`reference`** — analysis that never ships.

## Naming and index

- ALWAYS number specs: flat `specs/<NN>-<topic>.md` (zero-padded NN, next =
  max + 1), or `specs/<phase>/<N>-<topic>.md` ONLY when specs cluster into
  distinct workstreams. NEVER an unnumbered name; lint: spec-naming.
- ALWAYS keep `specs/index.md` in step: one row per file
  (`| [01-auth.md](01-auth.md) | partial | JWT auth flow |`), Status equal to
  the frontmatter, the row removed with the file; lint: spec-index-row,
  spec-index-dangling.

## Body

- ALWAYS write the problem, the approach with its WHY, and pointers to the
  code it changes (`src/config.ts` — one sentence why); lint: spec-pointer.
- NEVER implementation steps, code that duplicates the codebase, checklists,
  schedules or TBD/TODO — decide or omit; lint: spec-tbd, spec-future-tense.

## Links point one way

- NEVER link a spec from the docs or the code — ALWAYS state the fact in the
  doc. A spec points at what it changes; nothing points back, so deleting a
  spec never breaks a doc.

## When the change ships

1. ALWAYS move what stays true — each structure, its WHY beside it — into the
   doc `readme` → `topology.md` names; set `status: shipped` in the same change.
2. The spec MAY then be deleted — NEVER before step 1. Before deleting or
   renaming, ALWAYS grep the repo for its path AND its handle (`spec 4/6`);
   a path-only grep misses the handle. Re-point every hit in the same change.

## Before commit

ALWAYS run `python3 ~/.claude/hooks/spec_lint.py specs` from the repo root. It
checks everything above except one judgement: the spec says WHY and WHERE,
never HOW.
