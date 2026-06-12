name = ascfix

.PHONY: build test install clean

build:
	go build -o $(name) .

test:
	go test .

install: build
	cp $(name) ~/.local/bin/$(name)

clean:
	rm -f $(name)
