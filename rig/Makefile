.PHONY: install clean demo test check

install:
	mkdir -p ~/.local/bin
	install -m 755 rig ~/.local/bin/rig
	~/.local/bin/rig install
	# clean old gt symlinks
	rm -f ~/.local/bin/gt ~/.local/bin/gto
	rm -f ~/.local/bin/gtp ~/.local/bin/gtr
	rm -f ~/.local/bin/gt-checkout ~/.local/bin/gt-push ~/.local/bin/gt-rebase
	rm -f ~/.local/bin/gb ~/.local/bin/gpo ~/.local/bin/gtb ~/.local/bin/gt-branch
	rm -f ~/bin/gt ~/bin/gco ~/bin/gto ~/bin/gtp ~/bin/gtr

clean:
	test ! -d ~/.local/bin || find ~/.local/bin -maxdepth 1 -type l \( -lname rig -o -lname ~/.local/bin/rig \) -delete
	rm -f ~/.local/bin/rig

test: check
	bash test.sh

check:
	bash -n rig test.sh

tmp/demo.cast: demo/run.ts
	mkdir -p tmp
	COLUMNS=80 LINES=30 asciinema rec tmp/demo.cast --overwrite --cols 80 --rows 30 -c 'bun run demo/run.ts'

demo/demo.gif: tmp/demo.cast
	agg --theme solarized-light --font-size 16 \
	    --cols 80 --rows 30 \
	    --idle-time-limit 3 --last-frame-duration 8 \
	    tmp/demo.cast demo/demo.gif

demo: demo/demo.gif
