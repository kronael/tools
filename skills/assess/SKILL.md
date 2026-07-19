---
name: assess
description: >
  Run an adversarial assessment of a product, codebase, or docs from a
  specified expert perspective (CEO, CTO, CISO, enterprise buyer, etc.).
  Produces a structured critique memo saved to .ship/critique-<role>-<date>.md.
  NOT for code review (use /code-review). NOT for bug hunting (use /bugs).
user-invocable: true
---

# Assess

Run an adversarial expert assessment and return a verdict.

## Usage

`/assess <role> [target]`

- `role` — perspective: `ceo`, `cto`, `ciso`, `buyer`, `investor`, `competitor`
- `target` — what to assess: `docs`, `security`, `architecture`, `dashboards`, `all` (default: `all`)

## Workflow

1. **Load context** — read the target material:
   - `docs`: the product's onepager, how-to, and concept docs
   - `security`: `SECURITY.md` and any threat-model / security specs
   - `architecture`: `ARCHITECTURE.md`, `CLAUDE.md`, `README.md`
   - `dashboards`: fetch live pages (see §Dashboard evidence), read the dashboard service's source
   - `all`: all of the above + the spec index

2. **Adopt the role** — play the expert with no softening:
   - **ceo**: business model, defensibility, kill shot, TAM
   - **cto**: architecture scalability, tech debt, build vs buy, missing primitives
   - **ciso**: threat model gaps, compliance blockers (SOC2, HIPAA, GDPR), pen-test surface
   - **buyer**: enterprise procurement checklist, SLA/support gaps, integration story
   - **investor**: market size, moat, team signal, competitive risk
   - **competitor**: how to replicate and undercut in 6 months

3. **Structure the memo** — sections vary by role but always include:
   - One-line verdict (pass/fail/conditional)
   - Top 3 strengths (honest — avoid padding)
   - Top 3 blockers (specific, not vague)
   - Kill shot (single thing that would sink it)
   - Recommended next action (what would change the verdict)

4. **Save** — write to `.ship/critique-<role>-<YYYYMMDD>.md`

5. **Report** — return the verdict + blockers in ≤150 words

## Dashboard evidence (target=dashboards)

ALWAYS gather live evidence before critiquing. Start the dashboard service
locally on a scratch data dir, then fetch each page and inspect the rendered
structure (auth headers as the app requires):

```bash
for p in <dashboard routes>; do
  echo "=== $p ==="
  curl -sf "http://localhost:<port>$p" -H "$AUTH_HEADERS" \
    | grep -E "<h[123]|<nav|class=|<a href|<td|<th|<form|data-status" | head -20
done
```

Also check for 404s: pages in nav that return 404 are missing routes (not just "not specced").

## Dashboard CTO lens

Operator dashboards serve **engineers and on-call operators**. Apply these axes:

| Axis | Question | Red flag |
|------|----------|----------|
| **Information density** | Can you diagnose an incident without clicking? | Landing shows ≤3 metrics |
| **Data freshness** | Is stale data labelled? Auto-refresh rates explicit? | Raw ISO timestamps, no "N min ago" |
| **Actionability** | Every status has a matching control (kill, retry, reprompt) | Status-only pages with no actions |
| **Failure surface** | Are error rates, breaker state, queue depth visible? | "0 errored chats" is not a health signal |
| **Auth trust signal** | Does the page show who you are and what scope you hold? | No identity banner |
| **API completeness** | Do `/v1` endpoints exist for everything the UI does? | UI action with no backing API |
| **Consistency** | Same pattern (tile→table→action) across all daemon pages? | Each page invents its own layout |
| **Nav correctness** | Every nav link resolves to 200; no dead links | 404 on nav item = broken |

## Dashboard CEO lens

Operator dashboards create **operator confidence** and **reduce support tickets**. Apply these axes:

| Axis | Question | Red flag |
|------|----------|----------|
| **Time-to-answer** | Can operator answer "is it working?" in <10 sec? | Requires 3+ clicks to find an error |
| **Incident posture** | Does the landing page surface active problems? | No error count, no stuck-agent alert |
| **Onboarding flow** | Can a new operator deploy and verify end-to-end without docs? | Groups exist but invite flow buried |
| **Business visibility** | Are usage metrics (message volume, active users) visible? | Only infra metrics, no tenant metrics |
| **Trust signals** | Does the UI communicate system reliability? | "unknown" status on all 8 daemons |
| **Feature discoverability** | Are all features reachable within 2 clicks from landing? | Features only findable via nav, not tiles |
| **Competitive table stakes** | Status page, audit log, usage graphs — present? | No audit log page, no usage graph |
| **Support deflection** | Can an operator self-diagnose without filing a ticket? | No error detail, no runbook link |

## Rules

- NEVER soften — if something is broken or missing, say so directly
- ALWAYS cite specific files, line numbers, env vars, or spec sections
- ALWAYS distinguish "not shipped" vs "not specced" — both are gaps, different severity
- NEVER recycle a prior critique — re-read source material fresh each time
- For dashboards: ALWAYS include a "Gaps not in any spec" section — unspecced missing table stakes
