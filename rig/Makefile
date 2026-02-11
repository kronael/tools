.PHONY: install clean

install:
	mkdir -p ~/.local/bin
	install -m 755 rig ~/.local/bin/rig
	ln -sf rig ~/.local/bin/rio
	ln -sf rig ~/.local/bin/rip
	ln -sf rig ~/.local/bin/rir
	ln -sf rig ~/.local/bin/rim
	# clean old gt symlinks
	rm -f ~/.local/bin/gt ~/.local/bin/gco ~/.local/bin/gto
	rm -f ~/.local/bin/gtp ~/.local/bin/gtr
	rm -f ~/.local/bin/gt-checkout ~/.local/bin/gt-push ~/.local/bin/gt-rebase
	rm -f ~/.local/bin/gb ~/.local/bin/gpo ~/.local/bin/gtb ~/.local/bin/gt-branch
	rm -f ~/bin/gt ~/bin/gco ~/bin/gto ~/bin/gtp ~/bin/gtr

clean:
	rm -f ~/.local/bin/rig ~/.local/bin/rio
	rm -f ~/.local/bin/rip ~/.local/bin/rir ~/.local/bin/rim
