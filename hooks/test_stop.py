import json
import os
import subprocess
import sys
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from pathlib import Path

from stop import build_recap
from stop import dirty_lines
from stop import emit
from stop import git_run
from stop import safe_recap

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


def stamp_path(repo):
    return repo / '.git' / 'claude-recap-s1'


def backdate_stamp(repo, hours=1):
    when = datetime.now(tz=UTC) - timedelta(hours=hours)
    stamp_path(repo).write_text(when.isoformat(timespec='seconds'))
    return when.strftime('%H:%M')


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


def test_dirty_tree_still_blocks_and_holds_the_recap(tmp_path) -> None:
    repo = make_repo(tmp_path)
    (repo / 'a.txt').write_text('one\ntwo\n')

    out = run_hook(repo)

    assert out['decision'] == 'block'
    assert out['reason'].startswith('Uncommitted changes detected.\na.txt | 1 +')
    assert 'Run /commit.' in out['reason']
    assert 'systemMessage' not in out
    assert not stamp_path(repo).exists()


def test_broken_git_status_blocks_instead_of_reading_clean(tmp_path) -> None:
    repo = make_repo(tmp_path)
    (repo / 'a.txt').write_text('one\ntwo\n')
    (repo / '.git' / 'index').write_text('corrupt')

    out = run_hook(repo)

    assert out['decision'] == 'block'
    assert out['reason'].startswith('git status failed')
    assert 'fatal:' in out['reason']
    assert 'systemMessage' not in out
    assert not stamp_path(repo).exists()


def test_first_stop_recaps_head_and_dirty_tree(tmp_path) -> None:
    repo = make_repo(tmp_path)
    (repo / 'a.txt').write_text('one\ntwo\n')

    out = run_hook(repo, stop_hook_active=True)

    assert 'decision' not in out
    lines = out['systemMessage'].splitlines()
    assert lines[0].startswith('head ')
    assert lines[0].endswith(' feat: first')
    assert lines[1:] == ['uncommitted: 1 changed (+1 -0)', '  a.txt']
    assert datetime.fromisoformat(stamp_path(repo).read_text()) <= datetime.now(tz=UTC)


def test_first_stop_never_calls_an_untracked_tree_clean(tmp_path) -> None:
    repo = make_repo(tmp_path)
    (repo / 'new.txt').write_text('x\n')

    out = run_hook(repo)

    lines = out['systemMessage'].splitlines()
    assert lines[0].startswith('head ')
    assert lines[1:] == ['no tracked changes']


def test_next_stop_lists_commits_and_new_files_since_last_stop(tmp_path) -> None:
    repo = make_repo(tmp_path)
    hhmm = backdate_stamp(repo)
    commit(repo, 'b.txt', 'two\n', 'fix: second')
    (repo / 'new.txt').write_text('x\n')

    out = run_hook(repo, stop_hook_active=True)

    lines = out['systemMessage'].splitlines()
    assert lines[0] == f'since {hhmm}Z: 1 commit'
    assert lines[1].startswith('+ ')
    assert lines[1].endswith(' fix: second')
    assert lines[2:] == ['uncommitted: 1 untracked', '  new.txt']


def test_old_untracked_files_are_not_this_turns_work(tmp_path) -> None:
    repo = make_repo(tmp_path)
    (repo / 'old.txt').write_text('x\n')
    old = datetime.now(tz=UTC).timestamp() - 7200
    os.utime(repo / 'old.txt', (old, old))
    hhmm = backdate_stamp(repo)

    out = run_hook(repo)

    assert 'decision' not in out
    assert out['systemMessage'].splitlines() == [
        f'since {hhmm}Z: no commits',
        'nothing uncommitted',
    ]


def test_quoted_paths_reach_the_recap(tmp_path) -> None:
    repo = make_repo(tmp_path)
    hhmm = backdate_stamp(repo)
    for name in 'plain.md', 'résumé.md', 'two words.md':
        (repo / name).write_text('x\n')

    out = run_hook(repo)

    assert out['systemMessage'].splitlines() == [
        f'since {hhmm}Z: no commits',
        'uncommitted: 3 untracked',
        '  plain.md résumé.md two words.md',
    ]


def test_a_rename_counts_once(tmp_path) -> None:
    repo = make_repo(tmp_path)
    git(repo, 'mv', 'a.txt', 'b.txt')

    text = build_recap(repo, 's1', datetime.now(tz=UTC))

    assert text.splitlines()[1:] == ['uncommitted: 1 changed (+0 -0)', '  b.txt']


