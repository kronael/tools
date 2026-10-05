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
| `README.md` | What is this, why use it, how do I start | elevator pitch (line 2, one sentence), plain-English glossary before any jargon, "How fast" (benched number + repro command + caveat) if perf matters, "Why this exists" (the gap), "What it gives you" (bullet per capability — no removed/dead features), "Quick start" (runnable, links a real example), "Guarantees", "When NOT to use this", requirements/assumptions, lineage/acknowledgments, "How to read this" index |
| `ARCHITECTURE.md` | How is it built internally | module/file table (one-line purpose each), ASCII data-flow/layout diagrams, algorithm walk-throughs, trust model + invariants, edge cases, "Architectural Decisions" (each names the *rejected* alternative and why) |
| `notes/*.md` (or `WHY.md`) | Why this design, not a simpler one | one file per non-obvious decision, each **Problem → Fix → Cost-it-removes**, cited sources, a trade-off, no "measured" numbers (those live in README/ARCHITECTURE), a through-line paragraph naming the pattern across the fixes |
| `compare/*.md` | How it stacks up vs named alternatives | one file per competitor, cited lineage, generous not dismissive |
| `facts/*.md` | Dated, sourced numeric claims | YAML frontmatter `date:`/`sources:`/`status:` so numbers can't silently rot |
| crate-local `CLAUDE.md` | Doc *conventions* for this component | which file answers which question, a "keeper sections — don't regress" list, an update checklist |

ALWAYS state the split explicitly — end the README with a **"How to read this"**
section naming which file answers which question.

## Repo layout (house)

- UPPERCASE at root: CLAUDE.md, README.md, ARCHITECTURE.md, SPEC.md, PLAN.md,
  TODO.md. CLAUDE.md under 200 lines: shocking patterns and project layout.
- `specs/` for design docs (`specs/index.md` the master index), `docs/` for
  project documentation, `.claude/plans/` — plan mode's directory, pinned by
  `plansDirectory` in `.claude/settings.json` — for plans and shipping
  artifacts (flat, type in the filename, ephemeral; `ship` § Work record owns
  it), `.diary/YYYYMMDD.md` for the shipping log. NO `todos/`, NO `plans/`
  outside `.claude/`.
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
