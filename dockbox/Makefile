.DEFAULT_GOAL := help
.PHONY: help image install test native-image integration test-all smoke clean

IMAGE := dockbox
SUDO := $(shell docker info >/dev/null 2>&1 || echo sudo)
PREFIX := $(HOME)/.local/bin
NATIVE_IMAGE := dockbox-native:forky
DOCKBOX_DOCKER ?= $(SUDO) docker

help:
	@echo "make image        - build the full production image"
	@echo "make install      - build the image and install dockbox"
	@echo "make test         - syntax and fast tests (no Docker)"
	@echo "make integration  - build and test the small native fixture"
	@echo "make test-all     - fast and native fixture tests"
	@echo "make smoke        - native tests against the production image"
	@echo "make clean        - remove installed binary and production image"

test:
	for script in dockbox dockbox-init dockbox-docker test.sh; do bash -n "$$script" || exit; done
	sh -n dockbox-codex-bridge
	bash -n tests/native.sh
	bash test.sh

native-image:
	timeout 300s $(SUDO) docker build --memory=2g -t $(NATIVE_IMAGE) -f tests/Dockerfile ..

integration: native-image
	DOCKBOX_IMAGE=$(NATIVE_IMAGE) DOCKBOX_DOCKER='$(DOCKBOX_DOCKER)' timeout 300s bash tests/native.sh

test-all: test integration

smoke:
	DOCKBOX_TEST_AGENTS=1 DOCKBOX_IMAGE=$(IMAGE) DOCKBOX_DOCKER='$(DOCKBOX_DOCKER)' timeout 300s bash tests/native.sh

image:
	$(SUDO) docker build --target dockbox \
	    --build-arg AGENTS_CACHEBUST=$(shell date +%s) \
	    -t $(IMAGE) -f ../qemubox/Dockerfile ..

install: image
	install -m 755 dockbox $(PREFIX)/

clean:
	rm -f $(PREFIX)/dockbox
	-$(SUDO) docker rmi $(IMAGE) 2>/dev/null
