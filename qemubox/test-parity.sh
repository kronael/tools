tool_cmd codex
eq "codex default model and effort" "${cmd[*]}" \
    'codex -m gpt-6.1-sol -c model_reasoning_effort=high'
args=(--model gpt-6-astra); tool_cmd codex
eq "a session --model replaces the codex alias model and effort" "${cmd[*]}" codex
args=(-m x); tool_cmd gpt
eq "a session -m replaces the alias model" "${cmd[*]}" codex
args=(--model=x); tool_cmd opus
eq "a session --model= replaces the claude alias model and effort" "${cmd[*]}" claude
args=(--verbose); tool_cmd sonnet
eq "other session flags keep the alias model" "${cmd[*]}" \
    'claude --model claude-sonnet-5-5 --effort high'
args=(-p "explain the -m flag"); tool_cmd opus
eq "a model flag inside a prompt keeps the alias model" "${cmd[*]}" \
    'claude --model claude-opus-5-5 --effort high'
args=(); tool_cmd fable
eq "fable pins high effort" "${cmd[*]}" \
    'claude --model claude-fable-5-1 --effort high'
tool_cmd gpt
eq "astra pins high effort" "${cmd[*]}" \
    'codex -m gpt-6-astra -c model_reasoning_effort=high'
args=()
primary="$fixture/project.with.dots"
slug="${primary//[\/.]/-}"
mkdir -p "$HOME/.claude/projects/$slug"
touch "$HOME/.claude/projects/$slug/session.jsonl"
for tool in claude haiku sonnet opus fable; do
    tool_cmd "$tool"
    resume_session
    eq "$tool selects existing session" "${cmd[1]}" --resume
done
tool_cmd codex; resume_session
eq "codex does not use Claude resume" "${cmd[1]}" -m
primary="$fixture/no-sessions"
tool_cmd claude; resume_session
eq "claude starts fresh without sessions" "${cmd[1]}" --model
primary="$fixture/project.with.dots"
new_session=1; tool_cmd claude; resume_session
eq "-N starts a new session over existing history" "${cmd[1]}" --model
new_session=""

printf '# defaults\n\n-n global\n-P' > "$fixture/rc"
read_rc "$fixture/rc"
eq "rc tokenizes without execution, including final line" "${rc_tokens[*]}" '-n global -P'
read_rc "$fixture/missing-rc"
eq "missing rc is empty" "${#rc_tokens[@]}" 0
(
    set -e
    name_override=original; entrypoint=claude
    ssh_agent=""; docker_sock=""; gpg_forward=""; warnings=()
    persist_builds=""; eph_no_tmpfs=""; tmp_session=""; new_session=""
    printf '%s\n' '-A -D -K -S -T -n attacker -d bash -x codex -P -B -N' > "$PROJ/.qemuboxrc"
    project_rc "$PROJ"
    [ "$name_override" = original ]
    [ "$entrypoint" = claude ]
    [ -z "$ssh_agent$docker_sock$gpg_forward" ]
    [ "$persist_builds$eph_no_tmpfs$new_session" = 111 ]
    [ -z "$tmp_session" ]
    [ "${#warnings[@]}" = 0 ]
) > "$fixture/project-rc.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/project-rc.log"; bad "project rc safe subset"; }
rm -f "$PROJ/.qemuboxrc"

project_persist_test() {
    local paths
    dirs=("$PROJ"); persist_builds=""; eph_no_tmpfs=""
    mkdir -p "$PROJ/node_modules"
    stage_ephemeral "$fixture/rc-builds"
    mapfile -d '' -t paths < "$fixture/rc-builds"
    [[ "${#paths[@]}" -gt 1 ]]
    printf '%s\n' --no-ephemeral > "$PROJ/.qemuboxrc"
    project_rc "$PROJ"
    stage_ephemeral "$fixture/rc-builds"
    mapfile -d '' -t paths < "$fixture/rc-builds"
    [[ "${#paths[@]}" -eq 1 ]]
}
regression "project --no-ephemeral keeps build directories on the host" \
    project_persist_test
rm -f "$PROJ/.qemuboxrc"

(
    set -e
    git init -q "$fixture/git-main"
    git -C "$fixture/git-main" -c user.name=Test -c user.email=test@example.test \
        -c commit.gpgsign=false commit -q --allow-empty -m fixture
    git -C "$fixture/git-main" worktree add -q --detach "$fixture/git-worktree"
    reset_mounts
    dirs=("$fixture/git-worktree" "$fixture/git-worktree")
    name=worktree; untrusted=1; extra_dirs=(); extra_modes=()
    assemble_mounts
    [ "$(mount_mode "$fixture/git-main/.git")" = rw ]
    [ "$(printf '%s\n' "${mount_dests[@]}" | grep -Fxc "$fixture/git-main/.git")" = 1 ]
    reset_mounts
    dirs=("$fixture/git-main")
    assemble_mounts
    [ "${#mount_dests[@]}" = 1 ]
) > "$fixture/worktree.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/worktree.log"; bad "worktree common dir and dedup"; }

