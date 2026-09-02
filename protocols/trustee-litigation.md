# Protocol: trustee identity and the standard courts actually apply

**Status:** draft
**Pre-registered:** not yet. Commit this file with stages 1 to 5 filled in, and
register it, **before** the first query runs.
**Author:** Kevin D. Klagge, Esq. · ORCID 0009-0002-1385-8498

> This supersedes the scoping in `NEXT-PROJECTS.md` §1. That pass established
> what the corpus holds and killed the original framing. This one establishes
> what the question is, and it is a different question again — because the
> literature had not been read when the sizing was done, and reading it moves
> the target.

---

## 0. What changed, and why

The sizing pass ended at: *"conditioning on litigation needs no population
denominator, because both arms are already inside the courthouse."* True about
the denominator. **Not true about the bias**, and the bias is the reason the
outcome comparison cannot be the headline. See §9.

Reading the literature moved three things:

**There is a live doctrinal debate this measures.** Melanie B. Leslie,
*Common Law, Common Sense: Fiduciary Standards and Trustee Identity*, 27 Cardozo
L. Rev. 2713 (2006), argues that trust statutes should differentiate
**professional from non-professional** trustees, on the ground that settlor
expectations, the negotiating setting and monitoring costs all differ, and that
large institutional trustees have benefited most from statutes that do not
differentiate. Twenty years on, a search found nobody measuring whether courts
differentiate anyway. The corpus can answer that, and answering it lands the
work in an existing argument rather than floating free.

**The statute already differentiates, partially.** UTC §806, enacted in Florida
as **s. 736.0806**: *"A trustee who has special skills or expertise, or is named
trustee in reliance on the trustee's representation that the trustee has special
skills or expertise, shall use those special skills or expertise."* That is a
heightened standard keyed to held-out expertise, and whether courts invoke it is
a fact about published text — visible, countable, and not a function of who
settled.

**Exculpation is the omitted variable, and it is not randomly distributed.**
Adam S. Hofri-Winogradow, *The Demand for Fiduciary Services*, 68 Hastings L.J.
931, 984–85 (2017), surveying 409 professional trust service providers across 82
jurisdictions: **71.1% of trusts carry a trustee exculpatory term**, standard in
professionally serviced trusts, and most settlors get nothing in return. If
corporate trustees win more often, the first explanation is that their
instruments exculpate them. Any outcome comparison that does not code the
exculpatory clause is measuring drafting and calling it conduct.

**And the causal story is probably about money, not trustees.** A corporate
trustee will not take a small trust, so the corporate arm is drawn from the top
of the wealth distribution by construction. Wealth is a common cause of both
hiring a professional and having enough at stake to sue over. `corpus_value` is
therefore a coded variable and not a footnote, and every comparison runs within
value bands. §9 has the full argument and the two further mechanisms — deep
pockets and fee-dispute composition — that point the same way.

### Prior empirical work, and where the gap is

| Work | What it measured | What it did not |
|---|---|---|
| Sitkoff & Schanzenbach, 115 Yale L.J. 356 (2005) | state-year panel of **institutional** trust assets and account sizes from federal bank reports | nothing about litigation |
| Hofri-Winogradow, 68 Hastings L.J. 931 (2017) | terms of trusts they service, from 409 professional providers in 82 jurisdictions plus 25 interviews | outcomes; and it is self-report, not records |
| Weisbord, 53 U.C. Davis L. Rev. 2561 (2020) | **executor** provisions in wills probated in Sussex County NJ, 2015 | trustees; appellate outcomes |
| Horton, 103 Iowa L. Rev. 2027, 2059 (2018) | Alameda County probate: 204 of 368 (55%) litigated claims involved breach of fiduciary duty, objection to, or removal of the personal representative | trustee type |

