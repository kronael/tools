#!/usr/bin/env bash
set -uo pipefail
unset DOCKBOX_DOCKER

here="$(cd "$(dirname "$0")" && pwd)"

# shellcheck disable=SC1090
DOCKBOX_LIB=1 . "$here/dockbox"
set +e  # sourcing turned on set -e; take back control for assertions

pass=0; fail=0
ok()   { pass=$((pass+1)); }
bad()  { fail=$((fail+1)); echo "FAIL: $1" >&2; }
true_() { if eval "$2"; then ok; else bad "$1"; fi; }
false_(){ if eval "$2"; then bad "$1"; else ok; fi; }
exits() { ( eval "$2" ) >/dev/null 2>&1; [ "$?" = "$1" ] && ok || bad "$3"; }

tmp=$(mktemp -d)
trap 'echo "fast tests: retained fixture data: $tmp"' EXIT

false_ "rm empty pattern matches nothing"  'rm_matches dockbox-repo ""'
true_  "rm '\''*'\'' matches all"               'rm_matches dockbox-repo "*"'
true_  "rm exact bare"                     'rm_matches dockbox-repo repo'
true_  "rm exact full name"                'rm_matches dockbox-repo dockbox-repo'
false_ "rm exact no substring"             'rm_matches dockbox-repo-facade repo'
true_  "rm glob star"                      'rm_matches dockbox-repo-1 "repo-*"'
false_ "rm glob non-match"                 'rm_matches dockbox-other "repo-*"'
false_ "rm prefixed name is taken literally" 'rm_matches dockbox-dockbox-repo dockbox-repo'

df_out='Type    Used Mounted on
tmpfs     84 /tmp
ext4  900000 /tmp/cargo-target
tmpfs 109604 /home/dockbox
tmpfs 109604 /home/dockbox'
true_ "tmpfs sums each mount once, skips non-tmpfs" \
    '[ "$(tmpfs_used <<< "$df_out")" = 107M ]'
true_ "tmpfs prints G from 1G up" \
    '[ "$(printf "h\ntmpfs 3145728 /tmp\n" | tmpfs_used)" = 3.0G ]'
true_ "tmpfs empty is 0M" '[ "$(printf "h\n" | tmpfs_used)" = 0M ]'
true_ "tmpfs counts a mount sampled twice at new usage once" \
    '[ "$(printf "h\ntmpfs 4096 /home/dockbox\ntmpfs 5120 /home/dockbox\n" | tmpfs_used)" = 4M ]'
true_ "tmpfs keys the whole target, spaces included" \
    '[ "$(printf "h\ntmpfs 1024 /w/a b\ntmpfs 2048 /w/a c\n" | tmpfs_used)" = 3M ]'

cat > "$tmp/top-idle" <<'EOF'
1 0 Ss /sbin/docker-init -- /usr/local/bin/dockbox-init sleep infinity
2 1 S sleep infinity
3 0 R ps -eo pid=,ppid=,stat=,args=
EOF
{ cat "$tmp/top-idle"
  echo "4 0 S claude --model claude-opus-5-5"
} > "$tmp/top-busy"
true_  "use idle when only the keepers run"   '[ "$(box_use < "$tmp/top-idle")" = idle ]'
true_  "use busy with any other process"      '[ "$(box_use < "$tmp/top-busy")" = busy ]'
false_ "use fails when ps lists no process"  ': | box_use'
cat > "$tmp/top-docker-idle" <<'EOF'
1 0 Ss /sbin/docker-init -- /usr/local/bin/dockbox-init sleep infinity
2 1 S /bin/bash /usr/local/bin/dockbox-init sleep infinity
3 2 S dockerd --host=unix:///var/run/docker.sock --group=users
4 3 S containerd --config /var/run/docker/containerd/containerd.toml
5 2 S sleep infinity
6 0 R ps -eo pid=,ppid=,stat=,args=
7 4 Z [containerd-shim] <defunct>
EOF
true_ "use ignores an idle nested daemon" \
    '[ "$(box_use < "$tmp/top-docker-idle")" = idle ]'
true_ "use counts a nested workload as busy" \
    '[ "$( { cat "$tmp/top-docker-idle"; echo "8 4 S /bin/httpd -f"; } | box_use)" = busy ]'
true_ "use counts a session sleeping forever as busy" \
    '[ "$( { cat "$tmp/top-idle"; echo "8 0 S sleep infinity"; } | box_use)" = busy ]'

true_  "resolver on the gateway address" \
    'printf "UNCONN 0 0 172.17.0.1:53 0.0.0.0:*\n" | resolver_on 172.17.0.1'
true_  "resolver on every address counts" \
    'printf "UNCONN 0 0 0.0.0.0:53 0.0.0.0:*\n" | resolver_on 172.17.0.1'
true_  "a dual-stack wildcard counts" \
    'printf "UNCONN 0 0 *:53 *:*\n" | resolver_on 172.17.0.1'
false_ "a v6-only wildcard does not answer on the v4 gateway" \
    'printf "UNCONN 0 0 [::]:53 [::]:*\n" | resolver_on 172.17.0.1'
false_ "a wildcard bound to one device is not a gateway resolver" \
    'printf "UNCONN 0 0 0.0.0.0%%lo:53 0.0.0.0:*\n" | resolver_on 172.17.0.1'
false_ "the loopback stub is not a gateway resolver" \
    'printf "UNCONN 0 0 127.0.0.53%%lo:53 0.0.0.0:*\n" | resolver_on 172.17.0.1'
