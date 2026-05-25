# Skill Auto-Improvement: v3 — Bundle Eval Loop

## TL;DR

Forget cloning Hermes. The right model is **DSPy MIPROv2 applied to our bundled skill library**: an offline eval loop that proposes edits to `skills/*/SKILL.md` in this repo, scores each against a held-out task set, and lands accepted edits as PRs. No runtime mutation of `~/.claude/skills/`. No per-turn hooks. No self-rated confidence.

The library-drift paper measured a +0.0pp lift for LLM-authored skill libraries vs +16.2pp for human-curated. We don't get to skip the human-in-the-loop. The loop's job is to **propose**, **measure**, and **surface**; the human approves the merge.

See `research/` for the literature this design rests on.

## Why this instead of v1/v2

v1 (clone Hermes via `Stop` hook + `claude -p`) was wrong on several counts: per-turn trigger is a documented anti-pattern, the conversation snapshot we'd send is incomplete, the `--bare` flag we'd need is uncertain, the recursion guard would leak. Spec v2 partially addressed this but kept "auto-edit live skills" as the action. The Library Drift paper and BSWEN's Hermes critique both point at the same finding: **any system that lets an LLM commit edits to its own skill library without an external evaluator regresses to the baseline**.

## Architecture

```
┌──────────────────────┐   ┌─────────────────────┐   ┌──────────────────────┐
│ evals/               │   │ proposer            │   │ candidates/          │
│ Hand-curated +       │──→│ LLM suggests        │──→│ patch.diff           │
│ mined task examples  │   │ edits to one        │   │ rationale.md         │
│ Schema in research/  │   │ SKILL.md            │   │ scores.json          │
└──────────────────────┘   └─────────────────────┘   │ cost.txt             │
                                  ▲                  └──────────────────────┘
                                  │                            │
                                  │                            ▼
                                  │                  ┌──────────────────────┐
                                  │                  │ evaluator            │
                                  │                  │ Replay eval set      │
                                  │                  │ against the patched  │
                                  └──────────────────│ skill; score 0-1     │
                                                     └──────────────────────┘
                                                              │
                                                              ▼
                                                     ┌──────────────────────┐
                                                     │ PR review            │
                                                     │ Human approves       │
                                                     │ Merge → ships in     │
                                                     │ next release         │
                                                     └──────────────────────┘
```

## Stage 1: eval set (mandatory prerequisite)

Without an eval set, the rest is theater. Build this first.

- Location: `evals/<skill>/<id>.json`
- Schema: see [research/eval-sets.md](../research/eval-sets.md)
- Initial size: 30 hand-curated examples across `commit`, `py`, `ts`, `tsx`, `rs`, `release`, `ship`, `wisdom`
- Sources: real session transcripts (60%), synthetic from skill rules (30%), failure cases from `.diary/` and bug commits (10%)
- Scoring: outcome (0.5) + rubric (0.3) + cost (0.2)

Add `evals/README.md` documenting the schema, contamination tradeoff, and how to add an example.

## Stage 2: proposer

A standalone command. Run as:

```
make refine-skill SKILL=commit [N=3]
```

Behavior:
1. Read `skills/commit/SKILL.md`.
2. Read 5-10 randomly-sampled `evals/commit/*.json` examples for context.
3. Spawn `claude -p` with prompt: "Here is a skill; here are tasks where this skill is consulted. Propose N edits that would improve agent performance on similar tasks. Each edit is a unified diff against the SKILL.md."
4. Restrict tools to `Read, Glob, Grep`. No Write — proposer outputs diffs only, doesn't apply them.
5. Save each proposal to `candidates/<timestamp>-commit-<idx>/patch.diff` + `rationale.md`.

Hard limits:
- `--max-cost $0.50` per run
- `--max-iterations 50` (proposer can't loop)
- N defaults to 3

## Stage 3: evaluator

For each candidate:

1. Copy `skills/commit/SKILL.md` to a temp file, apply `patch.diff`, validate it parses (frontmatter intact, body non-empty).
2. For each eval example in `evals/commit/`:
   - Run the task with the patched skill loaded.
   - Score outcome (binary: did it succeed?) and rubric (LLM judge, rubric specific to the skill).
3. Aggregate: `score = mean(outcome) * 0.5 + mean(rubric) * 0.3 + cost_penalty * 0.2`
4. Write `scores.json` with per-example breakdown.

Baseline score = current SKILL.md run on same eval set. Candidate must beat baseline by ≥0.03 to be PR-worthy.

## Stage 4: PR + human review

For candidates that beat baseline:

1. Open a branch `refine/skill-<name>-<timestamp>`.
2. Apply `patch.diff` to the real `skills/<name>/SKILL.md`.
3. Commit with `[skill] refine <name>: <rationale headline>` and PR body = `rationale.md` + score delta table.
4. `gh pr create` — but DO NOT auto-merge (settings already block `gh pr merge`).
5. Human reviews diff, approves or rejects.

No auto-merge, ever. The settings-recommended.json `gh pr merge*` deny rule enforces this at the harness level.

## What we do NOT build

- No `Stop` hook spawning anything.
- No `claude -p` child running with hook recursion guards.
- No live mutation of `~/.claude/skills/`.
- No self-attested "this edit is good" — always validated against eval set.

## File layout

| path | purpose |
|---|---|
| `evals/<skill>/<id>.json` | eval examples |
| `evals/README.md` | schema, contamination notes |
| `tools/refine-skill.py` | proposer driver |
| `tools/eval-skill.py` | evaluator driver |
| `candidates/` (gitignored) | proposal artifacts |
| `Makefile` (extend) | `make refine-skill SKILL=<name>`, `make eval-skill SKILL=<name>` |
| `research/*.md` | source literature this design rests on |

## Open questions

1. **Eval-set contamination**. The agent reads this repo; if eval examples are in-tree, the agent learns to game them. Phase 1 accepts this; Phase 2 needs a held-out private set.
2. **Skill versioning**. Should SKILL.md carry a `version: N` frontmatter? Git history covers it, but `version` makes rollback explicit in tooling.
3. **Multi-skill edits**. A single change might affect two sibling skills (e.g., `/py` and `/testing`). Phase 1: one skill at a time. Phase 2: cross-skill candidates with joint scoring.
4. **Anthropic format conflict**. Their guidance is "explain why" > "ALWAYS/NEVER caps"; our wisdom skill says the opposite. The eval loop should run A/B between formats and let scores decide. See [research/anthropic-skills.md](../research/anthropic-skills.md).

## Sign-off needed before implementing

- [ ] Build the eval set first (5 examples per priority skill, 30 total) — Stage 1
- [ ] Implement `tools/eval-skill.py` (replay harness) — Stage 3, smallest first
- [ ] Implement `tools/refine-skill.py` (proposer) — Stage 2
- [ ] Wire `make refine-skill` / `make eval-skill`
- [ ] PR-creation script (no auto-merge)

Stages 1 and 3 are the load-bearing pieces. Stage 2 is mechanical once those exist. Stage 4 is `gh pr create` + a template.

## References

All sources are in `research/`. The decisive ones:
- [Library Drift, arXiv 2605.19576](https://arxiv.org/abs/2605.19576) — the +0.0pp vs +16.2pp finding
- [DSPy MIPROv2](https://dspy.ai/learn/optimization/optimizers/) — the model we're adapting
- [Hermes Curator docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator) — what NOT to copy (live edit, self-rated confidence)
- [BSWEN's Hermes critique](https://docs.bswen.com/blog/2026-04-07-hermes-ai-overwrites-skills/) — documented failure mode
