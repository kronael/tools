#!/bin/bash
set -u

stub=$(mktemp -d)
work=$(mktemp -d)
trap 'chmod -R u+w -- "$work"; rm -rf -- "$stub" "$work"' EXIT
PATH=$stub:$PATH
export HOME=$work
unset RUSTUP_HOME XDG_CACHE_HOME
fail=0

check() {
    local name=$1
    shift
    if "$@"
    then
        echo "ok   $name"
    else
        echo "FAIL $name"
        fail=1
    fi
}
has() { [[ $2 == *"$1"* ]]; }
lacks() { [[ $2 != *"$1"* ]]; }

for cmd in pnpm bun uv pip pre-commit yay qemubox dockbox
do
    printf '#!/bin/sh\necho "stub %s $*"\n' "$cmd" > "$stub/$cmd"
done
cat > "$stub/go" <<'EOF'
#!/bin/sh
case "$*" in
    "env GOCACHE") echo "$HOME/gocache" ;;
    *) echo "stub go $*" ;;
esac
EOF
printf '#!/bin/sh\nexit 0\n' > "$stub/df"
printf '#!/bin/sh\necho "${MNT_OPTS:-rw,relatime}"\n' > "$stub/findmnt"
age_tree() {
    find "$1" -exec touch -h -d "@$(( $(date +%s) - $2 * 86400 ))" {} +
}
cat > "$stub/mountpoint" <<'EOF'
#!/bin/sh
for last; do :; done
[ "$last" = "${MOUNTED:-}" ] || exit 32
EOF
cat > "$stub/rustup" <<'EOF'
#!/bin/sh
case "$*" in
    "toolchain list")
        printf '%s\n' 'stable-x86_64-unknown-linux-gnu (default)' \
            1.82.0-x86_64-unknown-linux-gnu \
            1.83.0-x86_64-unknown-linux-gnu \
            '1.84.0-x86_64-unknown-linux-gnu (default)' \
            1.89.0-sbpf-x \
            nightly-x86_64-unknown-linux-gnu solana
        cat "$RUSTUP_EXTRA" 2>/dev/null || true ;;
    *) echo "stub rustup $*" ;;
esac
EOF
anon=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
cat > "$stub/docker" <<EOF
#!/bin/sh
case "\$*" in
    "volume ls -q -f dangling=true") printf '%s\n' $anon pgdata ;;
    *) echo "stub docker \$*" ;;
