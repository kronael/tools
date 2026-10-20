# kvs

A key-value store on one SQLite file for scripts and hooks that run as separate
processes and need shared memory: counters, flags, last-seen values, locks.
Every write is one short transaction in WAL mode, so many processes can write at
once and no update is lost.

## Install

```
make install          # builds dist/kvs and installs $PREFIX/kvs (default ~/.local/bin/kvs)
go run github.com/kronael/tools/kvs@latest --help
```

Needs a Go toolchain; the SQLite driver is pure Go (`modernc.org/sqlite`).

## Scopes

A key lives under a **project** and a **session**.

- **project** — the current directory's main git tree (the first entry of `git worktree
  list`), or the directory itself outside git, slugged the way Claude Code slugs it: every
  character that is not a letter or digit becomes `-`. `-p DIR` picks another directory; `-g`
  selects the global scope shared by every project.
- **session** — `-s ID`, else `$CLAUDE_SESSION_ID`, else none: the key is project-wide.

A hook passes the `session_id` from its input as `-s`. A human runs `kvs ls` in the project and
sees its project-wide keys.

## Commands

```
kvs get KEY                      print the value; exit 1 when absent
kvs set KEY VALUE [-t S] [-i OLD]  write; VALUE "-" reads stdin
kvs incr KEY [N] [-t S]          add N (default 1) to an integer, print the result
kvs del KEY...                   remove keys
kvs ls [PREFIX]                  "key<TAB>value" lines of the scope
kvs sessions                     sessions of the project: "session<TAB>keys<TAB>last write"
kvs lock NAME [-w S] [-n] -- CMD ARGS...   run CMD while holding the lock NAME
```

- `-t`, `--ttl S` — the key expires S seconds after this write. `incr -t` arms the expiry when
  it creates the key, so `incr calls -t 600` counts calls inside a 10-minute window.
- `-i`, `--if OLD` — compare-and-set: write only when the current value equals OLD; an empty OLD
  means "only when absent". Exit 1 when the condition fails.
- `incr` on an absent or expired key starts at 0. A value that is not an integer is an error.
- `lock` takes an OS file lock (`flock(2)`) on `<dir>/locks/<project>/NAME`, runs CMD, and
  releases the lock when CMD exits, also when either process dies. It exits with CMD's exit
  code; `-w S` waits up to S seconds for the lock, `-n` does not wait. A lock that is held
  exits 75. `flock(1)` does the same for a path you name; `kvs lock` names the lock and scopes
  it to the project.

Options: `-p DIR` (project directory), `-s ID` (session), `-g` (global scope), `-h` (help).

## Storage

One database: `$KVS_DIR/kv.db`, where `KVS_DIR` defaults to `$XDG_STATE_HOME/kvs`
(`~/.local/state/kvs`). Lock files live beside it under `locks/`. One file for every project
keeps cross-project queries (`kvs -g ls`, `kvs sessions` per project) in one place and leaves one
WAL to checkpoint; the write rate of hooks is far below what one SQLite file serves.

Expired keys read as absent and are purged on the next write. Values are text; a script that
needs structure stores JSON.

## Exit codes

- 0 — done
- 1 — key absent, or the `--if` condition failed
- 2 — usage error
- 3 — database or lock error
- 75 — `lock`: the lock is held (after `-w` or with `-n`)
- otherwise — the exit code of the command `lock` ran

## Test

```
make test
```

The suite builds `dist/kvs` and runs it from many processes at once: parallel `incr` on one
key loses no update, and parallel `lock` never has two holders.
