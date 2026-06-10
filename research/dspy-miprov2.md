# DSPy MIPROv2 — offline batch compilation, the model we're adopting

DSPy's optimizer suite formalizes "improving a program made of prompts" as a batch compilation problem with explicit eval sets. MIPROv2 (Multi-prompt Instruction PROposer v2) is the workhorse.

## Sources

- [DSPy optimizers overview](https://dspy.ai/learn/optimization/optimizers/)
- [MIPROv2 reference](https://dspy.ai/api/optimizers/MIPROv2/)
- [Sample-efficient LM-program optimization, arXiv 2406.11695](https://arxiv.org/abs/2406.11695)

## How MIPROv2 works

1. **Bootstrap traces**: run the program on a small training set, record successful traces.
2. **Propose**: an LLM proposer reads the traces + task description and proposes alternative prompt instructions.
3. **Evaluate**: each candidate is scored on a held-out validation set using a user-supplied metric.
4. **Search**: Bayesian optimization picks the candidate combination that maximizes validation score.
5. **Output**: the best instructions get baked into the program. No online mutation.

## Why this matches our problem

Our "program" is the bundled skill library:
- `skills/<name>/SKILL.md` ≈ DSPy instruction prompts
- `CLAUDE.md` ≈ a top-level instruction prompt
- The "metric" is a scored outcome from replaying real tasks

We don't need MIPROv2's full Bayesian search. The single-candidate version (propose one edit, score it, accept/reject) covers our case.

## What we adopt

- **Eval set is mandatory**. No mutation without a measurement.
- **Validation-set scoring**, not LLM-self-grading.
- **Offline + batch**: never during a live user turn.
- **Multiple proposals per change**: propose 3-5 variants of the edit, pick the best by score, present that to the human.

## What we leave out

- Bayesian optimization over the whole library. Too heavy. We process one SKILL.md at a time.
- DSPy's runtime (Pydantic signatures, etc.). We're writing markdown, not Python programs.

## Practical translation

```
make refine-skill SKILL=commit
  → load skills/commit/SKILL.md
  → run proposer: "here is the skill, here are eval-set tasks where it was used; propose 3 edits"
  → for each proposal: apply, replay eval-set tasks, score, revert
  → write candidates/commit-<timestamp>/{patch.diff, scores.json, rationale.md}
  → user opens PR or rejects
```

The hard part is the eval set, not the proposer. See [eval-sets.md](eval-sets.md).
