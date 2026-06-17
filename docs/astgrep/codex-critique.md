- [research-astgrep.md](/home/onvos/app/tools/docs/astgrep/research-astgrep.md:282): `console.log($$$) -> ''` corrupts expression contexts, not just standalone statements. Test: `printf 'const f = () => console.log(a)\n' | ast-grep run --stdin -l ts -p 'console.log($$$)' -r ''` Output:
  ```text
  STDIN
  @@ -0,1 +0,1 @@
  1  │-const f = () => console.log(a)
    1│+const f = () => 
  ```

- [research-astgrep.md](/home/onvos/app/tools/docs/astgrep/research-astgrep.md:282): same rewrite also breaks larger expressions. Test: `printf 'x = console.log(a) + 1\n' | ast-grep run --stdin -l ts -p 'console.log($$$)' -r ''` Output:
  ```text
  STDIN
  @@ -0,1 +0,1 @@
  1  │-x = console.log(a) + 1
    1│+x =  + 1
  ```

- [research-astgrep.md](/home/onvos/app/tools/docs/astgrep/research-astgrep.md:285): “keeping children” is false; the pattern only matches self-closing JSX. Test: `printf '<OldButton>hi</OldButton>\n' | ast-grep run --stdin -l tsx -p '<OldButton $$$PROPS />' -r '<Button $$$PROPS />'; printf '\nEXIT:%s\n' $?` Output:
  ```text

  EXIT:1
  ```

- [research-astgrep.md](/home/onvos/app/tools/docs/astgrep/research-astgrep.md:293): `$E.unwrap() -> $E?` still fires in arbitrary expression statements and assignments; the doc admits no type-awareness, but this is too unsafe to present as a canned codemod. Test: `printf 'let x = value.unwrap();\n' | ast-grep run --stdin -l rust -p '$E.unwrap()' -r '$E?'` Output:
  ```text
  STDIN
  @@ -0,1 +0,1 @@
  1  │-let x = value.unwrap();
    1│+let x = value?;
  ```

- [research-astgrep.md](/home/onvos/app/tools/docs/astgrep/research-astgrep.md:296): backtick rewrite corrupts nested backticks. Test: `printf '\`echo \`date\`\`\n' | ast-grep run --stdin -l bash -p '\`$CMD\`' -r '$($CMD)'; printf '\nEXIT:%s\n' $?` Output:
  ```text
  STDIN
  @@ -0,1 +0,1 @@
  1  │-`echo `date``
    1│+$(echo)date``

  EXIT:0
  ```

- [research-astgrep.md](/home/onvos/app/tools/docs/astgrep/research-astgrep.md:241): strictness list is stale/incomplete for installed `ast-grep 0.42.3`; the CLI has `template`, but the doc lists only `cst/smart/ast/relaxed/signature`. Test: `ast-grep run --help | sed -n '/strictness of the pattern/,+14p'` Output:
  ```text
            The strictness of the pattern

            Possible values:
            - cst:       Match exact all node
            - smart:     Match all node except source trivial nodes
            - ast:       Match only ast nodes
            - relaxed:   Match ast node except comments
            - signature: Match ast node except comments, without text
            - template:  Similar to smart but match text only, node kinds are ignored
  ```

- [research-astgrep.md](/home/onvos/app/tools/docs/astgrep/research-astgrep.md:1): too long for a skill source; this file is 306 lines before any condensation, so an agent-facing skill copied from it will violate the repo’s under-200-line rule unless cut hard. Test: `wc -l docs/astgrep/research-astgrep.md` Output:
  ```text
  306 docs/astgrep/research-astgrep.md
  ```

- [research-astgrep.md](/home/onvos/app/tools/docs/astgrep/research-astgrep.md:10): cut most of §§1-7 for the skill. They are background/reference prose, not operational guardrails. The parts with demonstrated agent-failure value are the parse-validity warnings, strictness caveat, and a much smaller set of rewrites that survive hostile stdin tests.
