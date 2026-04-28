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
    done | fzf --exit-0 -q "$q" --with-nth=1 --delimiter=$'\t' | cut -f2
}

clp() {
    local dir
    dir=$(_clp_pick_dir "$1") || return
    cd "$dir" || return
    claude ${2:+-r "$2"}
}
