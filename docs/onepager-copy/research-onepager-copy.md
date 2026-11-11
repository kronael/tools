# Research: wording and ordering a persuasive, non-misleading money-offer onepager

Corrected after `audit-critique.md` (same directory). The proposed section order at the end is cut: `readme/onepager.md` keeps one order. Section 6 NN/g chart quotes are unverified (audit R6.5, R6.6).

Reader: a middle-class man, sent the link by a friend, knows some trading and games, does not know prop-trading challenges, a few thousand dollars matter.
"WEAK" marks secondary, contested or unread-at-source evidence. Quotes were checked in the fetched source unless marked.

## 1. Plain language for non-experts

- Cut words to about half of conventional text, make it scannable, use objective language: concise +58%, scannable +47%, objective +27%, all three +124% usability vs promotional copy. 79% of users always scan. NN/g, "How Users Read on the Web", https://www.nngroup.com/articles/how-users-read-on-the-web/ (1997 study, small samples; direction repeated since).
- Drop marketese; promotional language "imposes a cognitive burden". Same source.
- One idea per paragraph, conclusion first. Same source.
- Use active voice, direct verbs, present tense; turn hidden verbs back into verbs ("conduct an analysis of" becomes "analyze"). Federal Plain Language Guidelines, https://digital.gov/guides/plain-language/writing
- Split sentences over 25 words; paragraphs at most 5 sentences; "buy" not "purchase"; avoid "-ion"/"-ment" nouns and buzzwords. GOV.UK, https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/
- Explain a specialist term the first time it appears; avoid negative contractions ("can't"), users misread them. GOV.UK, same URL.
- Define acronyms on first use or replace them with a plain term; avoid idioms. Home Office, https://design.homeoffice.gov.uk/accessibility/written-content/readability
- Use defined terms sparingly in the opening and summary; they make readers quit. SEC, A Plain English Handbook (1998), ch. on cover page and summary, https://www.sec.gov/pdf/handbook.pdf (text read via local PDF extraction).
- Explain an abstract idea with a worked example of one person doing actions (the handbook's call-option example with "Mr. Smith"). Same handbook.
- Avoid vague boilerplate, text copied from legal documents, and repeated disclosure. SEC Rule 421(b) note, quoted in the same handbook.
- SEC Rule 421(d) minimum principles for risk-bearing text: active voice, short sentences (about 25-30 words), concrete everyday language, bullets/tables for complex material, no jargon, no multiple negatives. Federal Register 21 Jan 1997, https://www.govinfo.gov/content/pkg/FR-1997-01-21/html/97-1300.htm
- Target a reading age near 9 (UK government convention, "even for specialist audiences", Home Office, URL above). WEAK as a number: it is a convention, and the UK DfE dropped it from its own standard (https://dfedigital.blog.gov.uk/2025/03/19/introducing-the-dfe-plain-language-standard/). Direction holds: higher-literacy readers also prefer plain English (GOV.UK).

Pitfalls: undefined industry words ("challenge", "funded account", "drawdown", "profit split"); passive voice that hides who pays whom; the key condition at the end of a long sentence.

## 2. Page structure and section order

- Put the important points in the first two paragraphs; front-load headings so the first two words carry the gist. NN/g, https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/
- Put top-priority content and the main CTA high: 57% of viewing time above the fold, 74% in the first two screenfuls, 81% in the first three. NN/g, https://www.nngroup.com/articles/scrolling-and-attention/ . So "why is this possible" must sit within the first three screens.
- Order sections by the reader's questions. Schwartz's awareness stages (unaware, problem aware, solution aware, product aware, most aware): the less aware the reader, the more the page must teach before the offer. Eugene Schwartz, Breakthrough Advertising (1966). WEAK: book not read; the stages were confirmed only through secondary summaries (e.g. https://selzee.com/eugene-schwartz-5-levels-of-awareness).
- This reader is solution aware, not product aware (knows people earn from trading, not how buying a challenge works): define the mechanism before the offer details. Inference from the Schwartz model.
- Name the reader's situation first, then the solution briefly, then one ask (AIDA/PAS). Stripe Atlas, https://stripe.com/en-cn/guides/atlas/landing-page-copy (vendor guide, WEAK).
- Add an "ideal for" line near the top; phrase objections as "claim even if objection". Stripe Atlas, same URL; Joanna Wiebe's "even if" via MarketingProfs, https://www.marketingprofs.com/articles/2015/27420/three-deceptively-simple-but-powerful-tips-for-writing-persuasive-landing-page-copy (WEAK, secondary; Copyhackers originals not read).
- Close by restating the offer, the results list and the single CTA. Stripe Atlas, same URL.

Pitfalls: story-first openings; "false floors" where the page looks finished before the key facts (NN/g scrolling article); risk answers only in the last screen.

## 3. Headline and opening

- Be specific; follow the Rule of One (one reader, one idea, one promise, one offer); lead with "you" or a verb. Stripe Atlas, URL above.
- A value proposition states relevance (who it is for), quantified value, differentiation; test: the reader can repeat it to a friend in one or two sentences. Peep Laja, CXL, https://cxl.com/blog/value-proposition-examples-how-to-create/ (403 on fetch; wording via search summary, WEAK).
- Prefer an actual figure to a generality: "Platitudes and generalities roll off the human understanding like water from a duck... Actual figures are not generally discounted." Claude Hopkins, Scientific Advertising (1923), ch. 7 "Being Specific", https://archive.org/download/scientific-advertising/Scientific%20Advertising_djvu.txt
- Superlatives hurt: "They lead readers to discount all the statements that you make." Hopkins, ch. 7.
- Offer service, not "buy my brand"; let the reader test the claim "without any cost or risk". Hopkins, ch. 3 "Offer Service".
- State what he gets, what he pays and what he can lose in the opening block (balanced benefits and risks, section 5).

Pitfalls: a headline with the maximum outcome and no cost; a tagline ("Creativity made easy") that says nothing checkable.

## 4. Persuasion that holds up

- Specific claims are believed because readers do not expect a writer to lie in specifics (Hopkins, ch. 7): a persuasion effect, so the duty to substantiate comes from the disclosure rules in section 5, not from Hopkins.
- Give the reason why: a number plus the mechanism that produces it (Hopkins' "weight of an argument may often be multiplied by making it specific": three and one-third times the light, ch. 7). Reason-why placement: right next to the claim.
- Social proof must be real, attributable and typical. FTC: results claims "should reflect what the typical person to whom the representation is directed is likely to achieve" and top-earner testimonials "likely will be interpreted as representing that their experience is representative". FTC, Business Guidance Concerning Multi-Level Marketing, Q13, https://www.ftc.gov/business-guidance/resources/business-guidance-concerning-multi-level-marketing
- "Results not typical" disclaimers "is not enough"; disclosures must be "clear, prominent, and unavoidable" beside the claim. Same FTC page, Q13.
- Handle objections in the reader's own doubts, in the order he has them (section 2, Wiebe/Stripe; WEAK).
- Cialdini's six principles (reciprocity, commitment, social proof, authority, liking, scarcity) are tools; they turn manipulative when the cue is false. deceptive.design lists the false versions: fake social proof, fake urgency, fake scarcity, confirmshaming, trick wording, hidden costs, sneaking. https://deceptive.design/types
- FTC dark-pattern report groups the harm as false beliefs, hidden material information, and unauthorised charges. FTC staff, "Bringing Dark Patterns to Light" (Sept 2022), https://www.ftc.gov/reports/bringing-dark-patterns-light (categories via law-firm summaries, WEAK).
- No countdowns, "spots left", or "other people joined today" unless true and dated.

Evidence gap: no primary Cialdini text with an explicit ethics rule per principle was reachable (HBR paywalled); the true-cue test above is drawn from the deceptive.design definitions.

## 5. Trust and risk disclosure for money offers

No legal conclusion here: which regime applies depends on jurisdiction and offer. The rules below are borrowed as a published standard for balance. The FCA page cited covers mainstream products; for high-risk investments the FCA also bans "refer a friend" bonuses. Borrow:

- Fair, clear and not misleading; "a balanced impression of the benefits and risks" (COBS 4.5.2R(2)). FCA, https://www.fca.org.uk/firms/risk-warnings-mainstream-investments ; core rule COBS 4.2.1R via search summary (handbook site did not render, WEAK).
- Do not "disguise, diminish or obscure important information or warnings" (COBS 4.5.2R(4)). Same FCA page; it lists "you can't use words like 'but'" as a misunderstanding, not a rule.
- Risks need not come first; order should support understanding. A bare "capital at risk" line is often ineffective in FCA behavioural testing; use contextualised risk statements. Same FCA page.
- FINRA 2210(d)(1): "fair and balanced", no "false, exaggerated, unwarranted, promissory or misleading" claim, "balanced treatment of risks and potential benefits", information in a footnote only if that does not inhibit understanding, no implying past performance will recur. https://www.finra.org/rules-guidance/rulebooks/finra-rules/2210
- SEC Marketing Rule (206(4)-1): no unsubstantiated material claim, no benefits without "fair and balanced treatment of material risks or limitations", no gross performance without net, no cherry-picked periods or subset of results; testimonials and endorsements need disclosure. SEC fact sheet, https://www.sec.gov/newsroom/press-releases/2020-334
- Subtract costs: earnings claims must net out expenses ("must be subtracted from any revenue earned"). FTC MLM guidance Q13, URL above. For this offer: challenge fees and resets are expenses.
- If you lack data on typical outcomes, refrain from earnings claims (FTC MLM Q14). Back claims with evidence; a few exceptional earners do not support a claim for others (FTC, 2026 blog, https://www.ftc.gov/business-guidance/blog/2026/06/back-those-earnings-claims-other-lessons-ftcs-labor-task-force-work).
- Disclose the sender's interest: payment, free product, or family/friend ties that readers would not expect "should be disclosed clearly and conspicuously"; a disclosure only in comments or behind a "LEGAL" link is not enough. FTC, Endorsement Guides Q&A, https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking . Referrers and recruiters can be held liable for their own claims (FTC 2026 blog).
- ESMA/MiFID II: marketing must be identifiable as such and fair, clear, not misleading, with essential characteristics and balanced risks, prominent and accessible. https://www.esma.europa.eu/publications-and-data/interactive-single-rulebook/mifid-ii/article-24-general-principles-and (search summary only, WEAK).
- NN/g trust factors: up-front disclosure of base costs, additional fees, return policy and contact details; accuracy (typos "quickly degrade credibility"); link to third-party sources, users distrust on-site testimonials because they assume only positive ones. https://www.nngroup.com/articles/trustworthy-design/

Pitfalls: a risk section that is accurate but placed where nobody reads; "past results" shown without costs or the number who tried.

## 6. Numbers for laypeople

- Use frequencies, not single-event probabilities: "x out of 100", natural frequencies instead of conditional probabilities. Gigerenzer et al., "Helping Doctors and Patients Make Sense of Health Statistics", Psychological Science in the Public Interest 2007, https://pubmed.ncbi.nlm.nih.gov/26161749/ (abstract read; the 2011 BMJ column notes a conflicting review, so the effect size is debated).
- Prefer absolute figures to relative ones; always name the reference class ("of 100 people who buy a challenge, N get paid"). Same source.
- Show the full chain in currency for the reader's likely stake: cost, probability, payout, expected net. Inference from FTC (expenses netted) and Gigerenzer.
- State the denominator: pass rates vary 17% vs 52% depending on counting accounts or people (press analysis, WEAK: https://daytradingtoolkit.com/psychology-and-risk/prop-firm-challenge-pass-rate-statistics ; industry-wide figures of roughly 5-14% passing are firm-reported and unaudited).
- Charts: people interpret a number by comparing it with another; do not truncate an axis when readers will compare values; "emphasize a finding" is fine, "manipulating a chart" is not. NN/g, https://www.nngroup.com/articles/choosing-chart-types/ and the NN/g chart-honesty piece surfaced in search (https://www.nngroup.com/articles/clutter-charts/; WEAK, secondary summary).
- Test numbers and charts with members of the audience by asking them to summarise. NN/g (same).

Pitfall: a best-case example presented as the example; a percentage with no stake in dollars.

## 7. Explaining an unfamiliar mechanism by analogy

- Use a familiar domain, map the matching parts, then state where the analogy breaks down. Glynn, Duit and Thiele, Teaching with Analogies (1995), steps via https://www.csun.edu/science/books/sourcebook/chapters/10-analogies/teaching-analogies.html (secondary description).
- Analogies mislead when carried too far; good ones answer questions so reliably that people forget the limits. Teaching-analogy research summarised in the Chronicle piece https://www.chronicle.com/article/When-Analogies-Fail/237716 (WEAK, not fetched).
- Game analogy rule (inference): a game analogy ("entry fee, level, prize") hides that the platform is the counterparty and that most entrants lose their fee; say the analogy fails there. Do not let a trading analogy imply the reader's money is invested.
- Prefer a worked example of one person over an abstract definition (SEC Plain English Handbook, call-option example).

## 8. Calls to action and next step for a personal-referral page

- One reader, one offer, one clear action; name the action. Stripe Atlas, URL above, suggests "Get the Sampler" as a rewrite of "Try Now" and cites no data (WEAK).
- Link and button labels say what happens next; avoid "Learn more" and "Click here". NN/g, https://www.nngroup.com/articles/better-link-labels/
- Offer a cost-free or low-commitment first step before a payment (Hopkins, ch. 3, sample "without any cost or risk").
- Disclose who sent the link and what they earn (FTC Endorsement Guides, section 5). Give a real person to contact. NN/g trust article.
- Put the CTA above the fold and repeat it at the end (NN/g scrolling; Stripe Atlas).

## 9. Common pitfalls that cost trust

- Generalities and superlatives (Hopkins ch. 7).
- Best-case results as typical results; disclaimers instead of typical figures (FTC MLM Q13).
- Gross payouts without costs (FTC Q13).
- Warnings placed where readers will not see them (FCA; FTC "clear, prominent, and unavoidable").
- Fake urgency and scarcity, confirmshaming, hidden costs (deceptive.design).
- Undisclosed commission or friendship ties (FTC Endorsement Guides).
- Typos and broken links (NN/g trust).
- Press-reported prop-industry trust gap, unaudited payout figures and "consistency rule" payout disputes: financemagnates.com reports, WEAK trade press, e.g. https://www.financemagnates.com/forex/analysis/hola-prime-brings-in-deloitte-to-audit-payouts-as-trust-gap-widens-across-prop-firms/

## Proposed section order for a money-offer onepager

1. What it is, who it is for, what you get, pay and can lose, in two or three sentences, with one figure. Reader question: "What is this and is it for me?" (NN/g F-pattern, value proposition rule, FCA balance.)
2. Who sent this and what they earn. "Why is a friend sending me this?" (FTC Endorsement Guides, material connection.)
3. How the money flows, in one worked example of one person, with each term defined once. "How does anyone make money from this?" (SEC handbook, GOV.UK, Schwartz solution-aware stage.)
4. Why it is possible and why the number is high, with the mechanism next to the claim. "Why would this pay so much?" (Hopkins reason-why, ch. 7; within first three screens per NN/g.)
5. Typical outcomes in "out of 100" and dollars, net of fees, with the denominator named. "What usually happens to people like me?" (Gigerenzer; FTC Q13/Q14; FINRA 2210; SEC marketing rule.)
6. What you can lose, in the same place and weight as the gain. "What if it goes wrong?" (COBS 4.5.2R, FINRA balanced treatment.)
7. Objections, as questions he would actually ask, answered with "even if". "Is this a scam?" (Wiebe/Stripe, WEAK; NN/g upfront disclosure.)
8. Evidence: independently verifiable sources, testimonials typical and attributed, no counters or timers. (NN/g trust; deceptive.design.)
9. One next step, named, low commitment, with a real contact. (NN/g link labels; Hopkins ch. 3.)
