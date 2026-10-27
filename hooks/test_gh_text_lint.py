from __future__ import annotations

import json
import time

import gh_text_lint
import pytest
from gh_text_lint import SUBMIT_ASK
from gh_text_lint import Kind
from gh_text_lint import command_reason
from gh_text_lint import latest_prompt
from gh_text_lint import lint

ROBOT = '\U0001f916'
FOOTER = f'{ROBOT} Generated with [Claude Code](https://claude.com/claude-code)'
CLOSE = 'Closes #12'
GOOD_PR = (
    f'{ROBOT} **TL;DR:** Deploys the collector on web1 through the `service:` list, so the playbook goes.\n\n'
    f'{CLOSE}\n'
)
PR_PAD_AT_CAP = 400 - len(GOOD_PR.split('\n\n', maxsplit=1)[0]) + len('the playbook goes.')
CONTEXT_PR = (
    f'{ROBOT} **TL;DR:** Add an optional cache dependency for thumbnail jobs.\n\n'
    'Saved jobs contain image identifiers, not live cache clients. Resuming a job '
    'needs the configured cache to locate its source image. The existing dependency '
    'container supplies runtime clients when the worker restores a job.\n\n'
    'The optional field extends that container so callers can supply the cache '
    'through the same path. Jobs without a cache keep their existing behavior. '
    'Worker wiring and changes to image rendering remain separate work.\n\n'
    'Validation covers construction with and without a cache. A restart test '
    'needs the worker wiring and does not run for this field-only change.\n'
)
GOOD_ISSUE = f'{ROBOT} `gh pr edit` fails with 403 on a token without read:org.\n\nRepro: `gh pr edit 1 --body x`.\n'
GOOD_COMMENT = (
    f'{ROBOT} \U0001f534 Charges `sold_qty`, the retained piece.\nFix: use the sale leg here.\n'
)