false_ "no listener, no resolver" ': | resolver_on 172.17.0.1'

printf 'nameserver 127.0.0.53\noptions edns0 trust-ad\n' > "$tmp/stub.conf"
printf 'nameserver 127.0.0.53\nnameserver 1.1.1.1\n' > "$tmp/mixed.conf"
: > "$tmp/empty.conf"
true_  "a stub-only resolv.conf is loopback"      'loopback_resolver "$tmp/stub.conf"'
false_ "a resolv.conf with an uplink server is not" 'loopback_resolver "$tmp/mixed.conf"'
false_ "an empty resolv.conf is not"              'loopback_resolver "$tmp/empty.conf"'

# The stub serves the boxes in $STUB/boxes (name, state, age in seconds, use,
# size) through each --format template, answers `top` from the fixtures above,
# runs the session-marker snippets against $STUB/run and the ls probe against
# the fake box in $STUB/box — under dash when installed, the box's /bin/sh —
# and logs every call. It reports the box running unless STUB_FRESH is set,
# when a launch starts a new one; STUB_STAYS then makes that box show up in
# `ps` once it has been run, STUB_PSDOWN makes `ps` fail, and STUB_UNREADY keeps
# the ready marker from appearing. Its `logs` are 25 numbered lines. The sleep
# stub (not part of docker) skips the wait between readiness probes.
export STUB="$tmp"
log="$tmp/log"
cat > "$tmp/docker" <<'STUB'
#!/bin/bash
echo "$*" >> "$STUB/log"
if [[ "${DOCKBOX_ARGV_TEST:-}" == 1 ]]
then
    echo observed > "$STUB/argv"
fi
box_sh=$(command -v dash || command -v sh)
use_of() { awk -F'\t' -v n="$1" '$1 == n { print $4 }' "$STUB/boxes"; }
case "$1" in
    container)
        while [ $# -gt 0 ] && [ "$1" != --format ]; do shift; done
        fmt="${2//\\t/$'\t'}"
        now=$(date +%s)
        while IFS=$'\t' read -r name state age use size; do
            created=$(date -d "@$((now - age))" "+%Y-%m-%d %H:%M:%S %z %Z" 2>/dev/null) ||
                created=$(date -r "$((now - age))" "+%Y-%m-%d %H:%M:%S %z %Z")
            status="Up $age seconds"
            [ "$state" = exited ] && status="Exited (0) $age seconds ago"
            row="${fmt//'{{.Names}}'/$name}"
            row="${row//'{{.State}}'/$state}"
            row="${row//'{{.Status}}'/$status}"
            row="${row//'{{.RunningFor}}'/$age seconds ago}"
            row="${row//'{{.Size}}'/$size}"
            echo "${row//'{{.CreatedAt}}'/$created}"
        done < "$STUB/boxes" ;;
    top)
        cat "$STUB/top-$(use_of "$2")" 2>/dev/null || { echo "Error: top failed" >&2; exit 1; } ;;
    exec)
        case "$*" in
            *" -i "*|*" -it "*)
                [ -n "${STUB_WIPE:-}" ] && rm -f "$STUB"/run/sess/* && rmdir "$STUB/run/sess"
                if [ -n "${STUB_EXECUTE:-}" ]; then
                    while [ "$1" != -- ]; do shift; done
                    shift
                    exec "$@"
                fi
                exit "${STUB_RC:-0}" ;;
            */run/dockbox/ready)
                [ -n "${STUB_UNREADY:-}" ] && exit 1 ;;
            *"ps -eo pid=,ppid=,stat=,args=")
                cat "$STUB/top-$(use_of "$2")" 2>/dev/null || exit 1 ;;
            *"docker -H unix:///var/run/docker.sock info")
                [ -z "${STUB_NODOCKER:-}${STUB_DOCKERDOWN:-}" ] || exit 1 ;;
            */run/dockbox/sess*)
                script="${*: -1}"
                exec "$box_sh" -c "${script//"/run/dockbox"/$STUB/run}" ;;
            *"df -k"*)
                [ "$(use_of "$2")" = fail ] && { echo "Error: exec failed" >&2; exit 1; }
                script="${*: -1}"
                PATH="$STUB/box/bin:$PATH" exec "$box_sh" -c "${script//" /"/" $STUB/box/"}" ;;
        esac ;;
    inspect)
        case "$*" in
            *HostConfig.Runtime*) echo "${STUB_RUNTIME:-runsc-dockbox}" ;;
            *State.Running*) echo "${STUB_RUNNING:-true}" ;;
            *'{{.Id}}'*) echo c0ffee ;;
            *CapAdd*) echo "${STUB_CAPS-CAP_IPC_LOCK,CAP_SYS_NICE,CAP_SYS_PTRACE}" ;;
            *)
                echo "DOCKBOX_UID=${STUB_OWNER:-$(id -u)}"
                if [ -z "${STUB_NODOCKER:-}" ]; then echo DOCKBOX_NESTED_DOCKER=1; fi ;;
        esac ;;
    info)
        [ -n "${STUB_DOWN:-}" ] && { echo "Cannot connect to the Docker daemon" >&2; exit 1; }
        echo "${STUB_RUNTIMES-runsc-dockbox}" ;;
    ps)
        [ -n "${STUB_PSDOWN:-}" ] && { echo "Cannot connect to the Docker daemon" >&2; exit 1; }
        [ -z "${STUB_FRESH:-}" ] || { [ -n "${STUB_STAYS:-}" ] && grep -q '^run ' "$STUB/log"; } &&
            echo c0ffee ;;
    logs) seq -f "boot line %g" 1 25 ;;
    run)
        while [[ $# -gt 0 ]]
        do
            if [[ "$1" == --cidfile && -z "${STUB_NOCID:-}" ]]
            then
                echo c0ffee > "$2"
            fi
            shift
        done
        [[ -z "${STUB_RUNFAIL:-}" ]] || exit "$STUB_RUNFAIL" ;;
    rm) [ "$(use_of "${*: -1}")" = fail ] && { echo "Error: rm failed" >&2; exit 1; } ;;
    network)
        [ -n "${STUB_DOWN:-}" ] && { echo "Cannot connect to the Docker daemon" >&2; exit 1; }
        echo 172.17.0.1 ;;
