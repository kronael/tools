#!/usr/bin/env python3
"""Stop: once per session, point at `learn` so the session's corrections and
decisions get saved before the context is lost.

Fires on the first Stop after SESSION_THRESHOLD seconds of session time or
STOP_COUNT_THRESHOLD Stops, whichever comes first; one- or two-turn sessions
never reach either. State lives in kvs under the session; without kvs the hook
is silent.
"""

import json
import sys
import time

from lib import kvs
from lib.reminder import context
from lib.reminder import emit
from lib.reminder import reminder
from lib.state import hook_event

SESSION_THRESHOLD = 1800
STOP_COUNT_THRESHOLD = 3


def due(data, now):
    session = data.get('session_id')
    cwd = data.get('cwd')
    stops = kvs.incr('memory:stops', session, cwd)
    if stops is None:
        return False
    if stops == 1:
        kvs.set('memory:started', int(now), session, cwd)
        return False
    started = float(kvs.get('memory:started', session, cwd) or now)
    if stops < STOP_COUNT_THRESHOLD and now - started < SESSION_THRESHOLD:
        return False
    return kvs.set('memory:done', 1, session, cwd, if_old='')


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        return
    if not isinstance(data, dict) or data.get('stop_hook_active'):
        return
    if hook_event(data) != 'Stop':
        return
    if due(data, time.time()):
        emit(
            context(
                'Stop',
                reminder(
                    'learn',
                    text='session memory check: save corrections, decisions and durable facts',
                ),
            )
        )


if __name__ == '__main__':
    main()
