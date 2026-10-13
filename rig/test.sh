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

# ghpush derives the HTTPS URL from the SSH remote and never touches it; -n and
# -u contact nothing, so a GitHub-shaped URL on a local repo is enough.
git init -q "$tmp/gh"
git -C "$tmp/gh" remote add origin git@github.com:owner/repo.git
ghpush_(){ (cd "$tmp/gh" && ghpush "$@"); }
ghfetch_(){ (cd "$tmp/gh" && ghfetch "$@"); }
gh_url=https://github.com/owner/repo.git
helper="-c credential.helper= -c credential.helper=\\!gh\\ auth\\ git-credential"
pin="-c url.$gh_url.insteadOf=$gh_url -c url.$gh_url.pushInsteadOf=$gh_url"
true_ 'ghpush -u prints the HTTPS URL of an SSH origin' '[[ $(ghpush_ -u) == "$gh_url" ]]'
for url in ssh://git@github.com/owner/repo.git ssh://git@github.com:22/owner/repo.git \
           ssh://git@ssh.github.com:443/owner/repo.git https://github.com/owner/repo \
           git@github.com:owner/repo; do
    git -C "$tmp/gh" remote set-url origin "$url"
    true_ "ghpush -u normalizes $url" '[[ $(ghpush_ -u) == "$gh_url" ]]'
done
git -C "$tmp/gh" remote set-url origin git@GitHub.com:owner/repo.git
false_ 'ghpush refuses a host spelled other than github.com' 'ghpush_ -u >"$tmp/out" 2>&1'
git -C "$tmp/gh" remote set-url origin git@github.com:owner/repo.git
specs='abc123:refs/heads/x v1:refs/tags/v1 abc:refs/heads/a/b'
true_ 'ghpush -n prints the one-off HTTPS push through the gh credential helper' \
    '[[ $(ghpush_ -n $specs) == "git $helper $pin push --no-follow-tags $gh_url $specs " ]]'
true_ 'ghpush leaves the remote URL alone' \
    '[[ $(git -C "$tmp/gh" remote get-url origin) == git@github.com:owner/repo.git ]]'
fetch_want="git $helper $pin fetch $gh_url master +refs/heads/\\*:refs/remotes/origin/\\* "
true_ 'ghfetch -n prints the same one-off HTTPS fetch' \
    '[[ $(ghfetch_ -n master "+refs/heads/*:refs/remotes/origin/*") == "$fetch_want" ]]'
true_ 'ghfetch -n needs no refspec' '[[ $(ghfetch_ -n) == "git $helper $pin fetch $gh_url " ]]'

git -C "$tmp/gh" config remote.origin.pushurl git@github.com:fork/repo.git
fork_url=https://github.com/fork/repo.git
true_ 'ghpush -u reads the push URL' '[[ $(ghpush_ -u) == "$fork_url" ]]'
true_ 'ghpush -n pushes to the push URL' \
    '[[ $(ghpush_ -n abc:refs/heads/x) == *" push --no-follow-tags $fork_url abc:refs/heads/x " ]]'
true_ 'ghfetch -u reads the fetch URL' '[[ $(ghfetch_ -u) == "$gh_url" ]]'
true_ 'ghfetch -n fetches from the fetch URL' '[[ $(ghfetch_ -n) == *" fetch $gh_url " ]]'
git -C "$tmp/gh" config --unset remote.origin.pushurl

# A url rewrite of https://github.com/ to elsewhere (SSH for a real user, a
# local bare repo here) catches plain git; ghpush and ghfetch still go to the
# HTTPS URL, which GIT_ALLOW_PROTOCOL=file stops before any network.
git init -q --bare "$tmp/rewritten/owner/repo.git"
git -C "$tmp/gh" config "url.file://$tmp/rewritten/.insteadOf" https://github.com/
git -C "$tmp/gh" config "url.file://$tmp/rewritten/.pushInsteadOf" https://github.com/
git -C "$tmp/gh" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false \
    commit -q --allow-empty -m gh
rewritten_heads(){ git -C "$tmp/rewritten/owner/repo.git" for-each-ref --format='%(refname)'; }
true_ 'a plain push to the HTTPS URL follows the rewrite' \
    '(cd "$tmp/gh" && GIT_ALLOW_PROTOCOL=file git push -q "$gh_url" HEAD:refs/heads/plain) 2>/dev/null &&
     [[ $(rewritten_heads) == refs/heads/plain ]]'
