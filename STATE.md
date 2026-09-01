# Where this project stands

_Last updated 2026-09-01. Read this first after a context reset._

Everything below is committed. Nothing here is a plan; it is what exists.

---

## The one-paragraph version

We are building **empirical preventive law**: measuring which drafting language
gets litigated, so drafters can avoid the formulations that fail and prefer the
ones that survive. The corpus is 10.8M US judicial opinions held locally. A full
Florida run is done and produced its first real finding. The methodology is
written down and has been corrected six times by evidence, which is the point.

## Read in this order

| File | What it is |
|---|---|
| `EVIDENCE-BASED-DRAFTING.md` | The thesis, the moral argument, the PACER policy position, and the honest limits |
| `METHODOLOGY.md` | How studies are designed and reported, plus **the lessons log** — read that section, it is where the hard-won corrections live |
| `CORPUS-LINGUISTICS.md` | What the method is, its techniques, its critics, and where the open ground is |
| `studies/ambiguity-pools/REPORT.md` | The completed feasibility study |

## The headline result

Full Florida state appellate run, 6,523 decisions containing ambiguity language,
13,218 ambiguity sentences classified. Of those, **4,497 (34%) concern language
that was actually litigated**.

Reported as three numbers per domain, never one:

| Domain | Exposure | Found ambiguous | Upheld | Risk |
|---|---|---|---|---|
| Contract | 1,612 | 869 | 496 | **64%** |
| Statutory | 630 | 359 | 209 | **63%** |
| **Testamentary** | **303** | **139** | **139** | **50%** |
| Deed | 49 | 17 | 26 | **40%** |
| Constitutional | 34 | 21 | 7 | 75% (tiny N) |

**The finding: testamentary language that gets challenged is upheld half the
time, where contract language fails nearly two thirds of the time.** Wills and
trusts are challenged more often than they fail.

Three hypotheses, none tested: wills lean on boilerplate that has already been
judicially tested, so challenges fail more; will contests are brought on weaker
grounds because the emotional stakes support marginal suits; or the classifier
behaves differently across domains. The third must be excluded before the first
two are interesting.

242 distinct Florida decisions carry litigated testamentary instrument language.
That is the working corpus for the next study.

## The six corrections that shaped the method

Each cost a wrong result and is now a rule in `METHODOLOGY.md`.

1. **Sentence scoping, not document scoping.** Subtracting a contaminating pool
   at document level discarded half of a small pool. A will case cites statutes
   without its ambiguity analysis being statutory.
2. **Recall lives in the query.** A narrow query gave 216 decisions; widening the
   vocabulary gave 5,573 from the same corpus. Retrieve broadly, filter hard.
3. **Constitutional text is a third contaminant**, and was the largest at 35% of
   an early sample. Proximity operators do not catch it: `ambig! /4 constitution!`
   returns 27 decisions where document co-occurrence returns 1,425.
4. **The outcome variable is litigation, not a finding of ambiguity.** A clause
   held clear still drew a lawsuit and still cost the family.
5. **`found` and `rejected` point in opposite directions.** Found is an
   anti-pattern. Rejected is a **safe harbour**: the language drew a challenge and
   survived, so it now carries precedent that it is clear. Never pool them.
6. **Judicial opinions do not define their vocabulary.** Hearst-pattern alias
   mining failed. Statutory definitions sections are the authoritative source;
   221 defined Florida terms are in `data/florida-statutory-definitions.json`.

## What runs, and how

Everything goes through `~/caselaw/` (`clcorpus`), never by opening the corpus
directly. Its `fl` scope resolves to an SSD slice; queries return in under a
second where the platter takes minutes.

    python3 studies/ambiguity-pools/run_methods.py    # keyness, n-grams, collocation
    lib/pools.py                                      # Pool, keyness, collocates, dispersion
    lib/posture.py                                    # domain + posture classifiers

**`lib/posture.py` is validated**, not assumed: against 50 model-coded sentences
it scores **precision 92%, recall 92%, F1 0.92** on the litigated screen, with
posture agreement 70% and domain agreement 78%. Its dominant error is labelling
`rule_stated` as `uncertain`, which excludes rather than contaminates.

## Coded data, and the reliability debt

| File | N | Status |
|---|---|---|
| `sample40_coded.json` | 40 | held-out test set, coded before any rule existed |
| `train60_coded.json` | 60 | training set for rule induction |
| `amb_sentences50_coded.json` | 50 | domain + posture, the two-axis codebook |

