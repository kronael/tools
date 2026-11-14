#!/usr/bin/env python3
import contextlib
import json
import os
import sys
import time

from lib.state import hook_event
from lib.state import session_state

SESSION_THRESHOLD = 1800
PROMPT_COUNT_THRESHOLD = 4

NUDGE_TEXT = (
    "Session memory check: invoke /learn's memory pass first, before the work "
    'this turn asks for, to review the recorded session transcript. Follow its '
    'evidence check and save only qualifying durable memory. This nudge does '
    'not invoke the skill or lint pass. Report what qualified, or that '
    'nothing qualified, then do the work the user asked for. ALWAYS end the '
    'turn on the answer to the user, NEVER on the memory report.'
)


def emit(event):
    print(
        json.dumps(
            {
                'hookSpecificOutput': {
                    'hookEventName': event,
                    'additionalContext': NUDGE_TEXT,
                },
            }
        )
    )


def read_start(path):
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

    if not isinstance(data, dict):
        sys.exit(0)

    event = hook_event(data)
    session_id = data.get('session_id') or 'default'

    if event == 'SessionStart' and data.get('source') == 'compact':
        emit('SessionStart')
        touch_done(session_state('memory-nudge-done', session_id))
        sys.exit(0)

    if event == 'UserPromptSubmit':
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

        if now - started >= SESSION_THRESHOLD or count >= PROMPT_COUNT_THRESHOLD:
            emit(event)
            touch_done(done_file)

    sys.exit(0)


if __name__ == '__main__':
    main()