for permissions in 600 400 200 000; do
    touch "$fixture/kvm"
    chmod "$permissions" "$fixture/kvm"
    qemu_acceleration "$fixture/kvm"
    if [ "$permissions" = 600 ]; then
        eq "KVM read-write enables acceleration" "${accel[*]} $cpu" '-enable-kvm host'
    else
        eq "KVM $permissions selects emulation" "${accel[*]} $cpu" ' max'
    fi
done
chmod 600 "$fixture/kvm"
qemu_acceleration "$fixture/missing-kvm"
eq "missing KVM selects emulation" "$cpu" max

session_tty </dev/null
eq "nonterminal stdin does not allocate tty" "${#tty[@]}" 0
session_tty > "$fixture/tty"
eq "nonterminal stdout does not allocate tty" "${#tty[@]}" 0

literal_env_test() {
    local value=$'first=second\n literal $(false); `false` \' " \\ end\n'
    envs=()
    add_env "PARITY=$value"
    add_env EMPTY=
    export EXPORTED='exported = value'
    add_env EXPORTED
    name=vm; env_file="$fixture/literal-env"
    ssh_plain_box() { bash -c "$2"; }
    send_envs
    unset PARITY EMPTY EXPORTED
    source "$env_file"
    [[ "$PARITY" = "$value" && "$EMPTY" = '' && "$EXPORTED" = 'exported = value' ]]
    if (add_env '1INVALID=secret') 2> "$fixture/invalid-env"
    then
        return 1
    fi
    ! grep -q secret "$fixture/invalid-env"
}
regression 'literal and exported environment values survive upload without evaluation' \
    literal_env_test

capture_test() {
    regression_setup
    mkdir -p "$ROOT/vm" "$fixture/capture-source"
    local source="$fixture/capture-source/capture.png" stage
    printf first > "$source"
    reset_mounts
    stage_capture vm "$source"
    stage=$(cat "$ROOT/vm/capture-stage")
    [[ "${stage%/*}" = "${source%/*}" && "$(stat -c %a "$stage")" = 700 ]]
    [[ "$stage/capture.png" -ef "$source" ]]
    [[ "$(mount_mode /mnt/qemubox-capture)" = ro ]]
    [[ "${mount_tags[*]}" = capture ]]
    printf changed > "$source"
    [[ "$(cat "$stage/capture.png")" = changed ]]
    [[ "$(find "$stage" -mindepth 1 -maxdepth 1 | wc -l)" = 1 ]]
    cleanup_capture vm
    [[ -f "$source" && ! -e "$stage" && ! -e "$ROOT/vm/capture-stage" ]]
    reset_mounts
    stage_capture vm "$fixture/absent-capture"
    [[ "${#mount_tags[@]}" = 0 ]]
    if QEMUBOX_HOME="$ROOT" bash -c '
        QEMUBOX_LIB=1 source "$1"
        name=vm
        start_source=$2
        stage_record=$3
        start_box() {
            stage_capture vm "$start_source"
            cat "$ROOT/vm/capture-stage" > "$stage_record"
            false
        }
        enter_session
    ' fixture "$here/qemubox" "$source" "$fixture/failed-stage"
    then
        return 1
    fi
    [[ -f "$source" && ! -e "$(cat "$fixture/failed-stage")" ]]
    [[ ! -e "$ROOT/vm/capture-stage" ]]
}
regression 'capture shares one live inode through a private readonly directory' capture_test

