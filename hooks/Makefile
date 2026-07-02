.DEFAULT_GOAL := help
.PHONY: help test test-all clean

PYTEST := $(shell command -v pytest 2>/dev/null || echo $(HOME)/.local/bin/pytest)

# Test-bearing files. Some hook scripts still read stdin at import time, so
# collect only files known to be pytest-safe.
TEST_FILES := test_pretool_nudge.py test_codex_hook.py

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
