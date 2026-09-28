# What settles a claim

One kind per section: the command that proves it, and the trap that makes an
unproven one look proven.

## Absence — "there is no X", "nothing references Y"

Settled by the same query returning a hit where one exists, then re-run with
the access the answer needs. NEVER rest a design decision or a subagent brief
on an unproven negative.

- The wrapped `grep` excludes `.git`; history and secret scans need
  `command grep`.
- A failed fetch, a path that does not exist and a ref that does not resolve
  all print nothing, and the shell expands a glob as you before `sudo` runs.
- What this tree lacks may sit on an unmerged branch, in another checkout of
  the same remote, or behind a privilege: `git ls-tree -r FETCH_HEAD`,
  `git remote -v` in the directory whose name you are trusting, `sudo docker ps`.

## Count — "ten references", "two broken links"

Settled by reading the matches, then re-deriving with a differently shaped
query: by file where the first counted lines, by resolving each target where
the first matched its text.

- A bare identifier matches its own prefixes — anchor it.
- `grep -rl | wc -l` counts files and `grep -rn | wc -l` counts lines; say
  which one the claim means.
- An acceptance grep naming fewer sites than exist lets the change pass while a
  live path still points at the old one.

## Comparison — "nothing ahead", "no diff", "already merged"

Settled by `git rev-parse --verify` on both ends first, with the branch read
from `git branch --show-current` and `git branch -r` rather than assumed.

## Reference — a relative link, an include, an asset path

Settled by resolving every one from the directory that holds it. A move
invalidates a whole class at once, so sweep the entire set; the two that were
reported are the visible edge of it.

## Measurement — line counts, file counts, versions, table counts

Settled by measuring now. ONE document owns the number and the rest cite it;
the same figure written into a second file drifts from the tree silently and
the copies disagree before anyone notices.

## Green run — "tests pass", "the type checker is clean"

Settled through the project's own target with the environment that target
exports. A bare invocation of the same tool reports errors the project does not
have, and a disagreement between the two is the invocation's fault before it is
anyone's.

## Report — "the sub fixed it", "all findings applied"

Settled by the diff: `git show --stat`, then the hunks.
