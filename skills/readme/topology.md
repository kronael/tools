# Repository and documentation layout

The house layout, defined here and nowhere else — WISDOM and every other skill
point to this file. A doc set is a few files, each answering ONE question, read
in a stated order, with every behaviour tied to a test and every number to the
command that produced it. Section order inside one file: `shape.md`. The HTML
page's craft: `page.md`. Prose: `writing`.

## Files

| Path | The one question it answers |
|---|---|
| `docs/<name>.html` | What is it, who can do what, how does it behave? The study page for a newcomer. |
| `README.md` | What is in the repository, and how do I start? |
| `PLAN.md` | Why is it split this way, and which decisions must stay true? |
| `ARCHITECTURE.md` | Where does each piece live, and how does each flow run? |
| `FEATURES.md` | What does it do today, and which test proves it? |
| `BUGS.md` | What is open: defects, deliberate limits, decisions owed? Format: `bugs`. |
| `TODO.md` | What is deferred and not yet a spec? Format: `later`. |
| `<pkg>/README.md` | How does a caller use this package? |
| `test/research/README.md`, `test/research/<project>.md` | What else does this job, and how does this differ? |
| `test/research/verified.md` | Where does each number in these documents come from? |
| `CLAUDE.md`, `<pkg>/CLAUDE.md` | What must an editor not break? |
| `LICENSE`, `NOTICE` | Under what terms? Copyright in `LICENSE`; provenance and third-party terms in `NOTICE`. |

- ALWAYS put a fact in the file whose question it answers and link it from the
  others — NEVER a second copy; copies drift apart unnoticed.
- ALWAYS open each file with its question in one sentence and links to the
  files that answer the neighbouring questions.
- ALWAYS add a file only once its question has an answer the README cannot hold
  in one section — NEVER an empty stub. Root docs are UPPERCASE.
- NEVER create `todos/`, `notes/`, `facts/`, `compare/` or `WHY.md` — each
  one's content has a row above. `plans/` exists only as `.claude/plans/`, plan
  mode's directory, where `ship` keeps its records (`ship` § Work record).
- NEVER create `CHANGELOG.md` unless the project publishes versions to outside
  consumers (crates.io, npm, PyPI, a plugin) — history lives in git and
  `.diary/`. A repo that keeps one keeps it; `release` writes it.
- In a repo laid out otherwise, ALWAYS put a new fact where its question already
  lives — NEVER migrate the layout unasked.

## README.md

This order; cut a section with nothing true to say. Under 150 lines.

1. The title, then what it is and who it is for, in one plain sentence.
2. The link to the study page, naming what it answers.
3. Any status that changes whether to use it (unaudited, not for real funds).
4. **The words** — each domain term defined before its first use.
5. **What it gives you** — one bullet per capability that works today.
6. **What it does not give you** — each limit with its `BUGS.md` id.
7. **Packages** — directory, package name, one line, a link to its README; in
   a one-package repo, a quick start that runs and prints something instead.
8. **Commands** — every `make` target with a one-line comment.
9. **How to read this**, last — a table of order, file and the question it
   answers, the study page first, `LICENSE`/`NOTICE` unnumbered.

- NEVER put deployment (Dockerfile, CI, k8s, deploy steps) in the README —
  that belongs to the ops repo.

## PLAN.md and ARCHITECTURE.md

- PLAN.md holds the purpose and boundaries (which package owns what), the
  model, the decisions that must stay true and the deferred scope. ALWAYS name
  the alternative a decision rejected and why.
- ARCHITECTURE.md is for an engineer changing the code: NEVER re-explain what
  the thing is, and NEVER record a decision there — link PLAN.md. ALWAYS give
  it a package-flow diagram, a repository map (path → what it owns), a
  data-ownership table (data, source of truth, consumers) and one diagram per
  flow whose order matters; a structure in prose alone is undocumented. Draw
  with `diagrams`. Under 300 lines.

## FEATURES.md

- One row per behaviour: feature, current behaviour, evidence. The evidence is
  one `` `path::exact test name` `` or `` untested — `<BUG-ID>` `` — NEVER a
  wildcard, a bare file or a source symbol.
- Today's behaviour only; planned work is a `specs/` draft or a PLAN.md
  deferred-scope line.

## Numbers — one ledger

- Every measured number in the README, FEATURES.md, the package READMEs and
  the page comes from `test/research/verified.md`: one section per
  measurement, the command in a fenced block, its output, the date and the
  toolchain. The docs quote it.
- ALWAYS change a value only by re-running its command — a stale number is
  worse than none.
- ALWAYS name, in the CLAUDE.md of the directory whose change moves a number,
  which ledger section that change re-runs (`test/CLAUDE.md`: a new test
  re-runs the test count).
- A performance number is labelled and caveated per `finalize-crate` § 3b–3c.

## The study page

- `docs/<name>.html` comes first in the reading order and is linked from the
  README's second paragraph; it restates the decisions, features and limits
  for its reader.
- ALWAYS update it in the same commit as the PLAN.md decision, FEATURES.md row,
  `BUGS.md` entry or ledger number it restates.

## What `make lint` checks

ALWAYS wire these into `make lint`, so a stale doc fails the build:

- every FEATURES.md row's test exists at its path under a test directory, and
  every `untested` id exists in `BUGS.md`;
- every page claim's link carries `data-evidence="path::exact test name"` or
  `data-evidence="BUGS.md::<BUG-ID>"`, checked the same way;
- every number of two or more digits in the README, FEATURES.md, the package
  READMEs and the page's visible text appears in the ledger. This proves
  membership, not meaning; a changed meaning re-runs the command;
- the checker first refuses a planted fake citation and finds a planted real
  test, so a parser that matches nothing cannot pass.

## CLAUDE.md files

- A short root `CLAUDE.md` plus one `<pkg>/CLAUDE.md` per package that has
  invariants of its own. A rule that holds inside one package lives in that
  package's file, NEVER the root. Content: `wisdom` § CLAUDE.md (project).
  Under 200 lines each.
- NEVER put the reading order or a which-file index in a CLAUDE.md — the
  README's "How to read this" holds it.

## Tracked and local

- Every file above is tracked, `BUGS.md` included — it is in the reading order.
- Local, root-anchored in `.gitignore`: `/.claude/plans/` (`ship` § Work record
  owns the setting and the ignore step), `/.diary/` (`diary`), `/specs/`
  (`specs`), `/tmp/`. ALWAYS root-anchor them — a bare `specs/` matches at every
  depth and swallows a real `src/specs/`, and `/.claude/plans/` keeps the
  committed `.claude/` files (settings, commands, skills) tracked. A repo that
  already tracks `.diary/` or `specs/` keeps tracking them.

## Keeping it

- NEVER shorten a doc by cutting its limits, its alternatives or its why —
  the goal is one question answered per file, not brevity.
- ALWAYS cite alternatives generously and accurately enough that their authors
  would not object; a superlative carries its ledger number; a roadmap item is
  never listed as a feature.
