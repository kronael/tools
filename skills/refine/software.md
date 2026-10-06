# Refine lenses — software

What a refine pass hunts for against the language-agnostic baseline. Read WITH
`../software/code.md` (write-time rules), NEVER as a substitute — each lens names
the section that holds the rule. Every language skill requires `software`, so
every code context reads this file. Each lens carries the tag refine step 6
reads to pick the agent type.

## Coined and drifted names `simplify`

- ALWAYS grep the tree for every identifier the change introduces — function,
  parameter, field, type, test helper. A new word standing beside an existing
  name for the same thing (the column, the caller, the schema) is a finding;
  so is a synonym for the domain's word. Rule: `code.md` § Naming.
- ALWAYS grep the diff for the rebinding shapes: an import alias (`as`), a
  single-use `let x = y`, a named discard (`_foo`), a concept held in a bare
  initial (`u` for a URL), a `_from_<arg>` suffix the parameter already says.
- ALWAYS read each new or renamed function body against its verb — a `get_`
  that writes, an `is_` that mutates, a `finish_` that cancels is a finding,
  and a `simplify` fix is the rename, never a comment explaining the verb.

## Comments the baseline bans `simplify`

- ALWAYS list every comment in each touched FILE, not only in the hunks
  (`grep -nE '^\s*(//|#|--|/\*|\*)'`) — § Comments puts the whole file in
  scope. Each one that is not a public-API doc comment or one of the three
  named body exceptions is a finding.
- ALWAYS read a surviving doc comment against its item: on a private item, or
  restating the signature, it is a finding.
- ALWAYS check the comment directly above a log, warn or error call — a
  paraphrase of that message is the most common miss. So are line numbers,
  ticket IDs and history notes (`was`, `old`, `legacy`).

## Abstraction that does not pay `simplify`

- ALWAYS count the call sites of each helper, interface, generic, wrapper and
  config knob the change adds — `rg -n '<name>'`. One or two sites is a
  finding: inline it (§ Boring code).
- ALWAYS check each new branch, fallback or flag for an existing parameter,
  path or environment variable that already expresses the edge case.
- ALWAYS grep for function-typed struct fields the change adds (`func(` inside
  a Go struct, `Box<dyn Fn`, a `Callable` attribute) and run § Design's
  five-second test on each.
- ALWAYS flag two or more booleans that together encode one state — § Design
  wants the enum.

## Second path beside the first `simplify`

- ALWAYS grep the tree for the mechanism each new guard, helper, table, log
  site or config key duplicates — same verb, same table, same env var. A
  second path where the original could be extended is a finding
  (WISDOM § System-change discipline).
- ALWAYS check a fix that changes a contract or control flow across modules
  for its `BUGS.md` proposal; none is a finding, routed to `BUGS.md`, never
  applied.

## Swallowed, softened and retried errors `correctness`

- ALWAYS grep the diff for the swallow shapes: `_ = err`, `if err == nil {`
  with no else, `except …: pass` or log-and-continue, an empty `catch`,
  `.ok()`/`unwrap_or_default()`/`?? []` on a user-facing path, a fallback
  `None`/`[]`/`0` the caller proceeds on. Each must reach the user
  (WISDOM § System-change discipline).
- ALWAYS read every retry loop's body: anything but a network call or DB
  busy/locked inside it — a parse, a config read, a precondition — is a
  finding.

## External contract read from a summary `correctness`

- ALWAYS trace a client of another team's service to the provider's spec at
  its default head; a parameter name or formula sourced from an in-repo
  summary or a stub branch is a finding. ALWAYS recompute a derived formula on
  the spec's own worked examples (§ System changes).

## Layout drift `simplify`

- ALWAYS measure, never eyeball: `awk 'length > 80'` over the changed code
  lines, a multi-line expression inside an `if` condition, two imports on one
  line, a file log handler or log-file path in application code, `__dirname`
  or `basename $0` in a script (§ Layout and formatting).

## Deleted without being understood `correctness`

- ALWAYS check every deletion or "simplification" of code the change did not
  author for a stated reason the removed constraint does not hold — none
  stated is a finding (§ Grug rules, Chesterton's fence).
