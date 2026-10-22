name = diskclean
PREFIX ?= $(HOME)/.local/bin

.PHONY: test check install clean

test: check
	bash test.sh

check:
	bash -n $(name) test.sh

install:
	mkdir -p $(PREFIX)
	install -m 755 $(name) $(PREFIX)/$(name)

clean:
