resume_margin_test() {
    regression_setup
    mkdir -p "$ROOT/vm"
    echo 0 > "$ROOT/vm/idle"
    local probe_state=paused:io-error free_value=2047 qmp_rc=0
    run_state() { echo "$probe_state"; }
    df() {
        [[ "$free_value" != unavailable ]] || return 44
        printf 'Avail\n%s\n' "$free_value"
    }
    qmp_box() {
        echo "$*" >> "$fixture/resume-qmp"
        return "$qmp_rc"
    }
    session_count() { echo 0; }
    RESUME_FREE=2048
    : > "$systemd_log"
    check_box vm 2> "$fixture/resume-error"
    [[ ! -e "$fixture/resume-qmp" && ! -s "$systemd_log" ]]
    grep -q '2047 MiB free, need 2048 MiB' "$fixture/resume-error"
    for free_value in 2048 2049
    do
        : > "$fixture/resume-qmp"
        check_box vm
        [[ "$(cat "$fixture/resume-qmp")" = 'vm cont' ]]
    done
    : > "$fixture/resume-qmp"
    for probe_state in paused paused:prelaunch running
    do
        session_count() { echo 1; }
        check_box vm
        [[ ! -s "$fixture/resume-qmp" && ! -s "$systemd_log" ]]
    done
    probe_state=paused:io-error
    RESUME_FREE=0 free_value=unavailable check_box vm
    [[ ! -s "$fixture/resume-qmp" ]]
    for free_value in unavailable invalid
    do
        if check_box vm 2> "$fixture/resume-error"
        then
            return 1
        fi
        [[ ! -s "$fixture/resume-qmp" && ! -s "$systemd_log" ]]
    done
    free_value=2048 qmp_rc=45
    if check_box vm 2> "$fixture/resume-error"
    then
        return 1
    else
        [[ "$?" = 45 ]]
    fi
    [[ ! -s "$systemd_log" ]]
    : > "$fixture/resume-qmp"
    for RESUME_FREE in '' -1 2G ' 2' 1.5 1000000000
    do
        if check_box vm 2> "$fixture/resume-error"
        then
            return 1
        else
            [[ "$?" = 2 ]]
        fi
        [[ ! -s "$fixture/resume-qmp" && ! -s "$systemd_log" ]]
    done
    RESUME_FREE=0002048
    validate_resume
    [[ "$RESUME_FREE" = 2048 ]]
}
regression 'io-error resumes only at the free-space margin and preserves failures' \
    resume_margin_test

resume_startup_test() {
    regression_setup
    local probe_state=paused:io-error ready_calls=0
    run_state() { echo "$probe_state"; }
    ssh_plain_box() {
        ((ready_calls += 1))
        [[ "$probe_state" = running ]]
    }
    df() { printf 'Avail\n2048\n'; }
    qmp_box() {
        [[ "$*" = 'vm cont' ]]
        probe_state=running
    }
    sleep() { [[ "$1" = 0.1 ]]; }
    RESUME_FREE=2048
    wait_ready vm
    [[ "$probe_state" = running && "$ready_calls" = 2 ]]
    probe_state=paused:io-error
    if RESUME_FREE=0 wait_ready vm 2> "$fixture/disabled-resume-error"
    then
        return 1
    fi
    grep -q 'qemubox stop vm' "$fixture/disabled-resume-error"
    if QEMUBOX_RESUME_FREE=bad QEMUBOX_HOME="$ROOT/invalid-resume" \
        bash "$here/qemubox" -T exec true 2> "$fixture/invalid-resume-error"
    then
        return 1
    else
        [[ "$?" = 2 ]]
    fi
    [[ ! -e "$ROOT/invalid-resume" ]]
}
regression 'readiness recovers io-error pauses before its timer starts' \
    resume_startup_test
