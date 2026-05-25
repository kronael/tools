.DEFAULT_GOAL := help

# Subdirs whose Makefile exposes `test` / `clean` targets. Add as they land.
TEST_DIRS := hooks
CLEAN_DIRS := hooks dockbox

.PHONY: help test clean $(addprefix test-,$(TEST_DIRS)) $(addprefix clean-,$(CLEAN_DIRS))

help:
	@echo "make test        - run tests across all subdirs ($(TEST_DIRS))"
	@echo "make test-<dir>  - run tests in one subdir, e.g. make test-hooks"
	@echo "make clean       - clean across all subdirs + __pycache__ sweep"
	@echo "make clean-<dir> - clean one subdir"

test: $(addprefix test-,$(TEST_DIRS))
	@echo "all tests passed ($(TEST_DIRS))"

clean: $(addprefix clean-,$(CLEAN_DIRS))
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@echo "clean done"

test-%:
	$(MAKE) -C $* test

clean-%:
	$(MAKE) -C $* clean
