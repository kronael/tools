import subprocess
import sys
from pathlib import Path

from skill_frontmatter_lint import Severity
from skill_frontmatter_lint import check_body
from skill_frontmatter_lint import check_leaks
from skill_frontmatter_lint import frontmatter
from skill_frontmatter_lint import name_forms
from skill_frontmatter_lint import parse_meta
from skill_frontmatter_lint import process
from skill_frontmatter_lint import skill_files

VALID = """---
name: demo
description: Do the demo thing. NOT for real work (use other).
when_to_use: demo, example, trigger words
---

# Demo

- ALWAYS do X.
- NEVER do Y.
"""


def make(tmp_path: Path, text: str, name: str = 'demo') -> Path:
    directory = tmp_path / name
    directory.mkdir(exist_ok=True)
    path = directory / 'SKILL.md'
    path.write_text(text)
    return path


def findings(path: Path) -> list:
    text = path.read_text()
    split = frontmatter(text)
    assert split is not None
    meta, body = split
    return check_body(path, text, parse_meta(meta), body)


def rules(items: list, severity: Severity) -> set[str]:
    return {item.rule for item in items if item.severity is severity}


def test_valid_skill_passes(tmp_path: Path) -> None:
    assert findings(make(tmp_path, VALID)) == []
    assert process(make(tmp_path, VALID), write=False) == 0


def test_missing_key_fails(tmp_path: Path) -> None:
    text = VALID.replace('when_to_use: demo, example, trigger words\n', '')
    assert 'skill-keys' in rules(findings(make(tmp_path, text)), Severity.ERROR)


def test_unknown_key_fails(tmp_path: Path) -> None:
    text = VALID.replace('when_to_use:', 'arg: <x>\nwhen_to_use:')
    assert 'skill-keys' in rules(findings(make(tmp_path, text)), Severity.ERROR)


def test_name_must_match_directory(tmp_path: Path) -> None:
    path = make(tmp_path, VALID, name='other')
    assert 'skill-name' in rules(findings(path), Severity.ERROR)
    assert process(path, write=False) == 2