esac
EOF
chmod +x "$stub"/*

check "help" has "usage: diskclean" "$(./diskclean -h)"
./diskclean --help >/dev/null
check "help exits 0" test $? = 0
check "unknown option" has "Unknown option: -x" "$(./diskclean -x 2>&1)"
./diskclean -x >/dev/null 2>&1
check "unknown option exits 2" test $? = 2
check "level 3 is gone" has "Unknown option: -3" "$(./diskclean -3 2>&1)"
check "missing option argument" has "Option needs an argument: -k" \
    "$(./diskclean -k 2>&1)"
check "missing dir" has "Not a directory" "$(./diskclean "$work/nope" 2>&1)"
./diskclean "$work/nope" >/dev/null 2>&1
check "missing dir exits 2" test $? = 2

out=$(./diskclean -k list)
for kind in node_modules target pnpm-store next venv pycache toolcache gomod \
    rustup platform-tools pipenv browsers prunes
do
    check "kinds table lists $kind" has " $kind " "$out"
done
check "kinds table shows levels" has "2 rustup" "$out"
check "bogus kind" has "Unknown kind: bogus" "$(./diskclean -k bogus 2>&1)"
./diskclean -k target,bogus >/dev/null 2>&1
check "bogus kind exits 2" test $? = 2
./diskclean -k target,rustup -l "$work" >/dev/null 2>&1 </dev/null
check "known kinds accepted" test $? = 0

for bad in -o10x -o -o1d2
do
    ./diskclean "$bad" "$work" >/dev/null 2>&1
    check "bad value $bad exits 2" test $? = 2
done
check "bad age message" has "Bad age: 10x" "$(./diskclean -o 10x 2>&1)"
for good in "-o 30d" "-o 8w" "-o 6m" "-o 1y" "-o 30" "-l" "-1" "-2"
do
    read -ra args <<< "$good"
    ./diskclean "${args[@]}" "$work" >/dev/null 2>&1 </dev/null
    check "accepts $good" test $? = 0
done

check "nothing found" has "nothing to clean" \
    "$(echo n | ./diskclean "$work")"

mkdir -p "$work/app/node_modules/x" "$work/crate/target/debug" \
    "$work/crate/target/deploy" "$work/loose/target/keep" \
    "$work/.bun/install/node_modules" "$work/untagged/target/debug" \
    "$work/proj/.pr1/target/debug" "$work/proj/.pr1/node_modules" \
    "$work/nest/node_modules/inner/node_modules" "$work/deep/a/ok/b/node_modules"
touch "$work/app/package.json" "$work/crate/Cargo.toml" \
    "$work/crate/target/deploy/k.json" "$work/.bun/install/package.json" \
    "$work/crate/target/CACHEDIR.TAG" "$work/untagged/Cargo.toml" \
    "$work/proj/.pr1/Cargo.toml" "$work/proj/.pr1/target/CACHEDIR.TAG" \
    "$work/nest/package.json" "$work/nest/node_modules/inner/package.json" \
    "$work/deep/a/ok/b/package.json"
head -c 1048576 /dev/zero > "$work/crate/target/deploy/big.bin"
head -c 102400 /dev/zero > "$work/crate/target/debug/obj"

for dir in .git .claude .codex .agents .diary specs plans docs
do
    mkdir -p "$work/deep/a/$dir/b/node_modules" "$work/deep/a/$dir/c/target"
    touch "$work/deep/a/$dir/b/package.json" "$work/deep/a/$dir/c/Cargo.toml" \
        "$work/deep/a/$dir/c/target/CACHEDIR.TAG"
done
age_tree "$work" 400

out=$(echo n | ./diskclean "$work")
check "lists node_modules" has app/node_modules "$out"
check "lists target" has crate/target "$out"
check "lists worktree target" has proj/.pr1/target "$out"
check "skips node_modules without package.json" lacks proj/.pr1/node_modules \
    "$out"
check "skips target without Cargo.toml" lacks loose "$out"
check "skips hidden dirs under home" lacks .bun "$out"
check "does not list target without tag" lacks untagged/target "${out%%kept:*}"
check "reports target without tag" \
    has "kept: 1 target without CACHEDIR.TAG (untagged/target)" "$out"
check "nested node_modules is not a row" lacks nest/node_modules/inner "$out"
check "lists nest once" has nest/node_modules "$out"
check "lists project under deep dirs" has deep/a/ok/b/node_modules "$out"
for dir in .git .claude .codex .agents .diary specs plans docs
do
    check "never enters $dir" lacks "a/$dir/" "$out"
done
check "declined keeps dirs" test -d "$work/app/node_modules/x"
check "declined prunes nothing" lacks "stub " "$out"
check "table header" has "last use   size  kind           path" "$out"
check "target size skips deploy" \
    test -n "$(grep -E '^ +400d +[0-9.]+K +target +crate/target$' <<< "$out")"
check "summary total" has " total " "$out"
check "summary per kind" \
    test -n "$(grep -E '^ node_modules +[0-9]+ +[0-9.]+[KM]?$' <<< "$out")"
out=$(./diskclean "$work/.bun/install" 2>&1)
check "root inside a tool home is refused" \
    has "Refusing a root inside a hidden dir under home" "$out"
./diskclean "$work/.bun" >/dev/null 2>&1
check "root equal to a tool home exits 2" test $? = 2
for dir in .git .claude .codex .agents .diary specs plans docs
do
    ./diskclean "$work/deep/a/$dir" >/dev/null 2>&1
    check "root equal to $dir exits 2" test $? = 2
    out=$(./diskclean "$work/deep/a/$dir/b" 2>&1)
    check "root under $dir is refused" has "Refusing a root inside $dir" "$out"
done
ln -s "$work/.bun/install" "$work/toolhome-link"
./diskclean "$work/toolhome-link" >/dev/null 2>&1
check "symlinked root is resolved before the hidden check" test $? = 2
ln -s "$work/deep/a/ok" "$work/ok-link"
out=$(echo n | ./diskclean "$work/ok-link")
check "symlinked root is searched resolved" has deep/a/ok/b/node_modules "$out"
rm -- "$work/toolhome-link" "$work/ok-link"

out=$(echo y | ./diskclean)
check "defaults to home" has app/node_modules "$out"
check "level 1 runs no prunes" lacks "stub " "$out"
check "removes node_modules" test ! -e "$work/app/node_modules"
check "keeps the project beside node_modules" test -f "$work/app/package.json"
check "reports what was removed" has "removed 5 dirs," "$out"
check "empties target" test ! -e "$work/crate/target/debug"
check "keeps target/deploy" test -f "$work/crate/target/deploy/k.json"
check "keeps target without Cargo.toml" test -d "$work/loose/target/keep"
check "keeps hidden dirs" test -d "$work/.bun/install/node_modules"
check "keeps untagged target" test -d "$work/untagged/target/debug"
check "empties worktree target" test ! -e "$work/proj/.pr1/target/debug"
for dir in .git .claude .codex .agents .diary specs plans docs
do
    check "keeps $dir contents" test -d "$work/deep/a/$dir/b/node_modules" \
        -a -d "$work/deep/a/$dir/c/target"
done
check "level 1 leaves toolchains" lacks "stub rustup" "$out"

tc=$work/.rustup/toolchains
mkdir -p "$work/l2/node_modules" "$work/linked-tools/bin" "$work/pinproj"
touch "$work/linked-tools/bin/rustc"
for name in 1.82.0 1.83.0 1.84.0 stable nightly
do
    mkdir -p "$tc/$name-x86_64-unknown-linux-gnu/bin"
    touch "$tc/$name-x86_64-unknown-linux-gnu/bin/rustc"
done
mkdir -p "$tc/1.85.0-x86_64-unknown-linux-gnu"
touch "$work/l2/package.json"
ln -s "$work/linked-tools" "$tc/1.89.0-sbpf-x"
printf '[toolchain]\nchannel = "1.83.0"\n' > "$work/pinproj/rust-toolchain.toml"
age_tree "$work/.rustup" 400

out=$(echo n | ./diskclean -2 "$work")
check "level 2 runs level 1 first" has "last use" "$out"
check "level 2 reaches docker" has "stub docker system df" "$out"
check "level 1 alone leaves docker" lacks "stub docker system df" \
    "$(echo n | ./diskclean -1 "$work")"

out=$(printf 'n\ny\nn\n' | ./diskclean -2 "$work")
check "lists numbered toolchains" has 1.82.0-x86_64-unknown-linux-gnu "$out"
check "uninstalls numbered toolchains" \
    has "stub rustup toolchain uninstall 1.82.0-x86_64-unknown-linux-gnu" "$out"
table=${out%%kept:*}
check "keeps the default" lacks 1.84.0 "$table"
check "keeps stable" lacks stable "$table"
check "keeps nightly" lacks nightly "$table"
check "keeps linked toolchains" lacks sbpf "$table"
check "keeps pinned toolchains" lacks 1.83.0 "$table"
check "ignores a toolchain without bin/rustc" lacks 1.85.0 "$out"
check "names the pin" has "pinned by pinproj" "$out"
check "names the default" has "default or active" "$out"
check "names the link" has "1 symlink" "$out"
check "declined prunes nothing" lacks "stub qemubox prune" "$out"

out=$(printf 'n\nn\nn\n' | RUSTUP_HOME=$work/elsewhere ./diskclean -2 "$work")
check "honours RUSTUP_HOME" has "nothing to clean at level 2" "$out"

out=$(printf 'n\nn\nn\n' | ./diskclean -2 "$work")
check "lists anonymous volumes" has "$anon" "$out"
check "declined runs no qemubox prune" lacks "stub qemubox prune" "$out"
check "declined removes no volumes" lacks "volume rm" "$out"

mkdir "$work/gocache"
head -c 1048576 /dev/zero > "$work/gocache/blob"
out=$(printf 'n\nn\nn\n' | ./diskclean -2 "$work")
check "lists the prunes with a store size" \
    test -n "$(grep -E '^ +go clean -cache +1\.[0-9]M$' <<< "$out")"
check "declined runs no prunes" lacks "stub pnpm store prune" "$out"

out=$(printf 'n\nn\ny\n' | ./diskclean -2 "$work")
for prune in "pnpm store prune" "bun pm cache rm" "uv cache prune" \
    "pip cache purge" "pre-commit gc" "yay -Sc" "go clean -cache" \
    "go clean -modcache" "docker image prune -a -f" "docker builder prune -f" \
    "qemubox prune" "dockbox prune 0"
do
    check "runs $prune" has "stub $prune" "$out"
done
check "removes anonymous volumes" has "stub docker volume rm $anon" "$out"
check "keeps named volumes" lacks pgdata "$out"

mk_node() {
    mkdir -p "$1/node_modules/x"
    touch "$1/package.json"
    age_tree "$1" 400
}

mk_crate() {
    mkdir -p "$1/target/debug"
    touch "$1/Cargo.toml" "$1/target/CACHEDIR.TAG" "$1/target/debug/obj"
    age_tree "$1" 400
}

ask_session() {
    local root=$1 answer=$2 i
    shift 2
    rm -f -- "$work/session.in"
    mkfifo "$work/session.in"
    ./diskclean ${session_flags:-} "$root" < "$work/session.in" \
        > "$work/session.out" 2>&1 &
    session_pid=$!
    exec 3> "$work/session.in"
    for i in $(seq 50)
    do
        if grep -q '\[y/N\]' "$work/session.out"
        then
            break
        fi
        sleep 0.1
    done
    "$@"
    if [[ $answer ]]
    then
        echo "$answer" >&3
    fi
    wait "$session_pid"
    session_status=$?
    exec 3>&-
    session_out=$(< "$work/session.out")
}

mk_node "$work/ask/b"
out=$(echo n | ./diskclean "$work/ask" 2>&1)
check "the prompt is printed" has "[y/N]" "$out"
out=$(echo y | ./diskclean -l "$work/ask" 2>&1)
check "-l lists" has ask/b/node_modules "$out"
check "-l never prompts" lacks "[y/N]" "$out"
check "-l removes nothing" test -d "$work/ask/b/node_modules"
check "-l runs no prunes" lacks "stub " "$out"
out=$(echo n | ./diskclean -2 -l "$work/ask" 2>&1)
check "-l never prompts at level 2" lacks "[y/N]" "$out"

mk_node "$work/mounted"
export MOUNTED=$work/mounted/node_modules
out=$(echo y | ./diskclean "$work/mounted")
unset MOUNTED
check "mount point is kept" has "kept: 1 mount point (mounted/node_modules)" "$out"
check "mount point is not removed" test -d "$work/mounted/node_modules/x"

mk_node "$work/holder"
mkdir "$work/holder/node_modules/.git"
out=$(echo y | ./diskclean "$work/holder")
check "node_modules holding .git is kept" \
    has "kept: 1 holds .git (holder/node_modules)" "$out"
check "node_modules holding .git is not removed" \
    test -d "$work/holder/node_modules/x"

mk_crate "$work/clone"
mkdir "$work/clone/target/.git"
out=$(echo y | ./diskclean "$work/clone")
check "target holding .git is kept" \
    has "kept: 1 holds .git (clone/target)" "$out"
check "target holding .git is not removed" test -f "$work/clone/target/debug/obj"

mk_crate "$work/reproof"
ask_session "$work/reproof" y rm -- "$work/reproof/Cargo.toml"
check "re-proof skips a changed candidate" \
    has "skip: reproof/target changed since listing" "$session_out"
check "re-proof leaves the candidate" test -f "$work/reproof/target/debug/obj"
check "skip is not a failure" test "$session_status" = 0

mk_node "$work/swap"
swap_for_symlink() {
    mv -- "$work/swap/node_modules" "$work/swap/real"
    ln -s "$work/swap/real" "$work/swap/node_modules"
}
ask_session "$work/swap" y swap_for_symlink
check "symlink swapped in is skipped" \
    has "skip: swap/node_modules changed since listing" "$session_out"
check "symlink target survives" test -d "$work/swap/real/x"

mk_node "$work/gitted"
add_git() {
    mkdir "$work/gitted/node_modules/.git"
}
ask_session "$work/gitted" y add_git
check "a .git appearing is skipped" \
    has "skip: gitted/node_modules changed since listing" "$session_out"
check "a .git appearing keeps the dir" test -d "$work/gitted/node_modules/x"

mk_node "$work/term"
term_session() {
    kill -TERM "$session_pid"
}
ask_session "$work/term" n term_session
check "TERM exits 1" test "$session_status" = 1
check "TERM reports what was removed" has "interrupted: 0 dirs," "$session_out"
check "TERM removes nothing" test -d "$work/term/node_modules/x"

mk_node "$work/unread/a"
mk_node "$work/unread/b"
mkdir -p "$work/unread/a/node_modules/x/closed"
chmod 000 "$work/unread/a/node_modules/x/closed"
out=$(echo y | ./diskclean "$work/unread" 2>/dev/null)
status=$?
chmod 755 "$work/unread/a/node_modules/x/closed"
check "unreadable candidate is counted" \
    has "kept: 1 unreadable (unread/a/node_modules)" "$out"
check "unreadable candidate is not listed" lacks unread/a "${out%%kept:*}"
check "readable candidate is still removed" test ! -e "$work/unread/b/node_modules"
check "unreadable candidate is not removed" test -d "$work/unread/a/node_modules"
check "unreadable candidate is not a failure" test "$status" = 0

mkdir -p "$work/onlyunread/node_modules/closed"
touch "$work/onlyunread/package.json"
chmod 000 "$work/onlyunread/node_modules/closed"
out=$(echo y | ./diskclean "$work/onlyunread" 2>&1)
chmod 755 "$work/onlyunread/node_modules/closed"
check "no candidates prints nothing found" has "nothing to clean" "$out"
check "no candidates does not prompt" lacks "[y/N]" "$out"
check "no candidates runs no prunes" lacks "stub " "$out"

mk_node "$work/fail/a"
mk_node "$work/fail/b"
touch "$work/fail/a/node_modules/x/y"
age_tree "$work/fail/a" 400
chmod 500 "$work/fail/a/node_modules/x"
out=$(echo y | ./diskclean "$work/fail" 2>&1)
status=$?
chmod 755 "$work/fail/a/node_modules/x"
check "failed rm is reported" has "Failed: $work/fail/a/node_modules" "$out"
check "failed rm exits 1" test "$status" = 1
check "run continues after a failed rm" test ! -e "$work/fail/b/node_modules"

rmstub=$(mktemp -d)
printf '#!/bin/sh\necho "$*" >> "%s/rm.log"\nexec /bin/rm "$@"\n' \
    "$rmstub" > "$rmstub/rm"
chmod +x "$rmstub/rm"
mk_node "$work/mnt/a"
mk_node "$work/mnt/b"
age_tree "$work/mnt" 400
out=$(echo y | PATH=$rmstub:$PATH ./diskclean "$work/mnt" 2>&1)
check "removal runs rm within one filesystem" \
    test "$(grep -c -- '-rf --one-file-system' "$rmstub/rm.log")" = 2
rm -- "$rmstub/rm" "$rmstub/rm.log"
rmdir -- "$rmstub"

mk_aged() {
    mk_node "$1"
    head -c $(( $3 * 1024 )) /dev/zero > "$1/node_modules/x/blob"
    age_tree "$1" "$2"
}

all_three="lu/a/node_modules lu/b/node_modules lu/c/node_modules "
order_of() {
    grep -oE 'lu/[abc]/node_modules' <<< "$1" | tr '\n' ' '
}

mk_aged "$work/lu/a" 400 300
mk_aged "$work/lu/b" 300 200
mk_aged "$work/lu/c" 0 100
touch -a -d "@$(( $(date +%s) - 86400 ))" "$work/lu/b/node_modules/x/blob"

out=$(./diskclean -l "$work/lu")
check "default age lists the stale project" has lu/a/node_modules "$out"
check "default age hides the read project" lacks lu/b "$out"
check "default age hides the fresh project" lacks lu/c "$out"
check "default age counts what it hid" has "kept: 2 used within 30d" "$out"
check "header says atime is recorded" has "atime recorded: yes" "$out"
check "last use is the age in days" \
    test -n "$(grep -E '^ +400d +[0-9.]+K +node_modules +lu/a/node_modules$' \
        <<< "$out")"

out=$(MNT_OPTS=rw,noatime ./diskclean -l "$work/lu")
check "noatime ignores reads" has lu/b/node_modules "$out"
check "noatime header" has "atime recorded: no" "$out"
check "noatime still hides the fresh project" lacks lu/c "$out"

out=$(./diskclean -l -o 0 "$work/lu")
check "relatime order is stalest first" \
    test "$(order_of "$out")" = "$all_three"
out=$(MNT_OPTS=rw,noatime ./diskclean -l -o 0 "$work/lu")
check "noatime order is stalest first" \
    test "$(order_of "$out")" = "$all_three"
out=$(./diskclean -l -o 0 "$work/lu")
check "-o 0 hides nothing" lacks "kept:" "$out"

out=$(./diskclean -l -o 350d "$work/lu")
check "-o filters by age" test "$(order_of "$out")" = "lu/a/node_modules "
out=$(MNT_OPTS=rw,noatime ./diskclean -l -o 100d "$work/lu")
check "-o under noatime keeps the unread ones" \
    test "$(order_of "$out")" = "lu/a/node_modules lu/b/node_modules "
out=$(./diskclean -l -o 100 "$work/lu")
check "-o bare number is days" test "$(order_of "$out")" = "lu/a/node_modules "

out=$(echo n | ./diskclean -2 -l "$work/lu")
check "-2 also offers the recently used" \
    test "$(order_of "$out")" = "$all_three"

mk_node "$work/future"
touch -d tomorrow "$work/future/package.json"
out=$(./diskclean -l -o 0 "$work/future")
check "a future timestamp is clamped to 0d" \
    test -n "$(grep -E '^ +0d +[0-9.K]+ +node_modules +future/node_modules$' \
        <<< "$out")"

mk_node "$work/quiet"
touch "$work/quiet/package.json"
out=$(./diskclean -l "$work/quiet")
check "fresh source keeps an old node_modules" lacks quiet/node_modules "$out"
mk_node "$work/pull"
mkdir "$work/pull/.git"
touch "$work/pull/.git/FETCH_HEAD"
out=$(./diskclean -l "$work/pull")
check "a git fetch counts as use" lacks pull/node_modules "$out"

cache_tag="Signature: 8a477f597d28d172789f06886806bc55"
mk_files() {
    local file
    for file
    do
        mkdir -p "${file%/*}"
        touch "$file"
    done
}

k=$work/k
mk_files "$k/n/package.json" "$k/n/.next/package.json" "$k/n/.next/cache/x" \
    "$k/p/.pnpm-store/v3/files/ab/cd" "$k/v/.venv/pyvenv.cfg" \
    "$k/v/.venv/lib/__pycache__/m.pyc" "$k/v2/venv/pyvenv.cfg" \
    "$k/py/pyproject.toml" "$k/py/pkg/a.py" "$k/py/pkg/__pycache__/a.pyc" \
    "$k/py/pkg/sub/__pycache__/b.pyc" "$k/tc/pyproject.toml" \
    "$k/go/go.mod" "$k/go/gopath/pkg/mod/cache/download/x" \
    "$k/go/gopath/pkg/mod/github.com/a@v1/f.go"
mk_files "$k/dn/package.json" "$k/dn/.next/cache/x" \
    "$k/dp/.pnpm-store/v3/nofiles/x" "$k/dv/venv/bin/python" \
    "$k/dv/.venv/x" "$k/dv/venv/lib/__pycache__/m.pyc" \
    "$k/dpy/pyproject.toml" "$k/dpy/__pycache__/readme.txt" \
    "$k/dtc/pyproject.toml" "$k/dtc/.mypy_cache/x" "$k/dtc/.ruff_cache/y" \
    "$k/dg1/go.mod" "$k/dg1/pkg/mod/other/x" \
    "$k/dg2/pkg/mod/cache/download/x" \
    "$k/dd/package.json" "$k/dd/data/x" "$k/dd/cache/x" "$k/dd/.cache/x" \
    "$k/dd/build/x" "$k/dd/dist/x" "$k/dd/tmp/x" \
    "$k/cc/package.json" "$k/cc/.cache/ccache/0/CACHEDIR.TAG"
for dir in "$k/tc/.ruff_cache" "$k/tc/.pytest_cache" "$k/cc/.cache/ccache/0"
do
    mkdir -p "$dir"
    echo "$cache_tag" > "$dir/CACHEDIR.TAG"
done
echo "Signature: 0123456789abcdef" > "$k/dtc/.ruff_cache/CACHEDIR.TAG"
age_tree "$k" 400
chmod -R a-w "$k/go/gopath/pkg/mod"

out=$(./diskclean -l "$k")
row() { grep -E "$1" <<< "$out"; }
check "lists next" test -n "$(row ' next +k/n/.next$')"
check "lists pnpm-store" test -n "$(row ' pnpm-store +k/p/.pnpm-store$')"
check "lists .venv" test -n "$(row ' venv +k/v/.venv$')"
check "lists venv" test -n "$(row ' venv +k/v2/venv$')"
check "lists each pycache" \
    test -n "$(row ' pycache +k/py/pkg/__pycache__$')" -a \
    -n "$(row ' pycache +k/py/pkg/sub/__pycache__$')"
check "lists each toolcache" \
    test -n "$(row ' toolcache +k/tc/\.ruff_cache$')" -a \
    -n "$(row ' toolcache +k/tc/\.pytest_cache$')"
check "lists gomod" test -n "$(row ' gomod +k/go/gopath/pkg/mod$')"
check "last use of a cache is its parent's" \
    test -n "$(row '^ +400d +[0-9.K]+ +pycache ')"
for decoy in dn dp dv dpy dtc dg1 dg2 dd cc
do
    check "lists nothing from decoy $decoy" lacks "k/$decoy" "$out"
done
check "pruned venv hides its pycache" lacks k/v/.venv/lib "$out"
check "-k list has every walked kind" test "$(./diskclean -k list | grep -c '^1 ')" = 8

out=$(./diskclean -l "$k/v")
check "root that is the project finds .venv" has "k/v/.venv" "$out"

mk_files "$work/fh/package.json" "$work/fh/node_modules/x" \
    "$work/fh/pyproject.toml" "$work/fh/__pycache__/a.pyc" \
    "$work/fh/ok/package.json" "$work/fh/ok/node_modules/x"
age_tree "$work/fh" 400
out=$(HOME=$work/fh ./diskclean -l)
check "project at home is kept" has "2 project is home" "$out"
check "project at home is not listed" lacks " fh/node_modules" "$out"
check "project below home is listed" has " ok/node_modules" "$out"

out=$(echo y | ./diskclean "$k")
for gone in n/.next p/.pnpm-store v/.venv v2/venv py/pkg/__pycache__ \
    py/pkg/sub/__pycache__ tc/.ruff_cache tc/.pytest_cache go/gopath/pkg/mod
do
    check "removes $gone" test ! -e "$k/$gone"
done
for kept in n/package.json py/pyproject.toml \
    py/pkg/a.py tc/pyproject.toml go/go.mod go/gopath/pkg dn/.next/cache/x \
    dp/.pnpm-store/v3/nofiles/x dv/venv/bin/python dv/.venv/x \
    dv/venv/lib/__pycache__/m.pyc dpy/__pycache__/readme.txt \
    dtc/.mypy_cache/x dtc/.ruff_cache/y dg1/pkg/mod/other/x \
    dg2/pkg/mod/cache/download/x dd/data/x dd/cache/x dd/.cache/x \
    dd/build/x dd/dist/x dd/tmp/x cc/.cache/ccache/0/CACHEDIR.TAG
do
    check "keeps $kept" test -e "$k/$kept"
done
check "reports removed cache dirs" has "removed 9 dirs," "$out"

mk_files "$work/rp/pyproject.toml" "$work/rp/__pycache__/a.pyc"
age_tree "$work/rp" 400
ask_session "$work/rp" y rm -- "$work/rp/__pycache__/a.pyc"
check "re-proof skips a cache that changed" \
    has "skip: rp/__pycache__ changed since listing" "$session_out"

cache=$work/.cache
venvs=$work/.local/share/virtualenvs
mk_files "$cache/solana/v1.48/platform-tools/rust/bin/rustc" \
    "$cache/solana/v1.49/platform-tools/rust/bin/rustc" \
    "$cache/solana/v1.54/platform-tools/rust/bin/rustc" \
    "$cache/solana/v9.9/other/x" "$cache/ms-playwright/chromium-1/INSTALLATION_COMPLETE" \
    "$cache/puppeteer/chrome/124/f" "$venvs/app-Xy3Zk/pyvenv.cfg" \
    "$venvs/app-Xy3Zk/.project" "$venvs/live-1/pyvenv.cfg" \
    "$venvs/live-1/.project" "$venvs/bare-2/pyvenv.cfg" \
    "$venvs/noenv-3/.project" "$work/lp/f"
ln -s "$cache/solana/v1.49/platform-tools/rust" "$tc/1.90.0-sbpf-y"
echo "$work/gone-project" > "$venvs/app-Xy3Zk/.project"
echo "$work/lp" > "$venvs/live-1/.project"
age_tree "$cache" 400
age_tree "$work/.local" 400
age_tree "$work/lp" 400

out=$(./diskclean -2 -l -o 0 -k platform-tools,pipenv,browsers "$work")
row() { grep -E "$1" <<< "$out"; }
check "level 2 skips the level 1 scan" lacks scanning "$out"
check "lists an old platform-tools" \
    test -n "$(row '^ +400d +[0-9.KMG]+ +platform-tools +\.cache/solana/v1.48$')"
check "keeps the newest platform-tools" has "1 newest (.cache/solana/v1.54)" "$out"
check "keeps platform-tools a toolchain links to" \
    has "1 linked by rustup (.cache/solana/v1.49)" "$out"
check "ignores a version dir without platform-tools" lacks v9.9 "$out"
check "lists an orphan pipenv env first" \
    test -n "$(row '^ +never +[0-9.KMG]+ +pipenv +\.local/share/virtualenvs/app-Xy3Zk +\(project gone\)$')"
check "lists a pipenv env by its project's activity" \
    test -n "$(row '^ +400d +[0-9.KMG]+ +pipenv +\.local/share/virtualenvs/live-1$')"
check "ignores a pipenv env without .project" lacks bare-2 "$out"
check "ignores a .project without pyvenv.cfg" lacks noenv-3 "$out"
check "lists playwright browsers" \
    test -n "$(row ' browsers +\.cache/ms-playwright$')"
check "lists puppeteer browsers" test -n "$(row ' browsers +\.cache/puppeteer$')"
check "rustup stays out of a narrowed run" lacks toolchains/ "$out"

mkdir -p "$work/xdg/ms-playwright/chromium-1" "$work/xdg/puppeteer/other" \
    "$work/xdg/solana/v1.2/platform-tools/rust"
touch "$work/xdg/ms-playwright/chromium-1/x" "$work/xdg/puppeteer/other/x"
age_tree "$work/xdg" 400
out=$(XDG_CACHE_HOME=$work/xdg ./diskclean -2 -l -o 0 -k platform-tools,browsers "$work")
check "XDG_CACHE_HOME moves the cache" lacks ".cache/" "$out"
check "browsers without a marker are ignored" lacks ms-playwright "$out"
check "a lone platform-tools is the newest" has "1 newest (xdg/solana/v1.2)" "$out"

mkdir "$work/pinsess"
session_flags="-2 -k rustup"
pin_appears() {
    echo 1.82.0 > "$work/pinsess/rust-toolchain"
}
ask_session "$work/pinsess" y pin_appears
check "a pin appearing is skipped" \
    has "skip: .rustup/toolchains/1.82.0-x86_64-unknown-linux-gnu changed" \
    "$session_out"
check "the unpinned toolchain still goes" \
    has "stub rustup toolchain uninstall 1.83.0-x86_64-unknown-linux-gnu" \
    "$session_out"
check "the pinned toolchain stays" \
    lacks "uninstall 1.82.0-x86_64-unknown-linux-gnu" "$session_out"
rm -- "$work/pinsess/rust-toolchain"
default_appears() {
    echo "1.82.0-x86_64-unknown-linux-gnu (default)" > "$work/rustup.extra"
}
RUSTUP_EXTRA=$work/rustup.extra ask_session "$work/pinsess" y default_appears
check "a new default is skipped" \
    has "skip: .rustup/toolchains/1.82.0-x86_64-unknown-linux-gnu changed" \
    "$session_out"
rm -- "$work/rustup.extra"
session_flags="-2 -k platform-tools"
link_appears() {
    ln -s "$cache/solana/v1.48/platform-tools/rust" "$tc/1.91.0-link"
}
ask_session "$work/pinsess" y link_appears
check "a toolchain link appearing is skipped" \
    has "skip: .cache/solana/v1.48 changed since listing" "$session_out"
check "a linked platform-tools stays" \
    test -f "$cache/solana/v1.48/platform-tools/rust/bin/rustc"
rm -- "$tc/1.91.0-link"
session_flags=

out=$(echo y | ./diskclean -2 -k platform-tools,pipenv,browsers "$work")
check "removes an old platform-tools" test ! -e "$cache/solana/v1.48"
check "removes an orphan pipenv env" test ! -e "$venvs/app-Xy3Zk"
check "removes a pipenv env" test ! -e "$venvs/live-1"
check "removes playwright browsers" test ! -e "$cache/ms-playwright"
check "removes puppeteer browsers" test ! -e "$cache/puppeteer"
check "keeps the project of a removed env" test -f "$work/lp/f"
check "keeps the newest platform-tools" test -d "$cache/solana/v1.54"
check "keeps the linked platform-tools" test -d "$cache/solana/v1.49"
check "keeps the version dir without platform-tools" test -d "$cache/solana/v9.9"
check "keeps pipenv dirs without both markers" \
    test -d "$venvs/bare-2" -a -d "$venvs/noenv-3"
check "a narrowed run prunes nothing" lacks "stub " "$out"

mk_crate "$work/kt"
mk_files "$work/kt/package.json" "$work/kt/node_modules/x" \
    "$work/kt/.next/package.json"
age_tree "$work/kt" 400
out=$(./diskclean -l -o 0 -k next "$work/kt")
check "-k narrows level 1" test -n "$(grep -E ' next +kt/.next$' <<< "$out")"
check "-k drops the other level 1 kinds" lacks node_modules "$out"
out=$(echo y | ./diskclean -k target "$work/kt")
check "-k target removes target" test ! -e "$work/kt/target/debug"
check "-k target keeps node_modules" test -d "$work/kt/node_modules"
check "-k without prunes runs none" lacks "stub " "$out"
out=$(echo n | ./diskclean -2 -k prunes "$work")
check "-k prunes lists no table" lacks "last use" "$out"
check "-k prunes reaches the prunes" has "stub docker system df" "$out"

if (( fail ))
then
    exit 1
fi
echo "all passed"
