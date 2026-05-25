# Anti-patterns — documented horror stories and what v3 does about them

Each section is a real, public failure. For each: root cause + the exact mechanism in v3 that prevents it.

## Sources

- [BSWEN — "Hermes AI overwrites skills", April 2026](https://docs.bswen.com/blog/2026-04-07-hermes-ai-overwrites-skills/)
- [Hermes issue #18373 — open request for dry-run / approval before auto-archival](https://github.com/NousResearch/hermes-agent/issues/18373)
- [Hermes issue #17583 — Curator overwrites with sycophantic confidence](https://github.com/NousResearch/hermes-agent/issues/17583)
- [TechStartups — $47k multi-agent loop, Nov 2025](https://techstartups.com/2025/11/14/ai-agents-horror-stories-how-a-47000-failure-exposed-the-hype-and-hidden-risks-of-multi-agent-systems/)
- [Reflexion, arXiv 2303.11366](https://arxiv.org/abs/2303.11366) — per-turn variant degradation
- [Comet/Perplexity prompt-drift incident writeup, March 2026](https://www.perplexity.ai/blog/comet-prompt-drift-postmortem) — Comet's customer-facing agent drift

## 1. BSWEN: Hermes overwrites customized skills

### What happened

BSWEN deployed Hermes Agent in production. Operators customized several skills (added project-specific rules, refined trigger keywords). After ~2 weeks, the Curator's background-review cycle silently rewrote those skills to a worse state. Customizations gone; performance regressed.

### Root cause

Two compounding factors:

1. **Self-assessment bias** — the Curator's review prompt asks the LLM to evaluate its own edits. The LLM almost always answers "yes, this improvement is good" regardless of actual effect. BSWEN's exact wording: "Agent almost always thinks it performed well, even when it didn't."
2. **No external evaluator** — there's no independent check ("does this edit improve task outcomes?"). The Curator writes whatever it generates.

This is the exact mechanism [Library Drift](library-drift.md) measured: self-evaluated skill edits regress to baseline (or worse, when customizations are overwritten with generic rewrites).

### v3 prevention

- **The evaluator is separate from the proposer.** Different prompt, ideally different model. The proposer produces candidate diffs; the evaluator scores them against the eval set. Self-assessment is structurally impossible.
- **The skill store is git.** Customizations are commits. Even if the proposer suggests overwriting a customization, the diff is visible in the PR, and the maintainer can reject.
- **Human review gate.** Settings-recommended.json blocks `gh pr merge*`. No auto-merge under any condition. See [`specs/2-hermes-skill-autoimprove.md#stage-4-pr--human-review`](../specs/2-hermes-skill-autoimprove.md#stage-4-pr--human-review).

## 2. Hermes issue #18373: no dry-run before auto-archival

### What happened

A user filed an issue with Nous Research: the Curator was archiving skills (marking them inactive) without any visibility into which skills were being archived or why. By the time the user noticed, several useful skills had been moved out of the active set.

### Root cause

Hermes's archival step has no dry-run mode, no approval prompt, no diff preview. The skill goes from "active" to "archived" silently as part of the background-review cycle.

### v3 prevention

- **All proposals are dry-run by default.** A proposer run writes `candidates/<timestamp>-<skill>-<idx>/patch.diff` and stops. Nothing touches `skills/*/SKILL.md` until the maintainer runs `gh pr create` (or accepts via UI).
- **Visible artifacts.** Every candidate has `rationale.md`, `scores.json`, `cost.txt`. The maintainer sees what's proposed, why, what it scored, and what it cost.
- **No silent state changes.** The eval-loop runs are explicit (`make refine-skill SKILL=<name>`); there's no background daemon mutating anything.

## 3. Hermes issue #17583: Curator overwrites with sycophantic confidence

### What happened

The Curator generated a skill update that was *factually wrong* (called a nonexistent function in an example) but the LLM's self-rating said the update was "high confidence, well-tested". The update landed in the skill store. The agent then proceeded to invoke the nonexistent function on subsequent tasks, failing each time.

### Root cause

- **Self-rated confidence is uncalibrated.** The LLM's "high confidence" is uncorrelated with actual correctness. The signal looks useful but isn't.
- **No outcome test.** The Curator never ran the proposed skill against a real task to see if it actually worked.

### v3 prevention

- **Outcome scoring is mechanical, not LLM-judged.** The eval examples have `expected_outcome` constraints (regex matches, banned strings, required mentions) that are checked by code, not by an LLM judge. See [`eval-sets.md#outcome-scoring-details`](eval-sets.md#outcome-scoring-details).
- **The rubric LLM judge is separate from the proposer.** The judge sees the rubric and the actual response; it doesn't see the proposer's self-rationale. Independent assessment.
- **Candidate must beat baseline by ≥0.03.** Marginal or self-rated-good-but-actually-tied candidates don't get a PR.

The factually-wrong-but-confident edit would fail an outcome check (the agent calls a function that doesn't exist → the task doesn't complete → outcome = 0).

## 4. The $47k multi-agent loop (TechStartups, Nov 2025)

### What happened

A startup deployed a multi-agent system (orchestrator + worker agents + planner). The agents could request work from each other. Over a weekend, an agent A asked agent B to refine a plan; B asked C; C answered with a longer plan; A re-asked B with the longer plan; the loop ran for 36 hours and consumed ~$47,000 in API costs.

### Root cause

Several missing guardrails, all in the same family:

1. **No stop condition.** No "exit if X" rule; agents would loop until manually killed.
2. **No cost ceiling.** No per-task or per-day spend cap at the API or orchestrator level.
3. **No observability into agent state.** Operators couldn't see what each agent was doing in real time; the alarm was the bill, three days later.
4. **Self-reinforcing context growth.** Each iteration extended the plan; longer plans triggered more refinement requests; the context grew, the cost per iteration grew, the loop accelerated.

### v3 prevention

- **`--max-cost $0.50` per proposer run.** Hard cap. The Claude SDK's `--max-cost` flag enforces this at the runtime level; if a single `make refine-skill` run is hitting the cap, it terminates.
- **`--max-iterations 50`.** The proposer can't loop indefinitely even within its budget.
- **No multi-agent crew.** v3 is single-process: the proposer is one `claude -p` call, the evaluator is a separate Python script (`tools/eval-skill.py`). No agent-to-agent requests.
- **Visible cost log.** Each candidate dir has `cost.txt`. The maintainer sees aggregate spend per run.
- **Refuse if previous run was unbounded.** The cost ledger persists; if a prior run didn't report a final cost, the next run refuses to start until manually cleared.

These mitigations are listed in [`multi-agent-horror.md`](multi-agent-horror.md). The deeper lesson is in [`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md#stage-2-proposer): bound every loop with both a cost cap and an iteration cap; never trust the agent to stop itself.

## 5. Reflexion's repetitive self-criticism (per-turn variant)

### What happened

The [Reflexion paper](https://arxiv.org/abs/2303.11366) tested reflection at two granularities:

- **Episode boundary**: reflect after a task completes, before the next one starts. Worked well — task success improved across episodes.
- **Per-turn within a single task**: reflect after every action. Failed — reflections became repetitive ("I should reconsider..."), sycophantic ("My approach was correct, but..."), and added tokens without changing behavior.

The HuggingFace blog summary calls per-turn reflection "thinking out loud the LLM has already done in chain-of-thought" — the explicit reflection adds noise, not signal.

### Root cause

LLM self-reflection is high-variance and uncalibrated. Per-turn reflection samples the noise more often without giving the underlying behavior more chances to change. The agent isn't learning between turns within a task; it's just generating more text.

### v3 prevention

This is what killed v1 of our spec (Stop hook = per-turn). v3 inherits the fix:

- **Eval-loop runs are manual.** Triggered by `make refine-skill SKILL=<name>`. Never per-turn, never per-session.
- **Proposer + evaluator are offline.** No "during a live user turn" anything. The eval loop is batch work that produces PRs.
- **Reflexion's good variant (episode-boundary) is what `.diary/` is.** Users write diary entries at session end; the eval set mines them for failure cases. Episode-boundary reflection by humans, not by the agent.

## 6. Comet/Perplexity prompt drift (March 2026)

### What happened

Comet (Perplexity's research agent product) had a system prompt that operators tuned over several months. Operators didn't have version control on the prompt or a regression test set. After a routine "minor edit" to the system prompt, Comet started producing materially worse summaries — but the regression wasn't caught for ~3 weeks because there was no automated comparison. By the time it was noticed, multiple edits had layered on; bisecting was difficult.

### Root cause

- **No version control for the prompt.** Edits weren't atomic; rollback was theoretical.
- **No regression test set.** No way to compare "current prompt" vs "previous prompt" on a fixed task set.
- **Drift was gradual.** Each edit was small; no edit looked alarming in isolation; the cumulative effect was severe.

This is essentially [Library Drift](library-drift.md) for a single prompt instead of a skill library. Same mechanism, different surface area.

### v3 prevention

- **Skills are version-controlled.** Every SKILL.md edit is a git commit. Bisecting is `git bisect`.
- **The eval set is the regression test set.** Every candidate runs against the current eval set; scores are recorded in `scores.json` and visible in the PR.
- **The baseline is explicit.** Each candidate is scored against the current SKILL.md on the same eval set. A candidate that lowers the baseline score gets a "score regression" tag on the PR and is rejected by default.
- **Cost penalty discourages drift.** The 0.2-weight cost penalty in the scoring formula penalizes edits that bloat the skill (cumulative drift toward verbose hedging — the exact failure mode that hit Comet).

Open question (from [`anthropic-skills.md`](anthropic-skills.md#other-anthropic-points-worth-tracking)): should SKILL.md carry an explicit `version: N` frontmatter, beyond what git history gives us? Probably yes once we have a real rollback case. Until then, git suffices.

## Recurring themes across all six

Reading across the six horror stories:

| theme | how it shows up | v3 mitigation |
|---|---|---|
| **Self-assessment is uncalibrated** | BSWEN, Hermes #17583, Reflexion-per-turn | External eval set + separate proposer/evaluator |
| **Silent state changes** | Hermes #18373, Comet drift | All proposals are explicit artifacts (`candidates/`); PRs are the only mutation path |
| **No outcome signal** | BSWEN, Hermes #17583, Comet | Eval examples have mechanical `expected_outcome` checks |
| **Unbounded loops** | $47k incident | `--max-cost` + `--max-iterations` per run |
| **No regression detection** | Comet drift | Baseline score required; candidate must beat by ≥0.03 |
| **Drift is cumulative** | Comet drift, BSWEN | Cost penalty in scoring formula; PR review of each edit; git history for rollback |

Every horror story above reduces to **at least one** of these themes. v3's defenses are designed against the union.

## What's NOT defended against

We should be honest about gaps:

- **Eval-set contamination.** If the proposer reads the eval set during its run, it can produce edits that game the eval. Phase 1 accepts this (see [`eval-sets.md#contamination-tradeoff`](eval-sets.md#contamination-tradeoff)).
- **A coordinated adversary** (e.g., a malicious skill that adds rules to fool the judge). Out of scope; the maintainer is the trust boundary.
- **Bad eval examples.** If the eval set itself is wrong (a test that rewards bad behavior), every candidate will pass for the wrong reasons. Mitigated by hand-curation in Phase 1 and ongoing review.
- **The maintainer rubber-stamping PRs.** If the human reviewer doesn't actually read the diffs, the human gate is theater. The mitigation is the same one Anthropic recommends for any human-in-the-loop system: keep the diffs small enough to review in a few minutes.

These are real limitations. None of them undo the v3 architecture; they're places we'll need to invest if the system gets larger.

## See also

- [`research/library-drift.md`](library-drift.md) — the empirical mechanism behind most of these failures
- [`research/multi-agent-horror.md`](multi-agent-horror.md) — deeper notes on the $47k incident
- [`research/competing-systems.md`](competing-systems.md) — which systems each story implicates
- [`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md) — the design that incorporates these defenses
