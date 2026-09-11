#!/usr/bin/env python3
"""Stop hook: nudge commit and diary if needed, else recap the turn."""

import contextlib
import json
import os
import subprocess
import sys
import time
from datetime import UTC
from datetime import datetime

NUDGE_INTERVAL = 600
HEADER_RECENT = 300
RECAP_BUDGET = 0.6
RECAP_COMMITS = 6
RECAP_PATHS = 4
CONFLICT_CODES = frozenset({'DD', 'AU', 'UD', 'UA', 'DU', 'AA', 'UU'})
STUCK_OPS = {
    'MERGE_HEAD': 'merge',
    'rebase-merge': 'rebase',
    'rebase-apply': 'rebase',
    'CHERRY_PICK_HEAD': 'cherry-pick',
    'REVERT_HEAD': 'revert',
    'BISECT_LOG': 'bisect',
}


def git_run(cwd, *args, timeout=5):
    return subprocess.run(
        args, capture_output=True, text=True, timeout=timeout, cwd=cwd, check=False
    )


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


def git_dir(cwd):
    r = git_run(cwd, 'git', 'rev-parse', '--git-dir')
    if r.returncode != 0:
        return None
    gd = r.stdout.strip()
    if not os.path.isabs(gd):
        gd = os.path.join(cwd, gd)
    return gd


def git_path(cwd, name):
    gd = git_dir(cwd)
    if gd is None:
        return None
    return os.path.join(gd, name)


def write_stamp(path, text):
    try:
        with open(path, 'w') as f:
            f.write(text)
    except OSError:
        pass


def read_stamp(path):
    """ISO time stored in a stamp, or '' when the stamp is missing or unreadable."""
    try:
        with open(path) as f:
            text = f.read().strip()
        datetime.fromisoformat(text)
    except (OSError, ValueError):  # fmt: skip
        return ''
    return text


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


def emit_recap(recap):
    print(json.dumps({'ok': True, 'systemMessage': recap}))


def nudges(cwd, now):
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
            write_stamp(stamp, now.isoformat())

    # Diary freshness (missing today or stale > 1h) — only inside a git repo.
    # --git-common-dir resolves to the main repo's .git even from a worktree.
    common = git_run(cwd, 'git', 'rev-parse', '--git-common-dir')
    if common.returncode == 0:
        common_dir = common.stdout.strip()
        if not os.path.isabs(common_dir):
            common_dir = os.path.join(cwd, common_dir)
        diary_dir = os.path.join(os.path.dirname(common_dir), '.diary')
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
    return parts


def recap_git(cwd, deadline, run, *args):
    """stdout of a git command, or None once it fails or the recap budget is spent."""
    left = deadline - time.monotonic()
    if left <= 0:
        return None
    r = run(cwd, 'git', *args, timeout=left)
    if r.returncode != 0:
        return None
    return r.stdout


def landed_lines(cwd, deadline, run, since):
    if not since:
        head = recap_git(cwd, deadline, run, 'log', '-n', '1', '--format=%h %s')
        return [] if head is None else ['head ' + head.strip()]
    log = recap_git(cwd, deadline, run, 'log', f'--since={since}', '-n', '200', '--format=%h %s')
    if log is None:
        return []
    commits = log.splitlines()
    hhmm = datetime.fromisoformat(since).strftime('%H:%M')
    if not commits:
        return [f'since {hhmm}Z: no commits']
    n = len(commits)
    header = f'since {hhmm}Z: {n} commit' + ('s' if n != 1 else '')
    if n > RECAP_COMMITS:
        header += f', newest {RECAP_COMMITS}'
    return [header] + ['+ ' + c for c in commits[:RECAP_COMMITS]]


def plus_minus(numstat):
    plus = 0
    minus = 0
    for line in numstat.splitlines():
        added, deleted, _ = line.split('\t', 2)
        if added.isdigit():
            plus += int(added)
        if deleted.isdigit():
            minus += int(deleted)
    return f'+{plus} -{minus}'


def is_new(top, path, since_ts):
    if since_ts is None:
        return False
    try:
        return os.path.getmtime(os.path.join(top, path)) > since_ts
    except OSError:
        return False


def dirty_lines(top, status, numstat, since_ts):
    """Untracked paths count only when touched inside the window: the rest is old noise."""
    changed = 0
    conflicted = 0
    untracked = 0
    paths = []
    for line in status.splitlines():
        code = line[:2]
        path = line[3:]
        if code == '??':
            if not is_new(top, path, since_ts):
                continue
            untracked += 1
        elif code in CONFLICT_CODES:
            conflicted += 1
        else:
            changed += 1
        paths.append(path)
    if not paths:
        return ['nothing uncommitted']
    counts = []
    if changed:
        counts.append(f'{changed} changed')
    if conflicted:
        counts.append(f'{conflicted} conflicted')
    if untracked:
        counts.append(f'{untracked} untracked')
    header = 'uncommitted: ' + ', '.join(counts)
    if numstat:
        header += f' ({plus_minus(numstat)})'
    shown = ' '.join(paths[:RECAP_PATHS])
    if len(paths) > RECAP_PATHS:
        shown += ' …'
    return [header, '  ' + shown]


def stuck_lines(gd):
    ops = sorted({op for name, op in STUCK_OPS.items() if os.path.exists(os.path.join(gd, name))})
    return [', '.join(ops) + ' in progress'] if ops else []


def build_recap(cwd, session_id, now, run=git_run, budget=RECAP_BUDGET):
    """Compact turn recap: commits landed, dirty tree, stuck git operations."""
    gd = git_dir(cwd)
    if gd is None:
        return ''
    deadline = time.monotonic() + budget
    session = str(session_id or 'default').replace('/', '_')
    stamp = os.path.join(gd, f'claude-recap-{session}')
    since = read_stamp(stamp)
    since_ts = datetime.fromisoformat(since).timestamp() if since else None
    lines = landed_lines(cwd, deadline, run, since)
    status = recap_git(cwd, deadline, run, 'status', '--porcelain')
    top = recap_git(cwd, deadline, run, 'rev-parse', '--show-toplevel')
    if status is not None and top is not None:
        numstat = recap_git(cwd, deadline, run, 'diff', '--numstat', 'HEAD')
        lines += dirty_lines(top.strip(), status, numstat, since_ts)
    lines += stuck_lines(gd)
    if lines:
        write_stamp(stamp, now.isoformat(timespec='seconds'))
    return '\n'.join(lines)


def safe_recap(cwd, session_id, now, run=git_run):
    """The recap is best effort: any failure drops it and never touches the nudges."""
    recap = ''
    with contextlib.suppress(Exception):
        recap = build_recap(cwd, session_id, now, run)
    return recap


def recap_wanted(data):
    return hook_event(data) != 'PostToolUse' and not os.environ.get('KRONAEL_IN_CODEX')


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):  # fmt: skip
        sys.exit(0)

    if not isinstance(data, dict) or os.environ.get('CLAUDE_EVAL'):
        sys.exit(0)

    cwd = data.get('cwd', '.')
    now = datetime.now(tz=UTC)
    parts = [] if data.get('stop_hook_active') else nudges(cwd, now)
    if parts:
        emit(parts, data)
        return
    if recap_wanted(data):
        recap = safe_recap(cwd, data.get('session_id'), now)
        if recap:
            emit_recap(recap)


if __name__ == '__main__':
    main()
