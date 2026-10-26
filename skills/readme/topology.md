# Repository and documentation layout

The house layout, defined here and nowhere else — WISDOM and every other skill
point to this file. A doc set is a few files, each answering ONE question, read
in a stated order (with a docs site, by its sidebar and the README hub below), with every behaviour tied to a test and every number to the
command that produced it. Section order inside one file: `shape.md`. The HTML
page's craft: `page.md`. Prose: `writing`.

## Files

- ALWAYS keep packages, modules and utilities at the component root;
  NEVER nest a same-name package (`text-server/text_server/`) or wrap an API component in `api/`.

| Path | The one question it answers |
|---|---|
| `docs/<name>.html` | What is it, who can do what, how does it behave? The study page for a newcomer. |
| `README.md` | What is in the repository, and how do I start? |
| `PLAN.md` | Why is it split this way, and which decisions must stay true? |
| `ARCHITECTURE.md` | Where does each piece live, and how does each flow run? |
| `FEATURES.md` | What does it do today, and which test proves it? |
| `BUGS.md` | What is open: defects, deliberate limits, decisions owed? Format: `bugs`. |
| `TODO.md` | What is deferred and not yet a spec? Format: `next` § Later. |
| `specs/<NN>-<topic>.md` | What change is in flight, and why? No row above links it. Format: `specs`. |
| `<dir>/README.md` | What does this directory implement, and how is it used? |
| `test/research/README.md`, `test/research/<project>.md` | What else does this job, and how does this differ? |
| `test/research/verified.md` | Where does each number in these documents come from? |
| `CLAUDE.md`, `<dir>/CLAUDE.md` or `AGENTS.md` | What must an editor not break? |
| `LICENSE`, `NOTICE` | Under what terms? Copyright in `LICENSE`; provenance and third-party terms in `NOTICE`. |

- ALWAYS put a fact or a section in the one file whose question it answers —
  README, ARCHITECTURE, a package README and a diagram never repeat a section
  — and link it from the others in one line; NEVER a second copy, copies drift
  apart unnoticed.
- ALWAYS draw what can be drawn — a flow, a layout, the roles and their rights
  — as one diagram (`diagrams`) beside the list it illustrates; every other
  file links to it, NEVER redraws it.
- One tree beside the code: the root README and ARCHITECTURE hold the overview,
  a short section per concept with one link down. ALWAYS say at each level only
  what the level above does not, and name each file one level down in one line.
- ALWAYS open each file with its question in one sentence and links to the
  files that answer the neighbouring questions.
- ALWAYS add a file only once its question outgrows one section of the file
  above — NEVER an empty stub. Root docs are UPPERCASE; a concept gets its
  `<dir>/README.md`, with its diagram, in the directory that implements it —
  NEVER a page under `docs/`, which holds the study page and the site.
- NEVER create `todos/`, `notes/`, `facts/`, `compare/` or `WHY.md` — each
  one's content has a row above. NEVER `plans/`: plans and work records live
  under `~/.claude/` (`ship` § Work record).
- NEVER create `CHANGELOG.md` unless the project publishes versions to outside
  consumers (crates.io, npm, PyPI, a plugin) — history lives in git and
  the diary. A repo that keeps one keeps it; `release` writes it.
- In a repo laid out otherwise, ALWAYS put a new fact where its question already
  lives — NEVER migrate the layout unasked.

## README.md

This order; cut a section with nothing true to say. Under 150 lines.

1. The title, then what it is and who it is for, in one plain sentence.
2. The link to the study page, naming what it answers.
3. Any status that changes whether to use it (unaudited, not for real funds).
4. **Glossary** — the project's dictionary: one entry per domain term, each
   defined before its first use, and every term the docs use comes from it
   (`writing` § Language).
5. **What it gives you** — one bullet per capability that works today.
6. **What it does not give you** — each limit with its `BUGS.md` id.
7. **Packages** — directory, package name, one line, a link to its README; in
   a one-package repo, a quick start that runs and prints something instead.
8. **Commands** — every `make` target with a one-line comment.
9. **How to read this**, last — a table of order, file and the question it
   answers, the study page first, `LICENSE`/`NOTICE` unnumbered.

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

## PLAN.md and ARCHITECTURE.md

- PLAN.md holds the purpose and boundaries (which package owns what), the
  model, the decisions that must stay true and the deferred scope. ALWAYS name
  the alternative a decision rejected and why.
