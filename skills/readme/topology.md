# Documentation topology

Great docs aren't one long file — they're a small set of files, **each answering
exactly one question**, cross-linked by a "how to read this" index. Mixing the
questions ("what is it" tangled with "how is it built" tangled with "why not the
simpler thing") is what makes docs unreadable. ALWAYS split by question first,
write second.

This is the *which file* axis. For the order of sections *inside* one file —
an integration guide or API-reference page an external reader works through
end to end — see `shape.md`.

## One question per file

| File | The one question | Holds |
|---|---|---|
| `README.md` | What is this, why use it, how do I start | elevator pitch (line 2, one sentence), the status line under it while anything is unaudited or unreleased, plain-English glossary before any jargon, "How fast" (benched number + repro command + caveat) if perf matters, "Why this exists" (the gap), "What it costs" (formula plus one measured figure; both rules in `sync.md` step 3), "What it gives you" (bullet per capability — no removed/dead features), "Quick start" (runnable, links a real example), "Guarantees", "When NOT to use this", requirements/assumptions, lineage/acknowledgments, "How to read this" index |
| `ARCHITECTURE.md` | How is it built internally | module/file table (one-line purpose each), ASCII data-flow/layout diagrams, algorithm walk-throughs, trust model + invariants, edge cases, "Architectural Decisions" (each names the *rejected* alternative and why) |
| `notes/*.md` (or `WHY.md`) | Why this design, not a simpler one | one file per non-obvious decision, each **Problem → Fix → Cost-it-removes**, cited sources, a trade-off, no "measured" numbers (those live in README/ARCHITECTURE), a through-line paragraph naming the pattern across the fixes |
| `compare/*.md` | How it stacks up vs named alternatives | one file per competitor, cited lineage, generous not dismissive |
| `facts/*.md` | Dated, sourced numeric claims | YAML frontmatter `date:`/`sources:`/`status:` so numbers can't silently rot |
| crate-local `CLAUDE.md` | Doc *conventions* for this component | which file answers which question, a "keeper sections — don't regress" list, an update checklist |

ALWAYS state the split explicitly — end the README with a **"How to read this"**
section naming which file answers which question, or, when a docs site exists,
give it the hub shape below.

## README as a docs-site hub

When a docs site exists, ALWAYS make the README its front door, NEVER a
second copy of the site:

- A link row directly under the pitch: documentation, getting started, how it
  works, examples.
- Each capability bullet links to the guide page of the same title.
- The one README example is a guide example, with a link to the guide page
  that holds its imports, other languages and the code that runs it — NEVER
  a README-only example nothing compiles.
- A closing "Repository layout" names each top directory. The link row plus
  "Repository layout" replace "How to read this".

## A doc site splits into guide and reference

A built docs site (VitePress, mdBook, Docusaurus) turns the file split above
into a sidebar. ALWAYS order it as the newcomer's questions arrive:

| Group | Pages | What the pages must do |
|---|---|---|
| Start here | Why, Getting started, How it works | Why carries the status line, refutes the wrong reason to adopt and states the cost; How it works is one complete annotated example on one screen |
| Capabilities | one page per thing the reader gets, titled by it ("Amounts read at run time"), NEVER by the mechanism | each opens with what the plain approach cannot do |
| Build | one how-to page per task | guide shape, `shape.md` |
| Examples | an index, then one page per example | `shape.md` § Example and recipe pages |
| Security | trust model, security posture, failure modes | each failure mode states **What happens**, then **Recover** |
| Reference | one page per SDK language, then language, wire format, errors, glossary, limits, scope | glossary: one heading per term, so every term has an anchor; limits: every maximum in one place, naming the source file the values come from; scope: a table of Choice, Instead of, Why |

ALWAYS keep contributor notes (plans, reviews, style notes) in `docs/` beside
the pages and exclude them from the build (VitePress `srcExclude`) — NEVER
publish them as reader pages.

## Repo layout (house)

- UPPERCASE at root: CLAUDE.md, README.md, ARCHITECTURE.md, SPEC.md, PLAN.md,
  TODO.md. CLAUDE.md under 200 lines: shocking patterns and project layout.
- `specs/` for design docs (`specs/index.md` the master index), `docs/` for
  project documentation, `.claude/plans/` — plan mode's directory — for plans
  and shipping artifacts (flat, type in the filename, ephemeral; `ship` § Work
  record owns the setting and the ignore step), `.diary/YYYYMMDD.md` for the
  shipping log. NO `todos/`, NO `plans/` outside `.claude/`.
- ALWAYS root-anchor the gitignore rules for local working dirs:
  `/.claude/plans/`, `/.diary/`, `/specs/`, `/BUGS.md`. The bare `specs/` form
  matches at every depth and swallows a real `src/specs/`; `/.claude/plans/`
  keeps the committed `.claude/` files (settings, commands, skills) tracked.

## notes/ — the "why" layer

Tribal design-rationale rots unless it's written down. Each note:

1. **Restate the domain term in plain English before using it** ("An order book
   is the live list of resting bids and asks…"). NEVER assume the reader knows.
2. **Problem** — what the naive/simpler approach costs, *quantified* ("allocates
   a node per level, O(log n) per update").
3. **Fix** — the actual mechanism, prose + one code/ASCII sketch.
4. **Cost it removes** — tie back to the budget the fix protects.
5. **Through-line** — a closing paragraph naming the *pattern* across the notes.
6. **Cite** prior art with links (papers, crates, blog posts you borrowed from).

## Numbers: a source-of-truth chain

Doc rot lives in stale numbers. Chain them: **the benchmark is authoritative →
a dated `facts/*.md` records the number with its source/date → README and
ARCHITECTURE *quote* from facts and cite the bench name + repro command.** NEVER
inline a raw number that has no bench behind it. Every perf claim gets a caveat:
loopback ≠ production, single-core ≠ cross-process, closed-loop ≠ real workload —
and ALWAYS cite the honest cross-process number next to the flattering microbench.

With a docs build, ALWAYS generate counts and measured tables from the
artifact that produces them — a build-time data loader reading the fixture
(VitePress `*.data.ts`), or a script that rewrites the block between marker
comments (`<!-- benchmark:name -->` to `<!-- /benchmark -->`). NEVER type such
a number into a page. The dated `facts/` chain is the fallback for a repo
without a docs build.

## Anti-marketing discipline

High-quality docs read *earned*, not sold:

- Every superlative is immediately backed by a number + its bench name.
- The "When NOT to use this" / "Limitations" section is as long as the pitch.
- Alternatives are cited *generously* ("if this doesn't fit you, no problem"),
  never strawmanned.
- Assumptions and trust model are stated as flat non-negotiable bullets, not
  buried in prose.
- No badges, no adjectives ("blazing", "powerful"), no roadmap-as-feature.
- An examples index carries a verdict column saying whether the reader gets
  the same result without the project ("Plain transaction?": Yes / Yes,
  weaker / No), with every value defined in a list ABOVE the table. NEVER a
  verdict the reader decodes by guessing.
- The Why page names the obvious wrong reason to adopt and refutes it with a
  number ("batching is not the reason: thirty transfers already fit in one
  transaction"), before the real reason.

## The failure mode this prevents

A later editor "cleans up" a good README into something shorter but worse — gutting
the caveats, the alternatives, the "why". The crate-local `CLAUDE.md`'s "keeper
sections" list and this topology are the guard: brevity is not the goal, *one
question cleanly answered per file* is.

---

*Source: distilled from the `rsx-cast` and `rsx-book` crates, whose READMEs,
ARCHITECTURE, `notes/`, `facts/`, and crate-local `CLAUDE.md` files exemplify
this topology. Themselves derived in part from the `rtrb` crate's README
conventions.*
