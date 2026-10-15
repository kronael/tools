#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

from lib.state import hook_event

STYLE_NAME = 'caveman'
SECTION_RE = re.compile(r'^## Persistence\n(?P<body>.*?)(?=^## |\Z)', re.MULTILINE | re.DOTALL)


def read_reminder(home: Path) -> str | None:
    settings = json.loads((home / '.claude' / 'settings.json').read_text())
    if settings.get('outputStyle') != STYLE_NAME:
        return None
    raw = (home / '.claude' / 'output-styles' / f'{STYLE_NAME}.md').read_text()
    matched = SECTION_RE.search(raw)
    if not matched:
        return None
    body = matched.group('body').strip()
    if not body:
        return None
    return f'<caveman-reminder>\n{body}\n</caveman-reminder>'


def output_for(event: str, reminder: str) -> dict | None:
    if event == 'PreCompact':
        return {'ok': True, 'systemMessage': reminder}
    if event in {'UserPromptSubmit', 'PostToolUse'}:
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
