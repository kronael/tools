# Page — how a document or HTML page is laid out and reads

Applies to anything with layout: an HTML explainer under `docs/`
(`readme/page.md` says what one holds, in what order), a public onepager
(`readme/onepager.md`), a README with tables and boxes, the text blocks of a
designed page (`create/web.md`). Prose follows `SKILL.md` in this directory;
the finishing pass is `humanize`. The owner rejects every pattern below on
sight as "AI slop", and a page is finished only when § Before handing over
passes — every item there is one the owner otherwise prompts for.

## Boxes and cards

- A box or card header states the box's most important fact as a short claim
  (`SKILL.md` heading rule) — NEVER "Overview", "Details", "Keys".
- Each program, account and role gets its own box BEFORE the prose refers to
  it, under the one name the whole page uses for it.
- ALWAYS a description list (`<dl>`, or bold term then its line) for
  components, paths, roles and rules — the name, then what it does and where
  it lives. NEVER a run of names inside a sentence: a reader scans a list and
  loses a sentence.
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
- ALWAYS size a card to its text and let the text fill the width it is given.
  NEVER a narrow left-hugging column inside a wide card, a clipped line, an
  empty bottom or one tall card in a row of short ones (a subgrid evens a row).
  Text that does not fill its box reads as broken whatever it says.
- A callout holds one point in under 40 words. Settings, keys, refusals and
  limits are a table, NEVER a callout that grows into prose.
- A fact, a number or an error name and code appears ONCE — beside its
  evidence or in one table; a second place links to the first. NEVER the same
  metric in a summary card and again in the body, and NEVER a code chained
  through a caption, callout and diagram box.

## Layout

- ALWAYS give the page a real layout — parallel items (programs, keys, steps)
  sit side by side in a grid; NEVER one narrow column of stacked cards. Prose
  measure stays ≤70ch per block, and a wide screen is filled, not one centred
  column between wide margins.
- ALWAYS let the content set a section's shape. NEVER one skeleton — intro,
  figure, caption, callout, evidence — stamped on every section.
- ALWAYS give a page one name everywhere a doc set lists it — the sidebar
  entry, the index row and the page title match word for word. A rule lives
  on one page (`readme/sync.md` § Rules).
- In-page navigation is ONE inline block of short links, "[Roles] [Flows]
  [Limits]", each one or two words taken from its heading — NEVER a vertical
  list and NEVER a word the heading does not use; the heading keeps the full
  claim. Sibling pages link each other from the top.
- NEVER strand the reader: every section offers a way back to the top, and
  the first screen says what the thing is and its state.
- ALWAYS give a heading that another page or the README links to an explicit
  short anchor — `## What it costs {#cost}` in VitePress, `id="cost"` in
  HTML. NEVER let inbound links ride the generated slug, which changes
  whenever the heading is reworded.
- Craft, for a standalone document or explainer page: one self-contained file
  that renders from `file://` and under any path prefix: inline CSS, inline
  SVG, relative links only, no CDN, no external fonts, no build step. One font
  family, at most five font sizes, body at 16px or larger, generous line
  height. One accent colour: links plus at most one divider; actor colours
  live in figures only. Dark-mode-safe via `prefers-color-scheme` with an
  explicit background on `body`. A diagram is inline SVG or `<pre>`, never an
  image file. One short stylesheet: simplifying the CSS is what cleans the
  layout. An existing app's UI keeps its own stack and build. NEVER design
  past this: a taste-driven page is `create/web.md`'s job.
- ALWAYS carry what the sibling pages carry — the brand block in the header
  (project name, mark, section label), the same tokens, components, page
  width and names — so the set reads as one. NEVER add a visual element no
  sibling has (a new box kind, badge or colour) without asking, and a change
  to a shared element lands on every page in one pass.
- At phone width a figure reflows or gets its narrow variant, a full address
  wraps, nothing scrolls sideways.

## Density

- ALWAYS budget the words: a study page near 5,000 visible words, labels shown
  on a phone included, a onepager near 500 (`readme/onepager.md`). Past the
  budget the owner cuts, so cut first: the obvious, the second statement of a
  fact, the mechanics. NEVER cut a feature or a limit to make the budget.
- NEVER mechanics that decide nothing — rent and who pays it, call depth, byte
  layouts, how a tool works inside. The page shows who signs, what moves, what
  is refused, and the proof.
- NEVER an identifier that carries no claim — a list of variant names, bare
  field or function names. One that stays gets a plain gloss. Every term is
  defined at first use or cut, and a list of terms is headed "Glossary".
- NEVER re-explain an upstream system: name it, say what the page relies on,
  link its own docs.