> **Citation status.** Sitkoff & Schanzenbach, Leslie, Hofri-Winogradow and
> Weisbord verified against the journal or repository copy. **Horton is verified
> only as quoted in Weisbord at 2563 n.9 — the original has not been read**, and
> the figure must not be cited until it has. UTC §806 verified through
> s. 736.0806 and Mass. G.L. c. 203E §806. The UTC exculpation section number
> (§1008) is **not** independently verified; the substance is, via Weisbord at
> 2584 & n.137.
>
> **A search of the obvious sources found no empirical study comparing
> litigation outcomes by trustee type.** That is a search result, not a proof of
> absence, and it is recorded as such per the absence-claim rule in
> `METHODOLOGY.md` §9.

---

## 1. Question

**Primary.** In US state appellate decisions adjudicating a fiduciary-duty claim
against a trustee, does the court invoke a **heightened, expertise-keyed
standard** — UTC §806 or its common-law equivalent — and does that vary with the
trustee's identity?

**Secondary, and reported as exploratory.** Conditional on a claim being
adjudicated, does the remedy imposed differ by trustee identity?

The primary question is first because it is a fact about **what courts wrote**.
The secondary is a fact about **which disputes survived to a published opinion**,
which is a different and much weaker thing. Both are reported. They are never
pooled, and the second never carries the headline.

## 2. Population and corpus

- **Population of interest:** adjudicated fiduciary-duty claims against trustees
  of private donative trusts in the United States.
- **Corpus standing in for it:** CourtListener bulk export, snapshot 2026-06-30,
  topped up nightly, held locally.
- **Court scope:** state appellate only — CourtListener jurisdiction codes `S`
  and `SA`, all 50 states and DC, via `courts-by-state.tsv`. Trial coverage is
  uneven by state and would make any cross-state comparison an artefact of
  ingest. Federal courts are out: ERISA moves the fiduciary vocabulary into a
  statutory regime with its own standard, and bankruptcy trustees are not
  trustees in this sense at all.
- **Date range:** decisions of any date; report the distribution, and check the
  extremes before trusting the date field.
- **Gap between population and corpus:** the corpus holds appealed, published
  disputes. It does not hold trusts administered without incident, disputes
  settled, or trial dispositions not appealed. §9 says what that costs.

**National from the start. There is no pilot state.** The question is about
whether courts differentiate, and courts differ by state, so a single state
cannot answer it — it can only produce one of the fifty-one values. Florida in
particular holds 3 decisions crossing breach of fiduciary duty with "corporate
trustee" and **0** containing "professional trustee", so a Florida pilot measures
nothing at all.

The standing constraint that national phrase queries time out a scoping pass
stays true, and is handled by **sizing on the Florida SSD slice and running
nationally**, not by narrowing the study. Extraction quality is tuned on the
slice because it is fast; every reported number is national.

## 3. Query

Sized 2026-09-02; the counts below are national state appellate, and the script
that produces them is `studies/trustee-litigation/size_pools.py`. Run it before
trusting any figure here — the tables in `NEXT-PROJECTS.md` were produced by
ad-hoc queries that were never committed, which under this repository's own
reporting rules makes them provisional.

```
# Retrieval, deliberately broad. Recall lives in the query; precision in the filter.
("breach of fiduciary duty" OR "breached his fiduciary" OR "breached her fiduciary"
 OR "breached its fiduciary" OR "fiduciary duties" OR surcharge OR "self-dealing"
 OR "duty of loyalty" OR "duty of impartiality" OR "prudent investor")
AND (trustee OR trustees OR "successor trustee" OR "co-trustee")
```

| Pool, national state appellate | Decisions | States |
|---|---:|---:|
| "breach of fiduciary duty" | 31,681 | 51 |
| BFD **and** trustee | **7,061** | 51 |
| "corporate trustee" | 1,142 | 51 |
| "individual trustee" | 462 | 48 |
| "independent trustee" | 261 | 44 |
| "professional trustee" | 135 | 33 |
| "institutional trustee" | 78 | 25 |
| BFD **and** "corporate trustee" | 122 | 37 |
| BFD **and** "professional trustee" | 37 | 15 |

**The primary question has its own lane, and it is a citation lane.** UTC §806's
comment gives the citation family, so the rule is findable in decisions of any
vintage — two of the four forms predate the UTC by four decades:

```
# The special-skills standard, in every form a court states it.
("special skills or expertise" OR "special skills" OR "special facilities"
 OR "greater skill" OR "greater degree of skill" OR "prudent professional"
 OR "prudent professionals" OR "Uniform Prudent Investor"
 OR "professional trustee" OR "corporate fiduciary")
AND (trustee OR trustees)
```

    UTC §806  ==  UPC §7-302  ==  Restatement (2d) Trusts §174 (1959)  ==  UPIA §2(f)

A decision stating the rule in any of these forms is one where the professional
standard was in issue, **stated by the court in its own words with no classifier
in between**.

⚠ **The lane must be the union, and it must be relaxed off the exact statutory
phrase.** Counted nationally across all courts, each form crossed with `trustee`:
the full UTC §806 / UPIA §2(f) phrase *"special skills or expertise"* appears in
**88** opinions; relaxed to *"special skills"* it is **366**; the Restatement (2d)
§174 forms add *"greater skill"* **132** and *"special facilities"* **100**.
**Unioned and crossed with `trustee`: 1,748.** A lane built on §806's exact
wording alone would return almost nothing and read as evidence that courts do not
apply the standard, when it is evidence about how they phrase it. §806's own
comment supplies the equivalence, so unioning the forms is the drafters'
authority, not a liberty.

⚠ **Do not put `7-302` in the query.** A bare number string matches docket
numbers, dates and every other code: 3,898 opinions, almost none of them about
this. Reach the UPC form through its words, not its number.

**This makes the primary question a small-pool study, and that is a feature.**
The unioned lane is **1,748 opinions** nationally across all courts, before the
state-appellate filter and before the donative-trust exclusions — a few hundred
decisions after both. A few hundred decisions is the scale at
which a written codebook, a human second coder and a real Cohen's kappa are
affordable — which is the reliability debt `STATE.md` has carried from the start.
It also makes the name classifier much less load-bearing, because a few hundred
trustees can be identified by reading.

There is also a curated case list to validate against before hand-coding:
**Annot., *Standard of Care Required of Trustee Representing Itself to Have
Expert Knowledge or Skill*, 91 A.L.R.3d 904 (1979)**, cited in the UPIA §2(f)
comment. Obtain it first.

All queries run through `~/caselaw/`, never by opening the corpus directly.

⚠ `NEAR("breach fiduciary duty", 25)` searches for a **three-word phrase** and
returned 16 Florida decisions for the most litigated claim in American law. It
looks correct and is not. Expand into OR'd `NEAR()` calls over quoted phrases.

## 4. Exclusions

Applied in this order. Counts filled as the funnel runs.

| # | Rule | Rationale | N remaining | Dropped |
|---|---|---|---|---|
| 0 | Retrieved on the query above | — |  | — |
| 1 | State appellate only (`S`, `SA`) | trial coverage uneven by state |  |  |
| 2 | Drop **deed-of-trust foreclosure trustees** | in ~30 states the foreclosure "trustee" is a title company holding a security interest, not a fiduciary of anyone |  |  |
| 3 | Drop **securitisation and indenture trustees** | a bank is trustee for a bond issue or an MBS pool, not for a family |  |  |
| 4 | Drop **constructive and resulting trusts** | "constructive trustee" is a remedy, not an office |  |  |
| 4b | Drop **governing boards** — `Board of Trustees`, `Trustees of the Internal Improvement Fund`, regents, governors | a university board is not a fiduciary of anybody's family, and it is entity-shaped, so left in it lands in the corporate arm |  |  |
| 4c | Drop **personal representatives and executors** | a different office under a different article |  |  |
| 5 | Drop **ERISA, union, and pension plan trustees** | different statutory standard; "breach of fiduciary duty" is ERISA's phrase of art |  |  |
| 6 | Drop **business trusts** — voting, liquidating, Massachusetts, QSST | not donative |  |  |
| 7 | Drop where no fiduciary claim was **adjudicated** | a claim recited in the procedural history is not a holding |  |  |
| 8 | Trustee identifiable from caption or first mention | unidentifiable trustee cannot be classified |  |  |

