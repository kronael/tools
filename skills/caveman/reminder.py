from __future__ import annotations

import json
import re
import sys
from pathlib import Path

STYLE_NAME = 'caveman'


def section(raw: str, heading: str) -> str | None:
    matched = re.search(
        rf'^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)',
        raw,
        re.MULTILINE | re.DOTALL,
    )
    if not matched:
        return None
    body = matched.group('body').strip()
    return f'## {heading}\n\n{body}' if body else None


def character_budget(length: str | None) -> int | None:
    if not length:
        return None
    matched = re.search(r'(?P<count>[\d,]+)\s*(?:chars?|characters?)\b', length, re.IGNORECASE)
    return int(matched.group('count').replace(',', '')) if matched else None


def render_reminder(home: Path, portable: bool = True) -> dict[str, str | int | None] | None:
    claude = home / '.claude'
    settings = json.loads((claude / 'settings.json').read_text())
    selected = settings.get('outputStyle')
    if portable and selected != STYLE_NAME:
        return None

    styles = claude / 'output-styles'
    raw = (styles / f'{STYLE_NAME}.md').read_text()
    parts = [section(raw, 'Budget — chat only'), section(raw, 'Shape — chat only')]
    if any(part is None for part in parts):
        return None

    length = None
    if isinstance(selected, str) and selected not in {'', 'default', STYLE_NAME}:
        length = section((styles / f'{selected}.md').read_text(), 'Length')
        if length:
            parts.append(length)

    text = (
        '<caveman-reminder>\n'
        + '\n\n'.join(part for part in parts if part)
        + '\n</caveman-reminder>'
    )
    return {
        'text': text,
        'selectedStyle': selected if isinstance(selected, str) else None,
        'characterBudget': character_budget(length),
    }


def main() -> None:
    portable = '--always' not in sys.argv[1:]
    as_json = '--json' in sys.argv[1:]
    args = [arg for arg in sys.argv[1:] if arg not in {'--always', '--json'}]
    home = Path(args[0]) if args else Path.home()
    try:
        rendered = render_reminder(home, portable)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):  # fmt: skip
        return
    if not rendered:
        return
    sys.stdout.write(json.dumps(rendered) if as_json else str(rendered['text']))
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
