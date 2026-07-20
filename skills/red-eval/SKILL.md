---
name: red-eval
description: Deep adversarial engineering evaluation — correctness, failure modes, exploitability, and "no bullshit" source review. NOT for routine refinement (use refine) or high-level production readiness (use cto-eval).
when_to_use: "red eval, red-team review, adversarial code review, deep developer eval, no bullshit review, find what breaks, failure-mode audit, exploitability review, security-minded code audit"
user-invocable: true
---

# Red Eval

Deep adversarial developer evaluation. Goal: find the thing that breaks the
system, embarrasses the claim, corrupts state, loses money, or makes the demo
lie.

This is **not** a generic security-audit wrapper. Use the platform/security
audit skill for standard web/appsec checklist work. Red Eval is for hard
source-level attack thinking across correctness, operations, protocols,
durability, and exploitability.

## Positioning

- `refine` applies fixes through review/apply loops.
- `cto-eval` answers: would I bet an SLA or adoption decision on this?
- `ceo-eval` answers: would I demo or buy this?
- `red-eval` answers: what breaks if a hostile expert, bad state, or unlucky
  runtime condition hits it?

Red Eval is findings-only by default. Do not fix during the eval. If the user
then asks to address findings, route to `refine` or the relevant language skill.

## Execution

Use one to four focused passes. Prefer separate passes when the project is
large; keep them serial in the main context when the target is small.

1. **Claim busting** - pick the claims that would be costly if false and
   verify from code, tests, fresh output, or logs. For the most valuable
   claim, sketch a quick attack tree (Schneier): the claim's failure at the
   root, OR the paths beneath it, attack the cheapest leaf first — it
   replaces random poking with directed search.
2. **State and durability** - crash/restart, torn/partial writes (crash
   between write, fsync, and rename; fsync-error semantics), replay,
   idempotency, sequence gaps, corruption, migrations, recovery, split-brain
   after partition, leases + clock skew + process pauses (wall clocks and GC
   stalls lie - the Jepsen/Kingsbury canon).
3. **Trust boundaries** - sweep each boundary with STRIDE (spoofing,
   tampering, repudiation, info disclosure, DoS, elevation) as the coverage
   checklist, not the report format: auth/authz, input validation, protocol
   parsing, dependency/supply-chain, secrets, unsafe code,
   shell/database/path edges.
4. **Pressure and abuse** - concurrency, slow consumers, backpressure,
   resource limits, rate limits, infinite retries, queue growth, timeout
   behavior. Walk Deutsch's eight fallacies against every remote call:
   reliable network? zero latency? stable topology? one administrator?

For each pass, report only actionable findings with:

```text
<severity> <file:line> - <finding>
Repro/trace: <how to see it>
Expected: <what should happen>
Observed/risk: <what happens or can happen>
```

Severity: `critical`, `high`, `medium`, `low`, `info`. Calibrate by
reachability × blast radius: `critical`/`high` require a named, reachable
trigger (entry point + preconditions an attacker or unlucky runtime can
actually meet). No reachable path → `medium` at most, filed as hardening.

## Required Checks

- Build or import the relevant target before judging it, unless the failure is
  itself the finding.
- Trace at least three adversarial scenarios end-to-end through source or real
  runtime behavior.
- Verify at least five load-bearing claims when the project makes claims.
- Check whether failures are visible to operators, not just handled internally.
- When the system can run, prefer an injected fault over a source-only
  hypothesis (chaos discipline: state the steady-state expectation first,
  then inject; without an observed deviation it stays a hypothesis).
- Separate confirmed findings from hypotheses. Hypotheses need the next command
  or file that would confirm them.

## Output

Write a concise report in the requested location, or inline if no location is
specified:

```markdown
## Red Eval: <target>

**Verdict:** [PASS / PASS WITH HOLDS / HOLD / REWORK]

### Findings
- ...

### Confirmed Claims
- ...

### Holds Before Release
1. ...
```

## Rules

- Do not duplicate a standard security checklist when a dedicated security
  audit skill is available.
- Do not grade-inflate. If the core claim fails, say so plainly.
- ALWAYS try to DISPROVE each finding via its strongest benign explanation or
  counter-test; NEVER promote it past hypothesis unless disconfirmation fails.
  Every finding needs a this-run trace, repro, or cited source, not memory.
