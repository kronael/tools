Skills & Workflow — kronael toolkit

┌─ orientation ───────────────┐
│ resolve recall-memories     │
│ explore                     │
└──────────────┬──────────────┘
               │
┌─ planning ───▼──────────────┐
│ specs ship                  │
└──────────────┬──────────────┘
               │
┌─ coding ─────▼──────────────┐
│ go rs py ts tsx sh sql cli  │         ┌─ escalation ────────┐
│ service data trader         ├────────►│ haiku sonnet opus   │
└──────────────┬──────────────┘         │ fable sub fin       │
               │                        └─────────────────────┘
┌─ quality ────▼──────────────┐
│ review code-review improve  │
│ refine visual testing bugs  │
└──────────────┬──────────────┘
               │
┌─ output ─────▼──────────────┐         ┌─ communication ─────┐
│ commit pr-draft release     │         │ diary readme wisdom │
│ gh-comment                  ├────────►│ learn tweet         │
└─────────────────────────────┘         └─────────────────────┘

orientation — resolve, recall-memories, explore
Load context before acting. resolve is the universal entry point for every user
message: it loads diary and project facts, then matches the task against all
skill descriptions instead of pattern-jumping at the first fit. recall-memories
searches diary, memory, and prior session transcripts ("what did we decide").
explore is read-only answer mode — questions and audits with zero modifications.
Reach for this cluster at session start or whenever prior decisions matter.

planning — specs, ship
Turn intent into a plan before code. specs writes design docs into specs/ for
architecture and feature design; ship tracks multi-session work end to end
(plans, state, critiques in .ship/). Skip the cluster for one-off or <30min
tasks — go straight to coding.

coding — go, rs, py, ts, tsx, sh, sql, cli, service, data, trader
Domain rules loaded while writing code. Language skills (go, rs, py, ts, tsx,
sh, sql) activate by file type and carry language-specific ALWAYS/NEVER rules;
shape skills (cli, service, data, trader) activate by what is being built —
CLI tools, REST services, ETL/collectors, trading bots. They pair: a Rust CLI
loads rs + cli.

quality — review, code-review, improve, refine, visual, testing, bugs
Make working code right. review is deep multi-lens code review with discussion
and optional GitHub posting; code-review checks the current diff for bugs and
cleanups; improve does a targeted fix via subagent; refine orchestrates the
full polish of a finished feature; visual handles UI/styling through a headful
browser; testing carries test-writing and test-debugging patterns; bugs keeps
the bugs.md record-don't-fix queue. Reach for it after the feature works,
before it ships.

output — commit, pr-draft, release, gh-comment
Get verified work out of the working tree. commit formats and makes git
commits; pr-draft writes PR descriptions; release prepares and tags releases;
gh-comment posts inline review findings to a GitHub PR. Use once a unit of
work is done and verified — never before.

communication — diary, readme, wisdom, learn, tweet
Record and broadcast — a side channel that fires after milestones at any
stage, not a spine step. diary logs decisions to .diary/ after commits and key
choices; readme syncs README/ARCHITECTURE/CHANGELOG after shipping; wisdom
authors and edits SKILL.md/CLAUDE.md rules; learn mines session history into
new skills; tweet drafts X threads about shipped work.

escalation — haiku, sonnet, opus, fable, sub, fin
Route work to the right model or mode — a side channel available from any
stage. haiku, sonnet, opus, and fable spawn background subagents at increasing
capability: mechanical tasks ► coding and exploration ► design and complex
reasoning ► hardest long-horizon problems. sub is the generic background
spawn for work the main thread does not need results from; fin is finish
mode — run to completion without confirmation stops. Reach for it whenever
work can be offloaded or needs more (or less) horsepower.
