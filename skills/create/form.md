# Form — measurable checks for a finished page

Trial: kept only if the owner confirms after use.

The FORM of a standalone HTML page — layout, spacing, alignment, type, boxes,
colour, figures, phone reflow — judged by numbers a headless browser reads
from the rendered DOM, not by taste. The prose and page rules (headers as
claims, boxes, sources, links, density) live in `writing/page.md` and are not
repeated here; this file holds only what a machine measures and the
thresholds that calibration set. WHY: every rule below is one the owner has
prompted for by hand on an earlier page, and a reviewer's "looks fine" has
never caught them.

## Run

- ALWAYS render headless at 1440x900 and 375x812, light and dark
  (`prefers-color-scheme`), after `document.fonts.ready`; run the layout
  checks with every `<details>` closed (what a presenter sees) and the
  overflow, clipping, overlap and contrast checks again with all of them
  open. One Bun TypeScript script over `playwright-core` and the locally
  installed Chromium — NEVER a network fetch, NEVER a shell pipeline.
- ALWAYS print each failure as the check name, a CSS path, the page rect and
  one line of detail, crop every failing region to a PNG, and exit nonzero on
  any failure; a green run that prints nothing teaches nothing.
- ALWAYS calibrate every threshold on the pages the owner has accepted: a
  check an accepted page fails is too strict, and the loosening is written
  next to the threshold, not hidden in the code.
- ALWAYS plant one violation per check in a scratch copy of the page and read
  that the run fails before trusting a green run — a checker that cannot flag
  and a broken one look identical.
- ALWAYS measure with the page's first-choice fonts installed when the
  numbers are close: a fallback font is wider, so fit and measure results on
  a host without the fonts are conservative, never lenient.
- NEVER let a check fire inside a figure for what a figure does on purpose
  (short boxes beside tall ones, labels on connectors): the row and fill
  checks skip `figure`, `svg`, tables and navigation, and the SVG checks
  cover drawn boxes instead.

## Checks and calibrated thresholds

Thresholds come from three accepted sibling pages; "watch" means printed,
never failing. Rects are `getBoundingClientRect()` plus scroll offset; text
lines are `Range.getClientRects()` per text node; a visible element has a
rect larger than 1x1 (screen-reader-only text is skipped).

