from __future__ import annotations

import time

import gh_text_lint
import pytest
from gh_text_lint import Kind
from gh_text_lint import command_reason
from gh_text_lint import lint

ROBOT = '\U0001f916'
FOOTER = f'{ROBOT} Generated with [Claude Code](https://claude.com/claude-code)'
BULLET = '- One path: the role renders the unit; the playbook and deploy script go.'
CLOSERS = (
    'Contract to confirm: `collector.service` becomes `news-collector.service`.\n\n'
    'Known, deferred: the unit is not restarted on a config change.\n\n'
    '⚠️ Merge #1 first.'
)
GOOD_PR = (
    '**TL;DR:** Deploys the collector on hel1v1 through the `service:` list.\n\n'
    f'{BULLET}\n\n'
    f'{ROBOT}\n'
)
GOOD_ISSUE = f'`gh pr edit` fails with 403 on a token without read:org.\n\nRepro: `gh pr edit 1 --body x`.\n\n{ROBOT}\n'
GOOD_COMMENT = f'{ROBOT} \U0001f534 Charges `sold_lamports`, the retained piece.\nFix: use the sale leg here.\n'

LINT_CASES = [
    (Kind.PR, GOOD_PR, None),
    (Kind.ISSUE, GOOD_ISSUE, None),
    (Kind.COMMENT, GOOD_COMMENT, None),
    (Kind.PR, '', 'empty body'),
    (
        Kind.PR,
        GOOD_PR.replace(ROBOT + '\n', FOOTER + '\n'),
        'banned attribution "generated with [claude"',
    ),
    (Kind.PR, GOOD_PR.replace(ROBOT + '\n', 'Co-Authored-By: X <x@y>\n'), 'banned attribution'),
    (Kind.PR, GOOD_PR.replace(ROBOT + '\n', 'Done.\n'), f'last line must be a bare {ROBOT}'),
    (Kind.PR, GOOD_PR.replace(BULLET, f'{ROBOT} {BULLET}'), 'belongs on the last line'),
    (Kind.PR, GOOD_PR.replace('**TL;DR:**', '## Summary\n\n'), 'open with **TL;DR:**'),
    (Kind.PR, GOOD_PR.replace(BULLET, f'## Ansible\n\n{BULLET}'), 'header'),
    (Kind.PR, GOOD_PR.replace(BULLET, f'---\n\n{BULLET}'), 'horizontal rule'),
    (Kind.PR, GOOD_PR.replace(BULLET, '| a | b |\n|---|---|\n'), 'table'),
    (Kind.PR, GOOD_PR.replace(BULLET, '- [ ] run the tests\n'), 'checkbox'),
    (Kind.PR, GOOD_PR.replace(BULLET, 'The role renders the unit.'), 'paragraph after the lead'),
    (Kind.PR, GOOD_PR.replace(BULLET, '1. Stop the service.'), 'paragraph after the lead'),
    (Kind.PR, GOOD_PR.replace(BULLET, f'{BULLET}\n  The unit file goes too.'), None),
    (Kind.PR, GOOD_PR.replace('the `service:` list.', 'the\n`service:` list.'), None),
    (Kind.PR, GOOD_PR.replace(BULLET, f'{BULLET}\n\n{CLOSERS}'), None),
    (Kind.PR, GOOD_PR.replace(BULLET, f'{BULLET}\n\nCloses #12.'), None),
    (
        Kind.PR,
        GOOD_PR.replace(BULLET, f'{BULLET}\n\n**Known, deferred**: the lease is untested.'),
        None,
    ),
    (Kind.PR, GOOD_PR.replace(BULLET, f'{BULLET}\n\n![order panel](https://x.test/a.png)'), None),
    (
        Kind.PR,
        GOOD_PR.replace(BULLET, f'{BULLET}\n\nKnown, deferred: a.\n\nKnown, deferred: b.'),
        'second `Known, deferred` line',
    ),
    (Kind.PR, GOOD_PR.replace(BULLET, '- ' + 'word ' * 48), '241 chars in one line, max 240'),
    (Kind.PR, GOOD_PR.replace(BULLET, '- ' + 'word ' * 47), None),
    (Kind.PR, GOOD_PR.replace(BULLET, '\n'.join(f'- Choice {k}: reason.' for k in range(5))), None),
    (
        Kind.PR,
        GOOD_PR.replace(BULLET, '\n'.join(f'- Choice {k}: reason.' for k in range(6))),
        '6 bullets, max 5',
    ),
    (Kind.PR, GOOD_PR.replace('Deploys', 'This PR deploys'), '"this PR"'),
    (Kind.PR, GOOD_PR.replace('Deploys', 'Robust deploys'), 'marketing word "Robust"'),
    (Kind.PR, GOOD_PR.replace('Deploys', 'Robustly deploys'), None),
    (
        Kind.PR,
        GOOD_PR.replace('Deploys', 'Leveraging the cache, deploys'),
        'marketing word "Leveraging"',
    ),
    (Kind.PR, GOOD_PR.replace('hel1v1', 'commit deadbeef...cafe'), 'write it in full'),
    (Kind.PR, GOOD_PR.replace('hel1v1', 'vault 7xKXtg...gAsU'), 'write it in full'),
    (Kind.PR, GOOD_PR.replace('hel1v1', '0x12ab…'), 'write it in full'),
    (
        Kind.PR,
        GOOD_PR.replace(BULLET, '```\n' + 'x\n' * 7 + f'```\n\n{BULLET}'),
        'code blocks total 7 lines, max 6',
    ),
    (Kind.PR, GOOD_PR.replace(BULLET, '```\n' + 'x\n' * 6 + f'```\n\n{BULLET}'), None),
    (
        Kind.PR,
        GOOD_PR.replace(
            BULLET, '```\n' + 'x\n' * 4 + '```\n\n```\n' + 'x\n' * 4 + f'```\n\n{BULLET}'
        ),
        'code blocks total 8 lines, max 6',
    ),
    (Kind.PR, '**TL;DR:** x\n\n```\n' + 'y\n' * 7 + ROBOT, 'code blocks total 8 lines'),
    (
        Kind.PR,
        GOOD_PR.replace(BULLET, f'```\n412 passed, 1 skipped\n```\n\n{BULLET}'),
        'test or lint output in a code block',
    ),
    (Kind.PR, GOOD_PR.replace(BULLET, '- ' + 'word ' * 200), 'chars, cap 1000'),
    (Kind.ISSUE, GOOD_ISSUE.replace('Repro', '## Repro'), None),
    (Kind.ISSUE, GOOD_ISSUE.replace('Repro:', '- [x] 3.11\n- [ ] 3.12\n\nRepro:'), None),
    (Kind.ISSUE, GOOD_ISSUE.replace('Repro:', f'The bot wrote "{ROBOT} nit: x".\n\nRepro:'), None),
    (Kind.ISSUE, GOOD_ISSUE.replace(ROBOT + '\n', FOOTER + '\n'), 'banned attribution'),
    (Kind.COMMENT, GOOD_COMMENT.replace(f'{ROBOT} ', ''), f'must start with "{ROBOT} "'),
    (Kind.COMMENT, '\n' + GOOD_COMMENT, None),
    (Kind.COMMENT, f'{ROBOT} Repro on 3.11.\nFails on 3.12 too.\nLog attached.\n', None),
    (Kind.COMMENT, f'{ROBOT} ci.yml is generated with make workflows; edit the template.', None),
    (Kind.COMMENT, f'{ROBOT} Deferred: this PR does not touch the lease.', None),
    (Kind.COMMENT, f'{ROBOT} ' + 'x' * 240, '242 chars, cap 240'),
    (Kind.COMMENT, GOOD_COMMENT + f'\n{FOOTER}', 'banned attribution'),
]