esac
exit 0
STUB
chmod +x "$tmp/docker"
printf '#!/bin/sh\nexit 0\n' > "$tmp/sleep"
chmod +x "$tmp/sleep"
cat > "$tmp/ss" <<'SS'
#!/bin/bash
[ -z "${STUB_DNS:-}" ] || echo "UNCONN 0      0      ${STUB_DNS}:53 0.0.0.0:*"
SS
chmod +x "$tmp/ss"
# The fake box's df reports each path whose dir holds a .df (`fstype used`) and
# fails on any other, with df's own error for a missing one.
mkdir -p "$tmp/box/bin" "$tmp/box/tmp/cargo-target" "$tmp/box/dev/shm" \
    "$tmp/box/home/dockbox" "$tmp/box/w/node_modules" "$tmp/box/w/broken"
echo "tmpfs 84"     > "$tmp/box/tmp/.df"
echo "tmpfs 20480"  > "$tmp/box/tmp/cargo-target/.df"
echo "tmpfs 0"      > "$tmp/box/dev/shm/.df"
echo "tmpfs 102400" > "$tmp/box/home/dockbox/.df"
echo "tmpfs 30720"  > "$tmp/box/w/node_modules/.df"
cat > "$tmp/box/bin/df" <<'DF'
#!/bin/sh
shift 2
echo "Type Used Mounted on"
rc=0
for p; do
    if [ -f "$p/.df" ]; then
        echo "$(cat "$p/.df") $p"
    elif [ -e "$p" ]; then
        echo "df: $p: Input/output error" >&2; rc=1
    else
        echo "df: $p: No such file or directory" >&2; rc=1
    fi
done
exit "$rc"
DF
chmod +x "$tmp/box/bin/df"
boxes() { printf '%s\t%s\t%s\t%s\t%s\n' "$@" > "$tmp/boxes"; }
dockbox() { : > "$log"; PATH="$tmp:$PATH" bash "$here/dockbox" "$@"; }

boxes dockbox-up   running 7200   idle "12.3MB (virtual 1.2GB)" \
      dockbox-busy running 7200   busy "5MB (virtual 1.2GB)" \
      dockbox-old  exited  432000 -    "0B (virtual 1.2GB)" \
      dockbox-bad  running 60     fail "1kB (virtual 1.2GB)"
ls_out=$(DOCKBOX_EPH_PATHS="$tmp/box/home/dockbox" dockbox ls 2>/dev/null)
true_  "ls header carries USE"           'grep -Eq "^NAMES +STATUS +CREATED +USE +TMPFS +DISK$" <<< "$ls_out"'
true_  "ls totals a running box's tmpfs" 'grep -Eq "^dockbox-up .* 120M +12.3MB$" <<< "$ls_out"'
true_  "ls shows - for an exited box"    'grep -Eq "^dockbox-old .* - +- +0B$" <<< "$ls_out"'
true_  "ls shows ? when the probes fail" 'grep -Eq "^dockbox-bad .* [?] +[?] +1kB$" <<< "$ls_out"'
true_  "ls USE idle with only keepers"   'grep -Eq "^dockbox-up .* idle +120M" <<< "$ls_out"'
true_  "ls USE busy with a session"      'grep -Eq "^dockbox-busy .* busy +120M" <<< "$ls_out"'
false_ "ls strips the DISK virtual size" 'grep -q virtual <<< "$ls_out"'
boxes dockbox-up running 60 idle 0B
ls_out=$(DOCKBOX_EPH_PATHS="$tmp/box/home/dockbox:$tmp/box/w/gone:$tmp/box/w/node_modules" \
    dockbox ls 2>"$tmp/err")
true_  "ls totals the mounts left past a vanished path" 'grep -Eq "^dockbox-up .* 150M +0B$" <<< "$ls_out"'
true_  "ls prints nothing for a vanished path"          '[ ! -s "$tmp/err" ]'
ls_out=$(DOCKBOX_EPH_PATHS="$tmp/box/home/dockbox:$tmp/box/w/broken" \
    dockbox ls 2>"$tmp/err")
true_  "ls shows ? when df fails on a path that exists" 'grep -Eq "^dockbox-up .* [?] +0B$" <<< "$ls_out"'
true_  "ls passes that df error through"                'grep -q "w/broken: Input/output error" "$tmp/err"'

boxes dockbox-idle-old running 14410           idle 0B \
      dockbox-idle-new running 14399           idle 0B \
      dockbox-busy     running 18000           busy 0B \
      dockbox-bad      running 18000           fail 0B \
      dockbox-gone     exited  $((2161 * 3600)) -   0B \
      dockbox-recent   exited  3600            -    0B
