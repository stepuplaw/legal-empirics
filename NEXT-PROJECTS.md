# Next projects, scoped

_Written 2026-09-02 as a handoff. Each entry says what is known, what is not,
and what has to be decided before code gets written._

---

## 0. Re-run statutory-staleness first. It is unblocked and cheap.

Both statute crawls finished. `us-law.db` now holds **30 Florida editions, 1997
to 2026**, where the last run had five.

    python3 studies/statutory-staleness/build_dataset.py
    python3 -m nbconvert --execute --to notebook --inplace notebooks/statutory-staleness.ipynb

Text-diff coverage should go from **5.3% of pairs to roughly 58%**, and the
69.5% discount gets measured across three decades instead of four years. That
turns the 53.6% headline from an estimate into close to a measurement, and it
is worth a `v0.2.0` release with its own version DOI.

Do this before starting anything new. It is one command and it improves the
strongest result already published.

---

## 1. Trustee litigation. Scoped out, and the question changed twice.

> **Superseded by `protocols/trustee-litigation.md`, 2026-09-02.** Everything
> below stands as the record of how the design got here, and the pool tables are
> still the best numbers we have. But they were produced by ad-hoc queries that
> were never committed, so they are **provisional** until
> `studies/trustee-litigation/size_pools.py` reproduces them.
>
> Three things this pass got wrong, all fixed in the protocol:
>
> 1. **It never read the literature**, and the literature moves the question.
>    Leslie (27 Cardozo L. Rev. 2713) argues trust statutes *should* differentiate
>    professional from non-professional trustees; UTC s.806 partially already does.
>    Whether courts differentiate anyway is measurable, novel, and it is the
>    headline. Outcomes become the secondary result.
> 2. **Conditioning on litigation does not remove the selection effect.** It
>    removes the denominator problem and makes the selection problem worse, because
>    corporate trustees are repeat players who settle and appeal differently from
>    one-shot individual trustees. See the protocol, section 9.
> 3. **"Professional" and "corporate" are not the same axis**, and the classifier
>    plan below conflates them. A paid lawyer-trustee is a professional and a
>    natural person. A name-based classifier reads *form*, not *capacity*, so
>    validating it against the courts' "professional trustee" labels validates it
>    against the wrong variable.
>
> Since revised again, 2026-09-02, after sampling: **national from the start, no
> pilot state**; proximity does not identify the trustee and the measurement is in
> `studies/trustee-litigation/CLASSIFIER-NOTES.md`; the vocabulary question is
> answered from the uniform acts rather than from opinions, and the drafters' own
> pair is **professional / amateur**.

**The original framing:** does having a professional trustee reduce litigation?
Query sketched as `breach /s fiduciary /s duty` crossed with
`professional /2 trustee` and `independent /s trustee`.

I sized it. The framing does not survive contact with the corpus.

### What the corpus actually holds (Florida state appellate)

| Pool | Decisions |
|---|---:|
| "breach of fiduciary duty" | 1,023 |
| NEAR(breach fiduciary duty, 25) | 1,160 |
| breach of fiduciary duty **and** trustee | 186 |
| **"professional trustee"** | **0** |
| "corporate trustee" | 31 |
| "individual trustee" | 10 |
| "independent trustee" | 6 |
| "institutional trustee" | 2 |
| BFD **and** "professional trustee" | **0** |
| BFD **and** "corporate trustee" | 3 |
| "bank" or "trust company" as trustee | 2,024 |

### What the corpus holds NATIONALLY, which is the scope that matters

State appellate, all 51 jurisdictions. Sized 2026-09-02.

| Pool | Decisions | States |
|---|---:|---:|
| "breach of fiduciary duty" | 31,681 | 51 |
| BFD **and** trustee | **7,061** | 51 |
| "corporate trustee" | 1,142 | 51 |
| "individual trustee" | 462 | 48 |
| "independent trustee" | 261 | 44 |
| "professional trustee" | 135 | 33 |
| "institutional trustee" | 78 | 25 |
| BFD **and** "corporate trustee" | 122 | 37 |
| BFD **and** "professional trustee" | **37** | 15 |