LINT_CASES = [
    (Kind.PR, GOOD_PR, None),
    (Kind.PR, CONTEXT_PR, None),
    (Kind.PR, CONTEXT_PR.replace('\n\n', '\n \n'), None),
    (Kind.ISSUE, GOOD_ISSUE, None),
    (Kind.COMMENT, GOOD_COMMENT, None),
    (Kind.PR, '', 'empty body'),
    (
        Kind.PR,
        GOOD_PR + FOOTER + '\n',
        'banned attribution "generated with [claude"',
    ),
    (Kind.PR, GOOD_PR + 'Co-Authored-By: X <x@y>\n', 'banned attribution'),
    (Kind.PR, GOOD_PR.replace(f'{ROBOT} ', ''), f'must start with "{ROBOT} "'),
    (Kind.PR, GOOD_PR.replace(f'{ROBOT} ', '') + f'\n{ROBOT}\n', f'must start with "{ROBOT} "'),
    (Kind.PR, GOOD_PR + f'\n{ROBOT}\n', 'belongs at the start only'),
    (Kind.PR, GOOD_PR.replace(CLOSE, f'{ROBOT} {CLOSE}'), 'belongs at the start only'),
    (Kind.PR, GOOD_PR.replace('**TL;DR:**', '## Summary\n\n'), 'open with **TL;DR:**'),
    (Kind.PR, GOOD_PR.replace(CLOSE, f'## Scope\n\n{CLOSE}'), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, f'---\n\n{CLOSE}'), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, '| a | b |\n|---|---|\n'), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, '- [ ] run the tests\n'), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, 'The role renders the unit.'), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, '1. The role renders the unit.'), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, '- One path: the role renders the unit.'), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, '* One path: the role renders the unit.'), None),
    (
        Kind.PR,
        GOOD_PR.replace(CLOSE, 'Known, deferred: the unit is not restarted.'),
        None,
    ),
    (
        Kind.PR,
        GOOD_PR.replace(CLOSE, 'Contract to confirm: the unit is renamed.'),
        None,
    ),
    (Kind.PR, GOOD_PR.replace(CLOSE, '⚠️ Merge #1 first.'), None),
    (
        Kind.PR,
        GOOD_PR.replace(CLOSE, '![order panel](https://x.test/a.png)'),
        None,
    ),
    (Kind.PR, GOOD_PR.replace(CLOSE, '- ![unit](https://example.test/u.png)'), None),
    (
        Kind.PR,
        GOOD_PR.replace('Deploys', 'Deploys ![x](https://example.test/x.png)'),
        None,
    ),
    (Kind.PR, GOOD_PR.replace('Deploys', 'Deploys [the log](https://example.test/x.png)'), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, ''), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, 'Fixes #12\n\nCloses #13'), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, 'Closes #12.'), None),
    (Kind.PR, GOOD_PR.replace('the `service:` list', 'the\n`service:` list'), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, '```\nmake test\n```\n\n' + CLOSE), None),
    (Kind.PR, GOOD_PR.replace(CLOSE, '~~~\nmake test\n~~~\n\n' + CLOSE), None),
    (Kind.PR, GOOD_PR.replace('Deploys', 'This PR deploys'), '"this PR"'),
    (Kind.PR, GOOD_PR.replace('Deploys', 'Robust deploys'), 'marketing word "Robust"'),
    (Kind.PR, GOOD_PR.replace('Deploys', 'Robustly deploys'), None),
    (
        Kind.PR,
        GOOD_PR.replace('Deploys', 'Leveraging the cache, deploys'),
        'marketing word "Leveraging"',
    ),
    (Kind.PR, GOOD_PR.replace('web1', 'commit deadbeef...cafe'), 'write it in full'),
    (Kind.PR, GOOD_PR.replace('web1', 'vault 7xKXtg...gAsU'), 'write it in full'),
    (Kind.PR, GOOD_PR.replace('web1', '0x12ab…'), 'write it in full'),
    (Kind.PR, GOOD_PR.replace('the playbook goes.', 'x' * PR_PAD_AT_CAP + 'x'), 'chars, cap 400'),
    (Kind.PR, GOOD_PR.replace('the playbook goes.', 'x' * PR_PAD_AT_CAP), None),
    (Kind.PR, CONTEXT_PR + f'\n{ROBOT} Context.\n', 'belongs at the start only'),
    (Kind.PR, CONTEXT_PR + '\nCo-Authored-By: X <x@y>\n', 'banned attribution'),
    (Kind.PR, CONTEXT_PR + '\nA robust cache.\n', 'marketing word'),
    (Kind.PR, CONTEXT_PR + '\nSee commit deadbeef...cafe.\n', 'write it in full'),
    (Kind.PR, CONTEXT_PR + '\n```\nCo-Authored-By: X <x@y>\n```\n', 'banned attribution'),
    (Kind.PR, CONTEXT_PR + '\n| robust |\n|---|\n', 'marketing word'),
    (
        Kind.PR,
        CONTEXT_PR + '\n![deadbeef...cafe](https://example.test/a.png)\n',
        'write it in full',
    ),
    (Kind.ISSUE, f'{ROBOT} ' + 'x' * 2998, None),
    (Kind.ISSUE, f'{ROBOT} ' + 'x' * 2999, '3001 chars, cap 3000'),
    (Kind.ISSUE, GOOD_ISSUE.replace('Repro', '## Repro'), None),
    (Kind.ISSUE, GOOD_ISSUE.replace('Repro:', '- [x] 3.11\n- [ ] 3.12\n\nRepro:'), None),
    (
        Kind.ISSUE,
        GOOD_ISSUE.replace('Repro:', f'The bot wrote "{ROBOT} nit: x".\n\nRepro:'),
        'belongs at the start only',
    ),
    (Kind.ISSUE, GOOD_ISSUE + FOOTER + '\n', 'banned attribution'),
    (Kind.COMMENT, GOOD_COMMENT.replace(f'{ROBOT} ', ''), f'must start with "{ROBOT} "'),
    (Kind.COMMENT, '\n' + GOOD_COMMENT, None),
    (Kind.COMMENT, f'{ROBOT} Repro on 3.11.\nFails on 3.12 too.\nLog attached.\n', None),
    (Kind.COMMENT, f'{ROBOT} ci.yml is generated with make workflows; edit the template.', None),
    (Kind.COMMENT, f'{ROBOT} Deferred: this PR does not touch the lease.', None),
    (Kind.COMMENT, f'{ROBOT} ' + 'x' * 240, '242 chars, cap 240'),
    (Kind.COMMENT, GOOD_COMMENT + f'\n{FOOTER}', 'banned attribution'),
    (Kind.COMMENT, GOOD_COMMENT + f'\n{ROBOT}\n', 'belongs at the start only'),
]


