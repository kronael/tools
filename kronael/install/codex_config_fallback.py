"""Keep Codex's CLAUDE.md fallback at the top level of config.toml."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
import tomllib
from pathlib import Path

KEY = 'project_doc_fallback_filenames'
FILENAME = 'CLAUDE.md'
TABLE_RE = re.compile(r'^\s*\[([^\]]+)\]\s*(?:#.*)?$')
ASSIGN_RE = re.compile(r"^\s*([A-Za-z0-9_.\"'-]+)\s*=")


def strip_quotes(key: str) -> str:
    return key.strip().strip('"').strip("'")


def table_name(line: str) -> str | None:
    match = TABLE_RE.match(line)
    return match.group(1).strip() if match else None


def assignment_key(line: str) -> str | None:
    match = ASSIGN_RE.match(line)
    return strip_quotes(match.group(1)) if match else None


def assignment_end(lines: list[str], start: int) -> int:
    for end in range(start + 1, len(lines) + 1):
        try:
            tomllib.loads(''.join(lines[start:end]))
        except tomllib.TOMLDecodeError:
            continue
        return end
    raise ValueError(f'invalid TOML assignment starting at line {start + 1}')


def parse_top_level_list(lines: list[str]) -> list[str]:
    parsed = tomllib.loads(''.join(lines))
    value = parsed.get(KEY)
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ValueError(f'{KEY} must be an array of strings')
    return value


def format_fallback(values: list[str]) -> str:
    return f'{KEY} = {json.dumps(values)}\n'


def update_text(text: str) -> tuple[str, bool]:
    lines = text.splitlines(keepends=True)
    section = ''
    first_table = len(lines)
    skip: set[int] = set()
    replacement: tuple[int, int, str] | None = None
    top_level_range: tuple[int, int] | None = None
    changed = False

    i = 0
    while i < len(lines):
        line = lines[i]
        maybe_table = table_name(line)
        if maybe_table is not None:
            if first_table == len(lines):
                first_table = i
            section = maybe_table
            i += 1
            continue

        key = assignment_key(line)
        end = assignment_end(lines, i) if key else i + 1
        assignment = ''.join(lines[i:end])
        misplaced_fallback = key == KEY and section
        bad_tui_value = (
            section in {'tui', 'tui.model_availability_nux'}
            and key is not None
            and FILENAME in assignment
        )
        bad_dotted_tui_value = (
            section == ''
            and key is not None
            and (
                key == 'tui.model_availability_nux' or key.startswith('tui.model_availability_nux.')
            )
            and FILENAME in assignment
        )
        if misplaced_fallback or bad_tui_value or bad_dotted_tui_value:
            skip.update(range(i, end))
            changed = True
            i = end
            continue

        if key == KEY and not section:
            top_level_range = (i, end)
        i = end

    if top_level_range is not None:
        start, end = top_level_range
        values = parse_top_level_list(lines[start:end])
        if FILENAME not in values:
            values.append(FILENAME)
            skip.update(range(start, end))
            replacement = (start, end, format_fallback(values))
            changed = True
    else:
        replacement = (first_table, first_table, format_fallback([FILENAME]))
        changed = True

    kept: list[str] = []
    for idx, line in enumerate(lines):
        if replacement is not None and idx == replacement[0]:
            kept.append(replacement[2])
        if idx not in skip:
            kept.append(line)
    if replacement is not None and replacement[0] == len(lines):
        kept.append(replacement[2])

    updated = ''.join(kept)
    tomllib.loads(updated)
    return updated, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config',
        nargs='?',
        default=str(Path.home() / '.codex' / 'config.toml'),
    )
    args = parser.parse_args()

    path = Path(args.config).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    original = path.read_text() if path.exists() else ''
    try:
        updated, changed = update_text(original)
    except Exception as exc:
        sys.stderr.write(f'failed to update {path}: {exc}\n')
        return 1

    if changed:
        if path.exists():
            backup = path.with_suffix(path.suffix + f'.bak-{int(time.time())}')
            shutil.copy2(path, backup)
            sys.stdout.write(f'backup: {backup}\n')
        path.write_text(updated)
    status = 'updated' if changed else 'ok'
    sys.stdout.write(f'codex config fallback: {status}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
