#!/usr/bin/env python3
import argparse
import ast
import difflib
import fnmatch
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path

UV = ['uv', 'run', '--no-sync', '--with', 'mutmut>=3.8']
SEPARATOR = 'ǁ'
SURVIVED = ('survived', 'no tests')
SECTION = re.compile(r'^\[\s*tool\s*\.\s*mutmut\s*\]\s*(#.*)?$')
HEADER = re.compile(r'^\[\[?[^,\[\]]+\]\]?\s*(#.*)?$')
HUNK = re.compile(r'^@@ -\S+ \+(\d+)(?:,(\d+))? @@')
PROBE = (
    'import json\n'
    'from mutmut.configuration import config\n'
    'c = config()\n'
    'print(json.dumps([[str(p) for p in c.source_paths], c.do_not_mutate]))\n'
)


class CheckError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class Mutant:
    name: str
    status: str
    path: Path
    lines: list[int]


def run_git(*args: str) -> str:
    result = subprocess.run(['git', *args], capture_output=True, text=True, check=False)
    if result.returncode:
        raise CheckError(f'git {" ".join(args)}: {result.stderr.strip()}')
    return result.stdout


def run_uv(*args: str) -> str:
    command = UV + list(args)
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        detail = result.stderr.strip()[-2000:]
        raise CheckError(f'{" ".join(args[:2])} exited {result.returncode}: {detail}')
    return result.stdout


def run_mutmut(cap: list[str], max_children: int) -> None:
    command = [*cap, 'nice', '-n', '19', *UV, 'mutmut', 'run', '--max-children', str(max_children)]
    result = subprocess.run(command, stdout=sys.stderr, check=False)
    if result.returncode:
        raise CheckError(f'mutmut run exited {result.returncode}')


def is_test_path(path: Path) -> bool:
    name = path.name
    return (
        name.startswith('test_')
        or name.endswith('_test.py')
        or name == 'conftest.py'
        or 'tests' in path.parts
        or 'test' in path.parts
    )


def is_under(path: Path, roots: list[Path]) -> bool:
    return any(path == root or root in path.parents or root == Path() for root in roots)


def read_scope(base: str, source_paths: list[Path], do_not_mutate: list[str]) -> list[Path]:
    changed = run_git('diff', '--name-only', '--relative', base, '--', '.').splitlines()
    untracked = run_git('ls-files', '--others', '--exclude-standard', '--', '.').splitlines()
    paths = sorted({Path(name) for name in changed + untracked})
    return [
        path
        for path in paths
        if path.suffix == '.py'
        and path.is_file()
        and is_under(path, source_paths)
        and not is_test_path(path)
        and not any(fnmatch.fnmatch(str(path), pattern) for pattern in do_not_mutate)
    ]


def read_changed_lines(base: str, path: Path) -> set[int]:
    if not run_git('ls-files', '--', str(path)).strip():
        return set(range(1, len(path.read_text().splitlines()) + 1))
    lines: set[int] = set()
    for line in run_git('diff', '-U0', '--relative', base, '--', str(path)).splitlines():
        hunk = HUNK.match(line)
        if not hunk:
            continue
        start = int(hunk[1])
        count = 1 if hunk[2] is None else int(hunk[2])
        if count:
            lines.update(range(start, start + count))
        else:
            lines.update((start, start + 1))
    return lines


def render_section(section: dict[str, object]) -> str:
    return '[tool.mutmut]\n' + ''.join(f'{k} = {json.dumps(v)}\n' for k, v in section.items())


def without_section(data: dict[str, object]) -> dict[str, object]:
    tool = data.get('tool')
    if not isinstance(tool, dict):
        return data
    rest = {k: v for k, v in data.items() if k != 'tool'}
    others = {k: v for k, v in tool.items() if k != 'mutmut'}
    return rest | {'tool': others} if others else rest


def scope_pyproject(original: str, only_mutate: list[str]) -> str:
    data = tomllib.loads(original)
    tool = data.get('tool', {})
    section = dict(tool.get('mutmut', {})) | {'only_mutate': only_mutate}
    lines = original.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if SECTION.match(line)), len(lines))
    end = next((i for i in range(start + 1, len(lines)) if HEADER.match(lines[i])), len(lines))
    rest = ''.join(lines[:start] + lines[end:])
    if rest and not rest.endswith('\n'):
        rest += '\n'
    scoped = rest + '\n' + render_section(section)
    parsed = tomllib.loads(scoped)
    if parsed['tool']['mutmut'] != section or without_section(parsed) != without_section(data):
        raise CheckError('cannot rewrite [tool.mutmut] in pyproject.toml by line')
    return scoped


def module_of(path: Path) -> str:
    module = '.'.join(path.with_suffix('').parts)
    module = module.removeprefix('src.')
    return module.removesuffix('.__init__')


def index_functions(tree: ast.Module) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    found: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in tree.body:
        body = node.body if isinstance(node, ast.ClassDef) else [node]
        for child in body:
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                found.setdefault(child.name, child)
    return found


