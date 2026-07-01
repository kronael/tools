# CEO demo audit

Pass criterion: **would I put a friendly first customer on this today?**
Output: numeric grade 0-100 + ready/needs-polish/not-yet call.

## Required deliverables

### 1. Boot the system + verify the demo path

Document the boot sequence. Time cold-start from "start" to ready for first
request. Name every failed process, red health check, and retry storm. If boot
breaks, cite the file, symptom, observed behavior, and log line when available.

### 2. Run the demo flow end-to-end

Run the full happy path a counterparty would see: submit input, watch the side
effect, verify persistence, and verify downstream observables. Time every
endpoint. Flag 5xx, unexpected 4xx, and hangs over 2 seconds.

Be concrete. "The order didn't trade" is weak; "WAL `10_active.wal` is 0
bytes, ME log shows `accepted=0`, marketdata WS emits nothing on direct
subscribe" is useful.

### 3. Inject at least three faults

- Kill a process mid-flow; does the supervisor notice and recover?
- Force a network gap; does recovery actually fire?
- Force a state gap by truncating/corrupting state; does replication catch it?
- Submit malformed input: bad JSON, bad price, bad cid.
- Hit auth boundaries: no token or stolen token.
- Hammer with concurrent requests; observe rate limiting and queueing.

For each: what you did, what happened, what should have happened.

### 4. Produce at least five new findings

Each finding needs repro steps, observed vs expected, and severity
(critical / major / moderate / minor). NEW means absent from prior audit
reports such as `.ship/*/CEO-REPORT.md`; repeated findings are regressions.

### 5. Grade honestly

Grade `X / 100` for "would I demo this today to someone whose opinion matters?"
Below 40 means embarrassing live. Above 70 means you can show it and explain
the gaps honestly.

## Constraints

- Run the actual system. NOT a code review (`cto-eval` owns that).
- Don't fix bugs. CEO finds; the fix sprint fixes.
- Cite file:line for code-related findings and log excerpts for runtime ones.
- Don't grade-inflate. If the core demo action fails, say so.

## Output

`<sprint-dir>/CEO-REPORT.md` with boot, demo flow, faults, findings, numeric
grade, and one-sentence call.

Pattern references: `.ship/20-CTO-CEO-REVIEW-2/CEO-REPORT.md` and
`.ship/27-REFINE-AUDIT/CEO-REPORT.md`.

## Anti-patterns

- "I read the docs and they say it works." Run it.
- "Looks good!" without a timed endpoint or fault injection.
- Potential issues with no repro.
- Grade above 70 when the demo cannot perform its core action.
- Grade below 30 without naming the next three fixes.
