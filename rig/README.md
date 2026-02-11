# rig - ripgit

Lightweight git tools for upstream-only, detached HEAD workflows.

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
rio feature         # fetch + checkout origin/feature (detached)
# ... make changes, commit ...
rip feature         # push HEAD to origin/feature
rio main            # fetch + checkout origin/main (detached)
rim feature         # fetch + merge origin/feature into current
rip main            # push result to origin/main
```

**Rebase before push** (clean history):

```bash
rio feature         # fetch + checkout origin/feature (detached)
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
| `rig checkout` / `rig co` | `rio` | Fetch + checkout origin/branch (detached) |
| `rig push` / `rig p` | `rip` | Push HEAD to origin/branch |
| `rig rebase` / `rig r` | `rir` | Fetch + rebase -i origin/branch |
| `rig merge` / `rig m` | `rim` | Fetch + merge origin/branch |

**Shared flags**: `-z` offline (no fetch), `-n` dry-run, `?` force fzf

## Dependencies

- git
- fzf

## Installation

```bash
cd rig
make install
```

Installs to `~/.local/bin/`.

## Usage

### Checkout (rio)

```bash
rio apm           # Fetch + checkout best match for "apm"
rio -z apm        # Offline: checkout without fetching
rio -n apm        # Dry-run: show which branch matches
rio ?             # Force interactive fzf selection
rio               # Open fzf, type to filter, Enter to checkout
```

### Push (rip)

```bash
rip               # Push HEAD to current branch on origin
rip my-branch     # Push HEAD to origin/my-branch
rip branch:abc123 # Push specific commit
rip -n            # Dry-run
rip ?             # Interactive branch selection
rip my-branch -f  # Force push (flags forwarded to git push)
```

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

Single busybox-style script. Symlinks (`rio`, `rip`, `rir`, `rim`)
are detected via `basename $0` and dispatched to the matching
subcommand. All commands fetch by default; `-z` suppresses fetch.

Branch selection pipeline:
1. Recent branches from reflog (last 50)
2. All branches sorted by commit date
3. Dedupe, strip `origin/` prefix
4. Pipe to fzf for fuzzy matching
