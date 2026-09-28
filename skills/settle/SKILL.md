---
name: settle
description: Settle what a pull request asserts against the tree before it is called finished — per-aspect read-only subagents, every finding re-derived in main context. NOT for code-quality polish (use refine) or producing a review (use review).
when_to_use: "before I call the PR done, finalize the PR, settle the claims, is that actually true, verify the numbers, check the counts and the cross-references, the subagent says it is done, run the acceptance criteria, prove it rather than assert it, docs-only PR, spec PR"
user-invocable: true
---

# Settle

Runs in main context so the whole conversation stays visible. The unit of work
is a **claim**: a sentence in the diff, a commit subject, an acceptance
criterion or a subagent's report that one command proves or breaks. Settling it
means running that command and reading its output.

`/refine` makes the code good; `/settle` makes what the change says true. A
documents-only PR matches no language lens and still carries claims, so run
this whether or not refine applied.

## Workflow

1. **Range** — `gh pr view --json baseRefName,headRefName,headRefOid`, then
   `git rev-parse --verify` each end. ALWAYS take the base from the PR and the
   branch from `git branch -r`; NEVER type `origin/master` or `origin/main`
   from habit — a ref that does not resolve and a range holding nothing print
   the same nothing.
   → `git diff --stat <base>...<head>` names the files you expect.

2. **Harvest** — read the diff and list every claim with the `file:line` that
   states it: counts, sizes, line numbers, "there is no X", "every Y does Z",
   relative links, acceptance criteria, and the commit subjects. ALWAYS read
   `claims.md` first — it names each kind and the command that settles it.
   → every entry on the list carries its `file:line` and its command.

3. **Aspects** — group the claims into ≤4 aspects, one per command family —
   what resolves references, what counts occurrences, what deploys — never one
   per directory. Each claim lands in exactly one aspect.
   → no claim sits in two aspects and none sits in none.

4. **Dispatch** — one read-only subagent per aspect, each brief written from
   `brief.md`; ALWAYS read that file before writing the first brief. The subs
   report findings and never edit. ALWAYS leave an aspect's files alone in main
   context until its sub returns.
   → every aspect has returned findings with commands and outputs attached.

5. **Settle the reports** — re-derive each finding here with a differently
   shaped query than the sub used: by file where it counted lines, by resolving
   a target where it matched text. A count is settled by reading the matches.
   An absence is settled only once the same query has returned a hit somewhere
   it should. A capable model narrows a query as readily as a cheap one, so the
   model that produced a report says nothing about the report.
   → each finding is confirmed, corrected with the command that corrected it,
   or dropped as unverifiable.

6. **Acceptance** — run every command the changed documents state as their own
   acceptance, exactly as written, and read the matches rather than the exit
   code. A criterion whose command misses a live site is a defect in the
   criterion; fix the criterion, not the count.
   → every acceptance command in the diff has been run in this turn.

7. **House rules on the change itself** — `git log --format='%an %s%n%b'` over
   the range: conventional subjects ≤72 characters, one logical change each, no
   `Co-Authored-By` trailer, detached HEAD, no worktree left behind. ALWAYS do
   this before the push — afterwards amend, squash and force-push are all
   barred and the violation is permanent.
   → the range is clean, or each violation is named with its SHA and whether a
   remedy exists.

8. **Close** — apply what is a single edit, file anything needing a redesign in
   `BUGS.md` as `proposed`, and give a verdict counting what was settled, what
   was corrected and what could not be settled from here and why. NEVER
   `git push`, `gh pr merge` or `gh pr review`.
   → the verdict carries all three counts and the tree is clean.

## Review Checklist

- ALWAYS scale to the change: a handful of claims settles inline; NEVER fan out
  agents over a diff that asserts three things.
- NEVER read an empty result as a finding until that query has produced a
  non-empty one where one belongs.
- NEVER report a number without having read what it counted, and NEVER take the
  second number from the shape that produced the first.
- ALWAYS let one document own a measurement and have the rest cite it; a number
  copied into a second file has already begun drifting from the tree.
- ALWAYS run a check through the project's own target with the environment that
  target exports; a bare invocation's errors belong to the invocation.
- ALWAYS open the diff behind a subagent's report before acting on it.
- NEVER edit a file while a sub is reading it, and NEVER run two writing subs on
  one tree.