@pytest.mark.parametrize(('kind', 'text', 'expected'), LINT_CASES)
def test_lint(kind: Kind, text: str, expected: str | None) -> None:
    problems = lint(kind, text)
    if expected is None:
        assert problems == [], [p.text for p in problems]
    else:
        assert any(expected in p.text for p in problems), [p.text for p in problems]


@pytest.mark.parametrize(
    'markdown',
    [
        'Input | Result\n--- | ---\nmissing | skip\n',
        '    cache = configured_cache\n',
        '> ```\n> cache = configured_cache\n> ```\n',
        '![result][preview]\n\n[preview]: https://example.test/preview.png\n',
        '+ [x] Construction with a cache passes.\n',
        '> ---\n',
    ],
)
def test_supporting_markdown_passes_lint_and_post_gate(markdown, tmp_path):
    body = CONTEXT_PR + '\n' + markdown
    (tmp_path / 'body.md').write_text(body, encoding='utf-8')
    assert lint(Kind.PR, body) == []
    assert command_reason('gh pr create --title t --body-file body.md', str(tmp_path)) is None


@pytest.mark.parametrize('draft', [CONTEXT_PR, 'short', ' \n'])
def test_pr_draft_size_is_informational(draft, tmp_path, monkeypatch, capsys) -> None:
    body_file = tmp_path / 'body.md'
    draft_file = tmp_path / 'draft.md'
    body_file.write_text(CONTEXT_PR, encoding='utf-8')
    draft_file.write_text(draft, encoding='utf-8')
    monkeypatch.setattr(
        'sys.argv', ['gh_text_lint.py', 'pr', str(body_file), '--draft', str(draft_file)]
    )
    assert len(CONTEXT_PR) > 400
    assert gh_text_lint.main() == 0
    output = capsys.readouterr().out
    assert output.startswith('ok: pr ')
    if draft == CONTEXT_PR:
        assert '-> 100%' in output


TITLE_CASES = [
    ('fix(ansible): Deploy price-feed through the standard service list', None),
    ('x' * 73, 'title 73 chars, max 72'),
    ('feat: Add A and B and C', 'title lists changes'),
]


@pytest.mark.parametrize(('title', 'expected'), TITLE_CASES)
def test_lint_title(title: str, expected: str | None) -> None:
    problems = lint(Kind.PR, GOOD_PR, title=title)
    if expected is None:
        assert problems == []
    else:
        assert any(expected in p.text for p in problems)


