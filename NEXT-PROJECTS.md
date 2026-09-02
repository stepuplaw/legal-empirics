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

## 1. Trustee litigation. The question has to change before it can be answered.

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
outside the corpus. FDIC and OCC collect fiduciary-activity reports from banks
with trust powers, and IRS Statistics of Income covers fiduciary returns. Both
are aggregate rather than case-linkable, so they support a crude rate and
nothing finer. Decide whether that is worth it before building for it.

### Plan before implementing

1. Draft `protocols/trustee-litigation.md` from `protocols/TEMPLATE.md`, stages 1
   to 5, and **register it on OSF before running anything**. This one is worth
   preregistering precisely because the outcome variable is contestable.
2. Build the trustee-type classifier and validate it on a hand-coded sample of
   100 captions. Report precision and recall. It is the whole study.
3. Write the securitisation exclusion and report what it removes.
4. Only then compute outcomes.

---

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