@pytest.mark.parametrize(('kind', 'text', 'expected'), LINT_CASES)
def test_lint(kind: Kind, text: str, expected: str | None) -> None:
    problems = lint(kind, text)
    if expected is None:
        assert problems == [], [p.text for p in problems]
    else:
        assert any(expected in p.text for p in problems), [p.text for p in problems]


def test_lint_pr_draft_must_be_cut() -> None:
    assert lint(Kind.PR, GOOD_PR, draft=GOOD_PR) != []
    assert lint(Kind.PR, GOOD_PR, draft=GOOD_PR + 'more words\n') == []
    longer = [p for p in lint(Kind.PR, GOOD_PR, draft='short') if 'DISTILL' in p.text]
    assert longer


@pytest.mark.xfail(
    reason='GH-LINT-DISTILL-COUNTS-THE-TITLE: the ratio counts the title line the draft carries',
    strict=True,
)
def test_lint_pr_draft_ratio_ignores_the_draft_title() -> None:
    assert lint(Kind.PR, GOOD_PR, draft='fix: X\n\n' + GOOD_PR) != []


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
    (tmp_path / 'sub' / 'tmp').mkdir(parents=True)
    bad = GOOD_PR.replace(ROBOT + '\n', FOOTER + '\n')
    (tmp_path / 'tmp' / 'pr-body.md').write_text(GOOD_PR, encoding='utf-8')
    (tmp_path / 'tmp' / 'pr body.md').write_text(GOOD_PR, encoding='utf-8')
    (tmp_path / 'tmp' / 'bad.md').write_text(bad, encoding='utf-8')
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
    return tmp_path


