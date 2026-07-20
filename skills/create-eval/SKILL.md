---
name: create-eval
description: Generate a project-specific service-eval skill. NOT for running an existing eval (use service-eval) or adversarial review (use red-eval).
when_to_use: "create eval, create service-eval criteria, scaffold service-eval skill"
user-invocable: true
---

# Create service-eval

Generate `.claude/skills/service-eval/SKILL.md` for the current project.

The service-eval skill runs periodically to read logs, verify
correctness, and generate improvement specs when issues are found. It
is the routine-health pass; for adversarial pre-publication review,
see `cto-eval` (code/operations), `ceo-eval` (demo/business), and
`red-eval` (deep adversarial failure modes).

## Process

1. Read CLAUDE.md, README, specs/, ARCHITECTURE.md, docs/ — AND the
   failure history: BUGS.md, .diary/, incident notes. Past failures
   become the first checks (regression checks beat invented ones).
2. Identify what this project does and what "correct" means —
   invariants first (what must ALWAYS/NEVER hold), metrics second.
3. Ask user: what does "good" look like? What does "best" look like?
4. Ask user about known failure modes
   - Logs: check ops skill, /srv/log, /var/log, or ask
5. ALWAYS derive thresholds from invariants, explicit SLOs, or
   known-good/known-bad evidence; measure the current baseline only
   to test threshold sensitivity. NEVER make today's observed value
   or the user's desired "good/best" answer the threshold — a
   degraded system would define its own degradation as healthy.
6. Write `.claude/skills/service-eval/SKILL.md` with:
   - Log locations and what to grep for
   - Health checks (pass/fail criteria from logs)
   - When to generate improvement specs (to specs/ or .ship/)

## Rules

- NEVER include generic criteria — derive everything from the project
- ALWAYS express assertions as programmatically checkable (grep counts,
  thresholds, exit codes) — NEVER "looks healthy" / "works well"
- Every check = signal source + pass criterion + action-on-fail (what
  spec to generate, where). A check without an action-on-fail is a
  dashboard, not an eval.
- ALWAYS map every known failure mode (asked, or mined from BUGS.md /
  .diary/) to at least one check; a failure mode without a check is a
  named gap in the generated skill, never a silent omission.
- ALWAYS validate both directions before declaring it done:
  (a) run each check against real current logs — no false alarms;
  (b) prove each check CAN fail — run it against a known-bad sample
  (historical incident log, or an injected fault). A check that has
  never fired is unvalidated (mutation-testing logic).
- ALWAYS make the generated eval read-only and time-bounded — an eval
  that mutates service state is a fault injector, not a monitor.
- ALWAYS give the generated skill valid frontmatter (name, description
  with a NOT-for line pointing back at cto/ceo/red evals, when_to_use,
  user-invocable).