**All three are single-coded by model (Claude Fable 5) and carry
`reliability: NOT ESTABLISHED`.** Under our own rules that makes every study
resting on them **exploratory**. The fix is small and specific: Kevin re-codes
one of the 50-item sets and we compute Cohen's kappa. That single step converts
this from exploratory to measurement.

## Where the claim stands against prior art

The broad novelty claim died and the surviving one is better.

- **Corpus linguistics on private instruments is occupied.** Mouritsen,
  *Contract Interpretation with Corpus Linguistics*, 94 Wash. L. Rev. 1337
  (2019), plus six appellate courts on contracts, policies and benefit plans.
- **Empirical wills work is active.** Weisbord & Horton, *Boilerplate and Default
  Rules in Wills Law*, 103 Iowa L. Rev. 663 (2018), hand-coded 230 probated wills
  on lapse, class gifts and apportionment. Horton, Weisbord, Ryan and Cahn have
  several 2026 forthcoming pieces. **This is a live competitor, not a gap.**
- **The nearest prior art on method** is Schwarcz, 46 BYU L. Rev. 471 (2021),
  who hand-collected caselaw construing one homeowners policy and linked it to
  fifty years of revisions in the form.

**The defensible claim is a scaling claim:** done by hand, for a single form, in
one industry; never systematically across clause types at corpus scale, and never
separating exposure from risk from vindication. That three-way split is the
contribution, and it came out of Kevin's correction rather than the literature.

## Citations: what is verified and what is not

**Verified** against primary or repository sources: Hall & Wright, 96 Calif. L.
Rev. 63 (2008); Priest & Klein, 13 J. Legal Stud. 1 (1984); Lee & Mouritsen, 127
Yale L.J. 788 (2018); Mouritsen, 2010 BYU L. Rev. 1915; Loevinger, 33 Minn. L.
Rev. 455 (1949); **Louis M. Brown, *Manual of Preventive Law* (Prentice-Hall
1950)**; Stolle, Wexler, Winick & Dauer, 34 Cal. W. L. Rev. 15 (1997); Lee &
Mouritsen, *The Corpus and the Critics*, 88 U. Chi. L. Rev. 275 (2021); CRISP-DM
1.0; Wilkinson et al., FAIR, 3 Sci. Data 160018 (2016).

**Disputed, do not cite:** the Anya Bernstein critique (two passes disagree on
title and venue; no confirmable Cornell citation) and any Evan Zoldan corpus
critique (**could not be confirmed to exist**).

**Corrected:** *Rasabout*'s majority **rejected** corpus linguistics under a
heading saying so; only Lee's separate opinion applies it. The *Oltmanns* corpus
passage is Durham's. Corpus linguistics has never appeared in a Supreme Court
majority, only Alito concurring in *Duguid* and Breyer dissenting in *Bruen*.

**PACER:** *NVLSP v. United States*, 968 F.3d 1340, 1357 (Fed. Cir. 2020);
settled $125M; Federal Circuit affirmed 2026-03-20. **No reform legislation is
pending** — the Open Courts Act died three times and nothing has been introduced
in the 118th or 119th Congress. Do not write that reform is pending.

## Next, in order

1. **Kevin re-codes 50 sentences.** Kappa. This is the cheapest step with the
   largest effect on what the work can claim.
2. **Extract instrument spans from the 242 litigated testamentary decisions**,
   anchored on reporting verbs (`the will provides`, `the clause reads`) rather
   than on the ambiguity sentence, which was the window error that produced a
   null result the first time.
3. **Report the three numbers per clause type**, not per domain: exposure, risk,
   vindication for survivorship clauses, residuary clauses, class gifts.
4. **Scale to more states.** `clcorpus` has scopes for all 50. Florida alone
   gives 303 litigated testamentary sentences; ten states would give a few
   thousand.
5. **Website mapping, not yet started.** Notebooks belong here, not in the estate
   tax repo. The site needs a research index with `Dataset` and
   `ScholarlyArticle` schema, nbviewer links, and cross-links so the site,
   GitHub, Hugging Face and Zenodo name each other.

## Standing rules

- Query through `~/caselaw/`, never open the corpus directly.
- Report the exclusion funnel with counts. Silent filtering is the commonest defect.
- Rates against a same-court same-year denominator, never raw counts, for trends.
- Findings and hypotheses visibly separate.
- Name selection effects and corpus coverage in every limitations section.
- Deterministic code for retrieval and extraction; a model for classification;
  never describe model-coded results as mechanical.
- When two verification passes disagree, assert nothing.