prune_out=$(dockbox prune 2>/dev/null); rc=$?
true_  "prune exits 0 when every removal worked"   '[ "$rc" = 0 ]'
true_  "prune removes an idle box past the grace"  'grep -qx "rm -f -v dockbox-idle-old" "$log"'
false_ "prune spares an idle box inside the grace" 'grep -q "^rm .*dockbox-idle-new$" "$log"'
false_ "prune spares a busy box"                   'grep -q "^rm .*dockbox-busy$" "$log"'
false_ "prune spares a box whose probe fails"      'grep -q "^rm .*dockbox-bad$" "$log"'
true_  "prune removes an exited box past [hours]"  'grep -qx "rm -f -v dockbox-gone" "$log"'
false_ "prune spares a young exited box"           'grep -q "^rm .*dockbox-recent$" "$log"'
true_  "prune prints what it removed" \
    '[ "$prune_out" = "$(printf "removed %s\n" dockbox-idle-old dockbox-gone)" ]'

boxes dockbox-a            running 60 idle 0B \
      dockbox-b            exited  60 -    0B \
      dockbox-c            running 60 busy 0B \
      dockbox-repo         running 60 idle 0B \
      dockbox-dockbox-repo running 60 idle 0B
dockbox rm a b >/dev/null 2>&1; rc=$?
true_  "rm removes every name given" \
    '[ "$rc" = 0 ] && [ "$(grep "^rm " "$log")" = "$(printf "rm -f -v %s\n" dockbox-a dockbox-b)" ]'
dockbox rm dockbox-repo >/dev/null 2>&1
true_  "rm of a prefixed name removes only that box" \
    '[ "$(grep "^rm " "$log")" = "rm -f -v dockbox-repo" ]'
dockbox rm a -x >/dev/null 2>&1; rc=$?
true_  "rm rejects an unknown option, removing nothing" '[ "$rc" = 2 ] && ! grep -q "^rm " "$log"'
exits 1 'dockbox rm nope' "rm exits 1 when a pattern matches nothing"
dockbox rm -a >/dev/null 2>&1
true_  "rm -a removes every box" '[ "$(grep -c "^rm -f -v " "$log")" = 5 ]'
boxes dockbox-stuck running 60 fail 0B
exits 1 'dockbox rm stuck' "rm exits 1 when docker rm fails"

mkdir -p "$tmp/home"
cd "$tmp/home" || exit 1
exits 2 'DOCKBOX_DOCKER="" dockbox ls' "an empty Docker command fails"
exits 2 'DOCKBOX_DOCKER="   " dockbox ls' "a whitespace Docker command fails"
DOCKBOX_DOCKER="env DOCKBOX_ARGV_TEST=1 docker" dockbox ls >/dev/null 2>&1; rc=$?
true_ "the host command accepts an argument array" \
    '[ "$rc" = 0 ] && [ "$(cat "$STUB/argv")" = observed ]'
HOME="$tmp/home" STUB_RC=3 dockbox -n sess exec false >/dev/null 2>&1; rc=$?
true_  "a failed session exits with its status"   '[ "$rc" = 3 ]'
true_  "a failed session still tears the box down" 'grep -qx "rm -f -v dockbox-sess" "$log"'
touch "$tmp/run/sess/4242"
HOME="$tmp/home" dockbox -n sess exec true >/dev/null 2>&1
false_ "a session leaves the box to a live sibling" 'grep -q "^rm " "$log"'
rm -f "$tmp/run/sess/4242"
HOME="$tmp/home" STUB_WIPE=1 dockbox -n sess exec true >/dev/null 2>&1
false_ "a session keeps the box when markers can't be listed" 'grep -q "^rm " "$log"'
HOME="$tmp/home" STUB_WIPE=1 STUB_RUNNING=false STUB_RC=137 \
    dockbox -n sess exec true >/dev/null 2>&1; rc=$?
true_ "a stopped session removes its container without changing its status" \
    '[ "$rc" = 137 ] && grep -qx "rm -f -v c0ffee" "$log"'
output=$(printf 'session input\n' | HOME="$tmp/home" STUB_EXECUTE=1 dockbox -n sess exec cat)
true_ "a noninteractive command receives stdin and returns stdout" \
    '[ "$output" = "session input" ]'
false_ "a noninteractive command requests no terminal" \
    'grep -q "^exec -it " "$log"'
output=$(HOME="$tmp/home" STUB_EXECUTE=1 dockbox -n sess exec \
    sh -c 'printf command-output; printf command-error >&2; exit 7' 2>"$tmp/err"); rc=$?
true_ "a command failure preserves stdout, stderr, and status" \
    '[ "$rc" = 7 ] && [ "$output" = command-output ] && [ "$(cat "$tmp/err")" = command-error ]'
true_ "a noninteractive failure still cleans the last session" \
    'grep -qx "rm -f -v dockbox-sess" "$log"'
cd "$here" || exit 1

sess="setpriv --reuid=$(id -u) --regid=$(id -g) --init-groups"
sess="$sess --inh-caps=+sys_nice,+ipc_lock,+sys_ptrace"
sess="$sess --ambient-caps=+sys_nice,+ipc_lock,+sys_ptrace -- true"
cd "$tmp/home" || exit 1
HOME="$tmp/home" STUB_FRESH=1 STUB_RUNTIMES=runc \
    dockbox -n fresh exec true >/dev/null 2>"$tmp/err"; rc=$?
true_  "a new box without gVisor fails" '[ "$rc" = 1 ]'
true_  "the missing-runtime error names the runtime" \
    'grep -q "runsc-dockbox is unavailable" "$tmp/err"'
