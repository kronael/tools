# Multi-agent failure modes — what blows up at scale

A widely-shared writeup of a $47k overrun in a multi-agent system. The technical details are about a specific product, but the failure modes are general and apply to any "agents that modify their own configuration" architecture.

## Source

- [AI Agents Horror Stories: $47,000 multi-agent failure (TechStartups, Nov 2025)](https://techstartups.com/2025/11/14/ai-agents-horror-stories-how-a-47000-failure-exposed-the-hype-and-hidden-risks-of-multi-agent-systems/)

## The pattern that failed

Deployed without any of:

1. **Memory bounded by size**. Agents accumulated context indefinitely.
2. **Observability into agent state**. Operators couldn't see what each agent was doing in real time.
3. **Governance / approval gates**. Agents made changes (including spending changes) without human checkpoints.
4. **Stop conditions**. No "exit if X" rules; agents would loop until manually killed.
5. **Cost ceilings**. No per-task or per-day spend cap.

The loop that ran up the bill: agent A asked agent B to refine a plan; agent B asked agent C; C answered with a longer plan; A re-asked B with the longer plan; repeat for hours.

## Translation to our context

We're not building a multi-agent product, but the bundle eval loop introduces some of the same risk surfaces:

| risk | mitigation |
|---|---|
| Memory bounded | Eval set is fixed-size. Queue file rotates by date. Don't accumulate transcripts forever. |
| Observability | Every proposal writes `rationale.md` + `provenance.json`. Logs go to `.skill-review/log/`. |
| Approval gate | Mandatory PR review before merge. No auto-merge under any condition. |
| Stop conditions | Each proposer/evaluator run has `--max-cost <usd>` and `--max-iterations <n>`. |
| Cost ceiling | Eval-loop run has a per-run budget. CI fails if exceeded. |

## Things to bake in from day one

- **Hard cost cap per eval-loop run**. Suggest $1 initial; the evaluator caps tokens accordingly.
- **Visible cost log**. Each candidate dir has `cost.txt` with the spend on its generation + evaluation.
- **Refuse to run if previous run was unbounded**. The cost ledger persists; if a prior run didn't report a final cost, the next run refuses to start until manually cleared.
- **Read-only by default**. Eval loop runs in a "dry-run" mode that writes candidate dirs but never edits live skills. Live edit requires `--apply` AND a PR target.

## The deeper lesson

The horror story isn't "AI is dangerous". It's: any system that mutates its own behavior in a feedback loop needs an external invariant the loop can't touch. For our eval loop, that invariant is: **the merge of a skill change to the main branch requires a human reviewer**. Until that gate, candidates are inert.
