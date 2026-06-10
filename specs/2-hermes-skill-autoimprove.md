# Skill Auto-Improvement: v3 — Bundle Eval Loop

## TL;DR

Forget cloning Hermes. The right model is **DSPy MIPROv2 applied to our bundled skill library**, fed by a **lightweight runtime episode collector**: an online hook captures signals (no LLM, no edits), the human triages them into eval examples or skill notes, and an offline eval loop proposes SKILL.md edits scored against the eval set, landing accepted edits as PRs.

The library-drift paper measured a +0.0pp lift for LLM-authored skill libraries vs +16.2pp for human-curated. We don't get to skip the human-in-the-loop. The loop's job is to **observe** (cheap), **propose** (gated), **measure** (mandatory), and **surface**; the human approves the merge and curates the eval set from observed episodes.

See `research/` for the literature this design rests on.

## Why this instead of v1/v2

v1 (clone Hermes via `Stop` hook + `claude -p`) was wrong on several counts: per-turn trigger is a documented anti-pattern, the conversation snapshot we'd send is incomplete, the `--bare` flag we'd need is uncertain, the recursion guard would leak. Spec v2 partially addressed this but kept "auto-edit live skills" as the action. The Library Drift paper and BSWEN's Hermes critique both point at the same finding: **any system that lets an LLM commit edits to its own skill library without an external evaluator regresses to the baseline**.

## Architecture

```
ONLINE (real sessions, every day)                  OFFLINE (deliberate, scheduled)
─────────────────────────────────                  ─────────────────────────────
┌──────────────────────────┐                       ┌──────────────────────┐
│ Stage 0: episode hook    │                       │ Stage 1: eval set    │
│ Stop/PostToolUse hook    │                       │ Hand-curated +       │
│ Detects signals (no LLM):│                       │ promoted episodes    │
│ - user said "no/wrong"   │ episodes/             │ Schema in research/  │
│ - tool error loops       │──┬───────────────────►└──────────┬───────────┘
│ - high-praise utterances │  │                               │
│ Appends episode JSON to  │  │                               ▼
│ episodes/<date>/<sid>... │  │                    ┌──────────────────────┐
└──────────────────────────┘  │                    │ Stage 2: proposer    │
                              │                    │ LLM suggests edits   │
                              │                    │ to one SKILL.md      │
                              │                    └──────────┬───────────┘
                              │                               │
┌──────────────────────────┐  │                               ▼
│ Stage 0.5: triage        │  │                    ┌──────────────────────┐
│ /review-episodes (human) │◄─┘                    │ candidates/          │
│ Classify each episode:   │                       │ patch.diff           │
│  well / bad / neutral    │                       │ rationale.md         │
│  + skill tag + notes     │                       │ scores.json          │
│ Promote bad cases to     │──────────────────────►│ cost.txt             │
│ evals/<skill>/<id>.json  │                       └──────────┬───────────┘
└──────────────────────────┘                                  │
                                                              ▼
                                                     ┌──────────────────────┐
                                                     │ Stage 3: evaluator   │
                                                     │ Replay eval set      │
                                                     │ against patched      │
                                                     │ skill; score 0-1     │
                                                     └──────────┬───────────┘
                                                                │
                                                                ▼
                                                     ┌──────────────────────┐
                                                     │ Stage 4: PR + human  │
                                                     │ Approve, no auto-    │
                                                     │ merge ever           │
                                                     └──────────────────────┘
```

## Stage 0: episode collector (online, deterministic)

Runtime hook that scans the just-finished turn for *signals* and records an
episode if signal is detected. The hook does NO LLM work, mutates NO skills,
and produces only append-only JSONL files.

### What an episode is

An episode is a pointer to a moment worth a human's attention. Not an edit,
not a proposal — just "this turn looks interesting; come back to it later".

```json
{
  "episode_id": "20260525-184523-abc123-001",
  "ts": "2026-05-25T18:45:23Z",
  "session_id": "abc123-...",
  "jsonl_path": "/home/ondra/.claude/projects/-home-ondra-.../abc123.jsonl",
  "cwd": "/home/ondra/wk/foo",
  "trigger": "user_correction",
  "signal": {
    "last_user_text_excerpt": "no don't add comments, the code is self-explanatory",
    "last_assistant_tool_count": 2,
    "tool_errors_in_turn": 0,
    "negation_phrases": ["no", "don't"],
    "praise_phrases": [],
    "loop_signature": null
  },
  "skill_hint": null,         // human fills during triage
  "classification": null,     // human fills: "well" | "bad" | "neutral"
  "notes": "",                // human writes
  "promoted_to": null         // human sets to "evals/<skill>/<id>.json" if used
}
```

