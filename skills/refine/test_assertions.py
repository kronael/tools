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

OLD_TOTALS = """\
import pytest


def test_total():
    assert total([1, 2]) == 3
    with pytest.raises(ValueError, match='empty'):
        total([])


def test_rounding():
    assert total([0.5, 0.5]) == 1


def test_gone():
    assert total([1]) == 1
"""

WEAKENED_TOTALS = """\
import pytest


def test_total():
    assert total([1, 2])
    with pytest.raises(Exception):
        total([])


@pytest.mark.skip
def test_rounding():
    assert total([0.5, 0.5]) == 1
"""

REFORMATTED_TOTALS = """\
import pytest


def test_total():
    assert total([1, 2]) == 3
    with pytest.raises( ValueError, match="empty" ):
        total([])
    assert total([2]) == 2


def test_rounding():
    assert total([0.5, 0.5]) == 1
"""

MOVED_TEST = """\
def test_gone():
    assert total([1]) == 1
"""

SAME_NAME_TEST = """\
def test_total():
    assert product([2, 3]) == 6
"""


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for name, value in GIT_ENV.items():
        monkeypatch.setenv(name, value)
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    return tmp_path


def commit(repo, files):
    for name, text in files.items():
        path = repo / name
        if text is None:
            path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    subprocess.run(['git', 'add', '--', *files], cwd=repo, check=True)
    subprocess.run(['git', 'commit', '-q', '-m', 'change'], cwd=repo, check=True)
    head = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], cwd=repo, capture_output=True, text=True, check=True
    )
    return head.stdout.strip()


def run_assertions(pytestconfig, repo, base, head):
    script = pytestconfig.rootpath / 'skills' / 'refine' / 'assertions.py'
    return subprocess.run(
        [sys.executable, str(script), base, head],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def test_weakened_checks_and_a_removed_test_are_listed(pytestconfig, repo):
    # A loosened assert, a widened raises, an added skip and a deleted test -> exit 1, each named.
    base = commit(repo, {'tests/test_totals.py': OLD_TOTALS})
    head = commit(repo, {'tests/test_totals.py': WEAKENED_TOTALS})
    result = run_assertions(pytestconfig, repo, base, head)
    assert result.returncode == 1, result.stderr
    assert result.stdout.splitlines() == [
        'tests/test_totals.py::test_total',
        '  - assert total([1, 2]) == 3',
        "  - pytest.raises(ValueError, match='empty')",
        '  + assert total([1, 2])',
        '  + pytest.raises(Exception)',
        'tests/test_totals.py::test_rounding',
        '  + @pytest.mark.skip',
        'tests/test_totals.py::test_gone: removed',
        '  - assert total([1]) == 1',
        '3 of 3 functions in the changed tests lost or changed a check',
    ]


def test_reformat_rename_move_and_an_added_check_are_clean(pytestconfig, repo):
    # The file is renamed and reformatted, one test moves to a new file, one assert is added and
    # another new file reuses a test name -> exit 0: paired by the rename, then by the name.
    base = commit(repo, {'tests/test_totals.py': OLD_TOTALS})
    head = commit(
        repo,
        {
            'tests/test_totals.py': None,
            'tests/test_sums.py': REFORMATTED_TOTALS,
            'tests/test_single.py': MOVED_TEST,
            'tests/test_products.py': SAME_NAME_TEST,
        },
    )
    result = run_assertions(pytestconfig, repo, base, head)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == '0 of 3 functions in the changed tests lost or changed a check\n'


def test_a_file_outside_the_tests_is_not_read(pytestconfig, repo):
    # A removed assert in production code is not a test check -> exit 0, nothing compared.
    base = commit(repo, {'src/totals.py': MOVED_TEST})
    head = commit(repo, {'src/totals.py': 'def total(xs):\n    return sum(xs)\n'})
    result = run_assertions(pytestconfig, repo, base, head)
    assert result.returncode == 0, result.stderr
    assert result.stdout == '0 of 0 functions in the changed tests lost or changed a check\n'


def test_an_unknown_revision_fails_the_check(pytestconfig, repo):
    # A base that does not resolve -> exit 2, never a clean result.
    head = commit(repo, {'tests/test_totals.py': OLD_TOTALS})
    result = run_assertions(pytestconfig, repo, 'no-such-rev', head)
    assert result.returncode == 2
    assert result.stdout == ''
    assert 'Failed:' in result.stderr
