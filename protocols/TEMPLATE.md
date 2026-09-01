# Protocol: <study name>

**Status:** draft | pre-registered | analysis complete
**Pre-registered:** <commit hash and date, once stage 1 to 5 are committed>
**Author:** Kevin D. Klagge, Esq. · ORCID 0009-0002-1385-8498

> Commit this file with stages 1 through 5 filled in **before** running the
> analysis. Fixing the question after seeing results is the mechanism behind
> most irreproducible findings, and a commit timestamp is the cheapest possible
> protection against doing it by accident.

## 1. Question

<One sentence. Answerable. Fixed before looking at the data.>

## 2. Population and corpus

- **Population of interest:** <the real-world thing, e.g. Florida will contests>
- **Corpus standing in for it:** CourtListener bulk, snapshot <date>
- **Court scope:** <e.g. fladistctapp, fla — state appellate only>
- **Date range:** <e.g. 1960-01-01 to 2026-06-30>
- **Gap between population and corpus:** <state it plainly; this is where
  selection effects enter>

## 3. Query

```
<verbatim, runnable, via ~/caselaw/clcorpus — never a hand-rolled DB open>
```

## 4. Exclusions

Applied in this order. Fill counts as the funnel runs.

| # | Rule | Rationale | N remaining | Dropped |
|---|---|---|---|---|
| 0 | Retrieved | — |  | — |
| 1 |  |  |  |  |
| 2 |  |  |  |  |

## 5. Codebook

Omit if nothing is coded, and then label the study descriptive.

| Variable | Values | Decision rule for hard cases |
|---|---|---|
|  |  |  |

**Reliability plan:** <double-code N% at random; report Cohen's kappa. If
single-coded, say so here and label the study exploratory.>

**Coder:** <human | named model with prompt | both>

---
<!-- Everything below is filled in AFTER the analysis runs. -->

## 6. Denominator

<Which decisions form the rate denominator, and why they are the right
comparison. Same courts, same years, or explain.>

## 7. Results

<Rates, not raw counts. Tables and figures.>

## 8. Interpretation

**Findings** — what the data shows.

**Hypotheses** — what might explain it. Kept visibly separate, and labelled as
untested.

## 9. Limitations

Address each explicitly; do not omit one because it is unflattering.

- **Selection effects:** <published appellate opinions are not disputes>
- **Corpus coverage:** <uneven digitisation across decades and courts>
- **Query validity:** <the text proxy vs the legal concept; false positives>
- **Coding:** <single-coded? reliability figure?>

## 10. Data availability

Derived CSVs committed alongside. Licence: CC BY 4.0.
