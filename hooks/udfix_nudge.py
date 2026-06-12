#!/usr/bin/env python3
"""PostToolUse hook: auto-fix Unicode box-drawing junctions after Write/Edit."""

import json
import shutil
import subprocess
import sys

BOX_CHARS = set('─│┌┐└┘├┤┬┴┼')


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        sys.exit(0)

    if not isinstance(data, dict):
        sys.exit(0)

    tool = data.get('tool_name', '')
    if tool not in ('Write', 'Edit'):
        sys.exit(0)

    path = (data.get('tool_input') or {}).get('file_path', '')
    if not path:
        sys.exit(0)

    udfix = shutil.which('udfix')
    if not udfix:
        sys.exit(0)

    try:
        with open(path) as f:
            original = f.read()
    except OSError:
        sys.exit(0)

    if not any(ch in original for ch in BOX_CHARS):
        sys.exit(0)

    r = subprocess.run([udfix], check=False, input=original, capture_output=True, text=True)
    if r.returncode != 0 or r.stdout == original:
        sys.exit(0)

    try:
        with open(path, 'w') as f:
            f.write(r.stdout)
    except OSError:
        sys.exit(0)

    print(
        json.dumps(
            {
                'ok': True,
                'systemMessage': f'udfix: fixed box-drawing junctions in {path}',
            }
        )
    )


if __name__ == '__main__':
    main()
