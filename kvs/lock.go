package main

import (
	"errors"
	"os"
	"os/exec"
	"path/filepath"
	"syscall"
	"time"
)

const exitHeld = 75

var errHeld = errors.New("lock is held")

// acquire takes an exclusive flock on path, waiting up to wait (0 = do not
// wait, negative = wait forever). The lock lives as long as the returned file.
func acquire(path string, wait time.Duration) (*os.File, error) {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return nil, err
	}
	file, err := os.OpenFile(path, os.O_CREATE|os.O_RDWR, 0o644)
	if err != nil {
		return nil, err
	}
	deadline := time.Now().Add(wait)
	for {
		err = syscall.Flock(int(file.Fd()), syscall.LOCK_EX|syscall.LOCK_NB)
		if err == nil {
			return file, nil
		}
		if !errors.Is(err, syscall.EWOULDBLOCK) {
			// lock failed; the descriptor is useless
			_ = file.Close()
			return nil, err
		}
		if wait >= 0 && !time.Now().Before(deadline) {
			// lock busy; the descriptor is useless
			_ = file.Close()
			return nil, errHeld
		}
		time.Sleep(10 * time.Millisecond)
	}
}

// runLocked runs argv while holding the lock at path and returns the command's
// exit code; the kernel drops the lock when this process or the file closes.
func runLocked(path string, wait time.Duration, argv []string) (int, error) {
	file, err := acquire(path, wait)
	if err != nil {
		return 0, err
	}
	// closing releases the lock; the error changes nothing after the command ran
	defer file.Close() //nolint:errcheck
	cmd := exec.Command(argv[0], argv[1:]...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	err = cmd.Run()
	var exit *exec.ExitError
	if errors.As(err, &exit) {
		return exit.ExitCode(), nil
	}
	return 0, err
}
