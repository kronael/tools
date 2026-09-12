# Minimize — does this rule earn its context?

A rule in an always-loaded file costs every session. It earns that cost only
when the model would NOT already behave that way. Measure it: put the topic to
a model that cannot see the rule, and compare.

- Reproduced by the clean model → CUT. The text buys nothing.
- Contradicted by the clean model → KEEP, highest value. It overrides a strong
  prior, which is the only thing guidance can do that training cannot.
- Produced by neither → KEEP. Genuinely absent from the default.

Scope this to NORMATIVE content — wisdom, style, judgment. Workflow runbooks
(`commit`, `ship`, `release`) encode a specific procedure and are not
measurable this way.

## The contamination trap

A subagent is handed `~/.claude/CLAUDE.md` and every applicable project
`CLAUDE.md` before its first token. Telling it "do not read any files" removes
nothing — the text is already in its context, and it will paraphrase the rule
back as if it had invented it. NEVER measure with a subagent, a `Task`, or any
nested `claude` that inherits this machine's config; ALWAYS use a clean room
built below, and ALWAYS verify the room before trusting a single answer.

The tell is specificity. A clean model produces the field's default. A
contaminated one hands back this repo's own idiosyncrasies — an exact path, an
exact line count, an exact separator character. When an answer reads like the
file, the room leaked.

## Clean room

`minimize/scripts/clean-room.sh <model> <prompt-file>` runs one prompt against a
throwaway `HOME`, so no wisdom file exists to load, in an empty working
directory, so no project `CLAUDE.md` is discoverable. Export
`CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` first — the script refuses
without one, and a clean `HOME` means OAuth and keychain are unreachable.

ALWAYS run the same prompt at two models. One agreeing is a signal, two is a
verdict.

For a cross-vendor check, `codex` works the same way, but its `CODEX_HOME`
holds `AGENTS.md` symlinked to the wisdom file plus memories, history and
hooks, so copy ONLY `auth.json` into a throwaway home and pass `--ephemeral`:

```bash
S=$(mktemp -d); mkdir -p "$S/home" "$S/cwd"
cp ~/.codex/auth.json "$S/home/auth.json"
printf 'model_reasoning_effort = "high"\n' > "$S/home/config.toml"
cd "$S/cwd" && CODEX_HOME="$S/home" codex exec --ephemeral \
  --dangerously-bypass-approvals-and-sandbox "<topic prompt>" </dev/null
```

NEVER `resume` — a resumed session carries the last one's context. A different
vendor makes agreement stronger evidence that the field agrees, and makes a
lone difference weaker evidence, since it may be vendor taste.

## Verify the room, every run

Before the real topic, ask a probe whose answer this repo states unusually, and
confirm the reply gives the field default instead. Branch naming, worktree
placement, and line width work well. ALWAYS discard the whole run when the
probe comes back carrying repo-specific detail.

## Ask the topic

Ask for the guidance itself, never for a critique of ours, and NEVER quote or
paraphrase our text in the prompt — the prompt is the last place contamination
gets in. Name the topic and the setting, demand concrete committal rules with
real numbers, and forbid preamble. Run the same prompt at two models when both
are reachable; one agreeing is a signal, two is a verdict.

## Record

Findings go to `BUGS.md` as a proposal, never applied on sight — cutting an
always-loaded rule changes every future session. State which model produced
what, so the evidence can be re-checked.
