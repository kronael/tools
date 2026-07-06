#!/usr/bin/env python3
"""Stop hook: nudge commit and diary if needed."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from collections import deque
from datetime import UTC
from datetime import datetime

NUDGE_INTERVAL = 600
HEADER_RECENT = 300
FIN_STAMP_DIR = 'claude-fin-stop'


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


def is_fin_text(text):
    text = text.strip()
    compact = ''.join(text.split())
    return (
        text == '/fin'
        or '<command-name>fin</command-name>' in compact
        or '<command-name>/fin</command-name>' in compact
    )


def iter_content_texts(value):
    if isinstance(value, str):
        yield value
        return
    if not isinstance(value, list):
        return
    for item in value:
        if isinstance(item, str):
            yield item
        elif isinstance(item, dict):
            text = item.get('text')
            if isinstance(text, str):
                yield text


def iter_transcript_user_texts(lines):
    for line in lines:
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            if is_fin_text(line):
                yield line
            continue
        if not isinstance(item, dict) or item.get('type') != 'user':
            continue
        message = item.get('message')
        if isinstance(message, dict):
            yield from iter_content_texts(message.get('content'))
        yield from iter_content_texts(item.get('content'))


def get_fin_stamp(data):
    token = data.get('session_id') or data.get('sessionId') or data.get('transcript_path')
    if not isinstance(token, str) or not token:
        return None
    tmpdir = os.environ.get('TMPDIR')
    if tmpdir is None:
        tmpdir = tempfile.gettempdir()
    name = hashlib.sha256(token.encode()).hexdigest()[:32]
    return os.path.join(tmpdir, FIN_STAMP_DIR, name)


def mark_fin_seen(data):
    stamp = get_fin_stamp(data)
    if stamp is None:
        return
    try:
        os.makedirs(os.path.dirname(stamp), exist_ok=True)
        with open(stamp, 'w') as f:
            f.write(datetime.now(tz=UTC).isoformat())
    except OSError:
        pass


def fin_recent(data):
    stamp = get_fin_stamp(data)
    if stamp is not None and os.path.exists(stamp):
        return False
    transcript = data.get('transcript_path')
    if not transcript or not os.path.exists(transcript):
        return False
    try:
        with open(transcript, encoding='utf-8') as f:
            recent = deque(f, maxlen=60)
    except OSError:
        return False
    for text in iter_transcript_user_texts(recent):
        if is_fin_text(text):
            mark_fin_seen(data)
            return True
    return False


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

    if hook_event(data) != 'PostToolUse' and fin_recent(data):
        parts.append(
            '/fin (finish mode) was invoked. Before stopping, re-run the '
            'open-items pass: every item must be done, blocked, or explicitly '
            'deferred with a reason.'
        )

    if parts:
        emit(parts, data)


if __name__ == '__main__':
    main()
