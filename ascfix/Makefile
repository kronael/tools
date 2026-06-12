name = ascfix

.PHONY: build test install clean

build:
	go build -o $(name) .

test: build
	@echo "┌───┐" | printf '┌───┐\n│   │\n└─┬─┘\n  ─\n  │\n' | ./$(name)

install: build
	cp $(name) ~/.local/bin/$(name)

clean:
	rm -f $(name)
