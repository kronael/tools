.DEFAULT_GOAL := help
.PHONY: help test test-all clean

PYTEST := $(shell command -v pytest 2>/dev/null || echo $(HOME)/.local/bin/pytest)

# Test-bearing hook files. Other hooks (stop.py, local.py, prompt_nudge.py,
# reclaude.py) read stdin at import time and break pytest collection — add
# them here once they're refactored to put main() behind __name__ == '__main__'.
TEST_FILES := pretool_nudge.py

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
