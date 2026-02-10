.PHONY: install clean

install:
	mkdir -p ~/.local/bin
	install -m 755 gt ~/.local/bin/gt
	ln -sf gt ~/.local/bin/gco
	ln -sf gt ~/.local/bin/gto
	ln -sf gt ~/.local/bin/gtp
	ln -sf gt ~/.local/bin/gtr
	rm -f ~/.local/bin/gt-checkout ~/.local/bin/gt-push ~/.local/bin/gt-rebase
	rm -f ~/.local/bin/gb ~/.local/bin/gpo ~/.local/bin/gtb ~/.local/bin/gt-branch
	rm -f ~/bin/gt ~/bin/gco ~/bin/gto ~/bin/gtp ~/bin/gtr

clean:
	rm -f ~/.local/bin/gt ~/.local/bin/gco ~/.local/bin/gto
	rm -f ~/.local/bin/gtp ~/.local/bin/gtr
