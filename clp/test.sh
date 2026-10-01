#!/bin/bash
# Stubs fzf and claude, so this runs with no terminal and no session.
set -u
cd "$(dirname "$0")"

tmp=$(mktemp -d)
mkdir "$tmp/bin" "$tmp/bare" "$tmp/home" "$tmp/home/.config" "$tmp/home/.config/clp" \
    "$tmp/proj" "$tmp/start"
trap 'rm -f "$tmp/bin"/* "$tmp/home/.config/clp/projects" "$tmp/log"
      rmdir "$tmp/bin" "$tmp/bare" "$tmp/home/.config/clp" "$tmp/home/.config" \
          "$tmp/home" "$tmp/proj" "$tmp/start" "$tmp"' EXIT
PATH="$tmp/bin:$PATH"
fail=0

check() {
    if [[ "$3" == *"$2"* ]]; then
        echo "ok   $1"
    else
        echo "FAIL $1: expected '$2' in '$3'"
        fail=1
    fi
}

mkstub() { printf '%s\n' "$2" > "$tmp/bin/$1"; chmod +x "$tmp/bin/$1"; }

# fzf picks the first line, or with FZF_RC set exits that way with no pick
# (1 = no match, 130 = Esc), as the real one does.
mkstub fzf '#!/bin/sh
if [ "${FZF_RC:-0}" = 0 ]; then head -1; else cat >/dev/null; exit "$FZF_RC"; fi'
mkstub claude '#!/bin/sh
echo "claude $* in $(pwd)" >> "$LOG"'

# Each run sources clp into a fresh subshell, starting in $tmp/start.
here=$PWD
run() {
    local home=$1
    shift
    : > "$tmp/log"
    (set +u; export HOME="$home" LOG="$tmp/log"; source "$here/clp.bash"; cd "$tmp/start"; clp "$@") 2>&1
    echo "rc=$?"
}

out=$(run "$tmp/bare")
check "nothing to pick from fails" "rc=1" "$out"
check "nothing to pick from says why" "no ~/.config/clp/projects" "$out"
[[ -s "$tmp/log" ]] && { echo "FAIL nothing to pick from started claude"; fail=1; }

echo "$tmp/proj" > "$tmp/home/.config/clp/projects"
for rc in 1 130; do
    out=$(FZF_RC=$rc run "$tmp/home")
    check "no selection (fzf $rc) fails" "rc=1" "$out"
    check "no selection (fzf $rc) says so" "no project selected" "$out"
    [[ -s "$tmp/log" ]] && { echo "FAIL no selection (fzf $rc) started claude"; fail=1; }
done

out=$(run "$tmp/home")
check "a pick starts claude" "rc=0" "$out"
check "a pick starts claude in the project" "in $tmp/proj" "$(cat "$tmp/log")"

out=$(run "$tmp/home" "" sess1)
check "a session id resumes it" "claude -r sess1 in $tmp/proj" "$(cat "$tmp/log")"

[ "$fail" = 0 ] && echo "all passed"
exit "$fail"
