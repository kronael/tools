_clp_pick_dir() {
    local reg=~/.config/clp/projects q="${1:-}"
    local dirs
    [[ "$q" == "?" ]] && q=""
    if [[ -f "$reg" ]]; then
        dirs=$(sed "s|^~|$HOME|" "$reg")
    elif [[ -d ~/wk ]]; then
        dirs=$(find ~/wk -maxdepth 1 -mindepth 1 -type d)
    else
        echo "clp: no ~/.config/clp/projects and no ~/wk to pick from" >&2
        return 1
    fi
    echo "$dirs" | while read -r d; do
        printf "%s\t%s\n" "$(basename "$d")" "$d"
    done | fzf --exit-0 -q "$q" --with-nth=1 --delimiter=$'\t' | cut -f2
}

clp() {
    local dir
    dir=$(_clp_pick_dir "${1:-}") || return
    # fzf exits non-zero on Esc or no match, but the pipeline returns cut's 0.
    [[ -n "$dir" ]] || { echo "clp: no project selected" >&2; return 1; }
    cd "$dir" || return
    claude ${2:+-r "$2"}
}
