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

if not isinstance(data, dict) or data.get('stop_hook_active'):
    sys.exit(0)

cwd = data.get('cwd', '.')
parts = []

# Uncommitted changes
r = subprocess.run(
    ['git', 'status', '--porcelain', '-uno'],
    capture_output=True,
    text=True,
    timeout=5,
    cwd=cwd,
    check=False,
)
if r.returncode == 0 and r.stdout.strip():
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
    msg += '\nConsider running /commit.'
    parts.append(msg)

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
