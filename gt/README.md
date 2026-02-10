# gt - Git Tools

Collection of lightweight git utilities for faster workflows.

## Rationale

**gt optimizes for MAX INFLOW** - getting commands INTO the computer fast.

Git TUIs (LazyGit, GitUI, tig, etc.) are OUTPUT-focused: they help you *view* and *explore* git state across multiple screens. Great for browsing history, but they optimize for the wrong thing.

**gt is INPUT-focused:**
- **Minimal keystrokes**: `gt b apm` → on correct branch in <1 second
- **Stay in flow**: No screen takeover, no mode switching, no navigation
- **Single purpose**: One command does one thing, executes, returns control
- **Inline selection**: fzf appears, you type, you're done
- **No visual cruft**: Text in, action out, nothing else

Git TUIs solve *exploration* (navigating commits, viewing diffs, understanding history). **gt solves execution** (switching branches, pushing code, getting back to work).

For exploration, use **magit** (emacs) - it delivers what other TUIs attempt but actually works. For input speed, use **gt**.

## Tools

- **gt checkout** (alias: `gt co`, `gco`) - Smart branch checkout with fzf
- **gt push** (alias: `gt p`, `gtp`) - Smart push to origin with auto-detection
- **gt rebase** (alias: `gt r`, `groo`) - Smart interactive rebase on origin branch

## Dependencies

- git
- fzf (for branch switcher)

## Installation

```bash
cd gt
make install
```

Or self-install symlinks from the script itself:

```bash
gt install    # Creates gco, gcoo, gtp, groo symlinks
```

Installs to `~/.local/bin/` (ensure `~/.local/bin` is in your PATH).

## Usage

### Branch Checkout (gt checkout / gt co / gco)

**Interactive mode**:
```bash
gt co             # Opens fzf, type to filter, Enter to checkout
gco ?             # Force interactive (no auto-select on single match)
gco -u            # Fetch updates before showing branches
```

**Non-interactive mode**:
```bash
gco apm           # Auto-selects best match for "apm"
gcoo apm          # Same but fetches first (gco -u)
gt co workers     # Auto-selects "origin/20260127_workers"
gco 0128          # Matches by date pattern
gco -n apm        # Dry-run: show which branch matches
```

**Features**:
- Prioritizes recently checked-out branches
- Strips `origin/` prefix for clean display
- Auto-selects if only one match found
- Pre-filters with your query for multiple matches

### Push to Origin (gt push / gt p / gtp)

**Auto-detect current branch**:
```bash
gt p              # Pushes current branch to origin
gtp ?             # Interactive branch selection with fzf
gt p -n           # Show what would be pushed (dry-run)
gt p -f           # Force push current branch
```

**Explicit branch**:
```bash
gt p my-branch              # Pushes HEAD to origin/my-branch
gt p origin/my-branch       # Same, strips origin/ prefix
gt p refs/heads/my-branch   # Same, strips refs/heads/ prefix
```

**Push specific commit**:
```bash
gt p my-branch:abc123       # Pushes commit abc123 to origin/my-branch
gt p my-branch:HEAD~2       # Pushes 2 commits back from HEAD
```

**With git push flags**:
```bash
gt p my-branch -f                # Force push
gt p my-branch --force-with-lease  # Safe force push
gt p my-branch --set-upstream      # Set upstream tracking
```

### Rebase (gt rebase / gt r / groo)

```bash
groo main         # Fetch + rebase -i on origin/main
gt r main         # Rebase -i on origin/main (no fetch)
gt r -u main      # Fetch first, then rebase -i
gt r -n main      # Show what would be rebased (dry-run)
gt r ?            # Interactive branch selection
```

## How It Works

Single busybox-style script. Symlinks (`gco`, `gcoo`, `gtp`,
`groo`) are detected via `basename $0` and dispatched to the
matching subcommand. `gcoo` and `groo` auto-add `-u` (fetch).

Branch selection pipeline (shared by checkout and rebase):
1. Recent branches from reflog (last 50)
2. All branches sorted by commit date
3. Dedupe, strip `origin/` prefix
4. Pipe to fzf for fuzzy matching
