#!/usr/bin/env python3
"""Stop hook: nudge commit and diary when either is due.

Silent in a ship child that judges rather than builds: SHIP_ROLE set to
anything but a worker. Workers keep the nudges; the commit nudge is what
makes them commit.
"""

import json
import os
import subprocess
import sys
from datetime import UTC
from datetime import datetime

NUDGE_INTERVAL = 600


def git_run(cwd, *args, timeout=5):
    return subprocess.run(
        args, capture_output=True, text=True, timeout=timeout, cwd=cwd, check=False
    )


def git_dir(cwd):
    """Absolute git dir, or None outside a repo or on failure."""
    r = git_run(cwd, 'git', 'rev-parse', '--git-dir')
    if r.returncode != 0:
        return None
    gd = r.stdout.strip()
    if not os.path.isabs(gd):
        gd = os.path.join(cwd, gd)
    return gd


def git_path(cwd, name):
    gd = git_dir(cwd)
    return None if gd is None else os.path.join(gd, name)


def write_stamp(path, text):
    try:
        with open(path, 'w') as f:
            f.write(text)
    except OSError:
        pass


def nudge_due(stamp, now):
    if stamp is None or not os.path.exists(stamp):
        return True
    return now.timestamp() - os.path.getmtime(stamp) >= NUDGE_INTERVAL


def hook_event(data):
    env_event = os.environ.get('KRONAEL_HOOK_EVENT')
    if env_event:
        return env_event
    for key in 'hook_event', 'hook_event_name', 'hookEventName':
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return ''


def emit(parts, data):
    reason = '\n'.join(parts)
    if hook_event(data) == 'PostToolUse':
        print(
            json.dumps(
                {
                    'hookSpecificOutput': {
                        'hookEventName': 'PostToolUse',
                        'additionalContext': reason,
                    },
                }
            )
        )
        return
    print(json.dumps({'decision': 'block', 'reason': reason}))


def nudges(cwd, now):
    parts = []

    # Uncommitted changes
    stamp = git_path(cwd, 'claude-commit-nudge')
    r = git_run(cwd, 'git', 'status', '--porcelain', '-uno')
    if stamp is not None and r.returncode != 0:
        parts.append(
            'git status failed — cannot tell whether the tree is dirty:\n'
            + (r.stderr.strip() or f'exit {r.returncode}')
        )
    elif r.returncode == 0 and r.stdout.strip() and nudge_due(stamp, now):
        diff = git_run(cwd, 'git', 'diff', '--stat')
        msg = 'Uncommitted changes detected.'
        if diff.stdout.strip():
            msg += '\n' + diff.stdout.strip()
        msg += (
            '\nCommit your work — but split it into coherent chunks: one '
            'commit per logical change, related files together, '
            'unrelated work in separate commits. Not one mega-commit, not '
            'premature fragments. Run /commit.\n'
            'Rules: "type(scope): Message" (scope optional), subject <= 72 chars '
            '(overflow -> second '
            '-m body); NEVER add -A, -a, --amend, push, squash, Co-Authored-By, '
            '--no-verify.'
        )
        parts.append(msg)
        if stamp is not None:
            write_stamp(stamp, now.isoformat())

    # Diary freshness (missing today or stale > 1h) — only inside a git repo.
    # A tracked diary is committed on its branch, so it lives in the current
    # worktree; an ignored one keeps a single copy in the main tree.
    common = git_run(cwd, 'git', 'rev-parse', '--git-common-dir')
    if common.returncode == 0:
        common_dir = common.stdout.strip()
        if not os.path.isabs(common_dir):
            common_dir = os.path.join(cwd, common_dir)
        dated = '.diary/' + now.strftime('%Y%m%d') + '.md'
        top = git_run(cwd, 'git', 'rev-parse', '--show-toplevel')
        worktree = top.stdout.strip() if top.returncode == 0 else cwd
        ignored = git_run(worktree, 'git', 'check-ignore', '-q', dated).returncode == 0
        base = os.path.dirname(common_dir) if ignored else worktree
        diary_dir = os.path.join(base, '.diary')
        diary_file = os.path.join(diary_dir, now.strftime('%Y%m%d') + '.md')
        hhmm = now.strftime('%H:%M %Y-%m-%d')
        if not os.path.exists(diary_file):
            parts.append(f'No diary entry for today (now {hhmm}). Run /diary.')
        elif now.timestamp() - os.path.getmtime(diary_file) > 3600:
            parts.append(
                f'Diary not updated in over an hour (now {hhmm}). '
                'Run /diary deliberately if there is work to record.'
            )
    return parts


def is_ship_judge():
    role = os.environ.get('SHIP_ROLE', '')
    return bool(role) and not role.startswith('worker')


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):  # fmt: skip
        sys.exit(0)

    if not isinstance(data, dict) or os.environ.get('CLAUDE_EVAL'):
        sys.exit(0)
    if is_ship_judge():
        sys.exit(0)

    cwd = data.get('cwd', '.')
    now = datetime.now(tz=UTC)
    parts = [] if data.get('stop_hook_active') else nudges(cwd, now)
    if parts:
        emit(parts, data)


if __name__ == '__main__':
    main()