native_busy_test() {
    regression_setup
    run_state() { echo running; }
    mkdir -p "$ROOT/vm"
    echo 0 > "$ROOT/vm/idle"
    local probe=abcdef012345
    timeout() {
        printf '%s\n' "$@" > "$fixture/native-probe-args"
        cat > "$fixture/native-probe-stdin"
        [[ "$probe" != failed ]] || return 42
        [[ -z "$probe" ]] || printf '%s\n' "$probe"
    }
    ss() { :; }
    : > "$systemd_log"
    (check_box vm; cat) < <(printf preserved) > "$fixture/native-stdin"
    [[ "$(cat "$fixture/native-stdin")" = preserved ]]
    [[ ! -s "$fixture/native-probe-stdin" && ! -s "$systemd_log" ]]
    grep -Fq 'docker --host=unix:///var/run/docker.sock ps --quiet' \
        "$fixture/native-probe-args"
    [[ "$(session_count vm)" = 1 ]]
    run_state() { echo running; }
    ssh_plain_box() { printf '%s\n' 100 40 30 10; }
    [[ "$(list_boxes)" = *$'running\tbusy\t'* ]]
    touch -d '5 hours ago' "$ROOT/vm/idle"
    prune_boxes
    [[ ! -s "$systemd_log" || "$(cat "$systemd_log")" != *' stop '* ]]
    : > "$systemd_log"
    probe=failed
    if check_box vm 2> "$fixture/native-probe-error"
    then
        return 1
    fi
    [[ ! -s "$systemd_log" ]]
    grep -q 'preserving VM' "$fixture/native-probe-error"
    [[ "$(list_boxes 2>/dev/null)" = *$'running\t?\t'* ]]
    : > "$systemd_log"
    if prune_boxes 2>/dev/null
    then
        return 1
    fi
    [[ ! -s "$systemd_log" ]]
    probe='invalid response'
    if session_count vm 2>/dev/null
    then
        return 1
    fi
    probe=''
    check_box vm
    grep -Fxq 'systemctl --user stop --no-block qemubox@vm.service' "$systemd_log"
}
regression 'native containers prevent idle stop; idle daemon permits it; failed probes preserve VM' \
    native_busy_test

forward_config_test() {
    mkdir -p "$fixture/ssh-forward"
    printf 'Host *\n ForwardAgent yes\n' > "$fixture/ssh-forward/config"
    printf '#!/bin/sh\nexec /usr/bin/ssh -G -F "$FORWARD_CONFIG" "$@"\n' \
        > "$fixture/ssh-forward/ssh"
    chmod +x "$fixture/ssh-forward/ssh"
    local mode
    export FORWARD_CONFIG="$fixture/ssh-forward/config"
    for mode in disabled enabled
    do
        ssh_agent=''
        [[ "$mode" != enabled ]] || ssh_agent=1
        (PATH="$fixture/ssh-forward:$PATH" ssh_box vm true) \
            > "$fixture/ssh-forward/$mode"
    done
    grep -Fxq 'forwardagent no' "$fixture/ssh-forward/disabled"
    grep -Fxq 'forwardagent yes' "$fixture/ssh-forward/enabled"
    grep -Fxq 'serveraliveinterval 0' "$fixture/ssh-forward/disabled"
    (PATH="$fixture/ssh-forward:$PATH" ssh_plain_box vm true) \
        > "$fixture/ssh-forward/control"
    grep -Fxq 'serveraliveinterval 5' "$fixture/ssh-forward/control"
    grep -Fxq 'serveralivecountmax 2' "$fixture/ssh-forward/control"
}
regression 'configured SSH forwarding stays disabled until explicit -A' forward_config_test

codex_bridge_test() {
    local dir="$fixture/codex-bridge"
    mkdir -p "$dir/home/.claude/skills" "$dir/opt"
    printf 'fixture wisdom\n' > "$dir/home/.claude/CLAUDE.md"
    printf 'fixture bridge\n' > "$dir/opt/codex-AGENTS.md"
    sed "s|/opt/qemubox|$dir/opt|g" "$here/qemubox-codex-bridge" > "$dir/bridge"
    HOME="$dir/home" sh "$dir/bridge"
    [[ "$(readlink "$dir/home/.agents/skills")" = ../.claude/skills ]]
    cmp "$dir/opt/codex-AGENTS.md" "$dir/home/.codex/AGENTS.md"
    printf 'custom guidance\n' > "$dir/home/.codex/AGENTS.md"
    HOME="$dir/home" sh "$dir/bridge"
    grep -Fxq 'custom guidance' "$dir/home/.codex/AGENTS.md"
    rm "$dir/home/.codex/AGENTS.md"
    ln -s ../custom.md "$dir/home/.codex/AGENTS.md"
    HOME="$dir/home" sh "$dir/bridge"
    [[ "$(readlink "$dir/home/.codex/AGENTS.md")" = ../custom.md ]]
    rm "$dir/home/.codex/AGENTS.md"
    ln -s ../.claude/CLAUDE.md "$dir/home/.codex/AGENTS.md"
    HOME="$dir/home" sh "$dir/bridge"
    [[ ! -L "$dir/home/.codex/AGENTS.md" ]]
    cmp "$dir/opt/codex-AGENTS.md" "$dir/home/.codex/AGENTS.md"
}
regression 'fresh Codex homes bridge skills while custom files and symlinks survive' \
    codex_bridge_test
