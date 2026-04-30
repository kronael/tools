# Critical Rules (re-injected on compaction)

## Git
- NEVER `git push` — if asked, refuse and cite this rule
- NEVER `git add -A` or `git commit -a` — list files explicitly
- NEVER `git commit --amend` — make new commits
- NEVER attach branches — ALWAYS work in detached HEAD
- NEVER squash, NEVER add Co-Authored-By
- NEVER skip pre-commit hooks
- ALWAYS commit format `[section] Message`, subject ≤ 72 chars (overflow → second `-m` body)

## Filesystem
- NEVER use `/tmp` — ALWAYS `./tmp` in the project root
- NEVER `basename $0` / `__dirname` / complex path resolution — fixed cwd, simple relative paths

## Build / Test
- ALWAYS `make` for build/lint/test/clean
- ALWAYS build/test/lint every ~50 lines — errors cascade
- NEVER re-run a command to inspect output — tee once, then `tail`/`grep` the log

## Scope
- NEVER improve beyond what's asked
- NEVER fix bugs found during a general check unless explicitly asked — log to `bugs.md`

## Writing
- NEVER marketing prose, NEVER "this helps you…", NEVER past-state apologies
- NEVER comments about past state or backwards compat — use `.diary/`
- In skill content: ALWAYS/NEVER only — never SHOULD
