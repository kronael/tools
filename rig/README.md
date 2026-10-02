# rig - ripgit

Lightweight git tools for upstream-only, detached HEAD workflows.

![rig demo](demo/demo.gif)

## Rationale

**rig optimizes for MAX INFLOW** - getting commands INTO the computer
fast.

Git TUIs (LazyGit, GitUI, tig) are OUTPUT-focused: they help you
*view* and *explore*. **rig is INPUT-focused**: minimal keystrokes,
no screen takeover, single purpose, returns control immediately.

For exploration, use **magit**. For input speed, use **rig**.

## Detached HEAD Workflow

rig is designed for upstream-only branches. You never create local
branches - you work directly on detached HEAD from origin:

```bash
rco feature         # fetch + checkout origin/feature (detached)
# ... make changes, commit ...
rip feature         # push HEAD to origin/feature
rco main            # fetch + detach at origin/main, even with a local main
rim feature         # fetch + merge origin/feature into current
rip main            # push result to origin/main
```

**Rebase before push** (clean history):

```bash
rco feature         # fetch + checkout origin/feature (detached)
# ... make changes, commit ...
rir main            # fetch + rebase -i on origin/main
rip feature         # push rebased HEAD to origin/feature
```

Detached HEAD is safe: reflog keeps all commits for 90 days. If you
lose track, `git reflog` finds everything. No local branches to
maintain, no tracking to configure, no stale branches to clean up.

## Commands

| Command | Symlink | Action |
|---------|---------|--------|
| `rig checkout` / `rig co` | `rco` | Fetch + detached checkout of a ref, tag, hash or origin branch pattern |
| `rig gco` | `gco` | Detached checkout without fetch; `gco [ref] -- paths` restores files |
| `rig push` / `rig p` | `rip` | Push HEAD to origin/branch |
| `rig rebase` / `rig r` | `rir` | Fetch + rebase -i origin/branch |
| `rig merge` / `rig m` | `rim` | Fetch + merge origin/branch |

**Selection flags**: `-n` dry-run, `?` force fzf.
`rco`, `rir`, and `rim` also accept `-z` offline (no fetch); `gco` never fetches.

## Git aliases

These git shortcuts are symlinks and work in every shell with the install directory on PATH.
Arguments pass through to git; `gib` takes listing options and branch name patterns.
It lists local and remote branches by default; `gib -r` lists only remote branches.

| Symlink | Equivalent |
|---------|-----------|
| `gl` | `git log --oneline -20` |
| `gis` | `git status -uno` |
| `gig` | `git log --graph --oneline --simplify-by-decoration --all --decorate` |
| `gitg` | `git log --graph --oneline --all --decorate` |
| `gp` | `git cherry-pick` |
| `gpc` | `git cherry-pick --continue` |
| `gpa` | `git cherry-pick --abort` |
| `gw` | `git worktree` |
| `gif` / `gifs` | `git diff` / `git diff --staged` |
| `gss` / `gsp` / `gsl` | `git stash` / `git stash pop` / `git stash list --stat` |
| `grec` / `grea` / `gres` | `git rebase --continue` / `git rebase --abort` / `git rebase --skip` |
| `gib` | `git branch --all [arguments...] --list` |
| `gitsu` | `git status` |

## Dependencies

- git
- fzf

## Installation

```bash
cd rig
make install
```

Installs `rig` + all symlinks to `~/.local/bin/`.

## Usage

### Checkout (rco / gco)

```bash
rco apm           # Fetch + checkout best match for "apm"
rco -z apm        # Offline: checkout without fetching
rco -n apm        # Dry-run: show which branch matches
rco ?             # Force interactive fzf selection
rco               # Open fzf, type to filter, Enter to checkout
rco HEAD~2        # Fetch + detach at a commit
rco v1.0          # Fetch + detach at a tag
gco abc1234       # Detach at a hash without fetching
gco local-name    # Detach at a local branch if origin has no matching name
gco refs/heads/main # Detach at the local main explicitly
gco -             # Return to the previous checkout, detached
gco -- file       # Restore a file from the index
gco HEAD~2 -- file # Restore a file from a commit without moving HEAD
gco --ours -- file # Restore our side of a conflicted file
```

Both commands always detach when checking out a commit or branch.
They refuse `-b`, `-B`, `-c`, `-C`, `--track`, `-t`, and `--orphan`.
They never create local branches or set an upstream.
Branch patterns select `origin/<branch>` through fzf; remote-tracking refs stay intact.
An unqualified name shared by local and origin branches selects origin.
`HEAD` means the current commit; `origin/HEAD` is excluded from branch selection.
`rco` fetches origin branches into `refs/remotes/origin/*`, ignoring configured
fetch mappings; tags follow normally. `gco` uses only refs available locally.
Restore options `--ours`, `--theirs`, `-p`/`--patch`, `-m`/`--merge`, and
`--conflict=<style>` require `gco [ref] [restore-options] -- paths`.

### Push (rip)

```bash
rip               # Push HEAD to auto-detected branch (or fzf if ambiguous)
rip my-branch     # Push HEAD to origin/my-branch
rip branch:abc123 # Push specific commit
rip -n            # Dry-run
rip ?             # Interactive branch selection
rip my-branch -f  # Force push (flags forwarded to git push)
```

In detached HEAD (the normal workflow), `rip` auto-detects the branch by
walking first-parent ancestry until it finds a commit with a remote ref.
Stops at merge commits (ambiguous parentage) and falls back to fzf
selection when detection fails.

### Rebase (rir)

```bash
rir main          # Fetch + rebase -i on origin/main
rir -z main       # Offline: rebase without fetching
rir -n main       # Dry-run
rir ?             # Interactive branch selection
```

### Merge (rim)

```bash
rim main          # Fetch + merge origin/main
rim -z main       # Offline: merge without fetching
rim -n main       # Dry-run
rim ?             # Interactive branch selection
```

## How It Works

Single busybox-style script. `rig aliases` lists every installed symlink,
including `rco`, `gco`, `rip`, `rir`, `rim`, and the git aliases above.
They dispatch via `basename $0`. Checkout, rebase, and merge share a
`cmd_branch_op` helper; push has its own handler. Checkout (`rco`), rebase,
and merge fetch by default; `-z` suppresses fetch. `gco` never fetches.
`rig install` owns the symlink list; `make install` delegates to it.

Branch detection (`get_current_branch`):
1. `git symbolic-ref --short HEAD` (attached HEAD)
2. Walk first-parent ancestry, check each commit for a remote ref (detached HEAD)
3. Stop at merge commits (ambiguous parentage)
4. Fail with error if no remote ref found — `cmd_push` falls back to fzf

Branch selection pipeline:
1. Recent branches from reflog (last 50)
2. All branches sorted by commit date
3. Normalize names, keep existing origin branches, and dedupe
4. Pipe to fzf for fuzzy matching

## Tests

`make test` checks syntax and runs `test.sh` against a temporary local origin.
No network or TTY is required. Set `RIG=/absolute/path/to/rig` to test another copy.