**National changes the picture, and not in the way you would hope.** In Florida
the phrase "professional trustee" appears in zero appellate decisions. Nationally
it appears in 135, and crossed with breach of fiduciary duty it appears in 37.
So the arms exist, but 37 decisions cannot be compared against a 7,061-decision
population. A label-based study is still not viable.

**What the labelled subset IS good for is validation.** Those 135 professional
and 462 individual decisions are hand-labelled by the courts themselves, for
free. Use them as the ground-truth set for a name-based classifier, then apply
the classifier to all 7,061. That converts the label problem from a dead end
into a training set, and it means the classifier ships with measured precision
and recall like every other one in this repository.

### The vocabulary question, answered empirically

Trustee type is not stated as a term of art. Over 272 Florida trust-fiduciary
decisions, the modifiers courts actually put in front of "trustee" are:

    sole 16 · testamentary 7 · corporate 5 · co- 5 · prudent 4 · appointed 4
    special 3 · constructive 3 · individual 2 · nonresident 2

`corporate` appears in five documents and `individual` in two. There is no
descriptive vocabulary to filter on, which is the same answer the phrase counts
gave by a different route.

**The identity is in the name.** The same pass pulled the entities acting as
trustee, and they separate cleanly without any label: J.P. Morgan Chase Bank
N.A., J.P. Morgan Trust Company N.A. on one side, and Jerome Adams, Eleanor M.
Rich, Milton Wallace on the other. A corporate trustee announces itself through
`Bank`, `N.A.`, `Trust Company`, `Corp`, `LLC`, `Association`; an individual
carries a personal name. **Building and validating that classifier is the
study**, not a preprocessing step before it.

### Three findings, in increasing order of how much they matter

**1. The labels do not exist in the text.** Not one Florida appellate decision
contains the phrase "professional trustee". Courts name the trustee, they do not
classify it. Any design that filters on the label returns an empty arm, which is
what the zero above is.

**2. Trustee type has to be inferred from the party, not from a label.** A
corporate trustee is identifiable because the trustee *is* a bank or a trust
company, from the case caption and the first mention in the opinion. An
individual trustee carries a personal name. That is a tractable classification
problem and it is the actual first task of this project.

**3. The mortgage-backed securities trap, which will swamp everything.** The
2,024 decisions naming a bank as trustee are dominated by residential
foreclosure, where a bank is trustee **for a securitisation trust** and not for
anybody's family. Those cases have nothing to do with fiduciary administration
of a private trust. Left in, this study measures the foreclosure crisis and
calls it trust law. The exclusion has to be explicit and its count reported.

### The identification problem, which is fatal to the question as asked

"Do professional trustees reduce litigation" is a claim about a **rate**, and a
rate needs a denominator: how many trusts have professional trustees and how
many have individual ones. **Court records contain only the numerator.** If
individual-trustee disputes outnumber corporate-trustee disputes, the honest
reading is that individual trustees are more common, not that they are worse.
No amount of case data fixes this, because the population of untroubled trusts
never appears in the reports.

### What is answerable, and it is still worth doing

Condition on litigation. Given that a trustee was sued, does the outcome differ
by trustee type?

- surcharge imposed or refused
- removal granted or refused
- affirmed or reversed on appeal
- attorney fees assessed against the trustee personally

That comparison needs no population denominator, because both arms are already
inside the courthouse. It answers a real question a client asks, which is what
happens **when** a trust goes wrong, and it does not overclaim.

