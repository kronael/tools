---
name: cto-eval
description: CTO-style code audit. Source-and-bench reads, claim verification, attack scenarios, numeric SLA-bet grade. NOT a demo audit (use ceo-eval) or generic code review (use code-review).
when_to_use: "cto audit", "code review at scale", "would I bet SLA on this", verifying load-bearing claims before publishing/shipping, adversarial source-read pass after a refactor sprint
user-invocable: true
---

# cto-eval — adversarial code-and-bench audit

Pass criterion: **would I bet my SLA on this code as it stands today?**
Output: numeric grade 0-100 + ship/hold/rework call.

## Required deliverables

### 1. Verify ≥5 load-bearing claims

For each: claim text, source (file:line or doc), method (grep / read /
re-run bench), verdict (CONFIRMED / DISPUTED / UNVERIFIABLE), evidence.

Pick claims that, if false, would embarrass the team. Examples worth
checking on a perf-sensitive system:
- "Zero heap on the hot path" — grep for `Vec::new`, `Box::new`,
  `clone`, allocator paths in every hot-loop file
- "One CRC per record" — trace the encode path; count CRC compute sites
- "X µs round-trip" — re-run the bench, compare to claim
- "Y retention" — does the code actually do it? Time-based GC? File age?
- "Test count" — re-run, compare across surfaces (README, BLOG, MEMORY)

Don't confirm by re-reading the same doc. Verify against the code or a
fresh bench run.

### 2. Three attack scenarios

For each: describe the attack, trace from entry-point through code to
where it's (or isn't) caught, name file:line where the check holds or
fails. Categories worth thinking about:

- Malicious peer on a "trusted" network (what if trust is wrong?)
- Crash + restart with partial state
- Sustained-loss / NAK-storm class of bugs
- Replay attacks against any token / sequence number
- Pathological input (one user, many cancels; malformed framing;
  attacker-controllable loop bounds)

### 3. Numeric grade

`X / 100` for "would I bet my SLA on this today?"

Justify in two or three sentences. Below 50 = "I'd rewrite a subsystem
before shipping." Above 80 = "ready for a friendly first customer."

### 4. Spot-check recent sprint work

For each round / phase of the recent sprint: sample one commit, verify
the change is sound. Did the cut actually cut, or just relocate? Did
the refactor preserve behavior or just rename? Did the spec sync
update what the code does or what the writer wished it did?

## Constraints

- Source-and-bench reads only. NOT running the system end-to-end (that's
  `ceo-eval`).
- Don't write code, don't commit fixes. Findings → report only.
- Cite file:line for every claim.
- Don't grade-inflate ("looks great!"). Don't fabricate gotchas. If the
  code is genuinely good, say so plainly; if it's bad, name the file
  and the consequence.
- Don't run the full benchmark suite — pick the 3-5 that verify
  specific claims you're checking.

## Output

`<wherever the sprint dir is>/CTO-REPORT.md` with the four sections
above. End with: numeric grade + a one-sentence call ("ship", "hold",
"rework").

## Pattern reference

`.ship/20-CTO-CEO-REVIEW-2/CTO-REPORT.md` and
`.ship/27-REFINE-AUDIT/CTO-REPORT.md` are the canonical examples in
this repo's history.

## Anti-patterns

- Re-reading docs and pronouncing them correct.
- Bullet lists of "things to consider" with no verdict.
- Claims marked CONFIRMED without showing the grep / bench output.
- Grade above 70 with critical findings unaddressed in the rationale.
- Below 40 without naming the subsystem that needs rewriting.
