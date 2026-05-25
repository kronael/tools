# clp — Claude Project Launcher

Bash function: fzf-pick a project dir, cd there, launch claude.

## Usage

```
clp ?                # fzf picker, empty query (browse all)
clp <pattern>        # fzf prefiltered, Enter to confirm
clp <pattern> <name> # cd to project, resume named session
```

## Implementation

```bash
_clp_pick_dir() {
    local reg=~/.config/clp/projects q="${1:-}"
    local dirs
    [[ "$q" == "?" ]] && q=""
    if [[ -f "$reg" ]]; then
        dirs=$(sed "s|^~|$HOME|" "$reg")
    else
        dirs=$(find ~/wk -maxdepth 1 -mindepth 1 -type d)
    fi
    echo "$dirs" | while read -r d; do
        printf "%s\t%s\n" "$(basename "$d")" "$d"
    done | fzf --exit-0 -q "$q" --with-nth=1 --delimiter='\t' | cut -f2
}

clp() {
    local dir
    dir=$(_clp_pick_dir "$1") || return
    cd "$dir" || return
    claude ${2:+-r "$2"}
}
```

## Setup

Source from shell rc:
```bash
source ~/.local/share/clp/clp.bash
```

## Project Registry

`~/.config/clp/projects` — one dir per line:
```
~/wk/tools
~/wk/marinade
~/wk/trader
```

Falls back to `~/wk/*/` if file missing.

## Files

```
clp/
  clp.bash    # sourceable function definition
  Makefile    # install/clean
```

Install copies to `~/.local/share/clp/clp.bash`.

## Key Decisions

1. **Bash function** — must cd the calling shell
2. **No auto-select** — always show fzf, Enter to confirm
3. **`?` = browse all** — matches rig convention
4. **No session tracking** — claude -r <name> handles it natively
5. **Plain text registry** — one path per line, ~ expanded