If the incidence question is wanted later, the denominator has to come from
outside the corpus, and **one arm of it is better than this paragraph originally
allowed.** Federal bank Call Report **Schedule RC-T, item 4** reports the *number
of accounts* and market value of personal trust and agency accounts — testamentary
trusts, revocable and irrevocable living trusts — per institution, per quarter.
Sitkoff & Schanzenbach built a state-year panel from exactly that source for 115
Yale L.J. 356. So a corporate-arm rate, suits per thousand bank-held personal
trust accounts by state-year, is computable and is not crude.

There is no register of individual trustees, so the individual arm has no
denominator and never will. Report the corporate rate alone, labelled as one arm,
and never divide the two. IRS Statistics of Income fiduciary returns count trusts
and estates together and do not separate trustee type, so they bound the total
rather than supplying the missing arm.

### Plan before implementing

Written out in full at **`protocols/trustee-litigation.md`**, stages 1 to 5, with
the literature, the two-variable codebook, the eight-step exclusion funnel and
the selection-effect limitation. Register it on OSF before running anything.

Two additions that came out of writing it:

- **National from the start, and there is no pilot state.** The question is
  whether courts differentiate, and courts differ by state, so one state cannot
  answer it — it returns one of fifty-one values. Florida least of all: three
  decisions here cross breach of fiduciary duty with "corporate trustee" and zero
  contain "professional trustee". Extraction is *tuned* on the Florida SSD slice
  because it is fast; every reported number is national.
- **The deed-of-trust foreclosure trustee is a bigger contaminant than the MBS
  trustee**, and this pass missed it because Florida does not have one. In the
  thirty-odd states that foreclose by deed of trust, every non-judicial
  foreclosure has a statutory "trustee". Size that exclusion per state.

## 2. Treatment latency

Protocol already drafted at `protocols/treatment-latency.md`, stages 1 to 5
filled, results blank. Uses the **77.5M edge citation graph** in `us-meta.db`,
which is the largest unused asset here. Nationally scalable, needs no state
statutes, and it is the failure mode every language model has.

Pilot number already in hand: 209 citations since 2011 to Florida decisions
stating a rule the legislature reversed in 2011, of which 165 belong to one 1961
case almost certainly cited for something else. That gap between 209 and the
real number is the entire study.

---

## 3. Florida deed failure modes

The commercial one. Lady Bird deeds are already the practice's lead magnet and
the expertise is real, which is what makes the analysis credible rather than
mechanical. Lower novelty than the research projects, much higher commercial
value, and it ranks for queries people type before they hire somebody.

Expect this to earn clients. Do not expect it to earn citations.

---

## 4. Disputed terms, per clause type

The national dataset already exists with 286,846 rows. What has not been done is
cutting it by clause type rather than by functional category, so the output is
"survivorship clauses fail at X%" instead of "succession language fails at 27%".
That is the form a drafter can act on, and it is analysis of data already
collected rather than a new collection.

Cheapest real result on this list.

---

## 5. Florida homestead litigation

Florida-specific, constitutionally distinctive, and heavily searched. The
homestead exemption produces a large, self-contained body of appellate law with
recurring failure modes: devise restrictions, improper waiver, and the
distinction between the tax exemption and the creditor exemption.

Good SEO, moderate novelty, and it sits squarely inside the practice.

---

## What to hand the next session

Read in this order:

1. `STATE.md` for where everything stands
2. `METHODOLOGY.md`, especially the lessons log
3. `DISTRIBUTION.md` for what is published and where
4. This file

Standing constraints that have already cost time once each:

- Query through `~/caselaw/`, never open the corpus directly.
- Do **not** read `us-law.db` with `?immutable=1` while a crawl is writing. It
  reports `database disk image is malformed` on a healthy database.
- `us-law.db` takes one writer. Queue statute ingests.
- National phrase queries on the platter are slow enough to time out a scoping
  pass. Size on the Florida SSD slice first.
- Read the output before trusting the pattern. `NEAR("breach fiduciary duty", 25)`
  looks correct and silently searches for a three-word phrase, which returned
  16 Florida decisions for the most litigated claim in American law.
