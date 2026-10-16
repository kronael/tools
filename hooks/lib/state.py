"""The lifecycle event of a hook payload.

Claude Code sends hook_event_name; codex_hook.py normalizes to hook_event.
Session memory lives in kvs (kvs.py), never in files of this directory.
"""


def hook_event(data):
    for key in 'hook_event', 'hook_event_name', 'hookEventName':
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return ''
