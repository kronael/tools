#!/usr/bin/env python3
"""Stop hook: nudge commit and diary when either is due.

Silent in a ship child that judges rather than builds: SHIP_ROLE set to
anything but a worker. Workers keep the nudges; the commit nudge is what
makes them commit.
"""

import json
import os
import re
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
            '-m body); NEVER add -A, -a, --amend, push, Co-Authored-By, '
            '--no-verify; squash unpushed commits only, via /squash.'
        )
        parts.append(msg)
        if stamp is not None:
            write_stamp(stamp, now.isoformat())

    # Diary freshness (missing today or stale > 1h) — only inside a git repo.
    # The diary lives under ~/.claude, keyed on the main tree (skills/diary).
    main = main_tree(cwd)
    if main is not None:
        path = diary_file(main, now)
        hhmm = now.strftime('%H:%M %Y-%m-%d')
        if not os.path.exists(path):
            parts.append(f'No diary entry for today (now {hhmm}). Run /diary.')
        elif now.timestamp() - os.path.getmtime(path) > 3600:
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
