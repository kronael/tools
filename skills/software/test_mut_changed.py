import os
import subprocess
import sys

import pytest

GIT_ENV = {
    'GIT_CONFIG_GLOBAL': os.devnull,
    'GIT_CONFIG_SYSTEM': os.devnull,
    'GIT_AUTHOR_NAME': 'tester',
    'GIT_AUTHOR_EMAIL': 'tester@example.com',
    'GIT_COMMITTER_NAME': 'tester',
    'GIT_COMMITTER_EMAIL': 'tester@example.com',
}

PROJECT = """\
[project]
name = "fixture"
version = "0"
requires-python = ">=3.11"

[dependency-groups]
dev = ["pytest"]
"""

SECTION = """
[tool.mutmut]
only_mutate = [
    "nothing.py",
]
pytest_add_cli_args = ["-k", "weak"]

[tool.ruff]
line-length = 100
"""

FEES = """\
def fee(amount):
    if amount < 0:
        return 0
    return amount * 2
"""

TESTS = """\
from fees import fee


def test_weak():
    assert fee(10) > 0


def test_strong():
    assert fee(10) == 30
"""


@pytest.fixture
def project(tmp_path, monkeypatch, request):
    for name, value in GIT_ENV.items():
        monkeypatch.setenv(name, value)
    (tmp_path / 'pyproject.toml').write_text(PROJECT + request.param)
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src' / 'fees.py').write_text(FEES)
    (tmp_path / 'tests').mkdir()
    (tmp_path / 'tests' / 'test_fees.py').write_text(TESTS)
    (tmp_path / '.gitignore').write_text('.venv/\n')
    subprocess.run(['uv', 'sync', '-q'], cwd=tmp_path, check=True)
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    files = ['.gitignore', 'pyproject.toml', 'uv.lock', 'src', 'tests']
    subprocess.run(['git', 'add', '--', *files], cwd=tmp_path, check=True)
    subprocess.run(['git', 'commit', '-q', '-m', 'base'], cwd=tmp_path, check=True)
    return tmp_path


def site_packages(project):
    return sorted(
        str(p.relative_to(project)) for p in (project / '.venv').glob('lib/*/site-packages/*')
    )


def run_mut_changed(pytestconfig, project, base='HEAD', *extra):
    script = pytestconfig.rootpath / 'skills' / 'software' / 'mut_changed.py'
    return subprocess.run(
        [sys.executable, str(script), base, str(project), '--max-children', '2', *extra],
        capture_output=True,
        text=True,
        check=False,
    )


def change_fee(project):
    path = project / 'src' / 'fees.py'
    path.write_text(path.read_text().replace('amount * 2', 'amount * 3'))


def git_status(project):
    return subprocess.run(
        ['git', 'status', '--porcelain'], cwd=project, capture_output=True, text=True, check=True
    ).stdout


@pytest.mark.parametrize('project', [''], indirect=True, ids=['no_section'])
def test_without_the_section_killed_changed_lines_pass_and_the_project_is_untouched(
    pytestconfig, project
):
    # Both tests run, so every mutant of the changed line 4 dies; the ones on
    # the untouched lines 2-3 survive and are not counted.
    change_fee(project)
    pyproject = (project / 'pyproject.toml').read_bytes()
    lock = (project / 'uv.lock').read_bytes()
    packages = site_packages(project)
    result = run_mut_changed(pytestconfig, project)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '0 survivors on changed lines of 1 files' in result.stdout
    assert '3 survivors on unchanged lines not counted' in result.stdout
    assert (project / 'pyproject.toml').read_bytes() == pyproject
    assert (project / 'uv.lock').read_bytes() == lock
    assert site_packages(project) == packages
    assert not any('mutmut' in p for p in packages)
    assert git_status(project) == ' M src/fees.py\n'