true_ 'ghpush keeps the HTTPS URL under a url rewrite' \
    '[[ $(ghpush_ -n HEAD:refs/heads/x) == "git $helper $pin push --no-follow-tags $gh_url HEAD:refs/heads/x " ]]'
GIT_ALLOW_PROTOCOL=file ghpush_ HEAD:refs/heads/gh >"$tmp/out" 2>&1
rc=$?
true_ 'ghpush goes to HTTPS, not where the url rewrite points' \
    '[[ $rc != 0 && $(rewritten_heads) == refs/heads/plain ]] &&
     grep -q "transport '\''https'\'' not allowed" "$tmp/out"'
GIT_ALLOW_PROTOCOL=file ghfetch_ plain >"$tmp/out" 2>&1
rc=$?
true_ 'ghfetch goes to HTTPS, not where the url rewrite points' \
    '[[ $rc != 0 ]] && grep -q "transport '\''https'\'' not allowed" "$tmp/out"'
git -C "$tmp/gh" config --remove-section "url.file://$tmp/rewritten/"

# A refusal happens before any git call: under RIG_STUB the stub logs every
# git invocation, so an accepted refspec would leave a line in the log.
refused='takes the stated refspecs only'
shape='a refspec is <src>:refs/heads/<branch>'
while IFS='|' read -r cmd line msg; do
    read -r -a args <<<"$line"
    : > "$RIG_LOG"
    RIG_STUB=1 "${cmd}_" "${args[@]}" >"$tmp/out" 2>&1
    rc=$?
    true_ "$cmd refuses '$line' before git runs" \
        '[[ $rc == 1 && ! -s "$RIG_LOG" ]] && grep -qF "error: $msg" "$tmp/out"'
