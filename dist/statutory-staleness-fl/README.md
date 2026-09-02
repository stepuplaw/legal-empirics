---
license: cc-by-4.0
language:
- en
pretty_name: Statutory Staleness in Florida Appellate Construction Holdings
size_categories:
- 10K<n<100K
tags:
- legal
- law
- empirical-legal-studies
- statutory-interpretation
- abrogation
- citator
- legal-research
- empirical-legal-studies
- Florida
configs:
- config_name: default
  data_files:
  - split: train
    path: statutory-staleness-fl.csv
---

# Statutory Staleness in Florida Appellate Construction Holdings

One row per (decision, statutory section) pair where a Florida appellate court construed the meaning of a Florida statute, with whether that section has been amended since the decision and, where two editions of the code are held, whether the operative text actually changed. A citator reports whether a case was overruled by another case; it is far weaker on the other way a holding dies, which is that the legislature amended the statute and no court has had occasion to say so. This dataset measures that gap directly.

**19,085 rows.** Licence CC BY 4.0. Not legal advice.

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
| `oid` | integer | CourtListener opinion id |
| `cid` | integer | CourtListener cluster id |
| `name` | string | case name as reported |
| `court` | string | CourtListener court id |
| `year` | integer | year the decision was filed |
| `cites` | integer | times the decision has been cited, per CourtListener |
| `section` | string | Florida Statutes section construed, e.g. 732.615 |
| `last_amended` | integer | most recent amendment year in the section history trail |
| `amendments_since` | integer | count of amendments after the decision |
| `gap_years` | integer | years between the decision and the most recent later amendment |
| `exposed` | integer | 1 where the section was amended after the decision; an UPPER BOUND, not a finding of abrogation |
| `tier` | string | amendment-screen | text-diff -- text-diff is only available where an edition at or before the decision year is held |
| `text_changed` | integer | 1 where the operative text differs between the edition in force at the decision and the current edition; null outside the text-diff tier |
| `similarity` | number | SequenceMatcher ratio between the two editions operative text, history trail excluded |
| `edition_at_decision` | integer | the statute edition used as the baseline for the diff |
| `sentence` | string | the sentence in which the section was construed, verbatim |
| `statement` | string | the row written as one self-contained English sentence |

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
