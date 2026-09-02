"""Shared throttle state and payload reading for nudge hooks.

One definition of where a nudge remembers that it already fired, and one of
which payload key carries the lifecycle event.

Keyed by session_id ONLY. Never by cwd: a session that cd's between repos is
still one session, and a cwd-keyed guard silently resets on every move — which
is how the once-per-session nudges ended up firing once per directory.

KRONAEL_HOOK_STATE overrides the root so tests stay out of the real one.
"""

import os

DEFAULT_DIR = '~/.claude/state'


def state_dir():
    return os.environ.get('KRONAEL_HOOK_STATE') or os.path.expanduser(DEFAULT_DIR)


def session_state(name, session_id):
    """Path of a per-session throttle stamp, or None if the root is unusable."""
    root = state_dir()
    try:
        os.makedirs(root, exist_ok=True)
    except OSError:
        return None
    safe = str(session_id or 'default').replace('/', '_').replace('\\', '_')
    return os.path.join(root, f'{name}-{safe}')


def hook_event(data):
    """Lifecycle event name in a hook payload, or '' if it carries none.

    Claude Code sends hook_event_name; codex_hook.py normalizes to hook_event.
    """
    for key in 'hook_event', 'hook_event_name', 'hookEventName':
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return ''
