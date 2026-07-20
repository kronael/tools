---
name: doc-topology
description: Structure a project's docs by the question each file answers — README (what/why/how-to-start), ARCHITECTURE (how it's built), notes/ (why this design), compare/ (versus alternatives), facts/ (dated numbers) — plus a "how to read this" index and an anti-marketing discipline. Use when writing or auditing a project/crate/service README, ARCHITECTURE, or design docs; when docs are one mixed wall; or when someone asks for "good docs matching X quality". NOT for a single doc's prose polish (use writing), a design spec (use specs), or syncing docs after shipping (use readme).
when_to_use: "structure project docs, doc topology, README vs ARCHITECTURE split, how to organize docs, docs are one wall, good docs like X quality, notes/compare/facts layout, anti-marketing docs, audit doc structure, how-to-read-this index"
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