false_ "a missing runtime stops before any box change" \
    'grep -Eq "^(rm|run) " "$log"'
HOME="$tmp/home" dockbox -n sess exec true >/dev/null 2>&1; rc=$?
true_  "gVisor re-entry succeeds" '[ "$rc" = 0 ]'
true_  "a re-entered session drops through setpriv" \
    'grep -qx "exec -i -u 0:0 -e TERM dockbox-sess $sess" "$log"'
HOME="$tmp/home" STUB_CAPS=sys_nice,ipc_lock,sys_ptrace \
    dockbox -n sess exec true >/dev/null 2>&1; rc=$?
true_ "Docker's lowercase capability names reach setpriv" \
    '[ "$rc" = 0 ] && grep -q "$sess$" "$log"'
HOME="$tmp/home" STUB_CAPS= dockbox -n sess exec true >/dev/null 2>&1; rc=$?
old="setpriv --reuid=$(id -u) --regid=$(id -g) --init-groups -- true"
true_  "a box created without the caps still enters" \
    '[ "$rc" = 0 ] && grep -qx "exec -i -u 0:0 -e TERM dockbox-sess $old" "$log"'
HOME="$tmp/home" STUB_OWNER=4321 dockbox -n sess exec true >/dev/null 2>"$tmp/err"; rc=$?
true_  "another user's box refuses entry and names -n" \
    '[ "$rc" = 1 ] && grep -q "use -n" "$tmp/err" && ! grep -q "^exec -i" "$log"'
HOME="$tmp/home" STUB_RUNTIME=runc dockbox -n legacy exec true >/dev/null 2>"$tmp/err"; rc=$?
true_ "legacy re-entry fails before a session starts" \
    '[ "$rc" = 1 ] && grep -q "does not use runsc-dockbox" "$tmp/err" && ! grep -q "^exec " "$log"'
HOME="$tmp/home" STUB_NODOCKER=1 dockbox -D -n sess exec true >/dev/null 2>"$tmp/err"; rc=$?
true_ "-D refuses an existing box without a nested daemon" \
    '[ "$rc" = 1 ] && grep -q "no ready nested Docker" "$tmp/err" && ! grep -q "^exec -i" "$log"'
HOME="$tmp/home" STUB_DOCKERDOWN=1 dockbox -D -n sess exec true >/dev/null 2>"$tmp/err"; rc=$?
true_ "-D refuses re-entry when the nested API fails" \
    '[ "$rc" = 1 ] && grep -q "no ready nested Docker" "$tmp/err" && ! grep -q "^exec -i" "$log"'
# Start a fresh box with the given flags; leaves its run line in $run and
# removes the merged-settings temp file the launch left behind.
fresh() {
    HOME="$tmp/home" STUB_FRESH=1 dockbox "$@" exec true >/dev/null 2>"$tmp/err"; rc=$?
    run=$(grep "^run " "$log")
    settings=$(sed -n 's|.* -v \([^ ]*\):/home/dockbox/.claude/settings.json:ro .*|\1|p' <<< "$run")
    [ -n "$settings" ] && rm -f -- "$settings"
    return "$rc"
}
fresh -n fresh
true_  "a new box starts"                               '[ "$rc" = 0 ]'
false_ "without a gateway resolver the box keeps Docker's DNS" \
    'grep -q -- " --dns " <<< "$run"'
mkdir -p "$tmp/home/.claude"
fresh -n fresh
sessions="--tmpfs /home/dockbox/.claude/sessions:rw,mode=0700,uid=$(id -u),gid=$(id -g)"
true_  "a new box gets a private session registry" 'grep -q -- " $sessions " <<< "$run"'
true_  "the host registry dir exists for the overmount" '[ -d "$tmp/home/.claude/sessions" ]'
STUB_DNS=172.17.0.1 fresh -n fresh
true_  "a gateway resolver becomes the box's DNS" 'grep -q -- " --dns 172.17.0.1 " <<< "$run"'
fresh -n fresh -H
true_ "-H fails before creating a box" \
    '[ "$rc" = 2 ] && grep -q "incompatible with the gVisor" "$tmp/err" && ! grep -q "^run " "$log"'
HOME="$tmp/home" STUB_FRESH=1 STUB_DOWN=1 \
    dockbox -n fresh exec true >/dev/null 2>"$tmp/err"; rc=$?
true_  "an unreachable daemon fails the launch with docker's error" \
    '[ "$rc" != 0 ] && grep -q "Cannot connect to the Docker" "$tmp/err"'
STUB_UNREADY=1 fresh -n fresh
true_  "a box that exits before it is ready fails the launch" \
    '[ "$rc" = 1 ] && grep -qx "Container exited during startup" "$tmp/err"'
true_ "a failed startup removes its created container and volumes" \
    'grep -qx "rm -f -v c0ffee" "$log"'
STUB_RUNFAIL=125 fresh -n fresh
true_ "a failed Docker start removes its created container" \
    '[ "$rc" = 1 ] && grep -qx "rm -f -v c0ffee" "$log"'
STUB_RUNFAIL=125 STUB_NOCID=1 fresh -n fresh
false_ "a failed creation removes no unowned container ID" \
    'grep -qx "rm -f -v c0ffee" "$log"'
STUB_UNREADY=1 STUB_STAYS=1 fresh -n fresh
true_  "a box that never becomes ready fails the launch, not enters" \
    '[ "$rc" = 1 ] && grep -qx "Container not ready after the startup wait" "$tmp/err" && ! grep -q "^exec -i" "$log"'
