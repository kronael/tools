#!/usr/bin/env python3
"""Stop hook: nudge commit and diary if needed.

Both nudges are throttled by the same stamp mechanism (nudge_due/touch). The
commit stamp lives in the repo's git dir and expires after NUDGE_INTERVAL; the
diary stamp is session-keyed in ~/.claude/state and never expires, so the diary
nudge fires at most once per session no matter how many repos the session
visits or how long it runs.
"""

import importlib.util
import json
import os
import subprocess
import sys
from datetime import UTC
from datetime import datetime

spec = importlib.util.spec_from_file_location(
    'hook_state', os.path.expanduser('~/.claude/hooks/lib/state.py')
)
hook_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_state)
session_state = hook_state.session_state

NUDGE_INTERVAL = 600  # commit nudge: at most every 10 min per repo.
DIARY_INTERVAL = None  # diary nudge: once per session, never repeated.
DIARY_STALE = 3600


def git_run(cwd, *args):
    return subprocess.run(args, capture_output=True, text=True, timeout=5, cwd=cwd, check=False)


def append_header(diary_file, hhmm):
    """Append a blank `## HH:MM` header to today's diary. True if written.

    Never adds a second header while the previous one is still empty: an
    unfilled header IS the pending nudge, and stacking more only produced
    files of nothing but blank headers.
    """
    try:
        if os.path.exists(diary_file):
            with open(diary_file) as f:
                written = [line for line in f.read().splitlines() if line.strip()]
            if written and written[-1].startswith('## '):
                return False
        else:
            os.makedirs(os.path.dirname(diary_file), exist_ok=True)
        with open(diary_file, 'a') as f:
            f.write(f'\n## {hhmm}\n\n')
    except OSError:
        return False
    return True


def git_path(cwd, name):
    r = git_run(cwd, 'git', 'rev-parse', '--git-dir')
    if r.returncode != 0:
        return None
    gd = r.stdout.strip()
    if not os.path.isabs(gd):
        gd = os.path.join(cwd, gd)
    return os.path.join(gd, name)


def nudge_due(stamp, now, interval=NUDGE_INTERVAL):
    """True if this nudge may fire. interval None means once per stamp, ever."""
    if stamp is None or not os.path.exists(stamp):
        return True
    if interval is None:
        return False
    return now.timestamp() - os.path.getmtime(stamp) >= interval


def touch(stamp, now):
    if stamp is None:
        return
    try:
        with open(stamp, 'w') as f:
            f.write(now.isoformat())
    except OSError:
        pass


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


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        sys.exit(0)

    if not isinstance(data, dict) or data.get('stop_hook_active') or os.environ.get('CLAUDE_EVAL'):
        sys.exit(0)

    cwd = data.get('cwd', '.')
    now = datetime.now(tz=UTC)
    parts = []

    # Uncommitted changes
    r = git_run(cwd, 'git', 'status', '--porcelain', '-uno')
    stamp = git_path(cwd, 'claude-commit-nudge')
    if r.returncode == 0 and r.stdout.strip() and nudge_due(stamp, now):
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
        touch(stamp, now)

    # Diary freshness (missing today or stale > 1h) — only inside a git repo.
    # --git-common-dir resolves to the main repo's .git even from a worktree.
    diary_stamp = session_state('diary-nudge', data.get('session_id'))
    common = git_run(cwd, 'git', 'rev-parse', '--git-common-dir')
    if common.returncode == 0 and nudge_due(diary_stamp, now, DIARY_INTERVAL):
        git_dir = common.stdout.strip()
        if not os.path.isabs(git_dir):
            git_dir = os.path.join(cwd, git_dir)
        diary_dir = os.path.join(os.path.dirname(git_dir), '.diary')
        diary_file = os.path.join(diary_dir, now.strftime('%Y%m%d') + '.md')
        hhmm = now.strftime('%H:%M %Y-%m-%d')
        missing = not os.path.exists(diary_file)
        if missing or now.timestamp() - os.path.getmtime(diary_file) > DIARY_STALE:
            state = (
                f'No diary entry for today (now {hhmm}).'
                if missing
                else f'Diary not updated in over an hour (now {hhmm}).'
            )
            added = ' Entry header appended —' if append_header(diary_file, hhmm) else ''
            parts.append(f'{state}{added} fill it in. Run /diary.')
            touch(diary_stamp, now)

    if parts:
        emit(parts, data)


if __name__ == '__main__':
    main()
