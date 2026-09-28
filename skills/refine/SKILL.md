---
name: refine
description: Finalize a change before it is called done — read-only subagents per context of the project and the change, every claim the change makes re-derived against the tree. NOT for a targeted fix (use improve) or a second opinion (use oracle).
when_to_use: "refine this, polish this, final pass before shipping, tighten this before commit, finalize the PR, before I call the PR done, settle the claims, is that actually true, verify the numbers, check the counts and the cross-references, the subagent says it is done, run the acceptance criteria, docs-only PR, spec PR"
user-invocable: true
---

# Refine

Runs in main context so the whole conversation stays visible.

A change is finished when the code is good AND what it says about the tree is
true. One pass settles both, because both are found the same way: cut the
change into **contexts**, dispatch one read-only subagent per context, re-derive
every finding here. A context is an aspect of the project this change touches —
its deployment, its spec set, its data layer, its agent surface. A language
bucket is ONE KIND of context, never the axis: a documents-only PR matches no
extension and still carries every claim the reviewer will trust.

`/release` is the later gate (version bumps). Run this first.

## Workflow

1. **Settle the ask** — resolve every noun in the request against the tree
   before acting on it: the branch, the directory, the product name, the
   document, the host. ALWAYS read `intent.md` first. When the user's numbers
   disagree with what you measure, the user is naming a different object —
   ALWAYS check the referent before correcting the number. Every separate
   instruction
   in the message goes on a list and gets a verdict by step 11, including the
   ones you will not carry out.
   → each noun resolves to one path, ref or record, and no instruction is
   unaccounted for.

2. **Checkpoint and validate** — uncommitted changes → `Skill(commit, "chore:
   checkpoint before refine")`. Then build and test through the project's own
   target; fix failures before reviewing anything.
   → `git status --porcelain` is empty and the test target exits 0 in this turn.

3. **Range and claims** — with a PR: `gh pr view --json
   baseRefName,headRefName,headRefOid`, `git rev-parse --verify` both ends,
   `git diff --stat <base>...<head>`. ALWAYS take the base from the PR and the
   branch from `git branch -r`; NEVER type `origin/master` from habit — a ref
   that does not resolve and a range holding nothing print the same nothing.
   Then list what the change asserts, each with the `file:line` stating it:
   counts, line numbers, "there is no X", "every Y does Z", relative links,
   acceptance criteria, commit subjects. `claims.md` names each kind and the
   command that settles it.
   → the range resolves and every assertion carries its `file:line`.

4. **Contexts** — cut the change into ≤4 contexts, one per command family —
   what resolves references, what counts occurrences, what deploys, what the
   type checker reads — NEVER one per directory. Every changed path and every
   claim lands in exactly one. A code context also carries language lenses: map
   its files to their skills (`.rs`→`rs`, `.tsx`→`tsx`, `programs/**`→`solana`,
   plus every skill those require), `Skill(<matched>)` each so its cold rules
   are in context, and read the `<skill>.md` lens in this directory — list the
   directory, NEVER assume which exist. ALWAYS seed the correctness lenses from
   **Confessed defaults**. `contexts.md` carries the recurring contexts and what
   each one's sub must be handed.
   → every path and claim sits in exactly one context, and each context names
   its lenses and its command family.

5. **Threads** — find the open PR (`gh pr list`/`view`; `gh auth status` fails →
   `gh-comment` § Setup; a detached worktree has no local branch, so match by
   pushed branch or head SHA). None → skip silently. Fetch UNRESOLVED threads
   via `gh-comment` § Fetch threads. Triage each FIX or WON'T-FIX against the
   live WISDOM, the project `CLAUDE.md` invariants and `BUGS.md`. Automated
   reviewers skew false-positive: ALWAYS verify the premise against the code.
   An out-of-scope core-logic change is flagged, never applied. FIX items fold
   into the context that owns their path.
   → every unresolved thread carries a verdict and a reason.

6. **Dispatch** — one read-only subagent per context, in parallel, each brief
   written from `brief.md`; ALWAYS read that file before writing the first
   brief. Set `model=` by the context's heaviest tag: `simplify` → sonnet,
   `correctness` → opus. The subs report findings with commands and outputs and
   NEVER edit. ALWAYS leave a context's files alone in main context until its
   sub returns.
   → every context has returned findings, each with the command that produced
   it.

7. **Settle the reports** — re-derive each finding here with a DIFFERENTLY
   SHAPED query than the sub used: by file where it counted lines, by resolving
   a target where it matched text, by AST where it grepped. A count is settled
   by reading the matches. An absence is settled only once that same query has
   returned a hit where one belongs. A capable model narrows a query as readily
   as a cheap one, so which model wrote a report says nothing about it.
   → each finding is confirmed, corrected with the command that corrected it,
   or dropped as unverifiable.

