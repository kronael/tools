.PHONY: help test test-%

# Subdirs whose Makefile exposes a `test` target. Add more as tests land.
TEST_DIRS := hooks

help:
	@echo "make test       - run tests across all subdirs ($(TEST_DIRS))"
	@echo "make test-<dir> - run tests in a single subdir, e.g. make test-hooks"

test: $(addprefix test-,$(TEST_DIRS))
	@echo "all tests passed ($(TEST_DIRS))"

test-%:
	$(MAKE) -C $* test
