name = qemubox
PREFIX ?= $(HOME)/.local/bin

.PHONY: test install clean

test:
	bash -n $(name)

install:
	install -m 755 $(name) $(PREFIX)/$(name)

clean:
	rm -f $(PREFIX)/$(name)
