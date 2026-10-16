name = kvs
PREFIX ?= $(HOME)/.local/bin

.PHONY: build test install clean

build:
	go build -o dist/$(name) .

test:
	go vet ./...
	go test -race .

install: build
	install -m 755 dist/$(name) $(PREFIX)/$(name)

clean:
	rm -rf dist
