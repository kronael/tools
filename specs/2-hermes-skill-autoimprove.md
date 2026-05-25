# Skill Auto-Improvement: v2 Plan (post-oracle, post-research)

## TL;DR

The v1 plan (clone Hermes's post-turn background review into Claude Code via
the `Stop` hook + `claude -p` child) is wrong. Oracle found 22 concrete
failure modes; web research found documented horror stories with the
underlying approach (BSWEN: Hermes "auto-overwrites manual customizations
with worse versions"; "Library Drift" paper: LLM-authored skills deliver
**+0.0pp vs +16.2pp for human-curated**).

v2 design: deterministic observation queue (no LLM in hook) → manual or
scheduled batch synthesis → quarantine queue → explicit approval → promote.

---

## What killed v1

### Oracle's 22 failures, deduped to the load-bearing 8

1. **`Stop` ≠ "one user turn".** Fires on sidechains, tool pauses, intermediate stops. Counter is noisy at 1-stop-per-tool granularity.
2. **Sidechains reuse `sessionId`.** Task-spawned subagents live in `~/.claude/projects/<slug>/<sid>/subagents/...` with `isSidechain:true` — they increment the same counter and the JSONL we'd read is the wrong file.
3. **`claude -p` has no `--env` flag.** v1's recursion guard transport doesn't exist. Use shell env. The right hook-bypass flag is `--bare` (which I missed).
4. **One env var isn't enough.** Without `--bare`, child reloads UserPromptSubmit / PreCompact / PostToolUse — recursion via paths we didn't anticipate.
5. **Naive JSONL slicing is garbage.** Tool calls/results occupy many lines; "last 30 messages" might be 4 shell commands. Thinking blocks are present but empty in JSONL. No reliable "currently loaded skills" source.
6. **Direct skill edits = self-poisoning.** One bad inference mutates global behavior across all future sessions. `~/.claude/skills/` is not inherently a git repo — recovery is "hope the user notices".
7. **`systemMessage` is hidden injection, not UX.** v1 pretended it surfaces to the user; it doesn't.
8. **Race conditions** on `/tmp/<sid>.count` (no locking) and `.log`/`.read` markers (partial reads, dropped successes).

### Research findings

