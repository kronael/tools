---
name: design-eval
description: Design evaluation — visual + interaction design craft of a UI from a senior product-designer / design-system-owner lens (hierarchy, colour + measured contrast, tokens, density, redundant channels, data-density, minimalism, honesty). NOT novice can-I-use-it UX (use 13yo-eval), NOT code/production (use cto-eval), NOT adversarial failure modes (use red-eval).
when_to_use: "design evaluation, design review, design audit, is the UI good, visual design critique, design-system audit, contrast/accessibility audit, evaluate the screens, dashboard / data-dense UI design quality"
user-invocable: true
---

# Design Eval

Judge a UI's DESIGN CRAFT the way a design-system owner reviews a screen —
evidence-based, not taste. Read `rubric.md` for the ten dimensions + the verdict
template. Grounded in the methodology at `~/.claude/skills/go-gl/design-systems-research.md`
(Material 3 / Fluent / Carbon / DTCG tokens, WCAG + APCA, Cleveland-McGill,
Okabe-Ito) and NN/g's heuristics.

## Dispatch

- **Design review** (default): score the UI against the rubric's ten dimensions;
  produce ranked findings + a per-dimension verdict.
- **Design-system audit** (on request): deeper — the token structure, the full
  contrast matrix (WCAG + APCA over every ink×bg pair), consistency across screens.

## Rules

- **ALWAYS look at the RENDERED output, not just code.** A design eval that never
  sees pixels is invalid — read the rendered goldens/screenshots (rsx-glass
  `soft/testdata/*.png`, rsx-term DOM goldens or a captured screen). If you cannot
  see the pixels, that inability IS a finding, not an excuse to eyeball the code.
- **ALWAYS ground colour findings in a MEASURED number** — WCAG 1.4.3 (4.5:1
  text; 3:1 large) / 1.4.11 (3:1 non-text) AND **APCA Lc** (WCAG's symmetric
  ratio overestimates contrast on near-black bases; APCA is polarity-aware).
  State both values; never "looks low-contrast".
- **ALWAYS apply the redundant-channel test.** Any meaning carried by hue MUST
  have a second non-colour channel (shape / position / text / sign). Hue-alone is
  a finding (deuteranopia), even if the palette is pretty.
- **ALWAYS separate the visual LANGUAGE from this SCREEN's use of it.** Two
  distinct verdicts: is the design *system* sound (tokens, hierarchy, honesty,
  colour=meaning), vs does this screen *apply* it correctly? A screen bug and a
  system gap get fixed in different places.
- **ALWAYS end with the rubric verdict template** — per-dimension score, the top
  ranked findings (most-damaging first), and a KEEP vs SHARPEN split. Rank by
  reader impact: a misread magnitude or an invisible-in-colourblind meaning beats
  a spacing nit.
- **NEVER give a "looks nice / clean" verdict.** Every claim maps to a rubric
  dimension + concrete evidence (a pixel, a token name, a contrast number).
- **NEVER blur the lenses.** design-eval owns visual + interaction *craft*;
  13yo-eval owns novice *comprehension*; cto-eval owns *code/production*. If a
  finding is really "a novice can't tell what this is", route it to 13yo-eval.
- **ALWAYS reserve scope honestly for a pixels-only surface** (raw GL / canvas):
  it exposes no accessibility tree, focus order, screen-reader text, or IME —
  contrast + redundant channel is the *ceiling* of what you can claim, not "a11y
  covered". State that boundary.

## Output

One report per subject (do not merge two apps). Observed dimension scores (1–5;
otherwise N/A), the ranked findings each tagged `[system]` or `[screen]` with
the fix + where it lives, and a two-line verdict. When run before an improvement
pass, the findings ARE the work list — hand them straight to the fix.
