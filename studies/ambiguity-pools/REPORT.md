# Separating testamentary from statutory ambiguity

**A contrastive pool study over Florida appellate opinions**

Kevin D. Klagge, Esq. · [ORCID 0009-0002-1385-8498](https://orcid.org/0009-0002-1385-8498)
Run 2026-09-01 · Status: **exploratory, single-coded** · Licence CC BY 4.0

---

## Summary

"Ambiguity" is not one doctrine. Florida courts use the word for statutory
interpretation, contract construction, and the construction of wills and trusts,
and those are unrelated bodies of law sharing vocabulary. Any study that queries
the word without separating them measures the canons of statutory construction
and calls it estate law.

This run built four pools from the same corpus and used each as a contrast set
for the others. Two results:

1. **Document-level co-occurrence overstates contamination by about threefold.**
   Requiring the doctrinal vocabulary in the *same sentence* as the ambiguity
   term recovers 135 usable cases where a document-level subtraction had kept
   only 72.
2. **The doctrines separate cleanly at the vocabulary level.** A log-likelihood
   keyness comparison produces a coherent, interpretable marker list with no
   hand-tuning: *testator*, *trust*, *codicil*, *devise*, *testatrix*, *latent*,
   *extrinsic*, *admissible*, *probate*.

A third result is negative and is reported as such: extracting the disputed
instrument language from within ambiguity sentences **does not work**. The
window is wrong.

---

## 1. Business understanding (CRISP-DM stage 1)

**Question, fixed before the run.** Can testamentary ambiguity be separated from
statutory and contract ambiguity reliably enough to support a study of the
former, and if so, what vocabulary marks the boundary?

This is a **feasibility study for a method**, not a substantive finding about
law. Its output is a query and a filter, to be used by a later study.

## 2. Data understanding (stage 2)

- **Corpus:** CourtListener bulk, source snapshot 2026-06-30, accessed through
  `~/caselaw/clcorpus` at `beastmode-data/fl-opinions.db`.
- **Court scope:** `fladistctapp` and `fla`, the Florida District Courts of
  Appeal and the Supreme Court of Florida. State appellate only.
- **Unit:** the cluster (one decision), not the opinion, so a decision with a
  dissent counts once.

## 3. Data preparation (stage 3)

### Pools

| Pool | Query | N |
|---|---|---|
| ambiguity, any | `ambiguous OR ambiguity OR ambiguities` | 6,523 |
| statutory | `(ambiguous OR ambiguity) AND (statute OR statutory OR "legislative intent" OR "plain meaning" OR "rules of statutory construction")` | 3,491 |
| contract | `(ambiguous OR ambiguity) AND (contract OR "insurance policy" OR lease OR indemnity OR "purchase agreement")` | 2,862 |
| testamentary | `(ambiguous OR ambiguity) AND ("last will" OR testament OR codicil OR "trust instrument" OR devise OR bequest OR "residuary")` | 216 |

Ambiguity language appears in 6,523 Florida appellate decisions. Only 216
co-occur with testamentary vocabulary anywhere in the document. The word is
overwhelmingly not about wills.

### Exclusion funnel

| Stage | N | Dropped | Reason |
|---|---|---|---|
| Testamentary pool, document level | 216 | — | retrieval |
| Sentence-level classification applied | 216 | 0 | every case had ≥1 ambiguity sentence |
| Classified statutory | 188 | 28 | ambiguity sentences statutory, none testamentary |
| Classified contract | 177 | 11 | ambiguity sentences contractual, none testamentary |
| Classified unclear | 135 | 42 | no doctrinal vocabulary in any ambiguity sentence |
| **Retained** | **135** | | ≥1 ambiguity sentence with testamentary vocabulary and no competing doctrine |

### The finding that changed the method

A document-level subtraction (`testamentary − statutory − contract`) retains
**72** cases. Sentence-level classification retains **135**.

The reason is that a testamentary case routinely cites a statute somewhere in
the opinion without the ambiguity analysis being statutory. Reading a random
sample of 12 overlap cases, ambiguity sentences carried statutory vocabulary in
the same sentence only **17%** of the time, against **39%** carrying
testamentary vocabulary.

**Document-level co-occurrence is the wrong instrument.** It discards roughly
half of a small and valuable pool.

## 4. Modelling (stage 4)

### Classification rule

Deterministic and rule-based, applied per sentence containing `ambigu\w+`:

- testamentary vocabulary present and no statutory or contract vocabulary → testamentary
- statutory present and testamentary absent → statutory
- contract present and testamentary absent → contract
- testamentary present alongside another → testamentary
- otherwise → unclear

A case is retained if any of its ambiguity sentences classifies as testamentary.

### Keyness

Dunning log-likelihood (G²) over unigrams, target being the 452 ambiguity
sentences from the retained cases, reference being 862 ambiguity sentences from
statutory cases not retained. Log-likelihood is preferred to mutual information,
which over-rewards rare terms, and to raw ratio, which is unstable on low counts.

## 5. Evaluation (stage 5)

### Markers of testamentary ambiguity

| Term | Target | Reference | G² |
|---|---|---|---|
| testator | 88 | 0 | 185.3 |
| trust | 82 | 2 | 155.5 |
| estate | 43 | 2 | 75.9 |
| latent | 83 | 29 | 71.5 |
| codicil | 30 | 0 | 63.2 |
| devise | 29 | 0 | 61.1 |
| testatrix | 29 | 0 | 61.1 |
| extrinsic | 70 | 29 | 52.5 |
| instrument | 38 | 6 | 50.1 |
| intention | 36 | 5 | 49.7 |
| admissible | 32 | 6 | 39.4 |
| probate | 18 | 0 | 37.9 |

The list is coherent without hand-tuning, which is the evidence that the pools
genuinely separate. **`latent` and `extrinsic` are doctrinally interesting**:
both rank high but appear substantially in the statutory reference too, which is
what one would expect of the latent-ambiguity rule admitting extrinsic evidence.
That the method recovers a known doctrinal relationship it was not told about is
a partial validity check.

### Negative result: span extraction

Extracting quoted spans from **within** ambiguity sentences yielded 70 tokens
across 60 types, and most are doctrinal terms (`latent ambiguity`, `patent`)
rather than instrument language. One genuine hit: *"draftsman's formula [which]
requires distribution of seven shares."*

**The window is wrong.** Courts quote the disputed provision in the facts, often
pages before the sentence that calls it ambiguous. Extraction has to run over
the whole opinion with the ambiguity finding used to select the *case*, not the
*sentence*. That is the fix for the next run.

## 6. Limitations

- **Single-coded, no reliability figure.** No second coder, no kappa. This is
  exploratory and is labelled so.
- **The classifier is a lexical proxy.** It detects vocabulary, not reasoning. A
  court discussing a will's ambiguity without using any listed term is missed.
- **42 unclear cases were dropped**, roughly a fifth of the pool. Some are
  probably testamentary. The retained set is a lower bound.
- **Selection effects.** Published appellate opinions are not disputes. Nothing
  here speaks to how often instruments are ambiguous, only to how often an
  appellate court said so in a published opinion.
- **Reference corpus is capped** at 400 statutory cases for runtime. A different
  cap would shift G² magnitudes, though not plausibly the rank order.

## 7. Method disclosure

**No language model performed any classification, coding, or extraction in this
study.** Every step is deterministic: SQL, FTS5 queries, regular expressions,
and a log-likelihood calculation. Re-running the code reproduces the numbers
exactly. There is therefore no model-variance question and no model-versus-human
reliability question for the results above.

A language model (Claude, Fable 5) was used to *write* the queries, the code and
this report, and to choose the vocabulary lists. Those choices are researcher
degrees of freedom and are disclosed as such: the term lists in section 3 and
the classification rule in section 4 are stated verbatim so they can be
criticised or varied. Token consumption for the authoring session is not
instrumented and is not reported rather than being estimated.

## 8. Deployment (stage 6)

The retained cluster list and the marker vocabulary become inputs to the next
study. Concretely, the refined retrieval for testamentary construction is the
document-level query in section 3 **plus** the sentence-level filter in
section 4, and the section 5 markers can be fed back as additional seed terms.

## 9. What this is called

The design composes three established techniques, none invented here:

- **Contrastive or reference corpus analysis**, from corpus linguistics, where a
  term's *keyness* is its overrepresentation against a named reference corpus.
- **Bootstrapping**, in the DIPRE and Snowball lineage from information
  extraction, where seed terms find patterns and patterns yield better seeds.
- **Relevance feedback**, from information retrieval, where results refine the
  query that produced them.

Running several pools with different objectives over one corpus so that each
serves as the other's negative set is best described as **contrastive pool
construction with relevance feedback**. Naming the parts matters for reporting,
because each is separately criticisable and a reader who knows one knows what to
attack.

## 10. Data availability

Cluster ID lists and the keyness table are committed alongside. CC BY 4.0. Not
legal advice.
