.DEFAULT_GOAL := help
.PHONY: help test test-all clean

# uvx supplies PyYAML, which a uv-tool pytest lacks; CI pip-installs both.
PYTEST := $(shell command -v uvx >/dev/null 2>&1 && echo uvx --with pyyaml pytest || command -v pytest 2>/dev/null || echo $(HOME)/.local/bin/pytest)

# Explicit list, not the directory: a new test_*.py runs only once it is added
# here, and the suite stays green while silently skipping it.
TEST_FILES := test_pretool_nudge.py test_prompt_nudge.py test_codex_hook.py test_stop.py test_memory_nudge.py test_skill_frontmatter_lint.py test_spec_lint.py test_md_format.py

help:
	@echo "make test     - run bundled pytest cases ($(TEST_FILES))"
	@echo "make test-all - same as test, but verbose"
	@echo "make clean    - remove __pycache__"

test:
	$(PYTEST) -q $(TEST_FILES)

test-all:
	$(PYTEST) -v $(TEST_FILES)

clean:
	rm -rf __pycache__
