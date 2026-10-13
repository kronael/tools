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

ALWAYS move `status` in the commit that approves or lands the work. Open
questions live only in a `draft` (or a `reference`); promotion answers them
or cuts them; lint: spec-open-questions (warn).

## Naming and index

- ALWAYS number specs: flat `specs/<NN>-<topic>.md` (zero-padded NN, next =
  max + 1), or `specs/<phase>/<N>-<topic>.md` ONLY when specs cluster into
  distinct workstreams. NEVER an unnumbered name, and two files NEVER share
  one number; lint: spec-naming (hard fail; an unpadded flat number warns).
- ALWAYS keep `specs/index.md` in step: one row per file
  (`| [01-auth.md](01-auth.md) | partial | JWT auth flow |`), Status equal to
  the frontmatter, the row removed with the file; lint: spec-index-row,
  spec-index-dangling. A phase may keep its own `specs/<phase>/index.md`; its
  rows count once the master table links it.

## Body

- ALWAYS open with one plain sentence saying what the thing IS, before any
  path, mechanism or `## Problem` — a reader hangs the mechanism on that
  handle, and a "wtf?" means it was missing.
- ALWAYS write the problem (the constraint it answers), the approach — the
  decision and its one caveat, WHY this way — and pointers to the code it
  changes (`src/config.ts` — one sentence why). NEVER an option space or a
  taxonomy for the reader to choose from; lint: spec-options (warn).
- A pointer that no longer resolves, matches several files or points past the
  end of its file is stale; lint: spec-pointer (warn). A `partial` or
  `shipped` spec with no pointer at all; lint: spec-no-pointer (warn). A link
  to another spec or file resolves; lint: spec-link (hard fail).
- Tables with `file:line` anchors over prose — a spec over 500 lines is
  prose; lint: spec-length (warn; hard fail over 1000).
- One owner: each table, contract and term has one owning spec the others
  link to; a schema table derives from the code type it describes, with
  `file:line`; lint: spec-table-owner (hard fail on a second `CREATE TABLE`).
- Existing vs proposed: existing code is cited by `file:line`; a new API sits
  under a heading that says it is proposed. NEVER present proposed code as
  existing, and NEVER call something new or absent without the search that
  found nothing.
- A measured number — a test count, coverage, a line count — carries the
  commit it was measured at and is re-measured before it is repeated.
- A refactor or removal spec carries a Contract: the baseline numbers
  measured before the first edit, and the exact edit each gate performs.
- NEVER implementation steps, code that duplicates the codebase, re-stated
  signatures (link `file:line`), checklists, schedules or TBD/TODO — decide or
  omit; lint: spec-tbd (hard fail), spec-future-tense, spec-checklist (warn).
- NEVER a table, column, mode or abstraction no current case needs — name the
  case that would force it instead.
- NEVER narrate history ("no longer", "formerly", "used to be", "renamed
  from", backward compatibility) — a spec states what is; git holds what was;
  lint: spec-history (warn).
- NEVER coin a term or borrow jargon — the codebase's own name, "tests" never
  "harness", and no marketing words; lint: spec-wording (warn).
- NEVER write a defect up as a spec — it goes to `BUGS.md`, linked from the
  spec.

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

ALWAYS run `spec-lint specs` from the repo root; `spec-lint --help` lists every
rule. The kronael sync installs it, else `cd spec-lint && make install` from
the tools clone. An explicit `specs/` directory is checked even without an
index or numbered files; discovery from a project directory or a changed file
requires an index or numbered spec, so a test suite or the `skills/specs/`
router is excluded. The lint checks everything above except the judgements:
the spec says WHY and WHERE, never HOW; it opens with a definition; proposed
code is marked as proposed; a measured number carries its commit; and no doc
or code links a spec.
