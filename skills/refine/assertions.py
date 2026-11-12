#!/usr/bin/env python3
import argparse
import ast
import subprocess
import sys
from collections import Counter
from collections.abc import Iterator


def run_git(*args: str) -> str:
    return subprocess.run(['git', *args], stdout=subprocess.PIPE, text=True, check=True).stdout


def is_test_path(path: str) -> bool:
    parts = path.split('/')
    name = parts[-1]
    return (
        name.startswith('test_')
        or name.endswith('_test.py')
        or name == 'conftest.py'
        or 'tests' in parts
        or 'test' in parts
    )


def is_check_call(call: ast.Call) -> bool:
    func = call.func
    if isinstance(func, ast.Attribute):
        name = func.attr
    elif isinstance(func, ast.Name):
        name = func.id
    else:
        return False
    return name in ('raises', 'warns') or name.startswith('assert')


def iter_checks(function: ast.FunctionDef | ast.AsyncFunctionDef) -> Iterator[str]:
    for decorator in function.decorator_list:
        yield f'@{ast.unparse(decorator)}'
    for node in ast.walk(function):
        if isinstance(node, ast.Assert):
            yield f'assert {ast.unparse(node.test)}'
        elif isinstance(node, ast.Call) and is_check_call(node):
            yield ast.unparse(node)


def iter_functions(
    body: list[ast.stmt], prefix: str = ''
) -> Iterator[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
    for node in body:
        if isinstance(node, ast.ClassDef):
            yield from iter_functions(node.body, f'{prefix}{node.name}.')
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield f'{prefix}{node.name}', node


def read_checks(rev: str, path: str) -> dict[str, Counter[str]]:
    tree = ast.parse(run_git('show', f'{rev}:{path}'), filename=f'{rev}:{path}')
    return {name: Counter(iter_checks(function)) for name, function in iter_functions(tree.body)}


def is_test_function(name: str) -> bool:
    return name.rpartition('.')[2].startswith('test')


def has_disabling_mark(checks: Counter[str]) -> bool:
    return any(line.startswith('@') and ('skip' in line or 'xfail' in line) for line in checks)


def main() -> int:
    parser = argparse.ArgumentParser(
        description='List the checks a range removed from or changed in its Python tests: '
        'assert, raises/warns, assert* calls and decorators, per function.'
    )
    parser.add_argument('base')
    parser.add_argument('head')
    args = parser.parse_args()
    base = run_git('merge-base', args.base, args.head).strip()

    old: dict[tuple[str, str], Counter[str]] = {}
    new: dict[tuple[str, str], Counter[str]] = {}
    fields = iter(run_git('diff', '--name-status', '-M', '-z', base, args.head).split('\0'))
    for status in fields:
        if not status:
            break
        old_path = next(fields)
        new_path = next(fields) if status[0] == 'R' else old_path
        if not (old_path.endswith('.py') and new_path.endswith('.py')):
            continue
        if not (is_test_path(old_path) or is_test_path(new_path)):
            continue
        if status[0] != 'A':
            for name, checks in read_checks(base, old_path).items():
                old[new_path, name] = checks
        if status[0] != 'D':
            for name, checks in read_checks(args.head, new_path).items():
                new[new_path, name] = checks

    findings = 0
    for (path, name), before in old.items():
        target = (path, name)
        moved = [key for key in new if key not in old and key[1] == name]
        if target not in new and len(moved) == 1:
            target = moved[0]
        if target not in new:
            if is_test_function(name) or before:
                findings += 1
                print(f'{path}::{name}: removed')
                for line in before.elements():
                    print(f'  - {line}')
            continue
        after = new[target]
        removed = before - after
        added = after - before
        if not removed and not has_disabling_mark(added):
            continue
        findings += 1
        print(f'{target[0]}::{name}')
        for line in removed.elements():
            print(f'  - {line}')
        for line in added.elements():
            print(f'  + {line}')
    print(f'{findings} of {len(old)} functions in the changed tests lost or changed a check')
    return 1 if findings else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (subprocess.CalledProcessError, SyntaxError) as err:
        print(f'Failed: {err}', file=sys.stderr)
        sys.exit(2)