**Exclusion 2 is the largest and the sizing pass missed it.** The pass named the
mortgage-backed-securities trap, which is the Florida-shaped contaminant:
Florida is a judicial-foreclosure, mortgage state, so the noise there arrives as
*a bank suing as trustee for a securitisation trust*. In deed-of-trust states —
California, Texas, Virginia and Colorado among them — **a non-judicial
foreclosure has a "trustee" by statute**, and that pool is plausibly larger.
How many states and how much larger is not asserted here; `size_pools.py`
reports it per state, which is the only honest way to hold the claim. A national study scoped on a Florida intuition about what the noise is
will import that noise wholesale. Size exclusion 2 per state before running.

**Exclusion 4b was found by reading output, and it is not small.** On a random
256-decision Florida sample, **17%** of the pool was not about a donative trust
at all, and governing boards were the largest group — *University of Florida
Board of Trustees* sits in the raw pool. See
`studies/trustee-litigation/CLASSIFIER-NOTES.md` §4.

Each exclusion is a rule with a count, and each is reported whether or not it
flatters the study.

## 5. Codebook

The sizing pass proposed one classifier. **There are two variables here and they
are not the same axis**, which is the error the sizing pass was about to bake in.

A **professional trustee can be a natural person** — a lawyer, an accountant, a
licensed private fiduciary — paid, holding out expertise, squarely inside UTC
§806. A **corporate trustee is an entity**. A name-based classifier detects
*entity versus natural person*. It does **not** detect *professional versus lay*.
So training a name classifier against the courts' 135 "professional trustee" and
462 "individual trustee" labels trains it to predict the wrong variable, and
every paid individual fiduciary becomes a false negative that is not an error.

| Variable | Values | Decision rule for hard cases |
|---|---|---|
| `trustee_form` | entity \| natural_person \| both (co-trustees) \| unclear | entity on `Bank`, `N.A.`, `Trust Co`, `Corp`, `LLC`, `Association`, `& Co`; natural person on a personal name. Co-trustees of mixed form code `both` and are analysed separately, never assigned to an arm |
| `trustee_capacity` | professional \| amateur \| unclear | the drafters' own pair, from the UPIA §2(f) comment. `professional` where the opinion shows compensation for fiduciary service, held-out expertise, or a licence; a family member serving without fee is `amateur`. Where the opinion is silent, `unclear` — **never inferred from form** |
| `configuration` | entity \| amateur_person \| professional_person \| mixed_cotrustee \| delegated \| family_trust_co | the six ways form and capacity combine. `mixed_cotrustee` is not an edge case: UTC §703 cmt calls an institution-plus-family-member pairing the standard reason to appoint cotrustees. `delegated` is an amateur trustee who hired a professional under §807 |
| `standard_invoked` | special_skills \| ordinary_prudence \| both \| none | `special_skills` where the opinion cites UTC §806 or its state enactment, or states a higher duty owed by reason of expertise, professional status, or compensation. This is the primary outcome |
| `exculpatory_clause` | present_enforced \| present_rejected \| present_unresolved \| absent \| unstated | from the opinion's own account of the instrument. `unstated` is the modal value and must be reported, not dropped |
| `corpus_value` | dollar figure \| band \| unstated | the amount the opinion says is in the trust or in dispute. **The confounder that matters most** — see §9. Bands, because opinions state values inconsistently: <$500k, $500k–2M, $2M–10M, >$10M |
| `trustee_compensated` | yes \| no \| unstated | a fee-charging trustee generates fee litigation an unpaid family trustee never does |
| `remedy_sought` | surcharge \| removal \| fees \| accounting \| other, multi-select | **exposure**. Coded whether or not granted |
| `remedy_granted` | granted \| denied \| partial \| remanded | **risk**, conditional on sought |
| `appellate_posture` | affirmed \| reversed \| mixed | who appealed, and what happened to them |
| `appellant` | trustee \| beneficiary \| other | the differential-appeal check; see §9 |

**Report three numbers, never one** — exposure, risk, and survival — as
established for the disputed-terms study in `METHODOLOGY.md` §9. The sizing
pass listed four bare outcome variables with no exposure term and no covariate,
which would have reproduced the error that section exists to prevent.

