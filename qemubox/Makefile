name = qemubox
PREFIX ?= $(HOME)/.local/bin

.PHONY: test install clean

test:
	bash -n $(name)

install:
	install -m 755 $(name) $(PREFIX)/$(name)
	$(PREFIX)/$(name) build-base || echo "warning: prebuilt base not built (needs KVM + network); first box will provision lazily"

clean:
	rm -f $(PREFIX)/$(name)
