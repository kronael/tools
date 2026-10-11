name = spec-lint
PREFIX ?= $(HOME)/.local/bin
PYTEST := $(shell command -v uvx >/dev/null 2>&1 && echo uvx pytest || echo python3 -m pytest)

.PHONY: help test check install clean

help:
	@echo "make test    - run the pytest suite"
	@echo "make check   - byte-compile the script"
	@echo "make install - install as $(PREFIX)/$(name)"
	@echo "make clean   - remove caches"

test: check
	$(PYTEST) -q test_spec_lint.py

check:
	python3 -m py_compile spec_lint.py

install:
	mkdir -p $(PREFIX)
	install -m 755 spec_lint.py $(PREFIX)/$(name)

clean:
	rm -rf __pycache__ .pytest_cache
