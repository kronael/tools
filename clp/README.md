# clp — claude project picker

**Experimental.** Sourceable bash function that fzf-picks a project
directory, `cd`s into it, and launches `claude`. Optionally resumes a
previous Claude Code session.

## Install

```sh
cd clp && make install
# then in ~/.bashrc or ~/.zshrc:
source ~/.local/share/clp/clp.bash
```

`make install` copies `clp.bash` to `~/.local/share/clp/clp.bash`. It is
not a standalone executable — it must be sourced into your shell so the
`cd` it performs persists in the parent shell.

## Usage

```sh
clp              # fzf-pick a project, launch claude there
clp foo          # pre-fill the fzf query with "foo"
clp ?            # force fzf even if "?" matches an entry
clp foo bar123   # pick "foo", resume claude session id "bar123"
```

The second positional argument, if present, is passed as `claude -r <id>`
to resume a prior session.

## Project list

`clp` picks from `~/.config/clp/projects` if it exists. Each line is a
directory path; a leading `~` is expanded to `$HOME`. Example:

```
~/wk/tools
~/wk/foo
/srv/data/bar
```

If `~/.config/clp/projects` is missing, `clp` falls back to listing
immediate subdirectories of `~/wk`.

## Why

Two muscle-memory wins:
1. Pick a project without typing its full path.
2. Land in `claude` ready to work, not in the shell.

## Status

Experimental: API may change. Currently no tests, no error handling
beyond what bash gives you for free. The fallback (`~/wk` scan) assumes
that convention — adjust the script or maintain `~/.config/clp/projects`
if your layout differs.
