# Methodology

How studies in this repository are designed, reported, and criticised. Read this
before starting one.

---

## 1. What field this is

**Empirical legal studies**, and within it the sub-method called **systematic
content analysis of judicial opinions**: taking a defined population of cases,
coding them against a written protocol, and reporting distributions rather than
impressions. The canonical statement of the method is **Mark A. Hall & Ronald F.
Wright, *Systematic Content Analysis of Judicial Opinions*, 96 Calif. L. Rev. 63
(2008)** (verified, article PDF). Read it before
designing a study; the conventions below are largely theirs.

Where a study turns on what a **word or phrase means**, the relevant method is
**legal corpus linguistics** instead: frequency and collocation across a corpus,
used to establish ordinary meaning. That is the correct frame for anything
shaped like "is this term ambiguous," and it is a different design from content
analysis, not a variation of it.

> **Citation status.** Verified against primary or repository sources: Hall &
> Wright (96 Calif. L. Rev. 63); Priest & Klein (13 J. Legal Stud. 1, 1984);
> Lee & Mouritsen (127 Yale L.J. 788); Mouritsen, *Dictionary Is Not a Fortress*
> (2010 BYU L. Rev. 1915); Loevinger, *Jurimetrics — The Next Step Forward* (33
> Minn. L. Rev. 455, 1949); **Louis M. Brown, *Manual of Preventive Law*
> (Prentice-Hall 1950)**; Stolle, Wexler, Winick & Dauer (34 Cal. W. L. Rev. 15,
> 1997); CRISP-DM 1.0 guide; Wilkinson et al., FAIR (3 Sci. Data 160018, 2016).
> Disputed or unconfirmed citations are flagged where they appear.

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

---

## 9. Lessons from runs, recorded as they are learned

Each entry is something a run actually taught, with the run that taught it.
Written down because the alternative is relearning it.

### Sentence scoping beats document scoping, by about threefold
*Ambiguity pools, 2026-09-01.* Subtracting a contaminating pool at the document
level discarded 144 of 216 cases. Requiring the competing vocabulary in the
**same sentence** as the target term retained 135. A testamentary case routinely
cites a statute somewhere without its ambiguity analysis being statutory. In a
sample of overlap cases, statutory vocabulary shared a sentence with the
ambiguity term only 17% of the time against 39% for testamentary vocabulary.
**Never subtract pools at document level on a small corpus.**

