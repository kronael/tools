#!/usr/bin/env python3
"""Memory nudge: prompt a session memory review, far less often than diary.

Fires on:
- PreCompact (both "manual" and "auto" triggers) — always. Compaction is the
  moment context would otherwise be lost, so it's the natural low-frequency
  trigger the user asked for; it happens at most a handful of times per
  session, unlike the diary nudge's every-10-min/100-tool-calls cadence.
- Stop — at most ONCE per session, as a fallback for sessions that end
  without ever compacting. Fires on the first Stop where EITHER the session
  has run past SESSION_THRESHOLD wall-clock OR at least STOP_COUNT_THRESHOLD
  Stops have occurred — the count path is what covers *short* sessions that
  never approach the 30-min mark yet still did real work. Ultra-trivial
  one/two-turn sessions stay under the count and never nudge. Not recurring
  like stop.py's diary/commit nudges.

No LLM call. Never blocks. Emits additionalContext (Stop) or systemMessage
(PreCompact, matching the local.py/reclaude.py idiom already proven to
survive compaction in this codebase).
"""

import contextlib
import json
import os
import sys
import time

SESSION_THRESHOLD = 1800  # 30 min wall-clock — one path to the Stop fallback.
STOP_COUNT_THRESHOLD = 3  # ...or this many Stops, whichever comes first, so a
# short (sub-30-min) but multi-turn session still gets one memory nudge.
# PreCompact is unconditional and independent of both.

NUDGE_TEXT = (
    'Session memory check: before this context is lost, evaluate the '
    'conversation for anything worth persisting long-term — user '
    'corrections, confirmed approaches/decisions, durable project facts, '
    'reference pointers. Save qualifying items via the auto-memory '
    'mechanism (frontmatter name/description/metadata.type: '
    'user/feedback/project/reference, indexed in MEMORY.md), or run '
    '/learn for a fuller extraction pass — /learn now covers both '
    'session-memory evaluation and skill/pattern extraction. Skip if '
    'nothing qualifies; do not force it.'
)


def hook_event(data):
    for key in 'hook_event', 'hook_event_name', 'hookEventName':
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return ''


def state_path(cwd, session_id, name):
    state_dir = os.path.join(cwd, '.claude', 'tmp')
    try:
        os.makedirs(state_dir, exist_ok=True)
    except OSError:
        return None
    return os.path.join(state_dir, f'{name}-{session_id}')


def emit_precompact():
    print(json.dumps({'ok': True, 'systemMessage': NUDGE_TEXT}))


def emit_stop():
    print(
        json.dumps(
            {
                'hookSpecificOutput': {
                    'hookEventName': 'Stop',
                    'additionalContext': NUDGE_TEXT,
                },
            }
        )
    )


def read_start(path):
    """Return (started_ts, stop_count) from the start file, or (None, 0)."""
    try:
        with open(path) as f:
            parts = f.read().split()
        return float(parts[0]), int(parts[1])
    except (OSError, ValueError, IndexError):
        return None, 0


def write_start(path, started, count):
    try:
        with open(path, 'w') as f:
            f.write(f'{started} {count}')
    except OSError:
        pass


def touch_done(done_file):
    if done_file:
        with contextlib.suppress(OSError):
            open(done_file, 'w').close()


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        sys.exit(0)

    if not isinstance(data, dict) or data.get('stop_hook_active'):
        sys.exit(0)

    event = hook_event(data)
    cwd = data.get('cwd') or '.'
    session_id = data.get('session_id') or 'default'

    if event == 'PreCompact':
        emit_precompact()
        # Suppress the later Stop fallback — this session already got a
        # memory nudge at the natural (compaction) moment.
        touch_done(state_path(cwd, session_id, 'memory-nudge-done'))
        sys.exit(0)

    if event == 'Stop':
        done_file = state_path(cwd, session_id, 'memory-nudge-done')
        if done_file and os.path.exists(done_file):
            sys.exit(0)

        start_file = state_path(cwd, session_id, 'memory-nudge-start')
        if start_file is None:
            sys.exit(0)

        now = time.time()
        started, count = read_start(start_file)
        if started is None:
            # First Stop of the session — record it and wait; too early to
            # judge what's worth saving.
            write_start(start_file, now, 1)
            sys.exit(0)

        count += 1
        write_start(start_file, started, count)

        if now - started >= SESSION_THRESHOLD or count >= STOP_COUNT_THRESHOLD:
            emit_stop()
            touch_done(done_file)

    sys.exit(0)


if __name__ == '__main__':
    main()
