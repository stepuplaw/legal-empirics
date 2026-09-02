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

**Posture stays in the codebook, and the two classes point in OPPOSITE
directions.** This is the subtle part and it must not be flattened.

| Posture | What it evidences | Drafting implication |
|---|---|---|
| `found` | the language failed; a court could not determine its meaning | **anti-pattern.** Avoid the formulation |
| `rejected` | the language drew a challenge **and survived it** | **safe harbour.** The formulation now has precedent that it is clear |

A `rejected` case carries a cost and a benefit at once. The cost is that the
language attracted a fight. The benefit is that a court has now held it clear,
so the next drafter using that formulation has authority behind it. Language
that has been litigated and upheld has **known meaning**, which is precisely why
tested boilerplate persists in practice rather than being improved: its
interpretive risk has already been paid down by somebody else's lawsuit.

So the two classes support opposite advice from the same corpus. Pooling them
into a single "litigated, therefore bad" count would recommend abandoning the
formulations that are best established.

**Report three numbers, never one:** how often a formulation is litigated, how
often it fails when litigated, and how often it is upheld. The first is exposure,
the second is risk, the third is the argument for keeping it.

### Sentence-level coding is cheap enough to do properly
Fifty sentences is a short read. Where a corpus-scale mechanical filter is
brittle and a full-opinion review is unaffordable, **the ambiguity sentence
itself is the right unit**: short enough to code in bulk, long enough to carry
both domain and posture. Design the unit of coding to be the smallest text that
answers the question.

### Conditioning on litigation relocates the selection effect, it does not remove it
*Trustee scoping, 2026-09-02.* The trustee question "do professional trustees
reduce litigation" needs a denominator the courts do not hold, so the design
moved to comparing **outcomes among cases already sued**, on the reasoning that
both arms are inside the courthouse and no population denominator is needed.

The denominator problem does go away. **The selection problem gets worse**, and
the move hides it. Priest & Klein applies to *which disputes reach a published
appellate opinion*, and the two arms reach it by different routes. A corporate
trustee is a repeat player: insured, with in-house counsel, a reputational stake
across every other account it holds, and a budget to settle the cases it would
lose. An individual trustee is a one-shot player, often a family member paying
counsel personally and frequently unable to fund an appeal at all.

So an outcome difference between arms is equally consistent with better conduct,
with differential settlement, with differential ability to appeal, and with
differential instrument drafting. **Whenever an arm of a comparison is defined by
a party characteristic that also predicts settling and appealing, conditioning on
litigation is not a fix.** Report the appellant composition by arm, report
affirmance separately from first-instance outcome, and state every reading.

### Two labels that sound like one axis are usually two axes
*Trustee scoping, 2026-09-02.* The plan was one classifier separating
"professional" from "individual" trustees, validated against the 135 decisions
saying "professional trustee" and the 462 saying "individual trustee".

Those are not two ends of one variable. **A professional trustee can be a natural
person** — a paid lawyer, an accountant, a licensed private fiduciary — and a
corporate trustee is an entity. A name-based classifier reads **form**, entity
versus natural person. The statutory standard that matters, UTC s.806, keys off
**capacity**, held-out expertise. Validating a form classifier against capacity
labels scores every paid individual fiduciary as a false negative when it is not
an error at all.

Code them as separate variables and report the agreement between them. How often
entity form predicts professional capacity is itself a finding, and a cheap one.

### A one-state intuition about noise does not survive going national
*Trustee scoping, 2026-09-02.* The Florida sizing correctly identified the
mortgage-backed-securities trap: banks appear as trustee for securitisation
pools, not for families. That is the Florida-shaped contaminant, because Florida
forecloses judicially on a mortgage.

In **deed-of-trust** states — California, Texas, Virginia and Colorado among
them — a non-judicial foreclosure has a statutory "trustee", a title company
holding a security interest and a fiduciary of nobody. The Florida pass could
not see that pool at all, because Florida does not have the office. Whether it
is larger than the securitisation pool is a question for the sizing script, not
an assertion.

**When a study goes national, re-derive the exclusion list, do not port it.**
Contamination follows state procedure, so it changes shape at the state line.

### Sizing answers whether it can be measured; the literature answers whether it is worth measuring
*Trustee scoping, 2026-09-02.* The pool sizing was careful and it killed the
original design in a day, which is the system working. It was done without
reading a single prior study, so it could rule designs out and could not rule one
in — it produced "the label-based study is not viable" and stopped at the nearest
answerable substitute.

Reading four papers moved the question again, to whether courts invoke an
expertise-keyed standard, which is a live argument in the literature (Leslie, 27
Cardozo L. Rev. 2713), is measurable from published text, and is immune to the
selection problem that the substitute design was not. It also surfaced the
omitted variable: exculpatory clauses appear in 71.1% of professionally serviced
trusts (Hofri-Winogradow, 68 Hastings L.J. 931), so any outcome gap between arms
has a drafting explanation before it has a conduct explanation.

