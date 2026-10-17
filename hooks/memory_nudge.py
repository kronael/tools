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

Once-per-session state lives in ~/.claude/state, keyed by session_id alone
(see lib/state.py), so the Stop nudge stays once per session even when the
session changes directory.

No LLM call. Never blocks. Emits additionalContext (Stop) or systemMessage
(the idiom local.py/reclaude.py use on PreCompact).
"""

import contextlib
import json
import os
import sys
import time

from lib.state import hook_event
from lib.state import session_state

SESSION_THRESHOLD = 1800
STOP_COUNT_THRESHOLD = 3

NUDGE_TEXT = (
    'Session memory check: before this context is lost, evaluate the '
    'conversation for anything worth persisting long-term — user '
    'corrections, confirmed approaches/decisions, durable project facts, '
    'reference pointers. Save qualifying items via the auto-memory '
    'mechanism (frontmatter name/description/metadata.type: '
    'user/feedback/project/reference, indexed in MEMORY.md), or run '
    '/learn for a fuller extraction pass — /learn covers both '
    'session-memory evaluation and skill/pattern extraction. Skip if '
    'nothing qualifies; do not force it.'
)


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
    session_id = data.get('session_id') or 'default'

    if event == 'PreCompact':
        emit_precompact()
        touch_done(session_state('memory-nudge-done', session_id))
        sys.exit(0)

    if event == 'Stop':
        done_file = session_state('memory-nudge-done', session_id)
        if done_file and os.path.exists(done_file):
            sys.exit(0)

        start_file = session_state('memory-nudge-start', session_id)
        if start_file is None:
            sys.exit(0)

        now = time.time()
        started, count = read_start(start_file)
        if started is None:
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