true_ "a readiness timeout removes its created container" \
    'grep -qx "rm -f -v c0ffee" "$log"'
out=$(HOME="$tmp/home" STUB_FRESH=1 STUB_UNREADY=1 STUB_STAYS=1 dockbox -n fresh exec true 2>/dev/null)
settings=$(sed -n 's|.* -v \([^ ]*\):/home/dockbox/.claude/settings.json:ro .*|\1|p' "$log")
[ -n "$settings" ] && rm -f -- "$settings"
true_  "a box that never becomes ready shows the last 20 log lines" \
    '[ "$(grep -c "^boot line" <<< "$out")" = 20 ] && grep -qx "boot line 25" <<< "$out" && ! grep -qx "boot line 5" <<< "$out"'
STUB_UNREADY=1 STUB_PSDOWN=1 fresh -n fresh
true_  "a daemon that dies during startup reports docker's error, exit 1" \
    '[ "$rc" = 1 ] && grep -q "Cannot connect to the Docker" "$tmp/err" && ! grep -q "exited during startup" "$tmp/err"'
fresh -n fresh
true_  "a new box runs the required gVisor runtime" \
    'grep -q -- " --runtime runsc-dockbox " <<< "$run"'
false_ "a new box has no host seccomp profile" \
    'grep -q -- " --security-opt seccomp=" <<< "$run"'
true_  "a new box adds the session caps" \
    'grep -q -- " --cap-add sys_nice --cap-add ipc_lock --cap-add sys_ptrace " <<< "$run"'
true_  "its first session drops through setpriv in the workdir" \
    'grep -q "^exec -i -u 0:0 -e TERM .* -w $tmp/home dockbox-fresh $sess$" "$log"'
false_ "a plain box starts no nested daemon" \
    'grep -q -- "DOCKBOX_NESTED_DOCKER=1" <<< "$run"'
fresh -n fresh -D
true_ "-D enables the local daemon" \
    'grep -q -- "DOCKBOX_NESTED_DOCKER=1" <<< "$run"'
true_ "-D grants sandbox administration capabilities" \
    'grep -q -- " --cap-add sys_admin --cap-add net_admin " <<< "$run"'
true_ "-D uses bounded executable tmpfs storage" \
    'grep -q -- " --tmpfs /var/lib/docker:rw,exec,size=2g " <<< "$run"'
false_ "-D forwards no host Docker socket" \
    'grep -q -- " -v /var/run/docker.sock:" <<< "$run"'
true_ "nested daemon logs remain available on the host" \
    'grep -q -- " --log-driver json-file --log-opt max-size=1m --log-opt max-file=1 " <<< "$run"'
STUB_UNREADY=1 fresh -n fresh -D
true_ "an unready nested daemon stops the launcher before entry" \
    '[ "$rc" = 1 ] && ! grep -q "^exec -i" "$log"'
DOCKBOX_IMAGE=custom:test fresh -n fresh
true_ "DOCKBOX_IMAGE selects the image without changing containment" \
    'grep -q -- " -- custom:test sleep infinity" <<< "$run" && grep -q -- " --runtime runsc-dockbox " <<< "$run"'
cd "$here" || exit 1

mkdir -p "$tmp/repo_with.dot+space name"
primary="$tmp/repo_with.dot+space name"
slug="${primary//[^A-Za-z0-9]/-}"
mkdir -p "$tmp/home/.claude/projects/$slug"
touch "$tmp/home/.claude/projects/$slug/session.jsonl"
HOME="$tmp/home" dockbox -n resume claude "$primary" >/dev/null 2>&1
true_ "resume maps every nonalphanumeric path character" \
    'grep -q "claude --resume" "$log"'
HOME="$tmp/home" dockbox -N -n resume claude "$primary" >/dev/null 2>&1
false_ "-N starts a new session over existing history" 'grep -q "claude --resume" "$log"'

# A project .dockboxrc takes --no-ephemeral like the command line does: builds
# persist (no overmount for node_modules), claude gets no stray "--", and no
# "ignoring" warning. The run without an rc proves the overmount is there to lose.
proj="$tmp/proj"
mkdir -p "$proj/node_modules" "$proj/server/.venv"
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe claude "$proj" >/dev/null 2>"$tmp/err"
run=$(grep "^run " "$log")
true_  "a box without an rc overmounts node_modules" \
    'grep -q -- "--tmpfs $proj/node_modules:" <<< "$run"'
true_  "a box without an rc overmounts a nested .venv" \
    'grep -q -- "--tmpfs $proj/server/.venv:" <<< "$run"'
echo "--no-ephemeral" > "$proj/.dockboxrc"
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe claude "$proj" >/dev/null 2>"$tmp/err"
run=$(grep "^run " "$log")
true_  "project rc --no-ephemeral persists builds" \
    '! grep -q -- "--tmpfs $proj/node_modules:" <<< "$run"'
true_  "project rc --no-ephemeral passes no -- to claude" \
    '[ "$(sed -n "s/^exec -i .* -- claude //p" "$log")" = "--model claude-opus-5-5 --effort high" ]'
false_ "project rc --no-ephemeral prints no ignoring warning" 'grep -q ignoring "$tmp/err"'
printf -- '--no-ephemeral' > "$proj/.dockboxrc"
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe claude "$proj" >/dev/null 2>"$tmp/err"
run=$(grep "^run " "$log")
true_  "an rc file's unterminated last line still counts" \
    '! grep -q -- "--tmpfs $proj/node_modules:" <<< "$run"'
rm -f -- "$proj/.dockboxrc"

