#!/usr/bin/env python3
"""Stop: point at `commit` when the tree is dirty and at `diary` when today's
entry is missing or stale. PostToolUse: the same check every 100 tool calls or
10 minutes, as advisory context.

Silent in a ship child that judges rather than builds: SHIP_ROLE set to
anything but a worker. Workers keep the nudges; the commit nudge is what makes
them commit.
"""

import json
import os
import re
import subprocess
import sys
from datetime import UTC
from datetime import datetime

from lib import kvs
from lib.reminder import block
from lib.reminder import context
from lib.reminder import emit
from lib.reminder import reminder
from lib.state import hook_event

NUDGE_INTERVAL = 600
PERIODIC_CALLS = 100
DIARY_STALE = 3600


def git_run(cwd, *args, timeout=5):
    return subprocess.run(
        args, capture_output=True, text=True, timeout=timeout, cwd=cwd, check=False
    )


def main_tree(cwd):
    """The main worktree: first entry of `git worktree list`, or None outside a repo."""
    r = git_run(cwd, 'git', 'worktree', 'list', '--porcelain', '-z')
    if r.returncode != 0:
        return None
    return r.stdout.split('\0', 1)[0].removeprefix('worktree ')


def project_slug(path):
    """Claude Code's project directory name: every non-alphanumeric becomes '-'."""
    return re.sub(r'[^A-Za-z0-9]', '-', path)


def diary_file(main, now):
    """~/.claude/projects/<slug>/diary/YYYYMMDD.md, keyed on the main tree."""
    return os.path.join(
        os.path.expanduser('~/.claude/projects'),
        project_slug(main),
        'diary',
        now.strftime('%Y%m%d') + '.md',
    )


def commit_nudge(cwd):
    r = git_run(cwd, 'git', 'status', '--porcelain', '-uno')
    if r.returncode != 0:
        if main_tree(cwd) is None:
            return None
        return reminder(
            'commit', text='git status failed: ' + (r.stderr.strip() or f'exit {r.returncode}')
        )
    files = len(r.stdout.strip().splitlines())
    if not files:
        return None
    if kvs.BINARY and not kvs.set('commit-nudged', 1, cwd=cwd, ttl=NUDGE_INTERVAL, if_old=''):
        return None
    return reminder('commit', text='uncommitted changes; commit in coherent chunks', files=files)


def diary_nudge(cwd, now):
    main = main_tree(cwd)
    if main is None:
        return None
    path = diary_file(main, now)
    if not os.path.exists(path):
        return reminder('diary', text='no diary entry today')
    age = now.timestamp() - os.path.getmtime(path)
    if age > DIARY_STALE:
        return reminder('diary', text='diary not updated', age=f'{int(age // 3600)}h')
    return None


def nudges(cwd, now):
    return [line for line in (commit_nudge(cwd), diary_nudge(cwd, now)) if line]


def is_ship_judge():
    role = os.environ.get('SHIP_ROLE', '')
    return bool(role) and not role.startswith('worker')


def periodic_due(cwd):
    """Every PERIODIC_CALLS tool calls, and the first call of each NUDGE_INTERVAL window."""
    calls = kvs.incr('tool-calls', cwd=cwd, ttl=NUDGE_INTERVAL)
    return calls is not None and (calls == 1 or calls % PERIODIC_CALLS == 0)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        return
    if not isinstance(data, dict) or os.environ.get('CLAUDE_EVAL') or is_ship_judge():
        return
    if data.get('stop_hook_active'):
        return
    cwd = data.get('cwd', '.')
    event = hook_event(data)
    if event == 'PostToolUse':
        if periodic_due(cwd):
            lines = nudges(cwd, datetime.now(tz=UTC))
            if lines:
                emit(context(event, *lines))
        return
    lines = nudges(cwd, datetime.now(tz=UTC))
    if lines:
        emit(block(*lines))


if __name__ == '__main__':
    main()
