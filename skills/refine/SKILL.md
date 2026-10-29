---
name: refine
description: Finalize a change before it is called done — the code good and every claim it makes true. NOT for a targeted fix (use improve) or a second opinion (use oracle).
when_to_use: "refine this, polish this, final pass before shipping, finalize the PR, settle the claims, is that actually true, verify the numbers, the subagent says it is done, run the acceptance criteria, clean up the diff"
user-invocable: true
---

# Refine

Refine runs in main context. It audits the whole scope, selects context reviews,
verifies findings and applies confirmed fixes. Contexts are aspects such as
code, deployment, specs or data; documents also carry claims to verify.
`release` uses this same audit before version bumps.

## Workflow

1. **Settle the ask** — ALWAYS read `intent.md`. Resolve each noun against the
   tree: branch, directory, product, document or host. When measurements differ
   from the user's numbers, ALWAYS check the referent before correcting them.
   List every separate instruction, including those you will not carry out;
   each gets a verdict by step 11.
   → every noun resolves to a path, ref or record; every instruction is listed.

2. **Checkpoint and validate** — uncommitted changes → `Skill(commit, "chore:
   Checkpoint before refine")`. Then build and test through the project's own
   target; fix failures before reviewing anything.
   → `git status --porcelain` is empty and the test target exits 0 in this turn.

3. **Range and claims** — with a PR: `gh pr view --json
   baseRefName,headRefName,headRefOid`, `git rev-parse --verify` both ends,
   `git diff --stat <base>...<head>`. ALWAYS take the base from the PR and the
   branch from `git branch -r`; NEVER type `origin/master` from habit — a ref
   that does not resolve and a range holding nothing print the same nothing.
   `git diff --name-only <base>...<head> | cut -d/ -f1 | sort -u`: a top-level
   directory outside the PR's component with no reason in the ask is a
   drive-by finding (`code.md` § System changes); `software.md` § Changes the
   ask cannot explain carries the per-file, added-`.md` and line-count hunts.
   List assertions with their `file:line`: counts, absence/universality claims,
   links, acceptance and commit subjects. `claims.md` owns their verification.
   → the range resolves and every assertion carries its `file:line`.

   ALWAYS run mechanical checks per `astgrep` → `lints.md` § Refine, and repeat after fixes at step 10.

3.5. **Whole-change audit** — ALWAYS dispatch one fresh read-only audit of the
   complete scope: the bug and fix, the plan and its implementation, or the
   release range. Select the audit task through `dispatch`; provider runbooks
   own the launch. NEVER use a same-model inline shortcut for this pass.
   The audit checks intent, acceptance gaps, cross-context behavior and systemic
   risks. It returns findings and the required context review depth.
   ALWAYS record the audited snapshot, scope and evidence in the existing work
   record. Reuse it for the same snapshot and scope; NEVER
   add a duplicate broad audit. Confirmed fixes receive targeted verification;
   a material scope or contract change requires a new audit of the affected
   whole. ALWAYS settle audit findings in step 7 before applying them.
   → one whole-scope audit has evidence, and its depth sizes the context reviews.

4. **Contexts** — use the audit's depth to select ≤4 contexts, one per command family —
   what resolves references, what counts occurrences, what deploys, what the
   type checker reads — NEVER one per directory. Every changed path and every
   claim lands in exactly one. A code context also carries language lenses: map
   its files to their skills (`.rs`→`rs`, `.tsx`→`tsx`, `programs/**`→`solana`,
   plus every skill those require), `Skill(<matched>)` each so its cold rules
   are in context, and read the `<skill>.md` lens in this directory — list the
   directory, NEVER assume which exist. A document context (`docs/**`,
   `README.md`, `ARCHITECTURE.md`) reads the `readme.md` lens here beside the
   `claims.md` sections that apply. ALWAYS hand each context the chunks of the
   live WISDOM that govern it — NEVER a frozen checklist. A validation gate a
   lens names that the test target misses (a typecheck) runs once the lens is
   read, and again at step 10. ALWAYS seed the correctness lenses from
   `defaults.md`. Tag each lens `simplify` (reuse, dead code,
   minimisation, a new path grown beside an old one the change should have
   changed or deleted, cross-boundary leaks and coupling between packages) or
   `correctness` (bugs, logic errors, edge cases). `contexts.md` carries the
   recurring contexts and what each one's sub must be handed; `py.md`, `sql.md`,
   `ts.md` and `tsx.md` carry the per-language lenses, `software.md` the
   `code.md` lens every code context reads.
   → every path and claim sits in exactly one context, and each context names
   its lenses and its command family.

5. **Threads** — find the open PR for this work: the one whose head is an
   ancestor of HEAD (`gh-comment` § Setup, which also covers `GH_TOKEN` when
   `gh auth status` fails). None → skip silently. Fetch UNRESOLVED threads
   via `gh-comment` § Fetch threads. Triage each FIX or WON'T-FIX against the
   live WISDOM, the project `CLAUDE.md` invariants and `BUGS.md`. A documented
   invariant or a `BUGS.md` by-design entry is WON'T-FIX. Automated reviewers
   skew false-positive: ALWAYS verify the premise against the code. An
   out-of-scope core-logic change is flagged, never applied. FIX items fold
   into the context that owns their path. A thread the owner wrote is an
   instruction, resolved or not: ALWAYS read every owner comment on the PR
   before settling a finding, and NEVER rule one WON'T-FIX against a plan or
   a reviewer — the plan yields.
   → every unresolved thread carries a verdict and a reason.