def test_should_in_body_fails(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- You SHOULD do X.\n')
    assert 'skill-should' in rules(findings(path), Severity.ERROR)
    assert process(path, write=False) == 2


def test_over_cap_warns_never_errors(tmp_path: Path) -> None:
    long_body = '\n'.join(f'- line {i}' for i in range(250))
    path = make(tmp_path, VALID + long_body)
    found = findings(path)
    assert 'skill-length' in rules(found, Severity.WARN)
    assert 'skill-length' not in rules(found, Severity.ERROR)


def test_over_listing_cap_warns(tmp_path: Path) -> None:
    text = VALID.replace(
        'when_to_use: demo, example, trigger words\n',
        'when_to_use: ' + ', '.join(f'phrase {i}' for i in range(200)) + '\n',
    )
    found = findings(make(tmp_path, text))
    assert 'skill-budget' in rules(found, Severity.WARN)
    assert 'skill-budget' not in rules(found, Severity.ERROR)


def test_allowlisted_skill_gets_higher_cap(tmp_path: Path) -> None:
    long_body = '\n'.join(f'- line {i}' for i in range(250))
    path = make(tmp_path, VALID + long_body, name='ship')
    assert 'skill-length' not in rules(findings(path), Severity.WARN)


def test_nested_skill_md_warns(tmp_path: Path) -> None:
    top = tmp_path / 'router'
    top.mkdir()
    (top / 'SKILL.md').write_text(VALID)
    nested_dir = top / 'mode'
    nested_dir.mkdir()
    nested = nested_dir / 'SKILL.md'
    nested.write_text(VALID)
    assert 'skill-router' in rules(findings(nested), Severity.WARN)


def test_missing_notfor_warns(tmp_path: Path) -> None:
    text = VALID.replace(' NOT for real work (use other).', '')
    assert 'skill-notfor' in rules(findings(make(tmp_path, text)), Severity.WARN)


def sibling(path: Path, rel: str, text: str = 'data\n') -> Path:
    doc = path.parent / rel
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(text)
    return doc


def test_unnamed_sibling_is_an_orphan(tmp_path: Path) -> None:
    path = make(tmp_path, VALID)
    sibling(path, 'lonely.md')
    assert 'skill-orphan' in rules(findings(path), Severity.ERROR)
    assert process(path, write=False) == 2


def test_named_sibling_is_reachable(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- Read `lonely.md` for the rest.\n')
    sibling(path, 'lonely.md')
    assert findings(path) == []


def test_reachability_chains_through_a_named_sibling(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- Read `index.md`.\n')
    sibling(path, 'index.md', 'See `deep/leaf.md`.\n')
    sibling(path, 'deep/leaf.md')
    assert findings(path) == []


def test_path_style_reference_names_the_basename(tmp_path: Path) -> None:
    """`render.md` writes the path from its own directory, not the skill root.

    So `render/flavors/remotion.md` appears in no text and only the basename
    form, preceded by a `/`, reaches the file.
    """
    path = make(tmp_path, VALID + '\n- Read `render.md`.\n')
    sibling(path, 'render.md', 'Read `flavors/remotion.md`.\n')
    sibling(path, 'render/flavors/remotion.md')
    assert findings(path) == []


def test_longer_name_does_not_satisfy_its_suffix(tmp_path: Path) -> None:
    """`contexts.md` must not count as a reference to `ts.md`."""
    path = make(tmp_path, VALID + '\n- Read `contexts.md`.\n')
    sibling(path, 'contexts.md')
    sibling(path, 'ts.md')
    messages = [f.message for f in findings(path) if f.rule == 'skill-orphan']
    assert len(messages) == 1
    assert 'ts.md' in messages[0]


def test_claude_md_needs_no_reference(tmp_path: Path) -> None:
    """Claude Code loads a directory's CLAUDE.md itself, at any depth."""
    path = make(tmp_path, VALID)
    sibling(path, 'CLAUDE.md')
    sibling(path, 'mode/CLAUDE.md')
    assert findings(path) == []


def test_absolute_home_path_fails(tmp_path: Path) -> None:
    """A real account segment trips bare, with a tail, and on macOS alike."""
    for leak in '/home/devuser', '/home/devuser/src', '/Users/alice':
        path = make(tmp_path, VALID + f'\n- Run it in {leak}.\n')
        assert 'skill-local-path' in rules(check_leaks(path), Severity.ERROR), leak


def test_hooks_tree_ships_no_home_path() -> None:
    """hooks/ runs on other machines, so a literal home path here is the leak."""
    home = str(Path.home())
    tree = Path(__file__).parent
    leaking = [
        p.relative_to(tree).as_posix()
        for pattern in ('**/*.py', '**/*.md', '**/*.sh')
        for p in sorted(tree.glob(pattern))
        if home in p.read_text()
    ]
    assert leaking == []


def test_placeholder_home_path_passes(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- The slug of /home/u/app/x is -home-u-app-x.\n')
    assert check_leaks(path) == []


def test_secret_in_a_sibling_fails(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- Read `creds.md`.\n')
    creds = sibling(path, 'creds.md', 'export TOKEN=sk-ant-oat01-abcdefgh\n')
    assert 'skill-secret' in rules(check_leaks(creds), Severity.ERROR)


def test_duplicate_basename_needs_a_path_form(tmp_path: Path) -> None:
    """One `README.md` mention cannot stand for two files of that name."""
    path = make(tmp_path, VALID + '\n- Each mode ships a `README.md`.\n')
    sibling(path, 'art/p5js/README.md')
    sibling(path, 'video/manim/README.md')
    messages = [f.message for f in findings(path) if f.rule == 'skill-orphan']
    assert len(messages) == 2


def test_duplicate_basename_reached_by_a_path_suffix(tmp_path: Path) -> None:
    """A suffix with a directory in it is unique, so each file is reached."""
    path = make(tmp_path, VALID + '\n- Read `p5js/README.md` and `manim/README.md`.\n')
    sibling(path, 'art/p5js/README.md')
    sibling(path, 'video/manim/README.md')
    assert findings(path) == []


def test_root_file_keeps_its_name_beside_a_deeper_namesake(tmp_path: Path) -> None:
    """`manim.md` at the root and `render/flavors/manim.md` named from `render.md`."""
    path = make(tmp_path, VALID + '\n- Read `manim.md` or `render.md`.\n')
    sibling(path, 'manim.md')
    sibling(path, 'render.md', 'Read `flavors/manim.md`.\n')
    sibling(path, 'render/flavors/manim.md')
    assert findings(path) == []


def test_deeper_path_does_not_credit_a_shallower_namesake(tmp_path: Path) -> None:
    """`flavors/manim.md` in `render.md` names `render/flavors/manim.md`, not the root `manim.md`."""
    path = make(tmp_path, VALID + '\n- Read `render.md`.\n')
    sibling(path, 'manim.md')
    sibling(path, 'render.md', 'Read `flavors/manim.md`.\n')
    sibling(path, 'render/flavors/manim.md')
    messages = [f.message for f in findings(path) if f.rule == 'skill-orphan']
    assert len(messages) == 1
    assert messages[0].startswith(str(path.parent / 'manim.md'))


def test_root_name_does_not_credit_its_deeper_namesake(tmp_path: Path) -> None:
    """`README.md` is the root file's whole path; `deep/README.md` keeps needing its directory."""
    path = make(tmp_path, VALID + '\n- Read `README.md`.\n')
    sibling(path, 'README.md')
    sibling(path, 'deep/README.md')
    messages = [f.message for f in findings(path) if f.rule == 'skill-orphan']
    assert len(messages) == 1
    assert 'deep/README.md' in messages[0]


def test_every_doc_keeps_its_own_path_as_a_form() -> None:
    """Two docs sharing every suffix are each named by their full path alone."""
    docs = {'a/x/README.md', 'b/x/README.md'}
    assert name_forms(docs) == {rel: {rel} for rel in docs}


def run_lint(*paths: Path) -> subprocess.CompletedProcess[str]:
    script = Path(__file__).with_name('skill_frontmatter_lint.py')
    return subprocess.run(
        [sys.executable, str(script), *map(str, paths)], capture_output=True, text=True, check=False
    )


def test_leak_scan_reaches_a_doc_outside_any_skill(tmp_path: Path) -> None:
    """CLAUDE.md bans local paths in source, not only under a SKILL.md."""
    (tmp_path / 'README.md').write_text('Clone it into /home/devuser/src.\n')
    result = run_lint(tmp_path)
    assert result.returncode == 2, result
    assert 'skill-local-path' in result.stderr


def test_hidden_directories_are_not_scanned(tmp_path: Path) -> None:
    """Ignored state such as .claude/plans/ lives in hidden directories."""
    plans = tmp_path / '.claude' / 'plans'
    plans.mkdir(parents=True)
    (plans / 'plan.md').write_text('Edit /home/devuser/src/x.py.\n')
    assert run_lint(tmp_path).returncode == 0


def test_marker_opts_a_file_out_of_the_path_rule(tmp_path: Path) -> None:
    """evals/README.md shows a real-looking path as the thing to strip."""
    doc = tmp_path / 'README.md'
    doc.write_text('<!-- lint: allow skill-local-path -->\nStrip /home/devuser/wk/.\n')
    assert check_leaks(doc) == []


def test_marker_counts_only_on_a_line_of_its_own(tmp_path: Path) -> None:
    """skills/CLAUDE.md documents the marker in prose; quoting it must not disarm the file."""
    doc = tmp_path / 'README.md'
    for smuggled in (
        'Opt out with `<!-- lint: allow skill-local-path -->`.',
        '> <!-- lint: allow skill-local-path -->',
        'The <!-- lint: allow skill-local-path --> marker, mid-sentence.',
    ):
        doc.write_text(f'{smuggled}\nWork in /home/devuser/app/x.\n')
        assert 'skill-local-path' in rules(check_leaks(doc), Severity.ERROR), smuggled


def test_secret_has_no_opt_out(tmp_path: Path) -> None:
    doc = tmp_path / 'README.md'
    doc.write_text('<!-- lint: allow skill-local-path -->\nexport TOKEN=sk-ant-oat01-abcdefgh\n')
    assert 'skill-secret' in rules(check_leaks(doc), Severity.ERROR)


def test_container_home_is_not_a_leak(tmp_path: Path) -> None:
    """dockbox pins its container HOME; that path names no authoring machine."""
    doc = tmp_path / 'README.md'
    doc.write_text(
        '`~/.claude` -> `/home/dockbox/.claude` (rw); older images used /home/claude/.\n'
    )
    assert check_leaks(doc) == []


def test_container_account_prefix_is_not_the_exemption(tmp_path: Path) -> None:
    """Only the whole segment is the container HOME; `dockbox-2` is another account."""
    doc = tmp_path / 'README.md'
    for leak in '/home/claude-user', '/home/claude.local', '/home/dockbox-2', '/home/dockbox.old':
        doc.write_text(f'Work in {leak}/src.\n')
        assert 'skill-local-path' in rules(check_leaks(doc), Severity.ERROR), leak


def test_sibling_path_lints_its_owning_skill(tmp_path: Path) -> None:
    """A commit touching only `deep/leaf.md` still has to reach it from SKILL.md."""
    path = make(tmp_path, VALID)
    leaf = sibling(path, 'deep/leaf.md')
    assert skill_files([leaf]) == [path]


def test_direct_sibling_lints_its_owning_skill(tmp_path: Path) -> None:
    """`skills/create/web.md` sits beside SKILL.md, not under a subdirectory."""
    path = make(tmp_path, VALID)
    web = sibling(path, 'web.md')
    assert skill_files([web]) == [path]


def test_doc_without_an_owner_lints_no_skill(tmp_path: Path) -> None:
    doc = tmp_path / 'README.md'
    doc.write_text('notes\n')
    assert skill_files([doc]) == []


def test_missing_path_fails_loud(tmp_path: Path) -> None:
    result = run_lint(tmp_path / 'nope.md')
    assert result.returncode != 0
    assert 'nope.md' in result.stderr