def test_commit_list_is_capped(tmp_path) -> None:
    repo = make_repo(tmp_path)
    backdate_stamp(repo)
    for i in range(8):
        commit(repo, f'f{i}.txt', 'x\n', f'chore: n{i}')

    text = build_recap(repo, 's1', datetime.now(tz=UTC))

    lines = text.splitlines()
    assert lines[0].endswith(': 8 commits, newest 6')
    assert [ln for ln in lines if ln.startswith('+ ')] == lines[1:7]
    assert lines[1].endswith('chore: n7')


def test_stuck_merge_is_reported(tmp_path) -> None:
    repo = make_repo(tmp_path)
    (repo / '.git' / 'MERGE_HEAD').write_text('0' * 40)

    text = build_recap(repo, 's1', datetime.now(tz=UTC))

    assert text.splitlines()[-1] == 'merge in progress'


def test_conflicts_and_path_cap(tmp_path) -> None:
    for name in 'a', 'b', 'c', 'd', 'e':
        (tmp_path / name).write_text('x\n')
    status = 'UU a\0 M b\0A  c\0?? d\0?? e\0'

    lines = dirty_lines(str(tmp_path), status, '1\t0\tb\n-\t-\tc\n', 0)

    assert lines == ['uncommitted: 2 changed, 1 conflicted, 2 untracked (+1 -0)', '  a b c d …']


def test_no_recap_outside_git(tmp_path) -> None:
    assert run_hook(tmp_path) is None
    assert build_recap(tmp_path, 's1', datetime.now(tz=UTC)) == ''


def test_recap_never_raises(tmp_path) -> None:
    repo = make_repo(tmp_path)

    def boom(cwd, *args, timeout):  # noqa: ARG001
        raise RuntimeError('git exploded')

    try:
        build_recap(repo, 's1', datetime.now(tz=UTC), run=boom)
    except RuntimeError:
        pass
    else:
        raise AssertionError('build_recap must surface the failure to safe_recap')
    assert safe_recap(repo, 's1', datetime.now(tz=UTC), run=boom) == ''
    assert not stamp_path(repo).exists()


def test_spent_budget_drops_the_recap(tmp_path) -> None:
    repo = make_repo(tmp_path)
    assert build_recap(repo, 's1', datetime.now(tz=UTC), budget=0) == ''
    assert not stamp_path(repo).exists()


def test_failed_git_call_drops_the_whole_recap(tmp_path) -> None:
    repo = make_repo(tmp_path)
    (repo / 'a.txt').write_text('one\ntwo\n')
    (repo / '.git' / 'index').write_text('corrupt')

    assert run_hook(repo, stop_hook_active=True) is None
    assert not stamp_path(repo).exists()


def test_spent_budget_and_failed_git_call_agree(tmp_path) -> None:
    repo = make_repo(tmp_path)
    (repo / '.git' / 'MERGE_HEAD').write_text('0' * 40)

    def fails(cwd, *args, timeout):  # noqa: ARG001
        return subprocess.CompletedProcess(args, 128, '', 'fatal: broken')

    assert build_recap(repo, 's1', datetime.now(tz=UTC), budget=0) == ''
    assert build_recap(repo, 's1', datetime.now(tz=UTC), run=fails) == ''
    assert not stamp_path(repo).exists()


def test_git_dir_probe_shares_the_budget_and_the_injected_run(tmp_path) -> None:
    repo = make_repo(tmp_path)
    calls = []

    def record(cwd, *args, timeout):
        calls.append(args)
        return git_run(cwd, *args, timeout=timeout)

    assert build_recap(repo, 's1', datetime.now(tz=UTC), run=record, budget=0) == ''
    assert calls == []
    assert build_recap(repo, 's1', datetime.now(tz=UTC), run=record)
    assert calls[0] == ('git', 'rev-parse', '--git-dir')


def test_periodic_and_codex_calls_never_recap(tmp_path) -> None:
    repo = make_repo(tmp_path)
    assert run_hook(repo, env={'KRONAEL_HOOK_EVENT': 'PostToolUse'}) is None
    assert run_hook(repo, env={'KRONAEL_IN_CODEX': '1'}) is None
    assert not stamp_path(repo).exists()


def test_missing_diary_warns_without_writing_a_file(tmp_path) -> None:
    # The hook reports a missing entry and leaves .diary alone; ARCHITECTURE.md
    # and README.md both document that it never writes a header.
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
