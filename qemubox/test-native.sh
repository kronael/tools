#!/usr/bin/env bash
set -Eeuo pipefail

[[ "${QEMUBOX_NATIVE:-}" = 1 ]] || {
    echo 'Set QEMUBOX_NATIVE=1 to run disposable VM checks' >&2
    exit 2
}
production=${QEMUBOX_NATIVE_BASE:?Set QEMUBOX_NATIVE_BASE to a production qemubox state directory}
parent=${QEMUBOX_NATIVE_DIR:?Set QEMUBOX_NATIVE_DIR to an existing disk-backed fixture directory}
[[ -d "$parent" && "$(findmnt -n -o FSTYPE -T "$parent")" != tmpfs ]] || {
    echo 'Native fixtures require an existing disk-backed directory' >&2
    exit 2
}
parent=$(realpath -e "$parent")
production=$(realpath -e "$production")
[[ ! -e /tmp/capture.png && ! -L /tmp/capture.png ]] || {
    echo 'Native screenshot check requires /tmp/capture.png to be absent' >&2
    exit 2
}
launcher=$(realpath ./qemubox)
run=$(mktemp -d "$parent/qemubox-native.XXXXXXXX")
chmod 700 "$run"
export HOME="$run/home" QEMUBOX_HOME="$run/state"
unset CLAUDE_CODE_OAUTH_TOKEN OPENAI_API_KEY CODEX_API_KEY GH_TOKEN GITHUB_TOKEN
unset DOCKER_HOST DOCKER_CONTEXT CODEX_HOME CODEX_SQLITE_HOME
export QEMUBOX_MEM="${QEMUBOX_NATIVE_MEM:-4096}"
export QEMUBOX_SWAP="${QEMUBOX_NATIVE_SWAP:-1024}"
export QEMUBOX_DISK=12G QEMUBOX_LINGER=1200 QEMUBOX_READY_TIMEOUT=120
export GNUPGHOME="$HOME/.gnupg"
main="native-${run##*.}"
ssh_pid=''
capture_inode=''
cleanup() {
    local rc=$? name dir
    trap - EXIT INT TERM
    for dir in "$QEMUBOX_HOME"/*
    do
        [[ -d "$dir" && "${dir##*/}" != base ]] || continue
        name=${dir##*/}
        timeout 20 bash "$launcher" stop "$name" >&2 || rc=1
    done
    [[ -z "$ssh_pid" ]] || kill "$ssh_pid" || rc=1
    timeout 10 gpgconf --kill gpg-agent || rc=1
    if [[ -n "$capture_inode" && -f /tmp/capture.png &&
        "$(stat -c %d:%i /tmp/capture.png)" = "$capture_inode" ]]
    then
        rm /tmp/capture.png || rc=1
    fi
    echo "native fixture retained: $run" >&2
    exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -p "$HOME" "$GNUPGHOME" "$QEMUBOX_HOME/base/kernel" "$run/project" \
    "$run/readonly" "$run/private" "$HOME/.claude/skills"
chmod 700 "$GNUPGHOME" "$run/private"
image=$(cat "$production/base/current")
kernel=$(cat "$production/base/kernel/current")
[[ "$image" =~ ^[a-f0-9]{64}$ && "$kernel" =~ ^[a-f0-9]{64}$ ]]
[[ -s "$production/base/$image/exported" && -d "$production/base/$image/rootfs" ]]
[[ -x "$production/base/$image/rootfs/usr/local/bin/qemubox-codex-bridge" ]] || {
    echo 'Production base must include the qemubox Codex bridge' >&2
    exit 2
}
[[ -s "$production/base/kernel/$kernel/bzImage" && -s "$production/base/kernel/$kernel/initrd" ]]
printf '%s\n' "$image" > "$QEMUBOX_HOME/base/current"
printf '%s\n' "$kernel" > "$QEMUBOX_HOME/base/kernel/current"
ln -s "$(realpath "$production/base/$image")" "$QEMUBOX_HOME/base/$image"
ln -s "$(realpath "$production/base/kernel/$kernel")" "$QEMUBOX_HOME/base/kernel/$kernel"
printf 'fixture wisdom\n' > "$HOME/.claude/CLAUDE.md"
(set -o noclobber; printf 'fixture screenshot one\n' > /tmp/capture.png)
capture_inode=$(stat -c %d:%i /tmp/capture.png)
printf 'readonly fixture\n' > "$run/readonly/probe"
printf 'payload\000stdin\377\n' > "$run/project/payload"
mkdir -p "$run/project/node_modules"
git init -q "$run/project"
git -C "$run/project" -c user.name=Fixture -c user.email=fixture@example.test \
    -c commit.gpgsign=false commit -qm fixture --allow-empty
git -C "$run/project" worktree add -q --detach "$run/worktree"
ssh-keygen -q -t ed25519 -N '' -f "$run/private/sign"
cp "$run/private/sign.pub" "$run/project/sign.pub"
printf 'fixture %s\n' "$(cat "$run/project/sign.pub")" > "$run/project/allowed-signers"
ssh-agent -a "$run/private/ssh-agent" -s > "$run/ssh-agent.env"
ssh_pid=$(sed -n 's/^SSH_AGENT_PID=\([0-9]*\);.*/\1/p' "$run/ssh-agent.env")
[[ "$ssh_pid" =~ ^[0-9]+$ ]]
export SSH_AUTH_SOCK="$run/private/ssh-agent" SSH_AGENT_PID="$ssh_pid"
ssh-add "$run/private/sign" >/dev/null 2>&1
timeout 30 gpg --batch --pinentry-mode loopback --passphrase '' \
    --quick-generate-key 'Fixture <fixture@example.test>' ed25519 sign 0 > "$run/keygen.log" 2>&1
fingerprint=$(gpg --batch --with-colons --list-keys | awk -F: '$1=="fpr" {print $10; exit}')
docker=${QEMUBOX_NATIVE_DOCKER:-docker}
host_id=$(timeout 10 "$docker" --host=unix:///var/run/docker.sock info --format '{{.ID}}')
[[ -n "$host_id" ]]
cd "$run/project"
box() {
    timeout --foreground 180 bash "$launcher" -n "$main" \
        -v "$run/project:rw" -v "$run/readonly" "$@"
}
control() {
    QEMUBOX_LIB=1 source "$launcher"
    "$@"
}
echo 'native: cold and warm binary streams'
for boot in cold warm
do
    rc=0
    box exec bash -c 'cat; echo fixture-stderr >&2; exit 37' \
        < "$run/project/payload" > "$run/$boot.out" 2> "$run/$boot.err" || rc=$?
    [[ "$rc" = 37 ]]
    cmp "$run/project/payload" "$run/$boot.out"
    grep -Fxq fixture-stderr "$run/$boot.err"
done
echo 'native: identity, mounts, guidance and literal environment'
export FIXTURE_EXPORTED='exported value'
value=$'literal = $(false); `false`\ntrailing newline\n'
box -e "FIXTURE_VALUE=$value" -e FIXTURE_EMPTY= -e FIXTURE_EXPORTED \
    exec python3 -c '
import os
import sys
assert os.environ["FIXTURE_VALUE"] == sys.argv[1]
assert os.environ["FIXTURE_EMPTY"] == ""
assert os.environ["FIXTURE_EXPORTED"] == "exported value"
' "$value"
box exec bash -c '
    set -e
    test "$(id -u)" = "$1"; test "$(id -g)" = "$2"
    for gid in $3
    do
        id -G | tr " " "\n" | grep -qx "$gid"
    done
    sudo -n true
    touch "$4/guest-write"
    test "$(stat -c %u:%g "$4/guest-write")" = "$1:$2"
    ! touch "$5/forbidden" 2>/dev/null
    ! sudo -n touch "$5/forbidden-root" 2>/dev/null
    test "$(findmnt -n -o FSTYPE -T /)" = overlay
    grep -q CLAUDE_SANDBOX=qemubox /etc/claude-code/CLAUDE.md
    test "$(cat /tmp/capture.png)" = "fixture screenshot one"
    ! echo forbidden >> /tmp/capture.png
    ! sudo -n sh -c "echo forbidden >> /tmp/capture.png"
' fixture "$(id -u)" "$(id -g)" "$(id -G)" "$run/project" "$run/readonly"
printf 'fixture screenshot two\n' > /tmp/capture.png
box exec bash -c 'test "$(cat /tmp/capture.png)" = "fixture screenshot two"'
box -e "HOME=$HOME" exec bash -c '
    set -e
    qemubox-codex-bridge
    test "$(readlink "$HOME/.agents/skills")" = ../.claude/skills
    cmp /opt/qemubox/codex-AGENTS.md "$HOME/.codex/AGENTS.md"
    printf "custom fixture guidance\n" > "$HOME/.codex/AGENTS.md"
    qemubox-codex-bridge
    grep -qx "custom fixture guidance" "$HOME/.codex/AGENTS.md"
'
(cd "$run/worktree"; timeout --foreground 180 bash "$launcher" \
    -n "$main-w" -U exec git status --porcelain)
timeout 20 bash "$launcher" stop "$main-w"
echo 'native: SSH and GPG fixture signing'
box -A exec bash -c '
    set -e
    ssh-keygen -Y sign -n file -f "$1/sign.pub" < "$1/payload" > "$1/ssh.sig"
    ssh-keygen -Y verify -f "$1/allowed-signers" -I fixture -n file -s "$1/ssh.sig" < "$1/payload"
' fixture "$run/project"
box -K exec gpg --batch --local-user "$fingerprint" \
    --output "$run/project/gpg.sig" --detach-sign "$run/project/payload"
gpg --batch --verify "$run/project/gpg.sig" "$run/project/payload" > "$run/gpg-verify.log" 2>&1
echo 'native: Docker isolation, networking, DNS, build and busy lifetime'
guest_id=$(box exec docker info --format '{{.ID}}')
[[ -n "$guest_id" && "$guest_id" != "$host_id" ]]
box exec bash -c '
    set -e
    docker pull alpine:3.21 >/dev/null
    test "$(docker run --rm alpine:3.21 id -u)" = 0
    touch /tmp/guest-root-marker
    docker run --rm --privileged -v /:/guest:ro alpine:3.21 test -f /guest/tmp/guest-root-marker
    docker run --rm alpine:3.21 wget -q -T 15 -O /dev/null http://example.com
    docker network create fixture >/dev/null
    docker run -d --name fixture-dns --network fixture alpine:3.21 sleep 600 >/dev/null
    docker run --rm --network fixture alpine:3.21 nslookup fixture-dns >/dev/null
    printf "FROM alpine:3.21\nRUN nslookup example.com\n" | docker build -t fixture-build - >/dev/null
'
forward_id=$(box -D exec docker info --format '{{.ID}}')
[[ "$forward_id" = "$host_id" ]]
touch -d '5 hours ago' "$QEMUBOX_HOME/$main/idle"
(control check_box "$main" 0)
(control prune_boxes)
[[ "$(control run_state "$main")" = running ]]
control list_boxes > "$run/list-busy"
grep -q $'running\tbusy\t' "$run/list-busy"
box exec docker rm -f fixture-dns >/dev/null
box exec docker network rm fixture >/dev/null
control list_boxes > "$run/list-idle"
grep -q $'running\tidle\t' "$run/list-idle"
touch -d '5 hours ago' "$QEMUBOX_HOME/$main/idle"
(control check_box "$main" 0)
deadline=$((SECONDS + 20))
while [[ "$(control run_state "$main")" != stopped ]]
do
    ((SECONDS < deadline))
    sleep 0.1
done
[[ ! -f "$QEMUBOX_HOME/$main/capture-stage" ]]
echo 'native: network restrictions, untrusted config and build mounts'
for mode in u h b p
do
    flags=()
    case "$mode" in
        u) flags=(-U) ;;
        h) flags=(-H) ;;
        b) flags=(-B) ;;
        p) flags=(-P) ;;
    esac
    timeout --foreground 180 bash "$launcher" -n "$main-$mode" "${flags[@]}" \
        -v "$run/project:rw" -e "PROJECT=$run/project" exec bash -c '
            set -e
            sudo -n true
            if [[ "$1" = u || "$1" = h ]]
            then
                ! timeout 5 bash -c "echo >/dev/tcp/1.1.1.1/443"
            fi
            if [[ "$1" = u ]]
            then
                test ! -e /mnt/qemubox-home
                test -z "${SSH_AUTH_SOCK:-}${DOCKER_HOST:-}"
            fi
            touch "$PROJECT/node_modules/$1"
            case "$1" in
                b) test "$(findmnt -n -o FSTYPE -T "$PROJECT/node_modules")" = overlay ;;
                p) test "$(findmnt -fn -o FSTYPE -T "$PROJECT/node_modules")" = virtiofs ;;
                *) test "$(findmnt -n -o FSTYPE -T "$PROJECT/node_modules")" = tmpfs ;;
            esac
        ' fixture "$mode"
    timeout 20 bash "$launcher" stop "$main-$mode"
