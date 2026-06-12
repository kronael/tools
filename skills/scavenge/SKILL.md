---
name: scavenge
description: Codify public best practice into a durable, oracle-tested artifact — skill, agent, guideline, runbook, checklist, review template, or spec. NOT for conversation-history patterns (use learn) or editing an existing artifact (use wisdom).
when_to_use: "create a skill for X", "write up our guideline for Y", "draft a runbook for Z", "make a checklist for W", "codify our practice on X", "produce a review template for Y", "make an agent for Z", "draft a spec for V", new methodology, repeatable workflow extraction
user-invocable: true
---

# scavenge — gather, oracle-test at every step, assemble

You're not inventing. Someone (NN/g, Nielsen, Norman, Krug, GOV.UK,
Google SRE, OWASP, ...) has already figured out the activity in front
of you. The job: scavenge their work, sniff it for rot via `oracle` at
each step, and assemble what survives into a durable artifact your team
can reuse.

**Critique is not localised to step 3.** It threads through the
pipeline. `oracle` is the adversarial engine; call it at every
checkpoint below. Confirmation bias accumulates step by step — one
late critique can't undo a bias planted at step 1.

## Output shapes

| Shape | Path | When |
|-------|------|------|
| **skill** | `~/.claude/skills/<name>/SKILL.md` | reusable instruction set invoked by name |
| **agent** | `~/.claude/agents/<name>.md` | autonomous worker (tools, isolation) |
| **guideline** | `<cwd>/docs/guidelines/<name>.md` or section in `CLAUDE.md` | team-wide rules + rationale |
| **runbook** | `<cwd>/docs/runbooks/<name>.md` | preconditions + ops + rollback |
| **checklist** | `<cwd>/docs/checklists/<name>.md` | terse `[ ]` items in a workflow |
| **review template** | `<cwd>/docs/templates/review-<name>.md` | recurring critique with fixed criteria |
| **spec** | `<cwd>/specs/<name>.md` | forward-looking design / proposal |

Pick by REUSE + INVOCATION pattern. Pipeline is identical for all
shapes; only step 5's skeleton differs.

## When to invoke

- Recurring activity, known public best practice, team not uniform on it
- "Let's codify how we do X" / "write up our guideline for Y"
- After doing X twice ad-hoc and noticing the pattern

## When NOT to invoke

- One-off — just do it
- Tacit-knowledge domain (no public best practice) → use `learn`
- Existing artifact covers it → use `wisdom` to refine
- Zero repetition — diary entry suffices

## The pipeline (with critique checkpoints)

### Step 1 — name the activity AND the output shape

ONE sentence: "<name> [shape] that <verb> <domain> for <persona/output>."
Wobbling sentence → scope not bounded; reshape first.

**Critique checkpoint 1 (light).** Ask `oracle` in 2–4 lines: "is this
activity well-bounded, and is the shape the right one given REUSE +
INVOCATION pattern?" If oracle suggests a different shape, listen.

### Step 2 — research subagent

Spawn one (`general-purpose` or `Explore`). Self-contained prompt:

- activity name + scope, 5–15 sub-topics, explicit out-of-scope list
- length budget ~1500–2000 words
- output path `<cwd>/docs/<topic>/research-<topic>.md`
- cite-the-source — every claim grounded in named paper / author / org
- structure: methods, persona (if applicable), per-task protocol,
  output template, pitfalls

ALWAYS self-contained — subagent has zero context.

### Step 3 — adversarial oracle critique (the deep one)

Invoke `oracle` adversarially: "find what's wrong, where the science
doesn't support the claim, where the protocol generates bad data,
what to cut as filler, where classification collapses in practice."
NEVER frame as "is this correct?" Save to
`<cwd>/docs/<topic>/oracle-critique.md`.

### Step 4 — fold the critique in

Rewrite the methodology doc. Cut, correct, add. Don't defend. Keep
the critique file untouched as audit trail.

