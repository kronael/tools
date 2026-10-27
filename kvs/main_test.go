package main

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"testing"
	"time"
)

var binary string

func TestMain(m *testing.M) {
	dir, err := os.MkdirTemp("", "kvs-build")
	if err != nil {
		panic(err)
	}
	binary = filepath.Join(dir, "kvs")
	build := exec.Command("go", "build", "-o", binary, ".")
	if out, err := build.CombinedOutput(); err != nil {
		panic(string(out))
	}
	code := m.Run()
	// temp dir; a failed remove only leaves a file under TMPDIR
	_ = os.RemoveAll(dir)
	os.Exit(code)
}

type harness struct {
	t    *testing.T
	dir  string
	repo string
}

func newHarness(t *testing.T) harness {
	t.Helper()
	return harness{t: t, dir: t.TempDir(), repo: t.TempDir()}
}

// kvs runs the binary with KVS_DIR set and the project pinned to the harness
// directory, and returns stdout and the exit code.
func (h harness) kvs(args ...string) (string, int) {
	h.t.Helper()
	cmd := exec.Command(binary, append([]string{"-p", h.repo}, args...)...)
	cmd.Env = append(os.Environ(), "KVS_DIR="+h.dir, "CLAUDE_SESSION_ID=")
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	err := cmd.Run()
	code := 0
	if exit, ok := err.(*exec.ExitError); ok {
		code = exit.ExitCode()
	} else if err != nil {
		h.t.Fatalf("kvs %v: %v", args, err)
	}
	if stderr.Len() > 0 && code != exitUsage {
		h.t.Logf("stderr: %s", stderr.String())
	}
	return strings.TrimRight(stdout.String(), "\n"), code
}

func (h harness) want(args []string, wantOut string, wantCode int) {
	h.t.Helper()
	out, code := h.kvs(args...)
	if out != wantOut || code != wantCode {
		h.t.Fatalf("kvs %v = (%q, %d), want (%q, %d)", args, out, code, wantOut, wantCode)
	}
}

func TestGetSetDel(t *testing.T) {
	h := newHarness(t)
	h.want([]string{"get", "a"}, "", exitAbsent)
	h.want([]string{"set", "a", "one"}, "", exitOK)
	h.want([]string{"get", "a"}, "one", exitOK)
	h.want([]string{"set", "a", "two"}, "", exitOK)
	h.want([]string{"get", "a"}, "two", exitOK)
	h.want([]string{"del", "a", "missing"}, "", exitOK)
	h.want([]string{"get", "a"}, "", exitAbsent)
}

func TestSetFromStdin(t *testing.T) {
	h := newHarness(t)
	cmd := exec.Command(binary, "-p", h.repo, "set", "blob", "-")
	cmd.Env = append(os.Environ(), "KVS_DIR="+h.dir)
	cmd.Stdin = strings.NewReader("{\"level\": 2}\n")
	if out, err := cmd.CombinedOutput(); err != nil {
		t.Fatalf("set from stdin: %v %s", err, out)
	}
	h.want([]string{"get", "blob"}, "{\"level\": 2}", exitOK)
}

func TestScopes(t *testing.T) {
	h := newHarness(t)
	h.want([]string{"set", "k", "project"}, "", exitOK)
	h.want([]string{"-s", "s1", "set", "k", "session"}, "", exitOK)
	h.want([]string{"-g", "set", "k", "global"}, "", exitOK)
	h.want([]string{"get", "k"}, "project", exitOK)
	h.want([]string{"-s", "s1", "get", "k"}, "session", exitOK)
	h.want([]string{"-s", "s2", "get", "k"}, "", exitAbsent)
	h.want([]string{"-g", "get", "k"}, "global", exitOK)
	other := harness{t: t, dir: h.dir, repo: t.TempDir()}
	other.want([]string{"get", "k"}, "", exitAbsent)
	other.want([]string{"-g", "get", "k"}, "global", exitOK)
}

func TestSessionFromEnvironment(t *testing.T) {
	h := newHarness(t)
	cmd := exec.Command(binary, "-p", h.repo, "set", "k", "v")
	cmd.Env = append(os.Environ(), "KVS_DIR="+h.dir, "CLAUDE_SESSION_ID=env-session")
	if out, err := cmd.CombinedOutput(); err != nil {
		t.Fatalf("set: %v %s", err, out)
	}
	h.want([]string{"-s", "env-session", "get", "k"}, "v", exitOK)
	h.want([]string{"get", "k"}, "", exitAbsent)
}

