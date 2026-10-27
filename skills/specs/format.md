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
questions live only in a `draft` (or a `reference`); review answers them
or cuts them before promotion. NEVER infer implementation completion from lint.

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
- ALWAYS use `Spec`, `Status`, `Summary` as the first three index columns,
  with one Markdown spec link in the first cell. ALWAYS keep the frontmatter
  to one `status: value` line between `---` delimiters; comments and quoted
  values are accepted. The [speclint README](https://github.com/kronael/tools/tree/master/speclint) owns
  the supported input forms and diagnostics.

## Body

- ALWAYS open with one plain sentence saying what the thing IS, before any
  path, mechanism or `## Problem` — a reader hangs the mechanism on that
  handle, and a "wtf?" means it was missing.
- ALWAYS write the problem (the constraint it answers), the approach — the
  decision and its one caveat, WHY this way — and pointers to the code it
  changes (`src/config.ts` — one sentence why). NEVER an option space or a
  taxonomy for the reader to choose from. ALWAYS review that decision.
- A pointer that no longer resolves, matches several files or points past the
  end of its file needs review; lint: spec-pointer (warn). ALWAYS review
  whether pointers support the claims; absence alone never determines status.
- ALWAYS use tables with `file:line` anchors where they explain the design
  better than prose. NEVER infer quality from a line-count threshold.
- One owner: each table, contract and term has one owning spec the others
  link to; a schema table derives from the code type it describes, with
  `file:line`. ALWAYS review ownership against the code; SQL examples do not
  establish ownership.
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
  omit. ALWAYS check these choices during review.
- NEVER a table, column, mode or abstraction no current case needs — name the
  case that would force it instead.
- NEVER narrate history ("no longer", "formerly", "used to be", "renamed
  from", backward compatibility) — ALWAYS state the design; git holds history.
- NEVER coin a term or borrow jargon — the codebase's own name, "tests" never
  "harness", and no marketing words. ALWAYS review prose in context.
- NEVER write a defect up as a spec — it goes to `BUGS.md`, linked from the
  spec.

## Links point one way

- NEVER link a spec from the docs or the code — ALWAYS state the fact in the
  doc. A spec points at what it changes; nothing points back, so deleting a
  spec never breaks a doc.

## When the change ships

1. ALWAYS verify the approved requirements with implementation tests and review.
   `planned` and `partial` specs govern unfinished work; `shipped` records
   verified closeout, not a lint result. Reference analyses remain as applicable.
2. ALWAYS move lasting facts and rationale into the documentation that
   `readme` → `topology.md` names, then retire the verified implemented spec.
   NEVER keep implemented specs as a permanent system registry.
3. Before deleting or renaming, ALWAYS grep for both the path and its handle
   (`spec 4/6`), repair references, and remove its index row with the file.
   ALWAYS lint the remaining complete corpus, including unchanged indexes.

## Before commit

ALWAYS run `speclint` on each complete corpus during drafting, implementation
and retirement. The tool README owns installation, full-commit uvx pins,
discovery and the consumer hook. ALWAYS follow `readme/topology.md`
§ Documentation checks for consumer enforcement, scope and activation.

ALWAYS check ignored or externally stored specs explicitly while drafting and
verifying. CI can check only files present in its checkout. ALWAYS give Markdown
syntax, formatting and supported links/anchors to rumdl; lint cannot verify the
meaning of a link or decide that implementation meets a requirement.

The lint checks the items above that name a `lint:` rule, and only the
mechanical part of each. Everything else is a judgement:

- the spec says WHY and WHERE, never HOW, with no implementation steps,
  duplicated code, re-stated signatures or schedules
- it opens with a definition, and coins no term
- proposed code is marked as proposed, and a new or absent claim cites its
  search
- a measured number carries its commit
- a refactor or removal Contract holds the baseline numbers and the edit per gate
- a schema table derives from its code type with `file:line`, and each contract
  and term has one owning spec
- no table, column, mode or abstraction no current case needs
- a defect goes to `BUGS.md`, never into a spec
- `status` moves in the commit that approves or lands the work
- phase directories only when specs cluster into workstreams, and the next
  number is max + 1
- no doc or code links a spec; verified implementation and durable documentation
  precede retirement; remaining active specs and indexes agree
