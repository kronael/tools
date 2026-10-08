from __future__ import annotations

import pytest
from gh_text_lint import Kind
from gh_text_lint import command_reason
from gh_text_lint import lint

ROBOT = '\U0001f916'
FOOTER = f'{ROBOT} Generated with [Claude Code](https://claude.com/claude-code)'
GOOD_PR = (
    '**TL;DR:** Deploys the collector on hel1v1 through the `service:` list.\n\n'
    '**One path.** The role renders the unit; the playbook and deploy script go.\n\n'
    f'{ROBOT}\n'
)
GOOD_ISSUE = f'`gh pr edit` fails with 403 on a token without read:org.\n\nRepro: `gh pr edit 1 --body x`.\n\n{ROBOT}\n'
GOOD_COMMENT = f'{ROBOT} \U0001f534 Charges `sold_lamports`, the retained piece.\nFix: use the sale leg here.\n'

LINT_CASES = [
    (Kind.PR, GOOD_PR, None),
    (Kind.ISSUE, GOOD_ISSUE, None),
    (Kind.COMMENT, GOOD_COMMENT, None),
    (Kind.PR, '', 'empty body'),
    (Kind.PR, GOOD_PR.replace(ROBOT + '\n', FOOTER + '\n'), 'banned attribution "generated with"'),
    (Kind.PR, GOOD_PR.replace(ROBOT + '\n', 'Co-Authored-By: X <x@y>\n'), 'banned attribution'),
    (Kind.PR, GOOD_PR.replace(ROBOT + '\n', 'Done.\n'), f'last line must be a bare {ROBOT}'),
    (
        Kind.PR,
        GOOD_PR.replace('**One path.**', f'{ROBOT} **One path.**'),
        'belongs on the last line',
    ),
    (Kind.PR, GOOD_PR.replace('**TL;DR:**', '## Summary\n\n'), 'open with **TL;DR:**'),
    (Kind.PR, GOOD_PR.replace('**One path.**', '## Ansible\n\n**One path.**'), 'header'),
    (Kind.PR, GOOD_PR.replace('**One path.**', '---\n\n**One path.**'), 'horizontal rule'),
    (Kind.PR, GOOD_PR.replace('**One path.**', '| a | b |\n|---|---|\n'), 'table'),
    (Kind.PR, GOOD_PR.replace('**One path.**', '- [ ] run the tests\n'), 'checkbox'),
    (Kind.PR, GOOD_PR.replace('Deploys', 'This PR deploys'), '"this PR"'),
    (Kind.PR, GOOD_PR.replace('Deploys', 'Robust deploys'), 'marketing word "Robust"'),
    (Kind.PR, GOOD_PR.replace('Deploys', 'Robustly deploys'), None),
    (Kind.PR, GOOD_PR.replace('hel1v1', 'commit deadbeef...cafe'), 'write it in full'),
    (Kind.PR, GOOD_PR.replace('hel1v1', '0x12ab…'), 'write it in full'),
    (
        Kind.PR,
        GOOD_PR.replace('**One path.**', '```\n' + 'x\n' * 7 + '```\n\n**One path.**'),
        '7-line code block',
    ),
    (Kind.PR, GOOD_PR.replace('**One path.**', '```\n' + 'x\n' * 6 + '```\n\n**One path.**'), None),
    (Kind.PR, GOOD_PR.replace('**One path.**', 'word ' * 700), 'chars, cap 3000'),
    (Kind.ISSUE, GOOD_ISSUE.replace('Repro', '## Repro'), None),
    (Kind.ISSUE, GOOD_ISSUE.replace(ROBOT + '\n', FOOTER + '\n'), 'banned attribution'),
    (Kind.COMMENT, GOOD_COMMENT.replace(f'{ROBOT} ', ''), f'must start with "{ROBOT} "'),
    (Kind.COMMENT, GOOD_COMMENT + 'Third line.\n', '3 lines, cap 2'),
    (Kind.COMMENT, f'{ROBOT} ' + 'x' * 240, '242 chars, cap 240'),
    (Kind.COMMENT, GOOD_COMMENT + f'\n{FOOTER}', 'banned attribution'),
]


@pytest.mark.parametrize(('kind', 'text', 'expected'), LINT_CASES)
def test_lint(kind: Kind, text: str, expected: str | None) -> None:
    problems = lint(kind, text)
    if expected is None:
        assert problems == []
    else:
        assert any(expected in p.text for p in problems), [p.text for p in problems]


def test_lint_pr_draft_must_be_cut() -> None:
    assert lint(Kind.PR, GOOD_PR, draft=GOOD_PR) != []
    assert lint(Kind.PR, GOOD_PR, draft=GOOD_PR + 'more words\n') == []
    longer = [p for p in lint(Kind.PR, GOOD_PR, draft='short') if 'DISTILL' in p.text]
    assert longer