**Size the pools and read the field in the same pass.** Sizing alone converges on
the nearest question the corpus can answer, which is rarely the best one.

### A table without its committed query is provisional
*Trustee scoping, 2026-09-02.* Two pool tables were committed as markdown by a
session whose queries lived only in its own scrollback. The numbers are probably
right and cannot be checked, which under this repository's own reporting rule —
*query, verbatim and runnable* — makes them provisional rather than findings.

The fix costs one file. Commit the sizing script with the sizing, always, even
when the sizing is exploratory and especially when it is about to be quoted in a
protocol.

### Courts state a rule in the treatise's words, not the statute's
*Trustee vocabulary sizing, 2026-09-02.* The heightened standard for a trustee
holding out expertise has four citeable forms, and UTC §806's own comment says
they are equivalent: UTC §806, UPC §7-302, Restatement (2d) of Trusts §174
(1959), UPIA §2(f).

Counted nationally across every court, the exact phrase the two uniform acts use
— *"special skills or expertise"* — appears in **88** opinions. Relaxed to
*"special skills"* and crossed with `trustee` it is **366**; the Restatement's
older wording adds *"greater skill"* **132** and *"special facilities"* **100**.
All four forms unioned and crossed with `trustee`: **1,748**.

A lane built on the enacted phrasing would have returned almost nothing and read
as evidence that courts do not apply the standard, when it is evidence about how
they phrase it. **Before building a retrieval lane on a statutory phrase, find
the provision's ancestry and count every form.** A uniform act's comment names
its own sources, so the ancestry is free.

**And count each candidate crossed with the thing being studied, never on its
own.** Counted alone, *"special facilities"* (786) and *"greater skill"* (668)
looked like they dominated the statutory phrasing nine to one. Crossed with
`trustee` they fall to 100 and 132, because most opinions using those words are
about something else entirely, and the relaxed statutory form turns out to be the
workhorse after all. A bare phrase count ranks vocabulary by how common the words
are in English, not by how much of it is yours.

Corollary, learned the same afternoon: **never put a bare section number in an
FTS query.** `7-302` matched 3,898 opinions — docket numbers, dates, and every
other code that happens to contain the string. Reach a provision through its
words.

### The marked category is the one courts name, and it is only ever one arm
*Trustee vocabulary sizing, 2026-09-02.* Corporate-side vocabulary nationally:
`corporate trustee` 2,572, `corporate fiduciary` 1,710, `professional fiduciary`
394, `professional trustee` 192, `institutional trustee` 134. Individual side:
`individual trustee` 994, `family trustee` 55, `lay trustee` 19,
`nonprofessional trustee` 16, `amateur trustee` **0**.

Roughly four to one. Courts **mark** the institution and leave the natural person
unmarked, because an unmodified "trustee" is presumed to be a person. So a design
that filters on labels builds one arm from what courts name and the other from
what they decline to name, and the asymmetry is a fact about usage rather than
about trustees.

**Whenever one arm of a comparison is a marked category and the other is the
default, label-based retrieval cannot supply both arms.** Identify the entity in
the role instead. The tell is cheap to check: count the vocabulary for each arm
before designing, and be suspicious of any ratio far from one.

Note also that the vocabulary the drafters use need not exist in the reports at
all. `amateur trustee` is the UPIA comment's own term for the low end and returns
zero. Use it to name the axis; never to query it.

### When one arm is richer, the arm is not the cause
*Trustee scoping, 2026-09-02.* The trustee study compares corporate against
individual trustees. A corporate trustee will not accept a small trust — fee
schedules and account minima see to that — so the corporate arm is drawn from the
top of the wealth distribution by construction and the individual arm from
everywhere.

Wealth is then a **common cause** of both the exposure and the outcome: it
predicts hiring a professional, and it predicts having enough at stake to sue
over. Any raw difference between the arms is a difference in trust size before it
is a difference in trustee behaviour.

Two mechanisms compound it, neither involving misconduct. **Deep pockets**:
beneficiaries sue defendants who can pay, and a bank is solvent, insured and
reachable where an individual trustee may be judgment-proof. **Category
composition**: a trustee who charges a fee generates fee litigation, and an
unpaid family trustee generates none, so part of any excess is a category that
does not exist in the other arm.

**Whenever the two arms of a comparison are separated by a price, code the price
and compare within bands.** And write down in advance what a null result would
mean, because here it is the likely one and it is more useful than the finding
originally sought: *trust size predicts litigation, trustee type does not* tells a
client that a corporate trustee does not buy them a lawsuit, which is the
question they were actually asking.
