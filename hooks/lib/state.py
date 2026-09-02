"""Shared throttle state for nudge hooks.

One definition of where a nudge remembers that it already fired.

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
