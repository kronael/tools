# pyright: basic
import configparser
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile

import pytest

SOURCE = 'git+https://github.com/kronael/tools.git@FULL_COMMIT_HASH#subdirectory=speclint'


def run_process(args, cwd, env=None):
    return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)


@pytest.fixture(scope='module')
def wheel(tmp_path_factory, pytestconfig):
    output = tmp_path_factory.mktemp('wheel')
    result = run_process(['uv', 'build', '--out-dir', str(output)], pytestconfig.rootpath)
    assert result.returncode == 0, result.stderr
    return next(output.glob('*.whl'))


@pytest.fixture
def consumer(tmp_path):
    env = dict(os.environ)
    for name in ('PYTHONPATH', 'VIRTUAL_ENV', 'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
        env.pop(name, None)
    env['GIT_CONFIG_NOSYSTEM'] = '1'
    env['GIT_CONFIG_GLOBAL'] = os.devnull
    env['PRE_COMMIT_HOME'] = str(tmp_path / 'hook-cache')
    assert run_process(['git', 'init', '-q', '.'], tmp_path, env).returncode == 0
    for name, value in [
        ('user.name', 'Example'),
        ('user.email', 'example@example.invalid'),
        ('commit.gpgsign', 'false'),
    ]:
        assert run_process(['git', 'config', name, value], tmp_path, env).returncode == 0
    root = tmp_path / 'specs'
    root.mkdir()
    (root / '01-cache.md').write_text('---\nstatus: planned\n---\n# Cache\n')
    (root / 'index.md').write_text(
        '| Spec | Status | Summary |\n|---|---|---|\n'
        '| [Cache](01-cache.md) | planned | Cache reads |\n'
    )
    return tmp_path, env


def test_wheel_contents(wheel):
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        assert [name for name in names if not name.startswith('speclint-0.1.0.dist-info/')] == [
            'speclint.py'
        ]
        metadata = archive.read('speclint-0.1.0.dist-info/METADATA').decode()
        assert 'Requires-Python: >=3.13' in metadata
        assert 'Requires-Dist: markdown-it-py<5,>=4' in metadata
        config = configparser.ConfigParser()
        config.read_string(archive.read('speclint-0.1.0.dist-info/entry_points.txt').decode())
        assert dict(config['console_scripts']) == {'speclint': 'speclint:main'}


def test_source_archive_checks_and_rebuild(wheel, consumer):
    directory, env = consumer
    with tarfile.open(next(wheel.parent.glob('*.tar.gz'))) as archive:
        archive.extractall(directory / 'source', filter='data')
    source = directory / 'source' / 'speclint-0.1.0'
    result = run_process(['make', 'prepare', 'check', 'right', 'test', 'build'], source, env)
    assert result.returncode == 0, result.stdout + result.stderr
    rebuilt = next((source / 'dist').glob('*.whl'))
    result = run_process(['uvx', '--from', str(rebuilt), 'speclint', 'specs'], directory, env)
    assert result.returncode == 0, result.stdout + result.stderr


def test_uvx_wheel_outside_source(wheel, consumer):
    directory, env = consumer
    command = ['uvx', '--from', str(wheel), 'speclint', '.']
    result = run_process(command, directory, env)
    assert result.returncode == 0, result.stderr
    (directory / 'specs' / '01-cache.md').write_text('---\nstatus: wrong\n---\n')
    result = run_process(command, directory, env)
    assert result.returncode == 1
    assert '[spec-status]' in result.stdout
    result = run_process([*command[:-1], 'absent'], directory, env)
    assert result.returncode == 2
    assert 'no such file' in result.stderr


@pytest.mark.parametrize('invalid', ['nul', 'huge-line'])
def test_packaged_input_errors_exit_2(wheel, consumer, invalid):
    directory, env = consumer
    if invalid == 'nul':
        (directory / 'specs' / 'index.md').write_text('[Invalid](bad%00.md)\n')
    else:
        (directory / 'code.py').write_text('x = 1\n')
        (directory / 'specs' / '01-cache.md').write_text(
            '---\nstatus: planned\n---\n`code.py:' + '9' * 4500 + '`\n'
        )
    result = run_process(['uvx', '--from', str(wheel), 'speclint', '.'], directory, env)
    assert result.returncode == 2
    assert result.stderr.startswith('speclint: Cannot read corpus')
    assert len(result.stderr.splitlines()) == 1
    assert 'Traceback' not in result.stderr


def test_uvx_git_subdirectory_pin(consumer, tmp_path_factory, pytestconfig):
    directory, env = consumer
    repo = tmp_path_factory.mktemp('source')
    package = repo / 'speclint'
    package.mkdir()
    for name in ('pyproject.toml', 'speclint.py', 'README.md'):
        shutil.copyfile(pytestconfig.rootpath / name, package / name)
    assert run_process(['git', 'init', '-q', '.'], repo, env).returncode == 0
    assert run_process(['git', 'add', 'speclint'], repo, env).returncode == 0
    result = run_process(
        [
            'git',
            '-c',
            'user.name=Example',
            '-c',
            'user.email=example@example.invalid',
            '-c',
            'commit.gpgsign=false',
            'commit',
            '-qm',
            'Fixture',
        ],
        repo,
        env,
    )
    assert result.returncode == 0, result.stderr
    revision = run_process(['git', 'rev-parse', 'HEAD'], repo, env).stdout.strip()
    assert len(revision) == 40
    source = f'git+{repo.as_uri()}@{revision}#subdirectory=speclint'
    result = run_process(['uvx', '--from', source, 'speclint', '.'], directory, env)
    assert result.returncode == 0, result.stderr


def test_pre_commit_activation_and_deletion(wheel, consumer, pytestconfig):
    directory, env = consumer
    readme = (pytestconfig.rootpath / 'README.md').read_text()
    config = readme.split('```yaml\n', 1)[1].split('```', 1)[0]
    config = config.replace(SOURCE, str(wheel))
    (directory / '.pre-commit-config.yaml').write_text(config)
    result = run_process([sys.executable, '-m', 'pre_commit', 'install'], directory, env)
    assert result.returncode == 0, result.stderr
    paths = ['.pre-commit-config.yaml', 'specs/index.md', 'specs/01-cache.md']
    assert run_process(['git', 'add', *paths], directory, env).returncode == 0
    result = run_process(['git', 'commit', '-qm', 'Valid corpus'], directory, env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Passed' in result.stderr
    index = directory / 'specs' / 'index.md'
    original = index.read_text()
    index.write_text('<!--\n' + original + '-->\n')
    assert run_process(['git', 'add', 'specs/index.md'], directory, env).returncode == 0
    result = run_process(['git', 'commit', '-qm', 'Hidden row'], directory, env)
    assert result.returncode != 0
    assert '[spec-index-row]' in result.stderr
    index.write_text(original + '\n`[Template](02-missing.md)`\n')
    assert run_process(['git', 'add', 'specs/index.md'], directory, env).returncode == 0
    result = run_process(['git', 'commit', '-qm', 'Literal example'], directory, env)
    assert result.returncode == 0, result.stdout + result.stderr
    for target in '<02-removed.md>', "02-removed.md 'Example'":
        index.write_text(original + f'| [Removed]({target}) | shipped | Removed |\n')
        assert run_process(['git', 'add', 'specs/index.md'], directory, env).returncode == 0
        result = run_process(['git', 'commit', '-qm', 'Stale row'], directory, env)
        assert result.returncode != 0
        assert '[spec-index-dangling]' in result.stderr
    assert (
        run_process(
            ['git', 'restore', '--staged', '--worktree', 'specs/index.md'], directory, env
        ).returncode
        == 0
    )
    spec = directory / 'specs' / '01-cache.md'
    spec.write_text('---\nstatus: invalid\n---\n')
    assert run_process(['git', 'add', 'specs/01-cache.md'], directory, env).returncode == 0
    result = run_process(['git', 'commit', '-qm', 'Invalid corpus'], directory, env)
    assert result.returncode != 0
    assert '[spec-status]' in result.stderr
    assert (
        run_process(
            ['git', 'restore', '--staged', '--worktree', 'specs/01-cache.md'], directory, env
        ).returncode
        == 0
    )
    assert run_process(['git', 'rm', 'specs/01-cache.md'], directory, env).returncode == 0
    staged = run_process(['git', 'diff', '--cached', '--name-status'], directory, env)
    assert staged.stdout.strip() == 'D\tspecs/01-cache.md'
    result = run_process(['git', 'commit', '-qm', 'Stale retirement'], directory, env)
    assert result.returncode != 0
    assert '[spec-index-dangling]' in result.stderr
    assert run_process(['git', 'rm', 'specs/index.md'], directory, env).returncode == 0
    result = run_process(['git', 'commit', '-qm', 'Retire corpus'], directory, env)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'Passed' in result.stderr
    config = config.replace(f"uvx --from '{wheel}' speclint .", 'missing-speclint-command .')
    (directory / '.pre-commit-config.yaml').write_text(config)
    result = run_process([sys.executable, '-m', 'pre_commit', 'run', '--all-files'], directory, env)
    assert result.returncode != 0
    assert 'not found' in result.stdout


def test_install_target_isolated(consumer, pytestconfig):
    directory, env = consumer
    env['UV_TOOL_DIR'] = str(directory / 'tools')
    env['UV_TOOL_BIN_DIR'] = str(directory / 'bin')
    result = run_process(['make', 'install'], pytestconfig.rootpath, env)
    assert result.returncode == 0, result.stdout + result.stderr
    result = run_process([str(directory / 'bin' / 'speclint'), '.'], directory, env)
    assert result.returncode == 0, result.stderr