ALLOWED = [
    'gh pr create --title "fix: X" --body-file tmp/pr-body.md',
    'timeout 180 gh pr create --repo o/r --head h --base master --title "fix: X" --body-file tmp/pr-body.md 2>&1 | tail -3',
    'timeout -k 5 180 gh pr create --title "fix: X" --body-file tmp/pr-body.md',
    'GH_PAGER=cat gh pr create --title "fix: X" --body-file tmp/pr-body.md',
    'env GH_HOST=github.com gh pr create --title t --body-file tmp/pr-body.md',
    '(gh pr create --title t --body-file tmp/pr-body.md)',
    'if gh pr create --title t --body-file tmp/pr-body.md; then echo ok; fi',
    '/usr/bin/gh pr create --title t --body-file tmp/pr-body.md',
    'gh pr create --title t --body-file "tmp/pr body.md"',
    'gh pr create --title "$(cat tmp/title.txt)" --body-file tmp/pr-body.md',
    'gh pr create --title t --body "**TL;DR:** Says \\"done\\".\n\n' + ROBOT + '"',
    'gh api -X PATCH repos/o/r/pulls/176 -f body="$(cat tmp/pr-body.md)" --jq ".body | length"',
    'python3 gen.py --input tmp/review.json; gh pr create --title "fix: X" --body-file tmp/pr-body.md',
    'gh pr edit 5 --add-label bug',
    'gh pr view 176 --json body -q .body',
    'gh api repos/o/r/pulls/176 --jq .body',
    'gh api repos/o/r/pulls/176/reviews --jq ".[] | select(.state==\\"PENDING\\") | .id"',
    'gh api repos/o/r/pulls/176/reviews/1 --method DELETE',
    'gh api repos/o/r/pulls/176/reviews/1/events --method POST --input - <<\'EOF\'\n{"event":"COMMENT","body":""}\nEOF',
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
    f'gh issue create --repo o/r --title "T" --body "$(cat <<\'EOF\'\nSymptom first.\n\n{ROBOT}\nEOF\n)"',
    'gh pr review 176 --approve',
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
    ('gh pr create --title "fix: X" --body "## Summary\n\nStuff.\n\n' + ROBOT + '"', 'header'),
    (f'gh pr create --title "{"x" * 80}" --body-file tmp/pr-body.md', 'title 80 chars'),
    ('gh pr edit 5 --body "no robot here"', 'last line must be a bare'),
    ('gh api -X PATCH repos/o/r/pulls/176 -f body=@tmp/bad.md', 'last line must be a bare'),
    ('cd sub && gh pr create --title t --body-file tmp/pr-body.md', 'banned attribution'),
    (
        'gh pr create --title t --body-file tmp/pr-body.md && gh pr comment 1 --body "no robot here"',
        f'must start with "{ROBOT} "',
    ),
    ('gh pr comment 176 --body "Looks wrong to me."', f'must start with "{ROBOT} "'),
    ('gh pr comment 176 --body-file tmp/pr-body.md', f'must start with "{ROBOT} "'),
    ('gh pr review 176 --comment --body "Looks good, ship it"', f'must start with "{ROBOT} "'),
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
    ('gh api --method PATCH \\\nrepos/o/r/pulls/1 -f body="bad"', 'last line must be a bare'),
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