### Trigger heuristics (no LLM)

The hook reads the last 5 messages of the session JSONL and applies cheap
string checks. An episode is emitted if ANY trigger fires:

| trigger | detection | severity |
|---|---|---|
| `user_correction` | last user text contains 2+ of: `no`, `don't`, `stop`, `wrong`, `bad`, `actually`, `revert`, `undo` (word-boundary, case-insensitive) | bad-candidate |
| `tool_loop` | same `Bash` command string repeated 2+ times in last 10 tool_use blocks | bad-candidate |
| `tool_error_streak` | 3+ tool_result blocks with `is_error: true` in last 20 entries | bad-candidate |
| `praise` | last user text contains 2+ of: `perfect`, `great`, `exactly`, `nice`, `thanks`, `love it` | well-candidate |
| `periodic` | every 50th Stop event in a session (baseline sampling for neutral cases) | neutral |

Triggers are biased toward bad-cases (those are the high-value signal). All
heuristics are tunable in a constants block at the top of the hook script.

### Sidechain handling

When the Stop hook fires from a subagent (Task tool sidechain), the
`isSidechain:true` flag in the JSONL distinguishes it. The episode records
`sidechain: true` and points to the subagent JSONL, not the parent. Triage
treats subagent episodes as second-class (a problem in a subagent rarely
means the skill needs updating, but worth recording for cluster analysis).

### Storage

```
~/.claude/skill-review/
  episodes/
    20260525/
      abc123-001.json       # one file per episode, append-only
      abc123-002.json
      def456-001.json
  episodes-index.jsonl       # one line per episode for fast listing
```

Atomic write: `tempfile + rename`. No locking needed for write since each
file is per-episode (no concurrent writers on the same file). The index is
append-only with `fcntl.flock` on write.

### Hook implementation

`hooks/episode_observe.py`. Fires on `Stop`. Behavior:

1. Read JSON from stdin (session_id, cwd, hook_event_name, stop_hook_active).
2. Bail if `stop_hook_active` (parent retry path).
3. Open `~/.claude/projects/<slug(cwd)>/<sid>.jsonl`, read last 30 lines (cap on read).
4. Walk entries: collect `last_user_text`, count tool_use blocks, detect loops, count errors.
5. Apply trigger heuristics.
6. If any trigger fires, write episode JSON + append to index.
7. Exit 0 (never blocks).

Target latency: <100ms (file read + regex). No subprocess, no network.

### Triage workflow

User runs `/review-episodes` slash command. Skill file at
`skills/review-episodes/SKILL.md`. The skill is a Claude-driven workflow:

1. List pending episodes (those with `classification == null`) from last N days.
2. For each, show: trigger, signal excerpt, link to JSONL line.
3. Claude (with user supervision) classifies each:
   - **bad**: which skill is at fault? Tag `skill_hint`. Optionally promote to `evals/<skill>/<id>.json`.
   - **well**: which skill worked correctly? Tag for positive eval coverage.
   - **neutral**: dismiss.
4. Updates episode JSON in place with classification + notes.

The triage step is where human judgment enters. Hook is deterministic; human
decides what matters; eval set grows from real signal, not synthetic
guesses.

### Why episodes ≠ proposals

The hook records facts, never opinions:

- No "what the agent should have done" — that's the human's call during triage.
- No skill edits — episodes don't touch `~/.claude/skills/` or `skills/`.
- No LLM in the hook — costs are bounded to 5 file reads per turn.

This is the cheap, safe layer that makes the offline eval loop honest. Without
it, the eval set is synthetic guesses about what users say. With it, the eval
set is grown from real user corrections.

### Recursion safety

Hook runs in main process, fires once per Stop, does not spawn subprocess.
There's no recursion path. (Compare v1's `claude -p` child which had recursion
risk.)

### What this is NOT

- NOT a proposer. Episodes don't have "suggested edits".
- NOT a curator. Episodes don't get promoted automatically.
- NOT a Hermes clone. Hermes runs an LLM in the background; we run regex.

---

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
