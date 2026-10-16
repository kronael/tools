// kvs is a key-value store on one SQLite file for scripts and hooks: get, set,
// incr, del, ls, sessions and a flock-style lock wrapper, scoped by project
// and session. README.md holds the contract.
package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

const usage = `kvs — key-value store on one SQLite file, scoped by project and session

  kvs get KEY                       print the value; exit 1 when absent
  kvs set KEY VALUE [-t S] [-i OLD] write; VALUE "-" reads stdin
  kvs incr KEY [N] [-t S]           add N (default 1) to an integer, print it
  kvs del KEY...                    remove keys
  kvs ls [PREFIX]                   key<TAB>value lines of the scope
  kvs sessions                      session<TAB>keys<TAB>last write
  kvs lock NAME [-w S] [-n] -- CMD ARGS...   run CMD holding the lock NAME

  -p DIR   project directory (default: the current directory's main git tree)
  -s ID    session (default: $CLAUDE_SESSION_ID, else project-wide)
  -g       global scope, shared by every project
  -t S     --ttl: the key expires after S seconds
  -i OLD   --if: write only when the current value is OLD ("" = absent)
  -w S     lock: wait up to S seconds (default: forever); -n: do not wait

Database: $KVS_DIR/kvs.db, KVS_DIR defaults to $XDG_STATE_HOME/kvs (~/.local/state/kvs).
Exit: 0 ok, 1 absent or condition failed, 2 usage, 3 database or lock error,
75 lock held, else the exit code of the command lock ran.
`

const (
	exitOK     = 0
	exitAbsent = 1
	exitUsage  = 2
	exitError  = 3
)

var nonAlnum = regexp.MustCompile(`[^A-Za-z0-9]`)

type options struct {
	dir     string
	session string
	global  bool
	ttl     int64
	ifOld   *string
	wait    time.Duration
	args    []string
}

func main() {
	os.Exit(run(os.Args[1:], os.Stdout, os.Stderr))
}

func run(argv []string, stdout, stderr io.Writer) int {
	opts, err := parse(argv)
	if err != nil {
		fmt.Fprintln(stderr, "kvs:", err)
		fmt.Fprint(stderr, usage)
		return exitUsage
	}
	if len(opts.args) == 0 || opts.args[0] == "-h" || opts.args[0] == "--help" {
		fmt.Fprint(stdout, usage)
		return exitOK
	}
	command := opts.args[0]
	args := opts.args[1:]
	dir := dataDir()
	scope, err := resolveScope(opts)
	if err != nil {
		fmt.Fprintln(stderr, "kvs:", err)
		return exitError
	}
	if command == "lock" {
		return lockCommand(dir, scope, opts, args, stderr)
	}
	store, err := Open(dir)
	if err != nil {
		fmt.Fprintln(stderr, "kvs:", err)
		return exitError
	}
	// every command finished its statements; a close error changes nothing
	defer store.Close() //nolint:errcheck
	code, err := dispatch(store, scope, opts, command, args, stdout)
	if err != nil {
		fmt.Fprintln(stderr, "kvs:", err)
	}
	return code
}

func dispatch(store *Store, scope Scope, opts options, command string, args []string, stdout io.Writer) (int, error) {
	switch command {
	case "get":
		if len(args) != 1 {
			return exitUsage, errors.New("get takes one KEY")
		}
		value, err := store.Get(scope, args[0])
		if errors.Is(err, errAbsent) {
			return exitAbsent, nil
		}
		if err != nil {
			return exitError, err
		}
		fmt.Fprintln(stdout, value)
		return exitOK, nil
	case "set":
		if len(args) != 2 {
			return exitUsage, errors.New("set takes KEY and VALUE")
		}
		value := args[1]
		if value == "-" {
			data, err := io.ReadAll(bufio.NewReader(os.Stdin))
			if err != nil {
				return exitError, err
			}
			value = strings.TrimRight(string(data), "\n")
		}
		err := store.Set(scope, args[0], value, opts.ttl, opts.ifOld)
		if errors.Is(err, errAbsent) {
			return exitAbsent, nil
		}
		if err != nil {
			return exitError, err
		}
		return exitOK, nil
	case "incr":
		if len(args) < 1 || len(args) > 2 {
			return exitUsage, errors.New("incr takes KEY and an optional N")
		}
		n := int64(1)
		if len(args) == 2 {
			parsed, err := strconv.ParseInt(args[1], 10, 64)
			if err != nil {
				return exitUsage, fmt.Errorf("N must be an integer, got %q", args[1])
			}
			n = parsed
		}
		value, err := store.Incr(scope, args[0], n, opts.ttl)
		if err != nil {
			return exitError, err
		}
		fmt.Fprintln(stdout, value)
		return exitOK, nil
	case "del":
		if len(args) == 0 {
			return exitUsage, errors.New("del takes at least one KEY")
		}
		if err := store.Del(scope, args); err != nil {
			return exitError, err
		}
		return exitOK, nil
	case "ls":
		if len(args) > 1 {
			return exitUsage, errors.New("ls takes an optional PREFIX")
		}
		prefix := ""
		if len(args) == 1 {
			prefix = args[0]
		}
		entries, err := store.List(scope, prefix)
		if err != nil {
			return exitError, err
		}
		for _, entry := range entries {
			fmt.Fprintf(stdout, "%s\t%s\n", entry.Key, entry.Value)
		}
		return exitOK, nil
	case "sessions":
		if len(args) != 0 {
			return exitUsage, errors.New("sessions takes no argument")
		}
		rows, err := store.Sessions(scope.Project, opts.global)
		if err != nil {
			return exitError, err
		}
		for _, row := range rows {
			when := row.Updated.UTC().Format(time.RFC3339)
			if opts.global {
				fmt.Fprintf(stdout, "%s\t%s\t%d\t%s\n", row.Project, row.Session, row.Keys, when)
			} else {
				fmt.Fprintf(stdout, "%s\t%d\t%s\n", row.Session, row.Keys, when)
			}
		}
		return exitOK, nil
	}
	return exitUsage, fmt.Errorf("unknown command %q", command)
}

