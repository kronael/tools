# Repository and documentation layout

The house layout, defined here and nowhere else — WISDOM and every other skill
point to this file. A doc set is a few files, each answering ONE question, read
in a stated order (with a docs site, by its sidebar and the README hub below), with every behaviour tied to a test and every number to the
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
| `TODO.md` | What is deferred and not yet a spec? Format: `next` § Later. |
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
  one's content has a row above. `plans/` exists only as `.claude/plans/`
  (§ Tracked and local).
- NEVER create `CHANGELOG.md` unless the project publishes versions to outside
  consumers (crates.io, npm, PyPI, a plugin) — history lives in git and
  `.diary/`. A repo that keeps one keeps it; `release` writes it.
- In a repo laid out otherwise, ALWAYS put a new fact where its question already
  lives — NEVER migrate the layout unasked.

## README.md

This order; cut a section with nothing true to say. Under 150 lines.

1. The title, then what it is and who it is for, in one plain sentence.
2. The link to the study page, naming what it answers; with a docs site, the
   link row of `sync.md` step 3.
3. Any status that changes whether to use it (unaudited, not for real funds).
4. **The words** — each domain term defined before its first use.
5. **What it gives you** — one bullet per capability that works today.
6. **What it does not give you** — each limit with its `BUGS.md` id.
7. **Packages** — directory, package name, one line, a link to its README; in
   a one-package repo, a quick start that runs and prints something instead.
8. **Commands** — every `make` target with a one-line comment.
9. **How to read this**, last — a table of order, file and the question it
   answers, the study page first, `LICENSE`/`NOTICE` unnumbered.
   With a docs site, the hub shape below replaces it.

- ALWAYS state what adopting costs by `sync.md` § Rules; with a docs site the
  README links to the Why page that states it.
- NEVER put deployment (Dockerfile, CI, k8s, deploy steps) in the README —
  that belongs to the ops repo.

## README as a docs-site hub

When a docs site exists, ALWAYS make the README its front door, NEVER a
second copy of the site:

- The link row and the status line, in the order `sync.md` step 3 sets, and
  a link to the cost on the Why page.
- Each capability bullet links to the guide page of the same title.
- The one README example comes from a compiled guide region (`sync.md`
  § Rules) and links to the guide page that holds its imports, other
  languages and the code that runs it — NEVER a README-only example nothing
  compiles.
- A closing "Repository layout" names each top directory. The link row plus
  "Repository layout" replace "How to read this".

## A doc site splits into guide and reference

A built docs site (VitePress, mdBook, Docusaurus) turns the file split above
into a sidebar. ALWAYS order it as the newcomer's questions arrive:

| Group | Pages | What the pages must do |
|---|---|---|
| Start here | Why, Getting started, How it works | Why carries the status line, the cost and the wrong-reason refutation of § Keeping it; How it works is one complete annotated example on one screen |
| Capabilities | one page per thing the reader gets, titled by it ("Amounts read at run time"), NEVER by the mechanism | each opens with what the plain approach cannot do |
| Build | one how-to page per task | guide shape, `shape.md` |
| Examples | an index, then one page per example | `shape.md` § Example and recipe pages |
| Security | trust model, security posture, failure modes | each failure mode says what happens, then how to recover |
| Reference | one page per SDK language, then language, wire format, errors, glossary, limits, scope | glossary: one heading per term, so every term has an anchor; limits: every maximum in one place, naming the source file the values come from; scope: a table of Choice, Instead of, Why |

Contributor docs, such as style notes for page authors, may live in `docs/`
beside the pages, ALWAYS excluded from the build (VitePress `srcExclude`) —
NEVER published as reader pages. Plans, reviews and other work records NEVER
go in `docs/`. They live in `.claude/plans/`, as § Tracked and local sets.

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
- A performance number is labelled and caveated per `release` → `library.md` § 3b–3c.
- With a docs build, ALWAYS generate counts and measured tables from the
  artifact that produces them — a build-time data loader reading the fixture
  (VitePress `*.data.ts`), or a script that rewrites the block between marker
  comments (`<!-- benchmark:name -->` to `<!-- /benchmark -->`). NEVER type a
  count or a measured table into a page. A single measured figure from a tested
  run, such as a cost or a size, may be typed when the page names the test that
  produced it. A repo without a docs build keeps its measured figures in the
  ledger.

## The study page

- `docs/<name>.html` comes first in the reading order and is linked from the
  README's second paragraph; it restates the decisions, features and limits
  for its reader.
- ALWAYS update it in the same commit as the PLAN.md decision, FEATURES.md row,
  `BUGS.md` entry or ledger number it restates.

## What `make lint` checks

ALWAYS wire these into `make lint`, so a stale doc fails the build:

- every FEATURES.md row's test exists at its path, and every `untested` id
  exists in `BUGS.md`;
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
  owns the setting and the ignore step), `/.diary/` (`diary`), `/specs/`,
  `/tmp/`. ALWAYS root-anchor them — a bare `specs/` matches at every depth and
  swallows a real `src/specs/`, and `/.claude/plans/` keeps the committed
  `.claude/` files (settings, commands, skills) tracked. A repo that already
  tracks `.diary/` or `specs/` keeps tracking them.

## Keeping it

- NEVER shorten a doc by cutting its limits, its alternatives or its why —
  the goal is one question answered per file, not brevity.
- ALWAYS cite alternatives generously and accurately enough that their authors
  would not object; a superlative carries its ledger number; a roadmap item is
  never listed as a feature.
- An examples index carries a verdict column saying whether the reader gets
  the same result without the project ("Plain transaction?": Yes / Yes,
  weaker / No), with every value defined in a list ABOVE the table. NEVER a
  verdict the reader decodes by guessing.
- The why section, the Why page on a docs site, names the obvious wrong
  reason to adopt and refutes it with a number ("many calls in one
  transaction is not the reason: thirty transfers already fit in one"),
  before the real reason.
