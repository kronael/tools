# Skill Libraries Cannot Evolve Themselves

A consolidated writeup of what we learned designing an auto-improvement loop for an LLM coding agent's skill library. Three iterations of the spec, four research papers, two horror stories, one published critique of a competing system. The conclusion is unambiguous: **the LLM cannot maintain its own skill library without an external evaluator, and "the LLM rates its own work" is not an external evaluator**.

This document is the merged form of the research notes in [`research/`](.) and the spec in [`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md). Read this when you want the full picture; read the per-topic files when you want a single source in depth.

---

## TL;DR

A skill library is the procedural memory of an LLM agent — markdown files like `commit/SKILL.md` that tell the agent how to do specific tasks. The library is supposed to compound: every session teaches the agent something, the agent updates the relevant skill, future sessions benefit. The dream is auto-improvement.

The reality is that **letting an LLM curate its own skill library produces +0.0pp lift over a baseline with no library at all**, while a human-curated library lifts the same agent by +16.2pp on the same benchmark. The gap is measured, replicable, and persists across architectures.

What works instead:

1. **Offline batch refinement**, not online runtime mutation.
2. **External evaluator** (an eval set the proposer cannot game) decides which edits land.
3. **PR review** as the human gate — explicit, blocking, mandatory.
4. **Three governance components together**: outcome-driven retirement, bounded active cap, meta-skill priority.

What doesn't work:

- Live mutation of skills as the agent runs (Hermes-style).
- Per-turn reflection (a documented anti-pattern from Reflexion).
- Quarantine-without-eval (humans rubber-stamp edits they can't measure).
- Self-rated "did this improve?" (sycophantic confirmation bias).

The rest of this document is the long-form argument: what every existing system does, why each fails the way it does, what the literature converges on, and the design we landed on.

---

## The number that ended the discussion

[Library Drift in LLM Agents (arXiv 2605.19576)](https://arxiv.org/abs/2605.19576) is the single most important paper in this corpus. It introduces SkillsBench, a held-out coding-task benchmark, and measures the lift of three configurations against an identical baseline agent:

| condition | lift over baseline |
|---|---|
| Human-curated skill library | **+16.2 percentage points** |
| LLM-authored skill library, no human curation | **+0.0 percentage points** |
| No skill library at all | (baseline) |

The +0.0pp result is not noise. The authors show that the edits an LLM proposes to its own library, evaluated by the same LLM, cancel out on net: some help, some hurt, the average returns to baseline. The agent appears to improve (every edit looks like progress in the moment) but the cumulative effect is zero.

The paper names three mechanisms that produce this:

1. **Verbose-hedging drift.** Every edit adds caveats and edge-case handling. A rule that started as "always use a transaction" becomes "use a transaction unless the operation is read-only, idempotent, or the caller specified `--no-tx`, in which case..." The original signal dilutes; the agent stops trusting the rule.

2. **Loss of orthogonality.** New proposed skills overlap existing ones. The routing layer has two skills that both match a task, picks wrong often enough, and the gain from either skill's content disappears into routing noise.

3. **Self-rewarded bad edits.** The LLM rates its own edit as "an improvement" almost regardless of whether it is one. Confirmation bias compounds across cycles. Without an external evaluator, every edit appears good; in aggregate, edits regress to baseline.

The third mechanism is the killer. It generalizes to every system that lets the same LLM both propose and judge a change — which is most published agentic-skill systems.

### The survey finding

The same paper surveys 14 published systems (Hermes, Voyager, Generative Agents, RestGPT, and several proprietary platforms). It looks for two governance components: **outcome-driven retirement** (skills get demoted when they stop helping) and **bounded active cap** (the active set has a hard size limit). The finding:

- Most have neither — the library grows unbounded.
- A few have retirement but no cap.
- One has a cap but no retirement.
- **Zero** have both.

The implication: the field knows about these failure modes individually but hasn't combined the fixes. The +0.0pp result holds against every system in the survey.

---

## What Hermes actually does (and what BSWEN found)

Hermes Agent's [Curator feature](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator) is the closest existing system to "auto-improve your skills." It has been productized, has users, has support docs. Three things about it we got wrong on first read:

1. **The trigger is inactivity, not per-turn.** The Curator runs when the agent has been idle for ≥2 hours, or on a weekly schedule. We initially assumed it ran after every turn; that's wrong, and per-turn is in fact what [Reflexion (arXiv 2303.11366)](https://arxiv.org/abs/2303.11366) identifies as the anti-pattern.

2. **The scope is agent-authored skills only.** Bundled/hub-installed skills stay read-only. The Curator treats them as the canonical baseline; it can only retire or consolidate skills the agent itself created during use.

3. **The behavior is contested upstream.** [BSWEN's April 2026 writeup](https://docs.bswen.com/blog/2026-04-07-hermes-ai-overwrites-skills/) documents that Hermes's Curator overwrites manually customized skills with worse versions. Their finding: "The agent almost always thinks it performed well, even when it didn't." [Hermes issue #18373](https://github.com/NousResearch/hermes-agent/issues/18373) is an open P1 ticket from a user whose 54 personally-created custom skills were archived by the Curator's first automatic run with no dry-run or approval prompt.

What this means for us:

- The **scope guardrail** is good: bundled skills should be untouchable. Our equivalent is the `skills/*/SKILL.md` files in this repo — they're the canonical bundle.
- The **idle trigger** is right; per-turn is wrong.
- The **live-edit-without-approval** behavior is wrong even with quarantine, because humans rubber-stamp edits they can't measure.
- The **self-rated confidence** is the load-bearing failure. We need an external evaluator.

The clean takeaway: copy Hermes's *scope rules*, not its *action model*.

---

## The model we adopt: DSPy MIPROv2

[DSPy's optimizer suite](https://dspy.ai/learn/optimization/optimizers/) is built on a completely different assumption from Hermes. Where Hermes mutates the agent online and trusts the agent's own assessment, DSPy assumes **the agent is the optimizer's target, not its judge**.

[MIPROv2 (Multi-prompt Instruction PROposer v2)](https://dspy.ai/api/optimizers/MIPROv2/) — the workhorse — runs as a batch compilation step:

1. **Bootstrap traces**: run the agent on a small training set, record successful runs.
2. **Propose**: an LLM proposer reads the traces and proposes alternative prompt instructions.
3. **Evaluate**: each candidate is scored on a held-out validation set using a user-supplied metric.
4. **Search**: Bayesian optimization picks the candidate combination that maximizes validation score.
5. **Output**: the best instructions get baked into the program. No online mutation.

The detail that matters: **the evaluator is external to the proposer**. The proposer suggests changes; the evaluator measures them against held-out tasks; the search optimizes for measured outcomes, not proposer confidence.

Translated to our problem:

- Our "program" is the bundled skill library in this repo.
- Each `skills/<name>/SKILL.md` is a DSPy-style instruction prompt.
- The "metric" is a scored outcome from replaying real tasks.
- The "training/validation set" is an `evals/<skill>/*.json` directory of recorded sessions plus expected behaviors.

We don't need MIPROv2's full Bayesian search — one skill at a time, propose N variants, score each, accept the best — but the structural insight (external evaluator, batch, offline, no self-assessment) is exactly what Library Drift's failure mode demands.

The [sample-efficient LM-program optimization paper (arXiv 2406.11695)](https://arxiv.org/abs/2406.11695) puts the eval-set size at 50+ examples for stable optimization signal. Below that, individual-example noise dominates.

---

## A-MEM: Zettelkasten for the dedup problem

[A-MEM (arXiv 2502.12110)](https://arxiv.org/abs/2502.12110) applies Niklas Luhmann's Zettelkasten method — atomic notes, links between them, structure emerges — to LLM agent memory. We're not building a runtime memory system, but the dedup mechanics A-MEM describes apply directly to skill curation:

- Every new memory is an **atomic note** (one fact, one observation).
- Notes are **embedded** and linked to semantically similar prior notes.
- **Links emerge** from cosine proximity, not from human-assigned categories.
- **Retrieval** walks the graph: pull query-similar notes plus their strongest links.
- **Maintenance** is structural: when a cluster gets dense, propose a hub note linking to the cluster.

The two mechanisms worth borrowing:

1. **Dedup by embedding similarity.** If a proposed edit to `commit/SKILL.md` is semantically very close to an existing rule in that file, drop the proposal as redundant.
2. **Orthogonality check.** If a proposed new skill embeds within ε of an existing skill's description + `when_to_use`, reject as overlap — this is the "loss of orthogonality" failure mode from Library Drift, applied as a pre-merge gate.

A simple `sentence-transformers` model with cosine distance is enough; we don't need a vector DB for ~40 markdown files.

---

## Reflexion: why per-turn reflection is wrong

[Reflexion (arXiv 2303.11366)](https://arxiv.org/abs/2303.11366) is often miscited as endorsing per-turn self-criticism. It does not. The paper's actual finding:

- **Episode-boundary reflection works.** After a task finishes (success or failure), the agent writes a short reflection to an episodic memory buffer. The next attempt at a related task gets the buffer prepended to its prompt. Performance compounds across episodes.

- **Per-turn reflection is repetitive and inaccurate.** Asking the agent to reflect *during* a turn — between tool calls, after each step — produces sycophantic ("My approach was correct, but...") or repetitive ("I should reconsider...") output that adds tokens without changing behavior.

The [HuggingFace writeup on Reflection in LLM agents](https://huggingface.co/blog/Kseniase/reflection) makes this explicit. Per-turn reflection is "thinking out loud" that the LLM has already done in chain-of-thought; making it an explicit additional step doesn't recover signal.

This is why our first spec (v1) — which used a `Stop` hook after every assistant turn to trigger a skill review — was the wrong granularity. Reflexion's correct granularity is the **episode boundary**, which for our purposes is either `SessionEnd` or an idle timer.

---

## Anthropic's own guidance (which conflicts with our house style)

Anthropic has published three sources on writing skills:

- [Equipping Agents for the Real World with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) (engineering blog)
- [Agent Skills best practices](https://anthropic.mintlify.app/en/docs/agents-and-tools/agent-skills/best-practices) (docs)
- [`skill-creator/SKILL.md`](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) (their canonical meta-skill)

Five points across the three sources:

1. **Progressive disclosure.** Skill files load in layers. The frontmatter (name, description, when_to_use) is always visible to the router. The body loads only when the skill is selected. Linked sibling files load on demand. Don't pay context cost upfront.

2. **Pushy descriptions.** Anthropic recommends assertive "Use when X" phrasing over passive "This skill provides X." Passive descriptions don't trigger; pushy ones do.

3. **"Explain why" over capitalized rules.** This is the **direct conflict with our wisdom skill**. Anthropic's claim: rules without rationale degrade because the model follows the letter but misses edge cases. Narrative rules with embedded "why" generalize better.
   - Anthropic-preferred: "If you're updating a migration that's already been deployed, double-check the rollback path — out-of-order migration application leaves the schema in an inconsistent state."
   - Our `wisdom`-style: "NEVER apply migrations out of order — ALWAYS check deployed state first."
   - Both convey the same rule. Anthropic's framing teaches; ours commands.

4. **Models don't improve linearly with rule count.** Past ~10 rules per skill, signal dilutes. Several of our skills are at or past that threshold.

5. **Inline examples beat additional rules.** A small example showing right-vs-wrong action provides more signal than another rule.

Our `wisdom/SKILL.md` codifies ALWAYS/NEVER caps as the house style. Anthropic's data says this is sub-optimal for generalization, but the user has explicit preferences for this style. The right resolution is **not** to argue from first principles — it's to let the eval loop measure both variants on real tasks. Pick `commit` (densest rules, densest eval set), produce A (ALWAYS/NEVER) and B (narrative with why), score both, let the numbers settle the question.

This is also what Anthropic recommends: test skills against a small task suite. Their guidance and ours converge on the meta-rule "measure don't assume."

---

## What blows up at scale: the $47k loop

A widely-shared [TechStartups writeup from November 2025](https://techstartups.com/2025/11/14/ai-agents-horror-stories-how-a-47000-failure-exposed-the-hype-and-hidden-risks-of-multi-agent-systems/) documents a $47,000 overrun in a multi-agent product. The technical details are specific to that product; the failure modes generalize to any system with agent-modifies-config feedback loops.

The deployed system lacked all five of:

1. **Bounded memory** — agents accumulated context indefinitely.
2. **Observability** — operators couldn't see what each agent was doing in real time.
3. **Governance / approval gates** — agents made changes (including spending changes) without human checkpoints.
4. **Stop conditions** — no "exit if X" rules; agents looped until manually killed.
5. **Cost ceilings** — no per-task or per-day spend cap.

The loop that ran up the bill: agent A asked agent B to refine a plan; B asked C; C answered with a longer plan; A re-asked B with the longer plan; repeat for hours.

For a skill-eval loop, the equivalent risk profile is:

| risk | mitigation in v3 |
|---|---|
| Unbounded memory | Eval set is fixed-size; queue file rotates by date |
| Observability | Every proposal writes `rationale.md` + `provenance.json` + `cost.txt` |
| Approval gate | Mandatory PR review before merge — `gh pr merge*` is hard-denied at the harness level |
| Stop conditions | Per-run `--max-cost` and `--max-iterations` flags |
| Cost ceiling | Per-skill-refine run capped at $0.50 default; CI fails if exceeded |

The deeper lesson: any system that mutates its own behavior in a feedback loop needs an external invariant the loop can't touch. For our eval loop, that invariant is **the merge of a skill change to the main branch requires a human reviewer**. Until that gate, candidates are inert.

---

## The design we landed on (v3)

Three iterations, two abandoned. The current design is the third pass.

### v1 (abandoned): Stop hook + `claude -p` child

A `Stop` hook spawns `claude -p` after every assistant turn. The child reads the session JSONL, decides whether a skill needs editing, writes the edit to `~/.claude/skills/`.

Killed because:

- **Per-turn trigger is documented anti-pattern.** Reflexion finding above.
- **Incomplete snapshot.** The hook fires before the session is durably written to JSONL; final tool results are missing.
- **Recursion guard leaks.** Every guard mechanism we drafted (env var, marker file, claude flag) had a path where it leaked across nested invocations.
- **`--bare` flag uncertainty.** We needed the child to skip its own session bootstrap. The flag we wanted didn't exist or had unstable semantics.

### v2 (abandoned): idle trigger + quarantined live edits

Replace `Stop` with `SessionEnd` or an idle timer. Keep live-edit-to-`~/.claude/skills/` but quarantine edits in a "pending" subdir; require an explicit `/approve` from the user before promoting.

Killed because:

- **Library Drift shows quarantine-without-eval doesn't help.** Humans rubber-stamp edits they can't measure. The missing piece is an eval set, not an approval prompt.
- **BSWEN documents exactly this failure mode in Hermes.** The operator approves on inspection; the skill regresses; nobody notices because there's no comparison run.
- **Runtime mutation undoes the source/install split.** In this repo, `skills/*` is the source of truth and `~/.claude/skills/` is the installed snapshot. Runtime mutation creates drift between committed and loaded state.
- **Cross-machine drift.** Edits applied on machine A don't propagate to machine B without re-syncing.

### v3 (current): offline bundle eval loop

Forget runtime mutation entirely. Build an offline eval loop that:

1. Proposes edits to `skills/*/SKILL.md` in this repo.
2. Scores each candidate against a held-out eval set.
3. Lands accepted edits as PRs.
4. Never mutates the live `~/.claude/skills/` directory.

The architecture:

```
evals/<skill>/*.json   ──┐
(hand-curated + mined)   │
                         ▼
                    proposer (LLM)
                         │
                  proposes N edits to one SKILL.md
                         │
                         ▼
                    evaluator
                         │
              replays eval set against each candidate
              scores: outcome × 0.5 + rubric × 0.3 + cost × 0.2
                         │
                         ▼
                  candidates/<ts>-<skill>/
                    patch.diff
                    rationale.md
                    scores.json
                    cost.txt
                         │
                         ▼
                    PR + human review
                         │
                  merge → ships in next release
```

Why this works:

- **Eval set is the external invariant** the proposer can't game.
- **PR review** is the human gate; `gh pr merge*` is hard-denied at the harness level (no auto-merge can land).
- **Offline** = no per-turn cost, no recursion, no incomplete snapshots, no live-runtime risk.
- **One source of truth** = edits land in the repo; the install path syncs to `~/.claude/`.

The mapping to Library Drift's three-part governance recipe:

| Library Drift requirement | v3 mechanism |
|---|---|
| Outcome-driven retirement | Phase 2: surface skills with declining eval scores to maintainer for deletion PR |
| Bounded active cap | PR review is the tournament; new-skill PRs must justify the addition |
| Meta-skill priority | Edits to `skills/wisdom/` re-validate every dependent skill |

---

## The eval set is the hard part

Everything else (proposer, evaluator, gating) is mechanical once the eval set exists. Without one, [Library Drift](#the-number-that-ended-the-discussion) measured exactly what happens: regression to baseline.

### Schema

Each example targets a specific skill:

```json
{
  "id": "01",
  "skill": "commit",
  "task": "<one-line description of what the user is asking for>",
  "context": {
    "cwd": "<repo path snippet>",
    "git_status": "<output of git status --porcelain>",
    "git_diff": "<truncated diff or null>",
    "files_changed": ["<path>", "..."],
    "prior_turns": "<optional last 1-2 user/assistant turns>"
  },
  "expected_outcome": {
    "must_use_format": "<regex, e.g. '\\[\\w+\\] '>",
    "subject_max_chars": 72,
    "must_not_include": ["<banned string>", "..."],
    "should_mention": ["<topic that should be covered>"]
  },
  "rubric": [
    {"criterion": "<what to check>", "weight": 0.3}
  ],
  "source": "real-session | synthetic | failure-case",
  "provenance": "<session hash or .diary entry>"
}
```

### Source mix: 60 / 30 / 10

| source | share | how to mine |
|---|---|---|
| Real session transcripts | 60% | Walk `~/.claude/projects/<slug>/*.jsonl`. Find turns where a skill was invoked and the action succeeded. Paraphrase the user prompt, edit context to drop private data. |
| Synthetic from skill rules | 30% | Every ALWAYS/NEVER in a SKILL.md implies a test case. Templating script extracts rules and generates prompts. Human reviews for plausibility. |
| Failure cases | 10% | Search `.diary/*.md` for "fix:", "bug:", "regressed". Each is a high-value example because it pins behavior the current skill *didn't* prevent. |

Real sessions ground the eval in actual usage. Synthetic gives mechanical coverage. Failures pin known regressions.

### Scoring

Composite per example, then mean across the set:

```
example_score   = outcome*0.5 + rubric*0.3 + cost*0.2
candidate_score = mean(example_score for example in eval_set)
```

- **Outcome** (0.5 weight): binary, mechanical checks of `expected_outcome` constraints.
- **Rubric** (0.3): LLM judge with skill-specific rubric; weighted average across rubric criteria.
- **Cost** (0.2): tokens used, normalized against a per-skill budget. Discourages verbose-hedging drift.

Outcome dominates because it's the most trustworthy signal (no LLM in the loop). Cost penalty is the explicit antibody against Library Drift's verbose-hedging mechanism.

### Contamination

The eval set lives in this repo. The agent has read access to this repo. The eval set CAN appear in the agent's context during a task, and the agent can game it.

Phase 1 accepts the risk. Phase 2 needs:

- A held-out **secret** eval set committed but gitignored from the agent's view, OR
- Eval examples gitignored entirely (lives only on maintainer's machine), OR
- Rotating held-out set on each release.

The cleanest long-term solution is option 3: a fixed-size pool, rotated each release, with the rotation deterministic from the release tag so reproducibility holds. Phase 1: just ship 30 examples and don't sweat it yet.

### Size guidance

Per DSPy MIPROv2's empirics:

| phase | size | purpose |
|---|---|---|
| Phase 1 | 30 hand-curated, ~5 per priority skill | Detect obvious regressions; smoke-test the harness |
| Phase 2 | 100+ examples, semi-automated mining + manual QA | Stable optimization signal |
| Phase 3 | Continuous expansion from session transcripts | Eval set grows as the agent is used |

Below ~50, individual-example noise dominates and you can't tell which proposals are better.

---

## What's still open

Three questions don't change the architecture but need answers before the loop is production:

1. **Eval-set contamination strategy.** Phase 1 accepts the risk; Phase 2 needs the rotating secret-set described above.
2. **Skill versioning.** Should SKILL.md frontmatter carry a `version: N` field? Git history covers it for reverts, but explicit versioning makes rollback tooling cleaner.
3. **Anthropic format conflict.** ALWAYS/NEVER caps vs narrative-with-why. The eval loop is the right place to settle this — run A/B on `commit` and let scores decide.

And one practical question:

4. **Where does the proposer LLM live?** A fresh `claude -p --dangerously-bypass-approvals-and-sandbox` inside dockbox (we're the perimeter) is the obvious answer; it inherits the user's `~/.claude` for auth and lives in the same environment as the eval-set tasks. Per-run cost cap holds the spend down.

---

## Concrete file layout

```
skills/<name>/SKILL.md           # the bundled library (source of truth)
evals/<skill>/<id>.json          # eval examples per skill
evals/README.md                  # schema, contamination notes
tools/refine-skill.py            # proposer driver
tools/eval-skill.py              # evaluator driver
candidates/                      # proposal artifacts (gitignored)
research/*.md                    # the sources behind the design
specs/2-hermes-skill-autoimprove.md   # the current spec
```

Makefile targets:

- `make refine-skill SKILL=<name>` — proposer + evaluator + write candidate
- `make eval-skill SKILL=<name>` — score current SKILL.md against eval set (no proposer)
- `make pr-candidate CAND=<dir>` — open PR from a candidate directory (`gh pr create`, no auto-merge)

---

## Sources

| source | what it gave us |
|---|---|
| [Library Drift, arXiv 2605.19576](https://arxiv.org/abs/2605.19576) | The +0.0pp / +16.2pp result; the three-part governance recipe; the survey of 14 systems |
| [SkillsBench, arXiv 2602.12670](https://arxiv.org/abs/2602.12670) | The benchmark that exposes drift; 86 tasks across 11 domains with deterministic verifiers |
| [DSPy MIPROv2](https://dspy.ai/api/optimizers/MIPROv2/) | The model: external evaluator, batch compilation, validation-set scoring, no online mutation |
| [Sample-efficient LM-program optimization, arXiv 2406.11695](https://arxiv.org/abs/2406.11695) | Eval-set size needed for stable optimization (~50+) |
| [A-MEM, arXiv 2502.12110](https://arxiv.org/abs/2502.12110) | Dedup via embedding similarity; orthogonality check as pre-merge gate |
| [Reflexion, arXiv 2303.11366](https://arxiv.org/abs/2303.11366) | Episode-boundary reflection works; per-turn doesn't |
| [Self-Refine, arXiv 2303.17651](https://arxiv.org/abs/2303.17651) | Sibling work; intra-task refinement has limits |
| [Hermes Curator docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator) | Idle trigger; agent-authored-only scope; what the field looks like |
| [BSWEN's Hermes critique](https://docs.bswen.com/blog/2026-04-07-hermes-ai-overwrites-skills/) | Documented failure mode: self-rated confidence overwrites manual edits |
| [Hermes issue #18373](https://github.com/NousResearch/hermes-agent/issues/18373) | Production bug — 54 user skills archived without approval |
| [Anthropic — Equipping Agents with Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | "Explain why" > caps; progressive disclosure; inline examples |
| [Anthropic Agent Skills best practices](https://anthropic.mintlify.app/en/docs/agents-and-tools/agent-skills/best-practices) | Pushy descriptions; rule-count ceiling; testing-against-task-suite |
| [TechStartups $47k multi-agent loop](https://techstartups.com/2025/11/14/ai-agents-horror-stories-how-a-47000-failure-exposed-the-hype-and-hidden-risks-of-multi-agent-systems/) | Stop conditions and cost ceilings are non-negotiable |

---

## The shortest version

If you remember one thing from this document, it's this: **a proposer and an evaluator must not be the same LLM, must not be in the same loop, and must not share confidence**. Library Drift measured what happens when they do — zero net progress. Everything else in this design (offline, PR-gated, eval-set-scored, governance-bounded) is the structural consequence of that single constraint.

The skill library is procedural memory. Procedural memory needs an external test for what works. Without that test, the library is the agent's opinion of itself — and the agent's opinion of itself is, on average, exactly as good as having no library at all.
