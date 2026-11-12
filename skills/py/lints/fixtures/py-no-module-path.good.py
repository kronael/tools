import hashlib
import os
from pathlib import Path

MIGRATIONS = Path('migrations')
PARENT = os.path.dirname(os.getcwd())
SOURCE_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
WORKER_SOURCE = Path(worker.__file__).read_text()


def fixture_dir(pytestconfig):
    return pytestconfig.rootpath / 'tests' / 'assets'


def stub_location(monkeypatch, module):
    monkeypatch.setattr(module, '__file__', 'stub.py')


# An installed tool runs from any working directory; its templates ship beside it.
TEMPLATES = Path(__file__).resolve().parent / 'templates'  # ast-grep-ignore: py-no-module-path
