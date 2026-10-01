#!/usr/bin/env bash
set -Euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
rig=$(realpath "${RIG:-$here/rig}")
pass=0; fail=0
ok()   { pass=$((pass+1)); }
bad()  { fail=$((fail+1)); echo "FAIL: $1" >&2; }
true_() { if eval "$2"; then ok; else bad "$1"; fi; }
false_(){ if eval "$2"; then bad "$1"; else ok; fi; }

tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
export GIT_TERMINAL_PROMPT=0 GIT_EDITOR=true GIT_PAGER=cat
export FZF_DEFAULT_OPTS= FZF_DEFAULT_OPTS_FILE=/dev/null
export RIG_LOG="$tmp/git.log" RIG_GIT
RIG_GIT=$(command -v git)
set -e
mkdir "$tmp/bin"
cp "$rig" "$tmp/bin/rig"
chmod +x "$tmp/bin/rig"
mapfile -t aliases < <(bash "$rig" aliases)
for alias in "${aliases[@]}"; do
    ln -s rig "$tmp/bin/$alias"
done
cat > "$tmp/bin/fzf" <<'STUB'
#!/usr/bin/env bash
q=
for a in "$@"; do
    case "$a" in --query=*) q=${a#--query=} ;; esac
done
grep -F -m1 -- "$q"
STUB
chmod +x "$tmp/bin/fzf"
git init -q --bare "$tmp/origin"
git clone -q "$tmp/origin" "$tmp/seed" 2>"$tmp/setup.log"
cd "$tmp/seed"
git config user.name 'Rig Test'
git config user.email 'rig@example.invalid'
echo base > file
git add file
git -c commit.gpgsign=false commit -qm base
base=$(git rev-parse HEAD)
git -c tag.gpgsign=false tag -a release -m release
echo topic > file
git -c commit.gpgsign=false commit -qam topic
topic=$(git rev-parse HEAD)
git push -q origin HEAD:refs/heads/feature-one "$base:refs/heads/base" --tags
git init -q "$tmp/work"
cd "$tmp/work"
git remote add origin "$tmp/origin"
git fetch -q origin
git checkout -q --detach "$base"
git update-ref refs/heads/local-only "$base"
heads=$(git for-each-ref --format='%(refname) %(objectname)' refs/heads)
cat > "$tmp/bin/git" <<'EOF'
#!/bin/bash
printf '%q ' "$@" >> "$RIG_LOG"
printf '\n' >> "$RIG_LOG"
[[ ${RIG_STUB:-} ]] && exit "${RIG_RC:-0}"
exec "$RIG_GIT" "$@"
EOF
chmod +x "$tmp/bin/git"
export PATH="$tmp/bin:$PATH"
set +e

detached(){
    [[ -z $(git branch --show-current) && $(git rev-parse HEAD) == "$1" &&
       $(git for-each-ref --format='%(refname) %(objectname)' refs/heads) == "$heads" ]] &&
       ! git config --get-regexp '^branch\.'
}

checkout_(){
    local cmd=$1 ref=$2 want=$3 start=$base
    [[ "$want" == "$base" ]] && start=$topic
    git checkout -q --detach "$start" || return
    : > "$RIG_LOG"
    "$cmd" "$ref" >"$tmp/out" 2>&1 || return
    if [[ "$cmd" == rco ]]; then
        grep -q '^fetch ' "$RIG_LOG" || return 1
    else
        grep -q '^fetch ' "$RIG_LOG" && return 1
    fi
    grep -q '^checkout --detach ' "$RIG_LOG" && detached "$want"
}

for cmd in rco gco; do
    [[ "$cmd" == gco ]] && mv "$tmp/origin" "$tmp/offline"
    true_ "$cmd hash detaches" 'checkout_ "$cmd" "$base" "$base"'
    true_ "$cmd tag detaches" 'checkout_ "$cmd" release "$base"'
    true_ "$cmd branch pattern detaches" 'checkout_ "$cmd" feature-on "$topic"'
    true_ "$cmd local branch detaches" 'checkout_ "$cmd" local-only "$base"'
    true_ "$cmd qualified local branch detaches" 'checkout_ "$cmd" refs/heads/local-only "$base"'
    true_ "$cmd origin ref detaches" 'checkout_ "$cmd" origin/feature-one "$topic"'
    for flag in -b -B -c -C --track -t --orphan -bnew --track=direct --orphan=new; do
        : > "$RIG_LOG"
        "$cmd" feature-one "$flag" >"$tmp/out" 2>&1
        rc=$?
        true_ "$cmd refuses $flag before git runs" \
            '[[ $rc == 1 && ! -s "$RIG_LOG" ]] && grep -q "^error:" "$tmp/out" &&
             ! "$cmd" --ours "$flag" -- file >"$tmp/out" 2>&1 &&
             [[ ! -s "$RIG_LOG" ]] && detached "$topic"'
    done
done

echo dirty > file
true_ 'gco -- file restores the index' \
    'gco -- file >"$tmp/out" 2>&1 && [[ $(cat file) == topic ]] && detached "$topic"'
true_ 'gco ref -- file restores that ref without moving HEAD' \
    'gco release -- file >"$tmp/out" 2>&1 && [[ $(cat file) == base ]] && detached "$topic"'
git checkout HEAD -- file
: > "$RIG_LOG"
gco local-only -- >"$tmp/out" 2>&1
rc=$?
true_ 'gco requires paths after -- and stays detached' \
    '[[ $rc == 1 && ! -s "$RIG_LOG" ]] && grep -q "requires gco" "$tmp/out" && detached "$topic"'
true_ 'gib lists local and remote branches' \
    'gib >"$tmp/out" && grep -q local-only "$tmp/out" && grep -q remotes/origin/feature-one "$tmp/out"'
true_ 'gib name is a pattern, never a new branch' \
    'gib new-branch >"$tmp/out" && [[ ! -s "$tmp/out" ]] && detached "$topic"'
false_ 'gib --no-list cannot create a branch' \
    '! gib --no-list new-branch >/dev/null 2>&1 || git show-ref --verify --quiet refs/heads/new-branch'

while IFS='|' read -r alias expected; do
    : > "$RIG_LOG"
    RIG_STUB=1 "$alias" 'two words' '*' >"$tmp/out" 2>&1
    rc=$?
    printf -v tail '%q ' 'two words' '*'
    [[ $alias == gib ]] && tail+='--list '
    true_ "$alias symlink forwards exact git arguments" \
        '[[ $rc == 0 && $(cat "$RIG_LOG") == "$expected $tail" ]]'
    RIG_STUB=1 RIG_RC=7 "$alias" >"$tmp/out" 2>&1
    rc=$?
    true_ "$alias preserves git exit status" '[[ $rc == 7 ]]'
done <<'EOF'
gif|diff
gifs|diff --staged
gss|stash
gsp|stash pop
gsl|stash list --stat
grec|rebase --continue
grea|rebase --abort
gres|rebase --skip
gib|branch --all
gitsu|status
EOF

mkdir "$tmp/install"
cp "$rig" "$tmp/install/rig"
chmod +x "$tmp/install/rig"
"$tmp/install/rig" install >"$tmp/out" 2>&1
for alias in "${aliases[@]}"; do
    true_ "$alias is installed as a rig symlink" \
        '[[ $(readlink "$tmp/install/$alias") == rig ]]'
done

mv "$tmp/offline" "$tmp/origin"
source "$here/test-checkout.sh"

echo "rig/test.sh: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