func TestProjectIsTheMainTreeSlug(t *testing.T) {
	h := newHarness(t)
	git := func(args ...string) {
		cmd := exec.Command("git", append([]string{"-C", h.repo}, args...)...)
		if out, err := cmd.CombinedOutput(); err != nil {
			t.Fatalf("git %v: %v %s", args, err, out)
		}
	}
	git("init", "-q")
	git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init")
	worktree := filepath.Join(t.TempDir(), "linked")
	git("worktree", "add", "-q", "--detach", worktree)
	h.want([]string{"set", "k", "from-main"}, "", exitOK)
	linked := harness{t: t, dir: h.dir, repo: worktree}
	linked.want([]string{"get", "k"}, "from-main", exitOK)
	if got, want := slug("/a/b.c d"), "-a-b-c-d"; got != want {
		t.Fatalf("slug = %q, want %q", got, want)
	}
}

func TestIncr(t *testing.T) {
	h := newHarness(t)
	h.want([]string{"incr", "n"}, "1", exitOK)
	h.want([]string{"incr", "n", "5"}, "6", exitOK)
	h.want([]string{"incr", "n", "-2"}, "4", exitOK)
	h.want([]string{"set", "word", "abc"}, "", exitOK)
	_, code := h.kvs("incr", "word")
	if code != exitError {
		t.Fatalf("incr on a word exited %d, want %d", code, exitError)
	}
	_, code = h.kvs("incr", "n", "x")
	if code != exitUsage {
		t.Fatalf("incr with a bad N exited %d, want %d", code, exitUsage)
	}
}

func TestCompareAndSet(t *testing.T) {
	h := newHarness(t)
	h.want([]string{"set", "flag", "1", "-i", ""}, "", exitOK)
	h.want([]string{"set", "flag", "2", "-i", ""}, "", exitAbsent)
	h.want([]string{"get", "flag"}, "1", exitOK)
	h.want([]string{"set", "flag", "2", "-i", "9"}, "", exitAbsent)
	h.want([]string{"set", "flag", "2", "-i", "1"}, "", exitOK)
	h.want([]string{"get", "flag"}, "2", exitOK)
	h.want([]string{"set", "new", "x", "-i", "1"}, "", exitAbsent)
}

func TestTTL(t *testing.T) {
	h := newHarness(t)
	// Keys with a two-second TTL survive these commands, then expire and reset.
	h.want([]string{"set", "short", "v", "-t", "2"}, "", exitOK)
	h.want([]string{"incr", "window", "-t", "2"}, "1", exitOK)
	h.want([]string{"incr", "window"}, "2", exitOK)
	h.want([]string{"get", "short"}, "v", exitOK)
	time.Sleep(2100 * time.Millisecond)
	h.want([]string{"get", "short"}, "", exitAbsent)
	h.want([]string{"incr", "window", "-t", "1"}, "1", exitOK)
	h.want([]string{"set", "short", "again", "-i", ""}, "", exitOK)
	_, code := h.kvs("set", "bad", "v", "-t", "0")
	if code != exitUsage {
		t.Fatalf("ttl 0 exited %d, want %d", code, exitUsage)
	}
}

func TestListAndSessions(t *testing.T) {
	h := newHarness(t)
	h.want([]string{"-s", "s1", "set", "caveman:level", "2"}, "", exitOK)
	h.want([]string{"-s", "s1", "set", "caveman:last", "27"}, "", exitOK)
	h.want([]string{"-s", "s1", "set", "other", "x"}, "", exitOK)
	h.want([]string{"-s", "s2", "set", "a", "b"}, "", exitOK)
	h.want([]string{"set", "wide", "p"}, "", exitOK)
	h.want([]string{"-s", "s1", "ls", "caveman:"}, "caveman:last\t27\ncaveman:level\t2", exitOK)
	h.want([]string{"-s", "s1", "ls"}, "caveman:last\t27\ncaveman:level\t2\nother\tx", exitOK)
	h.want([]string{"ls"}, "wide\tp", exitOK)
	out, code := h.kvs("sessions")
	if code != exitOK {
		t.Fatalf("sessions exited %d", code)
	}
	lines := strings.Split(out, "\n")
	if len(lines) != 2 || !strings.HasPrefix(lines[0], "s2\t1\t") && !strings.HasPrefix(lines[1], "s2\t1\t") {
		t.Fatalf("sessions = %q", out)
	}
	for _, line := range lines {
		if strings.HasPrefix(line, "s1\t") && !strings.HasPrefix(line, "s1\t3\t") {
			t.Fatalf("s1 should hold 3 keys: %q", line)
		}
	}
	out, _ = h.kvs("-g", "sessions")
	if !strings.Contains(out, slug(h.repo)+"\ts1\t3\t") {
		t.Fatalf("global sessions = %q", out)
	}
}

