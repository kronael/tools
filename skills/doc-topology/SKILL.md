---
name: doc-topology
description: Structure a project's docs by the question each file answers — README (what/why/how-to-start), ARCHITECTURE (how it's built), notes/ (why this design), compare/ (versus alternatives), facts/ (dated numbers) — plus a "how to read this" index and an anti-marketing discipline. Use when writing or auditing a project/crate/service README, ARCHITECTURE, or design docs; when docs are one mixed wall; or when someone asks for "good docs matching X quality". NOT for a single doc's prose polish (use writing), a design spec (use specs), or syncing docs after shipping (use readme).
when_to_use: "structure project docs, doc topology, README vs ARCHITECTURE split, docs are one wall, good docs like X quality, notes/compare/facts layout, anti-marketing docs, audit doc structure, how-to-read-this index, is this README good, test the README, fresh-reader test"
---

# Documentation topology

Great docs aren't one long file — they're a small set of files, **each answering
exactly one question**, cross-linked by a "how to read this" index. Mixing the
questions ("what is it" tangled with "how is it built" tangled with "why not the
simpler thing") is what makes docs unreadable. Split by question first, write
second.

## One question per file

| File | The one question | Holds |
|---|---|---|
| `README.md` | What is this, why use it, how do I start | elevator pitch (line 2, one sentence), plain-English glossary before any jargon, "How fast" (benched number + repro command + caveat) if perf matters, "Why this exists" (the gap), "What it gives you" (bullet per capability — no removed/dead features), "Quick start" (runnable, links a real example), "Guarantees", "When NOT to use this", requirements/assumptions, lineage/acknowledgments, "How to read this" index |
| `ARCHITECTURE.md` | How is it built internally | module/file table (one-line purpose each), ASCII data-flow/layout diagrams, algorithm walk-throughs, trust model + invariants, edge cases, "Architectural Decisions" (each names the *rejected* alternative and why) |
| `notes/*.md` (or `WHY.md`) | Why this design, not a simpler one | one file per non-obvious decision, each **Problem → Fix → Cost-it-removes**, cited sources, a trade-off, no "measured" numbers (those live in README/ARCHITECTURE), a through-line paragraph naming the pattern across the fixes |
| `compare/*.md` | How it stacks up vs named alternatives | one file per competitor, cited lineage, generous not dismissive |
| `facts/*.md` | Dated, sourced numeric claims | YAML frontmatter `date:`/`sources:`/`status:` so numbers can't silently rot |
| crate-local `CLAUDE.md` | Doc *conventions* for this component | which file answers which question, a "keeper sections — don't regress" list, an update checklist |

State the split explicitly — end the README with a **"How to read this"** section
that says which file answers which question. The topology should be told, not
just implied.

## Derivable and lookupable content doesn't belong

ARCHITECTURE.md holds what a reader with the repo open could not work out for
themselves. A directory or file-tree listing is orientation, not architecture —
cut it, or fold only the genuinely unique fact (a file two unrelated
subsystems both import) into prose. A named third-party technology (a
framework, a spec, a vendor product) gets one link to its own docs, not a
paraphrase of how it works — assume the reader already knows it or will look
it up, and state only what's true of *this* repo's use of it.

## Generalize instead of enumerating

Write the governing rule, not a list of its current instances — the rule
survives the day a new instance shows up, the list needs an edit for every one.
Two tells that a doc has regressed into a list: a section titled after one
instance ("Adding an API") that turns out to only cover one variant, or two
near-identical bullets that differ only by a name.

## notes/ — the "why" layer

Tribal design-rationale rots unless it's written down. Each note:

1. **Restate the domain term in plain English before using it** ("An order book
   is the live list of resting bids and asks…"). Never assume the reader knows.
2. **Problem** — what the naive/simpler approach costs, *quantified* ("allocates
   a node per level, O(log n) per update").
3. **Fix** — the actual mechanism, prose + one code/ASCII sketch.
4. **Cost it removes** — tie back to the budget the fix protects.
5. **Through-line** — a closing paragraph naming the *pattern* across the notes.
6. **Cite** prior art with links (papers, crates, blog posts you borrowed from).

## Numbers: a source-of-truth chain

Doc rot lives in stale numbers. Chain them: **the benchmark is authoritative →
a dated `facts/*.md` records the number with its source/date → README and
ARCHITECTURE *quote* from facts and cite the bench name + repro command.** Never
inline a raw number that has no bench behind it. Every perf claim gets a caveat:
loopback ≠ production, single-core ≠ cross-process, closed-loop ≠ real workload —
and cite the honest cross-process number next to the flattering microbench.

## Anti-marketing discipline

High-quality docs read *earned*, not sold:

- Every superlative is immediately backed by a number + its bench name.
- The "When NOT to use this" / "Limitations" section is as long as the pitch.
- Alternatives are cited *generously* ("if this doesn't fit you, no problem"),
  never strawmanned.
- Assumptions and trust model are stated as flat non-negotiable bullets, not
  buried in prose.
- No badges, no adjectives ("blazing", "powerful"), no roadmap-as-feature.

## Test a README, don't just read it critically

A README is good only if a reader with zero context — no prior session,
nothing but the file — can answer from it alone what the project is and what
it's for. Reading it critically can't tell you that; it only surfaces
wording problems, not missing facts. Test it directly instead:

1. Read only the README and **write down** what you now believe: what the
   project is, what problem it solves, how it's built, how to run it, how to
   change it, what it does not do. An unrecorded mental model can't be
   checked against anything later.
2. Do the orientation pass you'd do anyway: list the tree, read the entry
   points and the build file, run the build and the tests, follow one
   request or code path end to end.
3. **Diff the recorded account against what you found.** Every divergence is
   a defect, and its kind says what to fix: something the README asserted
   that isn't true (stale fact), something it implied that misled (wording
   or emphasis), or something you needed and had to discover yourself
   (omission).

Step 2 is what makes step 3 work — you can't notice an omission by reading
alone, only by needing a fact and not finding it. This turns "the docs feel
vague" into a specific list of claims that failed.

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
