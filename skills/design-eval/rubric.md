# design-eval — the rubric

Score each dimension 1–5 (1 broken, 3 acceptable, 5 exemplary). Tag every finding
`[system]` (the visual language) or `[screen]` (this instance's use of it). Rank
by reader impact. Cite the pixel / token / number.

## The ten dimensions

**1. Visual hierarchy — the glance test.** In < 1 s, is the primary thing
obvious? Hierarchy comes from size / weight / colour, NOT boxes and borders
(Refactoring UI; Rams). Encode by channel rank (Cleveland-McGill: position/length
beat angle/area beat hue/saturation): exact value → text; magnitude →
length/position; category → hue; overview → luminance. NEVER encode magnitude
by hue.

**2. Colour system & tokens.** Three tiers: primitive stops → semantic roles
(named by MEANING) → component inks (Salesforce / W3C DTCG). The render reads
semantic/component, never raw hex; a theme swap rebinds the semantic tier only.
Colour = meaning, never decoration; few colours, each with intent. FINDING if
colours are raw hex scattered in the render, or a colour carries no meaning.

**3. Contrast — MEASURED, both models.** WCAG floors: text ≥ 4.5:1 (1.4.3; 3:1
only if large), non-text glyphs/UI ≥ 3:1 (1.4.11). **APCA Lc** floors (Somers,
WCAG 3 candidate): Lc 90 preferred body, Lc 75 body minimum, Lc 60 other content
text, Lc 45 large headlines; Lc 15 ≈ invisible. APCA is polarity-aware — a
near-black base can pass WCAG's symmetric ratio while failing readability, so
check BOTH and report both numbers. Reserved contrast pairs: NEVER derive a
foreground as "the background one tier up" (collapses to fg==bg). Gate the FULL
ink×bg matrix, EVERY theme, as a repeatable TEST — a one-off measure misses the
wall-tier and colourblind-theme cases.

**4. Redundant channel & colourblind.** Any meaning by hue MUST have a second
non-colour channel — shape / position / sign / text (WCAG 1.4.1). Palette
colourblind-safe (Okabe-Ito) or the meaning survives desaturation. Hue-only
category (buy/sell by colour alone) is a top finding — the fix is SHAPE/direction
(e.g. up/down triangles = buy/sell), not red-vs-green on one shape.

**5. Typography & numerics.** Numbers are **tabular** (fixed-width figures),
fixed precision, unit-scaled at the edge, right-aligned — a number that changes
width per update makes the layout jump. A constrained type scale; body legible at
the target size/DPI. FINDING on raw unscaled integers or ragged numeric columns.

**6. Spacing & density.** Spacing on a constrained scale (e.g. 4 px), not
arbitrary values (Refactoring UI). Density is a CHOSEN mode (comfortable /
compact, Fluent / Ant), one multiplier — not per-element fiddling. Start with too
much whitespace and remove.

**7. Layout & responsiveness.** Adaptive to a range of sizes; a sensible minimum
so it never collapses; content reflows (GNOME / Apple / Fluent HIGs). Size in
scale-independent units, apply DPI (effective pixels) — NEVER assume 1 coordinate
= 1 pixel. FINDING on pixel-pinned layout or HiDPI breakage.

**8. Consistency.** One meaning per colour and per glyph, everywhere; the same
token drives the same role across screens. FINDING on the same colour meaning two
things, or two glyphs doing one job (cross-check the element inventory). ALWAYS
cross-check the shared LANGUAGE against EACH renderer — a design fix made in one
renderer that never flowed to the language (or the others) is a `[system]`
finding: the template can silently diverge from its own downstream.

**9. Data-density & minimalism.** Maximise data-ink, erase chartjunk (Tufte);
every element earns its place (NN/g heuristic #8). Scales are STABLE — never
re-normalise to the current frame's max (the whole screen strobes on a spike);
verify over a sequence, not one frame. Small-multiples over one busy chart where
it helps comparison.

**10. Feedback, motion & honesty.** Response within NN/g budgets (0.1 s instant /
1 s flow / 10 s attention); one pacer, no double-paced jank. Data that stops
updating **ages visibly in place** (dims / `~` after N ms) — never a silent
last-known value. NEVER fabricate: mark estimates `~`, dash unknowns `—`,
hard-block over a fat-finger cap, withhold an overflow rather than wrap it.

## Verdict template

```
# design-eval: <subject>  (mode: review | system-audit)
Pixels seen: <goldens/screens read>   Palette source: <file>

Scores (1–5):
  hierarchy N · colour+tokens N · contrast N · redundant-channel N ·
  typography/numerics N · spacing/density N · layout/responsive N ·
  consistency N · data-density/minimalism N · feedback/honesty N

Findings (most-damaging first):
  1. [system|screen] <one line> — fix: <what/where>  (evidence: <pixel/token/Lc>)
  ...

Keep (already strong): <the dimensions at 4–5 — do not regress>
Sharpen (the gaps): <the ranked fix list = the improvement work>

Verdict: <two lines — is the language sound? is this screen's use of it sound?>
```

Reserve scope: for a pixels-only surface (raw GL / canvas) contrast + redundant
channel is the CEILING of the accessibility claim — no a11y tree / focus / IME /
screen-reader text exists. State that boundary; don't score a11y as "covered".
