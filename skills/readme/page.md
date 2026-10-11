# Doc page — one HTML explainer with diagrams

A self-contained HTML page under `docs/` that explains how a system works to
someone who will use or change the code, good enough to present from and to
study from: sections, inline SVG flow diagrams, claims backed by the
repository's tests, source and notes. It is NEVER a record of the work.

How it reads and looks — headers, boxes, layout, density, sources and links,
diagrams, contrast, the checklist before handing over — is the `writing`
skill: ALWAYS read `writing/page.md` in full before writing one or stripping
the generated look from one.

## What it holds — ALWAYS in this order

1. One claim that answers the question the page was asked, then what the
   thing is and its state today.
2. How the parts fit: one architecture figure with every actor, then who can
   do what, roles first — so the limits below can name them.
3. The limits and gaps, before any flow detail. A limit that changes a
   decision stays; the rest is a `BUGS.md` entry. Each is one plain claim:
   who is affected, what stops it, the link.
4. Each flow or finding as its own block — the result, its figure, its
   evidence. NEVER a status paragraph or a list of step ids.
5. A decide section last: whether the design holds, what the evidence
   supports, what is open, where the built design differs from `PLAN.md` and
   why, and for each design choice what it buys, not only the problem it
   solves. The page restates a decision; `PLAN.md` owns it
   (`topology.md`), so it is not re-argued here.

ALWAYS describe the design that exists. NEVER "either/or" or a rejected
option in the body — a comparison gets one section of its own, design options
the design doc.

ALWAYS run the `eval` skill's CEO, CTO and novice lenses on a page meant for
a decision, verify each finding, and fix the page defects within the asked
scope; a product defect goes to `BUGS.md` (WISDOM § Bug triage), NEVER into
the page pass. A CTO condition stays only when the project's own `BUGS.md`,
incidents or users justify it.

When the owner asks "what is X?" about the page, ALWAYS answer in the reply
and put the answer where the question arose — the figure, when that is where
— NEVER hand it to a sub to "lay out somewhere".

## Keeping it true

A page is checked when written; the repo moves on. ALWAYS run the fact pass
first on every later refine (`refine` lens `readme.md`); when to update the
page is `topology.md` § The study page.
