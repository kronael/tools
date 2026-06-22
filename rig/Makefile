.PHONY: install clean demo

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
	ln -sf rig ~/.local/bin/gw
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
	rm -f ~/.local/bin/gp ~/.local/bin/gpc ~/.local/bin/gpa ~/.local/bin/gw

tmp/demo.cast: demo/run.ts
	mkdir -p tmp
	COLUMNS=80 LINES=30 asciinema rec tmp/demo.cast --overwrite --cols 80 --rows 30 -c 'bun run demo/run.ts'

tmp/demo.gif: tmp/demo.cast
	agg --theme solarized-light --font-size 16 \
	    --cols 80 --rows 30 \
	    --idle-time-limit 3 --last-frame-duration 8 \
	    tmp/demo.cast tmp/demo.gif

demo: tmp/demo.gif