- ARCHITECTURE.md is for an engineer changing the code: NEVER re-explain what
  the thing is. ALWAYS give it a package-flow diagram, a repository map (path
  → what it owns), a data-ownership table (data, source of truth, consumers)
  and one diagram per concept, flows drawn in order; a concept in prose alone
  is undocumented. Draw with `diagrams`. Under 300 lines.
- A concept, here or in its `<dir>/README.md`, is its intent — what it is for,
  the constraint it keeps, how its parts relate — in its diagram plus a few
  concrete sentences, the WHY of the structure beside it. NEVER narrate what
  the code does; point at the file. A WHY that outlives the structure is a
  PLAN.md decision; link it.

## FEATURES.md

- One row per behaviour: feature, current behaviour, evidence. The evidence is
  one `` `path::exact test name` `` or `` untested — `<BUG-ID>` `` — NEVER a
  wildcard, a bare file or a source symbol.
- Today's behaviour only; planned work is a `specs/` draft or a PLAN.md
  deferred-scope line.

## Numbers — one ledger

- Every measured number in the README, FEATURES.md, the directory READMEs and
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

## Documentation checks

ALWAYS enforce documentation lint through pre-commit. NEVER add consumer
lint Makefile targets or repository checker scripts; ALWAYS reuse the tools
that own the checks:

- rumdl owns Markdown syntax, formatting and supported links/anchors.
  `software/code.md` § Layout and formatting owns its configuration.
- speclint owns spec naming, status, index agreement and code references.
  `specs/format.md` owns lifecycle and retirement; the tool README owns
  installation and the hook example.

ALWAYS check each affected complete corpus, including unchanged files that
reference deleted files. ALWAYS use `pass_filenames: false` and `always_run:
true` with explicit complete scopes or project discovery. A deletion-only
commit must activate the checks. ALWAYS prove activation with valid, invalid
and deletion-only commits, and let missing tools fail visibly.

ALWAYS verify enabled rumdl rules against the pinned version: MD057 for local
file targets and MD051 for heading fragments. Cross-file anchors need their
Markdown targets in scope. NEVER claim external URL availability from offline
checks. Ignored and external documents need explicit local checks.

ALWAYS use tests and review for semantic claims: the cited test proves the
behavior, a number means what the text says, the repository map describes the
code, and the nearest documentation hub links its children. ALWAYS verify
evidence identifiers against their sources and apply `writing/page.md` to
page quality. NEVER replace judgment with exact sentences, document inventories,
retired-file bans or a generic digit-membership check. `wisdom` owns the proof
required before promoting a rule to lint.

## Instruction files

- ONE per directory, under 200 lines: `CLAUDE.md`, or where a repo keeps
  `AGENTS.md` canonical, `AGENTS.md` plus `CLAUDE.md` as the single line
  `@AGENTS.md`; NEVER rules in both. Content: `wisdom` § CLAUDE.md (project).
- A rule that holds only in a subtree lives in that subtree's file, NEVER the
  parent; the parent names its subtree files in one line. NEVER a reading order
  or which-file index in one — the README's "How to read this" holds it.

## Tracked and local

- Every file above but `specs/` is tracked, `BUGS.md` included — it is in the
  reading order.
- Local, root-anchored in `.gitignore`: `/specs/`, `/tmp/`. ALWAYS root-anchor
  them — a bare `specs/` matches at every depth and swallows a real
  `src/specs/`. A repo that already tracks `specs/` keeps tracking it.
- A repo carries no diary (`diary` § Where it lives).

## Keeping it

- NEVER shorten a doc by cutting its limits, its alternatives or its why —
  the goal is one question answered per file, not brevity.
- ALWAYS cite alternatives generously and accurately enough that their authors
  would not object; a superlative carries its ledger number; a roadmap item is
  never listed as a feature.
- ALWAYS give "What it does not give you" the length of the pitch — a limits
  section shorter than the sell is a sell.
- ALWAYS state assumptions and the trust model as flat bullets, NEVER buried in
  prose.
- An examples index carries a verdict column saying whether the reader gets
  the same result without the project ("Plain transaction?": Yes / Yes,
  weaker / No), with every value defined in a list ABOVE the table. NEVER a
  verdict the reader decodes by guessing.
- An example file whose flow the tests and the CLI already run opens by
  saying why it exists, and says in those lines that it sends nothing when it
  sends nothing.
- The why section, the Why page on a docs site, names the obvious wrong
  reason to adopt and refutes it with a number ("many calls in one
  transaction is not the reason: thirty transfers already fit in one"),
  before the real reason.
