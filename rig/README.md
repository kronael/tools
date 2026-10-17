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

Detached HEAD is safe: reflog keeps all commits for 30 days. If you
lose track, `git reflog` finds everything. No local branches to
maintain, no tracking to configure, no stale branches to clean up.

## Commands

| Command | Symlink | Action |
|---------|---------|--------|
| `rig checkout` / `rig co` | `rco` | Fetch + detached checkout of a ref, tag, hash or origin branch pattern |
| `rig gco` | `gco` | Detached checkout without fetch; `gco [ref] -- paths` restores files |
| `rig push` / `rig p` | `rip` | Push HEAD to origin/branch; `-g` pushes stated refspecs over HTTPS with the `gh` token, the remote stays SSH |
| `rig fetch` / `rig f` | `rif` | Fetch from origin; `-g` fetches from origin's GitHub repo over HTTPS the same way |
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

### Push and fetch with the gh token (rip -g, rif -g)

```bash
rip -g <sha>:refs/heads/20260101_my_topic  # one-off HTTPS push, remote URL untouched
rip -g v1.2.3:refs/tags/v1.2.3              # a tag, the same way
rip -g -n <sha>:refs/heads/x                # print the git command
rip -g -u                                   # print the HTTPS URL
rif -g <branch>                             # read over HTTPS the same way, into FETCH_HEAD
rif -g '+refs/heads/*:refs/remotes/origin/*'   # refresh the tracking refs
rif                                      # plain: git fetch origin
```

The human pushes over SSH with plain `rip`. An agent session often has no SSH
agent (`Permission denied (publickey)`) while `gh auth status` shows a
token, so `rip -g` runs

```
git -c credential.helper= -c 'credential.helper=!gh auth git-credential' \
    -c url.<url>.insteadOf=<url> -c url.<url>.pushInsteadOf=<url> \
    push --no-follow-tags <url> <refspec>...
```

and `rif -g` the same with `fetch`, where `<url>` is
`https://github.com/<owner>/<repo>.git`. `rip -g` reads owner and repo from
origin's push URL (`git remote get-url --push origin`, so a
`remote.origin.pushurl` wins) and `rif -g` from its fetch URL; either may be
`git@github.com:`, `ssh://git@github.com/`, `ssh://git@github.com:<port>/`,
`ssh://git@ssh.github.com:<port>/`, `https://github.com/` or
`https://<userinfo>@github.com/`, and any other form, `GitHub.com` included,
is refused. The two `url.<url>` rules outmatch a `url.<base>.insteadOf` or
`pushInsteadOf` on a shorter base such as `https://github.com/`, so a rewrite
to SSH in the user's config does not catch the HTTPS URL. Neither command
rewrites `remote.origin.url` or stores the token: clones, remotes and
worktrees stay SSH.

A push refspec is `<src>:refs/heads/<branch>` or `<src>:refs/tags/<tag>`:
one colon, a non-empty source and a non-empty name; only the stated tags
travel. With `-g`, both commands refuse `-f`, `--force`, `--force-with-lease`,
`--force-if-includes`, `--tags`, `--all`, `--mirror`, `-d`, `--delete` and any
other flag but `-n`, `-u` (`--url`) and `-h` (`--help`); `rip -g` also refuses a `+`
refspec, a wildcard, a delete (`:<dst>`) and any other destination. `-u` takes no
refspec. `-g` is read as a leading flag, with `-n` in either order (`rip -n -g`).
rig reads its own flags (`-n`, `-g`, `-h`) only while they lead; after another
argument they pass to git (`rif --depth=1 -n` sends `-n` to `git fetch`). Without
`-g`, `rip` pushes and `rif` fetches through git's own `origin`, and `rif` passes its
other arguments to `git fetch origin`. A token without the `workflow` scope cannot
push a change under `.github/workflows` — GitHub refuses the push; report it
rather than working around it.

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
including `rco`, `gco`, `rip`, `rif`, `rir`, `rim`, and the git aliases above.
They dispatch via `basename $0`. Checkout, rebase, and merge share a
`cmd_branch_op` helper; push and fetch have their own handlers, and
`rip -g`/`rif -g` share a third (`cmd_gh_op`). Checkout (`rco`), rebase,
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
