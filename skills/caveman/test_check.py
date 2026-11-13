import json
import subprocess
import sys

import pytest

LOAD = {'type': 'tool_use', 'name': 'Skill', 'input': {'skill': 'caveman'}}
HOOK_LINE = {
    'type': 'hook_additional_context',
    'hookEvent': 'UserPromptSubmit',
    'content': [
        'caveman: reply by the caveman skill; load the skill when its rules are not in context.'
    ],
}
COMPACTION = {'type': 'system', 'subtype': 'compact_boundary'}


def prompt(text):
    return {'type': 'user', 'message': {'content': text}}


def assistant(*blocks):
    return {'type': 'assistant', 'message': {'content': list(blocks)}}


def reply(text):
    return assistant({'type': 'text', 'text': text})


def attachment(body):
    return {'type': 'attachment', 'attachment': body}


@pytest.fixture
def check(pytestconfig, tmp_path):
    script = pytestconfig.rootpath / 'skills' / 'caveman' / 'check.py'

    def run(*records):
        transcript = tmp_path / 'session.jsonl'
        transcript.write_text('\n'.join(json.dumps(record) for record in records))
        return subprocess.run(
            [sys.executable, str(script), str(transcript)],
            capture_output=True,
            text=True,
            check=False,
        )

    return run


def test_a_session_that_loads_the_skill_before_its_first_reply_passes(check):
    result = check(prompt('is it up?'), attachment(HOOK_LINE), assistant(LOAD), reply('Yes.'))
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        'window 1: skill loaded yes; replies before the load 0 of 1; '
        'hook line on 1 of 1 prompts; over 20 lines 0 of 1 (median 1, max 1)\n'
    )


def test_a_reply_written_without_the_skill_fails(check):
    result = check(prompt('is it up?'), reply('Yes.'))
    assert result.returncode == 1
    assert 'skill loaded NO; replies before the load 1 of 1' in result.stdout
    assert 'hook line on 0 of 1 prompts' in result.stdout


def test_a_load_after_the_first_reply_counts_the_early_reply(check):
    result = check(
        prompt('is it up?'), reply('Yes.'), prompt('and now?'), assistant(LOAD), reply('Yes.')
    )
    assert result.returncode == 1
    assert 'skill loaded yes; replies before the load 1 of 2' in result.stdout


def test_a_compaction_starts_a_window_that_needs_the_skill_again(check):
    result = check(
        prompt('is it up?'),
        assistant(LOAD),
        reply('Yes.'),
        COMPACTION,
        prompt('and now?'),
        reply('Yes.'),
    )
    assert result.returncode == 1
    assert 'window 1: skill loaded yes' in result.stdout
    assert 'window 2: skill loaded NO' in result.stdout


def test_a_skill_the_harness_attaches_again_after_a_compaction_counts_as_loaded(check):
    carried = attachment({'type': 'invoked_skills', 'skills': [{'name': 'caveman'}]})
    result = check(
        prompt('is it up?'),
        assistant(LOAD),
        reply('Yes.'),
        COMPACTION,
        carried,
        prompt('and now?'),
        reply('Yes.'),
    )
    assert result.returncode == 0, result.stdout
    assert 'window 2: skill loaded yes' in result.stdout


def test_a_typed_skill_command_loads_the_skill(check):
    result = check(prompt('<command-name>/caveman</command-name>'), reply('Loaded.'))
    assert result.returncode == 0, result.stdout


def test_only_the_last_text_of_a_turn_is_the_reply_and_it_wraps_at_80_columns(check):
    ceiling = '\n'.join(['x' * 80] * 20)
    over = ceiling + '\n' + 'x' * 81
    fenced = ceiling + '\n````\n' + 'code\n```\n' * 30 + '````'
    result = check(
        prompt('one'),
        assistant(LOAD),
        reply('working on it ' * 80),
        reply(ceiling),
        prompt('two'),
        reply(over),
        prompt('three'),
        reply(fenced),
    )
    assert result.returncode == 0, result.stdout
    assert 'over 20 lines 1 of 3 (median 20, max 22)' in result.stdout


def test_a_subagent_and_a_tool_result_are_not_the_owner(check):
    tool_result = {'type': 'user', 'message': {'content': [{'type': 'tool_result'}]}}
    sidechain = {**reply('a long subagent report'), 'isSidechain': True}
    result = check(prompt('one'), assistant(LOAD), tool_result, sidechain, reply('Done.'))
    assert 'hook line on 0 of 1 prompts; over 20 lines 0 of 1' in result.stdout


def test_the_check_counts_in_the_unit_and_ceiling_the_skill_states(pytestconfig):
    skill = (pytestconfig.rootpath / 'skills' / 'caveman' / 'SKILL.md').read_text()
    assert 'the rendered 80-column terminal line' in skill
    assert '≤20 lines, hard ceiling' in skill
