---
license: cc-by-4.0
language:
- en
pretty_name: Florida Reformation of Instruments, 1853-2026
size_categories:
- n<1K
tags:
- legal
- law
- empirical-legal-studies
- reformation
- scriveners-error
- wills
- trusts
- deeds
- legal-drafting
configs:
- config_name: default
  data_files:
  - split: train
    path: reformation-fl.csv
---

# Florida Reformation of Instruments, 1853-2026

Every Florida state appellate decision litigating the reformation of a legal instrument -- will, trust, deed, contract or insurance policy -- with the instrument type, the kind of drafting error alleged, the outcome, and which statutory regime was in force. Florida authorised trust reformation in 2007 (s. 736.0415) and will reformation in 2011 (s. 732.615); before those dates the remedy rested on equity, and for wills was unavailable entirely. The dataset makes that break observable within one jurisdiction.

**932 rows.** Licence CC BY 4.0. Not legal advice.

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
| `cid` | integer | CourtListener cluster id; one decision may hold several opinions |
| `name` | string | case name as reported |
| `court` | string | CourtListener court id (fla = Supreme Court of Florida, fladistctapp = District Courts of Appeal) |
| `year` | integer | year the decision was filed |
| `cites` | integer | times the decision has been cited, per CourtListener |
| `instrument` | string | will | trust | deed | contract | insurance | uncertain |
| `outcome` | string | granted | denied | sought | rule_stated | authority | uncertain -- see the codebook; only granted and denied are holdings |
| `regime` | string | statutory | pre-statute | equitable | unknown -- which reformation regime governed that instrument on that date |
| `errors` | string | comma-separated error types alleged; multi-label by design |
| `n_reform_sents` | integer | count of reformation sentences found in the opinion |
| `cites_statute` | integer | 1 where the opinion cites s. 732.615, s. 732.616 or s. 736.0415 |
| `key_sentence` | string | the sentence the outcome label was read from, verbatim |
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
