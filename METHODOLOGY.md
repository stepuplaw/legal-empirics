# Methodology

How studies in this repository are designed, reported, and criticised. Read this
before starting one.

---

## 1. What field this is

**Empirical legal studies**, and within it the sub-method called **systematic
content analysis of judicial opinions**: taking a defined population of cases,
coding them against a written protocol, and reporting distributions rather than
impressions. The canonical statement of the method is Hall & Wright, *Systematic
Content Analysis of Judicial Opinions*, 96 Cal. L. Rev. 63 (2008). Read it before
designing a study; the conventions below are largely theirs.

Where a study turns on what a **word or phrase means**, the relevant method is
**legal corpus linguistics** instead: frequency and collocation across a corpus,
used to establish ordinary meaning. That is the correct frame for anything
shaped like "is this term ambiguous," and it is a different design from content
analysis, not a variation of it.

> Citations here are given from knowledge and have not been verified against the
> published source. Check them before any of this is published.

**We are applying existing methods, not inventing one.** That matters: it means
a reader can criticise the work on known grounds, and it means the weaknesses
are already catalogued rather than waiting to be discovered by a critic.

---

## 2. The pipeline

Your instinct was right, and it has a standard shape. Each stage is written
down, with counts, before the next begins.

    1. POPULATION      define the universe and the corpus that stands in for it
    2. RETRIEVAL       a stated query; report the raw N
    3. SCREENING       apply exclusions in order; report N dropped at each
    4. CODING          a written codebook; each case gets coded values
    5. RELIABILITY     double-code a random subsample; report agreement
    6. ANALYSIS        distributions, rates against a denominator, trends
    7. INTERPRETATION  findings, then hypotheses, kept separate
    8. LIMITATIONS     what would have to be true for this to be wrong

### Report the funnel

Borrowed from PRISMA, the systematic-review reporting standard in medicine.
Every study reports its attrition as a table, so a reader can see exactly what
was thrown away and why:

| Stage | N | Dropped | Reason |
|---|---|---|---|
| Retrieved | 15,081 | — | FTS query, Florida scope |
| Statutory-interpretation context | 5,807 | 9,274 | canons of construction, not document construction |
| Contract or insurance context | 327 | 5,480 | contract ambiguity is a different doctrine |
| Coded | 29 | 298 | latent/patent ambiguity in a testamentary document |

Anyone can then re-derive your numbers or attack a specific exclusion. Silent
filtering is the single most common defect in this kind of work.

---

## 3. Exclusions are the study

A text query is a **proxy** for a legal concept, never the concept. State the
proxy and its failure modes explicitly.

**Write exclusions as rules, applied in a fixed order, each with a count.** For
the ambiguity case, measured across Florida courts:

- ambiguity language, any context — **15,081**
- co-occurring with statutory-interpretation vocabulary — **9,274**
- co-occurring with contract or insurance vocabulary — **8,923**
- co-occurring with will, testament, codicil, trust instrument or devise — **327**
- latent or patent ambiguity in a testamentary document — **29**

The lesson that produced this section: *ambiguity* is not a doctrine. It is a
word that three unrelated doctrines borrow, and the only thing separating them
is what kind of document the court was reading. A study that does not exclude
statutory interpretation is measuring the canons of construction and calling it
estate law.

**Sentence-scoped co-occurrence beats document-scoped.** Requiring the terms
within the same sentence, rather than merely the same opinion, removes most
false pairings. FTS5 `NEAR()` approximates this but accepts only phrases, so
expand into OR'd `NEAR()` calls.

---

## 4. Coding

Content analysis means humans (or a model, disclosed as such) assign values from
a **written codebook** fixed before coding starts. A codebook entry gives the
variable, its permitted values, and a decision rule for hard cases.

**Report intercoder reliability.** The convention is Cohen's kappa for two
coders or Krippendorff's alpha for more, on a random subsample of at least
10%. Below about 0.7 the coding is not reproducible and the finding should not
be reported as a finding.

**Single-coder studies must say so.** A study coded once, by one person or one
model, with no reliability check, is exploratory. Label it that way rather than
presenting it as measurement.

**If a language model does the coding, that is a disclosed method**, not an
implementation detail. Report the model, the prompt, and the agreement between
the model and a human on the reliability subsample.

---

## 5. The two threats that matter most

**Selection effects.** Published appellate opinions are a severely biased sample
of disputes. Most disputes never sue, most suits settle, most settlements are
invisible, most trials are not appealed, and not every appeal is published. The
classic treatment is Priest & Klein, *The Selection of Disputes for Litigation*,
13 J. Legal Stud. 1 (1984), whose central point is that litigated cases cluster
around genuine uncertainty and therefore do not represent disputes generally.

Practical consequence: a decline in appellate opinions about a doctrine is
**not** evidence that the underlying conduct declined. It is evidence about what
reached an appellate court and got published. Say so every time.

**Corpus coverage.** Digitisation is uneven across decades and courts. Any trend
over time must be reported as a **rate against a denominator drawn from the same
courts in the same years**, never as a raw count. Restricting numerator and
denominator to the same court set also controls for shifts in corpus
composition, which will otherwise manufacture a trend out of nothing.

---

## 6. Reporting conventions

Every study states, in this order:

1. **Question**, in one sentence, fixed before the data is examined.
2. **Population and corpus**, with the snapshot date and the court scope.
3. **Query**, verbatim and runnable.
4. **Exclusion funnel**, as a table with counts.
5. **Codebook**, if anything was coded.
6. **Reliability**, or an explicit statement that the study is single-coded.
7. **Results**, as rates against a denominator.
8. **Interpretation**, with findings and hypotheses visibly separated.
9. **Limitations**, naming selection effects and coverage specifically.
10. **Data availability**: derived CSVs alongside, licence stated.

**Pre-register the question.** Write stage 1 into the protocol file and commit it
before running the analysis. Deciding what the question was after seeing the
results is the mechanism behind most irreproducible findings, and a commit
timestamp is cheap protection against doing it accidentally.

---

## 7. Study designs, and which question each answers

**Descriptive / prevalence.** How often does a doctrine appear, and is that
changing? The capacity study is this. Cheap, and the weakest claim: it describes
the corpus, not the world.

**Case-control.** Take cases where an outcome occurred and matched cases where
it did not, then look backwards for what differs. This is the design for a
**document risk identifier**: to learn which drafting choices attract
litigation, you need litigated instruments *and* comparable unlitigated ones.
The corpus only holds the litigated half, which is the hard part and the reason
the question is not answerable by search alone.

**Outcome coding.** Who won, on what ground. Requires reading every case; there
is no text-search shortcut. This is where the practically useful findings live
and where the labour is.

**Corpus linguistics.** What does a term ordinarily mean, by frequency and
collocation. The right design for ambiguity questions.

---

## 8. Where this is heading

The honest ordering, weakest claim to strongest:

1. **Prevalence** — done, for capacity and undue influence.
2. **Outcome coding** on a sample — who actually wins a capacity challenge, and
   on what evidence. Requires a codebook and reading, and produces the first
   genuinely useful number.
3. **Factor extraction** — which recurring fact patterns appear in successful
   challenges. Still descriptive, but it is what a practitioner can act on.
4. **Document risk identification** — which drafting features correlate with
   being litigated. Needs a control group of unlitigated instruments, so it is a
   different data problem, not a bigger version of the same one.

Do not skip to 4. A risk identifier built only on litigated documents learns
what litigated documents look like, which is not the same as what causes
litigation, and it will be confidently wrong.