# Without a project .dockboxrc the project-rc pass has no words to read; the
# tool flags after the tool name reach the tool, not dockbox's own parser.
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe claude --resume "$proj" >/dev/null 2>"$tmp/err"
claude_line=$(sed -n "s/^exec -i .* -- claude //p" "$log")
true_  "no project rc leaves the tool flags to the tool" \
    '[ "$claude_line" = "--model claude-opus-5-5 --effort high --resume" ]'

# -d and -x take the same alias table as the first argument; a model flag in
# the session's own arguments replaces the alias's model and effort.
bypass="--dangerously-bypass-approvals-and-sandbox"
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe -d codex "$proj" >/dev/null 2>"$tmp/err"
true_  "-d codex takes the codex alias defaults" \
    '[ "$(sed -n "s/^exec -i .* -- codex //p" "$log")" = "$bypass -m gpt-6.1-sol -c model_reasoning_effort=high" ]'
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe -x haiku "$proj" >/dev/null 2>"$tmp/err"
true_  "-x haiku runs claude on the haiku model" \
    '[ "$(sed -n "s/^exec -i .* -- claude //p" "$log")" = "--model claude-haiku-4-5-20251001" ]'
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe codex --model gpt-6-astra "$proj" >/dev/null 2>"$tmp/err"
true_  "a session --model replaces the codex alias model and effort" \
    '[ "$(sed -n "s/^exec -i .* -- codex //p" "$log")" = "$bypass --model gpt-6-astra" ]'
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe opus --model claude-sonnet-5-5 "$proj" >/dev/null 2>"$tmp/err"
true_  "a session --model replaces the claude alias model and effort" \
    '[ "$(sed -n "s/^exec -i .* -- claude //p" "$log")" = "--model claude-sonnet-5-5" ]'
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe opus -p "explain the -m flag" "$proj" >/dev/null 2>"$tmp/err"
true_  "a model flag inside a prompt keeps the alias model" \
    '[ "$(sed -n "s/^exec -i .* -- claude //p" "$log")" = "--model claude-opus-5-5 --effort high -p explain the -m flag" ]'
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe fable "$proj" >/dev/null 2>"$tmp/err"
true_ "fable pins high effort" \
    '[ "$(sed -n "s/^exec -i .* -- claude //p" "$log")" = "--model claude-fable-5-1 --effort high" ]'
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe gpt "$proj" >/dev/null 2>"$tmp/err"
true_ "astra pins high effort" \
    '[ "$(sed -n "s/^exec -i .* -- codex //p" "$log")" = "$bypass -m gpt-6-astra -c model_reasoning_effort=high" ]'
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe opus --effort xhigh "$proj" >/dev/null 2>"$tmp/err"
true_ "explicit claude effort follows the alias default" \
    '[ "$(sed -n "s/^exec -i .* -- claude //p" "$log")" = "--model claude-opus-5-5 --effort high --effort xhigh" ]'
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe codex -c model_reasoning_effort=xhigh "$proj" >/dev/null 2>"$tmp/err"
true_ "explicit codex effort follows the alias default" \
    '[ "$(sed -n "s/^exec -i .* -- codex //p" "$log")" = "$bypass -m gpt-6.1-sol -c model_reasoning_effort=high -c model_reasoning_effort=xhigh" ]'
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe codex --model gpt-5.6-terra -c model_reasoning_effort=high "$proj" >/dev/null 2>"$tmp/err"
true_ "explicit terra model and effort replace the alias defaults" \
    '[ "$(sed -n "s/^exec -i .* -- codex //p" "$log")" = "$bypass --model gpt-5.6-terra -c model_reasoning_effort=high" ]'
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe -d bash "$proj" >/dev/null 2>"$tmp/err"
true_  "-d bash is the login shell the bash argument gives" \
    'grep -q -- " -- /bin/bash -l$" "$log"'

# Any other long flag in an rc file is an error naming the file and the flag,
# in the project rc and in ~/.dockboxrc alike. After the tool name it is the
# tool's argument and reaches the tool (the test above).
echo "--verbose" > "$proj/.dockboxrc"
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe claude "$proj" >/dev/null 2>"$tmp/err"; rc=$?
true_  "a project rc long flag it does not know is an error" \
    '[ "$rc" = 1 ] && grep -qx "dockbox: unknown flag --verbose in $proj/.dockboxrc" "$tmp/err"'
false_ "a rejected project rc starts no box" 'grep -q "^run " "$log"'
rm -f -- "$proj/.dockboxrc"
echo "--verbose" > "$tmp/home/.dockboxrc"
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe claude "$proj" >/dev/null 2>"$tmp/err"; rc=$?
true_  "a home rc long flag it does not know is an error" \
    '[ "$rc" = 1 ] && grep -qx "dockbox: unknown flag --verbose in $tmp/home/.dockboxrc" "$tmp/err"'
echo "--no-ephemeral" > "$tmp/home/.dockboxrc"
HOME="$tmp/home" STUB_FRESH=1 dockbox -n pe claude "$proj" >/dev/null 2>"$tmp/err"; rc=$?
run=$(grep "^run " "$log")
true_  "a home rc --no-ephemeral still persists builds" \
    '[ "$rc" = 0 ] && ! grep -q -- "--tmpfs $proj/node_modules:" <<< "$run"'
rm -f -- "$tmp/home/.dockboxrc"

