# Bootstrapping an eval set from session transcripts

The eval set is the single hardest piece. Everything else (proposer, evaluator, gating) is mechanical once you have one. This note collects sources and a concrete plan.

## Sources

- [DSPy on eval-set construction](https://dspy.ai/learn/evaluation/) — task type / metric mappings
- [HELM](https://crfm.stanford.edu/helm/) — eval-design conventions: held-out sets, contamination guards, multi-metric
- [SWE-bench](https://www.swebench.com/) — task format that matches our domain (real codebases, real bugs)
- [DSPy MIPROv2 paper](https://arxiv.org/abs/2406.11695) §4 — eval-set size needed for stable optimization

## What an eval example looks like for us

Each example targets a specific skill. Minimal schema:

```json
{
  "skill": "commit",
  "input": {
    "cwd": "/some/repo",
    "git_status": "<output of `git status --porcelain`>",
    "git_diff": "<output of `git diff --stat`>",
    "user_prompt": "commit this"
  },
  "expected_behavior": [
    "produces commit message with [section] prefix",
    "subject ≤ 72 chars",
    "does not use --amend, -A, --no-verify"
  ],
  "scoring": {
    "method": "rubric",
    "weights": {"format": 0.4, "scope": 0.3, "safety": 0.3}
  }
}
```

For our eval set: ~30 examples covering the heavily-used skills (`commit`, `py`, `ts`, `tsx`, `rs`, `release`, `ship`, `wisdom`). Heavier coverage on `commit` because it has the most behavioral rules.

## Where the examples come from

Three sources, in order of fidelity:

1. **Mined session transcripts**. Walk `~/.claude/projects/<slug>/*.jsonl` files. Find turns where a skill was invoked and the resulting action was successful (commit landed, file edited, tests passed). Each successful turn is a candidate example — distill its input + expected behavior into the schema.

2. **Synthetic from skill rules**. Each rule in a SKILL.md implies a test case: "NEVER squash commits" → input is a commit task with a squash hint; expected behavior is "refuses to squash, explains why". Mechanical. Coverage gap: only catches rules already in the skill, can't propose new ones.

3. **Failure-case archives**. The `.diary/` directory and bug commits surface places where the agent did the wrong thing. Each is a high-value example because it pins behavior the current skill didn't prevent.

Best mix: 60% mined real sessions, 30% synthetic, 10% failure-case. The real sessions ground the eval in actual usage; synthetic gives mechanical coverage; failures pin known regressions.

## Scoring metric

Three signals composed:

| signal | source | weight |
|---|---|---|
| Outcome | did the task complete? (commit landed, tests pass, etc.) | 0.5 |
| Rubric | LLM judge with skill-specific rubric | 0.3 |
| Cost | tokens used, normalized | 0.2 (penalty if high) |

The outcome signal is the most expensive (requires running the agent in a sandbox) but also the most trustworthy. Phase 1 can run only outcome + rubric, skip cost.

## Size guidance

- **Phase 1**: 30 hand-curated examples. Enough to detect obvious regressions.
- **Phase 2**: 100+, mined automatically with manual sampling for QA.
- **Phase 3**: continuous expansion from session transcripts. The eval set grows as the agent is used.

DSPy's experience is that >50 examples gives stable optimization signal. Below that, individual example noise dominates.

## Contamination

The eval set lives in this repo. The agent has read access to this repo. The eval set CAN appear in the agent's context during a task → it learns to game the eval.

Mitigations:
- Hold ~20% of examples back as a **secret** eval set committed but gitignored from the agent's view (e.g., in `.eval-private/` with a path-deny in the skill).
- Or: examples are gitignored entirely and live on the maintainer's machine. Reproducible builds suffer.
- Or: rotate the held-out set on each release.

We probably accept some contamination in Phase 1 and address it when the eval set matures.

## Action items

1. Add `evals/` directory with the JSON schema above.
2. Write 5 hand-curated `commit` examples to seed the format.
3. Build a simple replay harness: `python evals/replay.py --skill commit --candidate skills/commit/SKILL.md` → score 0-1.
4. CI runs replay on every PR that touches `skills/`.
5. Document contamination tradeoff explicitly in `evals/README.md`.
