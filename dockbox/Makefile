.PHONY: help image install

IMAGE := dockbox
UID := $(shell id -u)

help:
	@echo "make image    - build docker image"
	@echo "make install  - build image + install dockbox to /usr/local/bin"

image:
	docker build --build-arg UID=$(UID) -t $(IMAGE) .

install: image
	install -m 755 dockbox /usr/local/bin/