| source | finding | implication |
|---|---|---|
| [Library Drift, arXiv 2605.19576](https://arxiv.org/abs/2605.19576) | LLM-authored skills: +0.0pp baseline; human-curated: +16.2pp | Live-edit is empirically worse than baseline. Quarantine is mandatory. |
| [Hermes Curator docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator) | Hermes's actual trigger is inactivity (idle ≥2h, cycle ≥7d), NOT per-turn | v1 misread the source. Per-turn was never the design. |
| [Hermes issue #18373](https://github.com/NousResearch/hermes-agent/issues/18373) | Open complaint demanding dry-run/approval before auto-archival | Live-edit is contested upstream. |
| [BSWEN writeup](https://docs.bswen.com/blog/2026-04-07-hermes-ai-overwrites-skills/) | "Agent almost always thinks it performed well, even when it didn't" → overwrites manual customizations | Self-congratulation bias is documented in the system we're cloning. |
| [Reflexion arXiv 2303.11366](https://arxiv.org/abs/2303.11366) + [HF blog](https://huggingface.co/blog/Kseniase/reflection) | Per-turn reflection produces repetitive, inaccurate self-criticism | Per-turn is a documented anti-pattern. |
| [Anthropic SKILL.md best practices](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | "Explain *why*" > "ALWAYS/NEVER caps" — model follows the letter but misses edge cases | Conflicts with our wisdom skill's "ALWAYS use ALWAYS/NEVER" rule. Worth a deliberate call. |
| [DSPy MIPROv2](https://dspy.ai/learn/optimization/optimizers/) | Offline batch compilation against eval set — no online mutation | Eval set is the missing ingredient in any live mutation story. |
| [$47k multi-agent loop](https://techstartups.com/2025/11/14/ai-agents-horror-stories-how-a-47000-failure-exposed-the-hype-and-hidden-risks-of-multi-agent-systems/) | "Deployed without memory, observability, governance, stop conditions, or cost ceilings" | Stop conditions + cost ceilings are non-negotiable. |
| [A-MEM, arXiv 2502.12110](https://arxiv.org/abs/2502.12110) | Zettelkasten — atomic notes, embedding-linked, dedup by similarity + link structure | Better than threshold-based promotion. |

---

## v2 design

### Architecture (split into 3 stages)

```
┌─────────────────────┐    ┌─────────────────────┐    ┌────────────────────┐
│ Stage 1: observe    │    │ Stage 2: synthesize │    │ Stage 3: promote   │
│ Hook (deterministic)│ -> │ Out-of-band review  │ -> │ Manual gate        │
│ Append to queue     │    │ /learn equivalent   │    │ User approves      │
│ <1ms, no LLM        │    │ Reads queue + JSONL │    │ Promote to live    │
└─────────────────────┘    └─────────────────────┘    └────────────────────┘
```

### Stage 1: observation hook (deterministic, no LLM)

**Trigger**: `SessionEnd`, not `Stop`. One event per session. Sidechains don't fire it.

If `SessionEnd` isn't reliable on this Claude Code version, fall back to a `Stop` hook with **idle detection**: only fire if no Stop event in the previous 10 minutes (track via `/tmp/claude-skillreview/<sid>.last`, atomic flock).

**Behavior**: hook appends a single JSON line to `~/.claude/skill-review/queue/<YYYYMMDD>.jsonl`:

```json
{
  "ts": "2026-05-25T18:00:00Z",
  "session_id": "<sid>",
  "cwd": "/home/ondra/wk/foo",
  "jsonl_path": "~/.claude/projects/.../<sid>.jsonl",
  "is_sidechain": false,
  "turn_count": 23,
  "outcome_hint": "ended_normally"  // or "compacted" / "user_quit"
}
```

That's it. No LLM call. No file mutation outside the queue. <10ms hook.

Atomic append: `fcntl.flock` on the queue file before writing.

### Stage 2: synthesis (out-of-band)

A user-invoked command (`/skill-review` or `@curator`) or a scheduled batch (cron/systemd-timer via `/schedule`). Reads the queue, processes N pending entries, emits **candidate patches** to `~/.claude/skill-review/candidates/`.

Each candidate is a directory:
```
~/.claude/skill-review/candidates/<timestamp>-<skill-name>/
  patch.diff           # unified diff against current SKILL.md
  rationale.md         # why this change, citing transcript line numbers
  provenance.json      # source sessions, observed pattern count, model used
  status               # "pending" | "approved" | "rejected" | "promoted"
```

Synthesis runs with `claude -p --bare` (skips all hooks — verified flag), restricted `--allowedTools=Read,Glob,Grep,Edit,Write`, and writes only to `~/.claude/skill-review/candidates/`. The live `~/.claude/skills/` is **read-only to this process**.

Each candidate must satisfy structural guards before being written:
- **Multi-session evidence**: the same pattern must appear in ≥2 distinct sessions (per [learn skill](/home/ondra/wk/tools/skills/learn/SKILL.md) rule). Patterns observed in only one session are dropped, not candidated.
- **Bounded library**: if `~/.claude/skills/` is at the cap (default: 60 skills), creation of new skill candidates is rejected — only `update existing` patches are emitted.
- **Tier guard**: bundled skills (those in `git ls-files` of the tools repo) are READ-ONLY to the candidate generator. Only agent-authored / user-authored skills are mutable. Same rule as Hermes Curator (which scopes to "agent-authored skills only" — [docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/curator)).

### Stage 3: promotion (explicit approval)

User runs `/skill-review` to see pending candidates. UI is a slash command that lists:
```
3 pending candidates:
  1. update commit/SKILL.md  — "user prefers '[hotfix]' prefix for emergency fixes"  (2 sessions)
  2. update py/SKILL.md      — "always pin uv to >=0.4 because of XYZ"               (3 sessions)
  3. create skill 'hotfix'   — REJECTED (library at cap 60/60)
```

For each, user can: **diff** (show the patch), **approve** (apply), **reject** (drop), **edit** (open in `$EDITOR` then approve). Approved patches are applied with `git apply` if `~/.claude/skills/` is a git repo, else direct file write + tar.gz snapshot to `~/.claude/skill-review/snapshots/<timestamp>.tar.gz` for rollback.

Outcome-driven retirement: each promoted patch records a `usage_id`. If the next 5 sessions consulting that skill have user corrections to the same rule, the patch is auto-rolled-back. (Outcome attribution per Library Drift §4.)

---

## Sign-off checklist (v2)

### Decisions

| # | choice | recommend | rationale |
|---|---|---|---|
| A | trigger | SessionEnd (fallback: idle-Stop ≥10min) | Avoids per-turn noise, sidechain pollution |
| B | hook work | append-only observation queue, no LLM | <10ms, deterministic, no recursion risk |
| C | synthesis | user-invoked `/skill-review` or scheduled batch | Per-turn cost = 0; batch cost amortized |
| D | output | candidate dir with diff + rationale, never live edit | Library Drift mandates quarantine |
| E | approval | explicit slash command, no auto-promote | BSWEN horror story is exactly this |
| F | bounded cap | 60 skills max (configurable) | Library Drift §4 requirement |
| G | tier separation | bundled (RO) vs agent-authored (RW) | Hermes's own scoping rule |
| H | snapshot | tar.gz before each promote | Cheap rollback |
| I | child invocation | `claude -p --bare --allowedTools=Read,Glob,Grep,Edit,Write` | `--bare` skips hooks (real flag) |
| J | recursion guard | `CLAUDE_SKILL_REVIEW=1` env + `--bare` defense in depth | Belt + suspenders |
| K | multi-session evidence | ≥2 distinct sessions before candidate | matches existing `learn` skill rule |
| L | outcome retirement | rollback patches that get corrected in next 5 sessions | Library Drift outcome-driven retirement |

### Files

| file | lines | purpose |
|---|---|---|
| `hooks/skill_observe.py` | ~40 | SessionEnd hook, append to queue. NO LLM. |
| `hooks/stop.py` | +5 | Idle-fallback: if SessionEnd missing on this version, fire observe on stop+idle |
| `skills/skill-review/SKILL.md` | ~40 | New skill — user-invocable `/skill-review` |
| `skills/skill-review/curator.py` | ~150 | Stage 2 synthesis: queue → candidates. Spawns `claude -p --bare ...` |
| `skills/skill-review/promote.py` | ~80 | Stage 3: list candidates, approve/reject/edit, snapshot, apply |
| `CLAUDE.md` | +20 | Document the three-stage pipeline |

Total ~335 lines. Roughly 2× v1 — but with safety rails that prevent self-poisoning.

### Out of scope (deliberately)

- Per-turn reflection (Reflexion documented anti-pattern)
- Live skill mutation from any agent (Library Drift +0.0pp)
- Memory review (MEMORY.md) — Phase 3 once skills pipeline is proven
- Cross-session pattern detection beyond simple "2+ sessions" count — embedding-based dedup (A-MEM Zettelkasten) is Phase 4

### Anti-goals (explicit NEVER)

- NEVER edit `~/.claude/skills/` outside the explicit `/skill-review approve` path
- NEVER promote a candidate that touches a bundled (git-tracked) skill
- NEVER auto-create skills when library is at cap — force replace/retire instead
- NEVER run LLM synthesis inside a hook — only in Stage 2

---

## Open questions

1. **Does Claude Code's `SessionEnd` hook exist on the user's version?**
   - **Action**: verify in `claude --help` and settings docs. If absent, use the idle-Stop fallback.

2. **Is `~/.claude/skill-review/` a git repo?**
   - **Recommend**: init it as one in the skill bootstrap. Then `git apply` becomes the natural promotion path, and history is free.

3. **What's the right cap?**
   - Currently ~40 skills installed. Cap at 60 gives ~50% headroom. Override via env var.

4. **Anthropic SKILL.md guidance contradicts our wisdom rule.**
   - Our `wisdom` skill says "ALWAYS use ALWAYS/NEVER". Anthropic says "explain *why* > ALWAYS/NEVER caps".
   - This is a separate decision from the auto-improvement design. Worth raising as a wisdom-skill follow-up.

---

## What we'd be the first to ship

Per research, 20+ surveyed self-evolving systems exist but **none pair outcome-driven retirement with a bounded cap**. v2 has both. If we build this, we ship the Library Drift recommended fix that nobody else has built.

Also, no system I found does **structured observation queue + manual approval as the default**. Hermes auto-edits; LangGraph requires writing approval into the graph; DSPy is offline-only. v2 is a hybrid: cheap hook for capture, deliberate human for promotion. Closest analog is git's `staging area` model applied to skills.