func lockCommand(dir string, scope Scope, opts options, args []string, stderr io.Writer) int {
	if len(args) < 2 {
		fmt.Fprintln(stderr, "kvs: lock takes NAME -- CMD ARGS...")
		return exitUsage
	}
	name := args[0]
	if name == "" || strings.ContainsAny(name, "/\\") || name == "." || name == ".." {
		fmt.Fprintf(stderr, "kvs: lock NAME must be a plain name, got %q\n", name)
		return exitUsage
	}
	project := scope.Project
	if project == "" {
		project = "_global"
	}
	path := filepath.Join(dir, "locks", project, name)
	code, err := runLocked(path, opts.wait, args[1:])
	if errors.Is(err, errHeld) {
		return exitHeld
	}
	if err != nil {
		fmt.Fprintln(stderr, "kvs:", err)
		return exitError
	}
	return code
}

// parse splits argv into options and the command with its arguments; the
// first "--" ends option parsing so lock's command keeps its own flags.
func parse(argv []string) (options, error) {
	opts := options{wait: -1}
	var err error
	for i := 0; i < len(argv); i++ {
		arg := argv[i]
		if arg == "--" {
			opts.args = append(opts.args, argv[i+1:]...)
			return opts, nil
		}
		if !strings.HasPrefix(arg, "-") || arg == "-" || len(opts.args) > 0 && isValueOf(opts.args, i, argv) {
			opts.args = append(opts.args, arg)
			continue
		}
		next := func() (string, error) {
			if i+1 >= len(argv) {
				return "", fmt.Errorf("%s needs a value", arg)
			}
			i++
			return argv[i], nil
		}
		var value string
		switch arg {
		case "-p", "--project":
			if opts.dir, err = next(); err != nil {
				return opts, err
			}
		case "-s", "--session":
			if opts.session, err = next(); err != nil {
				return opts, err
			}
		case "-g", "--global":
			opts.global = true
		case "-t", "--ttl":
			if value, err = next(); err != nil {
				return opts, err
			}
			if opts.ttl, err = strconv.ParseInt(value, 10, 64); err != nil || opts.ttl <= 0 {
				return opts, fmt.Errorf("--ttl needs a positive number of seconds, got %q", value)
			}
		case "-i", "--if":
			if value, err = next(); err != nil {
				return opts, err
			}
			opts.ifOld = &value
		case "-w", "--wait":
			if value, err = next(); err != nil {
				return opts, err
			}
			seconds, err := strconv.ParseFloat(value, 64)
			if err != nil || seconds < 0 {
				return opts, fmt.Errorf("--wait needs a number of seconds, got %q", value)
			}
			opts.wait = time.Duration(seconds * float64(time.Second))
		case "-n", "--nowait":
			opts.wait = 0
		case "-h", "--help":
			opts.args = append([]string{"-h"}, opts.args...)
			return opts, nil
		default:
			return opts, fmt.Errorf("unknown option %s", arg)
		}
	}
	return opts, nil
}

// isValueOf reports whether argv[i] is a negative number given to incr, the
// one positional that may start with "-".
func isValueOf(args []string, i int, argv []string) bool {
	if args[0] != "incr" {
		return false
	}
	_, err := strconv.ParseInt(argv[i], 10, 64)
	return err == nil
}

func dataDir() string {
	if dir := os.Getenv("KVS_DIR"); dir != "" {
		return dir
	}
	if state := os.Getenv("XDG_STATE_HOME"); state != "" {
		return filepath.Join(state, "kvs")
	}
	home, err := os.UserHomeDir()
	if err != nil {
		home = "."
	}
	return filepath.Join(home, ".local", "state", "kvs")
}

func resolveScope(opts options) (Scope, error) {
	session := opts.session
	if session == "" {
		session = os.Getenv("CLAUDE_SESSION_ID")
	}
	if opts.global {
		return Scope{Session: session}, nil
	}
	dir := opts.dir
	if dir == "" {
		cwd, err := os.Getwd()
		if err != nil {
			return Scope{}, err
		}
		dir = cwd
	}
	root, err := mainTree(dir)
	if err != nil {
		return Scope{}, err
	}
	return Scope{Project: slug(root), Session: session}, nil
}

// mainTree is the main worktree of the repository holding dir, or dir itself
// outside git: the first entry of `git worktree list`.
func mainTree(dir string) (string, error) {
	abs, err := filepath.Abs(dir)
	if err != nil {
		return "", err
	}
	out, err := exec.Command("git", "-C", abs, "worktree", "list", "--porcelain").Output()
	if err != nil {
		return abs, nil
	}
	first, _, _ := strings.Cut(string(out), "\n")
	if root, ok := strings.CutPrefix(first, "worktree "); ok && root != "" {
		return root, nil
	}
	return abs, nil
}

func slug(path string) string {
	return nonAlnum.ReplaceAllString(path, "-")
}
