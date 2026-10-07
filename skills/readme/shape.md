# Doc shape

`topology.md` splits a project across *files* — README vs ARCHITECTURE vs
`notes/`. This file is the orthogonal axis: the order and grouping of *sections
inside one file* that an external integrator reads end to end — an
`INTEGRATE.md`, a guide page, an endpoint-reference page. Diátaxis names the
four needs (tutorial, how-to, reference, explanation —
[diataxis.fr](https://diataxis.fr)) but states no page-level ordering rule; the
shape below is what real API docs actually do with that framework on one page.

## The two shapes that recur

Diátaxis's tutorial and how-to collapse into one "guide" mode in practice — no
sampled source kept them apart on a page. Guide pages and reference pages each
converge on a shape:

| Mode | Opens with | Body | Closes with |
|---|---|---|---|
| **Guide** (tutorial+how-to) | one-line purpose, no conceptual preamble | prerequisites folded into step 1, never their own section → sequenced steps, each short prose + code → parameter detail linked out, not inlined | a verify/test step, then clearly labeled `Optional:` extensions, then see-also |
| **Reference** | title + one-line description | the field/parameter list as the structural spine | errors, scoped to the one operation — never pooled into a global appendix |

Guide precedent: Stripe's accept-a-payment page, Twilio's SMS quickstart,
Plaid's Link overview. Reference precedent: Stripe's PaymentIntent object page,
Twilio's Message resource, Solana's `getBalance`, GitHub's Issues endpoint,
Cloudflare's DNS-record endpoint, AWS's `GetObject`.

## The rule underneath both: front-load the common, scope the conditional

What explains both shapes at once: ALWAYS put first whatever is true for *every*
reader — title, one-line purpose, the one happy-path artifact. Push whatever
only applies to *some* readers — errors, edge-case params, alternate paths —
later, and scope it to the exact step or operation that triggers it. NEVER hoist
conditional material into one global section a reader must cross regardless of
whether it applies to them; that is what turns a doc with plenty of good
sections into one no reader can skim.

## When one file must hold guide + reference + explanation

Most sampled sources fork guide and reference onto separate pages (Cloudflare,
Stripe, Twilio). When there's no second file to fork to — one `INTEGRATE.md`,
one endpoint page — two sources blend deliberately instead of splitting: AWS's
`GetObject` opens a pure-reference page with several paragraphs of concept
before the parameter tables; Plaid's Link overview interleaves "how it works"
narrative with the actual API calls, step by step. Follow their precedent, not
the separation doctrine, when a split file genuinely isn't an option — but keep
the front-load/scope rule above: concept every integrator needs comes before the
spine; concept that only explains one branch stays next to that branch, not
hoisted to the top.

## Multiple strategies for one task, on one page

The case none of the sampled guide pages tested directly, and the most likely
reason to open this file: a page documenting several alternative routes to the
same outcome — multiple providers, multiple auth methods, multiple strategies
for one task. Extrapolate from the closest precedents — Stripe forks a full page
per integration path, Twilio repeats one H3 per language under the same task
heading:

- ONE shared overview first — why the alternatives exist, how a reader picks one
  — before any per-strategy detail.
- Per-strategy blocks repeat the *same* shape and heading pattern in the same
  order (request → response → errors) so a reader finds their one strategy and
  never has to read the others to find the parallel section.
- NEVER interleave strategy A's how-to with strategy B's rationale — same shape
  repeated is itself the signpost; prose that wanders between strategies defeats
  it.

## Errors: the one clean convergent rule

Every source that documents errors at all scopes them to the operation that
produces them — GitHub's per-endpoint status table, AWS's per-operation Errors
heading, Mintlify's stated rule (success example, then the errors a reader will
actually hit, right after it), Plaid's Link overview folding error handling into
the step it belongs to. NEVER pool errors into one appendix spanning the whole
document — no sampled source does this, and it forces every reader through
failure cases that don't apply to their call.

## Signposting which mode a paragraph is in

No sampled source used tabs or colored panels to mark guide-vs-reference — tabs
everywhere were for *language* choice, never *mode*. Mode is signposted by
page-forking (Stripe, Cloudflare) or by heading language: Google's developer
documentation style guide states task headings as bare infinitives ("Configure
notebook settings") and conceptual ones as noun phrases ("ML model monitoring
overview"). Inside one file with no page to fork to, that heading convention is
what's left — ALWAYS name the mode in the heading itself (infinitive = do this
now; noun phrase = here's the field list, or here's why), and NEVER let guide
prose and reference tables interleave paragraph-by-paragraph inside one
subsection.

## Table of contents

No shared mechanism — Cloudflare's guide has an on-page "On this page" widget,
Solana disables its TOC outright (`hideTableOfContents: true`), GitHub and AWS
lean on a persistent side-nav, Stripe uses a query-string expand mechanism
instead of a list. Every source that skips a TOC has a persistent site nav
standing in for one. A bare integration doc read outside such a site — one
`INTEGRATE.md`, no side-nav — has nothing standing in for it: ALWAYS default to
an on-page anchor list at the top.

## Where sources flatly disagree

- **Example before or after the parameter table — a real three-way split, not
  one rule.** Stripe, Solana, and Google's style guide put the worked example
  *before* the field list; Twilio, GitHub, and Plaid put parameters first,
  example after; AWS puts the example *last of all*, after even the errors
  section. What predicts which: a single simple call with few params reads fine
  example-first (Solana); one param table shared by several sibling operations —
  CRUD on one resource — reads better params-first, since one example can't
  represent the whole family (Twilio, GitHub); an operation complex enough that
  the example is unreadable without the mechanism first earns example-last
  (AWS). ALWAYS pick by that variable — NEVER default to one camp because a
  source you liked used it.
- **Separate pages vs one blended page.** Divio's original doctrine argues the
  four modes actively resist blending and must stay apart, or the structure
  collapses; AWS and Plaid blend anyway on pages that can't fork to a second
  file. Both are right for their constraint — the live question is whether a
  second file is available, not which doctrine wins in the abstract.
- **Auth/prerequisite placement.** GitHub repeats auth headers at the top of
  every resource page; Twilio makes account setup an explicit early step; Stripe
  reduces it to one line inside step one. Match the size of the prerequisite to
  how it's placed — a header value repeats near the call it authorizes; a
  one-time account-setup step earns its own step.

## Example and recipe pages

A page holding one complete, runnable example answers the reader's questions
in the order they come — can I trust it, what does it cost, what does it do,
what do I copy, how do I run it, what was proven. ALWAYS this order. Status
and Cost are the two opening lines. The rest are headings, named the same on
every example page:

1. Status — where it ran (local simulator, devnet, mainnet) and where not.
2. Cost — the measured figure from the tested run, naming the test
   (`sync.md` § Rules).
3. What it does — one sentence, then each check the code makes, named by
   the label it carries in the code (`swapPaysTheBorrower`), so an error
   message leads straight to the line.
4. Template — the code to copy, from a compiled file (`sync.md` § Rules).
5. Run it — the code that runs it.
6. What has been tested — the test file, each failure case it runs and the
   check it fails at. ALWAYS list what is not tested whenever anything is;
   NEVER leave a gap unstated: it reads as proven.

## Out of scope

Every guide and reference source sampled here is a REST or JSON-RPC
single-resource or single-flow document; the example-page order comes from one
SDK doc site. An SDK doc site's layout — guide groups, one reference page per
language — is `topology.md` § A doc site splits into guide and reference.
Webhook-driven APIs and GraphQL schemas were not sampled. NEVER extend these
rules to those shapes unchecked — ALWAYS check a real example of that kind
first.

---

*Source: live-fetched 2026-09-18 from Diátaxis (diataxis.fr) and the Divio
precursor (docs.divio.com); Stripe (docs.stripe.com — accept-a-payment guide,
PaymentIntent object reference); Twilio (SMS quickstart, Message resource
reference); Plaid (Link overview, `linkTokenCreate`); Solana (`getBalance` RPC
reference); GitHub REST (Issues endpoint); Cloudflare (DNS-record endpoint,
get-started guide, concepts page); Mintlify's published API-documentation
guidance; Google's developer documentation style guide; AWS's S3 `GetObject`
reference. Example-page order and the doc-site layout: the ballista.sh VitePress
source, read 2026-10-07.*
