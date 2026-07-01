name = udfix
PREFIX ?= $(HOME)/.local/bin

.PHONY: build test install clean

build:
	go build -o $(name) .

test:
	go test .

install: build
	install -m 755 $(name) $(PREFIX)/$(name)

clean:
	rm -f $(name)
