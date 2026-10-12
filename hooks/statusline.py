#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from datetime import timezone


def window(limits, key, label):
    pct = (limits.get(key) or {}).get('used_percentage')
    if pct is None:
        return None
    text = f'{label} {int(pct)}%'
    resets = limits[key].get('resets_at')
    if resets:
        text += datetime.fromtimestamp(resets, tz=timezone.utc).astimezone().strftime(' → %a %H:%M')
    return text


def render(data):
    parts = [(data.get('model') or {}).get('display_name') or '']
    ctx = (data.get('context_window') or {}).get('used_percentage')
    if ctx is not None:
        parts.append(f'ctx {int(ctx)}%')
    limits = data.get('rate_limits') or {}
    for key, label in ('five_hour', '5h'), ('seven_day', 'week'):
        text = window(limits, key, label)
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
