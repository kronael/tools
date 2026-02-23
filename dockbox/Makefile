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
