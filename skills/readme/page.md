# Doc page — one HTML explainer with diagrams

A self-contained HTML page under `docs/` that explains how a system works to
someone who will use or change the code: sections, inline SVG flow diagrams,
claims backed by the repository's tests, source and notes. Craft as
`onepager.md` § Rules — one file, inline CSS and SVG, one font, one accent,
measure ≤70ch, dark-mode-safe. Prose follows the `writing` skill; the
finishing pass is `humanize`. ALWAYS render the page and read the pixels
before handing over (`visual` agent) — an unfinished layout shows only there.

## Evidence

- ALWAYS put the link on the words of the claim it proves (`writing`, the
  parentheses rule) and NEVER a provenance badge on every line: when the
  apparatus outweighs the content the page reads as a dashboard, not an
  explanation.
- ALWAYS mark only what is NOT proven, in words ("not yet run on the copy");
  a proven claim carries its link and nothing else. A legend of status kinds
  means the marking has outgrown the content — cut the kinds, keep the words.
- ALWAYS fold each section's evidence list into one closed `<details>`;
  NEVER an always-open ledger in every section.
- An error name and code appears ONCE — beside its evidence or in one table —
  NEVER chained through a caption, callout or diagram box, and NEVER the same
  code explained twice in one section.

## Headings and navigation

- ALWAYS name the topic plainly. NEVER an "X: Y" colon heading — in h2–h4,
  card titles or SVG `<title>` alike (humanize #31).
- ALWAYS make a nav label the heading it jumps to, word for word.

## Sections

- ALWAYS let the content set a section's shape. NEVER one skeleton — intro,
  figure, caption, callout, evidence — stamped on every section.
- A callout holds one point in under 40 words. Settings, keys, refusals and
  limits are a table, NEVER a callout that grows into prose.
- NEVER a legend wall before the first content — a legend sits at the diagram
  that needs it, and a swatch's label covers every use of that colour.

## Diagrams

- One colour means one actor across the whole page (design-eval rubric #8).
- NEVER draw an edge label over an arrowhead — ALWAYS beside the edge.
- NEVER a lone box in a row built for three — fill the row or give the box
  its own; a box is sized to its text, NEVER a large empty bottom.
- A wide and a narrow variant of one diagram carry the same edge labels.

## Contrast

- ALWAYS measure every text colour on every background it sits on, in BOTH
  themes, against WCAG AA 4.5:1 (design-eval rubric #3) — a status colour that
  reads on dark fails on white, and a heading colour on its own tinted callout
  is a pair too. Prose is the primary ink, NEVER the muted token.

## Keeping it true

A page is checked when written; the repo moves on. ALWAYS run the fact pass
on every later refine — every cited test name, path and count grepped, every
claim against the newest results — before any style pass (`refine` lens
`readme.md`).