6. **Dispatch reviews** — ALWAYS read `brief.md` before the first brief.
   Select one fresh read-only review worker per required context through
   `dispatch`, for both tags. ALWAYS obey its capacity limits and queue when
   needed. Provider skills own native/CLI selection and explicit overrides.
   NEVER let a same-model shortcut replace a required fresh reviewer.
   For a small change, the whole-change audit can cover every context without
   separate review workers; ALWAYS record that coverage explicitly.
   A context worker reviews its assigned context itself; NEVER delegate that
   same review again. A context without a tag runs as `correctness`.
   The subs report findings with commands and outputs and NEVER edit.
   ALWAYS leave a context's files alone in main context until its sub returns.
   → every context has evidenced findings or explicit coverage by the audit.

7. **Settle the reports** — re-derive each finding here with a DIFFERENTLY
   SHAPED query than the sub used: by file where it counted lines, by resolving
   a target where it matched text, by AST where it grepped. A count is settled
   by reading the matches. An absence is settled only once that same query has
   returned a hit where one belongs. A capable model narrows a query as readily
   as a cheap one, so which model wrote a report says nothing about it.
   → each finding is confirmed, corrected with the command that corrected it,
   or dropped as unverifiable.

8. **Triage and apply** — DROP a finding that targets unused code (grep first),
   conflicts with the ask, or survived step 7 only as
   an assertion. A survivor needing a redesign goes to `BUGS.md` as `proposed`
   (WISDOM § Bug triage); NEVER build one without sign-off. A lint, type or
   formatter failure is fixed here, NEVER recorded.
   ALWAYS apply code findings under `software/code.md` § Boring code. Apply
   serially, one context at a time, briefed from `brief.md`.
   ALWAYS select confirmed refinement edits as coding through `dispatch`.
   An unresolved design choice returns to planning or spec before coding.
   Claude workers load `improve`; Codex briefs follow `dispatch` § Brief.
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

10. **Document and commit** — ALWAYS dispatch the docs round through `readme`
    → `sync.md` § Where it runs, with what changed, one line per file. The worker
    reconciles `README.md`, and `ARCHITECTURE.md`/`CLAUDE.md` where the project
    keeps them, against what the code now does. ALWAYS push every
    measurement corrected in step 7 into every document that repeats it — a
    number left standing in a second file is the next pass's false premise.
    Then final build and test, and `Skill(commit, "refa: Apply refinements")`
    when a file changed — NEVER skip that commit otherwise.
    → docs name every changed behaviour, tests pass in this turn, tree is clean.

11. **Close** — `git log --format='%an %s%n%b'` over the range: conventional
    subjects ≤72 characters, one logical change each, NO `Co-Authored-By`
    trailer, detached HEAD. ALWAYS do this before any push — a pushed
    violation is permanent, and WISDOM § Git bans amend, force-push and a
    squash of a pushed commit. ALWAYS read the open PR's body against
    `pr-draft` § Format — the cap, no results, no history — and rewrite it
    through `pr-draft` when it fails. Reply
    to each step-5 WON'T-FIX thread, and each FIX that step 8 deferred, with the
    invariant or `BUGS.md` entry it matches, via `gh-comment` — its distill and
    review-on-wisdom phases and its sign-off gate. A FIX thread gets no reply
    here: list each with its thread id and fix SHA, and show the PR's own head
    refspec, `rip -g <fix-sha>:refs/heads/<headRefName>`; resolve and
    request re-review through `gh-comment` once that push lands. A bot-authored
    thread resolves once replied (`gh-comment` § Resolve a thread). ONLY threads
    addressed this pass. Then the worktrees: one this run created goes by
    `worktree` (reconciled, then removed). For the rest, `git fetch --all`;
    an entry of `git worktree list` after the first (the main tree) is
    integrated only when `git branch -r --contains <its HEAD>` prints a ref
    AND `git -C <path> status --porcelain` prints nothing — `git worktree
    remove <path>` those, then `git worktree prune`. Every other one is
    unfinished work, this session's or another's: it stays, listed by path
    and reason. NEVER `--force` past a refusal, and NEVER read age or a dead
    lock as abandonment — integration is the only proof. Then a
    verdict: what was settled, what was corrected, what could not be settled
    from here and why, and each step-1 instruction's outcome. NEVER push by
    any command (`git push`, `rip -g`) outside the confirmed set (WISDOM
    § Git), and NEVER `gh pr merge` or `gh pr review`. The closing report
    follows `report.md`.
    → the verdict carries all four, every unfixed triaged thread is replied to
    and every fixed one listed, and every worktree left is named with its
    reason.

## Review Checklist

- ALWAYS scale review depth to the change: a small bug gets one scope-sized
  audit and only necessary context reviews. NEVER skip its whole-change audit.
  Release uses that same pass over its complete release range.
- NEVER report a number without reading what it counted, and NEVER take the
  second number from the shape that produced the first.
- ALWAYS ask the redesign question before polishing when the code shows one of
  three signals: a local closure or helper that only builds an error from an
  input, the same parse or validation repeated at several call sites, or an
  `expect`/`panic` on a state the types allow but "cannot happen". Each says the
  interface sits at the wrong layer: parse at the boundary into a type that
  cannot hold the bad state.
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
- ALWAYS delegate refinement edits through the coding route and `improve`;
  NEVER do the improvement work in main context. Provider runbooks own
  native and cross-provider CLI launches.
- A language lens lives at `<skill>.md` in this directory, named for the skill
  step 4 matched — adding the file is the whole registration. One lens per `##`
  heading, each ending in its tag so step 6 can assign the relevant hunts.
  NEVER copy write-time rules into a lens; it carries only the refine hunts.
