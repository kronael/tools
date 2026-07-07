#!/usr/bin/env python3
"""Stop hook: nudge commit and diary if needed."""

import json
import os
import subprocess
import sys
from datetime import UTC
from datetime import datetime

NUDGE_INTERVAL = 600
HEADER_RECENT = 300


def git_run(cwd, *args):
    return subprocess.run(args, capture_output=True, text=True, timeout=5, cwd=cwd, check=False)


def append_header(diary_file, hhmm):
    """Append a blank `## HH:MM` header to today's diary, creating dirs/file.

    Skip if the file already ends with a header newer than HEADER_RECENT,
    to avoid spamming empty headers on repeated stops.
    """
    try:
        if os.path.exists(diary_file):
            if datetime.now(tz=UTC).timestamp() - os.path.getmtime(diary_file) < HEADER_RECENT:
                return
        else:
            os.makedirs(os.path.dirname(diary_file), exist_ok=True)
        with open(diary_file, 'a') as f:
            f.write(f'\n## {hhmm}\n\n')
    except OSError:
        pass


def git_path(cwd, name):
    r = git_run(cwd, 'git', 'rev-parse', '--git-dir')
    if r.returncode != 0:
        return None
    gd = r.stdout.strip()
    if not os.path.isabs(gd):
        gd = os.path.join(cwd, gd)
    return os.path.join(gd, name)


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
        if stamp is not None:
            try:
                with open(stamp, 'w') as f:
                    f.write(now.isoformat())
            except OSError:
                pass

    # Diary freshness (missing today or stale > 1h) — only inside a git repo.
    # --git-common-dir resolves to the main repo's .git even from a worktree.
    common = git_run(cwd, 'git', 'rev-parse', '--git-common-dir')
    if common.returncode == 0:
        git_dir = common.stdout.strip()
        if not os.path.isabs(git_dir):
            git_dir = os.path.join(cwd, git_dir)
        diary_dir = os.path.join(os.path.dirname(git_dir), '.diary')
        diary_file = os.path.join(diary_dir, now.strftime('%Y%m%d') + '.md')
        hhmm = now.strftime('%H:%M %Y-%m-%d')
        if not os.path.exists(diary_file):
            append_header(diary_file, hhmm)
            parts.append(
                f'No diary entry for today (now {hhmm}). Entry header '
                'appended — fill it in. Run /diary.'
            )
        elif now.timestamp() - os.path.getmtime(diary_file) > 3600:
            append_header(diary_file, hhmm)
            parts.append(
                f'Diary not updated in over an hour (now {hhmm}). '
                'Entry header appended — fill it in.'
            )

    if parts:
        emit(parts, data)


if __name__ == '__main__':
    main()
