# Library Drift — LLM-authored skills regress vs human-curated

The single most important number in this corpus.

## Source

- [Library Drift in LLM Agents, arXiv 2605.19576](https://arxiv.org/abs/2605.19576)

## Headline

On a held-out coding-task benchmark:

- **Human-curated skill library**: +16.2 percentage points over baseline
- **LLM-authored skill library (no human curation)**: +0.0 percentage points
- Both started from the same baseline agent on the same tasks.

In other words, letting the agent maintain its own skill library is empirically equivalent to having no skill library at all.

## Why

The paper attributes the drift to:

1. **Drift toward verbose, hedging skill text**. LLMs add caveats and edge-case handling that dilute the rule.
2. **Loss of orthogonality**. New skills overlap existing ones; the agent picks the wrong one or both.
3. **Self-rewarded bad edits**. The agent's own review confirms the edit was useful even when it wasn't.

## What it tells us

- **Quarantine + human approval are not optional**. Any system that lets an LLM commit edits to its own skill library without an external check will, in expectation, not improve outcomes.
- **Eval set is the missing piece**. The human curator's job was implicitly running a small eval — reading the skill, simulating the task, rejecting the edit if it made the agent worse. Replicate that with a scored eval set.
- **Orthogonality matters**. Edits that create overlap with existing skills are net-negative even if locally "improving".

## How we use it in our design

The bundle eval loop (`specs/2-hermes-skill-autoimprove.md`) needs:

1. An **eval set** of representative tasks (≥30 examples to start).
2. A **proposer** LLM that suggests edits to `skills/*/SKILL.md`.
3. An **evaluator** that replays each candidate against the eval set and scores.
4. **Orthogonality check**: reject candidates that increase overlap with sibling skills (measured by embedding similarity of skill descriptions / when_to_use).
5. **PR review** as the human gate.

Without (1) and (3), we're rebuilding the failure mode the paper measured.
