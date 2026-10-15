# CEO Eval Checklist

Business-value evaluation of a technology or project. Assess whether adoption creates value, what it costs, and what risks it carries at the organizational level.

**Dimensions:** ROI · TCO · vendor lock-in · license risk · strategic fit · community health · make vs buy · risk profile

## 1. License Analysis

**Run this first — it is a hard blocker.**

| License | Commercial use | Modify & keep private | Embed in proprietary product |
|---------|---------------|----------------------|------------------------------|
| MIT / Apache-2.0 | ✅ | ✅ | ✅ |
| BSD-2/3 | ✅ | ✅ | ✅ |
| LGPL-2.1/3 | ✅ | ✅ | ✅ (dynamic link only) |
| GPL-2/3 | ✅ | ❌ must open source | ❌ must open source entire product |
| AGPL-3 | ✅ | ❌ must open source | ❌ includes SaaS usage |
| SSPL | ✅ (not as a service) | restricted | ❌ SaaS → open source entire stack |
| BSL (Busl) | ✅ up to limit | restricted | restricted |
| Proprietary | depends | ❌ | ❌ |
| No license | ❌ | ❌ | ❌ (copyright default) |

**Action if GPL/AGPL/SSPL:** (a) internal use only with no distribution, (b) fork and relicense if possible, or (c) do not adopt.

**Relicensing risk:** the LICENSE file is only as durable as the copyright owner. Single-vendor projects with a CLA can and do relicense (Terraform → BSL 2023, OpenTofu fork; Redis → SSPL 2024, Valkey fork); foundation-owned projects (Apache, CNCF, LF) effectively cannot. Check who owns the copyright, not just what the license says today.

## 2. Vendor & Dependency Lock-in

- Is this tool locked to a single cloud provider / paid service?
- If the upstream project disappears tomorrow, how long until we're broken?
- Is the protocol/API an open standard or proprietary?

```
              | Protocol open? | Alt implementations? | Self-hostable?
Ideal         |      ✅        |         ✅           |      ✅
Acceptable    |      ✅        |         ❌           |      ✅
Risky         |      ❌        |         ❌           |      ✅
Dangerous     |      ❌        |         ❌           |      ❌
```

**Red flag:** Vendor-only API + proprietary protocol + no alternative.

**Price the exit at entry** (switching costs — Shapiro & Varian): estimate cost-to-leave as a number before adopting — data export, protocol rewrite, retraining, parallel-run period. If it can't be estimated, that IS the finding.

## 3. Total Cost of Ownership (TCO) — 2-year estimate

| Cost Item | Estimate |
|-----------|---------|
| Integration time (hours × rate) | |
| Ongoing maintenance (patches, upgrades) | |
| Incident response when it breaks | |
| Training / onboarding | |
| Licensing / subscription fees | |
| Infrastructure (if self-hosted) | |
| Cost of NOT having this (lost productivity) | |

**Rule of thumb:** "Free" OSS requiring 2 engineers × 3 months = $200K+ TCO before first value.

**Acquisition is the small slice.** Run-rate dominates multi-year TCO: upgrades, incident response, security patches, and the salary share of whoever understands it. Price year 2, not day 1.

## 4. Time-to-Value

- How long from "decide to adopt" to "first production value"?
- Is there a working demo/binary runnable in < 30 minutes?
- Are there known adopters in production with similar use cases?
- If uncertain → pilot. A pilot is a purchased option: fixed budget, success metric, kill criteria, and decision date set BEFORE it starts — otherwise sunk cost converts it into adoption by drift.

## 5. Community & Support Health

```sh
gh repo view <org>/<repo> --json stargazerCount,forkCount,openIssues,updatedAt
```

| Metric | Healthy | Concerning |
|--------|---------|-----------|
| Last commit | < 3 months | > 1 year |
| Issue response | < 1 week | > 1 month or none |
| Contributors | > 3 active | 1 person (bus factor) |
| Security patches | Prompt | Ignored |
| Releases | Regular | None in 1+ year |

**Bus factor 1 = high risk.** Stars are vanity — weigh issue-close rate, release cadence, and maintainer diversity (contributors from ≥ 2 orgs). All maintainers from one vendor = a vendor project in OSS clothing (see relicensing risk, §1).

## 6. Strategic Fit

- Core vs context (Geoffrey Moore): core = what customers choose you for; everything else is context. Is this tool core or context for us? Build only core; buy/adopt context.
- Does it introduce a new language/runtime outside our stack?
- Are competitors already using this? (de-risking signal)
- Does it align with our 3-year architecture direction?

## 7. Risk Profile

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Upstream breaks API | | | Fork / pin version |
| Maintainer abandons | | | Evaluate fork cost |
| Security CVE | | | Track advisories |
| License change | | | Audit on each major version |
| Vendor raises prices | | | Self-host option? |

## 8. Make vs Buy

```
1. Is this core to our competitive advantage?
   YES → consider building   NO → prefer OSS/SaaS

2. Does an OSS solution solve 80%+ of our need?
   YES → adopt, live with the 20%   NO → build the delta only

3. Build cost vs adopt cost?
   Build < adopt×2 → consider building   else → adopt and contribute upstream

4. Can we afford to maintain this forever?
   NO → do not build
```

**Most common mistake:** Building what already exists because "it doesn't do exactly what we want."

**Second most common:** pricing "build" as build cost only. Building means owning a product with one customer forever — maintenance is the dominant term.

## Verdict Template

```
## CEO Eval: <project> v<version>

**Verdict:** ADOPT / ADOPT WITH CONSTRAINTS / PILOT / DO NOT ADOPT

**Business case:** [1-2 sentence ROI justification]

**License:** [permissive / copyleft + implication / proprietary]

**Lock-in risk:** [low / medium / high] — [why]

**TCO estimate (2yr):** [rough number or range]

**Time-to-value:** [X days/weeks]

### Conditions
- ...

### Risks to monitor
- ...

### Recommendation
[Plain English — a non-technical stakeholder must be able to act on this]
```

| Verdict | Meaning |
|---------|---------|
| **ADOPT** | Clear positive ROI, manageable risk, good strategic fit |
| **ADOPT WITH CONSTRAINTS** | Good ROI but specific license/lock-in conditions to satisfy first |
| **PILOT** | Uncertain ROI; time-boxed pilot (e.g. 30 days) with success metric + kill criteria fixed before start |
| **DO NOT ADOPT** | Negative ROI, unacceptable license risk, or anti-strategic |
