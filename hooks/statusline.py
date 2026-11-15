#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from datetime import timezone


EFFORT = {'low': 'l', 'medium': 'm', 'high': 'h', 'xhigh': 'x', 'max': 'M'}


def model(data):
    """'Opus 5.5' at high effort prints as 'O5.5h': family initial, version, effort letter."""
    name = (data.get('model') or {}).get('display_name') or ''
    family, _, version = name.partition(' ')
    return family[:1] + version + EFFORT.get((data.get('effort') or {}).get('level'), '')


def window(limits, key, label, when):
    pct = (limits.get(key) or {}).get('used_percentage')
    if pct is None:
        return None
    text = f'{label}{int(pct)}%'
    resets = limits[key].get('resets_at')
    if resets:
        text += datetime.fromtimestamp(resets, tz=timezone.utc).astimezone().strftime(when)
    return text


def render(data):
    parts = [model(data)]
    ctx = (data.get('context_window') or {}).get('used_percentage')
    if ctx is not None:
        parts.append(f'c{int(ctx)}%')
    limits = data.get('rate_limits') or {}
    for key, label, when in ('five_hour', '5h', ' → %H:%M'), ('seven_day', 'w', ' → %a %-d. %H:%M'):
        text = window(limits, key, label, when)
        if text:
            parts.append(text)
    return ' · '.join(p for p in parts if p)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}
    print(render(data if isinstance(data, dict) else {}))


if __name__ == '__main__':
    main()
