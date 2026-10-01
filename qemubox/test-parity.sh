tool_cmd codex
eq "codex default model and effort" "${cmd[*]}" \
    'codex -m gpt-5.6-sol -c model_reasoning_effort=xhigh'
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

printf '# defaults\n\n-n global\n-P' > "$fixture/rc"
read_rc "$fixture/rc"
eq "rc tokenizes without execution, including final line" "${rc_tokens[*]}" '-n global -P'
read_rc "$fixture/missing-rc"
eq "missing rc is empty" "${#rc_tokens[@]}" 0
(
    set -e
    name_override=original; entrypoint=claude
    ssh_agent=""; docker_sock=""; gpg_forward=""; warnings=()
    persist_builds=""; eph_no_tmpfs=""; no_copy=""
    printf '%s\n' '-A -D -K -S -n attacker -d bash -x codex -P -T -N' > "$PROJ/.qemuboxrc"
    project_rc "$PROJ"
    [ "$name_override" = original ] && [ "$entrypoint" = claude ]
    [ -z "$ssh_agent$docker_sock$gpg_forward" ]
    [ "$persist_builds$eph_no_tmpfs$no_copy" = 111 ]
    [ "${#warnings[@]}" = 0 ]
) > "$fixture/project-rc.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/project-rc.log"; bad "project rc safe subset"; }
rm -f "$PROJ/.qemuboxrc"

(
    set -e
    git init -q "$fixture/git-main"
    git -C "$fixture/git-main" -c user.name=Test -c user.email=test@example.test \
        -c commit.gpgsign=false commit -q --allow-empty -m fixture
    git -C "$fixture/git-main" worktree add -q --detach "$fixture/git-worktree"
    reset_mounts
    dirs=("$fixture/git-worktree" "$fixture/git-worktree")
    name=worktree; no_copy=""; untrusted=1; extra_dirs=(); extra_modes=()
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

(
    set -e
    ssh_plain_box() { cat > "$fixture/mount-parent.sh"; }
    setup_mount_path vm "$fixture/parents/a/b"
    mkdir -p "$fixture/parents"
    bash "$fixture/mount-parent.sh" "$(id -u)" "$(id -g)" "$fixture/parents/a/b"
    [ "$(stat -c %u "$fixture/parents/a")" = "$(id -u)" ]
    [ "$(stat -c %u "$fixture/parents/a/b")" = "$(id -u)" ]
    ssh_plain_box() { cat > "$fixture/limits.sh"; }
    setup_guest_limits vm
    sed "s|/etc/security/limits.d|$fixture/limits|g" "$fixture/limits.sh" > "$fixture/local-limits.sh"
    bash "$fixture/local-limits.sh" guest
    printf '%s\n' 'guest - nice -20' 'guest - rtprio 99' 'guest - memlock unlimited' > "$fixture/expected-limits"
    cmp "$fixture/limits/90-qemubox.conf" "$fixture/expected-limits"
    date() { echo 12345.125; }
    ssh_plain_box() { echo "$2" > "$fixture/clock-command"; }
    sync_guest_clock vm
    [ "$(cat "$fixture/clock-command")" = 'sudo date -u -s @12345.125 >/dev/null' ]
) > "$fixture/guest-parity.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/guest-parity.log"; bad "mount parents, limits and clock setup"; }
exits 23 'set -e; ssh_plain_box() { return 23; }; sync_guest_clock vm' \
    "clock sync errors fail launch"
exits 23 'set -e; ssh_plain_box() { return 23; }; setup_guest_limits vm' \
    "limits setup errors fail launch"

(
    set -e
    untrusted=""
    ssh_plain_box() { echo "$2" > "$fixture/sessions-command"; }
    setup_guest_sessions vm
    [ "$(cat "$fixture/sessions-command")" = "mkdir -p ~/.claude/sessions && sudo mount -t tmpfs -o rw,mode=0700,uid=$(id -u),gid=$(id -g) tmpfs ~/.claude/sessions" ]
    rm "$fixture/sessions-command"
    untrusted=1
    setup_guest_sessions vm
    [ ! -e "$fixture/sessions-command" ]
) > "$fixture/sessions.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/sessions.log"; bad "private session registry in the guest"; }
untrusted=""
exits 23 'set -e; ssh_plain_box() { return 23; }; setup_guest_sessions vm' \
    "session registry mount errors fail launch"