@pytest.fixture
def tree(tmp_path):
    (tmp_path / 'tmp').mkdir()
    (tmp_path / 'sub' / 'tmp').mkdir(parents=True)
    bad = GOOD_PR + FOOTER + '\n'
    (tmp_path / 'tmp' / 'pr-body.md').write_text(GOOD_PR, encoding='utf-8')
    (tmp_path / 'tmp' / 'context.md').write_text(CONTEXT_PR, encoding='utf-8')
    (tmp_path / 'tmp' / 'pr body.md').write_text(GOOD_PR, encoding='utf-8')
    (tmp_path / 'tmp' / 'bad.md').write_text(bad, encoding='utf-8')
    (tmp_path / 'tmp' / 'end-robot.md').write_text(GOOD_PR + f'\n{ROBOT}\n', encoding='utf-8')
    (tmp_path / 'sub' / 'tmp' / 'pr-body.md').write_text(bad, encoding='utf-8')
    (tmp_path / 'tmp' / 'latin1.md').write_bytes(b'**TL;DR:** caf\xe9 au lait.\n')
    (tmp_path / 'tmp' / 'title.txt').write_text('fix: X\n', encoding='utf-8')
    (tmp_path / 'tmp' / 'review.json').write_text(
        '{"commit_id": "abc", "comments": [{"path": "a.py", "line": 1, "body": "'
        + GOOD_COMMENT.replace('\n', '\\n')
        + '"}]}',
        encoding='utf-8',
    )
    (tmp_path / 'tmp' / 'review-raw.json').write_text(
        '{"comments": [{"body": "' + GOOD_COMMENT + '"}]}', encoding='utf-8'
    )
    (tmp_path / 'tmp' / 'submit.json').write_text(
        '{"commit_id": "abc", "event": "COMMENT", "comments": [{"path": "a.py", "line": 1, "body": "'
        + GOOD_COMMENT.replace('\n', '\\n')
        + '"}]}',
        encoding='utf-8',
    )
    return tmp_path


ALLOWED = [
    'gh pr create --title "fix: X" --body-file tmp/pr-body.md',
    'gh pr create --title "feat: Supply the thumbnail cache" --body-file tmp/context.md',
    'gh pr edit 5 --body-file tmp/context.md',
    'gh api -X PATCH repos/o/r/pulls/5 -F body=@tmp/context.md',
    f'gh pr create --title "fix: X" --body "{ROBOT} **TL;DR:** Stuff.\n\n## Context\n\nMore."',
    f'gh pr create --title "fix: X" --body "{ROBOT} **TL;DR:** Stuff.\n\n- [ ] Test."',
    'timeout 180 gh pr create --repo o/r --head h --base master --title "fix: X" --body-file tmp/pr-body.md 2>&1 | tail -3',
    'timeout -k 5 180 gh pr create --title "fix: X" --body-file tmp/pr-body.md',
    'GH_PAGER=cat gh pr create --title "fix: X" --body-file tmp/pr-body.md',
    'env GH_HOST=github.com gh pr create --title t --body-file tmp/pr-body.md',
    '(gh pr create --title t --body-file tmp/pr-body.md)',
    'if gh pr create --title t --body-file tmp/pr-body.md; then echo ok; fi',
    '/usr/bin/gh pr create --title t --body-file tmp/pr-body.md',
    'gh pr create --title t --body-file "tmp/pr body.md"',
    'gh pr create --title "$(cat tmp/title.txt)" --body-file tmp/pr-body.md',
    f'gh pr create --title t --body "{ROBOT} **TL;DR:** Says \\"done\\"."',
    'gh api -X PATCH repos/o/r/pulls/176 -f body="$(cat tmp/pr-body.md)" --jq ".body | length"',
    'python3 gen.py --input tmp/review.json; gh pr create --title "fix: X" --body-file tmp/pr-body.md',
    'gh pr edit 5 --add-label bug',
    'gh pr view 176 --json body -q .body',
    'gh api repos/o/r/pulls/176 --jq .body',
    'gh api repos/o/r/pulls/176/reviews --jq ".[] | select(.state==\\"PENDING\\") | .id"',
    'gh api repos/o/r/pulls/176/reviews/1 --method DELETE',
    'gh api repos/o/r/pulls/176/reviews --method POST --input tmp/review.json',
    'gh api repos/o/r/pulls/176/comments -F commit_id=abc -f path=a.py -F line=10 -f body="'
    + ROBOT
    + ' \U0001f534 Overflows at u64::MAX."',
    f'gh api repos/o/r/pulls/176/comments -F in_reply_to=123 -f body="{ROBOT} Deferred: B55 names it."',
    'gh api -X PATCH repos/o/r/issues/5 -F milestone=3',
    "gh api graphql -F pr=176 -f query='query($pr:Int!){ repository { pullRequest(number:$pr) { id } } }'",
    f'gh pr comment 176 --body "{ROBOT} @reviewer Fixed the lease. Please re-review."',
    f"gh pr comment 1 --body '{ROBOT} Fix `x` here.'",
    f'gh pr comment 1 --body "{ROBOT} Fix \\`x\\` here."',
    f'gh pr comment 1 --body "{ROBOT} ci.yml is generated with make workflows; edit the template."',
    f'gh pr comment 1 --body "{ROBOT} Deferred: this PR does not touch the lease."',
    f'gh issue comment 5 --body "{ROBOT} Repro on 3.11.\nFails on 3.12 too.\nLog attached."',
    f'gh api repos/o/r/pulls/comments/123/replies -f body="{ROBOT} Deferred: B55 names it."',
    f'gh issue create --repo o/r --title "T" --body "$(cat <<\'EOF\'\n{ROBOT} Symptom first.\nEOF\n)"',
    "cat > docs/x.md <<'EOF'\nRun this:\n\ngh pr create --title t --fill\nEOF",
    'grep -c "gh pr create" transcript.jsonl',
    'git push origin abc:refs/heads/x',
]

