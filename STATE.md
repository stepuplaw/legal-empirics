# Where this project stands

_Last updated 2026-09-02. Read this first after a context reset._

Everything below is committed. Nothing here is a plan; it is what exists.

---

## The one-paragraph version

We are building **empirical preventive law**: measuring which drafting language
gets litigated, so drafters can avoid the formulations that fail and prefer the
ones that survive. The corpus is 10.8M US judicial opinions held locally, now
joined to the Florida Statutes edition by edition. Three studies are built and
exported as citable datasets. The methodology has been corrected by evidence
nine times, which is the point.

## Read in this order

| File | What it is |
|---|---|
| `EVIDENCE-BASED-DRAFTING.md` | The thesis, the moral argument, the PACER policy position, and the honest limits |
| `METHODOLOGY.md` | How studies are designed and reported, plus **the lessons log** — read that section |
| `CORPUS-LINGUISTICS.md` | What the method is, its techniques, its critics, and where the open ground is |
| `PUBLISHING.md` | Where the datasets live and how the records reference one another |

## What changed on 2026-09-01

**The question moved from domain to term.** The earlier headline — testamentary
language upheld half the time against contract language failing two thirds —
was a fact about *categories of case*. A drafter cannot act on it. The unit of
analysis is now the **(term, decision) pair**: which specific words get fought
over, how often the challenge succeeds, and in how many states.

**And from one state to fifty-one.** Florida alone gave confidence intervals so
wide they were useless: `degree` risk 70%, interval 40–89%.

## The three studies

### disputed-terms — 286,846 (term, decision) pairs, all 51 jurisdictions

Terms are extracted by **cue-anchored quotation** (`the term "X"`, `"X" as used
in`) over the **whole opinion**, with the ambiguity holding selecting the *case*
rather than the *sentence*. That is the fix `studies/ambiguity-pools/REPORT.md`
identified after its own extraction returned null.

Raw quoted spans do not work: the top hits are `and`, `yes` and `i'd rather not
talk about it`. Cue anchoring returns `accident`, `occurrence`, `arising out
of`, `all-risk`.

Risk by functional category, linked rows only, Wilson 95%:

| Category | Exposure | Risk |
|---|---:|---|
| temporal | 2,458 | 42% (39–44) |
| scope | 8,865 | 41% (40–42) |
| mental | 1,465 | 40% (36–43) |
| conduct | 3,673 | 39% (37–41) |
| role | 7,395 | 38% (37–40) |
| condition | 1,425 | 38% (35–41) |
| degree | 2,247 | 37% (35–40) |
| property | 4,679 | 35% (33–37) |
| event | 5,775 | 35% (33–36) |
| nexus | 774 | 31% (27–35) |
| modal | 2,075 | 30% (28–33) |
| **succession** | 1,391 | **27% (24–30)** |

Succession language is the *safest* class, which independently corroborates the
old domain-level finding by a different route.

**Link tiers are never pooled.** `direct` (81,131) means an ambiguity sentence
names the term; `proximate` (28,074) means it is quoted within three sentences
of one; `inferred` (177,641) carries only the decision's posture and is excluded
from every headline. Inferring everywhere is what produced the earlier null.

### reformation-fl — 932 Florida decisions, 1853–2026

Reformation is the sharpest available measure of drafting failure: a petition
says the drafter got it wrong and somebody paid to fix it.

Three regimes coexist in one state with dated statutory breaks — deeds and
contracts in equity throughout, trusts from **2007** (s. 736.0415), wills from
**2011** (s. 732.615), before which Florida held that a will could not be
reformed at all.

| Instrument | n | Granted | Denied |
|---|---:|---:|---:|
| contract | 376 | 5 | 5 |
| deed | 242 | 13 | 7 |
| insurance | 202 | 8 | 1 |
| trust | 66 | 4 | 1 |
| will | 42 | 4 | 1 |

