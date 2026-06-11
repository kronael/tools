# Critical Rules (re-injected on compaction)

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

## Tasks
- NEVER leave a task incomplete — finish it or report the exact blocker
- ALWAYS resume unfinished prior-session work surfaced by recall — NEVER restart or guess
- ALWAYS recall (`/resolve` or `/recall-memories`) on a new task before claiming you lack context
- NEVER take commits or hard-to-reverse actions when direction is ambiguous — ask one clarifying question first
