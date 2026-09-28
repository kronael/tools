# What settles a claim

One kind per section: the command that proves it, and the trap that makes an
unproven one look proven. A claim is any sentence in the diff, a commit
subject, an acceptance criterion or a subagent's report that one command
proves or breaks.

## Absence — "there is no X", "nothing references Y", "I can't from here"

Settled by the same query returning a hit where one exists, then re-run with
the access and the scope the answer needs. NEVER rest a design decision, a
document or a subagent brief on an unproven negative.

- **A projection hides what the pattern targets.** `docker ps --format
  '{{.Names}}\t{{.Ports}}' | grep postgres` finds nothing when the image name
  carries the word. ALWAYS grep a field you printed.
- **A failure prints nothing.** A refused SSH fetch, a path that does not
  exist and a ref that does not resolve are all silent; the shell expands a
  glob as YOU before `sudo` runs; the wrapped `grep` excludes `.git`.
- **One branch is not the repository.** A directory holding no `specs/` here
  held eleven on an unmerged branch nine commits old. `git ls-tree -r
  FETCH_HEAD`, `git branch -r`, `git remote -v` in the directory whose name
  you are trusting — and fetch by explicit HTTPS URL where the origin is SSH.
- **A thing is missing where you looked, not where it is kept.** Config in
  `cfg/`, data on the deployment host, a running service behind `sudo`.

## Count — "ten references", "109 of 144 files", "two broken links"

Settled by reading the matches, then re-deriving with a differently shaped
query: by file where the first counted lines, by resolving each target where
the first matched text, by AST where the first grepped.

- **Grep counts mentions; imports need an AST walk.** "109 of 144 test files
  import the module" did not reproduce even at the commit that wrote it — 113
  merely mention the word, 106 import it. The easy query is the one that gets written down.
- `grep -rl | wc -l` counts files, `grep -rn | wc -l` counts lines — say which
  one the claim means, and a bare identifier matches its own prefixes.
- **An acceptance grep narrower than its claim passes while the tree is
  wrong.** A criterion naming ten sites where twenty exist would have let an
  extraction pass with the live deploy still building from the old path. ALWAYS check a
  criterion's coverage with a second query before trusting its exit code.

## Superlative — "the one place", "the only X", "four listeners"

The strongest claims are the least checked, because they read as summary
rather than measurement. Settled by enumerating the whole set.

- ALWAYS list every member before writing "the one" or "the only"; a second
  hand-written deploy handler and two unlisted listeners each sat one listing
  away.
- A structural claim ("three copies of the same loop") is settled by reading
  the file now — the shared helper it asks for may already exist.

## Comparison — "nothing ahead", "no diff", "already merged"

Settled by `git rev-parse --verify` on both ends first, with the branch read
from `git branch -r` rather than assumed. A range that holds nothing and a
range that does not resolve print the same nothing.

## Reference — a relative link, an include, an asset path, a `file:line`

Settled by resolving each one from the directory that holds it, and by opening
the cited line rather than trusting the number. A move invalidates a whole
class at once, so sweep the set; the two that were reported are its visible
edge.

## Measurement — line counts, file counts, versions, table counts

Settled by measuring now. ONE document owns the number and the rest cite it.
A figure copied into a second file drifts silently, and the copies disagree
before anyone notices: one stale line count sat in a spec, an `ARCHITECTURE.md`
and a `README.md` at the same time.

- A document that dates its counts is still wrong when the number was never
  right; ALWAYS re-measure before deciding a figure is merely old.

## Green run — "tests pass", "the type checker is clean"

Settled through the project's own target with the environment that target
exports. The same tool invoked bare reported two errors the project does not
have, in a file the change never touched — a missing `PYTHONPATH` the Makefile
sets. A disagreement between the two is the invocation's fault first.

## Report — "the sub fixed it", "all findings applied"

Settled by the diff: `git show --stat`, then the hunks. A report is upstream
like any document — its counts and its `file:line` citations settle the same
way as a spec's.
