# Library Drift — LLM-authored skills regress vs human-curated

The single most important paper in this corpus. The numbers in it are why our v3 design is "offline eval loop with PR gating", not "auto-edit at runtime".

## Sources

- [Library Drift: Diagnosing and Fixing a Silent Failure Mode in Self-Evolving LLM Skill Libraries, arXiv 2605.19576](https://arxiv.org/abs/2605.19576) (May 2026)
- [SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks, arXiv 2602.12670](https://arxiv.org/abs/2602.12670) (Feb 2026) — the held-out benchmark Library Drift uses to measure the +0.0pp / +16.2pp gap. 86 tasks across 11 domains with curated skills and deterministic verifiers.

## Headline finding

On SkillsBench, holding the base agent constant:

| condition | lift over baseline |
|---|---|
| **Human-curated skill library** | **+16.2 percentage points** |
| **LLM-authored skill library (no human curation)** | **+0.0 percentage points** |

Both arms started from identical baseline agents on identical task distributions. The only variable was whether a human reviewed each proposed library change before it landed.

**+0.0pp is not a measurement error.** It means letting an LLM maintain its own skill library — under the setups the paper tested — is empirically equivalent to having no skill library at all. The edits the LLM made cancelled out on net: some helped, some hurt, the average came back to baseline.

This is the load-bearing number for our spec. See [`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md#why-this-instead-of-v1v2): "any system that lets an LLM commit edits to its own skill library without an external evaluator regresses to the baseline."

## What "library drift" means in the paper

The authors define **drift** as the cumulative degradation of a skill library over autonomous edit cycles. Three distinct mechanisms produce it:

1. **Verbose-hedging drift**. Each edit cycle adds caveats and edge-case handling. The rule "always use a transaction" becomes "use a transaction unless the operation is read-only, idempotent, or the caller specified `--no-tx`, in which case...". The original signal is diluted; the agent stops trusting the rule.

2. **Loss of orthogonality**. The agent proposes new skills that overlap existing ones. When a task arrives, the retrieval/routing step has to disambiguate between two skills that both match — and picks wrong often enough to dominate the gains from either skill's content.

3. **Self-rewarded bad edits**. The LLM's own evaluation of "did this edit improve the skill?" is biased toward "yes, this looks better". Without an external evaluator, every edit appears to be an improvement; the cycle compounds noise.

The third mechanism is the killer. It's why [Hermes's Curator](hermes-agent.md) self-rates its own edits as good ("the BSWEN finding") and why we cannot let the same LLM both propose and judge an edit.

## The three-part governance recipe

The paper concludes with a recipe for keeping a self-modifying skill library net-positive. Three components, all required:

### 1. Outcome-driven retirement

Skills are retired when they **measurably stop helping**, not when they age. The library has a fixed-size hot set; anything that doesn't score well on recent eval runs falls out.

- Mechanism: every skill has a rolling outcome score (success rate on tasks where it was invoked).
- Threshold: below a configurable floor, the skill is moved to "cold storage" (still in the repo, not in the agent's active context).
- Reverse path: a cold skill can be reactivated if a new task exposes its usefulness.

**Our translation**: bundled skills already have an implicit version (git history). v3 doesn't retire skills automatically — that's Phase 2 — but the eval set will surface skills that consistently underperform on their advertised triggers. Those become deletion candidates for the maintainer.

### 2. Bounded active cap

The active skill set has a **hard size limit**, not a soft preference. The paper found that beyond ~40-60 skills, the cost of routing the wrong skill exceeds the benefit of any single skill being available.

- Mechanism: when a new skill is proposed, it must displace an existing one (a tournament against the weakest current skill).
- Why a hard cap: soft preferences are ignored by LLMs proposing edits. They keep adding.

**Our translation**: this repo currently has ~40 skills. The cap is implicitly enforced by the maintainer. v3's PR review process is the tournament: a new-skill PR has to argue why the active set should grow.

### 3. Meta-skill authoring prior

A "meta-skill" — i.e., a skill about how to write skills — is treated as a special class. It anchors the *style* the library uses. New skills must conform to the meta-skill's format, and edits to it require extra scrutiny.

- Mechanism: changes to the meta-skill trigger re-validation of *every* skill it governs.
- Why: format drift in the meta-skill propagates to every new skill, which is a multiplicative regression risk.

**Our translation**: [`skills/wisdom/SKILL.md`](../skills/wisdom/SKILL.md) is our meta-skill. Per the paper's recommendation, edits to `wisdom` should re-validate all skills that conform to it (every SKILL.md in `skills/*/`). v3's eval loop should treat a wisdom edit as a multi-skill candidate: score it across all dependent skills.

## The survey finding: nobody pairs retirement with cap

The paper surveys 14 published agentic-skill systems (Hermes, Voyager, Generative Agents, RestGPT, several proprietary platforms). **None of them implement both retirement and an active cap simultaneously.**

- Most have neither (Voyager, RestGPT) — library grows unbounded.
- A few have retirement but no cap (Generative Agents) — old entries decay, new ones flood in.
- One has a cap but no retirement (a proprietary product, name redacted in the paper) — the library hits its cap, then refuses new skills, going stale.
- **Zero** have both.

The implication: the field knows about these failure modes individually but hasn't combined the fixes. The paper's headline regression (+0.0pp) holds against every system in the survey.

**Our position**: v3 doesn't implement either retirement or cap automatically. The PR-review human gate is doing the work of both — a human decides whether to merge a skill addition (cap) or accept a deletion-PR (retirement). This is slower than automation but uses the one external invariant we know works.

## Direct implications for our SKILL.md eval loop

Mapping the paper's findings onto [`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md):

| paper finding | v3 mechanism |
|---|---|
| Self-rewarded bad edits regress to baseline | Eval set is external; proposer cannot also be evaluator |
| Verbose-hedging drift | Rubric explicitly scores terseness; cost penalty in scoring formula |
| Loss of orthogonality | Embedding-similarity check between proposed skill and existing siblings (see [a-mem.md](a-mem.md)) |
| Outcome-driven retirement | Phase 2: surface skills with declining scores to maintainer for deletion PR |
| Bounded active cap | PR review is the gate; new-skill PRs must justify the addition |
| Meta-skill priority | Edits to `skills/wisdom/` re-validate every dependent skill |

Each row is a direct mapping. None are speculative.

## Methodological caveats

The paper's experimental setup has limits we should acknowledge:

- **SkillsBench is small** (~200 tasks per condition). The +16.2pp / +0.0pp gap is statistically significant in their framing but a follow-up paper could see different magnitudes.
- **The "LLM-authored" arm used GPT-4-class models** circa late 2025. A frontier model in 2026 might do better at self-curation in isolation. The structural argument (no external evaluator → no calibration) still holds, but the numerical gap may shrink.
- **The base agent matters**. If the agent's own zero-shot capability is high, skills matter less; if it's low, skills matter more. Our agents are mid-range; we expect skills to matter materially.

These caveats reduce the precision of the +0.0pp number, not the directional conclusion. The conclusion — "external evaluator + human gate beats self-curation" — is robust across reasonable parameter variations.

## What we adopt from this paper

In order of importance:

1. **An eval set is mandatory.** No mutation without measurement. This is Stage 1 in our spec and the prerequisite for everything else.
2. **The evaluator must be separate from the proposer.** Different prompts at minimum; different models is better. Even if both are the same model, the framing must be "judge against a rubric and an outcome", not "did I improve this?".
3. **The human reviewer is the gate.** PR review, no auto-merge. Settings-level enforcement of `gh pr merge` deny is the floor.
4. **Score every edit against a baseline.** A candidate must beat the current SKILL.md by ≥0.03 to be PR-worthy. Tied or marginal edits stay in the candidate pool until a clearer winner emerges.

## What we explicitly do NOT do

- We do **not** trust LLM-self-assessment of "did this edit improve things?" — it's the documented failure mode.
- We do **not** allow runtime mutation of `~/.claude/skills/`. Edits land in this repo via PR; the install path syncs.
- We do **not** allow auto-merge of skill PRs, ever. The settings-recommended.json `gh pr merge*` deny rule enforces this.

## Open question: orthogonality threshold

A-MEM (see [a-mem.md](a-mem.md)) suggests cosine similarity > 0.85 as a "too similar" threshold for memory dedup. For skills, the right threshold is probably tighter (0.70-0.80) because skills are short and topical overlap is high even between distinct skills. We need to calibrate empirically once the eval loop is running.

The library-drift paper doesn't prescribe a specific threshold — only "measure and enforce one". The threshold is a hyperparameter to tune.

## See also

- [`research/anthropic-skills.md`](anthropic-skills.md) — Anthropic's own SKILL.md guidance and where it conflicts with our `wisdom` skill (the meta-skill in this paper's terminology).
- [`research/anti-patterns.md`](anti-patterns.md) — documented horror stories that empirically confirm the +0.0pp result.
- [`research/competing-systems.md`](competing-systems.md) — how each of the surveyed systems implements (or fails to implement) the three-part recipe.
