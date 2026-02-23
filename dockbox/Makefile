# dockbox - dockerized Claude Code sandbox
# Builds a container with claude, codex, go, rust, node
# pre-installed. UID-matched to host user for correct
# file permissions on mounted directories.

.PHONY: help image install clean

IMAGE := dockbox
UID := $(shell id -u)
TZ := $(shell date +%Z 2>/dev/null || echo UTC)
SUDO := $(shell docker info >/dev/null 2>&1 || echo sudo)
PREFIX := $(HOME)/.local/bin

help:
	@echo "make image    - build docker image"
	@echo "make install  - build image + install dockbox to ~/.local/bin"
	@echo "make clean    - remove installed binary and docker image"

image:
	$(SUDO) docker build --build-arg UID=$(UID) --build-arg TZ=$(TZ) -t $(IMAGE) .

install: image
	install -m 755 dockbox $(PREFIX)/

clean:
	rm -f $(PREFIX)/dockbox
	-$(SUDO) docker rmi $(IMAGE) 2>/dev/null
