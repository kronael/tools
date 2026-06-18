---
name: credit
description: Attribution and licensing practice for LLM-assisted work — how to acknowledge upstream sources, ported code, and AI tools. NOT a slash command; loaded as ambient context.
when_to_use: "porting code, adapting a skill, adding a dependency, shipping anything built on prior work"
---

# Credit

## Why this matters more in LLM-vibed work

LLMs blend sources invisibly. When a model ports, adapts, or derives from upstream
work, the human reviewing the output may not notice the provenance. The obligation
to attribute does not disappear because the author was AI-assisted — it shifts to
the person directing the work.

## ALWAYS

- ALWAYS create a `NOTICE` file when the repo contains ported or adapted code from
  named upstream sources
- ALWAYS include upstream copyright, license type, and URL in `NOTICE`
- ALWAYS retain per-file copyright headers and LICENSE files that came with ported work
- ALWAYS update `NOTICE` when adding a new ported skill, adapted algorithm, or
  vendored snippet — even if the source license does not legally require attribution
- ALWAYS note the chain: if work was ported via an intermediary (e.g. hermes-agent),
  acknowledge both the original author and the intermediary

## NEVER

- NEVER strip copyright headers from ported files — even MIT/Unlicense
- NEVER claim original authorship of adapted work in commit messages or README
- NEVER omit Apache-2.0 NOTICE obligations — Apache requires the NOTICE file to be
  preserved and reproduced in derivative works

## NOTICE file format

Follow the arizuko pattern (see ~/wk/arizuko/NOTICE):

```
<project> — by <author>
<license>. <warranty disclaimer>. <attribution ask>.

If you build on this — say so:
  Built on <project> (<url>) by <author>.

Built on:
  <upstream> © <year> <author> (<license>)
    <url>
    [ported via <intermediary> if applicable]
```

One entry per upstream source. Group minor sources under a shared line if they
share the same origin repo. Keep it readable — a legal file someone will actually
look at.

## AI tool attribution

When a project is substantially shaped by an AI tool (code generation, skill
authoring, architectural decisions), note it in README or NOTICE:

```
Development assisted by Claude Code (Anthropic).
```

This is not legally required for most licenses, but sets accurate expectations
for contributors and auditors about the project's provenance.

## License compatibility quick reference

| Upstream license | Can include in Unlicense/MIT project? | Condition |
|-----------------|--------------------------------------|-----------|
| MIT             | ✅ | Keep copyright notice |
| Apache-2.0      | ✅ | Keep NOTICE file, copyright header |
| BSD-2/3         | ✅ | Keep copyright notice |
| GPL-2/3         | ❌ | Contaminates — do not port |
| AGPL-3          | ❌ | Contaminates — do not port |
| Unlicense       | ✅ | Nothing required |
