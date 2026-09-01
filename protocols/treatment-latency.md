# Protocol: treatment latency, or how long bad law stays citable

**Status:** draft
**Pre-registered:** not yet. Commit this file with stages 1 to 5 filled in, and
register it, **before** the first query runs.
**Author:** Kevin D. Klagge, Esq. · ORCID 0009-0002-1385-8498

> This protocol exists because the study has not been run. That is the only
> condition under which preregistration means anything. The three studies
> already in this repository were not preregistered and are labelled
> exploratory; registering them now, after the fact, would be a
> misrepresentation and is not being done.

## 1. Question

When a decision stops being good law, how long is it before a court says so,
and how many courts cite it as live authority in the meantime?

## 2. Population and corpus

- **Population of interest:** published US appellate decisions whose holding has
  been displaced, either by a later decision overruling them or by a statute
  superseding the rule they applied.
- **Corpus standing in for it:** CourtListener bulk export, snapshot 2026-06-30,
  topped up nightly, held locally. 10.8M opinions and **77.5M citation edges** in
  `citation_edges`, indexed on both `cited_id` and `citing_id`.
- **Court scope:** state appellate (jurisdiction codes `S` and `SA`) in all 50
  states and DC, plus the federal courts of appeals. Trial-court coverage is
  uneven by state and would make any cross-state comparison an artefact of
  ingest rather than a fact about the law.
- **Date range:** decisions of any date; citing activity measured through the
  snapshot date.
- **Gap between population and corpus:** a decision is only visible as displaced
  if some later opinion says so in words this study can match. Silent
  displacement is exactly what the statutory half is for, and even there the
  study sees only sections it can resolve to a citation.

## 3. Query

Two events, retrieved separately.

```
# A. Case-on-case displacement. The announcing opinion names the displaced case.
"receded from" OR "we recede" OR overruled OR "overrule our" OR disapproved
  OR "no longer good law" OR "abrogated by" OR "superseded by statute"
  OR "legislatively overruled" OR "statutorily overruled"

# B. Statutory displacement, Florida only, from studies/statutory-staleness.
#    A decision construing a section whose operative text later changed.
```

Both run through `~/caselaw/clcorpus`, never by opening the corpus directly.

## 4. Exclusions

Applied in this order. Counts filled as the funnel runs.

| # | Rule | Rationale | N remaining | Dropped |
|---|---|---|---|---|
| 0 | Retrieved on the displacement vocabulary | — |  | — |
| 1 | State appellate or federal appellate only | trial coverage is uneven by state |  |  |
| 2 | Announcing sentence names a case this corpus can resolve | an unresolvable name cannot be linked to an edge |  |  |
| 3 | Displaced case has a date and at least one citation edge | latency is undefined without both |  |  |
| 4 | Drop self-citations within one cluster | a case citing its own sibling opinion is not treatment |  |  |

## 5. Codebook

| Variable | Values | Decision rule for hard cases |
|---|---|---|
| `displacement_type` | case \| statute | statute only where the staleness dataset supplies a text change, not merely an amendment |
| `scope` | full \| partial | "receded from X to the extent that" is partial. Where the opinion does not say, code partial, because it is the conservative reading |
| `citing_purpose` | for_displaced_point \| other \| unclear | the citing sentence must engage the displaced proposition. A string cite or a citation for an unrelated holding is `other` |
| `latency_years` | integer | announcing decision date minus displaced decision date. For the statutory half, effective date of the amendment |
| `exposure_count` | integer | citations to the displaced case dated after displacement and before announcement |

**Reliability plan:** `citing_purpose` is the variable the finding depends on and
the only one requiring judgment. Double-code 100 randomly drawn citing sentences
and report Cohen's kappa **before** any headline rate is published. If kappa is
not computed, the study is labelled exploratory and reports counts only.

**Coder:** deterministic rules for retrieval and edge counting; a named model
with a committed prompt for `citing_purpose`; a human second coder on the
reliability sample.

---
<!-- Everything below is filled in AFTER the analysis runs. -->

## 6. Denominator

Latency is reported per displaced case. Exposure is reported as a **rate against
the same case's citation count in an equal window before displacement**, not as a
raw count, because a heavily cited case will accumulate post-displacement
citations for reasons that have nothing to do with the displacement.

## 7. Results

To be completed.

## 8. Interpretation

To be completed. Findings and hypotheses stay visibly separate.

## 9. Limitations

To be addressed explicitly, and none omitted for being unflattering.

- **Selection effects:** displacement is only observable when a court announces
  it. The silent cases are the interesting ones and are systematically missing
  from the case half of the study.
- **Corpus coverage:** the citation graph is only as complete as CourtListener's
  extraction. Missed edges bias exposure downward.
- **Query validity:** `overruled` appears constantly in opinions that are
  reporting the trial court overruling an objection. This is the single largest
  false-positive risk and the funnel must show what it removed.
- **Citation purpose is the whole study.** A citation to a displaced case is not
  evidence of error unless it is cited for the displaced proposition. The
  Florida reformation pilot makes the point: 209 citations since 2011 to
  decisions stating a rule the legislature reversed, of which 165 belong to a
  single 1961 case almost certainly cited for something else entirely.
- **Coding:** see the reliability plan. Single-coded means exploratory.

## 10. Data availability

Derived CSV published under CC BY 4.0 with a DOI, and described in Frictionless,
schema.org and Croissant form alongside.
