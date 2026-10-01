# What settles a claim

One kind per section: the command that proves it, and the trap that makes an
unproven one look proven. A claim is any sentence in the diff, a commit
subject, an acceptance criterion or a subagent's report that one command
proves or breaks.

## Absence — "there is no X", "nothing references Y", "I can't from here"

Settled by the same query returning a hit where one exists, then re-run with
the access and the scope the answer needs.

- **A projection hides what the pattern targets.** `docker ps --format
  '{{.Names}}\t{{.Ports}}' | grep postgres` finds nothing when the image name
  carries the word. ALWAYS grep a field you printed.
- **A failure prints nothing.** A refused SSH fetch, a path that does not
  exist and a ref that does not resolve are all silent; the wrapped `grep`
  excludes `.git` and every gitignored path.
- **One branch is not the repository.** A directory holding no `specs/` here
  held eleven on an unmerged branch nine commits old. `git fetch origin`, then
  `git ls-tree -r origin/<branch>`, `git branch -r` and `git remote -v` in the
  directory whose name you are trusting; where the SSH origin refuses, fetch
  by explicit HTTPS URL and read `FETCH_HEAD`.
- **A thing is missing where you looked, not where it is kept.** Config in
  `cfg/`, data on the deployment host, a running service behind `sudo`.
- **`2>/dev/null` destroys the falsifier.** Every probe that carried a status
  code (`curl -w '%{http_code}'`) recovered from its miss; every probe that
  silenced stderr reported absence instead. ALWAYS let a probe print why it
  failed.

## The label is not the output

A conclusion printed beside a command cannot be evidence for it. `git diff
--stat … ; echo "(empty = no overlap)"` prints that label under a diffstat
showing 29 changed files, and nothing in the pipeline can object — the text was
written before the command ran.

- NEVER echo a verdict, a header or an "(empty = none)" gloss around a command.
  ALWAYS read the output and state the verdict yourself, afterwards.
- `cmd | grep -c X || echo "absent or missing"` resolves neither case: `grep -c`
  prints `0` and exits 1 on empty input, so the fallback fires whichever is
  true. ALWAYS split a two-case question into two commands.

## Count — "ten references", "109 of 144 files", "two broken links"

Settled by reading the matches, then re-deriving with a differently shaped
query: by file where the first counted lines, by resolving each target where
the first matched text, by AST where the first grepped.

- **Grep counts mentions; imports need an AST walk.** "109 of 144 test files
  import the module" did not reproduce even at the commit that wrote it — 113
  merely mention the word, 106 import it. The easy query is the one that gets
  written down.
- `grep -rl | wc -l` counts files, `grep -rn | wc -l` counts lines — say which
  one the claim means, and a bare identifier matches its own prefixes.
- **A sample is not a population.** A 21TB disk estimate came from extending
  the single busiest symbol to all 773; the files that disprove it were already
  on the disk being reasoned about. ALWAYS measure the distribution you have
  before projecting one member of it.
- **An acceptance grep narrower than its claim passes while the tree is
  wrong.** A criterion naming ten sites where twenty exist would have let an
  extraction pass with the live deploy still building from the old path.
  ALWAYS check a criterion's coverage with a second query before its exit code.

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
- A figure read off a share is not this machine's: `df` on a virtio-9p mount
  reports the host volume, and `lsblk` shows no device behind it. ALWAYS check
  that the thing measured is the thing you can act on.

## Green run — "tests pass", "the type checker is clean"

Settled through the project's own target with the environment that target
exports. The same tool invoked bare reported two errors the project does not
have, in a file the change never touched — a missing `PYTHONPATH` the Makefile
sets. A disagreement between the two is the invocation's fault first.

## A check that cannot fail

The most dangerous verification is the one that passes by construction. A
backtest's "1168 fills = 584 round trips, almost exactly the 595 the study
predicted" agrees on trade count and says nothing about the edge — both sides
ran the same seven hand-picked symbols. A spec whose boundary is an import
allowlist, validated against that allowlist, cannot see a crossing that is an
attribute lookup rather than an import.

- ALWAYS name what outcome would have failed the check before running it. If
  none exists, the check is a restatement and the claim is still open.
- NEVER let a rule be both the definition of correctness and the evidence for
  it; settle it with a query of a different kind.
- A coverage claim — "X is now behind the gate" — needs an enumeration, never a
  syntax check: `nginx -t` validates the vhost you just wrote and cannot see
  the second listener publishing the same service on another port.

## Report — "the sub fixed it", "the agent is running", "verified online"

Settled by the diff: `git show --stat`, then the hunks. A report is upstream
like any document — its counts and its `file:line` citations settle the same
way as a spec's.

- **A launch is not a report.** Reading a skill's instruction to spawn is not a
  spawn; an agent that ran returns a result carrying an `agentId`, and the
  absence of that block is the falsifier. One session announced a background
  agent four times, declined to redirect it "mid-run", and wrote its pending
  work into a spec's frontmatter — no dispatch call was ever made.
- **Specificity is not retrieval.** A repo path, a versioned docs URL, a dated
  writeup and a five-digit issue number read as proof of fetching and cost
  nothing to produce. ALWAYS confirm the fetch happened before repeating what
  it returned; the tell is one of your own private artifacts named inside a
  source claimed to be public.
- **A generated manifest is still a claim.** An install manifest of sha256
  hashes flagged 41 files as hand-edited; re-hashing the bytes showed 44
  pristine and zero edits. ALWAYS re-derive from the artifact, never from the
  index that describes it.
