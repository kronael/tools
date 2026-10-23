port_test() {
    regression_setup
    untrusted=""
    ensure_box portbox
    python3 - "$fixture/listener-port" <<'PY' &
import socket
import sys
import time
with socket.socket() as listener:
    listener.bind(('127.0.0.1', 0))
    listener.listen(100)
    with open(sys.argv[1], 'w') as out:
        out.write(str(listener.getsockname()[1]))
    time.sleep(30)
PY
    listener=$!
    trap 'kill "$listener"; wait "$listener" 2>/dev/null || true' EXIT
    for ((i=0;i<100;i++)); do
        [ ! -s "$fixture/listener-port" ] || break
        sleep 0.01
    done
    cat "$fixture/listener-port" > "$ROOT/portbox/port"
    saved=$(cat "$ROOT/portbox/port")
    missing_deps() { :; }; assemble_mounts() { :; }
    start_box portbox
    unlock_box
    chosen=$(cat "$ROOT/portbox/port")
    [ "$chosen" != "$saved" ]
    (QEMU="$fake_qemu" QEMU_ARGS="$fixture/port-qemu" run_qemu portbox)
    grep -q "hostfwd=tcp:127.0.0.1:$chosen-:22" "$fixture/port-qemu"
}
regression "boot walks away from an occupied saved port" port_test

cache_test() {
    mkdir -p "$fixture/cache/a/node_modules" "$fixture/cache/b/node_modules"
    ln -s "$fixture/cache/a" "$fixture/cache/alias"
    awk '/^    IFS= read -r -d .* backing/ {print "{"; emit=1}
        emit {print} emit && /^} </ {exit}' "$here/guest-init" |
        sed 's|/run/qemubox/config/ephemeral|"$QEMUBOX_TEST_PATHS"|' \
        > "$fixture/cache-script"
    mount() { printf '%s\n' "$*" >> "$fixture/cache-mounts"; }
    mkdir() { :; }; chown() { :; }
    export -f mount mkdir chown
    export fixture
    printf '%s\0' disk "$fixture/cache/a/node_modules" "$fixture/cache/b/node_modules" > "$fixture/cache-paths"
    QEMUBOX_TEST_PATHS="$fixture/cache-paths" user_uid=1000 user_gid=1000 \
        bash "$fixture/cache-script"
    first=$(head -1 "$fixture/cache-mounts" | cut -d' ' -f2)
    second=$(tail -1 "$fixture/cache-mounts" | cut -d' ' -f2)
    printf '%s\0' disk "$fixture/cache/b/node_modules" "$fixture/cache/alias/node_modules" > "$fixture/cache-paths"
    QEMUBOX_TEST_PATHS="$fixture/cache-paths" user_uid=1000 user_gid=1000 \
        bash "$fixture/cache-script"
    [ "$(tail -1 "$fixture/cache-mounts" | cut -d' ' -f2)" = "$first" ]
    [ "$(tail -2 "$fixture/cache-mounts" | head -1 | cut -d' ' -f2)" = "$second" ]
    [ "$first" != "$second" ]
}
regression "disk caches follow canonical paths across discovery order changes" cache_test

explicit_mount_test() {
    regression_setup
    gcloud_creds=""; untrusted=1
    extra_dirs=("$fixture/missing-volume"); extra_modes=(ro)
    if assemble_mounts 2> "$fixture/volume-error"; then exit 1; fi
    grep -q missing-volume "$fixture/volume-error"
}
regression "missing explicit volume fails even in a conditional caller" explicit_mount_test

socket_wait_test() {
    regression_setup
    untrusted=1
    ensure_box sockets
    echo off > "$ROOT/sockets/net"
    printf 'qbx0\t%s\t/first\trw\ncfg\t%s\t/run/qemubox/config\tro\n' \
        "$PROJ" "$ROOT/sockets/config" > "$ROOT/sockets/config/mounts"
    if (QEMUBOX_READY_TIMEOUT=0 QEMU="$fake_qemu" \
        QEMU_ARGS="$fixture/socket-qemu" run_qemu sockets) \
        2> "$fixture/socket-error"
    then
        return 1
    fi
    grep -q 'Timed out waiting for virtiofs socket .*qbx0.sock' \
        "$fixture/socket-error"
    [ ! -e "$fixture/socket-qemu" ]
    python3 - "$ROOT/sockets" <<'PY'
import pathlib
import socket
import sys

with socket.socket(socket.AF_UNIX) as sock:
    sock.bind(str(pathlib.Path(sys.argv[1]) / "qbx0.sock"))
PY
    if (QEMUBOX_READY_TIMEOUT=0 QEMU="$fake_qemu" \
        QEMU_ARGS="$fixture/socket-qemu" run_qemu sockets) \
        2> "$fixture/socket-error"
    then
        return 1
    fi
    grep -q 'Timed out waiting for virtiofs socket .*cfg.sock' \
        "$fixture/socket-error"
    [ ! -e "$fixture/socket-qemu" ]
    python3 - "$ROOT/sockets" <<'PY' &
import pathlib
import socket
import sys
import time

time.sleep(0.2)
with socket.socket(socket.AF_UNIX) as sock:
    sock.bind(str(pathlib.Path(sys.argv[1]) / "cfg.sock"))
PY
    local binder=$!
    (MEM=768 QEMUBOX_READY_TIMEOUT=3 QEMU="$fake_qemu" \
        QEMU_ARGS="$fixture/socket-qemu" run_qemu sockets)
    wait "$binder"
    grep -Fxq 'memory-backend-memfd,id=mem,size=768M,share=on' \
        "$fixture/socket-qemu"
    [ "$(grep -A1 -Fx -- -m "$fixture/socket-qemu" | tail -1)" = 768 ]
    [ "$(grep -Fxc -- -chardev "$fixture/socket-qemu")" = 2 ]
}
regression "QEMU waits for every socket within one deadline and uses configured shared RAM" \
    socket_wait_test

control_stdin_test() {
    regression_setup
    untrusted=1
    ensure_box vm
    printf 'payload\000with\nbytes\377' > "$fixture/session-input"
    ssh() {
        case "${!#}" in
            'test -f /run/qemubox/ready')
                cat > "$fixture/control-input" ;;
            'umask 077 && cat > '* ) cat > "$fixture/env-input" ;;
            payload)
                cat
                echo session-error >&2
                return 37 ;;
            *) return 96 ;;
        esac
    }
    local mode rc
    for mode in cold warm
    do
        session_io() {
            [[ "$mode" != cold ]] || setup_box vm
            name=vm
            env_file=/dev/shm/fixture-env
            envs=('PROBE=literal $value')
            send_envs
            ssh_plain_box vm payload
        }
        if session_io < "$fixture/session-input" \
            > "$fixture/session-output" 2> "$fixture/session-error"
        then
            return 1
        else
            rc=$?
        fi
        [[ "$rc" = 37 ]]
        cmp "$fixture/session-input" "$fixture/session-output"
        grep -Fxq session-error "$fixture/session-error"
        grep -Fxq 'export PROBE=literal\ \$value' "$fixture/env-input"
        [[ ! -s "$fixture/control-input" ]]
    done
}
regression 'cold control SSH preserves session stdin and explicit environment upload' \
    control_stdin_test