REFUSED = [
    ('gh pr create --title "fix: X" --body-file tmp/bad.md', 'banned attribution'),
    ('gh pr create --title "fix: X" --fill', 'pr body not found'),
    ('gh pr create --title "fix: X" --web', 'pr body not found'),
    ('gh pr create --title "fix: X" --body-file tmp/missing.md', 'write it in its own call first'),
    ('gh pr create --title t --body-file tmp/latin1.md', 'cannot read the body file tmp/latin1.md'),
    (
        'S=tmp; gh api -X PATCH repos/o/r/pulls/176 -f body="$(cat $S/pr-body.md)"',
        'pass a literal path',
    ),
    (f'gh pr create --title "{"x" * 80}" --body-file tmp/pr-body.md', 'title 80 chars'),
    ('gh pr edit 5 --body "no robot here"', f'must start with "{ROBOT} "'),
    ('gh api -X PATCH repos/o/r/pulls/176 -F body=@tmp/end-robot.md', 'belongs at the start only'),
    (
        'gh api -X PATCH repos/o/r/pulls/176 -f body=@tmp/end-robot.md',
        f'must start with "{ROBOT} "',
    ),
    ('cd sub && gh pr create --title t --body-file tmp/pr-body.md', 'banned attribution'),
    (
        'gh pr create --title t --body-file tmp/pr-body.md && gh pr comment 1 --body "no robot here"',
        f'must start with "{ROBOT} "',
    ),
    ('gh pr comment 176 --body "Looks wrong to me."', f'must start with "{ROBOT} "'),
    ('gh pr comment 176 --body-file tmp/end-robot.md', 'belongs at the start only'),
    ('gh pr review 176 --comment --body "Looks good, ship it"', 'review submit refused'),
    (
        "gh api repos/o/r/pulls/176/reviews --method POST --input - <<'EOF'\n"
        '{"commit_id": "abc", "comments": [{"path": "a.py", "line": 1, "body": "Overflows at u64::MAX."}]}\nEOF',
        f'must start with "{ROBOT} "',
    ),
    (
        "jq -n '{}' | gh api repos/o/r/pulls/176/reviews --method POST --input -",
        'stdin the hook cannot see',
    ),
    ('printf "%s" "$BODY" | gh pr create --title t --body-file -', 'stdin the hook cannot see'),
    (
        'gh api repos/o/r/pulls/176/reviews --method POST --input tmp/review-raw.json',
        'cannot parse the JSON body',
    ),
    (f'gh issue create --repo o/r --title "T" --body "Symptom.\n\n{FOOTER}"', 'banned attribution'),
    ('cd /x && gh pr comment 1 --body "$(python3 gen.py)"', 'command substitution'),
    (f'gh pr comment 1 --body "{ROBOT} Fix `x` here."', 'command substitution'),
    ('gh api --method PATCH \\\nrepos/o/r/pulls/1 -f body="bad"', f'must start with "{ROBOT} "'),
]


