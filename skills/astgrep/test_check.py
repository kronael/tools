import os
import shutil
import subprocess
import sys

import pytest


@pytest.fixture
def runner(pytestconfig):
    return pytestconfig.rootpath / 'skills' / 'astgrep' / 'check.py'


def test_scan_uses_bundled_rules_from_another_cwd(runner, tmp_path):
    # An unrelated project config cannot hide the bundled violations.
    source = tmp_path / 'file with spaces.py'
    source.write_text('logger = logging.getLogger(__name__)\n')
    (tmp_path / 'sgconfig.yml').write_text('ruleDirs: []\n')
    result = subprocess.run(
        [sys.executable, str(runner), '--scan', source.name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stderr
    assert 'file with spaces.py:1:1: py-log-name:' in result.stdout
    assert '1 lint findings' in result.stdout


def test_scan_from_installed_skill_without_pyyaml(runner, tmp_path):
    # Sync's skills-only layout suffices; scans need no Python packages.
    installed = tmp_path / 'bundle' / 'skills'
    (installed / 'astgrep').mkdir(parents=True)
    shutil.copyfile(runner, installed / 'astgrep' / 'check.py')
    for rules in runner.parents[1].glob('*/lints/rules.yml'):
        dest = installed / rules.relative_to(runner.parents[1])
        dest.parent.mkdir(parents=True)
        shutil.copyfile(rules, dest)
    source = tmp_path / 'source.py'
    source.write_text('log = logging.getLogger(__name__)\n')
    result = subprocess.run(
        [sys.executable, '-S', str(installed / 'astgrep' / 'check.py'), '--scan', str(source)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == '0 lint findings\n'


@pytest.mark.parametrize('args', [['--scan'], ['--scan', 'missing.py']])
def test_scan_invalid_paths_fail(runner, tmp_path, args):
    # Empty selections and missing files must not become whole-tree or clean scans.
    result = subprocess.run(
        [sys.executable, str(runner), *args],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert result.stderr
    assert not result.stdout


def test_missing_ast_grep_fails(runner, tmp_path):
    # A missing checker is a failed check, not an empty result.
    source = tmp_path / 'source.py'
    source.write_text('value = 1\n')
    result = subprocess.run(
        [sys.executable, str(runner), '--scan', str(source)],
        env={**os.environ, 'PATH': str(tmp_path)},
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert 'ast-grep' in result.stderr


def test_scan_preserves_judgment_exceptions(runner, tmp_path):
    # Valid record properties and boundary decoders need semantic review.
    source = tmp_path / 'source.py'
    source.write_text(
        'class Row:\n'
        '    @property\n'
        '    def size(self):\n'
        '        return self.end - self.start\n'
        'def decode(kind, data):\n'
        '    match kind:\n'
        '        case "row/1":\n'
        '            return Row(**data)\n'
        'DECODERS: dict[str, Callable] = {"row/1": decode}\n',
    )
    result = subprocess.run(
        [sys.executable, str(runner), '--scan', str(source)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
