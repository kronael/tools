# Competing systems — how others handle self-improving agents

Comparison matrix of agent systems that try to make agents improve themselves over time. Each row maps onto v3's design via the rightmost column.

## Sources

- [Hermes Agent Curator docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator)
- [DSPy MIPROv2 reference](https://dspy.ai/api/optimizers/MIPROv2/) and [paper, arXiv 2406.11695](https://arxiv.org/abs/2406.11695)
- [Reflexion, arXiv 2303.11366](https://arxiv.org/abs/2303.11366)
- [LangGraph human-in-the-loop docs](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [mem0 architecture](https://docs.mem0.ai/core-concepts/memory-architecture)
- [Letta (MemGPT) docs](https://docs.letta.com/concepts/memgpt)
- [A-MEM, arXiv 2502.12110](https://arxiv.org/abs/2502.12110)
- [Voyager, arXiv 2305.16291](https://arxiv.org/abs/2305.16291)
- [AutoGen design docs](https://microsoft.github.io/autogen/)
- [CrewAI tasks/agents docs](https://docs.crewai.com/)
- [Library Drift, arXiv 2605.19576](https://arxiv.org/abs/2605.19576) — the survey across these systems
- See also prior session research at `research/library-drift.md` for the +0.0pp / +16.2pp framing

## Comparison matrix

| system | trigger model | mutation target | drift defense | cost model | anti-patterns |
|---|---|---|---|---|---|
| **Hermes Curator** | Idle ≥2h or weekly cron | Skill files + memory; agent-authored only | Bundled skills read-only; `write_origin` tag | Per-cycle, opaque | Self-rated edits congratulatory ([BSWEN](anti-patterns.md)); no dry-run; #18373 |
| **DSPy MIPROv2** | Offline `compile()` call | Prompt instructions in DSPy programs | Bayesian search over held-out eval set | Bounded by trial count (configurable) | Requires eval set; doesn't address library-level drift |
| **Reflexion** | Episode boundary (post-task) | Episodic memory buffer | None — relies on outcome reward | Per-episode reflection token cost | Per-turn variant repeats sycophancy; degrades with mis-calibrated reward |
| **LangGraph HITL** | At interrupt nodes in a graph | Whatever the human approves; arbitrary state | Human approval is the defense | Interactive; human time is the cost | None inherent — but graph designer can omit interrupts and lose safety |
| **mem0** | Per-message ingest | Memory store (vector + graph) | Dedup via similarity; user-scoped namespaces | Hosted SaaS; pay per ingest+query | "Memory bloat" without TTL; cross-user leakage if scopes misconfigured |
| **Letta / MemGPT** | Agent-driven page-fault into context | Long-term memory blocks | LLM-controlled paging; relies on agent's judgment | Compute per memory operation | Agent paging logic itself drifts; no eval; memory-of-memory recursion |
| **A-MEM** | Per-write embedding similarity | Memory notes with emergent links | Hub-detection, dedup via cosine sim | Per-write embedding cost (cheap) | None major; designed conservatively; lacks eval-set framing |
| **Voyager** | Episode boundary in Minecraft env | Skill library (executable code) | Iterative env feedback (Minecraft runs the test) | Per-episode env interaction | Library grows unbounded; no retirement |
| **AutoGen** | Multi-agent conversation rounds | Agent prompts at runtime | None — agents self-correct via debate | Per-round; can spiral ([$47k example](anti-patterns.md)) | Loops without stop conditions; no cost ceiling |
| **CrewAI** | Per-task in a crew workflow | Task instructions; sometimes agent definitions | None inherent; framework provides hooks | Per-task; configurable | Tasks can re-spawn each other; debugging opacity |
| **v3 (this repo)** | Manual: `make refine-skill` | `skills/*/SKILL.md` in source tree | **External eval set + PR review** | `--max-cost` + `--max-iterations` per run | Designed to avoid all of the above |

## Row-by-row commentary

### Hermes Agent (Curator)

The most direct comparator. Hermes proposes skill edits during idle windows, writes them to the agent's skill store, and tags them `write_origin="background_review"`. **What we should not copy**:

- Live mutation of the skill store. No external evaluator; relies on agent self-assessment.
- The "agent almost always thinks it performed well" failure mode is documented ([BSWEN, April 2026](anti-patterns.md)).
- No dry-run mode at time of writing (Hermes issue #18373).

What we keep: the idle-trigger framing (better than per-turn) and the bundled-skills-read-only guardrail. Adapted to our world: our bundled skills are this repo; edits land via PR.

### DSPy MIPROv2

The closest formal analog to v3. MIPROv2 is offline batch optimization with an explicit eval-set scoring step. **We are essentially adapting MIPROv2 to markdown skill files** instead of Python DSPy programs.

Differences:

- DSPy uses Bayesian search over candidate combinations. We use single-candidate per skill — simpler, cheaper, sufficient for our scale.
- DSPy operates on prompt instructions inside Python programs. We operate on markdown SKILL.md files. Same idea, different medium.
- DSPy assumes you have an eval set. We have to build one (see [`eval-sets.md`](eval-sets.md)).

This is the row whose mechanics we are most directly inheriting.

### Reflexion

Per-episode self-criticism. **The granularity is the key result**: reflection at the episode boundary (after a task ends) works; reflection inside a turn doesn't. This is what killed v1 of our spec (Stop hook = per-turn).

For v3, Reflexion's pattern shows up indirectly: the `.diary/` entries the user writes are a form of episode-boundary reflection. The eval-loop proposer can mine `.diary/` for failure cases (see [`eval-sets.md`](eval-sets.md#10-failure-cases)).

### LangGraph human-in-the-loop

LangGraph treats human approval as a first-class graph node. The agent runs a workflow; at predefined points it pauses for human input. **The defense is the human, not any internal check**.

This is the model v3 inherits at the merge step: the PR is our `interrupt` node, the human reviewer is the approver. Settings-level `gh pr merge*` deny is the harness enforcing the interrupt — we can't accidentally code around it.

### mem0 and Letta/MemGPT

Both are memory-management systems, not skill systems. Relevant because they share v3's risk surface: a store that grows over time, with the agent doing the writing.

mem0's defense is **namespace scoping** (memories belong to a user) and **dedup via similarity**. Letta's is **LLM-controlled paging** (the agent itself decides what to keep in working memory).

Neither addresses the [library-drift](library-drift.md) finding because both leave evaluation to the agent. Both are mem-system parallels; the skill-system parallel is Hermes, and Hermes has the same flaw.

### A-MEM

The most thoughtful memory architecture in the survey. Atomic notes, embedding-linked, hub-detection. **What v3 borrows**: the orthogonality / dedup mechanic. Proposed skill edits that are semantically very close to an existing skill rule are rejected (see [`a-mem.md`](a-mem.md) for implementation hint).

What v3 doesn't borrow: the runtime memory store. We're operating on ~40 markdown files in a git repo; we don't need a vector DB.

### Voyager

Minecraft-environment skill library. The system genuinely improves over time because **the environment provides a hard outcome signal** (the Minecraft world tells you if your code worked). Voyager doesn't have library drift the way Hermes does because the environment is the evaluator.

v3's eval set is trying to recover this property: the eval set is our "environment". It tells us if a proposed edit makes outcomes better or worse. Without it, we have Hermes; with it, we have something closer to Voyager.

### AutoGen and CrewAI

Multi-agent frameworks. Mentioned for completeness. Both have the cost-spiral failure mode documented in [`anti-patterns.md`](anti-patterns.md). Neither is a direct comparator for skill-curation — they're orchestration frameworks — but they're the systems most associated with "agent failures at scale" in 2025-2026 writeups.

v3 is single-agent (the proposer, the evaluator are separate processes but the architecture isn't an agent crew). The multi-agent failure modes don't apply directly. The cost-ceiling lesson does: `--max-cost $0.50` per proposer run, hard.

## What v3 takes from this matrix

In priority order:

1. **DSPy's eval-set-driven scoring** — the formal model for "propose, measure, accept".
2. **LangGraph's HITL interrupt** — the human-approval gate at merge time.
3. **Reflexion's episode-boundary granularity** — never per-turn; the loop is manual or offline.
4. **A-MEM's dedup + hub mechanics** — orthogonality check on proposed edits.
5. **Hermes's bundled-skills-read-only invariant** — adapted to "edits land via PR, not via runtime".

Combine these and the result is the v3 design. Each component handles a different failure mode of the systems above; the union covers the +0.0pp regression that [Library Drift](library-drift.md) measured.

## What v3 explicitly rejects

- **Self-assessment of edit quality** (Hermes, Reflexion-per-turn, AutoGen rounds)
- **Unbounded library growth** (Voyager, mem0 without TTL, Letta with bad paging)
- **Multi-agent loops without stop conditions** (AutoGen, CrewAI worst-case)
- **Runtime mutation of the skill store** (Hermes, mem0)
- **No external evaluator** (everything except DSPy and Voyager-in-environment)

## See also

- [`research/library-drift.md`](library-drift.md) — the empirical finding that motivates the v3 choices above
- [`research/anti-patterns.md`](anti-patterns.md) — specific horror stories from the AutoGen / Hermes ecosystems
- [`research/hermes-agent.md`](hermes-agent.md) — Hermes deep-dive
- [`research/dspy-miprov2.md`](dspy-miprov2.md) — DSPy MIPROv2 deep-dive
- [`research/reflexion.md`](reflexion.md) — Reflexion deep-dive
- [`research/a-mem.md`](a-mem.md) — A-MEM deep-dive