@pytest.mark.parametrize('command', ALLOWED)
def test_command_reason_allows(command: str, tree) -> None:
    assert command_reason(command, str(tree)) is None


@pytest.mark.parametrize(('command', 'expected'), REFUSED)
def test_command_reason_refuses(command: str, expected: str, tree) -> None:
    reason = command_reason(command, str(tree))
    assert reason is not None, command
    assert expected in reason, reason


def human(content: str | list) -> dict:
    return {
        'type': 'user',
        'origin': {'kind': 'human'},
        'message': {'role': 'user', 'content': content},
    }


def transcript(path, *records: dict) -> str:
    path.write_text(
        ''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in records), encoding='utf-8'
    )
    return str(path)


NOT_THE_USER = {
    'hook feedback': {
        'type': 'user',
        'isMeta': True,
        'message': {'role': 'user', 'content': f'Stop hook feedback: {SUBMIT_ASK}'},
    },
    'task notification': {
        'type': 'user',
        'origin': {'kind': 'task-notification', 'producer': 'session-task'},
        'message': {
            'role': 'user',
            'content': f'<task-notification>{SUBMIT_ASK}</task-notification>',
        },
    },
    'subagent thread': {
        'type': 'user',
        'isSidechain': True,
        'message': {'role': 'user', 'content': f'Give a review, then {SUBMIT_ASK}.'},
    },
    'tool result': {
        'type': 'user',
        'message': {
            'role': 'user',
            'content': [{'type': 'tool_result', 'tool_use_id': 'x', 'content': SUBMIT_ASK}],
        },
    },
    'assistant turn': {
        'type': 'assistant',
        'message': {
            'role': 'assistant',
            'content': [{'type': 'text', 'text': f'Say {SUBMIT_ASK} to submit review 1.'}],
        },
    },
}

SUBMITS = [
    'gh pr review 176 --approve',
    f'gh pr review 176 --comment --body "{ROBOT} Looks right."',
    f'gh pr review 176 -r -b "{ROBOT} Overflows at u64::MAX."',
    'gh api repos/o/r/pulls/176/reviews/1/events --method POST --input - <<\'EOF\'\n{"event":"COMMENT","body":""}\nEOF',
    'gh api repos/o/r/pulls/176/reviews/$PENDING/events -f event=COMMENT',
    'gh api repos/o/r/pulls/176/reviews --method POST --input tmp/submit.json',
    'gh api repos/o/r/pulls/176/reviews --method POST --input - <<\'EOF\'\n{"commit_id": "abc", "event": "COMMENT", "comments": []}\nEOF',
    'gh api repos/o/r/pulls/176/reviews -F commit_id=abc -f event=APPROVE',
    "gh api graphql -f query='mutation($id:ID!){submitPullRequestReview(input:{pullRequestReviewId:$id,event:COMMENT}){pullRequestReview{id}}}' -f id=PRR_1",
    'gh api repos/o/r/pulls/176/reviews/1 --method DELETE && gh pr review 176 --approve',
]

PENDING = [
    'gh api repos/o/r/pulls/176/reviews --method POST --input tmp/review.json',
    'gh api repos/o/r/pulls/176/reviews --jq ".[] | select(.state==\\"PENDING\\") | .id"',
    'gh api repos/o/r/pulls/176/reviews/1 --method DELETE',
    'gh api repos/o/r/pulls/176/reviews/1 --jq .state',
    f'gh pr comment 176 --body "{ROBOT} Fix the lease."',
    "gh api graphql -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{id}}}' -f id=T_1",
]


@pytest.mark.parametrize('command', SUBMITS)
def test_submit_needs_the_ask_in_the_users_newest_message(command: str, tree) -> None:
    asked = transcript(
        tree / 'tmp' / 'asked.jsonl', human('post them'), human(f'yes. {SUBMIT_ASK}, then check #7')
    )
    answered = transcript(
        tree / 'tmp' / 'answered.jsonl',
        human(SUBMIT_ASK),
        human('yes. please also verify the lease'),
    )
    assert command_reason(command, str(tree), asked) is None
    for path in answered, None, str(tree / 'tmp' / 'missing.jsonl'):
        reason = command_reason(command, str(tree), path)
        assert reason is not None, (command, path)
        assert 'review submit refused' in reason
        assert SUBMIT_ASK in reason


