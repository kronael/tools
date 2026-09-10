# Codex adversarial critique — research-social-meme.md

Audit trail. Raw adversarial pass (codex-cli 0.144.4). Kept verbatim; folds
applied to the SKILL and to the research doc's "Corrections" section.

## Claims where the source does not support the number
- NN/g scanning studies do not establish the **0.5–2s image dwell time** — extrapolated.
- The **40px** floor is only sound for fixed 1080→~500 scaling (`40×500/1080 = 18.5px`); real X render varies.
- **90px** headline → 41.7px on-screen, but no cited evidence makes 90px an *optimal* minimum.
- WCAG 1.4.5 *discourages* images of text; it does not itself set the contrast rule.
- "**4.5:1 always**" is stricter than WCAG, which permits 3:1 for qualifying large text.
- **8–10 hook words, 20–25 total, 64px margins, 300px stats** are house preferences dressed as findings.
- **≤12 code lines** is arbitrary — width, font size, syntax density, annotations matter more; Carbon's stars don't prove a line threshold.
- Facebook 20%-overlay research does not transfer cleanly to organic X posts for senior engineers.
- **50–90% link-reach loss** and **~2× native-media boost** read as folklore, not stable measurements; "directional" does not rescue fake precision.
- Vendor virality roundups can't establish that numbers/before-after layouts generally win.

## Protocol steps that still generate generic output
- **No evidence-acquisition step** — an agent can invent a metric, then execute the checklist perfectly. (THE hole.)
- "Concrete and falsifiable" is never *verified* — require a benchmark/command/commit/artifact/source.
- "Never hedge" encourages false certainty; hardware/workload/version/scope qualifiers are often essential.
- "Strong verb + curiosity gap + benefit" reliably emits growth-copy: "Ship faster," "Cut complexity."
- One accent + huge type + asymmetry + tiny branding is just a *different* recognizable template.
- Thumbnail-squint tests legibility, not novelty, truth, or project specificity.

## Modes that overlap
- STAT and BEFORE/AFTER collapse whenever the centerpiece is a numeric delta.
- HOT-TAKE collapses into STAT when numbered; CODE-SHOT collapses into BEFORE/AFTER for diffs/LOC.

## Cut
- Merge Principles, Copy rules, Validation, Anti-slop, Pitfalls — they repeat one-claim / low-word / high-contrast.

## Biggest risk
- **It validates presentation, not insight.** An agent can dress a generic claim in anti-slop aesthetics and ship polished AI slop.

## Folds applied
1. Added a hard **Gate 0 — Evidence** step: no post without a checkable artifact pulled from the repo (command output, LOC, binary size, real API, benchmark). This is the anti-slop lever, not the styling.
2. Cut all fabricated percentages. Kept only the actionable rule: post native media, link in a reply.
3. Numeric thresholds reframed as **defaults/floors** with the downscale assumption stated — not laws.
4. Softened "never hedge" → kill *marketing* hedges, keep *technical* qualifiers (version, workload). Precision ≠ hedging.
5. Collapsed 4 modes → **3** keyed by hero element (CODE / DELTA / TAKE); numeric delta lives in DELTA.
6. Added the **transferability test**: if the hook fits any other project, it is slop — rewrite until it names the specific thing.
7. 4.5:1 kept as an opinionated floor, noted as stricter than WCAG (helps thumbnail legibility).
