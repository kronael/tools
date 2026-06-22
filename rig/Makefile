.PHONY: install clean

install:
	mkdir -p ~/.local/bin
	install -m 755 rig ~/.local/bin/rig
	ln -sf rig ~/.local/bin/rco
	ln -sf rig ~/.local/bin/rip
	ln -sf rig ~/.local/bin/rir
	ln -sf rig ~/.local/bin/rim
	ln -sf rig ~/.local/bin/riq
	ln -sf rig ~/.local/bin/gl
	ln -sf rig ~/.local/bin/gis
	ln -sf rig ~/.local/bin/gig
	ln -sf rig ~/.local/bin/gitg
	ln -sf rig ~/.local/bin/gp
	ln -sf rig ~/.local/bin/gpc
	ln -sf rig ~/.local/bin/gpa
	# clean old gt symlinks
	rm -f ~/.local/bin/gt ~/.local/bin/gco ~/.local/bin/gto
	rm -f ~/.local/bin/gtp ~/.local/bin/gtr
	rm -f ~/.local/bin/gt-checkout ~/.local/bin/gt-push ~/.local/bin/gt-rebase
	rm -f ~/.local/bin/gb ~/.local/bin/gpo ~/.local/bin/gtb ~/.local/bin/gt-branch
	rm -f ~/bin/gt ~/bin/gco ~/bin/gto ~/bin/gtp ~/bin/gtr

clean:
	rm -f ~/.local/bin/rig ~/.local/bin/rco
	rm -f ~/.local/bin/rip ~/.local/bin/rir ~/.local/bin/rim ~/.local/bin/riq
	rm -f ~/.local/bin/gl ~/.local/bin/gis ~/.local/bin/gig ~/.local/bin/gitg
	rm -f ~/.local/bin/gp ~/.local/bin/gpc ~/.local/bin/gpa
