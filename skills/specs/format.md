# Spec files — the architecture document of the system after the change

A spec drives one change: what to build and why, written before the code. Its
body is the ARCHITECTURE section the change will produce: the figures and the
WHY beside each structure that `readme` → `topology.md` § PLAN.md and
ARCHITECTURE.md asks for, drawn for the system AFTER the change. Every figure
marks what is new, changed and removed, and the code the change touches is
quoted at the place it changes. A spec NEVER documents the current
system; current state belongs to the docs (`topology.md` § Files). When the
change ships, the figures and the WHY move into the docs with the marks taken
off (§ When the change ships).

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

## Body — sections in this order

1. **What it is** — one plain sentence saying what the thing IS, before any
   path, mechanism or problem. A reader hangs the mechanism on that handle; a
   "wtf?" means it was missing.
2. **The problem** — the constraint the change answers, with the case in the
   code today that shows it, cited `path:line`.
3. **Where it fits** — the one figure of the system after the change: the
   change's boxes among the unchanged neighbours they connect to, marked as
   § Figures says. The reader sees where the change sits before any detail.
   A change that alters one flow draws it once, here.
4. **One section per flow, layout or relation the change alters**, each
   opening with its figure after the change, then the current and the
   proposed excerpt of the code at the place it changes (§ Code excerpts),
   then the WHY in a few sentences: the decision and its one caveat. A
   change too small for a figure is too small for a section.
5. **Open questions** — `draft` or `reference` only, numbered, each as § Open questions
   says.
6. **Contract** — a refactor or removal spec only: the baseline numbers
   measured before the first edit, and the exact edit each gate performs.

ALWAYS keep the sections in this order. ALWAYS let the figure carry the
explanation. The prose beside it says WHY,
the decision and its caveat; NEVER what the figure already shows. NEVER an
option space or a taxonomy for the reader to choose from. ALWAYS review that
decision.

## Figures

- ALWAYS draw with `diagrams`; `writing/page.md` § Diagrams applies as
  written.
- ALWAYS mark each box and edge the change touches with one word inside its
  label, `(new)`, `(changed)` or `(removed)`, and draw the unchanged
  neighbours unmarked, so the mark is the only difference the eye finds.
  NEVER mark by colour, a legend or a second figure of the state before: the
  current code excerpt is the before.

```
┌──────────┐ events (new) ┌──────────────┐ rows (new) ┌───────┐
│ producer ├─────────────►│ filter (new) ├───────────►│ store │
└─────┬────┘              └──────────────┘            └───────┘
      │ rows (removed)                                    ▲
      └───────────────────────────────────────────────────┘
```

What generalizes: two unchanged neighbours, drawn so the reader sees where
`filter` sits; the new box, its two edges and the edge that goes carry the
only marks.

- ALWAYS draw only the neighbours the change connects to. NEVER the rest of
  the system: a figure the change does not touch belongs to ARCHITECTURE.md,
  linked in one line.

## Tables

- A table ONLY where it adds a dimension the figure cannot show, one value
  per row: a setting, a limit, a field with its type and source, a decision
  per case. ALWAYS place it after the figure it extends. NEVER a table that restates
  the figure, its boxes and edges as rows, and NEVER a table per reader, per
  file or per step with `path:line` cells: that content is the figure and the
  excerpt, and the table makes the spec twice as long to review.
- A schema table derives from the code type it describes, with `path:line`.
  One owner: each table, contract and term has one owning spec the others
  link to. ALWAYS review ownership against the code; SQL examples do not
  establish ownership.
- NEVER a table, column, mode or abstraction no current case needs — name
  the case that would force it instead.

## Code excerpts

- ALWAYS quote the code at the place it changes, twice: the current lines,
  fenced, with `path:line-line` on the line above, then the proposed lines
  under a caption that says proposed. The reader sees the change in place
  without opening the repo. NEVER present proposed code as existing, and
  NEVER call something new or absent without the search that found nothing.
- An excerpt is as long as the change needs to be read in place, the whole
  function or type when the change alters its shape. ALWAYS judge it apart
  from the prose: prose and tables are the shortest that carry the decision
  (`writing/page.md` § Density), excerpts are whatever the reading needs.
  NEVER infer quality from a line count of either.
