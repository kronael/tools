# dockbox - dockerized Claude Code sandbox
# Builds a container with claude, codex, go, rust, node
# pre-installed. UID-matched to host user for correct
# file permissions on mounted directories.

.PHONY: help image install

IMAGE := dockbox
UID := $(shell id -u)
SUDO := $(shell docker info >/dev/null 2>&1 || echo sudo)

help:
	@echo "make image    - build docker image"
	@echo "make install  - build image + install dockbox to /usr/local/bin"

image:
	$(SUDO) docker build --build-arg UID=$(UID) -t $(IMAGE) .

install: image
	sudo install -m 755 dockbox /usr/local/bin/
