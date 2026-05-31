#!/usr/bin/env python3
"""Stop hook: nudge commit and diary if needed."""

import json
import os
import subprocess
import sys
from datetime import UTC
from datetime import datetime

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError, ValueError):
    sys.exit(0)

if not isinstance(data, dict) or data.get('stop_hook_active') or os.environ.get('CLAUDE_EVAL'):
    sys.exit(0)

cwd = data.get('cwd', '.')
parts = []

# Commit nudge is throttled: nag at most once per NUDGE_INTERVAL so work can
# accumulate into coherent chunks instead of being nagged after every stop.
NUDGE_INTERVAL = 600


def git_path(name):
    r = subprocess.run(
        ['git', 'rev-parse', '--git-dir'],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=cwd,
        check=False,
    )
    if r.returncode != 0:
        return None
    gd = r.stdout.strip()
    if not os.path.isabs(gd):
        gd = os.path.join(cwd, gd)
    return os.path.join(gd, name)


def nudge_due(stamp):
    if stamp is None or not os.path.exists(stamp):
        return True
    return datetime.now(tz=UTC).timestamp() - os.path.getmtime(stamp) >= NUDGE_INTERVAL


# Uncommitted changes
r = subprocess.run(
    ['git', 'status', '--porcelain', '-uno'],
    capture_output=True,
    text=True,
    timeout=5,
    cwd=cwd,
    check=False,
)
stamp = git_path('claude-commit-nudge')
if r.returncode == 0 and r.stdout.strip() and nudge_due(stamp):
    diff = subprocess.run(
        ['git', 'diff', '--stat'],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=cwd,
        check=False,
    )
    msg = 'Uncommitted changes detected.'
    if diff.stdout.strip():
        msg += '\n' + diff.stdout.strip()
    msg += (
        '\nCommit your work — but split it into coherent chunks: one '
        '[section] commit per logical change, related files together, '
        'unrelated work in separate commits. Not one mega-commit, not '
        'premature fragments. Run /commit.\n'
        'Rules: "[section] Message", subject <= 72 chars (overflow -> second '
        '-m body); NEVER add -A, -a, --amend, push, squash, Co-Authored-By, '
        '--no-verify.'
    )
    parts.append(msg)
    if stamp is not None:
        try:
            with open(stamp, 'w') as f:
                f.write(datetime.now(tz=UTC).isoformat())
        except OSError:
            pass

# Diary freshness (missing today or stale > 1h)
diary_dir = os.path.join(cwd, '.diary')
if os.path.isdir(diary_dir):
    diary_file = os.path.join(diary_dir, datetime.now(tz=UTC).strftime('%Y%m%d') + '.md')
    if not os.path.exists(diary_file):
        parts.append('No diary entry for today. Consider running /diary.')
    elif datetime.now(tz=UTC).timestamp() - os.path.getmtime(diary_file) > 3600:
        parts.append('Diary not updated in over an hour. Consider running /diary.')

if parts:
    print(json.dumps({'decision': 'block', 'reason': '\n'.join(parts)}))