def find_source_function(
    tree: ast.Module, mangled: str
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    if SEPARATOR in mangled:
        _, class_name, name = mangled.split(SEPARATOR)
        scopes = [n.body for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name]
    else:
        name = mangled.removeprefix('x_')
        scopes = [tree.body]
    for body in scopes:
        for node in body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == name:
                return node
    return None


def span(lines: list[str], node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    return lines[node.lineno - 1 : node.end_lineno]


def map_mutants(statuses: dict[str, str], scope: list[Path]) -> list[Mutant]:
    mutants: list[Mutant] = []
    for path in scope:
        names = [n for n in statuses if n.rpartition('.')[0] == module_of(path)]
        if not names:
            continue
        mutated_text = (Path('mutants') / path).read_text()
        mutated = mutated_text.splitlines()
        generated = index_functions(ast.parse(mutated_text))
        source_text = path.read_text()
        source = source_text.splitlines()
        source_tree = ast.parse(source_text)
        for name in names:
            key = name.rpartition('.')[2]
            mangled = key.partition('__mutmut_')[0]
            orig = generated.get(mangled + '__mutmut_orig')
            mutant = generated.get(key)
            func = find_source_function(source_tree, mangled)
            if orig is None or mutant is None or func is None:
                raise CheckError(f'cannot find the functions of {name} in {path}')
            before = span(mutated, orig)
            after = span(mutated, mutant)
            before[0] = before[0].replace(mangled + '__mutmut_orig', mangled, 1)
            after[0] = after[0].replace(key, mangled, 1)
            if len(before) != len(span(source, func)):
                raise CheckError(f'{name}: the unmutated copy does not match {path}')
            offsets: set[int] = set()
            matcher = difflib.SequenceMatcher(None, before, after, autojunk=False)
            for tag, i1, i2, _, _ in matcher.get_opcodes():
                if tag == 'equal':
                    continue
                offsets.update(range(i1, i2) if i2 > i1 else (max(i1 - 1, 0), i1))
            lines = sorted(func.lineno + offset for offset in offsets)
            mutants.append(Mutant(name, statuses[name], path, lines))
    return mutants


def read_statuses() -> dict[str, str]:
    statuses: dict[str, str] = {}
    for line in run_uv('mutmut', 'results', '--all', 'true').splitlines():
        name, sep, status = line.strip().rpartition(': ')
        if sep and '__mutmut_' in name:
            statuses[name] = status
    return statuses


def memory_cap(memory: str) -> list[str]:
    cap = ['systemd-run', '--user', '--scope', '--quiet', '-p', f'MemoryMax={memory}']
    if not shutil.which('systemd-run'):
        return []
    probe = subprocess.run([*cap, 'true'], capture_output=True, check=False)
    return [] if probe.returncode else cap


def move_aside(path: Path) -> Path | None:
    if not path.exists():
        return None
    target = Path(tempfile.mkdtemp(prefix='mutants-')) / path.name
    shutil.move(path, target)
    return target


def check(base: str, memory: str, max_children: int) -> int:
    run_git('rev-parse', '--verify', '--quiet', f'{base}^{{commit}}')
    pyproject = Path('pyproject.toml')
    if not pyproject.is_file():
        raise CheckError(f'no pyproject.toml in {Path.cwd()}')
    source_names, do_not_mutate = json.loads(run_uv('python', '-c', PROBE))
    source_paths = [Path(name) for name in source_names]
    scope = read_scope(base, source_paths, do_not_mutate)
    if not scope:
        roots = ', '.join(source_names)
        print(f'scope empty: no changed source file under {roots} since {base}, nothing mutated')
        return 0
    changed = {path: read_changed_lines(base, path) for path in scope}
    original = pyproject.read_bytes()
    stat = pyproject.stat()
    scoped = scope_pyproject(original.decode(), [str(path) for path in scope])
    previous = move_aside(Path('mutants'))
    if previous:
        print(f'moved the previous mutants/ to {previous}')
    cap = memory_cap(memory)
    if not cap:
        print('no systemd user scope: running without a memory cap', file=sys.stderr)
    print('mutating ' + ', '.join(str(path) for path in scope), flush=True)
    try:
        pyproject.write_text(scoped)
        run_mutmut(cap, max_children)
        mutants = map_mutants(read_statuses(), scope)
        hits = [m for m in mutants if set(m.lines) & changed[m.path]]
        unchecked = [m for m in hits if m.status == 'not checked']
        survivors = [m for m in hits if m.status in SURVIVED]
        for mutant in survivors:
            lines = ','.join(str(n) for n in sorted(set(mutant.lines) & changed[mutant.path]))
            print(f'\n{mutant.path}:{lines}: {mutant.name} {mutant.status}')
            print(run_uv('mutmut', 'show', mutant.name).rstrip())
    finally:
        pyproject.write_bytes(original)
        os.utime(pyproject, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        kept = move_aside(Path('mutants'))
    if pyproject.read_bytes() != original:
        raise CheckError('pyproject.toml was not restored')
    elsewhere = sum(m.status in SURVIVED for m in mutants) - len(survivors)
    print(f'\nthis run kept its mutants/ in {kept}')
    print(
        f'{len(survivors)} survivors on changed lines of {len(scope)} files: '
        f'{len(hits)} of {len(mutants)} mutants fall on changed lines, '
        f'{elsewhere} survivors on unchanged lines not counted'
    )
    if unchecked:
        raise CheckError(f'{len(unchecked)} mutants on changed lines were not checked')
    return 1 if survivors else 0


def stop(signum: int, _frame: object) -> None:
    raise CheckError(f'stopped by signal {signum}')


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Mutation-test the lines a change touched; exit 0 clean, 1 survivors, 2 failed.'
    )
    parser.add_argument('base', help='git revision the change is compared against')
    parser.add_argument(
        'dir', nargs='?', default='.', help='component directory with pyproject.toml'
    )
    parser.add_argument('--memory', default='4G', help='MemoryMax of the run scope')
    parser.add_argument('--max-children', type=int, default=4)
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, stop)
    os.chdir(args.dir)
    return check(args.base, args.memory, args.max_children)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (Exception, KeyboardInterrupt) as err:
        print(f'Failed: {type(err).__name__}: {err}', file=sys.stderr)
        sys.exit(2)
