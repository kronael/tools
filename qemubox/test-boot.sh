port_test() {
    regression_setup
    untrusted=""; locked=""
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
    wait_ready() { :; }; ssh_plain_box() { :; }
    setup_guest_tmp() { :; }; mount_host_paths() { :; }
    setup_guest_builds() { :; }; setup_guest_runtime() { :; }
    setup_guest_auth() { :; }; setup_guest_limits() { :; }
    sync_guest_clock() { :; }
    QEMU=fake_qemu
    fake_qemu() { printf '%s\n' "$@" > "$fixture/port-qemu"; }
    start_box portbox
    chosen=$(cat "$ROOT/portbox/port")
    [ "$chosen" != "$saved" ]
    grep -q "hostfwd=tcp:127.0.0.1:$chosen-:22" "$fixture/port-qemu"
    unlock_box
}
regression "boot walks away from an occupied saved port" port_test

