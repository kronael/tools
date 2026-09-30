name = qemubox
PREFIX ?= $(HOME)/.local/bin

.PHONY: test image install clean

test:
	bash -n $(name)
	bash test.sh

image:
	QEMUBOX_SOURCE="$(abspath ..)" bash ./$(name) build-base

install: image
	install -m 755 $(name) $(PREFIX)/$(name)

clean:
	rm -f $(PREFIX)/$(name)
