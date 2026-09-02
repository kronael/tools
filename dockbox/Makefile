.DEFAULT_GOAL := help
.PHONY: help image install test clean

IMAGE := dockbox
TZ := $(shell date +%Z 2>/dev/null || echo UTC)
SUDO := $(shell docker info >/dev/null 2>&1 || echo sudo)
PREFIX := $(HOME)/.local/bin

help:
	@echo "make image    - build docker image"
	@echo "make install  - build image + install dockbox to ~/.local/bin"
	@echo "make test     - syntax check + unit tests (no docker)"
	@echo "make clean    - remove installed binary and docker image"

test:
	bash -n dockbox
	bash test.sh

image:
	$(SUDO) docker build --build-arg TZ=$(TZ) --build-arg AGENTS_CACHEBUST=$(shell date +%s) -t $(IMAGE) -f Dockerfile ..

install: image
	install -m 755 dockbox $(PREFIX)/

clean:
	rm -f $(PREFIX)/dockbox
	-$(SUDO) docker rmi $(IMAGE) 2>/dev/null
