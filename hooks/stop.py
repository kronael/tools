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
    msg += (
        '\nConsider running /commit.\n'
        'Commit rules: format "[section] Message", subject <= 72 chars '
        '(overflow -> second -m body); NEVER add -A, -a, --amend, push, squash, '
        'Co-Authored-By, --no-verify.'
    )
    parts.append(msg)

# Diary freshness (missing today or stale > 1h)
diary_dir = os.path.join(cwd, '.diary')
if os.path.isdir(diary_dir):
    diary_file = os.path.join(diary_dir, datetime.now(tz=UTC).strftime('%Y%m%d') + '.md')
    if not os.path.exists(diary_file):
        parts.append('No diary entry for today. Consider running /diary.')
    elif datetime.now(tz=UTC).timestamp() - os.path.getmtime(diary_file) > 3600:
        parts.append('Diary not updated in over an hour. Consider running /diary.')

# /fin enforcement: if the user recently invoked /fin (finish mode), don't let
# a stop slide on work that was falsely deferred. Scan the tail of the
# transcript for a recent /fin and, if found, force a re-check.
transcript = data.get('transcript_path')
if transcript and os.path.exists(transcript):
    try:
        with open(transcript, encoding='utf-8') as f:
            recent = ''.join(f.readlines()[-60:])
    except OSError:
        recent = ''
    if '/fin' in recent or '<command-name>fin' in recent or 'finish mode' in recent:
        parts.append(
            '/fin (finish mode) was invoked. Before you stop, RE-RUN the '
            'open-items pass. A "deferred" item is legitimate ONLY if it is '
            'blocked (waiting on the user) or genuinely out of scope. If '
            'anything you labelled "deferred", "later", "marginal", "not worth '
            'it", or "next session" is actually doable now, you are bullshitting '
            'the user -- CONTINUE and finish it instead of stopping. Stop ONLY '
            'when every active item is truly done, blocked, or out of scope -- '
            'and say which for each.'
        )

if parts:
    print(json.dumps({'decision': 'block', 'reason': '\n'.join(parts)}))
