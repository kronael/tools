#!/usr/bin/env bash

set -e
ancestor=$(printf ancestor | git hash-object -w --stdin)
git -C "$tmp/seed" push -q origin "$topic:refs/heads/master"
git fetch -q origin
git update-ref refs/heads/master "$base"
git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
heads=$(git for-each-ref --format='%(refname) %(objectname)' refs/heads)
set +e

for cmd in rco gco; do
    true_ "$cmd prefers origin over stale local master" \
        'checkout_ "$cmd" master "$topic" && checkout_ "$cmd" refs/heads/master "$base"'
    git checkout -q --detach "$base"
    true_ "$cmd HEAD stays at the current commit" \
        '"$cmd" HEAD >"$tmp/out" 2>&1 && detached "$base"'
done

git checkout -q --detach "$topic"
git checkout -q --detach "$base"
true_ 'gco - returns to the previous checkout' \
    'gco - >"$tmp/out" 2>&1 && detached "$topic"'

restore_(){
    local flag=$1 want=$2
    git checkout -q HEAD -- file || return
    printf '0 %s\tfile\n100644 %s 1\tfile\n100644 %s 2\tfile\n100644 %s 3\tfile\n' \
        "$ancestor" "$ancestor" "$(git rev-parse "$topic:file")" \
        "$(git rev-parse "$base:file")" | git update-index --index-info || return
    gco "$flag" -- file >"$tmp/out" 2>&1 &&
        grep -q -- "$want" file && detached "$topic" &&
        ! gco "$flag" >"$tmp/out" 2>&1 &&
        ! rco "$flag" -- file >"$tmp/out" 2>&1
}

git checkout -q --detach "$topic"
for flag in --ours --theirs -m --merge --conflict=diff3; do
    want='<<<<<<<'
    [[ $flag == --ours ]] && want='^topic$'
    [[ $flag == --theirs ]] && want='^base$'
    true_ "gco $flag restores conflict paths only" 'restore_ "$flag" "$want"'
done
git reset -q HEAD -- file
git checkout -q HEAD -- file
for flag in -p --patch; do
    echo dirty > file
    true_ "gco $flag restores selected hunks only with paths" \
        'gco "$flag" -- file <<< y >"$tmp/out" 2>&1 &&
         [[ $(cat file) == topic ]] && detached "$topic" &&
         ! gco "$flag" >"$tmp/out" 2>&1'
done
git checkout -q HEAD -- file

true_ 'gib -r passes options through and retains listing mode' \
    'gib -r >"$tmp/out" && grep -q origin/feature-one "$tmp/out" &&
     ! grep -q local-only "$tmp/out" &&
     gib --no-list new-branch >/dev/null 2>&1 && detached "$topic"'

for ((i=0; i<400; i++)); do
    printf 'update refs/remotes/origin/candidate-%s %s\n' "$i" "$base"
done | git update-ref --stdin
: > "$RIG_LOG"
true_ 'branch picker filters origin candidates without per-candidate git calls' \
    'gco -n candidate-399 >"$tmp/out" && [[ $(cat "$tmp/out") == origin/candidate-399 ]] &&
     [[ $(grep -c "^show-ref " "$RIG_LOG") -le 3 ]]'

set -e
git update-ref refs/heads/feature-one "$topic"
heads=$(git for-each-ref --format='%(refname) %(objectname)' refs/heads)
git -C "$tmp/seed" -c commit.gpgsign=false commit --allow-empty -qm fresh
fresh=$(git -C "$tmp/seed" rev-parse HEAD)
git -C "$tmp/seed" -c tag.gpgsign=false tag -a fresh -m fresh
git -C "$tmp/seed" push -q origin "$fresh:refs/heads/feature-one" --tags
set +e
true_ 'rco checks out a commit pushed after initial fetch' \
    'checkout_ rco feature-one "$fresh" &&
     [[ $(git rev-parse origin/feature-one) == "$fresh" &&
        $(git rev-parse "fresh^{commit}") == "$fresh" ]]'

true_ 'gco help names gco and path restore without offering offline mode' \
    'gco -h >"$tmp/out" && grep -q "Usage: gco" "$tmp/out" &&
     grep -q -- "-- paths" "$tmp/out" && ! grep -q -- "-z" "$tmp/out"'

git config remote.origin.fetch '+refs/heads/*:refs/heads/*'
true_ 'rco fetch cannot create local branches through configured refspecs' \
    'checkout_ rco "$base" "$base" &&
     [[ $(git rev-parse origin/master) == "$topic" ]]'
