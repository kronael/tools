# CTO code audit

Pass criterion: **would I bet my SLA on this code as it stands today?**
Output: numeric grade 0-100 + ship/hold/rework call.

## Required deliverables

### 1. Verify at least five load-bearing claims

For each: claim text, source (file:line or doc), method (grep / read / fresh
bench), verdict (CONFIRMED / DISPUTED / UNVERIFIABLE), and evidence.

Choose claims that would embarrass the team if false:

- "Zero heap on the hot path" — grep for `Vec::new`, `Box::new`, `clone`,
  and allocator paths in hot-loop files.
- "One CRC per record" — trace encode paths and count CRC compute sites.
- "X us round-trip" — re-run the bench and compare to the claim.
- "Y retention" — verify actual time/file-age GC behavior.
- "Test count" — re-run and compare README, blog, MEMORY, and code surfaces.

Do not confirm by re-reading the same doc. Verify against code or fresh output.

### 2. Trace three attack scenarios

For each: describe the attack, trace from entry point through code to where it
is caught or missed, and cite file:line. Useful categories:

- Malicious peer on a trusted network.
- Crash + restart with partial state.
- Sustained-loss / NAK-storm class bugs.
- Replay against tokens or sequence numbers.
- Pathological input: many cancels, malformed framing, attacker-controlled
  loop bounds.

### 3. Grade honestly

Grade `X / 100` for "would I bet my SLA on this today?" Justify in two or
three sentences. Below 50 means rewrite a subsystem before shipping. Above 80
means ready for a friendly first customer.

### 4. Spot-check recent sprint work

For each recent round/phase, sample one commit and verify it is sound. Did the
cut actually cut, or just relocate? Did the refactor preserve behavior? Did the
spec sync update reality or wishes?

## Constraints

- Source-and-bench reads only. NOT an end-to-end demo audit (`ceo-eval` owns that).
- Don't write code, don't commit fixes. Findings only.
- Cite file:line for every claim.
- Don't run the full benchmark suite; pick the 3-5 benches tied to claims.
- Don't grade-inflate. Don't fabricate gotchas.

## Output

`<wherever the sprint dir is>/CTO-REPORT.md` with claims, attack scenarios,
grade, sprint spot-checks, and one-sentence call.

Pattern references: `.ship/20-CTO-CEO-REVIEW-2/CTO-REPORT.md` and
`.ship/27-REFINE-AUDIT/CTO-REPORT.md`.

## Anti-patterns

- Re-reading docs and pronouncing them correct.
- Bullet lists of "things to consider" with no verdict.
- CONFIRMED claims without grep / bench evidence.
- Grade above 70 with critical findings unaddressed.
- Grade below 40 without naming the subsystem that needs rewriting.
