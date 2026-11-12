#!/usr/bin/env python3
import argparse
import ast
import subprocess
import sys
from collections import Counter
from collections.abc import Iterable
from collections.abc import Iterator

FUNCTION = (ast.FunctionDef, ast.AsyncFunctionDef)
SIMPLE_STATEMENT = (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Expr)
CHECKS = ('raises', 'warns', 'parametrize')
DISABLERS = (
    'pytest.skip',
    'pytest.xfail',
    'pytest.importorskip',
    'pytest.mark.skip',
    'pytest.mark.skipif',
    'pytest.mark.xfail',
    'unittest.skip',
    'unittest.skipIf',
    'unittest.skipUnless',
    'unittest.expectedFailure',
    'unittest.SkipTest',
    'self.skipTest',
)
DISABLED = 'disabled by '


def run_git(*args: str) -> bytes:
    return subprocess.run(['git', *args], stdout=subprocess.PIPE, check=True).stdout


def is_collected(path: str) -> bool:
    name = path.rpartition('/')[2]
    return name.endswith('.py') and (name.startswith('test_') or name.endswith('_test.py'))


def is_test_path(path: str) -> bool:
    parts = path.split('/')
    return path.endswith('.py') and (
        is_collected(path) or parts[-1] == 'conftest.py' or 'tests' in parts or 'test' in parts
    )


def is_test_function(name: str) -> bool:
    return name.rpartition('.')[2].startswith('test')


def is_check_call(call: ast.Call) -> bool:
    func = call.func
    if isinstance(func, ast.Attribute):
        name = func.attr
    elif isinstance(func, ast.Name):
        name = func.id
    else:
        return False
    return name in CHECKS or name.startswith('assert')


def iter_checks(roots: Iterable[ast.AST]) -> Iterator[str]:
    for root in roots:
        calls = {id(node.func): node for node in ast.walk(root) if isinstance(node, ast.Call)}
        for node in ast.walk(root):
            if isinstance(node, ast.Attribute) and ast.unparse(node) in DISABLERS:
                yield f'{DISABLED}{ast.unparse(calls.get(id(node), node))}'
            elif isinstance(node, ast.Assert):
                yield f'assert {ast.unparse(node.test)}'
            elif isinstance(node, ast.Call) and is_check_call(node):
                yield ast.unparse(node)


def scope_checks(scope: ast.Module | ast.ClassDef) -> list[str]:
    decorators = scope.decorator_list if isinstance(scope, ast.ClassDef) else []
    statements = [node for node in scope.body if isinstance(node, SIMPLE_STATEMENT)]
    return list(iter_checks(decorators + statements))


def iter_functions(
    node: ast.AST, prefix: str, inherited: list[str]
) -> Iterator[tuple[str, Counter[str]]]:
    for child in ast.iter_child_nodes(node):
        if isinstance(child, FUNCTION):
            yield f'{prefix}{child.name}', Counter(inherited + list(iter_checks([child])))
        elif isinstance(child, ast.ClassDef):
            checks = inherited + scope_checks(child)
            yield from iter_functions(child, f'{prefix}{child.name}.', checks)
        else:
            yield from iter_functions(child, prefix, inherited)


def read_checks(rev: str, path: str) -> dict[str, Counter[str]]:
    tree = ast.parse(run_git('show', f'{rev}:{path}'), filename=f'{rev}:{path}')
    seen: Counter[str] = Counter()
    checks: dict[str, Counter[str]] = {}
    for name, found in iter_functions(tree, '', scope_checks(tree)):
        seen[name] += 1
        checks[name if seen[name] == 1 else f'{name}#{seen[name]}'] = found
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(
        description='List the Python test functions that lost or changed a check in a range '
        '(assert, raises/warns, assert* calls, parametrize) or gained a skip or xfail.'
    )
    parser.add_argument('base')
    parser.add_argument('head')
    args = parser.parse_args()
    base = run_git('merge-base', args.base, args.head).decode().strip()

    old: dict[tuple[str, str], Counter[str]] = {}
    new: dict[tuple[str, str], Counter[str]] = {}
    changes = run_git('diff', '--name-status', '-M', '-z', base, args.head).decode()
    fields = iter(changes.split('\0'))
    for status in fields:
        if not status:
            break
        old_path = next(fields)
        new_path = next(fields) if status[0] == 'R' else old_path
        is_kept = is_test_path(new_path) and (is_collected(new_path) or not is_collected(old_path))
        if status[0] != 'A' and is_test_path(old_path):
            path = new_path if is_kept else old_path
            for name, checks in read_checks(base, old_path).items():
                old[path, name] = checks
        if status[0] != 'D' and is_kept:
            for name, checks in read_checks(args.head, new_path).items():
                new[new_path, name] = checks

    findings = 0
    claimed: set[tuple[str, str]] = set()
    for (path, name), before in old.items():
        target = (path, name)
        if target not in new:
            moved = [
                key
                for key in new
                if key[1] == name
                and key not in old
                and key not in claimed
                and (is_collected(key[0]) or not is_test_function(name))
            ]
            if len(moved) == 1:
                target = moved[0]
                claimed.add(target)
        is_removed = target not in new
        after = Counter[str]() if is_removed else new[target]
        lost = [line for line in (before - after).elements() if not line.startswith(DISABLED)]
        gained = list((after - before).elements())
        is_disabled = any(line.startswith(DISABLED) for line in gained)
        if not (lost or is_disabled or (is_removed and is_test_function(name))):
            continue
        findings += 1
        suffix = ': removed' if is_removed else ''
        print(f'{target[0]}::{name}{suffix}')
        for line in lost:
            print(f'  - {line}')
        for line in gained:
            print(f'  + {line}')
    print(
        f'{findings} of {len(old)} functions in the changed tests '
        'lost a check, gained a skip or were removed'
    )
    return 1 if findings else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as err:
        print(f'Failed: {type(err).__name__}: {err}', file=sys.stderr)
        sys.exit(2)