- ALWAYS use the name the code and the sibling pages use; NEVER coin one, and
  NEVER two names for one thing. A rename sweeps every page and doc at once.
- After every cut, read each paragraph whole: a sentence without its verb or a
  clause pointing nowhere is a defect the cut left behind.

## Sources and links

- Citations do not crowd the explanation: each section gets ONE short sources
  note — a single line, or one closed `<details>` when it lists several —
  NEVER an always-open ledger in every section and NEVER an evidence link
  inside the prose.
- Every link shows short visible text in square brackets, "[queue test]", so
  adjacent links read as separate items; the full test path goes in the href
  or the title.
- A code link names the exact lines, `#L12-L20` on the host's own line view:
  a relative path while the page ships inside the repo, a blob URL pinned to
  a commit once it is served elsewhere. NEVER a code viewer of your own.
- Every identifier on the page links — code, a test, or a live `BUGS.md`
  entry — or it goes. A bare step id, plan number or retired bug id is noise.
- ALWAYS mark only what is NOT proven, in words ("not yet run on the copy"); a
  proven claim is listed in the sources note and carries nothing else. A legend
  of status kinds means the marking has outgrown the content — cut the kinds,
  keep the words. Out of scope means deferred: the stub stays, marked in
  words, NEVER deleted.

## Diagrams

- ALWAYS one architecture figure first, every actor on it, then one figure per
  flow and per tested scenario the page claims — who signs, what moves, what
  is refused. A table, not a figure, for settings, keys and limits. The test
  of a figure is that it makes the reader's next question moot.
- ALWAYS draw a flow faithful to the code and the test it cites: one actor per
  lifeline, the real sequence end to end, which-is-which labelled on the
  picture, not in the prose. NEVER two scenarios merged into one figure, a
  flow that undoes itself, or a generic illustration where a real worked case
  exists.
- A refusal figure shows what was tried and the check that stops it; a bare
  refusal proves nothing.
- One colour means one actor, or one owner (ours, already deployed, third
  party), across the whole page (`eval/design/rubric.md` #8); a legend sits at
  the diagram that needs it, NEVER a legend wall before the first content, and
  a swatch's label covers every use of that colour.
- A box is labelled by what it is for, NEVER by its language or tool ("the
  scheduler", not "Rust CLI").
- A figure title and an SVG `<title>` state the claim, as headers do; one
  short caption at most.
- NEVER draw an edge label over an arrowhead — ALWAYS beside the edge.
- NEVER a lone box in a row built for three — fill the row or give the box its
  own; a box is sized to its text, NEVER a large empty bottom.
- A wide and a narrow variant of one diagram carry the same edge labels.
- A chart makes one point with few series, its reading beside it.

## Contrast

- ALWAYS measure every text colour on every background it sits on, in BOTH
  themes, against WCAG AA 4.5:1 (`eval/design/rubric.md` #3) — a status colour that
  reads on dark fails on white, and a heading colour on its own tinted callout
  is a pair too. Prose is the primary ink, NEVER the muted token.

## Before handing over

ALWAYS run every item on every page, in this order; `keeper` marks an item a
test in `make test` enforces (`readme/topology.md` § What `make lint` checks),
trusted only once it has failed on a planted violation. A sub's "looks fine"
settles nothing: read the pixels yourself (`visual` skill).

1. Facts first, on every later pass (`refine` lens `readme.md`): a style pass
   alone polishes a page that is wrong.
2. Rendered at 1440 and 375, light and dark, read as viewport screenshots —
   a full-page capture is too tall to judge. `keeper`: overflow, contrast.
3. Text fills its box: no clipped line, empty bottom or uneven row.
4. One font family, five sizes at most, body ≥16px. `keeper`
5. Word budget met, phone-visible labels counted. `keeper`
6. Every term glossed at first use or cut; the term list is "Glossary".
7. No mechanics, no rent noise. `keeper`: a banned-word list.
8. Brand block present; tokens and names match the sibling pages. `keeper`
9. First screen is one claim answering the question the page was asked;
   every heading, box header and figure title is a claim. `keeper`: generic
   labels.
10. Each figure checked against the code and test it cites by a reader who
    did not draw it.
11. Every claim links to its evidence, every identifier links or is gone,
    every link resolves. `keeper`
12. No work-record prose: step ids, phase names, planned tests, what the
    session did. `keeper`: ids outside links.
13. A fact, number or error code appears once. `keeper`
14. Limits sit right after the answer, each one plain claim; the decide
    section closes the page (`readme/page.md`).
15. Edited in place, one writer at a time — NEVER a draft copy beside the
    page.