@pytest.mark.parametrize('record', NOT_THE_USER.values(), ids=NOT_THE_USER.keys())
def test_submit_reads_only_what_the_user_typed(record: dict, tree) -> None:
    """A record that is not the user's words neither grants the ask nor hides
    the user's own ask behind it."""
    command = SUBMITS[0]
    said_no = transcript(tree / 'tmp' / 'no.jsonl', human('no'), record)
    assert command_reason(command, str(tree), said_no) is not None
    said_yes = transcript(tree / 'tmp' / 'yes.jsonl', human(SUBMIT_ASK), record)
    assert command_reason(command, str(tree), said_yes) is None


@pytest.mark.parametrize('command', PENDING)
def test_pending_posts_and_reads_need_no_ask(command: str, tree) -> None:
    answered = transcript(tree / 'tmp' / 'answered.jsonl', human('yes'))
    assert command_reason(command, str(tree), answered) is None


def test_submit_body_is_linted_once_the_ask_is_given(tree) -> None:
    asked = transcript(tree / 'tmp' / 'asked.jsonl', human(SUBMIT_ASK))
    reason = command_reason('gh pr review 176 --comment --body "Looks good"', str(tree), asked)
    assert reason is not None
    assert f'must start with "{ROBOT} "' in reason


def test_latest_prompt_joins_text_blocks_and_takes_the_newest(tree) -> None:
    path = transcript(
        tree / 'tmp' / 'blocks.jsonl',
        human('first'),
        human([{'type': 'text', 'text': 'look'}, {'type': 'image', 'source': {}}]),
    )
    assert latest_prompt(path) == 'look'
    assert latest_prompt(None) == ''
    assert latest_prompt(str(tree / 'tmp' / 'missing.jsonl')) == ''


def test_latest_prompt_skips_a_long_turn_inside_the_hook_budget(tree) -> None:
    """A turn's tool results are skipped by a substring scan, not parsed, so
    megabytes of output after the ask stay far inside the 500 ms budget."""
    result = {
        'type': 'user',
        'message': {
            'role': 'user',
            'content': [{'type': 'tool_result', 'tool_use_id': 'x', 'content': 'x' * 2048}],
        },
    }
    path = transcript(tree / 'tmp' / 'long.jsonl', human(SUBMIT_ASK), *([result] * 4000))
    start = time.perf_counter()
    assert latest_prompt(path) == SUBMIT_ASK
    assert time.perf_counter() - start < 0.5


def test_command_reason_names_the_skill_and_the_lint() -> None:
    reason = command_reason('gh pr create --title t --body "x"', '/')
    assert 'pr-draft' in reason
    assert 'gh_text_lint.py pr' in reason


@pytest.mark.parametrize('step', ['mark_heredocs', 'find_posts', 'read_bodies'])
def test_command_reason_turns_a_gate_failure_into_a_refusal(monkeypatch, step: str) -> None:
    """A lint that raises must refuse the post, never let the hook's suppress allow it."""

    def explode(*_args, **_kwargs):
        raise RuntimeError('boom')

    monkeypatch.setattr(gh_text_lint, step, explode)
    reason = command_reason('gh pr create --title t --body-file tmp/pr-body.md', '/')
    assert reason is not None
    assert 'gate failed' in reason


def test_command_reason_keeps_the_wrapper_prefix_on_one_line() -> None:
    """800 wrapped lines stay inside the hook's 500 ms budget: a wrapper's
    arguments end at the newline instead of being retried across every line."""
    command = '\n'.join(f'sudo systemctl restart svc-{n}' for n in range(800))
    start = time.perf_counter()
    assert command_reason(command, '/') is None
    assert time.perf_counter() - start < 0.5
