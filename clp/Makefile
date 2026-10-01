DEST = $(HOME)/.local/share/clp

test:
	bash -n clp.bash
	bash test.sh

install:
	mkdir -p $(DEST)
	cp clp.bash $(DEST)/clp.bash

clean:
	rm -f $(DEST)/clp.bash
	test ! -d $(DEST) || rmdir $(DEST)
