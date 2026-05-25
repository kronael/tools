# Evals

Eval examples for the skill auto-improvement loop ([`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md)). One JSON file per example; one subdirectory per skill.

Design and schema rationale: [`research/eval-sets.md`](../research/eval-sets.md). Read that first — this README is the operational guide.

## Layout

```
evals/
├── README.md                # this file
├── commit/                  # examples for skills/commit/SKILL.md
│   ├── 01.json
│   ├── 02.json
│   └── ...
├── py/                      # examples for skills/py/SKILL.md (not yet seeded)
├── ts/
├── tsx/
├── rs/
├── release/
├── ship/
└── wisdom/
```

Each `<skill>/<id>.json` is a self-contained example. The harness picks them up by glob.

## Current per-skill counts

| skill | examples | phase | notes |
|---|---|---|---|
| `commit` | 5 | 1 (seed) | Hand-crafted; covers bugfix, refactor, multi-file feature, docs, release |
| `py` | 0 | — | Pending |
| `ts` | 0 | — | Pending |
| `tsx` | 0 | — | Pending |
| `rs` | 0 | — | Pending |
| `release` | 0 | — | Pending |
| `ship` | 0 | — | Pending |
| `wisdom` | 0 | — | Pending |

Phase 1 target: 30 examples across 8 priority skills (5 per skill, with `commit` getting more weight if needed). Phase 2: 100+ examples mined from session transcripts.

## Schema

Full schema documented in [`research/eval-sets.md`](../research/eval-sets.md#required-schema-for-evalsskillidjson). Minimal shape:

```json
{
  "id": "01",
  "skill": "commit",
  "task": "user just made a small bugfix; help them commit it",
  "context": {
    "git_status": "...",
    "git_diff": "...",
    "files_changed": ["..."]
  },
  "expected_outcome": {
    "must_use_format": "<regex>",
    "subject_max_chars": 72,
    "must_not_include": ["..."],
    "should_mention": ["..."]
  },
  "rubric": [
    {"criterion": "...", "weight": 0.3}
  ],
  "source": "synthetic|real-session|failure-case",
  "provenance": "hand-crafted-YYYY-MM-DD or session-hash"
}
```

The harness validates against this shape on load. Missing required fields fail the eval run.

## Scoring

Composite score per example:

```
example_score = outcome * 0.5 + rubric_score * 0.3 + cost_score * 0.2
```

- **Outcome** (binary, 0 or 1): all `expected_outcome` constraints pass.
- **Rubric** (0 to 1): LLM-judge scores each criterion 0-1, weighted average.
- **Cost** (0 to 1): `1 - (tokens_used / budget)`, clamped to [0, 1].

Aggregate candidate score is the mean across all examples in the skill's eval set.

Details: [`research/eval-sets.md#scoring-formula`](../research/eval-sets.md#scoring-formula).

## How to add an example

1. **Pick the skill** the example targets (`commit`, `py`, etc.).
2. **Pick the next `id`** in that subdirectory (zero-padded, two-digit: `06`, `07`, ...).
3. **Source the example** from one of three:
   - **Real session transcript** (preferred — 60% of target mix). Find a turn in `~/.claude/projects/<slug>/*.jsonl` where the skill was invoked successfully. Paraphrase the user prompt and edit identifying details so we don't ship private data verbatim.
   - **Synthetic from a skill rule** (30%). Take an ALWAYS or NEVER from the SKILL.md and template an example that exercises it.
   - **Failure case** (10%). Pick a `.diary/` entry or a `[fix]`/`[refined]` commit that reveals a regression; reconstruct the pre-failure state.
4. **Fill in the JSON** per the schema. Pay attention to:
   - `must_not_include`: every literal substring you want banned. Case-sensitive.
   - `should_mention`: literal substrings the response must reference. Case-insensitive in the harness.
   - `rubric weights`: must sum to 1.0 across criteria. The harness enforces this.
5. **Validate locally**: `python tools/eval-skill.py --skill <name> --example <id> --dry-run` (Stage 3, pending).
6. **Commit**: one example per commit. Use the `[evals]` prefix: `[evals] commit/06: docs-only changes are docs section`.

## Contamination notes

The eval set lives in this repo. The agent has read access. **Examples can leak into the agent's context during a task.**

Phase 1 position: **we accept this**. The eval is small, hand-curated, and visible. The agent doesn't gain from gaming the eval because:

1. The eval runs offline (in `make refine-skill`), not during user turns.
2. The "right answer" in the eval *is* good behavior; the agent reading it is no worse than reading the corresponding SKILL.md.
3. PR review is the merge gate. Even if a candidate gimmes the eval, the maintainer sees the diff.

Phase 2 fix (when needed): hold 20% of examples back as a private set, gitignored, synced via a side channel. The harness uses the private set for the gating decision; the public set is for proposer context only. Details: [`research/eval-sets.md#contamination-tradeoff`](../research/eval-sets.md#contamination-tradeoff).

If you notice candidates that score implausibly well, suspect contamination first.

## Privacy

When mining real sessions:

- **Paraphrase the user prompt.** Don't copy verbatim if it contains personal details.
- **Strip identifying paths.** Replace `/home/ondra/wk/myproject/` with `/some/repo/` or a fake path that makes sense for the example.
- **Edit diffs.** If the real diff includes proprietary code or secrets, replace with synthesized equivalents that exercise the same skill behavior.
- **Set `source: "real-session"` and `provenance: "<session-id-truncated>"`** so we can find it again if needed.

## Anti-patterns when writing examples

- **Don't pin to language-model-specific quirks.** "The response uses exactly the phrase 'Sure, I can help'" is brittle; eval the *behavior*, not the surface text.
- **Don't over-constrain.** If `expected_outcome` has 15 fields, almost every response will fail one. Keep it to 3-5 hard constraints + a rubric for the soft stuff.
- **Don't reward verbose responses.** The cost penalty exists for a reason; long answers should not be rewarded just for being thorough.
- **Don't write rubrics the LLM-judge can't evaluate.** "The response sounds confident" is unjudgable; "The response cites the specific file modified" is judgable.
- **Don't fake the context.** If `git_diff` in the example doesn't match what `git_status` would produce, the example is broken; the agent reads both and gets confused.

## See also

- [`research/eval-sets.md`](../research/eval-sets.md) — full design rationale
- [`research/library-drift.md`](../research/library-drift.md) — why the eval set exists at all
- [`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md) — the loop this set feeds
