# Close

Step 11 runs these sections in order.

## Commit range

ALWAYS read `git log --format='%an %s%n%b'` over the range: conventional
subjects ≤72 characters, one logical change each, NO `Co-Authored-By` trailer,
detached HEAD. ALWAYS do this before any push — a pushed violation is
permanent, and WISDOM § Git bans amend, force-push and a squash of a pushed
commit.

## PR body

ALWAYS read the open PR's body against `pr-draft` § Format — the cap, no
results, no history — and rewrite it through `pr-draft` when it fails.

## Threads

ALWAYS reply to each step-5 WON'T-FIX thread, and each FIX that step 8
deferred, with the invariant or `BUGS.md` entry it matches, via `gh-comment` —
its distill and review-on-wisdom phases and its sign-off gate. A FIX thread
gets no reply here: ALWAYS list each with its thread id and fix SHA, and show
the PR's own head refspec, `rip -g <fix-sha>:refs/heads/<headRefName>`; resolve
and request re-review through `gh-comment` once that push lands. A bot-authored
thread resolves once replied (`gh-comment` § Resolve a thread). ONLY threads
addressed this pass.

## Worktrees

ALWAYS take one this run created through `worktree` (reconciled, then removed).
For the rest, ALWAYS `git fetch --all` first; an entry of `git worktree list`
after the first (the main tree) is integrated only when `git branch -r
--contains <its HEAD>` prints a ref AND `git -C <path> status --porcelain`
prints nothing — `git worktree remove <path>` those, then `git worktree prune`.
Every other one is unfinished work, this session's or another's: it stays,
listed by path and reason. NEVER `--force` past a refusal, and NEVER read age
or a dead lock as abandonment — integration is the only proof.

## Verdict

ALWAYS state what was settled, what was corrected, what could not be settled
from here and why, and each step-1 instruction's outcome.
