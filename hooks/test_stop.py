import json
import os
import re
import subprocess
import sys
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytest
from stop import emit
from stop import project_slug

HOOK = Path(__file__).with_name('stop.py')
ENV = {
    k: v
    for k, v in os.environ.items()
    if k not in ('KRONAEL_HOOK_EVENT', 'KRONAEL_IN_CODEX', 'CLAUDE_EVAL', 'SHIP_ROLE')
}
ENV.update(
    GIT_CONFIG_GLOBAL='/dev/null',
    GIT_AUTHOR_NAME='t',
    GIT_AUTHOR_EMAIL='t@t',
    GIT_COMMITTER_NAME='t',
    GIT_COMMITTER_EMAIL='t@t',
)


@pytest.fixture(autouse=True)
def home(tmp_path_factory, monkeypatch) -> Path:
    """HOME for the hook and for the tests, so ~/.claude never reaches the real one."""
    path = tmp_path_factory.mktemp('home')
    monkeypatch.setitem(ENV, 'HOME', str(path))
    return path


def diary_path(home, tree):
    """~/.claude/projects/<slug of the main tree>/diary/YYYYMMDD.md."""
    slug = re.sub(r'[^A-Za-z0-9]', '-', str(Path(tree).resolve()))
    day = datetime.now(tz=UTC).strftime('%Y%m%d')
    return home / '.claude' / 'projects' / slug / 'diary' / f'{day}.md'


def write_today_diary(home, tree):
    path = diary_path(home, tree)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('# today\n')
    return path


def listed_main(tree):
    """First entry of `git worktree list`: the tree the diary is keyed on.

    Git lists the git dir, not the checkout, for a submodule or a
    --separate-git-dir repo.
    """
    r = subprocess.run(
        ['git', 'worktree', 'list', '--porcelain'],
        cwd=tree,
        env=ENV,
        check=True,
        capture_output=True,
        text=True,
    )
    return r.stdout.split('\n', 1)[0].removeprefix('worktree ')


def git(repo, *args):
    subprocess.run(['git', *args], cwd=repo, env=ENV, check=True, capture_output=True)


def commit(repo, name, text, subject, age_hours=0):
    (repo / name).write_text(text)
    git(repo, 'add', name)
    when = (datetime.now(tz=UTC) - timedelta(hours=age_hours)).isoformat()
    env = {**ENV, 'GIT_AUTHOR_DATE': when, 'GIT_COMMITTER_DATE': when}
    subprocess.run(
        ['git', 'commit', '-q', '-m', subject], cwd=repo, env=env, check=True, capture_output=True
    )


def make_repo(tmp_path, home):
    git(tmp_path, 'init', '-q')
    commit(tmp_path, 'a.txt', 'one\n', 'feat: first', age_hours=2)
    write_today_diary(home, tmp_path)
    return tmp_path


def run_hook(repo, env=None, **payload):
    payload = {'cwd': str(repo), 'hook_event_name': 'Stop', 'session_id': 's1', **payload}
    r = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=repo,
        env={**ENV, **(env or {})},
        check=False,
    )
    assert r.returncode == 0, r.stderr
    assert r.stderr == ''
    return json.loads(r.stdout) if r.stdout else None


def test_project_slug_replaces_every_non_alphanumeric() -> None:
    assert project_slug('/home/u/app/x') == '-home-u-app-x'
    assert project_slug('/home/u/my.app_2/.linked') == '-home-u-my-app-2--linked'
    assert project_slug('/home/U/App.x_1') == '-home-U-App-x-1'


def test_emit_keeps_stop_block(capsys) -> None:
    emit(['commit first'], {'hook_event': 'Stop'})

    output = json.loads(capsys.readouterr().out)
    assert output == {'decision': 'block', 'reason': 'commit first'}


def test_emit_post_tool_nudge_is_context(capsys) -> None:
    emit(['commit soon'], {'hook_event_name': 'PostToolUse'})

    output = json.loads(capsys.readouterr().out)
    assert 'decision' not in output
    assert output == {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': 'commit soon',
        },
    }


def test_emit_post_tool_env_is_context(capsys, monkeypatch) -> None:
    monkeypatch.setenv('KRONAEL_HOOK_EVENT', 'PostToolUse')
    emit(['commit soon'], {})

    output = json.loads(capsys.readouterr().out)
    assert 'decision' not in output
    assert output['hookSpecificOutput']['hookEventName'] == 'PostToolUse'


def test_dirty_tree_blocks(tmp_path, home) -> None:
    repo = make_repo(tmp_path, home)
    (repo / 'a.txt').write_text('one\ntwo\n')

    out = run_hook(repo)

    assert out['decision'] == 'block'
    assert out['reason'].startswith('Uncommitted changes detected.\na.txt | 1 +')
    assert 'Run /commit.' in out['reason']
    assert 'systemMessage' not in out


def test_broken_git_status_blocks_instead_of_reading_clean(tmp_path, home) -> None:
    repo = make_repo(tmp_path, home)
    (repo / 'a.txt').write_text('one\ntwo\n')
    (repo / '.git' / 'index').write_text('corrupt')

    out = run_hook(repo)

    assert out['decision'] == 'block'
    assert out['reason'].startswith('git status failed')
    assert 'fatal:' in out['reason']
    assert 'systemMessage' not in out