### Step 5 — write the artifact

Pick the shape skeleton below. Constraint: produced artifact stays
< 200 lines. House style: terse, opinionated, ALWAYS/NEVER, no
marketing prose, no emoji.

**Critique checkpoint 2 (post-write).** Before declaring step 5 done,
re-read and verify:

- the ALWAYS / NEVER rules from the methodology actually appear in
  the artifact (they tend to get summarised away)
- the artifact addresses every operational failure mode the critique
  identified, not just the methodological ones
- the shape skeleton was followed (no missing sections)

If thin or off-pattern, send to `oracle` for a focused second pass.

### Step 6 — dogfood (gating step, not a smoke test)

Run the new artifact end-to-end on the originating task. Verify:

1. Every output the artifact CLAIMS to produce actually landed.
2. If subagents were used, they WROTE — not just RAN. Read the
   produced files; never trust subagent success summaries alone.
3. The artifact survived a long-running fan-out without losing work.
4. Operational ambiguities (write timing, fan-out width, salvage,
   ownership) did not surface.

**Critique checkpoint 3 (dogfood-as-critique).** Dogfood IS critique
against reality. If anything broke or surfaced ambiguity, send the
v1 artifact + dogfood notes back to `oracle` adversarially: "what
operational rules are still missing? what rules will get smuggled
around in practice?" Patch and re-run.

Operational gaps are where most artifacts fail — methodology errors
are the easy half.

## Shape skeletons (step 5)

Skeletons for all seven shapes live in the sibling file `shapes.md`
next to this SKILL.md. Read it before writing the artifact and pick
one. SKILL.md keeps workflow only; the skeletons are reference
material.

## Rules

- ALWAYS call `oracle` at MULTIPLE checkpoints, not just step 3.
  Adversarial framing on every call.
- ALWAYS keep oracle critique files as audit trail.
- ALWAYS dogfood as a GATING step (verify writes, not just runs).
- ALWAYS main thread owns the final write to `~/.claude/skills/` or
  `~/.claude/agents/` — subagents may be sandbox-blocked from writing
  there.
- ALWAYS require durable intermediate artifacts from subagents.
  NEVER let a subagent put its only write at the end of a long run.
- ALWAYS default to 1–2 subagents. 3+ only with explicit budget for
  contention risk.
- ALWAYS include a salvage rule in the produced artifact: if evidence
  captured but final write failed, run a writer-only recovery pass.
- ALWAYS verify the methodology's ALWAYS / NEVER rules landed in the
  produced artifact — re-read after writing.
- ALWAYS one activity per artifact. NEVER fold two domains into one.
- ALWAYS cite the methodology doc from the artifact.
- ALWAYS pick the shape by REUSE + INVOCATION pattern.
- NEVER skip step 3 oracle.
- NEVER let the produced artifact exceed 200 lines.
- NEVER name artifacts as workflow summaries — ALWAYS a punchy
  compound that says the point (`last30days`, `eye-13yo`).

## Anti-patterns

- **Critique only at step 3.** Bias planted earlier survives.
  Critique threads through.
- **Wrong output shape.** One-off ops procedure minted as skill
  (it's a runbook); reusable persona-driven eval minted as checklist
  (it's a skill).
- **Bloat.** Artifact becomes a generic "do good X" how-to.
- **Validatory oracle.** "Does this look right?" returns blessing,
  surfaces nothing.
- **Critique-doc dead-letter.** Methodology never updated after
  oracle.
- **Two activities, one artifact.** Different triggers — separate
  artifacts.
- **Artifact written from intuition.** No research, no citations —
  that's `wisdom`, not `scavenge`.
- **Dogfood as smoke test.** "Subagents ran successfully" ≠
  "artifacts landed." Verify the writes.

## Reference

This skill was itself scavenged + dogfooded — `eye-13yo` was the first
artifact it produced. The methodology + oracle critiques live under
`<cwd>/docs/<topic>/` per the pipeline above.