⚠ **Drop "attorney fees assessed against the trustee *personally*".** It was on
the sizing pass's list and it is not commensurable across arms: "personally" is
close to meaningless for a bank, which pays from corporate funds either way,
while personal exposure is the entire fight for an individual trustee. Coding it
produces a difference that is an artefact of the word. Code `fees` as sought and
granted, and say who bore them, without the personal/entity split.

**Identify the trustee by ROLE SLOT, not by proximity.** Measured on 256 Florida
decisions: an entity marker anywhere in the opinion calls 95% of them corporate;
within ±50 words, 70%; ±25, 57%; ±10, 36%. The numbers decline smoothly with the
window and never plateau, which means proximity measures how many entity words
the opinion contains, not who the trustee was. Cue-anchored extraction of the
trustee slot — `X, as trustee of the Y Trust`, `the trustee, X,`, `appointed X as
trustee` — returns the filler directly. Resolve mentions to a **party** before
classifying, because mention-level classification truncates `Barnett Banks Trust
Co., NA` to `Barnett` and scores it a natural person. Full workings in
`studies/trustee-litigation/CLASSIFIER-NOTES.md` §4.

⚠ **A decision usually names more than one trustee.** *Holley v. First Guaranty
Bank & Trust Co.* (Fla. 1st DCA 1997) names **First Guaranty Bank** as the acting
trustee that moved for surcharge, and **Paine Webber Trust Company of
Jacksonville** as the successor trustee the instrument designated in case of
incompetency. The slot extractor pulled the second. Both are entities here so the
arm survives, but in a mixed case it would not. The extractor has to pick the
trustee **whose conduct is at issue**, and separate it from predecessors,
designated successors who never served, and trustees of other trusts in the same
opinion. Rank slot fillers by proximity to the breach language, and code
`n_trustees_named` so the ambiguous decisions are visible rather than silently
resolved.

**Ground truth for `trustee_form` comes from a hand-coded random sample of the
7,061**, not from the courts' labels. The labelled decisions are not a random
sample: a court writes "professional trustee" precisely when trustee type is
legally in issue, which is the subpopulation where the standard is contested.
They are a useful **supplementary check** and a good source of hard cases. They
are not the validation set, and the sizing pass's neat line — that the label
problem becomes the training set — is the thing to resist.

**Reliability plan:** `standard_invoked` is the primary outcome and the only
variable the headline depends on. Double-code **100 randomly drawn decisions**
and report Cohen's kappa before any rate is published. `trustee_form` gets
precision and recall against 100 hand-coded captions. Below kappa 0.7 the study
reports counts and is labelled exploratory.

**Coder:** deterministic rules for retrieval and for the name-pattern first
pass; a named model with a committed prompt for `trustee_capacity`,
`standard_invoked` and `exculpatory_clause`; a human second coder on both
reliability samples. Model-coded results are never described as mechanical.

---
<!-- Everything below is filled in AFTER the analysis runs. -->

## 6. Denominator

**The primary question needs none.** `standard_invoked` is a proportion of
adjudicated decisions, and the denominator is the decisions themselves.

**The secondary question needs one it cannot fully have, and one arm of it is
available.** Federal bank Call Report **Schedule RC-T, item 4** — personal trust
and agency accounts — reports the **number of accounts** and market value for
testamentary trusts and revocable and irrevocable living trusts, per
institution, per quarter. Sitkoff & Schanzenbach built a state-year panel from
exactly this source. So a **corporate-arm incidence rate** — suits per thousand
bank-held personal trust accounts, by state-year — is computable, and it is
better than the "crude rate and nothing finer" the sizing pass assumed.

There is no register of individual trustees, so the individual arm has no
denominator and never will. **Report the corporate rate alone, labelled as one
arm, and never divide the two.** A ratio of a rate to a count is not a
comparison.

## 7. Results

To be completed.

## 8. Interpretation

To be completed. Findings and hypotheses stay visibly separate.

## 9. Limitations

### Trustee type is a proxy for money, and money is the likelier cause

