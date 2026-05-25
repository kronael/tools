# Anthropic's own SKILL.md guidance — conflicts with our wisdom skill

Anthropic published its internal best practices for writing skills. There's a load-bearing disagreement with our `skills/wisdom/SKILL.md`.

## Source

- [Equipping Agents for the Real World with Agent Skills (Anthropic engineering blog)](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

## Anthropic's stance

- **Explain *why***, not just *what*. Rules without rationale degrade — the model follows the letter but misses edge cases.
- Prefer narrative ("If you're updating a migration that's already been deployed, double-check the rollback…") over bullet lists of ALWAYS/NEVER.
- Models do not improve linearly with more rules. Past ~10 rules per skill, signal is diluted by noise.
- Tests inside the skill (small inline examples showing the right vs wrong action) help more than additional rules.

## Our `wisdom` skill's stance

From `skills/wisdom/SKILL.md`:

> - ALWAYS use ALWAYS/NEVER; NEVER use SHOULD (too soft).
> - ALWAYS pair NEVER with ALWAYS: "NEVER X — ALWAYS Y instead."

We tell ourselves to use ALWAYS/NEVER caps. Anthropic's data suggests this is sub-optimal.

## How to resolve

Three options, in order of effort:

1. **Keep wisdom's rule, document the disagreement**. Add a note: "Anthropic recommends 'explain why' over capitalized rules; we use ALWAYS/NEVER because it makes scope crisp and easier for humans to scan. Tradeoff is acknowledged." Cheapest.
2. **Hybrid format**. Rule line + 1-sentence rationale: "NEVER squash commits — preserves intermediate state for `git bisect`." Both readable and explainable.
3. **Rewrite all skills**. Heaviest; risks regressing terseness.

Recommendation: option 2 going forward. New rules in skills add a rationale. Don't retrofit the old ones until the bundle eval loop is online to measure whether the change helps.

## Other Anthropic points worth tracking

- They explicitly recommend testing skills by running them on a small task suite — our eval-loop direction matches.
- They warn against "skills that look like tutorials" — verbose, narrative-only, no actionable lines. Our skills are mostly terse, good.
- They suggest **versioning skills** so you can roll back when a change regresses. We get this for free via git — every skill change is a commit. Worth surfacing in the SKILL.md frontmatter? Possibly — adds a `version` field that lives alongside `name`/`description`.

## Action items

- Add a "rationale" convention to `skills/wisdom/SKILL.md`: new rules SHOULD pair the rule with a why-clause.
- Add a section to the bundle eval loop spec: "wisdom-format conflict" is a known issue, eval loop scoring should compare ALWAYS/NEVER variants against rationale-bearing variants on the same eval set.