done
[[ -f "$run/project/node_modules/p" && ! -e "$run/project/node_modules/b" ]]
echo 'native: project rc restrictions and random scratch names'
printf '%s\n' '-A -D -K -n attacker -d codex -P -N' > "$run/project/.qemuboxrc"
timeout --foreground 180 bash "$launcher" -n "$main-p" exec bash -c '
    test -z "${SSH_AUTH_SOCK:-}${DOCKER_HOST:-}"
    test ! -s .qemuboxrc
'
for n in 1 2
do
    scratch=$(timeout --foreground 180 bash "$launcher" -U -T exec hostname \
        2> "$run/scratch-$n.err")
    scratch_name=$(sed -n 's/.*running in qemubox-\([^:]*\):.*/\1/p' "$run/scratch-$n.err")
    [[ "$scratch" = qemubox && "$scratch_name" =~ ^[a-z]+-[a-z]+$ ]]
    printf '%s\n' "$scratch_name" > "$run/scratch-$n.name"
    timeout 20 bash "$launcher" stop "$scratch_name"
done
[[ "$(cat "$run/scratch-1.name")" != "$(cat "$run/scratch-2.name")" ]]
if timeout 10 bash "$launcher" -n "$main" -v "$HOME" exec true \
    > "$run/sensitive.out" 2> "$run/sensitive.err"
then
    echo 'Sensitive mount guard accepted the fixture home' >&2
    exit 1
fi
grep -q 'refusing to mount sensitive path' "$run/sensitive.err"
echo 'native matrix passed; authenticated Codex, Claude and pi checks remain parent-owned'