func TestUsage(t *testing.T) {
	h := newHarness(t)
	out, code := h.kvs("-h")
	if code != exitOK || !strings.Contains(out, "kvs get KEY") {
		t.Fatalf("help = (%q, %d)", out, code)
	}
	_, code = h.kvs("bogus")
	if code != exitUsage {
		t.Fatalf("unknown command exited %d", code)
	}
	_, code = h.kvs("get")
	if code != exitUsage {
		t.Fatalf("get without key exited %d", code)
	}
	_, code = h.kvs("--frob")
	if code != exitUsage {
		t.Fatalf("unknown option exited %d", code)
	}
}

func TestParallelIncrLosesNoUpdate(t *testing.T) {
	h := newHarness(t)
	const procs, perProc = 16, 25
	var wg sync.WaitGroup
	errs := make(chan error, procs)
	for p := 0; p < procs; p++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			script := fmt.Sprintf("for i in $(seq %d); do %s -p %s incr counter >/dev/null || exit 9; done", perProc, binary, h.repo)
			cmd := exec.Command("sh", "-c", script)
			cmd.Env = append(os.Environ(), "KVS_DIR="+h.dir)
			if out, err := cmd.CombinedOutput(); err != nil {
				errs <- fmt.Errorf("%v: %s", err, out)
			}
		}()
	}
	wg.Wait()
	close(errs)
	for err := range errs {
		t.Fatal(err)
	}
	h.want([]string{"get", "counter"}, strconv.Itoa(procs*perProc), exitOK)
}

func TestLockRunsOneHolderAtATime(t *testing.T) {
	h := newHarness(t)
	log := filepath.Join(h.dir, "holders.log")
	const procs, rounds = 8, 3
	var wg sync.WaitGroup
	for p := 0; p < procs; p++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for r := 0; r < rounds; r++ {
				script := fmt.Sprintf("echo start $$ >> %s; sleep 0.02; echo end $$ >> %s", log, log)
				cmd := exec.Command(binary, "-p", h.repo, "lock", "shared", "--", "sh", "-c", script)
				cmd.Env = append(os.Environ(), "KVS_DIR="+h.dir)
				if out, err := cmd.CombinedOutput(); err != nil {
					t.Errorf("lock: %v %s", err, out)
				}
			}
		}()
	}
	wg.Wait()
	data, err := os.ReadFile(log)
	if err != nil {
		t.Fatal(err)
	}
	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	if len(lines) != procs*rounds*2 {
		t.Fatalf("%d log lines, want %d", len(lines), procs*rounds*2)
	}
	for i := 0; i < len(lines); i += 2 {
		start := strings.Fields(lines[i])
		end := strings.Fields(lines[i+1])
		if start[0] != "start" || end[0] != "end" || start[1] != end[1] {
			t.Fatalf("two holders overlapped around line %d: %q / %q", i, lines[i], lines[i+1])
		}
	}
}

func TestLockBusyAndExitCodes(t *testing.T) {
	h := newHarness(t)
	ready := filepath.Join(h.dir, "ready")
	holder := exec.Command(binary, "-p", h.repo, "lock", "busy", "--", "sh", "-c",
		"touch "+ready+"; sleep 1")
	holder.Env = append(os.Environ(), "KVS_DIR="+h.dir)
	if err := holder.Start(); err != nil {
		t.Fatal(err)
	}
	for i := 0; i < 100; i++ {
		if _, err := os.Stat(ready); err == nil {
			break
		}
		time.Sleep(10 * time.Millisecond)
	}
	_, code := h.kvs("lock", "busy", "-n", "--", "true")
	if code != exitHeld {
		t.Fatalf("-n on a held lock exited %d, want %d", code, exitHeld)
	}
	_, code = h.kvs("lock", "busy", "-w", "0.1", "--", "true")
	if code != exitHeld {
		t.Fatalf("-w on a held lock exited %d, want %d", code, exitHeld)
	}
	// the holder's exit code is the sleep's; the test only needs the lock freed
	_ = holder.Wait()
	_, code = h.kvs("lock", "busy", "-n", "--", "sh", "-c", "exit 7")
	if code != 7 {
		t.Fatalf("lock passed exit %d, want 7", code)
	}
	_, code = h.kvs("lock", "a/b", "--", "true")
	if code != exitUsage {
		t.Fatalf("lock with a path name exited %d, want %d", code, exitUsage)
	}
	_, code = h.kvs("lock", "only-name")
	if code != exitUsage {
		t.Fatalf("lock without a command exited %d, want %d", code, exitUsage)
	}
}