### Judicial opinions do not define their own vocabulary
*Alias mining, 2026-09-01.* Hearst-style patterns ("also called", "also known
as", "referred to as", "or a") were run over 1,200 estate decisions. Precision
was very low. "Also known as" in opinions overwhelmingly means a party's
alias; "referred to as" is usually "hereinafter referred to as"; "or a" catches
ordinary disjunction. Real doctrinal aliases exist in the output (*dependent
relative revocation*, *pot trust*, *election*) but at perhaps one in twenty.

Courts assume their readers know the vocabulary. **Legal synonymy lives in
statutes, dictionaries and treatises, not in opinions.** Mine the right corpus.

### Dispersion is the filter that separates a term from a name
A genuine legal alias recurs across many decisions; a party's a/k/a appears in
one. Requiring a candidate in **three or more distinct documents** removes
nearly all name noise. Report document frequency, not raw count.

### Statutory definitions are the authoritative controlled vocabulary
*2026-09-01.* Nineteen Florida definitions sections yield **221 statutorily
defined terms** across the probate, trust, principal-and-income, disclaimer,
guardianship and power-of-attorney codes. These are authoritative by
construction, freely available, and citable. Extract with a curly-quote pattern:
statutes use `“term” means`, and a straight-quote regex silently returns zero.

Prefer this to a hand-built list. Practitioner intuition is a supplement, not
the source.

### Legal synonymy is treacherous and must be checked term by term
A *revocable trust* is also a *living trust*. A **living will** is an entirely
different instrument, an advance directive about end-of-life care. A *revocable
will* is not standard usage at all, since wills are revocable by nature. Any
automated thesaurus would happily merge these. **No synonym enters a controlled
vocabulary without a source, and a statutory definition beats every other
source.**

### State the corpus parameters, and check the extremes
*2026-09-01.* The Florida slice reports dated decisions spanning 0019-01-31 to
2028-04-13. Both extremes are data errors. The Florida state appellate courts
in scope, `fladistctapp` and `fla`, hold 430,135 decisions spanning 1825-02-08
to 2026-06-29. **Always report court scope, date range and snapshot, and always
look at the minimum and maximum before trusting a date field.**

### Wildcards need testing before use
Root expanders such as `ambig!` or `statut!` change recall substantially and
silently. Test each expansion against its literal form and record the counts
before adopting it.

### Constitutional interpretation is a third ambiguity domain, and the largest
*Disputed-language extraction, 2026-09-01.* Having separated statutory and
contract ambiguity, a coded sample of 40 extracted spans came back **35%
constitutional** and only **25% testamentary**. Constitutional provisions evade
a citation-based reject filter because the quoted text itself contains no
reporter, no "v.", and no "Fla." Courts quote constitutional text constantly and
call it ambiguous. Any future pool must exclude it explicitly.

### Model classification beats regex, and costs a reliability obligation
Regex classification is deterministic and reproducible but brittle: it cannot
tell that "the common law of trusts and principles of equity supplement this
code" is the Trust Code rather than a trust instrument, though it contains
"trust". A model reading the span gets that right.

The trade is real and must be paid, not waved at. Model coding is
**non-deterministic**, so a rerun may differ; it requires the model and date
recorded; and under the coding rules above it requires a **human second coder on
a random subsample with Cohen's kappa reported**. Until that exists the study is
exploratory and must say so on its face.

The practical division: use deterministic code for RETRIEVAL and mechanical
extraction, where reproducibility matters most and judgement is not required.
Use a model for CLASSIFICATION, where judgement is the whole task. Never
describe a model-coded result as if it were mechanical.

### Recall lives in the query, precision lives in the filter
*2026-09-01.* A narrow retrieval query returned 216 Florida decisions; widening
the vocabulary returned **5,573**, a 26-fold increase, from the same corpus and
courts. The bottleneck was never the corpus.

Retrieve broadly, then filter hard. A narrow query silently caps the study at
whatever the query author happened to think of, and unlike a filter it leaves no
funnel entry to show what was lost.

### Never assert that a term is absent from an opinion without the official PDF
*Citation checking, 2026-09-01.* A full-text search reported that *Facebook v.
Duguid* does not discuss corpus linguistics. It does, in Alito's concurrence,
592 U.S. 412. The search missed it because the U.S. Reports print **hyphenates
the word across a line break**. Any claim that something is *absent* from an
opinion must be checked against the official PDF, not a reporter database.
Absence claims are the easiest kind to get wrong and the hardest to defend.

### Crossref cannot disconfirm a US law review citation
Crossref does not index most US student-edited law reviews; a query for an
entire law review can return zero. A Crossref miss is not evidence a citation is
fake. Fall back to the journal's institutional repository, whose OAI-PMH feed
(`/do/oai/?verb=ListRecords&metadataPrefix=oai_dc&set=publication:<journal>`) is
the reliable enumeration path. The bepress `/do/search/` endpoint returns
HTTP 500 and should not be used.

### Proximity operators under-capture doctrinal contamination
*2026-09-01.* A tempting fix for constitutional contamination was `ambig! /4
constitution!`. Tested: **27 decisions** at a four-word window, **86** at ten,
against **1,425** co-occurring at document level and a coded sample showing 35%
of extracted spans were constitutional. The window misses almost everything,
because a court quotes a constitutional provision and calls it ambiguous
paragraphs later.

The lesson generalises. **Contamination is a property of the extracted span, not
of the distance between two words in the opinion.** Filter where the object of
study is, which here means at span level, not at opinion level.

### When two verification passes disagree, assert nothing
*2026-09-01.* One pass reported Bernstein and Zoldan critiques as verified
against repository sources. A second, more thorough pass found the Bernstein
title probably wrong, no confirmable Cornell citation, and **no evidence the
Zoldan piece exists at all**. Both had been committed as verified.

A citation that two passes dispute is **less** trustworthy than one never
checked, because the first check creates false confidence. Record the conflict,
name both readings, and cite neither until someone has the printed article.

### Preventive law is dormant, and must be cited historically
Brown's work is *Manual of Preventive Law* (Prentice-Hall 1950). The National
Center for Preventive Law's domain is dead, last archived 2022. Its living
descendant is the merger with therapeutic jurisprudence. Use the term with a
historical gloss, never as a live term of art.

### The outcome variable is LITIGATION, not a finding of ambiguity
*Sentence coding, 2026-09-01, corrected the same day.* Fifty ambiguity sentences
coded on two axes, domain and posture. My first inclusion rule admitted only
cases where the court **found** ambiguity, 7 of 50, and excluded the 12 where
the court **rejected** it.

**That was wrong, and it mistook the research question.** A clause the court held
clear still drew a lawsuit. Somebody paid a lawyer to argue it was ambiguous, an
opponent paid to argue it was not, and a court spent time resolving it. Under
[evidence-based drafting](EVIDENCE-BASED-DRAFTING.md) the harm to be prevented is
the **dispute**, not the adverse ruling. A provision that wins after three years
of litigation has still failed the family that paid for it.

If anything, `rejected` is the more instructive class: the drafter thought the
language was clear, the court agreed it was clear, and it was fought over
anyway.

**Corrected inclusion rule.** Admit `found`, `rejected` and `alleged`, because
all three evidence that the language was litigated. Exclude only `rule_stated`,
where the sentence recites black-letter law and says nothing about the text in
front of the court, and `uncertain`, which goes to a second round.

That takes the usable pool from 14% to **50% of sentences**, and the testamentary
subset from 4 to 8.

**Posture stays in the codebook**, but as a severity stratum rather than a
gate: `found` means the language actually failed, `rejected` means it survived a
challenge it should never have attracted. Report them separately and never pool
them into a single "failed" count.

### Sentence-level coding is cheap enough to do properly
Fifty sentences is a short read. Where a corpus-scale mechanical filter is
brittle and a full-opinion review is unaffordable, **the ambiguity sentence
itself is the right unit**: short enough to code in bulk, long enough to carry
both domain and posture. Design the unit of coding to be the smallest text that
answers the question.
