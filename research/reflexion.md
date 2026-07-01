# Reflexion — verbal self-criticism, with caveats

Reflexion shows that agents can improve across episodes by **reflecting on past failures and writing those reflections to a memory buffer**. The catch: the *granularity* of reflection matters a lot.

## Sources

- [Reflexion: Language Agents with Verbal Reinforcement Learning, arXiv 2303.11366](https://arxiv.org/abs/2303.11366)
- [HuggingFace blog: Reflection in LLM agents](https://huggingface.co/blog/Kseniase/reflection)
- [Self-Refine, arXiv 2303.17651](https://arxiv.org/abs/2303.17651) — sibling work, intra-task refinement

## What works

Reflection at the **episode boundary** (after a task finishes, before the next one starts):

- Agent sees the task, its own trace, the failure mode.
- Writes a short reflection to an episodic memory buffer.
- On the next attempt, the buffer is prepended to the prompt.
- Performance compounds across episodes.

## What doesn't work

Reflection **inside a single turn**:

- Repetitive ("I should reconsider…") with no new information.
- Sycophantic ("My approach was correct, but…") leading to no change.
- Adds tokens without changing behavior.

The HuggingFace blog summarizes this as: per-turn reflection is "thinking out loud" that the LLM has already done in chain-of-thought — adding an explicit reflection step doesn't recover signal.

## Why this matters for us

Our v1 spec used `Stop` (per-turn) as the trigger. That's the documented anti-pattern. The right granularity is:

- **End of session** (`SessionEnd` hook), OR
- **Idle ≥ N minutes** (a session that hasn't been touched is functionally over)
- NOT per-turn

This aligns with Hermes's actual design (idle-triggered, not per-turn).

## What we adopt

- **Reflection writes are structured**: in Reflexion, the reflection is appended to a buffer with a clear schema. Our equivalent: the queue file `~/.claude/skill-review/queue/<date>.jsonl`, one JSON entry per session-end event.
- **Reflection is read, not re-derived**: the next turn doesn't re-reflect; it consumes prior reflections. For us: the proposer reads the queue + transcripts; it doesn't re-analyze the same session twice.

## What we don't take

- The full RL framing (Reflexion treats reflections as policy gradients via prompts). Overkill for skill curation.
- Mandatory reflection on every episode. Most of our sessions won't yield a useful reflection — the eval-loop filter handles that.
