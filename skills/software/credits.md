# Credits — attribution and licensing for ported work

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

## AI tool

NEVER a "Development assisted by …" or "Generated with …" line in README or
NOTICE — the AI marker is the `🤖` in WISDOM § Git, nowhere else.

## License compatibility

NEVER assume the destination license. Read the repository's current `LICENSE`,
package metadata, and `NOTICE` first. Preserve upstream copyright and notice
requirements. Describe copyleft obligations neutrally; NEVER call a license
"contamination."

Compatibility depends on the exact source and destination licenses and how
the work is linked and distributed. When distribution rights are not clear
from the license texts, surface the narrow uncertainty instead of inventing a
blanket prohibition.