The framing this study inherited — professional trustees change litigation risk —
assumes the trustee is doing the causing. **Wealth is a common cause of both**,
and it explains the same association without any claim about trustee conduct:

    settlor wealth ──→ hires a professional trustee
           │
           └────────→ larger corpus ──→ more worth fighting over ──→ litigation

A corporate trustee does not take a $180,000 trust; published fee schedules and
account minima see to that. So the corporate arm is drawn from the top of the
wealth distribution by construction, and the individual arm from everywhere. Any
raw difference between the arms is a difference in trust size before it is
anything else.

Two further mechanisms push the same way, and neither involves misconduct:

**Deep pockets.** Beneficiaries sue defendants who can pay. A bank is solvent,
insured and reachable; an individual trustee who is also a beneficiary may be
judgment-proof, and suing them may cost more than it returns. Corporate trustees
attract suits *because they are collectible*.

**Category composition.** A trustee who charges a fee generates fee litigation.
An unpaid family trustee generates none. Some portion of any excess in the
corporate arm is a category that simply does not exist in the other arm —
nationally, `fee schedule` crossed with `trustee` is 1,232 opinions and
`termination fee` 1,435.

**What to do about it.** Code `corpus_value` and compare **within value bands**.
Where the opinion gives no figure, say so and report the unstated share on the
face of every table rather than dropping those decisions. Report the remedy mix
by arm before reporting any rate, so a composition difference is visible as a
composition difference.

**And say plainly what a null result would mean, because it is the likely one and
it is useful.** If the trustee-type difference disappears inside value bands, the
finding is *"trust size predicts litigation; trustee type does not"* — which
answers the client's real question better than the original framing did. It says
choosing a corporate trustee does not buy you a lawsuit, and having a large trust
does. That is a publishable result and a saleable one, and the design has to be
able to reach it.

### Conditioning on litigation relocates the selection effect; it does not remove it

This is the largest threat and the sizing pass did not see it. Its reasoning was
that comparing outcomes needs no population denominator "because both arms are
already inside the courthouse." The denominator problem does go away. **The
selection problem changes form and gets worse**, because the two arms are
selected into the corpus by different processes.

Priest & Klein, 13 J. Legal Stud. 1 (1984): litigated cases cluster around
genuine uncertainty and do not represent disputes generally. Apply it here.
A corporate trustee is a **repeat player** — insured, with in-house counsel, a
reputational stake across every other account it holds, and a settlement budget.
An individual trustee is a **one-shot player**, often a family member, often
paying counsel personally, frequently unable to fund an appeal at all. Those two
populations settle at different rates, appeal at different rates, and publish at
different rates.

So a measured difference in remedies between arms is consistent with:

1. corporate trustees behaving better, or
2. corporate trustees settling the cases they would have lost, or
3. individual trustees being unable to appeal the losses they suffered, or
4. corporate instruments exculpating more, per Hofri-Winogradow, or
5. any combination.

Nothing in the corpus separates these. **The outcome comparison therefore
reports an association and states all five readings**, and it is not the
headline. Two partial checks are available and both are cheap: report `appellant`
composition by arm, since differential appeal shows up there and not in the
first-instance outcome; and report affirmance separately from remedy, since a
selection story predicts a difference in one and not the other.

### The rest

- **Corpus coverage:** uneven digitisation across decades and courts. Any trend
  is a rate against the same courts in the same years, never a raw count.
- **Query validity:** "trustee" names at least seven offices, four of them
  nothing to do with donative trusts. Exclusions 2 to 6 are the study; their
  counts are reported.
- **The classifier is the load-bearing step.** `trustee_form` is applied to
  7,061 decisions on the strength of 100 hand-coded ones. It ships with measured
  precision and recall or the study does not ship.
- **`trustee_capacity` will be `unclear` often**, because opinions do not
  routinely say whether a trustee was paid. Report the `unclear` share on the
  face of every table. If it exceeds roughly a third, capacity is not a usable
  variable and the study reports form alone and says so.
- **Coding:** see the reliability plan. Single-coded means exploratory.

## 10. Data availability

Derived CSV published under CC BY 4.0 with a DOI, described in Frictionless,
schema.org and Croissant form alongside, every row carrying a `statement` field.
