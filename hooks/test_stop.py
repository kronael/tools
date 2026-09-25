import json
import os
import subprocess
import sys
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from pathlib import Path

from stop import emit

HOOK = Path(__file__).with_name('stop.py')
ENV = {
    k: v
    for k, v in os.environ.items()
    if k not in ('KRONAEL_HOOK_EVENT', 'KRONAEL_IN_CODEX', 'CLAUDE_EVAL')
}
ENV.update(
    GIT_CONFIG_GLOBAL='/dev/null',
    GIT_AUTHOR_NAME='t',
    GIT_AUTHOR_EMAIL='t@t',
    GIT_COMMITTER_NAME='t',
    GIT_COMMITTER_EMAIL='t@t',
)


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


def make_repo(tmp_path):
    git(tmp_path, 'init', '-q')
    (tmp_path / '.diary').mkdir()
    today = datetime.now(tz=UTC).strftime('.diary/%Y%m%d.md')
    (tmp_path / today).write_text('# today\n')
    git(tmp_path, 'add', today)
    commit(tmp_path, 'a.txt', 'one\n', 'feat: first', age_hours=2)
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


def test_dirty_tree_blocks(tmp_path) -> None:
    repo = make_repo(tmp_path)
    (repo / 'a.txt').write_text('one\ntwo\n')

    out = run_hook(repo)

    assert out['decision'] == 'block'
    assert out['reason'].startswith('Uncommitted changes detected.\na.txt | 1 +')
    assert 'Run /commit.' in out['reason']
    assert 'systemMessage' not in out


def test_broken_git_status_blocks_instead_of_reading_clean(tmp_path) -> None:
    repo = make_repo(tmp_path)
    (repo / 'a.txt').write_text('one\ntwo\n')
    (repo / '.git' / 'index').write_text('corrupt')

    out = run_hook(repo)

    assert out['decision'] == 'block'
    assert out['reason'].startswith('git status failed')
    assert 'fatal:' in out['reason']
    assert 'systemMessage' not in out


def test_clean_repo_with_a_fresh_diary_is_silent(tmp_path) -> None:
    repo = make_repo(tmp_path)
    assert run_hook(repo) is None
    assert run_hook(repo, env={'KRONAEL_HOOK_EVENT': 'PostToolUse'}) is None


def test_missing_diary_warns_without_writing_a_file(tmp_path) -> None:
    git(tmp_path, 'init', '-q')
    (tmp_path / '.diary').mkdir()
    commit(tmp_path, 'a.txt', 'one\n', 'feat: first')

    out = run_hook(tmp_path)

    assert 'Run /diary.' in out['reason']
    assert list((tmp_path / '.diary').iterdir()) == []


def test_stale_diary_warns_without_touching_the_file(tmp_path) -> None:
    repo = make_repo(tmp_path)
    diary = repo / datetime.now(tz=UTC).strftime('.diary/%Y%m%d.md')
    stale = (datetime.now(tz=UTC) - timedelta(hours=2)).timestamp()
    os.utime(diary, (stale, stale))
    before = diary.read_text()

    out = run_hook(repo)

    assert 'Diary not updated in over an hour' in out['reason']
    assert diary.read_text() == before
