(
    set -e
    export QEMUBOX_HOME="$fixture/cli-state" STUB="$fixture/cli"
    mkdir -p "$STUB/bin" "$STUB/sess" "$QEMUBOX_HOME/cli" "$QEMUBOX_HOME/base"
    touch "$STUB/sess/$$" "$QEMUBOX_HOME/cli/ready"
    echo base > "$QEMUBOX_HOME/base/fixture.qcow2"
    echo fixture > "$QEMUBOX_HOME/cli/image-id"
    bash -c 'exec -a "$1" sleep 120' -- "file=$QEMUBOX_HOME/cli/disk.qcow2," &
    vm_pid=$!
    trap 'kill "$vm_pid"; wait "$vm_pid" 2>/dev/null || true' EXIT
    echo "$vm_pid" > "$QEMUBOX_HOME/cli/pid"
    for binary in qemu-system-x86_64 qemu-img; do
        printf '#!/bin/sh\nexit 99\n' > "$STUB/bin/$binary"
        chmod +x "$STUB/bin/$binary"
    done
    cat > "$STUB/bin/ssh" <<'STUB'
#!/usr/bin/env bash
set -e
printf '%s\n' "$*" >> "$STUB/ssh.log"
command=${!#}
case "$command" in
    'test -f /run/qemubox/ready') exit 0 ;;
    'sudo mkdir -p /run/qemubox/sess && sudo touch '*)
        touch "$STUB/sess/${command##*/}" ;;
    'sudo rm -f /run/qemubox/sess/'*) rm "$STUB/sess/${command##*/}" ;;
    'sudo ls -1 /run/qemubox/sess') ls -1 "$STUB/sess" ;;
    *'exec env'*)
        echo "$command" > "$STUB/command"
        if [ -n "${STUB_HOLD:-}" ]; then
            trap 'exit 143' TERM
            sleep 10 &
            child=$!
            trap 'kill "$child"; wait "$child" || true; exit 143' TERM
            wait "$child"
        fi
        exit "${STUB_RC:-0}" ;;
    *) echo "unexpected SSH command: $command" >&2; exit 2 ;;
esac
STUB
    chmod +x "$STUB/bin/ssh"
    export PATH="$STUB/bin:$PATH"
    printf '%s\n' '-n global' '-d codex' > "$HOME/.qemuboxrc"
    bash "$here/qemubox" -n cli "$PROJ" </dev/null > "$STUB/output" 2>&1
    grep -q 'codex -m gpt-5.6-sol -c model_reasoning_effort=xhigh' "$STUB/command"
    ! grep -q -- ' -t ' "$STUB/ssh.log"
    [ "$(ls "$STUB/sess")" = $$ ]
    export STUB_RC=17
    if bash "$here/qemubox" -n cli exec true </dev/null > "$STUB/output" 2>&1; then
        exit 1
    else
        [ "$?" = 17 ]
    fi
    [ "$(ls "$STUB/sess")" = $$ ]
    unset STUB_RC
    for signal in HUP TERM; do
        rm -f "$STUB/command"
        STUB_HOLD=1 bash "$here/qemubox" -n cli exec true </dev/null > "$STUB/output" 2>&1 &
        parent=$!
        for ((i=0;i<100;i++)); do
            [ ! -f "$STUB/command" ] || break
            sleep 0.01
        done
        [ -f "$STUB/command" ]
        [ -f "$STUB/sess/$parent" ]
        kill -"$signal" "$parent"
        if wait "$parent"; then exit 1; else
            code=$?
            [ "$signal:$code" = HUP:129 ] || [ "$signal:$code" = TERM:143 ]
        fi
        [ "$(ls "$STUB/sess")" = $$ ]
    done
    rm "$HOME/.qemuboxrc"
) > "$fixture/cli.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/cli.log"; bad "CLI rc precedence, exit, HUP, TERM and non-TTY"; }
