.DEFAULT_GOAL := help
.PHONY: help image install seccomp test clean

IMAGE := dockbox
TZ := $(shell date +%Z 2>/dev/null || echo UTC)
SUDO := $(shell docker info >/dev/null 2>&1 || echo sudo)
PREFIX := $(HOME)/.local/bin
SHARE := $(HOME)/.local/share/dockbox

help:
	@echo "make image    - build docker image"
	@echo "make install  - build image + install dockbox and its seccomp profile"
	@echo "make seccomp  - install only the seccomp profile (no image build)"
	@echo "make test     - syntax check + unit tests (no docker)"
	@echo "make clean    - remove installed binary, profile and docker image"

test:
	bash -n dockbox
	bash test.sh

image:
	$(SUDO) docker build --target dockbox --build-arg TZ=$(TZ) --build-arg AGENTS_CACHEBUST=$(shell date +%s) -t $(IMAGE) -f Dockerfile ..

install: image seccomp
	install -m 755 dockbox $(PREFIX)/

seccomp: $(SHARE)/seccomp.json $(SHARE)/seccomp.LICENSE

$(SHARE)/%: %
	mkdir -p $(SHARE)
	install -m 644 $< $@

clean:
	rm -f $(PREFIX)/dockbox $(SHARE)/seccomp.json $(SHARE)/seccomp.LICENSE
	-rmdir $(SHARE) 2>/dev/null
	-$(SUDO) docker rmi $(IMAGE) 2>/dev/null