| Rule | Metric | Fails when |
|---|---|---|
| Nothing clipped or off screen | `scrollWidth` vs `innerWidth`; any rect outside the viewport; for `overflow: visible` the element's own text lines past its border box, for hidden/auto `scrollWidth - clientWidth` | > 1px |
| Text fills its box | in a framed prose box ≥ 300px wide (border or background, holding p/ul/dl/h3), widest line ÷ content width | < 60% |
| A section fills its width | per top-level section, 32px strips: mean share of the width right of the rightmost painted rect | > 25% (hero > 45%) at 1440 |
| The content uses the screen | main width ÷ viewport width at 1440 | < 80% |
| Cards in a row end together | row of ≥ 2 similar-width items ≥ 40px tall: row bottom − last content bottom − padding, ÷ row height | > 55% and > 48px |
| First lines align across a row | spread of the first text-line tops in the row | > 8px |
| No lone box | a grid whose last row holds one framed item under a row of ≥ 2 of the same width | any |
| A drawn box is sized to its text | SVG `rect` holding text or boxes: empty height below the content ÷ rect height, when taller than 2.5 lines | > 45% |
| Labels clear of lines, edges, arrowheads | every path/line sampled every 3px in screen space, hit against SVG text rects grown by the clearance (a label with its own backing shape is exempt); every `rect` perimeter hit against the text rects themselves; a `marker-end` end point inside a label; text outside its `<svg>` | a line within 6px of a label; a box edge crossing a label; any arrowhead under a label or text outside its figure |
| A connector is short and direct | a stroked path with an arrow marker, sampled every 3px: turns over 30° between steps, adjacent turning steps merged into one corner | > 1 corner (the accepted figures draw every connector as one straight segment) |
| A connector keeps clear of boxes it does not join | the same samples against every leaf box (a `rect` holding text and no other `rect`) the connector neither starts nor ends on | ≥ 20px of the path inside the box, or within 12px of its edge |
| The key sits at the first figure of its kind | figures grouped by kind, the tag and classes of the first child that is not a heading, caption, paragraph or key; when a later figure of a kind carries a key, the first one must carry a key, follow a page-level key (one outside every figure), or name in its own words every keyed mark it draws (an element carrying a swatch's own classes, those not shared with another swatch of that key) | any |
| A key lists only what its figure draws | per key item, the colours its swatch paints (border sides, background, SVG fill and stroke, `::before`/`::after`) against those painted by the visible elements of its scope: the figure it sits in, or, outside every figure, the figures up to the next such key; an item whose label states a count of none is exempt | any swatch colour not painted |
| No text overlaps | pairwise intersection of text line boxes and SVG text rects of unrelated elements | > 2px both ways |
| Phone reflow | the overflow, clip and label checks at 375; which wide/narrow variants are visible | any |
| Body text size | `body` size and the median of paragraphs ≥ 80 characters, outside figures and notes | < 16px |
| Secondary text size | smallest li/dd/dt/p outside figures | < 13px |
| Smallest text | smallest rendered size, SVG text scaled by viewBox ÷ rendered width | < 11px |
| One family | distinct first family names over all text | > 2 (sans + mono) |
| Few sizes | distinct HTML sizes in 0.5px buckets | > 16 fails; ≤ 5 is the target (watch) |
| Line length | widest line ÷ mean character width of the element's font | > 160 characters |
| Line height | smallest line-height ÷ font-size over prose | < 1.3 |
| Contrast | every text leaf and SVG text against the background `elementsFromPoint` finds under its first line, alpha-blended, both themes | < 4.5:1 (< 3:1 at ≥ 24px or bold ≥ 18.66px) |
| Body background | alpha of `body`'s background in both themes | < 1 |
| No accent stripe | solid left border ≥ 3px wider than the right on a block ≥ 24px tall; top border ≥ 3px wider than the bottom on a block ≥ 120px wide | any |
| No stacked all-caps | two `text-transform: uppercase` siblings within 20px vertically; counts of caps labels and pills | stacked: any; counts: watch |
| Legend at its figure | a legend element not inside a figure, more than 56px from one, and not a section key (only headings stand between it and the next figure of its section); a legend above the first h2 | any |
| Heading structure | one h1; no level skipped in order; each top-level section opens with h2 (the hero may hold the h1) | any |
| One rhythm | distinct gaps between the main container's children; gaps inside sections | > 2 top-level gap values; inner: watch |
| Self-contained | stylesheet, script, image, frame or font sources that are not inline or `data:` | any |
| Reader not stranded | sticky header height vs `scroll-padding-top`; the h1 inside the first viewport; count of links to the top | header taller than the padding; h1 below the fold; links: watch |
| Same look as siblings | content width share, body size, families, gap set, min contrast, brand block, compared across the pages given | a value that differs |

Calibration record for the thresholds above: the accepted pages run 12–15
HTML font sizes, captions and notes to 119–154 characters and body prose to
86–140, carry one hero at 40% right-empty, one code map column 52% empty and
address lines at 11.0px; every looser number in the table exists for one of
those. Their one drawn architecture figure keeps every label at least 9px
from a line but sets band headers 4px inside a box edge, which is why the
clearance applies to lines and not to edges; a bar chart that names its
series in each bar's own label carries no key, which is why own words
exempt a first figure. Keys are matched by colour, not class: the
accepted keys name swatches with classes their figures never use, while
every swatch colour they list is painted in the figure or the figures
under the key; one accepted key lists a class with a count of none on
purpose. The owner saw three flaws the table missed
by eye: a connector routed around the figure's edge in three bends with its
label block touching it, a worked example drawn without the key its
later siblings carry, and a key inside a figure that listed a mark only
later figures draw. Two owner complaints have no metric and stay a reading task: the
colours under a figure against the shared palette, and whether a figure says
which is which.