@pytest.mark.parametrize('project', [SECTION], indirect=True, ids=['section'])
def test_the_section_keeps_its_test_arguments_and_a_survivor_fails_the_gate(pytestconfig, project):
    # The section's `-k weak` leaves `fee(10) > 0` alone, so `amount / 3` and
    # `amount * 4` survive on line 4; its stale only_mutate is replaced.
    change_fee(project)
    pyproject = (project / 'pyproject.toml').read_bytes()
    mtime = (project / 'pyproject.toml').stat().st_mtime_ns
    result = run_mut_changed(pytestconfig, project)
    assert result.returncode == 1, result.stdout + result.stderr
    assert 'src/fees.py:4: fees.x_fee__mutmut_' in result.stdout
    assert '+    return amount / 3' in result.stdout
    assert 'src/fees.py:2' not in result.stdout
    assert 'src/fees.py:3' not in result.stdout
    assert '2 survivors on changed lines of 1 files' in result.stdout
    assert (project / 'pyproject.toml').read_bytes() == pyproject
    assert (project / 'pyproject.toml').stat().st_mtime_ns == mtime
    assert git_status(project) == ' M src/fees.py\n'


@pytest.mark.parametrize('project', [''], indirect=True, ids=['no_section'])
def test_a_change_to_tests_only_reports_an_empty_scope(pytestconfig, project):
    path = project / 'tests' / 'test_fees.py'
    path.write_text(path.read_text() + '\n\ndef test_zero():\n    assert fee(0) == 0\n')
    result = run_mut_changed(pytestconfig, project)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.startswith('scope empty: no changed source file under src since HEAD')


@pytest.mark.parametrize('project', [''], indirect=True, ids=['no_section'])
def test_an_unknown_base_fails_the_check(pytestconfig, project):
    result = run_mut_changed(pytestconfig, project, base='no-such-revision')
    assert result.returncode == 2
    assert result.stderr.startswith('Failed: CheckError: git rev-parse')


def add_rates(project):
    (project / 'src' / 'rates.py').write_text('def rate(x):\n    return x + 1\n')
    (project / 'tests' / 'test_rates.py').write_text(
        'from rates import rate\n\n\ndef test_weak():\n    assert rate(1) > 0\n'
    )


def survivor_lines(stdout):
    return sorted(
        line for line in stdout.splitlines() if ': fees.x_fee__' in line or ': rates.' in line
    )


@pytest.mark.parametrize('project', [SECTION], indirect=True, ids=['section'])
def test_batches_of_one_file_report_the_survivors_of_one_run(pytestconfig, project):
    change_fee(project)
    add_rates(project)
    whole = run_mut_changed(pytestconfig, project, 'HEAD', '--batch', '8')
    split = run_mut_changed(pytestconfig, project, 'HEAD', '--batch', '1')
    assert whole.returncode == split.returncode == 1, split.stdout + split.stderr
    assert whole.stdout.count('mutating ') == 1
    assert split.stdout.count('mutating ') == 2
    assert survivor_lines(split.stdout) == survivor_lines(whole.stdout)
    assert 'src/rates.py:' in split.stdout
    summary = [line for line in split.stdout.splitlines() if 'survivors on changed lines' in line]
    assert summary == [line for line in whole.stdout.splitlines() if 'survivors on changed' in line]
    assert 'of 2 files' in summary[0]


@pytest.mark.parametrize('project', [''], indirect=True, ids=['no_section'])
def test_a_file_the_running_interpreter_cannot_parse_fails_before_mutating(pytestconfig, project):
    # The script parses with its own interpreter; a project file written for a
    # newer one fails the same way, so a broken file stands in for it.
    (project / 'src' / 'newer.py').write_text('def f(:\n    pass\n')
    pyproject = (project / 'pyproject.toml').read_bytes()
    result = run_mut_changed(pytestconfig, project)
    assert result.returncode == 2
    assert 'src/newer.py:1:' in result.stderr
    assert 'cannot parse it, run it with the project interpreter' in result.stderr
    assert 'mutating' not in result.stdout
    assert (project / 'pyproject.toml').read_bytes() == pyproject
    assert not (project / 'mutants').exists()


@pytest.mark.parametrize('project', [''], indirect=True, ids=['no_section'])
def test_a_missing_import_path_fails_with_the_import_error_and_the_hint(pytestconfig, project):
    path = project / 'src' / 'fees.py'
    path.write_text('import no_such_dependency\n\n' + path.read_text().replace('* 2', '* 3'))
    pyproject = (project / 'pyproject.toml').read_bytes()
    result = run_mut_changed(pytestconfig, project)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "ModuleNotFoundError: No module named 'no_such_dependency'" in result.stderr
    assert 'set the PYTHONPATH the project needs' in result.stderr
    assert (project / 'pyproject.toml').read_bytes() == pyproject
