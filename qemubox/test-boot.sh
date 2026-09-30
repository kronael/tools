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

cache_test() {
    mkdir -p "$fixture/cache/a/node_modules" "$fixture/cache/b/node_modules"
    ln -s "$fixture/cache/a" "$fixture/cache/alias"
    ssh_stream_box() { cat > "$fixture/cache-script"; }
    setup_guest_builds vm
    mount() { printf '%s\n' "$*" >> "$fixture/cache-mounts"; }
    mkdir() { :; }; chown() { :; }
    export -f mount mkdir chown
    export fixture
    printf '%s\0' disk "$fixture/cache/a/node_modules" "$fixture/cache/b/node_modules" > "$fixture/cache-paths"
    bash "$fixture/cache-script" 1000 1000 "$fixture/cache-paths"
    first=$(head -1 "$fixture/cache-mounts" | cut -d' ' -f2)
    second=$(tail -1 "$fixture/cache-mounts" | cut -d' ' -f2)
    printf '%s\0' disk "$fixture/cache/b/node_modules" "$fixture/cache/alias/node_modules" > "$fixture/cache-paths"
    bash "$fixture/cache-script" 1000 1000 "$fixture/cache-paths"
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
