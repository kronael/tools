# Research Hub

Notes, paper summaries, and source links that informed the **skill auto-improvement design** in [`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md).

Each file is a single topic. Drop new findings into their own file rather than expanding an existing one. Keep files between 150-400 lines so a future reader can pull just the brief they need.

## Index

| topic | file | one-liner |
|---|---|---|
| Hermes Agent | [hermes-agent.md](hermes-agent.md) | What the Curator actually does (idle-triggered) and why BSWEN's critique matters |
| **Library Drift paper** | [library-drift.md](library-drift.md) | Empirical: LLM-authored skills underperform human-curated by 16.2pp — the load-bearing finding |
| DSPy MIPROv2 | [dspy-miprov2.md](dspy-miprov2.md) | Offline batch compilation against an eval set — the model we're adopting |
| A-MEM | [a-mem.md](a-mem.md) | Zettelkasten for agent memory: atomic notes, embedding-linked, dedup by similarity |
| Reflexion | [reflexion.md](reflexion.md) | Self-critique helps over episodes; per-turn reflection is a documented anti-pattern |
| **Anthropic SKILL.md guidance** | [anthropic-skills.md](anthropic-skills.md) | "Explain *why*" > "ALWAYS/NEVER caps" — direct conflict with our wisdom skill |
| **Eval-set construction** | [eval-sets.md](eval-sets.md) | Schema and bootstrapping plan for `evals/<skill>/<id>.json` |
| Multi-agent failures | [multi-agent-horror.md](multi-agent-horror.md) | What blows up at scale: no stop conditions, no cost ceilings, no observability |
| **Competing systems** | [competing-systems.md](competing-systems.md) | Comparison matrix: Hermes, DSPy, Reflexion, LangGraph HITL, mem0, Letta, A-MEM, Voyager, AutoGen, CrewAI |
| **Anti-patterns** | [anti-patterns.md](anti-patterns.md) | Documented horror stories + the exact mitigation each maps onto in v3 |

The bolded files are load-bearing: read those first.

## Design history — v1 → v2 → v3

Three iterations of the spec, each abandoned for a documented reason. The current design is the third pass.

### v1 — Stop hook + `claude -p` child (abandoned)

**Idea**: a `Stop` hook spawns `claude -p` after every assistant turn. The child reads the just-finished session, decides whether a skill needs editing, and writes the edit.

**Why we killed it**:

- **Per-turn trigger is a documented anti-pattern**. See [`reflexion.md`](reflexion.md): per-turn reflection produces sycophantic, repetitive criticism that adds tokens without changing behavior. The right granularity is episode-boundary (session end) or idle (Hermes's actual design).
- **Incomplete snapshot**. The Stop hook fires before the conversation is durably written to its JSONL; sampling at that point misses the final tool results.
- **Recursion guard leaks**. The child invocation needs its own `Stop` disabled or it recurses. Every guard mechanism we drafted (env var, marker file, claude-flag) had a path where it leaked across nested invocations.
- **`--bare` flag uncertainty**. We needed the child to skip its own session bootstrap. The flag we wanted didn't exist or had unstable semantics across versions.

Spec v1 lives in git history; do not resurrect.

### v2 — idle trigger + quarantined live edits (abandoned)

**Idea**: replace `Stop` with `SessionEnd` or an idle timer. Keep the live-edit-to-`~/.claude/skills/` behavior but quarantine edits in a "pending" subdir and require an explicit `/approve` from the user before promoting them.

**Why we killed it**:

- **[Library Drift](library-drift.md) shows quarantine-without-eval doesn't help**. The paper found +0.0pp lift for LLM-authored libraries even when humans were notionally in the loop — humans rubber-stamp edits they can't measure. The missing piece is an eval set, not an approval prompt.
- **[BSWEN's Hermes writeup](anti-patterns.md)** documents this exact failure: Hermes proposes edits, the operator approves them on inspection, the skill regresses, the operator doesn't notice because there's no comparison run.
- **Runtime mutation of `~/.claude/skills/` undoes the source/install split** in this repo. The bundle in `skills/*` is the source of truth; runtime mutation creates drift between what's committed and what's loaded.
- **Cross-machine drift**. Edits applied on machine A don't propagate to machine B. Either we re-introduce sync (which is what the install path already does) or we accept divergence (which defeats the purpose).

### v3 — offline bundle eval loop (current)

**Idea**: forget runtime mutation entirely. Build an **offline eval loop** that proposes edits to `skills/*/SKILL.md` in this repo, scores each against an eval set, and lands accepted edits as PRs. The model is DSPy MIPROv2 adapted to markdown skill files. See [`specs/2-hermes-skill-autoimprove.md`](../specs/2-hermes-skill-autoimprove.md).

**Why this works**:

- **Eval set is the external invariant** the agent can't game. [Library Drift](library-drift.md) measured the exact regression that happens without it; we cannot ship without one.
- **PR review** is the human gate. The settings-recommended.json `gh pr merge*` deny rule enforces "no auto-merge" at the harness level.
- **Offline = no per-turn cost, no recursion, no incomplete snapshots**. The loop runs when the user invokes `make refine-skill SKILL=<name>`, not on every Stop.
- **One source of truth**: edits land in this repo; the install path syncs them to `~/.claude/`. No drift.

The three open questions in the spec — [eval contamination](eval-sets.md#contamination), [skill versioning](anthropic-skills.md#versioning), [Anthropic format conflict](anthropic-skills.md) — are tractable; none change the architecture.

## How to add a topic

1. Create `research/<slug>.md` with a 1-line title + the source link(s).
2. Summarize the source in your own words (one paragraph).
3. List the specific findings that bear on our design (bullet form).
4. Note what it suggests we should do or avoid.
5. Add a row to the table above.

## Conventions

- Cite the source URL on first mention. Add a footnote-style block at the bottom if you cite many.
- One claim per bullet. If you can't link a claim to a quote or measurement, qualify it ("probably", "anecdotally").
- Keep each file under ~400 lines. If it's longer, split it.
- Link out to the spec section a finding bears on — `specs/2-hermes-skill-autoimprove.md#stage-3-evaluator` etc.