TITLE_CASES = [
    ('fix(ansible): Deploy news-collector through the standard service list', None),
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
    (tmp_path / 'tmp' / 'pr-body.md').write_text(GOOD_PR, encoding='utf-8')
    (tmp_path / 'tmp' / 'bad.md').write_text(
        GOOD_PR.replace(ROBOT + '\n', FOOTER + '\n'), encoding='utf-8'
    )
    (tmp_path / 'tmp' / 'review.json').write_text(
        '{"commit_id": "abc", "comments": [{"path": "a.py", "line": 1, "body": "'
        + GOOD_COMMENT.replace('\n', '\\n')
        + '"}]}',
        encoding='utf-8',
    )
    return tmp_path


ALLOWED = [
    'gh pr create --title "fix: X" --body-file tmp/pr-body.md',
    'timeout 180 gh pr create --repo o/r --head h --base master --title "fix: X" --body-file tmp/pr-body.md 2>&1 | tail -3',
    'gh api -X PATCH repos/o/r/pulls/176 -f body="$(cat tmp/pr-body.md)" --jq ".body | length"',
    'gh pr edit 5 --add-label bug',
    'gh pr view 176 --json body -q .body',
    'gh api repos/o/r/pulls/176 --jq .body',
    'gh api repos/o/r/pulls/176/reviews --jq ".[] | select(.state==\\"PENDING\\") | .id"',
    'gh api repos/o/r/pulls/176/reviews/1 --method DELETE',
    'gh api repos/o/r/pulls/176/reviews/1/events --method POST --input - <<\'EOF\'\n{"event":"COMMENT","body":""}\nEOF',
    'gh api repos/o/r/pulls/176/reviews --method POST --input tmp/review.json',
    f'gh pr comment 176 --body "{ROBOT} @reviewer Fixed the lease. Please re-review."',
    f'gh api repos/o/r/pulls/comments/123/replies -f body="{ROBOT} Deferred: B55 names it."',
    f'gh issue create --repo o/r --title "T" --body "$(cat <<\'EOF\'\nSymptom first.\n\n{ROBOT}\nEOF\n)"',
    'grep -c "gh pr create" transcript.jsonl',
    'git push origin abc:refs/heads/x',
]

REFUSED = [
    ('gh pr create --title "fix: X" --body-file tmp/bad.md', 'banned attribution'),
    ('gh pr create --title "fix: X" --fill', 'pr body not found'),
    ('gh pr create --title "fix: X" --web', 'pr body not found'),
    (
        'gh pr create --title "fix: X" --body-file tmp/missing.md',
        'cannot read the body file tmp/missing.md',
    ),
    (
        'S=tmp; gh api -X PATCH repos/o/r/pulls/176 -f body="$(cat $S/pr-body.md)"',
        'pass a literal path',
    ),
    ('gh pr create --title "fix: X" --body "## Summary\n\nStuff.\n\n' + ROBOT + '"', 'header'),
    (f'gh pr create --title "{"x" * 80}" --body-file tmp/pr-body.md', 'title 80 chars'),
    ('gh pr edit 5 --body "no robot here"', 'last line must be a bare'),
    ('gh pr comment 176 --body "Looks wrong to me."', f'must start with "{ROBOT} "'),
    ('gh pr comment 176 --body-file tmp/pr-body.md', f'must start with "{ROBOT} "'),
    (
        "gh api repos/o/r/pulls/176/reviews --method POST --input - <<'EOF'\n"
        '{"commit_id": "abc", "comments": [{"path": "a.py", "line": 1, "body": "Overflows at u64::MAX."}]}\nEOF',
        f'must start with "{ROBOT} "',
    ),
    (f'gh issue create --repo o/r --title "T" --body "Symptom.\n\n{FOOTER}"', 'banned attribution'),
    ('cd /x && gh pr comment 1 --body "$(python3 gen.py)"', 'command substitution'),
]


@pytest.mark.parametrize('command', ALLOWED)
def test_command_reason_allows(command: str, tree) -> None:
    assert command_reason(command, str(tree)) is None


@pytest.mark.parametrize(('command', 'expected'), REFUSED)
def test_command_reason_refuses(command: str, expected: str, tree) -> None:
    reason = command_reason(command, str(tree))
    assert reason is not None, command
    assert expected in reason, reason


def test_command_reason_names_the_skill_and_the_lint() -> None:
    reason = command_reason('gh pr create --title t --body "x"', '/')
    assert 'pr-draft' in reason
    assert 'gh_text_lint.py pr' in reason
