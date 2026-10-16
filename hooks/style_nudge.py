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


def output_for(event: str, rendered: dict, data: dict) -> dict | None:
    if event == 'Stop':
        feedback = MODULE['render_feedback'](rendered, data)
        if not feedback:
            return None
        return {
            'hookSpecificOutput': {
                'hookEventName': event,
                'additionalContext': feedback,
            }
        }
    if event in {'UserPromptSubmit', 'PostToolUse', 'SessionStart'}:
        return {
            'hookSpecificOutput': {
                'hookEventName': event,
                'additionalContext': rendered['text'],
            }
        }
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            return
        home = Path(os.environ.get('HOME', '')).expanduser()
        rendered = MODULE['render_reminder'](home)
        if not rendered:
            return
        output = output_for(hook_event(data), rendered, data)
        if output:
            print(json.dumps(output))
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return


if __name__ == '__main__':
    main()