# -T mounts no project: the box keys on tmp, works in a box-only tmpfs that
# dockbox-init chowns, and its claude starts a new session over old history.
cd "$proj" || exit 1
fresh -T
true_  "-T starts a box"                  '[ "$rc" = 0 ]'
true_  "-T keys the box on tmp"           'grep -q -- " --name dockbox-tmp " <<< "$run"'
true_  "-T works in a tmpfs workdir" \
    'grep -q -- " --tmpfs /tmp/work:rw,exec,mode=1777 " <<< "$run" && grep -q -- " -w /tmp/work " <<< "$run"'
true_  "-T chowns the workdir"            'grep -q -- "DOCKBOX_EPH_PATHS=/home/dockbox:/tmp/work " <<< "$run"'
false_ "-T mounts no project dir"         'grep -q -- " -v $proj:" <<< "$run"'
false_ "-T overmounts no project build dir" 'grep -q -- "$proj/node_modules" <<< "$run"'
mkdir -p "$tmp/home/.claude/projects/-tmp-work"
touch "$tmp/home/.claude/projects/-tmp-work/session.jsonl"
HOME="$tmp/home" dockbox -T >/dev/null 2>&1
true_  "-T re-enters its own box"         'grep -q "^exec -i .* dockbox-tmp setpriv " "$log"'
false_ "-T starts a new session"          'grep -q "claude --resume" "$log"'
HOME="$tmp/home" STUB_FRESH=1 dockbox -T claude "$proj" >/dev/null 2>"$tmp/err"; rc=$?
true_  "-T refuses a project dir, starting no box" \
    '[ "$rc" = 2 ] && grep -q "use -v" "$tmp/err" && ! grep -q "^run " "$log"'
printf -- "-T\n" > "$proj/.dockboxrc"
fresh -n pe
true_  "project rc -T is ignored"         'grep -q "ignoring -T" "$tmp/err" && grep -q -- " -v $proj:$proj:rw " <<< "$run"'
rm -f -- "$proj/.dockboxrc"
fresh -n pe -B
true_  "-B puts build dirs on Docker volumes" \
    'grep -q -- " -v $proj/node_modules " <<< "$run" && ! grep -q -- "--tmpfs $proj/node_modules:" <<< "$run"'
cd "$here" || exit 1

# The help line naming the flags a project rc ignores lists exactly the set the
# rc loop's `case` ignores.
ignored=$(sed -n 's/^[[:space:]]*\([A-Za-z|]*\)) echo "dockbox: ignoring -\$opt.*/\1/p' "$here/dockbox" | tr '|' '\n' | sort)
helped=$(dockbox --help | grep 'ignored there' | grep -oE -- '-[A-Za-z]' | tr -d - | sort)
true_  "the ignored-flag set is read from the code" '[ -n "$ignored" ]'
true_  "help names exactly the flags a project rc ignores" '[ "$helped" = "$ignored" ]'

exits 2 'apply_flag n ..'  "-n .. rejected"
exits 2 'apply_flag n ""'  "-n empty rejected"
exits 2 'apply_flag n a/b' "-n with slash rejected"
true_   "-n keys the dir, prefix stays" 'apply_flag n goodname; [ "$dir_override" = goodname ]'

gpg_forward=""; apply_flag K
true_ "-K sets gpg_forward" '[ -n "$gpg_forward" ]'

## sandbox note -------------------------------------------------------------
nout="$(sandbox_note myhost bridge \
    -v /h/.claude:/home/dockbox/.claude:rw -v /p:/p:rw \
    -v /tmp/s.json:/home/dockbox/.claude/settings.json:ro \
    -v /p/node_modules --tmpfs /home/dockbox:rw,exec,mode=1777)"
true_ "note names the sandbox"       '[[ "$nout" == *CLAUDE_SANDBOX=dockbox* ]]'
true_ "note names the host"          '[[ "$nout" == *"host \`myhost\`"* ]]'
true_ "note names the network"       '[[ "$nout" == *"Network: bridge"* ]]'
true_ "note routes GitHub over HTTPS" '[[ "$nout" == *"credential.helper='"'"'!gh auth git-credential'"'"'"* ]]'
true_ "note maps a box path to host" '[[ "$nout" == *"- /home/dockbox/.claude (rw) <- /h/.claude"* ]]'
true_ "note marks a same-path mount" '[[ "$nout" == *"- /p (rw) <- same path"* ]]'
true_ "note keeps a ro mode"         '[[ "$nout" == *"settings.json (ro) <- /tmp/s.json"* ]]'
true_ "note lists volume and tmpfs as lost" \
    '[[ "$nout" == *"Lost at exit (tmpfs or volume): /p/node_modules /home/dockbox"* ]]'
true_ "note lists a -B volume as an empty dependency dir" '[[ "$nout" == *"  - /p/node_modules"* ]]'
true_ "note names the gh token -g brings" '[[ "$nout" == *"without \`-g\` has none"* ]]'
nout="$(sandbox_note myhost bridge -v /p:/p:rw \
    --tmpfs /p/.venv:rw,exec,mode=1777 --tmpfs /tmp:rw,exec,mode=1777)"
true_ "note lists an empty dependency dir" \
    '[[ "$nout" == *"empty box-only mounts."*"  - /p/.venv"$'"'"'\n'"'"'"- GitHub"* ]]'
false_ "note omits a tmpfs that is no dependency dir" '[[ "$nout" == *"  - /tmp"* ]]'
nout="$(sandbox_note myhost bridge -v /p:/p:rw --tmpfs /tmp:rw,exec,mode=1777)"
false_ "note claims no empty dependency dir without one" '[[ "$nout" == *box-only* ]]'

echo "dockbox/test.sh: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
