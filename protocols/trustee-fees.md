# Protocol: trustee compensation, and when a court takes it back

**Status:** draft — stages 1 to 5 fixed before the analysis runs
**Pre-registered:** this commit
**Author:** Kevin D. Klagge, Esq. · ORCID 0009-0002-1385-8498

> Committed with stages 1 through 5 filled in and **before** the analysis runs.
> The three studies already in this repository were not preregistered and are
> labelled exploratory. This one is, which is the only condition under which
> preregistration means anything.

---

## 0. Why this one, and why it is cleaner than the trustee-type study

`protocols/trustee-litigation.md` compares corporate against individual trustees
and spends most of its length on why that comparison is hard: the arms are
selected differently, wealth confounds them, and the labels courts use are
asymmetric.

**Fee litigation has no arm problem.** The unit is a challenge to a trustee's
compensation, both sides of the dispute are inside one case, and the outcome —
was the fee cut — is a fact about that case rather than a rate needing an outside
denominator. It also has a statutory hook that says what the court is supposed to
do, which most questions in this corpus do not.

**UTC §708.** Compensation must be "reasonable under the circumstances"; where the
terms of the trust specify it, the court may allow more or less if the duties
turned out substantially different, or if the specified figure is "unreasonably
low or high". The comment adds two rules with teeth, and both are testable:

- **a downward adjustment "may be appropriate if a trustee has delegated
  significant duties to agents"** — so delegation should predict reduction;
- **"a trustee with special skills… may be entitled to extra compensation"** — the
  §806 expertise standard reappearing on the credit side of the ledger.

And on the institutional side: *"Financial institution trustees normally base
their fees on **published fee schedules**. Published fee schedules are subject to
the same standard of reasonableness… The courts have generally upheld published
fee schedules but this is not automatic. Among the more litigated topics is the
issue of **termination fees**."*

That paragraph is a set of empirical claims by the drafters — *generally upheld*,
*not automatic*, *termination fees are among the more litigated* — and none of
them has ever been checked. Checking them is the study.

## 1. Question

When a trustee's compensation is challenged, how often does the court reduce it,
and does the outcome differ by how the fee was set — a published schedule, a
percentage, an hourly rate, or a figure named in the instrument?

**Secondary:** do the two adjustments UTC §708's comment predicts actually appear
— fees reduced where the trustee delegated, fees enhanced where the trustee had
special skills?

## 2. Population and corpus

- **Population of interest:** adjudicated challenges to the compensation of a
  trustee of a private donative trust in the United States.
- **Corpus:** CourtListener bulk export, snapshot 2026-06-30, topped up nightly.
- **Court scope:** state appellate only, jurisdiction codes `S` and `SA`, all 50
  states and DC, via `courts-by-state.tsv`.
- **Date range:** any; report the distribution and check the extremes.
- **National, not Florida.** Florida holds **35** decisions in this lane, which is
  not a study. Extraction is tuned on the Florida SSD slice because it is fast;
  every reported number is national.
- **Gap between population and corpus:** a fee dispute reaches an appellate
  opinion only if somebody funded an appeal over a fee. Small fees are
  systematically absent, which biases the sample toward large trusts. §9.

## 3. Query

⚠ **Two words, not one, and the difference is regional.** Eastern states call
fiduciary compensation **commissions** (NY SCPA 2309); most others call it
**fees**. A lane built on either word alone measures a region and calls it a
country. Both go in, and the ratio is reported per state as a finding in its own
right.

```
# Trustee compensation, both vocabularies.
"trustee's compensation" OR "trustees' compensation" OR "trustee compensation"
 OR "trustee's fee"      OR "trustee's fees"   OR "trustees' fees"  OR "trustee fees"
 OR "trustee's commission" OR "trustee's commissions" OR "trustees' commissions"
 OR "trustee commissions"
```

Sized 2026-09-02 by `studies/trustee-fees/size_lanes.py`. Opinions, not
decisions — this is lane triage, not the funnel.

| Lane | National | Florida |
|---|---:|---:|
| `trustee's fee(s)` | **3,999** | 145 |
| `trustee's commission(s)` | **1,429** | **15** |
| `trustee's compensation` | 1,377 | 34 |
| `reasonable compensation` ∧ trustee | 8,438 | 220 |
| `excessive fees/compensation` ∧ trustee | 1,956 | 90 |
| `fee schedule` ∧ trustee | 1,232 | 55 |
| `extraordinary services` ∧ trustee | 671 | 20 |
| `double compensation` ∧ trustee | 404 | 6 |
| `termination fee` ∧ trustee | 313 | 4 |
| `published fee schedule` | 50 | 5 |

**The regional split is confirmed and it is large.** Florida holds 3.6% of the
national `trustee's fee(s)` pool but only **1.0%** of the `trustee's
commission(s)` pool — under-represented in the commissions vocabulary by roughly
three and a half times. A study built on either word alone would have measured a
region. Both go in, and the per-state ratio is reported as a finding.

⚠ **One lane was not sized nationally.** `attorney's fees` ∧ trustee was still
running after eighteen minutes and was killed because it was blocking the study
itself. The Florida ratio stands as the evidence for exclusion 2 — **2,849
against 145, roughly twenty to one** — and the national figure is outstanding.
Recorded rather than quietly omitted.

## 4. Exclusions

Applied in this order. Counts filled as the funnel runs.