def test_ship_judging_role_is_silent(tmp_path, home) -> None:
    repo = make_repo(tmp_path, home)
    (repo / 'a.txt').write_text('one\ntwo\n')
    diary = diary_path(home, repo)
    stale = (datetime.now(tz=UTC) - timedelta(hours=2)).timestamp()
    os.utime(diary, (stale, stale))

    assert run_hook(repo, env={'SHIP_ROLE': 'planner'}) is None


def test_ship_worker_keeps_nudges(tmp_path, home) -> None:
    repo = make_repo(tmp_path, home)
    (repo / 'a.txt').write_text('one\ntwo\n')

    out = run_hook(repo, env={'SHIP_ROLE': 'worker-w0'})

    assert 'Run /commit.' in out['reason']


def test_outside_a_git_repo_is_silent(tmp_path) -> None:
    assert run_hook(tmp_path) is None


def test_clean_repo_with_a_fresh_diary_is_silent(tmp_path, home) -> None:
    repo = make_repo(tmp_path, home)
    assert run_hook(repo) is None
    assert run_hook(repo, env={'KRONAEL_HOOK_EVENT': 'PostToolUse'}) is None


def test_missing_diary_warns_without_writing_a_file(tmp_path, home) -> None:
    git(tmp_path, 'init', '-q')
    commit(tmp_path, 'a.txt', 'one\n', 'feat: first')

    out = run_hook(tmp_path)

    assert 'Run /diary.' in out['reason']
    assert not diary_path(home, tmp_path).parent.exists()
    assert not (tmp_path / '.diary').exists()


def test_stale_diary_warns_without_touching_the_file(tmp_path, home) -> None:
    repo = make_repo(tmp_path, home)
    diary = diary_path(home, repo)
    stale = (datetime.now(tz=UTC) - timedelta(hours=2)).timestamp()
    os.utime(diary, (stale, stale))
    before = diary.read_text()

    out = run_hook(repo)

    assert 'Diary not updated in over an hour' in out['reason']
    assert diary.read_text() == before


def test_diary_in_the_repo_does_not_count(tmp_path) -> None:
    git(tmp_path, 'init', '-q')
    commit(tmp_path, 'a.txt', 'one\n', 'feat: first')
    (tmp_path / '.diary').mkdir()
    (tmp_path / datetime.now(tz=UTC).strftime('.diary/%Y%m%d.md')).write_text('# today\n')

    out = run_hook(tmp_path)

    assert out['reason'].startswith('No diary entry for today')


def test_main_tree_diary_silences_linked_worktree(tmp_path, home) -> None:
    git(tmp_path, 'init', '-q')
    commit(tmp_path, 'a.txt', 'one\n', 'feat: first')
    linked = tmp_path / '.linked'
    git(tmp_path, 'worktree', 'add', '-q', '--detach', str(linked))
    write_today_diary(home, tmp_path)

    assert run_hook(linked) is None


def test_diary_keyed_on_a_linked_worktree_does_not_count(tmp_path, home) -> None:
    git(tmp_path, 'init', '-q')
    commit(tmp_path, 'a.txt', 'one\n', 'feat: first')
    linked = tmp_path / '.linked'
    git(tmp_path, 'worktree', 'add', '-q', '--detach', str(linked))
    write_today_diary(home, linked)

    out = run_hook(linked)

    assert out['decision'] == 'block'
    assert out['reason'].startswith('No diary entry for today')
    assert 'Run /diary.' in out['reason']


def make_submodule(tmp_path):
    origin = tmp_path / 'origin'
    origin.mkdir()
    git(origin, 'init', '-q')
    commit(origin, 'a.txt', 'one\n', 'feat: first')
    super_repo = tmp_path / 'super'
    super_repo.mkdir()
    git(super_repo, 'init', '-q')
    git(
        super_repo, '-c', 'protocol.file.allow=always', 'submodule', 'add', '-q', str(origin), 'sub'
    )
    return super_repo / 'sub'


def test_diary_in_submodule_is_keyed_on_the_listed_main_tree(tmp_path, home) -> None:
    sub = make_submodule(tmp_path)
    write_today_diary(home, listed_main(sub))

    assert run_hook(sub) is None


def test_diary_in_separate_git_dir_repo_is_keyed_on_the_listed_main_tree(tmp_path, home) -> None:
    work = tmp_path / 'work'
    work.mkdir()
    git(tmp_path, 'init', '-q', '--separate-git-dir', str(tmp_path / 'gitdir'), str(work))
    commit(work, 'a.txt', 'one\n', 'feat: first')
    write_today_diary(home, listed_main(work))

    assert run_hook(work) is None


def test_diary_in_submodule_main_tree_silences_its_linked_worktree(tmp_path, home) -> None:
    sub = make_submodule(tmp_path)
    linked = tmp_path / '.linked'
    git(sub, 'worktree', 'add', '-q', '--detach', str(linked))
    write_today_diary(home, listed_main(sub))

    assert run_hook(linked) is None
