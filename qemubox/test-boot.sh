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
    MEM=768 ensure_box sockets
    (QEMUBOX_READY_TIMEOUT=3 QEMU="$fake_qemu" \
        QEMU_ARGS="$fixture/socket-qemu" run_qemu sockets)
    wait "$binder"
    grep -Fxq 'memory-backend-memfd,id=mem,size=768M,share=on' \
        "$fixture/socket-qemu"
    [ "$(grep -A1 -Fx -- -m "$fixture/socket-qemu" | tail -1)" = 768M ]
    [ "$(grep -Fxc -- -chardev "$fixture/socket-qemu")" = 2 ]
    ! grep -qE 'maxmem|id=vmem|virtio-mem-pci' "$fixture/socket-qemu"
    local value expected boot extra
    for value in 2048 2049 2175 2177 24576
    do
        case "$value" in
            2048) expected=2048M; boot=2048; extra=0 ;;
            2049) expected=2049M; boot=2049; extra=0 ;;
            2175) expected=2175M; boot=2175; extra=0 ;;
            2177) expected=2049M,maxmem=2177M; boot=2049; extra=128 ;;
            24576) expected=2048M,maxmem=24576M; boot=2048; extra=22528 ;;
        esac
        MEM="$value" ensure_box sockets
        (MEM=1 QEMU="$fake_qemu" \
            QEMU_ARGS="$fixture/socket-qemu" run_qemu sockets)
        [[ "$(grep -A1 -Fx -- -m "$fixture/socket-qemu" | tail -1)" = \
            "$expected" ]]
        grep -Fxq "memory-backend-memfd,id=mem,size=${boot}M,share=on" \
            "$fixture/socket-qemu"
        if ((extra == 0))
        then
            ! grep -qE 'maxmem|id=vmem|virtio-mem-pci' "$fixture/socket-qemu"
            continue
        fi
        grep -Fxq \
            "memory-backend-memfd,id=vmem,size=${extra}M,share=on,prealloc=off" \
            "$fixture/socket-qemu"
        grep -Fxq \
            'virtio-mem-pci,id=vm0,memdev=vmem,requested-size=0,dynamic-memslots=on,prealloc=off' \
            "$fixture/socket-qemu"
        awk '/^vhost-user-fs-pci,/ {fs=NR}
            /^virtio-mem-pci,/ {mem=NR} END {exit !(mem > fs && fs > 0)}' \
            "$fixture/socket-qemu"
    done
    rm "$ROOT/base/fixture/rootfs/opt/qemubox/memory-hotplug"
    MEM=24576 ensure_box sockets
    [[ "$(cat "$ROOT/sockets/config/memory")" = $'24576\n0' ]]
    (QEMU="$fake_qemu" QEMU_ARGS="$fixture/socket-qemu" run_qemu sockets)
    grep -Fxq 'memory-backend-memfd,id=mem,size=24576M,share=on' \
        "$fixture/socket-qemu"
    [[ "$(grep -A1 -Fx -- -m "$fixture/socket-qemu" | tail -1)" = 24576M ]]
    ! grep -qE 'maxmem|id=vmem|virtio-mem-pci' "$fixture/socket-qemu"
    touch "$ROOT/base/fixture/rootfs/opt/qemubox/memory-hotplug"
}
regression "QEMU waits for every socket within one deadline and uses configured shared RAM" \
    socket_wait_test

qmp_growth_test() (
    regression_setup
    untrusted=1
    ensure_box vm
    python3 - "$ROOT/vm/qmp" "$fixture/qmp-listening" <<'PY' &
import json
import pathlib
import socket
import sys

with socket.socket(socket.AF_UNIX) as listener:
    listener.settimeout(5)
    listener.bind(sys.argv[1])
    listener.listen()
    pathlib.Path(sys.argv[2]).touch()
    for size in [None, 134217728, 23622320128]:
        sock, _ = listener.accept()
        with sock, sock.makefile("rw") as qmp:
            qmp.write('{"QMP": {}}\n')
            qmp.flush()
            assert json.loads(qmp.readline()) == {"execute": "qmp_capabilities"}
            qmp.write('{"return": {}}\n')
            qmp.flush()
            request = json.loads(qmp.readline())
            if size is None:
                assert request == {"execute": "query-status"}
                reply = {"return": {"status": "running"}}
            else:
                assert request == {
                    "execute": "qom-set",
                    "arguments": {
                        "path": "/machine/peripheral/vm0",
                        "property": "requested-size",
                        "value": size,
                    },
                }
                reply = {"return": {}}
                if size == 23622320128:
                    reply = {"error": {"desc": "growth rejected"}}
            qmp.write('{"event": "MEMORY_DEVICE_SIZE_CHANGE"}\n')
            qmp.write(json.dumps(reply) + "\n")
            qmp.flush()
PY
    local server=$! i
    trap 'kill "$server" 2>/dev/null || true
        wait "$server" 2>/dev/null || true' EXIT
    for ((i=0; i<100; i++))
    do
        [[ ! -f "$fixture/qmp-listening" ]] || break
        sleep 0.01
    done
    [[ "$(qmp_box vm query-status)" = running ]]
    wait_ready() { echo ready > "$fixture/qmp-ready"; }
    systemd-run() {
        [[ -f "$fixture/qmp-ready" ]]
        echo timer >> "$fixture/qmp-timers"
    }
    MEM=2175 ensure_box vm
    MEM=1 setup_box vm
    [[ "$(wc -l < "$fixture/qmp-timers")" = 1 ]]
    MEM=2177 ensure_box vm
    MEM=1 setup_box vm
    [[ "$(wc -l < "$fixture/qmp-timers")" = 2 ]]
    MEM=24576 ensure_box vm
    if MEM=1 setup_box vm 2> "$fixture/qmp-error"
    then
        return 1
    fi
    grep -Fxq 'QMP qom-set: growth rejected' "$fixture/qmp-error"
    [[ "$(wc -l < "$fixture/qmp-timers")" = 2 ]]
    wait "$server"
    trap - EXIT
    wait_ready() { return 42; }
    if MEM=24576 setup_box vm
    then
        return 1
    else
        [[ "$?" = 42 ]]
    fi
)
regression 'QMP growth follows SSH, preserves payloads and fails startup on rejection' \
    qmp_growth_test

control_stdin_test() {
    regression_setup
    untrusted=1
    ensure_box vm
    qmp_box() { :; }
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
