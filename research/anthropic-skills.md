# Anthropic's SKILL.md guidance — conflicts with our wisdom skill

Anthropic has published guidance for writing skills, both as an engineering blog post and in their official docs and example skill repos. There's a **load-bearing disagreement** with our [`skills/wisdom/SKILL.md`](../skills/wisdom/SKILL.md) on format.

## Sources

- [Equipping Agents for the Real World with Agent Skills (Anthropic engineering blog)](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — design rationale, examples, "why" framing
- [Agent Skills best practices (Anthropic docs)](https://anthropic.mintlify.app/en/docs/agents-and-tools/agent-skills/best-practices) — checklist + anti-patterns
- [`skill-creator/SKILL.md`](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) — Anthropic's canonical meta-skill (the equivalent of our `wisdom`)

## Anthropic's stance, summarized

Five points from across the three sources:

### 1. Progressive disclosure

Skills load in layers:

- **Metadata** (`name`, `description`, `when_to_use`) is always visible to the routing layer. Keep it short and discriminating.
- **Body** loads only when the skill is selected for use. Can be longer; should be progressively organized — common case first, edge cases later.
- **Linked resources** (sibling files, scripts referenced by the skill) load on demand. Use these for reference material so the body stays workflow-oriented.

The point: **don't pay context cost upfront for content the agent might not need**. Our skills already follow this — the per-language skills (`py`, `ts`, etc.) link out to sibling files for API references.

### 2. "Pushy" descriptions

Anthropic explicitly recommends descriptions that are **assertive about when to use the skill**, not passive summaries.

- Good: "Use when editing .py files or writing Python code."
- Bad: "This skill provides Python development support."

The reason: descriptions are consumed by an LLM router that's deciding "should I use this skill?". Passive descriptions don't trigger; pushy ones do.

Our skills mostly do this well already — we use `NOT for X (use Y)` clauses, which double as disambiguation triggers. Anthropic calls this out approvingly.

### 3. "Explain *why*" beats "ALWAYS/NEVER caps"

This is the **direct conflict** with our `wisdom` skill.

Anthropic's claim: rules without rationale degrade. The model follows the letter but misses edge cases. Narrative rules with embedded "why" generalize better:

- **Anthropic-preferred**: "If you're updating a migration that's already been deployed, double-check the rollback path — out-of-order migration application leaves the schema in an inconsistent state."
- **Our wisdom-style**: "NEVER apply migrations out of order — ALWAYS check deployed state first."

Both convey the same rule. Anthropic's framing teaches; ours commands. The empirical claim is that the teaching version produces better generalization on novel cases.

### 4. Models don't improve linearly with rule count

Past ~10 rules per skill, signal is diluted by noise. The model can't attend to all of them; the marginal rule pushes other rules out of attention.

Several of our skills are close to or past this threshold. `wisdom/SKILL.md` itself has ~14 ALWAYS/NEVER lines; `commit/SKILL.md` has 11 rules. Worth measuring whether splitting these helps.

### 5. Inline examples beat additional rules

A small inline example showing the right vs wrong action provides more signal than another rule. Two reasons:

- Examples ground the rule in a concrete shape the model can pattern-match.
- Examples implicitly handle edge cases the rule wouldn't enumerate.

Anthropic's `skill-creator` skill includes example skill stubs inline. Our skills don't, because [our `wisdom` says "NEVER add obvious code examples LLMs already know"](../skills/wisdom/SKILL.md). The two positions can coexist — Anthropic isn't asking for obvious examples, they're asking for *disambiguating* examples — but the wisdom rule is currently broad enough to discourage all of them.

## Our `wisdom` skill's stance

From [`skills/wisdom/SKILL.md`](../skills/wisdom/SKILL.md):

> - ALWAYS use ALWAYS/NEVER; NEVER use SHOULD (too soft).
> - ALWAYS pair NEVER with ALWAYS: "NEVER X — ALWAYS Y instead."
> - NEVER add obvious code examples LLMs already know.

We codified ALWAYS/NEVER caps as the house style. Anthropic's data suggests this is sub-optimal for generalization.

The user's own [auto-memory](/home/ondra/.claude/projects/-home-ondra-wk-tools/memory/MEMORY.md) reinforces this preference:

> feedback_should_not_allowed.md — Skill content: use ALWAYS/NEVER only — never SHOULD (too soft)

So the rule is a deliberate choice with explicit user preference behind it, not an oversight. Resolving it isn't just adopting Anthropic's recommendation — it requires either the user changing position or evidence that the change improves outcomes.

## How to resolve — let the eval loop decide

Three options, in order of effort:

### Option 1: keep wisdom's rule, document the disagreement

Cheapest. Add a note to `wisdom/SKILL.md`:

> Anthropic recommends "explain why" over capitalized rules; we use ALWAYS/NEVER because it makes scope crisp and easier for humans to scan. Tradeoff is acknowledged; will be revisited if eval-loop data shows generalization loss.

Pros: respects user preference, no risk of breaking working skills.
Cons: leaves an unmeasured belief in place.

### Option 2: hybrid format — rule + rationale

Each rule gets a one-sentence why-clause:

- Before: "NEVER squash commits"
- After: "NEVER squash commits — preserves intermediate state for `git bisect`."

Both readable and explainable. Format-wise: the rule remains scannable; the rationale rides along for generalization.

Pros: addresses Anthropic's point without abandoning the user's house style.
Cons: ~30% more text per rule; some rules don't have a clean one-sentence why.

### Option 3: rewrite all skills in Anthropic narrative format

Heaviest. Risks regressing terseness (our skills are intentionally short).

Pros: aligns with Anthropic's research-backed recommendation.
Cons: large diff, undoes existing user feedback, no evidence it improves outcomes in *our* eval set.

## **Recommendation**: A/B in the eval loop

Don't decide a priori. Pick a skill (probably `commit`, since it has the most rules and the densest eval set), produce two variants:

- **Variant A**: current ALWAYS/NEVER form.
- **Variant B**: Anthropic-style narrative with embedded why-clauses.

Run both against the `evals/commit/` set. Compare scores. **Let the numbers settle the question.**

This matches Anthropic's own recommendation that skills should be tested against a small task suite. It matches DSPy's MIPROv2 model (propose variants, score against a held-out set, pick the winner). It matches the design of v3 (offline measurement gates merge).

The output is one of:

- Variant B scores materially higher → adopt narrative format; rewrite `wisdom` to recommend it; gradually migrate other skills.
- Variant A scores higher or equal → keep current format; document that we measured.
- Mixed (some criteria better, some worse) → adopt hybrid; rewrite `wisdom` to require rule + rationale.

This is **what the eval loop is for**. It removes the need to take Anthropic's word for it OR our own a-priori preference; we measure on our skill, our eval set, our agents.

## Other Anthropic points worth tracking

- They recommend **testing skills by running them on a small task suite**. Our eval-loop direction matches.
- They warn against **"skills that look like tutorials"** — verbose, narrative-only, no actionable lines. Our skills are mostly terse; this is one place we're already aligned.
- They suggest **versioning skills** so you can roll back. We get this for free via git. **Open question** (from the spec): should `SKILL.md` carry a `version: N` frontmatter? Git history covers it, but `version` makes rollback explicit in tooling. Probably worth adding once we have a second instance of needing to roll back.
- They emphasize **discoverability** — the routing layer is doing pattern-matching against `description` + `when_to_use`. We do this well already; our `when_to_use` fields pack retrieval keywords.

## The `skill-creator` skill — Anthropic's `wisdom` equivalent

[`skill-creator/SKILL.md`](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) is the canonical meta-skill. Notable differences from our `wisdom`:

| dimension | Anthropic's `skill-creator` | Our `wisdom` |
|---|---|---|
| Format prescription | "Use clear, narrative instructions" | "ALWAYS use ALWAYS/NEVER" |
| Examples | Inline example stubs | "NEVER add obvious code examples" |
| Length | Long body with embedded "why" | Short body, no prose |
| Rule density | ~5-7 high-level guidelines | ~14 specific ALWAYS/NEVER lines |
| Frontmatter | Same shape (name, description, when_to_use) | Same |

Both meta-skills agree on **what frontmatter looks like** and **what discoverability requires**. They disagree on **body style**.

The eval-loop A/B is the right way to resolve this. The structural agreements (frontmatter, discoverability) are stable; the body-style question is the one where we have a measurable disagreement.

## Action items

- Add a "rationale" convention to `wisdom`: new rules SHOULD pair the rule with a why-clause (Option 2 hybrid). Encode as: "Rules in new skills are encouraged to include a why-clause inline." Doesn't force migration of existing skills.
- Once the eval loop is running: A/B variant A vs variant B for `commit`. Run weekly until results stabilize.
- If variant B wins materially: rewrite `wisdom` to recommend narrative + why-clauses; open migration PR for each skill, one at a time, scored.
- Independent of the format debate: **add `version: N` frontmatter** to SKILL.md once we hit a case where we need explicit rollback. Until then, git history suffices.

## See also

- [`research/library-drift.md`](library-drift.md) — why eval-loop measurement beats a-priori format preference
- [`research/dspy-miprov2.md`](dspy-miprov2.md) — the variant-scoring pattern this recommendation borrows from
- [`specs/2-hermes-skill-autoimprove.md#open-questions`](../specs/2-hermes-skill-autoimprove.md#open-questions) — open question 4 references this conflict directly
