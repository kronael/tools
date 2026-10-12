# The case against building it

Argue the project should not exist. One-sided on purpose — the counterweight
to a review that only hears reasons to build. `eval` gives the full picture
from a named role; this gives one verdict with prior art as its spine. NEVER
blend them: "give me the full picture" is `eval`.

## Memo

Write `critique-useless-<YYYYMMDD>.md` in the record dir — `ship` § Work record
names it. Each step below is one section, in this
order. Findings inside a section rank worst-first.

1. **Verdict** — one line: `don't build`, `build only if <condition>`, or
   `build`. Write it LAST, put it FIRST. A teardown with no verdict is a rant.
2. **Prior art** — the decisive axis, so it leads. One row per shipped
   competitor: live since when, on what, at what price, and what it already
   does that this project only proposes. ALWAYS research online past the
   first hit, and confirm each claim on the competitor's own site or repo
   rather than a search summary; the competitor that kills the project is
   the one nobody in the repo named.
3. **Residue** — prior art subtracted from the project, in one sentence. When
   what is left is thin, say so in those words.
4. **Cost vs payoff** — the project's OWN estimates against the cost of
   adopting the prior art. Add the audit and operations cost of anything novel.
5. **Defect history** — what the bug queue and review record predict about the
   code not yet written.
6. **Operations** — who runs this daily, and why they will not want to.
7. **The strongest counter-argument** — mandatory. The honest best case FOR
   building, and the conditions that make it right. Skipping this makes the
   memo easy to dismiss, which is how a real objection gets ignored.

No code yet — just docs, plans, or an idea? Skip 5, attack the claim instead
of the files.

## Rules

- ALWAYS cite inline — URL, doc, or `path:line`. An uncited claim is noise.
- NEVER invent a defect, benchmark, price, or competitor capability — ALWAYS
  mark what you could not verify as `unverified`. One fabricated hit voids
  the memo.
- ALWAYS read the project's own record first — README, specs, `BUGS.md`,
  the diary. A strawman teardown is worthless.
- ALWAYS concede in one line where the project already answered an objection,
  then say why the answer is not enough. The memo must survive its author.
