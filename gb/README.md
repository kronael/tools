# gb - Smart Git Branch Switcher

Fuzzy find and checkout git branches using fzf.

## Problem

Frequently switching between git branches using `git checkout origin/20260128_apm` is tedious. This tool intelligently matches partial patterns against recent branches.

## Features

- **Interactive mode**: Opens fzf to fuzzy find branches
- **Non-interactive mode**: Auto-selects best match when given a pattern
- **Recent branches first**: Prioritizes recently checked-out branches
- **Clean display**: Strips `origin/` prefix for readability

## Dependencies

- fzf
- git

## Installation

```bash
cd gb
make install
```

Installs to `~/.local/bin/gb` (ensure `~/.local/bin` is in your PATH).

## Usage

**Interactive mode** (no arguments):
```bash
gb              # Opens fzf, type to filter, Enter to checkout
gb -u           # Fetch updates before showing branches
```

**Non-interactive mode** (with argument):
```bash
gb apm          # Auto-selects best match for "apm"
gb workers      # Auto-selects "origin/20260127_workers"
gb 0128         # Matches by date pattern
gb -u apm       # Fetch updates before checkout
```

If multiple matches exist, shows fzf pre-filtered to your query for final selection.

**Flags:**
- `-u`: Fetch updates from remote before checkout (optional, faster without)

## How It Works

1. Gets recently checked-out branches from git reflog (last 50)
2. Gets all branches sorted by commit date
3. Removes duplicates and strips `origin/` prefix
4. Pipes to fzf for fuzzy matching
5. Executes `git fetch && git checkout origin/<selected>`

## fzf Flags

- `--select-1`: Auto-select if only one match
- `--exit-0`: Exit if no matches
- `--query`: Pre-filter with argument
