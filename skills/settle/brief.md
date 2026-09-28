# Brief contract

Four blocks. A brief that omits one licenses what it omitted, because the brief
is the only thing that reaches the sub.

## Shape — goal, not steps

State what the output enables, hand over the context, draw the bounds, define
done, and let the sub choose the path. Numbered steps degrade current models.

```
I'm <larger task> for <who>. They need <what the output enables>.

Tree: <worktree path>, clean at <SHA>. Branch: <name>.
Read first: <the files carrying the idiom to match>.
Out of bounds: <paths not to touch>.

<the request, stated as a goal>

Done: <observable condition>.
```

## Evidence the sub must return

- ALWAYS demand the command and its output beside each finding, with
  `file:line` — a summary of a summary cannot be checked against anything.
- ALWAYS demand the positive control beside any "there is no X": the same query
  returning a hit where one exists.
- ALWAYS name the queries that lie here — the wrapped `grep` skips `.git`, a
  failed fetch prints nothing, a bare identifier matches its prefixes.
- NEVER accept a count without the matches it counted.

## House rules — paste verbatim into any brief whose sub may commit

A subagent carries a harness instruction to sign commits with a
`Co-Authored-By` trailer, which this house forbids. The brief is the only place
that resolves the conflict for the sub, and a pushed commit cannot be rewritten.

```
- Conventional commits, `type(scope): Message`, subject ≤72 characters.
- Stage by path. NEVER `git add -A`, NEVER `--amend`, NEVER `git push`.
- NEVER add a `Co-Authored-By` trailer to any commit.
- Detached HEAD only — NEVER create or attach a local branch.
- NEVER remove recursively; delete named files only.
- A fix that changes a contract or the control flow goes to `BUGS.md` as
  `proposed` — do not build it.
- Report the command and its output, never a conclusion on its own.
```

## Bounds

- ALWAYS name the worktree, the SHA it is clean at, and the paths that are out
  of bounds — a sub that meets a dirty tree otherwise treats the changes as its
  own and commits over another agent's work.
- ALWAYS keep writing subs serial on a shared tree; parallel belongs to
  read-only subs and to `git worktree add --detach` isolation.
- ALWAYS send a correction to a running sub with `SendMessage` rather than
  editing its files behind it.
