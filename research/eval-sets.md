# Eval-set construction — schema, sources, contamination

The eval set is the single hardest piece of [`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md). Everything else (proposer, evaluator, gating) is mechanical once you have one. Without it, [Library Drift](library-drift.md) shows the loop regresses to baseline.

## Sources

- [DSPy on eval-set construction](https://dspy.ai/learn/evaluation/) — task type / metric mappings
- [HELM](https://crfm.stanford.edu/helm/) — eval-design conventions: held-out sets, contamination guards, multi-metric
- [SWE-bench](https://www.swebench.com/) — task format that matches our domain (real codebases, real bugs)
- [DSPy MIPROv2 paper](https://arxiv.org/abs/2406.11695) §4 — eval-set size needed for stable optimization
- [Library Drift, arXiv 2605.19576](https://arxiv.org/abs/2605.19576) — what the eval set is *for*: external invariant the agent can't game

## Required schema for `evals/<skill>/<id>.json`

```json
{
  "id": "01",
  "skill": "<skill-name>",
  "task": "<one-line natural-language description of what the user is asking for>",
  "context": {
    "cwd": "<repo path snippet>",
    "git_status": "<output of git status --porcelain>",
    "git_diff": "<truncated git diff, or null>",
    "files_changed": ["<path>", "..."],
    "prior_turns": "<optional: last 1-2 user/assistant turns for context>"
  },
  "expected_outcome": {
    "must_use_format": "<format constraint, e.g. '[section] Message'>",
    "subject_max_chars": 72,
    "must_not_include": ["<banned string>", "..."],
    "should_mention": ["<topic the response should cover>"]
  },
  "rubric": [
    {"criterion": "<what to check>", "weight": 0.3},
    {"criterion": "<...>", "weight": 0.2}
  ],
  "source": "<one of: real-session, synthetic, failure-case>",
  "provenance": "<optional: session hash or .diary entry it came from>"
}
```

Field-by-field:

- **`id`** — zero-padded string, unique within a skill (`01`, `02`, ...). Two-digit is enough for the foreseeable expansion. Sort key in the directory.
- **`skill`** — slug matching `skills/<skill>/SKILL.md`. The harness uses this to pick which SKILL.md to load for the run.
- **`task`** — single sentence, natural-language, what the user just said. Should read like a real user message.
- **`context`** — everything the agent would normally see at the moment the skill triggers. Git state for git-related skills; file contents for code skills; prior turns for skills that depend on conversation history.
- **`expected_outcome`** — hard constraints the agent's output MUST meet. Binary success: did it meet all of them?
- **`rubric`** — soft criteria scored 0-1 each, weighted, combined into a rubric score. LLM-judge does the scoring.
- **`source`** — provenance class. Used to balance the set (60/30/10 — see below).
- **`provenance`** — exact origin for debugging. A session hash, a diary entry, or "hand-crafted-YYYY-MM-DD".

## Scoring formula

The composite score per example is a weighted sum of three signals:

| signal | source | weight | range |
|---|---|---|---|
| **Outcome** | binary: did all `expected_outcome` constraints pass? | 0.5 | 0 or 1 |
| **Rubric** | LLM judge scores each rubric criterion 0-1; weighted average | 0.3 | 0 to 1 |
| **Cost penalty** | tokens used, normalized against a budget | 0.2 | 0 to 1 (1 = under budget) |

```
example_score = outcome * 0.5 + rubric_score * 0.3 + cost_score * 0.2
candidate_score = mean(example_score for example in eval_set)
```

The 0.5 weight on outcome is deliberate: it's the most trustworthy signal (mechanical check, no LLM in the loop) and should dominate. The rubric handles things mechanical checks can't (e.g., "the body explains why, not what"). The cost penalty discourages verbose skill drift — the [Library Drift](library-drift.md) failure mode where edits accumulate hedging clauses.

### Outcome scoring details

Each `expected_outcome` field is a mechanical check:

- `must_use_format` — regex match on the response.
- `subject_max_chars` — first line length.
- `must_not_include` — substring scan; ANY match fails the example.
- `should_mention` — substring scan; ALL must match. Lenient: case-insensitive, substring not exact-token.

Outcome is **binary**. Either every constraint passes (1) or any one fails (0). No partial credit at the outcome layer; partial credit lives in the rubric.

### Rubric scoring details

The LLM judge receives:

- The skill's current SKILL.md (or the patched version under evaluation).
- The eval example (task, context, expected_outcome, rubric).
- The agent's actual response.

For each rubric criterion, the judge returns 0-1 plus a one-sentence justification. The composite rubric score is the weighted average.

Judge instructions are constant across runs to avoid prompt drift. They are versioned in `tools/judge-prompts/<skill>.md`.

### Cost-penalty details

The agent's run consumes tokens (input + output). Normalize against a per-skill budget:

```
cost_score = max(0, 1 - (tokens_used / budget))
```

Default budget is `2000` tokens per example. Skills like `commit` are typically well under; skills like `ship` may consume more. Tune the budget per skill once we have baseline numbers.

## Source mix: 60% real / 30% synthetic / 10% failure

Three sources of examples, in priority order:

### 60% — real session transcripts

Walk `~/.claude/projects/<slug>/*.jsonl`. Find turns where:

1. A skill was invoked (`/commit`, `/py`, etc.) or was implicitly triggered (a hook redirect, a `when_to_use` keyword match).
2. The resulting action was successful (commit landed, file edited, tests passed).
3. The pre-turn state is recoverable (git state, files, prior turns).

Each such turn is a candidate example. Distill into the schema above, **paraphrasing the user prompt and editing the context** so we don't ship verbatim private data.

These ground the eval set in actual usage. Without them, we're testing a hypothetical agent.

### 30% — synthetic from skill rules

Each rule in a SKILL.md implies a test case:

- "NEVER squash commits" → input is a commit task with a squash hint; expected behavior is "refuses to squash, explains why".
- "ALWAYS pair NEVER with ALWAYS" (from wisdom skill) → input is a skill-editing task; expected behavior is the edit follows the pairing rule.

Mechanical. Coverage gap: only catches rules already in the skill, can't propose new ones. But gives us guaranteed coverage of every rule currently shipped.

Generate with a small script that walks each SKILL.md, extracts ALWAYS/NEVER lines, and templates them into example contexts. Then a human reviews the generated examples for plausibility.

### 10% — failure cases

The `.diary/` directory and bug commits surface places where the agent did the wrong thing. Each is a high-value example because it pins behavior the current skill **didn't** prevent.

- Search `.diary/*.md` for "fix:", "bug:", "regressed", "should have"
- Search git log for commits with `[fix]` or `[refined]` prefix referencing a skill
- For each, reconstruct the pre-failure state and define expected_outcome as the correct behavior the agent should have produced

These are the hardest examples and the most valuable. Each represents a real regression.

## Size guidance

| phase | size | purpose |
|---|---|---|
| **Phase 1** | 30 hand-curated examples, ~5 per priority skill | Detect obvious regressions. Smoke-test the harness. |
| **Phase 2** | 100+ examples, semi-automated mining + manual QA | Stable optimization signal. DSPy's empirical threshold for low-noise gradients. |
| **Phase 3** | Continuous expansion from session transcripts | Eval set grows as the agent is used; rotate older examples. |

DSPy's experience ([arXiv 2406.11695](https://arxiv.org/abs/2406.11695) §4): >50 examples gives stable optimization signal. Below that, individual example noise dominates. Phase 1's 30 is **below** that threshold deliberately — Phase 1 is for proving the loop works, not for production optimization.

The current `evals/commit/` directory ships 5 examples (Phase 1 seed). Add 5 more per skill as we expand: `py`, `ts`, `tsx`, `rs`, `release`, `ship`, `wisdom`.

## Contamination tradeoff

The eval set lives in this repo. The agent has read access to this repo (via Read/Grep). The eval set **can** appear in the agent's context during a task → it learns to game the eval.

This is the **contamination problem**. HELM and SWE-bench both call it out as the central design challenge of any in-tree eval.

### Mitigations, ranked

1. **Accept it (Phase 1)**. The eval is small, hand-curated, and visible. The agent doesn't have an incentive to game it because the operator isn't running it on every turn — it runs offline, in `make refine-skill`. If the agent reads the eval during a normal session, fine: the eval is "what good behavior looks like", and reading it is no worse than reading the skill. This is the **current position**.

2. **Hold ~20% back as a secret set (Phase 2)**. Commit a `.eval-private/` directory, gitignore the contents, sync via a side channel (Anthropic-internal git remote, or a maintainer's local-only directory). The harness uses the private set for the *gating* decision; the public set is for proposer context only. Slower iteration but recovers the held-out property.

3. **Rotate the held-out set each release (Phase 2.5)**. The held-out set changes monthly; agents can't memorize a moving target. Adds operational overhead.

4. **Fully gitignored eval set on maintainer's machine (Phase 3)**. Reproducible builds suffer; new contributors can't run the eval loop. We don't do this unless contamination is empirically a problem.

**Current position**: Phase 1 accepts contamination explicitly. We measure proposer behavior on the in-tree set; if we see suspicious patterns (proposer-output text quoting eval examples verbatim, candidates that score implausibly well), we move to Phase 2.

The contamination is acceptable in Phase 1 because the loop is **bounded by PR review**. Even if the agent gimmes the eval, the maintainer sees the diff and can reject. The contamination risk grows when (and only when) we move toward auto-merge — which we explicitly never do (see [`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md#what-we-do-not-build)).

## Action items (current state)

1. **Done**: `evals/` directory exists with the JSON schema in this doc.
2. **Done**: 5 hand-curated `commit` examples seed the format (Phase 1 partial).
3. **Pending**: replay harness `tools/eval-skill.py` — Stage 3 of the spec.
4. **Pending**: 5 examples each for `py`, `ts`, `tsx`, `rs`, `release`, `ship`, `wisdom` (Phase 1 complete = 30 total).
5. **Pending**: CI runs replay on every PR that touches `skills/`.
6. **Done**: contamination tradeoff documented (this file, `evals/README.md`).

## Example: a complete eval entry

See [`evals/commit/01.json`](../evals/commit/01.json) for a working example. Shape:

```json
{
  "id": "01",
  "skill": "commit",
  "task": "user just made a small bugfix to handle null username; help them commit it",
  "context": {
    "git_status": " M src/auth/login.py",
    "git_diff": "@@ -42,7 +42,11 @@ def login(username, password):\n+    if username is None:\n+        return error('username required')",
    "files_changed": ["src/auth/login.py"]
  },
  "expected_outcome": {
    "must_use_format": "\\[fix\\] .+",
    "subject_max_chars": 72,
    "must_not_include": ["Co-Authored-By", "--amend", "git add -A", "--no-verify"],
    "should_mention": ["null", "username"]
  },
  "rubric": [
    {"criterion": "Subject under 72 chars including [fix] prefix", "weight": 0.2},
    {"criterion": "[fix] section matches the bugfix nature of the change", "weight": 0.2},
    {"criterion": "Body explains why (null-username crash) not just what", "weight": 0.3},
    {"criterion": "No banned flags (--amend, -A, --no-verify, -a)", "weight": 0.3}
  ],
  "source": "synthetic",
  "provenance": "hand-crafted-2026-05-25"
}
```

## See also

- [`research/library-drift.md`](library-drift.md) — why we need an eval set at all
- [`research/anthropic-skills.md`](anthropic-skills.md) — Anthropic's own guidance recommends running A/B between skill formats; the eval set is how
- [`evals/README.md`](../evals/README.md) — operational guide for adding examples
