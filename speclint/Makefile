.PHONY: prepare test integration check right build install clean

prepare:
	uv sync --locked

test:
	uv run --locked python -X dev -W error -m pytest -q test_speclint.py

integration:
	uv run --locked python -X dev -W error -m pytest -q test_integration.py

check:
	uv run --locked ruff check .
	uv run --locked ruff format --check .

right:
	uv run --locked basedpyright

build:
	uv build

install:
	uv tool install --force .

clean:
	find . -type f \( -name '*.pyc' -o -path './dist/*' \) -delete