- Code the change does not touch is linked `path:line`, NEVER quoted. A
  pointer that does not resolve, matches several files or points past the
  end of its file needs review; lint: spec-pointer (warn). ALWAYS review
  whether pointers support the claims; absence alone never determines status.
- NEVER implementation steps, checklists, schedules or TBD/TODO — decide or
  omit; the build plan is `ship`'s. ALWAYS check these choices during review.

## Open questions

- ALWAYS write each question so the owner answers it from the spec alone.
  It names the concrete case that forces it, the input, the row or the call,
  in the system's own names with its `path:line`; the answers it decides
  between; and the recommendation with its one reason. NEVER a question that names a
  mechanism without its case ("how are collisions handled?"): the reply is
  "wdym?" and the question comes back. ALWAYS number them so the answer can
  be "1 yes 3 no".
- NEVER a question that asks the owner to design. ALWAYS recommend; the
  question is whether the recommendation stands.

## Simple and simplifying

- NEVER a second mechanism, name, path, flag, table or config key for a job
  the system already does one way — ALWAYS change the one in place and mark
  the old one `(removed)` on the figure.
- ALWAYS use the codebase's own name for everything, "tests" never
  "harness"; NEVER coin a term. The prose rules, the no-history and
  no-marketing rules and the full-address rule are `writing` § Rules; ALWAYS
  review prose in context against them.
- A measured number — a test count, coverage, a line count — carries the
  commit it was measured at and is re-measured before it is repeated.
- NEVER write a defect up as a spec — it goes to `BUGS.md`, linked from the
  spec.

## The doc rules a spec follows

ALWAYS read these before drafting; each owns its rule and this file only says
how it lands in a spec.

- `readme` → `topology.md` § PLAN.md and ARCHITECTURE.md — what the figures
  hold and the WHY beside each structure; the spec draws that for the after
  state. § Files — the current system is the docs', never the spec's.
- `readme` → `shape.md` § The rule underneath both — the figure every reader
  needs comes first; a case only one reader needs sits in its own section,
  never hoisted to the top.
- `writing` — every prose rule: one word one meaning, the glossary's names,
  headings as claims, no preamble, define before use. `writing/page.md`
  § Diagrams and § Density apply as written. § Sources and links does not: a
  spec cites `path:line` beside the excerpt it quotes.
- `diagrams` — the drawing itself.
- The finish is the page's: `writing/page.md` § Density prune, then the
  `humanize` pass.

## Links point one way

- NEVER link a spec from the docs or the code — ALWAYS state the fact in the
  doc. A spec points at what it changes; nothing points back, so deleting a
  spec never breaks a doc.

## When the change ships

1. ALWAYS verify the approved requirements with implementation tests and review.
   `planned` and `partial` specs govern unfinished work; `shipped` records
   verified closeout, not a lint result. Reference analyses remain as applicable.
2. ALWAYS move lasting facts and rationale into the documentation that
   `readme` → `topology.md` names, the figures with their `(removed)`
   elements deleted and the marks dropped on the rest, and the WHY beside each
   structure, then retire the verified implemented spec.
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
mechanical part of each. Everything else is a judgement — ALWAYS review:

- the spec opens with a definition, the sections run in § Body's order, and
  every section that alters a flow opens with its figure after the change,
  marked `(new)`, `(changed)`, `(removed)`, with the unchanged neighbours drawn
- every table adds a value per row the figure cannot show; none restates a
  figure or lists readers, files or steps with `path:line` cells
- the code at each place it changes is quoted current and proposed; untouched
  code is linked; proposed code is marked as proposed, and a new or absent
  claim cites its search
- each change is the smallest shape for today's cases and adds no second
  mechanism, name, path or key for a job the system does one way
- each open question carries its concrete case and a recommendation, and the
  owner can answer it by number without the conversation
- the spec says WHY and WHERE, never HOW: no implementation steps, schedules
  or checklists
- a measured number carries its commit; a refactor or removal Contract holds
  the baseline numbers and the edit per gate
- a schema table derives from its code type with `path:line`, and each
  contract and term has one owning spec
- a defect goes to `BUGS.md`, never into a spec
- `status` moves in the commit that approves or lands the work
- phase directories only when specs cluster into workstreams, and the next
  number is max + 1
- no doc or code links a spec; verified implementation and durable documentation
  precede retirement; remaining active specs and indexes agree
