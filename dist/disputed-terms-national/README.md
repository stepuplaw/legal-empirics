---
license: cc-by-4.0
language:
- en
pretty_name: Disputed Contract and Instrument Terms in US State Appellate Courts
size_categories:
- 100K<n<1M
tags:
- legal
- law
- empirical-legal-studies
- contract-interpretation
- ambiguity
- corpus-linguistics
- legal-drafting
- empirical-legal-studies
- state-courts
configs:
- config_name: default
  data_files:
  - split: train
    path: disputed-terms-national.csv
---

# Disputed Contract and Instrument Terms in US State Appellate Courts

One row per (term, decision) pair: a word or phrase a court quoted as the disputed language in a decision containing an ambiguity holding, across the state appellate courts of all 50 states and DC. Terms are extracted from the whole opinion by cue-anchored quotation ('the term "X"', '"X" as used in'), classified into functional drafting categories, and linked to the holding by three graded levels of evidence.

**286,846 rows.** Licence CC BY 4.0. Not legal advice.

## Where this comes from

| | |
|---|---|
| Canonical record | https://doi.org/10.5281/zenodo.22247377 |
| Code and methodology | https://github.com/stepuplaw/legal-empirics |
| Research page | https://stepuplaw.com/research/ |
| Author | Kevin D. Klagge, [ORCID 0009-0002-1385-8498](https://orcid.org/0009-0002-1385-8498) |
| Source corpus | CourtListener bulk export, snapshot 2026-06-30 |

The DOI above identifies the **code**, which is a different object from this
dataset. Cite the code when you are describing the method and cite this dataset
when you are using the numbers.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `term` | string | the disputed language, lowercased and normalised, as the court quoted it |
| `category` | string | functional drafting class: nexus, degree, temporal, scope, modal, role, succession, property, event, conduct, condition, mental, uncategorised |
| `source` | string | the instrument the words sit in: testamentary, deed, insurance, contract, statute, constitution, uncertain |
| `posture` | string | found | rejected | alleged | uncertain -- whether the court held the language ambiguous |
| `link` | string | direct | proximate | inferred -- strength of the link between this term and the holding; inferred rows must not be pooled with the other two |
| `oid` | integer | CourtListener opinion id |
| `cid` | integer | CourtListener cluster id |
| `court` | string | CourtListener court id |
| `state` | string | two-letter state postal code |
| `year` | integer | year the decision was filed |
| `statement` | string | the row written as one self-contained English sentence, so it can be retrieved, quoted and checked on its own |

Every row carries a `statement` column, which is the row written as one
self-contained English sentence. A row of codes can be downloaded but not
retrieved or quoted, and the sentence is what makes each row usable on its own.

## How it was built

Retrieval and extraction are deterministic code over a local corpus of 10.8M US
judicial opinions. Classification uses rules written against a hand-coded sample
that ship with their measured accuracy, so the error rate is reported rather
than assumed. Every study states its exclusion funnel with counts, because
silent filtering is the commonest defect in research on opinions and it is
invisible in the result.

`datapackage.json` carries the Frictionless schema, `croissant.json` the
MLCommons Croissant description, and `dataset.jsonld` the schema.org form.

## Limits

**This is exploratory.** The coded samples behind it were coded once, so it
supports a described pattern rather than a measurement. Inter-annotator
reliability has not been established.

**Published appellate opinions are not disputes.** Most disputes settle, most
settlements are unpublished, and appellate coverage varies by court and decade.
Any rate here is a rate among decisions that reached an appellate court and were
published, which is not the same population a drafter cares about.

**Read the study's own limitations section** in the repository before quoting a
number. Each one names the specific threats to its own validity, including the
ones that are unflattering.