| # | Rule | Rationale | N remaining | Dropped |
|---|---|---|---|---|
| 0 | Retrieved on the compensation lane | — |  | — |
| 1 | State appellate only (`S`, `SA`) | trial coverage uneven by state |  |  |
| 2 | Drop **attorney's fees paid from the trust** unless the trustee's own compensation is also at issue | fee-shifting is a different doctrine and it is roughly twenty times the size — 2,849 against 145 in Florida. Left in, this study measures fee-shifting and calls it trustee compensation |  |  |
| 3 | Drop **surplus trustees** in foreclosure | a statutory disbursement fee, not fiduciary compensation. Found in the Florida sample |  |  |
| 4 | Drop **indenture and bond trustees** | "trustee fees" in a payment waterfall is a contract term |  |  |
| 5 | Drop **governing boards** — `Board of Trustees`, regents, governors | 68,284 opinions nationally |  |  |
| 6 | Drop **eminent domain "trustees"** | *Dade County v. Midic Realty* awards "the trustees compensation and severance damages" — property owners, not fiduciaries |  |  |
| 7 | Drop **brokerage and sale commissions** styled "trustee's fee" | a 1937 Florida case sets a "trustee's fee of ten per cent of the sales price". Not fiduciary compensation |  |  |
| 8 | Drop ERISA, pension and bankruptcy trustees | different regimes |  |  |
| 9 | Compensation actually **adjudicated**, not merely recited | a fee mentioned in the procedural history is not a holding |  |  |

Exclusion 2 is the one that decides whether this study is about what it says it
is about. It is the same shape as the ambiguity trap in `METHODOLOGY.md` §3:
a word that two doctrines share, separated only by what the court was deciding.

## 5. Codebook

| Variable | Values | Decision rule for hard cases |
|---|---|---|
| `fee_basis` | published_schedule \| percentage \| hourly \| instrument_specified \| statutory \| unstated | how the challenged fee was computed. `unstated` is expected to be common and is reported, never dropped |
| `challenge_outcome` | reduced \| disallowed \| upheld \| increased \| remanded \| mixed | **the primary outcome.** `remanded` is not `reduced`: a remand decides nothing |
| `amount_before` / `amount_after` | dollars \| unstated | only where the opinion states both. Expected to be a minority — 11% of Florida fee sentences carry a dollar figure |
| `trustee_form` | entity \| natural_person \| both \| unclear | as in `protocols/trustee-litigation.md`; identified by **role slot**, not proximity |
| `delegated` | yes \| no \| unstated | UTC §708 cmt predicts a downward adjustment. Delegation vocabulary from §807 / UPIA §9 |
| `special_skills_claimed` | yes \| no | §708 cmt predicts extra compensation. Ties this study to the §806 lane |
| `termination_fee` | at_issue \| not_at_issue | the drafters call it "among the more litigated topics". Cheap to check |
| `cotrustees` | yes \| no | §708 cmt: more trustees does not mean more total compensation |
| `self_dealing_alleged` | yes \| no | a trustee who paid himself without authority is a different case from a fee thought too high, and pooling them would be the "never pool measures that point in opposite directions" error |

**Report three numbers, never one** — how often compensation was challenged, how
often it was cut when challenged, and how often it was upheld. The third is what
a trustee wants to know and the first is what a beneficiary wants to know.

**Reliability plan:** `challenge_outcome` is the primary outcome. Double-code
**100 randomly drawn decisions** and report Cohen's kappa before any rate is
published. Below 0.7 the study reports counts and is labelled exploratory.

⚠ **Outcome coding will not be mechanical, and the sizing says so in advance.**
On a Florida sample, only **23%** of decisions put an outcome verb in the same
sentence as the fee, and only **11%** put a dollar amount there. That is better
than the reformation study's 51-of-932 but nowhere near enough for a regex. Model
classification over the opinion, with a committed prompt, and a human second
coder — never described as mechanical.

**Coder:** deterministic retrieval and slot extraction; a named model with a
committed prompt for the coded variables; a human second coder on the reliability
sample.

---
<!-- Everything below is filled in AFTER the analysis runs. -->

## 6. Denominator

Rates are reported per **adjudicated challenge**, which needs no outside
denominator. Where a trend over time is reported it runs against decisions from
the same courts in the same years, never as a raw count.

## 7. Results

To be completed.

## 8. Interpretation

To be completed. Findings and hypotheses stay visibly separate.

## 9. Limitations

- **Selection into an appeal is about size.** Nobody appeals a fee dispute worth
  less than the appeal. The sample is biased toward large trusts, and every rate
  here describes contested fees large enough to be worth contesting.
- **This study inherits the wealth confounder** from
  `protocols/trustee-litigation.md` §9 wherever it compares by `trustee_form`.
  A corporate trustee will not take a small trust, so `trustee_form` and
  `corpus_value` are entangled. Report fee outcomes within value bands or not by
  form at all.
- **Corpus coverage:** uneven digitisation across decades and courts.
- **Query validity:** "trustee" names at least seven offices. Exclusions 2 to 8
  are the study; their counts are reported.
- **The regional vocabulary split is a threat as well as a finding.** If
  commissions states and fees states differ in outcome, the first hypothesis is
  that their statutes differ, not their judges.
- **Coding:** see the reliability plan. Single-coded means exploratory.

## 10. Data availability

Derived CSV under CC BY 4.0 with a DOI, described in Frictionless, schema.org and
Croissant form, every row carrying a `statement` field.
