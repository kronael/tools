#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from runpy import run_path

from lib.state import hook_event

RENDERER = Path(__file__).resolve().parent.parent / 'skills' / 'caveman' / 'reminder.py'
MODULE = run_path(str(RENDERER))


def read_reminder(home: Path, portable: bool = True) -> str | None:
    rendered = MODULE['render_reminder'](home, portable)
    return rendered['text'] if rendered else None


def output_for(event: str, reminder: str) -> dict | None:
    if event in {'UserPromptSubmit', 'PostToolUse', 'SessionStart'}:
        return {
            'hookSpecificOutput': {
                'hookEventName': event,
                'additionalContext': reminder,
            }
        }
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            return
        home = Path(os.environ.get('HOME', '')).expanduser()
        reminder = read_reminder(home)
        if not reminder:
            return
        output = output_for(hook_event(data), reminder)
        if output:
            print(json.dumps(output))
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return


if __name__ == '__main__':
    main()
