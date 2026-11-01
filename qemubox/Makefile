name = qemubox
PREFIX ?= $(HOME)/.local/bin

.PHONY: test test-native image install clean

test:
	bash -n $(name)
	bash -n guest-init
	sh -n initrd-init
	sh -n qemubox-codex-bridge
	bash -n test-native.sh
	bash test.sh

test-native:
	timeout --foreground 1800 bash test-native.sh

image:
	QEMUBOX_SOURCE="$(abspath ..)" bash ./$(name) build-base

install: image
	install -m 755 $(name) $(PREFIX)/$(name)

clean:
	rm -f $(PREFIX)/$(name)
