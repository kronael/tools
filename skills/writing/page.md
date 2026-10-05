# Page — how a document or HTML page is laid out and reads

Applies to anything with layout: an HTML explainer under `docs/`
(`readme/page.md` says what one holds), a public onepager
(`readme/onepager.md`), a README with tables and boxes, the text blocks of a
designed page (`create/web.md`). Prose follows `SKILL.md` in this directory;
the finishing pass is `humanize`. The owner rejects every pattern below on
sight as "AI slop".

## Boxes and cards

- A box or card header states the box's most important fact as a short claim
  (`SKILL.md` heading rule) — NEVER "Overview", "Details", "Keys".
- Each program, account and role gets its own box BEFORE the prose refers to
  it, under the one name the whole page uses for it.
- NEVER an accent stripe — a thick coloured top or left border per role or per
  state. ALWAYS separate cards with a neutral 1px border, spacing and type
  weight.
- NEVER a legend whose only job is to decode decorative colour — ALWAYS say who
  acts or what state applies in the card's own text.
- NEVER a pill or status tag on every line, and NEVER a provenance badge per
  claim — when the apparatus outweighs the content the page reads as a
  dashboard, not an explanation. NEVER stacked all-caps labels.
- NEVER a card written as one dense paragraph — ALWAYS short lines, one fact
  per line, with the actor, the effect and the failure each findable at a
  glance.
- A callout holds one point in under 40 words. Settings, keys, refusals and
  limits are a table, NEVER a callout that grows into prose.
- An error name and code appears ONCE — beside its evidence or in one table —
  NEVER chained through a caption, callout or diagram box, and NEVER the same
  code explained twice in one section.

## Layout

- ALWAYS give the page a real layout — parallel items (programs, keys, steps)
  sit side by side in a grid; NEVER one narrow column of stacked cards. Prose
  measure stays ≤70ch per block.
- ALWAYS let the content set a section's shape. NEVER one skeleton — intro,
  figure, caption, callout, evidence — stamped on every section.
- ALWAYS make a nav label the heading it jumps to, word for word.
- Craft: one self-contained file that renders from `file://`: inline CSS,
  inline SVG, no CDN, no external fonts, no build step. One font family, at
  most five font sizes, generous line height. One accent colour: links plus at
  most one divider, nothing else. Dark-mode-safe via `prefers-color-scheme`
  with an explicit background on `body`. A diagram only for a mechanism words
  handle badly, inline SVG or `<pre>`, never an image file. NEVER design past
  this: a taste-driven page is `create/web.md`'s job.

## Sources and links

- Citations do not crowd the explanation: each section gets ONE short sources
  note — a single line, or one closed `<details>` when it lists several —
  NEVER an always-open ledger in every section and NEVER an evidence link
  inside the prose.
- Every link shows short visible text in square brackets, "[queue test]", so
  adjacent links read as separate items; the full test path goes in the href
  or the title.
- ALWAYS mark only what is NOT proven, in words ("not yet run on the copy"); a
  proven claim is listed in the sources note and carries nothing else. A legend
  of status kinds means the marking has outgrown the content — cut the kinds,
  keep the words.

## Diagrams

- One colour means one actor across the whole page (design-eval rubric #8); a
  legend sits at the diagram that needs it, NEVER a legend wall before the
  first content, and a swatch's label covers every use of that colour.
- A figure title and an SVG `<title>` state the claim, as headers do.
- NEVER draw an edge label over an arrowhead — ALWAYS beside the edge.
- NEVER a lone box in a row built for three — fill the row or give the box its
  own; a box is sized to its text, NEVER a large empty bottom.
- A wide and a narrow variant of one diagram carry the same edge labels.

## Contrast

- ALWAYS measure every text colour on every background it sits on, in BOTH
  themes, against WCAG AA 4.5:1 (design-eval rubric #3) — a status colour that
  reads on dark fails on white, and a heading colour on its own tinted callout
  is a pair too. Prose is the primary ink, NEVER the muted token.

## Before handing over

ALWAYS render the page and read the pixels (`visual` skill) — an unfinished
layout shows only there. On a later refine the fact pass runs first (`refine`
lens `readme.md`); a style pass alone polishes a page that is wrong.
