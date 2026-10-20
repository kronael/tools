#!/bin/bash
set -u

stub=$(mktemp -d)
work=$(mktemp -d)
trap 'rm -rf -- "$stub" "$work"' EXIT
PATH=$stub:$PATH
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

for cmd in pnpm bun pre-commit yay qemubox dockbox
do
    printf '#!/bin/sh\necho "stub %s $*"\n' "$cmd" > "$stub/$cmd"
done
printf '#!/bin/sh\nexit 0\n' > "$stub/df"
cat > "$stub/rustup" <<'EOF'
#!/bin/sh
case "$*" in
    "toolchain list")
        printf '%s\n' 'stable-x86_64-unknown-linux-gnu (default)' \
            1.82.0-x86_64-unknown-linux-gnu \
            nightly-x86_64-unknown-linux-gnu solana ;;
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
check "unknown option" has "unknown option -x" "$(./diskclean -x 2>&1)"
./diskclean -x >/dev/null 2>&1
check "unknown option exits 2" test $? = 2
check "missing dir" has "not a directory" "$(./diskclean "$work/nope" 2>&1)"
./diskclean "$work/nope" >/dev/null 2>&1
check "missing dir exits 2" test $? = 2

check "nothing found" has "no node_modules or target dirs" \
    "$(echo n | ./diskclean "$work")"

mkdir -p "$work/app/node_modules/x" "$work/crate/target/debug" \
    "$work/crate/target/deploy" "$work/loose/target/keep" \
    "$work/.bun/install/node_modules"
touch "$work/app/package.json" "$work/crate/Cargo.toml" \
    "$work/crate/target/deploy/k.json" "$work/.bun/install/package.json"

out=$(echo n | ./diskclean "$work")
check "lists node_modules" has app/node_modules "$out"
check "lists target" has crate/target "$out"
check "skips target without Cargo.toml" lacks loose "$out"
check "skips hidden dirs" lacks .bun "$out"
check "declined keeps dirs" test -d "$work/app/node_modules/x"
check "declined prunes nothing" lacks "stub " "$out"

out=$(echo y | HOME=$work ./diskclean)
check "defaults to home" has app/node_modules "$out"
check "prunes caches" has "stub pnpm store prune" "$out"
check "prunes dangling images" has "stub docker image prune -f" "$out"
check "empties node_modules" test ! -e "$work/app/node_modules/x"
check "empties target" test ! -e "$work/crate/target/debug"
check "keeps target/deploy" test -f "$work/crate/target/deploy/k.json"
check "keeps target without Cargo.toml" test -d "$work/loose/target/keep"
check "keeps hidden dirs" test -d "$work/.bun/install/node_modules"
check "level 1 leaves toolchains" lacks "stub rustup" "$out"

out=$(printf 'n\ny\n' | ./diskclean -2 "$work")
check "lists numbered toolchains" has 1.82.0-x86_64-unknown-linux-gnu "$out"
check "uninstalls numbered toolchains" \
    has "stub rustup toolchain uninstall 1.82.0-x86_64-unknown-linux-gnu" "$out"
check "keeps the default" lacks stable "$out"
check "keeps nightly" lacks nightly "$out"
check "keeps linked toolchains" lacks solana "$out"
check "level 2 leaves docker" lacks "stub docker" "$out"

out=$(printf 'n\nn\nn\n' | ./diskclean -3 "$work")
check "lists anonymous volumes" has "$anon" "$out"
check "declined removes no VMs" lacks "stub qemubox prune" "$out"
check "declined removes no volumes" lacks "volume rm" "$out"

out=$(printf 'n\nn\ny\n' | ./diskclean -3 "$work")
check "prunes VMs" has "stub qemubox prune 0" "$out"
check "prunes boxes" has "stub dockbox prune 0" "$out"
check "prunes unused images" has "stub docker image prune -a -f" "$out"
check "removes anonymous volumes" has "stub docker volume rm $anon" "$out"
check "keeps named volumes" lacks pgdata "$out"

if (( fail ))
then
    exit 1
fi
echo "all passed"
