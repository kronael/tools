"""The hooks' memory: the kvs CLI (../../kvs), scoped by session and project.

Every call is silent when kvs is not installed or fails: a hook without memory
still runs, it only forgets.
"""

import shutil
import subprocess

BINARY = shutil.which('kvs')
TIMEOUT_S = 3


def run(args, session=None, cwd=None):
    """Return (stdout, exit code), or None when kvs is unavailable."""
    if not BINARY:
        return None
    command = [BINARY]
    if session:
        command += ['-s', str(session)]
    if cwd:
        command += ['-p', str(cwd)]
    command += list(args)
    try:
        done = subprocess.run(
            command, capture_output=True, text=True, timeout=TIMEOUT_S, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.rstrip('\n'), done.returncode


def get(key, session=None, cwd=None):
    done = run(['get', key], session, cwd)
    if done is None or done[1] != 0:
        return None
    return done[0]


def set(key, value, session=None, cwd=None, ttl=None, if_old=None):  # noqa: A001
    """True when the value was written; False on a failed --if or no kvs."""
    args = ['set', key, str(value)]
    if ttl:
        args += ['-t', str(ttl)]
    if if_old is not None:
        args += ['-i', if_old]
    done = run(args, session, cwd)
    return done is not None and done[1] == 0


def incr(key, session=None, cwd=None, ttl=None):
    args = ['incr', key]
    if ttl:
        args += ['-t', str(ttl)]
    done = run(args, session, cwd)
    if done is None or done[1] != 0:
        return None
    try:
        return int(done[0])
    except ValueError:
        return None
