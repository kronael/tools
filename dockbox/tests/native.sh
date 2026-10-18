#!/bin/bash
set -Eeuo pipefail

here=$(cd "$(dirname "$0")/.." && pwd)
read -ra docker_cmd <<< "${DOCKBOX_DOCKER-docker}"
[[ ${#docker_cmd[@]} -gt 0 ]] || exit 2
export DOCKBOX_IMAGE="${DOCKBOX_IMAGE:-dockbox-native:forky}"
export DOCKBOX_DOCKER="${DOCKBOX_DOCKER-docker}"
unset CLAUDE_CODE_OAUTH_TOKEN OPENAI_API_KEY CODEX_API_KEY GH_TOKEN
unset GITHUB_TOKEN SSH_AUTH_SOCK
tmp=$(mktemp -d)
name="native-$$"
box="dockbox-$name"
pids=()
volumes=()
started=$SECONDS

run_docker() {
    "${docker_cmd[@]}" "$@"
}

cleanup() {
    local status=$?
    trap - EXIT
    run_docker rm -f -v "$box" >/dev/null 2>&1 || true
    if run_docker inspect "$box" >/dev/null 2>&1
    then
        echo "FAIL: task container remains: $box" >&2
        status=1
    fi
    for pid in "${pids[@]}"
    do
        kill "$pid" 2>/dev/null || true
        wait "$pid" 2>/dev/null || true
    done
    for volume in "${volumes[@]}"
    do
        if run_docker volume inspect "$volume" >/dev/null 2>&1
        then
            echo "FAIL: task volume remains: $volume" >&2
            status=1
        fi
    done
    echo "native: retained fixture data: $tmp"
    echo "native: exit $status after $((SECONDS - started))s"
    exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

wait_file() {
    local path=$1
    for ((i = 0; i < 200; i++))
    do
        [[ ! -f "$path" ]] || return 0
        sleep 0.1
    done
    fail "file did not appear: $path"
}

launch() {
    HOME="$tmp/home" "$here/dockbox" -n "$name" "$@"
}

start_session() {
    rm -f "$tmp/input" "$tmp/project/ready" "$tmp/project/release"
    mkfifo "$tmp/input"
    exec 9<>"$tmp/input"
    launch "$@" exec sh -c \
        'read -r gate; test "$gate" = allowed; exec sh -s' \
        < "$tmp/input" 9>&- > "$tmp/session.log" 2>&1 &
    session_pid=$!
    pids+=("$session_pid")
    for ((i = 0; i < 200; i++))
    do
        if run_docker inspect "$box" > "$tmp/inspect.json" 2>/dev/null
        then
            break
        fi
        kill -0 "$session_pid" || {
            cat "$tmp/session.log"
            fail 'launcher exited before inspect'
        }
        sleep 0.1
    done
    python3 "$here/tests/boundary.py" < "$tmp/inspect.json"
    printf 'allowed\n' >&9
    cat >&9 <<'EOF'
set -eu
touch ready
while ! test -f release
do
    sleep 0.1
done
exit 0
EOF
    wait_file "$tmp/project/ready"
}

finish_session() {
    touch "$tmp/project/release"
    wait "$session_pid" || {
        cat "$tmp/session.log"
        fail 'session failed'
    }
    exec 9>&-
}

assert_removed() {
    if run_docker inspect "$box" >/dev/null 2>&1
    then
        fail 'last session retained the box'
    fi
}

mkdir -p "$tmp/home/.claude/skills" "$tmp/home/.codex"
mkdir -p "$tmp/project/node_modules" "$tmp/readonly" "$tmp/repo"
printf 'fixture guidance\n' > "$tmp/home/.claude/CLAUDE.md"
printf '{"sandbox":{"enabled":true}}\n' > \
    "$tmp/home/.claude/settings.json"
printf 'host-dependency\n' > "$tmp/project/node_modules/host"
printf 'readonly\n' > "$tmp/readonly/file"
printf 'unmounted-host-sentinel\n' > "$tmp/sentinel"
cd "$tmp/project"
run_docker info >/dev/null
run_docker image inspect "$DOCKBOX_IMAGE" >/dev/null
host_id=$(run_docker info --format '{{.ID}}')

echo 'native: plain launcher, runtime boundary, UID/GID, mounts, bridge'
start_session -v "$tmp/readonly"
for mutation in runtime socket
do
    python3 - "$tmp/inspect.json" "$mutation" <<'PY' > "$tmp/mutant.json"
import json
import sys
box = json.load(open(sys.argv[1]))
if sys.argv[2] == "runtime":
    box[0]["HostConfig"]["Runtime"] = "runc"
else:
    box[0]["Mounts"].append({"Source": "/var/run/docker.sock"})
json.dump(box, sys.stdout)
PY
    if python3 "$here/tests/boundary.py" < "$tmp/mutant.json" \
        > "$tmp/mutation.log" 2>&1
    then
        fail "boundary guard accepted $mutation mutation"
    fi
    cat "$tmp/mutation.log"
done
launch exec sh -eu -c '
    test "$(id -u)" = "$1"
    test "$(id -g)" = "$2"
    test "$(id -un)" = "$3"
    test "$(awk "/CapAmb/ { print \$2 }" /proc/self/status)" = 0000000000884000
    test ! -S /var/run/docker.sock
    test -L "$HOME/.agents/skills"
    cmp /opt/dockbox/codex-AGENTS.md "$HOME/.codex/AGENTS.md"
    test "$(jq -r .sandbox.enabled "$HOME/.claude/settings.json")" = false
    test ! -e node_modules/host
    echo ephemeral > node_modules/inside
    echo writable > written
    echo tmp > /tmp/native-temporary
    test "$(cat "$4/file")" = readonly
    if (echo denied > "$4/file") 2>/dev/null
    then
        exit 1
    fi
' sh "$(id -u)" "$(id -g)" "$(id -un)" "$tmp/readonly"
set +e
printf 'piped input\n' | launch exec sh -c 'cat; echo status >&2; exit 37' \
    > "$tmp/stdio.log" 2> "$tmp/status.log"
status=$?
set -e
[[ "$status" == 37 ]] || fail "piped command status: $status"
[[ "$(cat "$tmp/stdio.log")" == 'piped input' ]] || fail 'piped stdout'
grep -qx status "$tmp/status.log"
run_docker inspect "$box" >/dev/null
finish_session
assert_removed
[[ "$(cat node_modules/host)" == host-dependency ]] || fail 'host dependency'
[[ ! -e node_modules/inside ]] || fail 'dependency write escaped'
[[ "$(cat written)" == writable ]] || fail 'project write failed'

echo 'native: worktree backing mount and anonymous volume cleanup'
git -C "$tmp/repo" init -q
git -C "$tmp/repo" -c user.name=Fixture -c user.email=fixture@example.invalid \
    commit --allow-empty -qm fixture
git -C "$tmp/repo" worktree add --detach -q "$tmp/worktree"
mkdir -p "$tmp/worktree/node_modules"
cd "$tmp/worktree"
launch -B exec sh -eu -c '
    git status --porcelain
    test ! -e /tmp/native-temporary
    echo volume > node_modules/test
'
assert_removed
[[ ! -e node_modules/test ]] || fail 'volume write escaped'
cd "$tmp/project"

echo 'native: nested Docker, network, build and privileged containment'
start_session -D -B
if [[ "${DOCKBOX_TEST_AGENTS:-}" == 1 ]]
then
    for tool in claude codex pi
    do
        launch -D exec "$tool" --version
    done
fi
mapfile -t volumes < <(run_docker inspect "$box" --format \
    '{{range .Mounts}}{{if eq .Type "volume"}}{{println .Name}}{{end}}{{end}}' |
    sed '/^$/d')
launch -D exec docker info --format '{{.ID}}' > "$tmp/nested-id"
[[ "$(cat "$tmp/nested-id")" != "$host_id" ]] || fail 'host daemon exposed'
launch -D exec sh -eu -c '
    docker pull busybox:1.37.0
    docker run --rm busybox:1.37.0 nslookup example.com
    docker run --rm busybox:1.37.0 wget -qO /dev/null http://example.com
    docker network create native-net
    docker run -d --name native-service --network native-net \
        busybox:1.37.0 sh -c "mkdir -p /www; echo native-http > /www/index.html
        exec httpd -f -p 8080 -h /www"
    docker run --rm --network native-net busybox:1.37.0 \
        nslookup native-service
    docker run --rm --network native-net busybox:1.37.0 \
        wget -qO- http://native-service:8080
    mkdir /tmp/native-build
    printf "FROM busybox:1.37.0\nRUN echo native-build > /built\nCMD [\"cat\", \"/built\"]\n" \
        > /tmp/native-build/Dockerfile
    docker build -t native-build /tmp/native-build
    test "$(docker run --rm native-build)" = native-build
    docker rm -f native-service
    docker network rm native-net
    echo sandbox-root > /tmp/native-root
    docker_path=$(command -v docker)
    docker run --rm --privileged -v /:/sandbox busybox:1.37.0 sh -eu -c \
        '\''test "$(cat /sandbox/tmp/native-root)" = sandbox-root
        test ! -e "/sandbox$1"
        test ! -e "$1"
        daemon_id=$(chroot /sandbox "$3" info --format "{{.ID}}")
        test -n "$daemon_id"
        test "$daemon_id" != "$2"'\'' \
        sh "$1" "$2" "$docker_path"
' sh "$tmp/sentinel" "$host_id"
run_docker exec "$box" touch /run/dockbox/sess/native-retain
finish_session
HOME="$tmp/home" "$here/dockbox" ls | tee "$tmp/list.log"
awk -v box="$box" '$1 == box { found=1; if ($0 !~ / idle /) exit 1 }
    END { if (!found) exit 1 }' "$tmp/list.log"
run_docker exec "$box" docker run -d --name native-active \
    busybox:1.37.0 sleep 60
HOME="$tmp/home" "$here/dockbox" ls | tee "$tmp/list.log"
awk -v box="$box" '$1 == box { found=1; if ($0 !~ / busy /) exit 1 }
    END { if (!found) exit 1 }' "$tmp/list.log"
run_docker exec "$box" docker rm -f native-active

echo 'native: post-ready daemon death fails the active session'
launch -D exec sh -c 'touch death-ready; exec sleep 60' > "$tmp/death.log" 2>&1 &
death_pid=$!
pids+=("$death_pid")
wait_file "$tmp/project/death-ready"
run_docker exec "$box" sh -c 'kill "$(pidof dockerd)"'
set +e
wait "$death_pid"
status=$?
set -e
[[ "$status" != 0 ]] || fail 'daemon death returned success'
run_docker logs "$box" > "$tmp/daemon.log" 2>&1
grep -q 'dockbox: nested Docker exited' "$tmp/daemon.log"
tail -8 "$tmp/daemon.log"
run_docker rm -f -v "$box" >/dev/null

echo 'native: controlled daemon startup failure is visible'
name="native-$$-failure"
box="dockbox-$name"
mkdir "$tmp/project/fail-bin"
cat > "$tmp/project/fail-bin/dockerd" <<'EOF'
#!/bin/sh
echo invoked >> daemon-calls
echo native-daemon-failure >&2
exit 73
EOF
chmod +x "$tmp/project/fail-bin/dockerd"
set +e
launch -D -e "PATH=$tmp/project/fail-bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" \
    exec true > "$tmp/startup.log" 2>&1
status=$?
set -e
cat "$tmp/startup.log"
[[ "$status" != 0 ]] || fail 'startup failure returned success'
grep -qx invoked "$tmp/project/daemon-calls"
grep -q native-daemon-failure "$tmp/startup.log"
grep -q 'Container exited during startup' "$tmp/startup.log"
run_docker rm -f -v "$box" >/dev/null
echo 'native: all checks passed'
