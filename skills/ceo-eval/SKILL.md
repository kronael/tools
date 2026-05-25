---
name: ceo-eval
description: CEO-style demo audit. Run the system end-to-end, inject faults, time endpoints, find what a first-impression viewer would hit. NOT a code review (use cto-eval).
when_to_use: "ceo audit", "would I demo this", validating a system before showing it to anyone, fault-injection pass on a running deployment, finding bugs the demo would surface
user-invocable: true
---

# ceo-eval — adversarial demo audit

Pass criterion: **would I put a friendly first customer on this today?**
Output: numeric grade 0-100 + ready/needs-polish/not-yet call.

## Required deliverables

### 1. Boot the system + verify the demo path

Document the boot sequence. Time the cold-start from "click start" to
"ready for first request". Note every process that fails to start, every
health check that's red, every retry storm.

If anything in the boot path is broken: name the file, the symptom, what
you saw. Cite log lines verbatim where possible.

### 2. Run the demo flow end-to-end

The full happy path a counterparty would see: submit something, watch
the side effect, verify persistence, verify any downstream observable.
Time every endpoint hit. Note any endpoint that returns 5xx, 4xx (other
than expected), or hangs >2 s.

Be specific. "The order didn't trade" with no detail is useless.
"WAL `10_active.wal` is 0 bytes, ME log shows `accepted=0`, marketdata
WS emits nothing on direct subscribe" is what to write.

### 3. Inject ≥3 faults

Pick at least three:

- Kill a process mid-flow (`pkill -9 <name>`); does the supervisor
  notice + recover?
- Force a network gap (drop packets, restart receiver) — does the
  recovery path actually fire?
- Force a state gap (truncate a log, corrupt a record) — does the
  replication catch it?
- Submit malformed input (bad JSON, bad price, bad cid)
- Hit an auth boundary with no token / a stolen token
- Hammer with N concurrent requests (rate-limit / queueing behaviour)

For each: what you did, what happened, what should have happened.

### 4. ≥5 NEW findings (not in prior audits)

Each: brief description + repro steps + observed vs expected +
severity (critical / major / moderate / minor).

NEW = not in any prior audit report (check `.ship/*/CEO-REPORT.md`
or equivalent). If you're repeating a finding from a prior round,
note explicitly that it's a regression and which prior audit named it.

### 5. Numeric grade

`X / 100` for "would I demo this today to someone whose opinion
matters?"

Justify. Below 40 = "embarrassing in a live demo." Above 70 = "I can
show this and explain the gaps honestly."

## Constraints

- Run the actual system. NOT a code review (`cto-eval` owns that).
- Don't fix bugs. CEO finds; the fix sprint after the audit fixes them.
- Cite file:line for code-related findings; cite log excerpts verbatim
  for runtime findings.
- Don't grade-inflate. The README probably says it's demo-ready; pretend
  you have 30 minutes to make a first impression to a serious
  counterparty. What breaks?

## Output

`<sprint-dir>/CEO-REPORT.md` with the five sections above. End with:
numeric grade + one-sentence call ("ready", "needs polish", "not yet").

## Pattern reference

`.ship/20-CTO-CEO-REVIEW-2/CEO-REPORT.md` and
`.ship/27-REFINE-AUDIT/CEO-REPORT.md` are the canonical examples in
this repo's history.

## Anti-patterns

- "I read the docs and they say it works." — Run it.
- "Looks good!" without a single timed endpoint or fault injection.
- A list of "potential" issues with no repro. Findings need repro steps.
- Grade above 70 when the demo doesn't trade / doesn't ship / doesn't
  function end-to-end. Be honest.
- Below 30 without three concrete fixes the next sprint should
  prioritize.
