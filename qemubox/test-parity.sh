tool_cmd codex
eq "codex default model and effort" "${cmd[*]}" \
    'codex -m gpt-6.1-sol -c model_reasoning_effort=xhigh'
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
    'claude --model claude-opus-5-5 --effort xhigh'
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
