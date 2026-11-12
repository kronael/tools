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
SUMMARY = 'functions in the changed tests lost a check, gained a skip or were removed'

OLD_TOTALS = """\
import pytest


def test_total():
    assert total([1, 2]) == 3
    with pytest.raises(ValueError, match='empty'):
        total([])


@pytest.mark.parametrize('xs', [[0.5, 0.5], [0.25, 0.75]])
def test_rounding(xs):
    assert total(xs) == 1


def test_gone():
    assert total([1]) == 1
"""

WEAKENED_TOTALS = """\
import pytest


def test_total():
    assert total([1, 2])
    with pytest.raises(Exception):
        total([])


@pytest.mark.parametrize('xs', [[0.5, 0.5]])
def test_rounding(xs):
    assert total(xs) == 1
"""

REFORMATTED_TOTALS = """\
import pytest


def test_total():
    assert total([1, 2]) == 3
    with pytest.raises( ValueError, match="empty" ):
        total([])
    assert total([2]) == 2


@pytest.mark.parametrize('xs', [[0.5, 0.5], [0.25, 0.75]])
def test_rounding(xs):
    assert total(xs) == 1
"""

MOVED_TEST = """\
def test_gone():
    assert total([1]) == 1
"""

SAME_NAME_TEST = """\
def test_total():
    assert product([2, 3]) == 6
"""

OLD_MARKS = """\
import pytest


class TestSums:
    def test_pair(self):
        assert total([1, 2]) == 3


@pytest.mark.skip
def test_enabled():
    assert total([1]) == 1


def test_inline():
    assert total([2]) == 2


@pytest.mark.skipif(False, reason='slow')
def test_conditional():
    assert total([5]) == 5


if hasattr(sum, '__call__'):
    def test_guarded():
        assert total([3]) == 3


if not total:
    def test_guarded():
        assert False
"""

NEW_MARKS = """\
import pytest


@pytest.mark.skip(reason='later')
class TestSums:
    def test_pair(self):
        assert total([1, 2]) == 3


def test_enabled():
    reader.skip(1)
    assert total([1]) == 1


def test_inline():
    pytest.skip('later')
    assert total([2]) == 2


@pytest.mark.skipif(True, reason='slow')
def test_conditional():
    assert total([5]) == 5


if hasattr(sum, '__call__'):
    def test_guarded():
        assert total([3])


if not total:
    def test_guarded():
        assert False
"""

OLD_MODULE = """\
def test_whole():
    assert total([4]) == 4
"""

NEW_MODULE = """\
import pytest

pytestmark = pytest.mark.xfail


def test_whole():
    assert total([4]) == 4
"""