done <<EOF
ghpush|-f abc:refs/heads/x|-f is refused: ghpush $refused
ghpush|--force abc:refs/heads/x|--force is refused: ghpush $refused
ghpush|--force-with-lease abc:refs/heads/x|--force-with-lease is refused: ghpush $refused
ghpush|--force-with-lease=refs/heads/x:abc abc:refs/heads/x|--force-with-lease=refs/heads/x:abc is refused
ghpush|--force-if-includes abc:refs/heads/x|--force-if-includes is refused: ghpush $refused
ghpush|--tags abc:refs/heads/x|--tags is refused: ghpush $refused
ghpush|--all|--all is refused: ghpush $refused
ghpush|--mirror|--mirror is refused: ghpush $refused
ghpush|-d abc:refs/heads/x|-d is refused: ghpush $refused
ghpush|--delete abc:refs/heads/x|--delete is refused: ghpush $refused
ghpush|-- abc:refs/heads/x|unknown flag: --
ghpush|-o ci.skip abc:refs/heads/x|unknown flag: -o
ghpush|--prune abc:refs/heads/x|unknown flag: --prune
ghpush|--no-verify abc:refs/heads/x|unknown flag: --no-verify
ghpush|-nf abc:refs/heads/x|unknown flag: -nf
ghpush|--atomic abc:refs/heads/x|unknown flag: --atomic
ghpush|+abc:refs/heads/x|+abc:refs/heads/x: $shape
ghpush|:refs/heads/x|:refs/heads/x: $shape
ghpush|refs/heads/*:refs/heads/*|refs/heads/*:refs/heads/*: $shape
ghpush|abc:refs/heads/*|abc:refs/heads/*: $shape
ghpush|abc:x|abc:x: $shape
ghpush|master|master: $shape
ghpush|refs/heads/x|refs/heads/x: $shape
ghpush|abc:refs/notes/x|abc:refs/notes/x: $shape
ghpush|abc:refs/pull/1/head|abc:refs/pull/1/head: $shape
ghpush|abc:refs/remotes/origin/x|abc:refs/remotes/origin/x: $shape
ghpush|abc:refs/heads/|abc:refs/heads/: $shape
ghpush|abc:refs/tags/|abc:refs/tags/: $shape
ghpush|abc:refs/heads/x:refs/heads/y|abc:refs/heads/x:refs/heads/y: $shape
ghpush|abc:refs/heads/x master|master: $shape
ghpush||a refspec is required
ghpush|-u abc:refs/heads/x|-u takes no refspec: abc:refs/heads/x
ghfetch|-f master|-f is refused: ghfetch $refused
ghfetch|--force master|--force is refused: ghfetch $refused
ghfetch|--force-with-lease master|--force-with-lease is refused: ghfetch $refused
ghfetch|--force-if-includes master|--force-if-includes is refused: ghfetch $refused
ghfetch|--tags|--tags is refused: ghfetch $refused
ghfetch|--all|--all is refused: ghfetch $refused
ghfetch|--mirror|--mirror is refused: ghfetch $refused
ghfetch|-d master|-d is refused: ghfetch $refused
ghfetch|--delete master|--delete is refused: ghfetch $refused
ghfetch|--prune master|unknown flag: --prune
ghfetch|-- master|unknown flag: --
ghfetch|-u master|-u takes no refspec: master
EOF

git init -q "$tmp/no-origin"
for cmd in ghpush ghfetch; do
    (cd "$tmp/no-origin" && "$cmd" -n abc:refs/heads/x) >"$tmp/out" 2>&1
    rc=$?
    true_ "$cmd fails loud without an origin remote" \
        '[[ $rc == 1 ]] && grep -qx "error: no origin remote" "$tmp/out"'
done

git -C "$tmp/gh" remote set-url origin "https://user:secret@github.com/owner/repo.git"
true_ 'ghpush -u accepts a tokened https origin and drops the token' '[[ $(ghpush_ -u) == "$gh_url" ]]'
git -C "$tmp/gh" remote set-url origin "https://user:secret@example.test/owner/repo.git"
false_ 'ghpush refuses a non-GitHub origin' 'ghpush_ -u >"$tmp/out" 2>&1'
true_  'ghpush names the non-GitHub origin without its userinfo' \
    'grep -q "not a GitHub remote: https://example.test/owner/repo.git" "$tmp/out"'

mkdir "$tmp/install"
cp "$rig" "$tmp/install/rig"
chmod +x "$tmp/install/rig"
"$tmp/install/rig" install >"$tmp/out" 2>&1
for alias in "${aliases[@]}"; do
    true_ "$alias is installed as a rig symlink" \
        '[[ $(readlink "$tmp/install/$alias") == rig ]]'
done

# Reinstalling drops a link to rig that the list no longer ships and leaves
# everything else in the dir: files, links elsewhere, and the current aliases.
ln -s rig "$tmp/install/riq"
ln -s "$tmp/install/rig" "$tmp/install/riq-abs"
ln -s "$tmp/work" "$tmp/install/elsewhere"
ln -s "$tmp/missing" "$tmp/install/dangling"
echo keep > "$tmp/install/gpx"
"$tmp/install/rig" install >"$tmp/out" 2>&1
false_ "install removes a dropped alias"            '[[ -L "$tmp/install/riq" ]]'
false_ "install removes a dropped alias linked by absolute path" \
    '[[ -L "$tmp/install/riq-abs" ]]'
true_  "install leaves a link pointing elsewhere"   '[[ $(readlink "$tmp/install/elsewhere") == "$tmp/work" ]]'
true_  "install leaves a dangling link elsewhere"   '[[ -L "$tmp/install/dangling" ]]'
true_  "install leaves a regular file"              '[[ $(< "$tmp/install/gpx") == keep ]]'
true_  "install leaves the shipped aliases linked" \
    '[[ $(readlink "$tmp/install/${aliases[0]}") == rig ]]'
true_  "install leaves rig itself"                  '[[ -f "$tmp/install/rig" && ! -L "$tmp/install/rig" ]]'

# make clean takes the same links away, dropped aliases included, and rig.
mkdir -p "$tmp/home/.local/bin"
cp "$rig" "$tmp/home/.local/bin/rig"
HOME="$tmp/home" "$tmp/home/.local/bin/rig" install >/dev/null 2>&1
ln -s rig "$tmp/home/.local/bin/riq"
ln -s "$tmp/work" "$tmp/home/.local/bin/elsewhere"
echo keep > "$tmp/home/.local/bin/gpx"
HOME="$tmp/home" make -s -C "$here" clean >/dev/null 2>&1
false_ "clean removes a dropped alias"              '[[ -L "$tmp/home/.local/bin/riq" ]]'
false_ "clean removes a shipped alias"              '[[ -L "$tmp/home/.local/bin/${aliases[0]}" ]]'
false_ "clean removes rig"                          '[[ -e "$tmp/home/.local/bin/rig" ]]'
true_  "clean leaves a link pointing elsewhere"     '[[ -L "$tmp/home/.local/bin/elsewhere" ]]'
true_  "clean leaves a regular file"                '[[ -f "$tmp/home/.local/bin/gpx" ]]'

mv "$tmp/offline" "$tmp/origin"
source "$here/test-checkout.sh"

echo "rig/test.sh: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