**Wills: 36 decisions before 2011, six after.** Eight litigated decisions in the
whole corpus cite the reformation statutes.

**Grant rates are not publishable.** Only 51 decisions carry a machine-readable
holding, because most opinions state their disposition in a sentence that never
repeats the word. Volume, composition, error taxonomy and the statutory break
are solid; the rates are not.

### statutory-staleness — 19,085 (decision, section) pairs

**77.0%** construe a section amended since the decision; median gap 20 years.
That number is identical on the full corpus and on an independent 2,500-decision
sample.

Where two editions are held, **69.5%** of those flagged had a real change to the
operative text — so the combined estimate is that **53.6%** of Florida
construction holdings rest on statutory text that has actually changed.

Exposure is **not** abrogation, and the notebook says so. A text change anywhere
in a long section is not proof the construed subsection changed. Subsection-level
alignment is the next step and is not done.

## The corpus grew a second half

`us-law.db` now holds the Florida Statutes **edition by edition**, which is what
makes the text-diff tier possible at all.

- **2010–2026** via the chapter view. `build-flstat.py` was parsing only the
  2013+ markup; the 2010–2012 editions use divs where later ones use spans, and
  every pre-2013 section was silently dropped with an empty number.
- **1997–2009** via per-section URLs. The chapter view is empty for those years,
  which produced a wrong conclusion that the site did not hold them. It holds
  them. `build-flstat-sections.py` is targeted rather than wholesale — 25,000
  requests per edition is not a crawl anyone should run.
- **USC** had 0 of 14,052 sections with a history trail. The amendment notes
  were being kept in the body and never filed; GovInfo delimits them with HTML
  comments, so extraction is exact. Fixed, reload queued.

## Publishing

`scripts/export_dataset.py` emits CSV, Frictionless datapackage, schema.org
JSON-LD and MLCommons Croissant, with SHA-256 and row counts throughout. It
refuses to ship a column with no description. Every row carries a `statement`
field — the row as one English sentence — because a row of codes can be
downloaded but not retrieved or quoted.

**FL-Stale** is a 1,500-item benchmark on statutory currency. Ground truth is
mechanical rather than interpretive, and the binary tasks are balanced so a
constant answer scores 0.50, with the baseline shipped alongside.

## The reliability debt, unchanged

All three coded sets are single-coded by model and carry
`reliability: NOT ESTABLISHED`. Under our own rules that makes every study
resting on them **exploratory**. Kevin re-codes one 50-item set, we compute
Cohen's kappa, and the work becomes measurement. This is still the cheapest step
with the largest effect, and nothing built since has substituted for it.

## Next, in order

1. **Kevin re-codes 50 sentences.** Kappa. Still first.
2. **Re-run statutory-staleness** when the edition backfill finishes. The
   text-diff tier goes from 5.3% of pairs to roughly 58%, and the 69.5% discount
   gets measured across three decades instead of four years.
3. **Subsection-level alignment**, to turn exposure into abrogation.
4. **The research pages on stepuplaw.com**, which do not exist yet — every
   metadata file names `/research/` and it currently 404s.
5. **Zenodo release and DOIs**, then fill `identifier` in the metadata.
6. **Report disputed terms per clause type**, not only per category.

## Standing rules

- Query through `~/caselaw/`, never open the corpus directly.
- Report the exclusion funnel with counts. Silent filtering is the commonest defect.
- Rates against a same-court same-year denominator, never raw counts, for trends.
- Findings and hypotheses visibly separate.
- Name selection effects and corpus coverage in every limitations section.
- Deterministic code for retrieval and extraction; a model for classification;
  never describe model-coded results as mechanical.
- When two verification passes disagree, assert nothing.
- Never pool measures that point in opposite directions.
- Read the output before trusting the pattern. Bush v. Gore reached a
  testamentary dataset because `will` is also an auxiliary verb, and reversal
  direction was scored backwards until the sentences were read.