8. **Triage and apply** — DROP a finding that adds an abstraction, targets
   unused code (grep first), conflicts with the ask, or survived step 7 only as
   an assertion. A survivor needing a redesign goes to `BUGS.md` as `proposed`;
   NEVER build one without sign-off. Apply the rest with serial
   `Task(agent="improve")`, one context at a time, briefed from `brief.md`.
   Abort a context on a failure.
   → build and test pass after each context, and no two writing subs shared a
   tree.

9. **Acceptance** — run every command the changed documents state as their own
   acceptance, exactly as written, and read the matches rather than the exit
   code. ALWAYS re-derive what each one claims to cover: a criterion whose grep
   names fewer sites than exist lets the change pass while a live path still
   points at the old one. That is a defect in the criterion — fix the criterion.
   → every acceptance command in the diff has been run in this turn and its
   coverage checked against a second query.

10. **Document and commit** — `Task(agent="readme")` with what changed, one line
    per file; it reconciles `README.md`, and `ARCHITECTURE.md`/`CLAUDE.md` where
    the project keeps them, against what the code now does. ALWAYS push every
    measurement corrected in step 7 into every document that repeats it — a
    number left standing in a second file is the next pass's false premise.
    Then final build and test, `Skill(commit, "refa: apply refinements")`.
    → docs name every changed behaviour, tests pass in this turn, tree is clean.

11. **Close** — `git log --format='%an %s%n%b'` over the range: conventional
    subjects ≤72 characters, one logical change each, NO `Co-Authored-By`
    trailer, detached HEAD. ALWAYS do this before any push — afterwards amend,
    squash and force-push are all barred and the violation is permanent. Reply
    to and resolve each step-5 thread via `gh-comment`, citing the SHA or the
    invariant; ONLY threads addressed this pass. `git worktree remove --force`
    each stale worktree under `.claude/worktrees/`. Then a verdict: what was
    settled, what was corrected, what could not be settled from here and why,
    and each step-1 instruction's outcome. NEVER `git push`, `gh pr merge`,
    `gh pr review` or `gh pr create`.
    → the verdict carries all four, and `git worktree list` shows only the main
    tree.

Pass every agent `Intent:` (the user's original words), `Primary:` (files
to modify) and `Context:` (read-only reference) — NEVER a summary of the ask.

## Confessed defaults — hunt these first

Asked in isolation, models name these as their own defaults while being able to
recite the rule against each. Knowing a rule and following it differ; this is
where the gap shows.

- **Errors** — a broad catch that logs and continues; a fallback `None`/`[]`/`0`
  letting callers proceed on bad data; graceful degradation where crashing is
  cheaper than corrupted output; a guard on a path the caller already
  guarantees; a second logging or helper path because the first was never
  grepped for.
- **Scope** — adjacent code tidied unasked; the reported instance patched while
  sibling cases that fail the same way are left.
- **Tests** — mocks stacked until the test proves nothing; the assertion edited
  when a broken test is annoying; a guessed test command reported green.
- **Comments** — a comment above almost every block, half restating the code;
  docstrings added reflexively to a repo that has none; verbose names where the
  repo is terse.
- **Reporting** — done declared on a green run without exercising the path; a
  partial result softened into language that reads complete; a subagent's
  summary repeated without opening its diff.

## Review Checklist

- ALWAYS scale to the change: tens of lines or three assertions → inline, 1-2
  lenses; NEVER fan out agents over a ~40-line diff.
- NEVER report a number without reading what it counted, and NEVER take the
  second number from the shape that produced the first.
- NEVER read an empty result as a finding until that same query has produced a
  non-empty one where one belongs.
- NEVER print a verdict or an "(empty = none)" gloss beside a command — a label
  written before the command runs cannot disagree with it. ALWAYS read the
  output, then say what it showed.
- ALWAYS name what outcome would fail a check before running it; a check that
  cannot fail leaves the claim open.
- ALWAYS let one document own a measurement and have the rest cite it; the same
  figure written into a second file drifts from the tree silently.
- ALWAYS run a check through the project's own target with the environment that
  target exports; a bare invocation's errors belong to the invocation.
- ALWAYS open the diff behind a subagent's report before acting on it, and
  NEVER report a sub as running without the `agentId` its launch returned.
- ALWAYS delegate the edit to the improve agent; NEVER do the improvement work
  in main context.
- NEVER edit a file while a sub is reading it, and NEVER run two writing subs on
  one tree.
- ALWAYS route a critique, plan or creative second opinion to `oracle` instead.
- A language lens lives at `<skill>.md` in this directory, named for the skill
  step 4 matched — adding the file is the whole registration. One lens per `##`
  heading, each ending in its own tag so step 6 can set `model=` without
  re-reading the code. NEVER copy write-time rules from a language skill into
  its lens; a lens carries only what a refine pass goes hunting for.