NEW_TYPED_MODULE = """\
import pytest

pytestmark: object = pytest.mark.skip


def test_whole():
    assert total([4]) == 4
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
    # A loosened assert, a widened raises, a dropped parametrize case and a
    # deleted test -> exit 1, each named.
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
        "  - pytest.mark.parametrize('xs', [[0.5, 0.5], [0.25, 0.75]])",
        "  + pytest.mark.parametrize('xs', [[0.5, 0.5]])",
        'tests/test_totals.py::test_gone: removed',
        '  - assert total([1]) == 1',
        f'3 of 3 {SUMMARY}',
    ]


def test_a_skip_added_at_any_level_is_listed_and_a_removed_one_is_not(pytestconfig, repo):
    # A skip lands on a class, inside a body, in a skipif condition and as a
    # plain and an annotated module pytestmark; a test under a module-level `if`
    # loosens its assert while a same-named twin stays; another test loses its
    # skip and calls an unrelated `skip` method -> exit 1 naming the five
    # disabled tests and the loosened one, never the test that was enabled.
    old = {
        'tests/test_marks.py': OLD_MARKS,
        'tests/test_module.py': OLD_MODULE,
        'tests/test_typed.py': OLD_MODULE,
    }
    new = {
        'tests/test_marks.py': NEW_MARKS,
        'tests/test_module.py': NEW_MODULE,
        'tests/test_typed.py': NEW_TYPED_MODULE,
    }
    result = run_assertions(pytestconfig, repo, commit(repo, old), commit(repo, new))
    assert result.returncode == 1, result.stderr
    assert result.stdout.splitlines() == [
        'tests/test_marks.py::TestSums.test_pair',
        "  + disabled by pytest.mark.skip(reason='later')",
        'tests/test_marks.py::test_inline',
        "  + disabled by pytest.skip('later')",
        'tests/test_marks.py::test_conditional',
        "  + disabled by pytest.mark.skipif(True, reason='slow')",
        'tests/test_marks.py::test_guarded',
        '  - assert total([3]) == 3',
        '  + assert total([3])',
        'tests/test_module.py::test_whole',
        '  + disabled by pytest.mark.xfail',
        'tests/test_typed.py::test_whole',
        '  + disabled by pytest.mark.skip',
        f'6 of 7 {SUMMARY}',
    ]


def test_reformat_rename_move_and_an_added_check_are_clean(pytestconfig, repo):
    # The file is renamed and reformatted, one test moves to a new file, one
    # assert is added and another new file reuses a test name -> exit 0: paired
    # by the rename, then by the name.
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
    assert result.stdout == f'0 of 3 {SUMMARY}\n'


def test_two_removed_tests_do_not_share_one_new_test(pytestconfig, repo):
    # Two files each lose a test of one name and one new file gains it -> exit 1:
    # the new test pairs with one, the other is removed.
    base = commit(repo, {'tests/test_a.py': MOVED_TEST, 'tests/test_b.py': MOVED_TEST})
    head = commit(
        repo,
        {
            'tests/test_a.py': 'VALUE = 1\n',
            'tests/test_b.py': 'VALUE = 2\n',
            'tests/test_c.py': MOVED_TEST,
        },
    )
    result = run_assertions(pytestconfig, repo, base, head)
    assert result.returncode == 1, result.stderr
    assert result.stdout.splitlines() == [
        'tests/test_b.py::test_gone: removed',
        '  - assert total([1]) == 1',
        f'1 of 2 {SUMMARY}',
    ]


@pytest.mark.parametrize('renamed', ['notes/single.txt', 'tests/single.py'])
def test_a_test_file_renamed_out_of_collection_is_removed(pytestconfig, repo, renamed):
    # A test file renamed to a name pytest does not collect, outside the tests
    # or inside them -> exit 1, its test removed.
    base = commit(repo, {'tests/test_single.py': MOVED_TEST})
    head = commit(repo, {'tests/test_single.py': None, renamed: MOVED_TEST})
    result = run_assertions(pytestconfig, repo, base, head)
    assert result.returncode == 1, result.stderr
    assert result.stdout.splitlines() == [
        'tests/test_single.py::test_gone: removed',
        '  - assert total([1]) == 1',
        f'1 of 1 {SUMMARY}',
    ]


def test_a_test_moved_into_an_uncollected_file_is_removed(pytestconfig, repo):
    # A test leaves its file for a helper module pytest does not collect -> exit 1,
    # the test removed: the copy in the helper is no test.
    base = commit(repo, {'tests/test_sums.py': OLD_TOTALS})
    head = commit(repo, {'tests/test_sums.py': REFORMATTED_TOTALS, 'tests/support.py': MOVED_TEST})
    result = run_assertions(pytestconfig, repo, base, head)
    assert result.returncode == 1, result.stderr
    assert result.stdout.splitlines() == [
        'tests/test_sums.py::test_gone: removed',
        '  - assert total([1]) == 1',
        f'1 of 3 {SUMMARY}',
    ]


def test_a_file_outside_the_tests_is_not_read(pytestconfig, repo):
    # A removed assert in production code is not a test check -> exit 0, nothing compared.
    base = commit(repo, {'src/totals.py': MOVED_TEST})
    head = commit(repo, {'src/totals.py': 'def total(xs):\n    return sum(xs)\n'})
    result = run_assertions(pytestconfig, repo, base, head)
    assert result.returncode == 0, result.stderr
    assert result.stdout == f'0 of 0 {SUMMARY}\n'


def test_an_unknown_revision_fails_the_check(pytestconfig, repo):
    # A base that does not resolve -> exit 2, never a clean result.
    head = commit(repo, {'tests/test_totals.py': OLD_TOTALS})
    result = run_assertions(pytestconfig, repo, 'no-such-rev', head)
    assert result.returncode == 2
    assert result.stdout == ''
    assert 'Failed:' in result.stderr
