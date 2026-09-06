# Protocol: Florida local code finder

**Status:** analysis complete
**Pre-registered:** descriptive census, not a hypothesis test. See stage 5.
**Author:** Kevin D. Klagge, Esq. · ORCID 0009-0002-1385-8498

## 1. Question

For each of Florida's 478 local governments with ordinance power, where is its
code of ordinances published online, who publishes it, and how current is it?

## 2. Population and corpus

- **Population of interest:** every Florida county and municipality, that is
  every local government that adopts ordinances under Fla. Stat. ch. 125 or
  ch. 166.
- **Frame standing in for it:** the Census Bureau subcounty population file
  `sub-est2024_12.csv`, vintage 2024, which enumerates 67 counties and 411
  incorporated places. That count matches the Florida League of Cities
  directory, which is the independent check on the frame.
- **Sources surveyed:** the Municode public API, the American Legal Publishing
  Florida region listing, the General Code eCode360 library, and the
  jurisdiction's own website for anything the codifiers do not carry.
- **Date of survey:** 2026-09-03.
- **Gap between population and frame:** the Census frame counts incorporated
  places. It excludes special districts, community development districts and
  county constitutional officers, several of which publish codes through the
  same vendors. Those are visible in the raw cache and deliberately not rows,
  because a reader looking for "the code of ordinances for X" means the
  general-purpose government.

## 3. Query

```
python3 studies/fl-local-codes/build_dataset.py
```

Sources, all public and unauthenticated:

```
https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/cities/totals/sub-est2024_12.csv
https://api.municode.com/Clients/stateAbbr?stateAbbr=FL
https://api.municode.com/ClientContent/{ClientID}
https://api.municode.com/Jobs/latest/{productId}
https://library.municode.com/localapi/Organizations/GetByUrlEncodedNames/fl/{slug}/
```

Requests are held to one per second with an identifying User-Agent, and every
response is cached so a rerun makes no network calls. Only metadata is
retrieved. No ordinance text is downloaded, stored or republished.

## 4. Exclusions

| # | Rule | Rationale | N remaining | Dropped |
|---|---|---|---|---|
| 0 | Census places and counties, Florida | the frame | 478 | 0 |
| 1 | Municode clients that are not general-purpose governments | a hospital district, a water management district, two clerks of court, a university student government and a services district are not municipalities | 478 | 8 clients, not rows |
| 2 | Municode clients with no published code product | membership is not publication; `ClientContent` returns an empty `codes[]` for some clients | 478 | see funnel |

Counts are written to `studies/fl-local-codes/fl-local-codes-run.json` on every
run.

## 5. Codebook

Descriptive. Nothing is coded from prose, so there is no reliability figure to
report, and the study is labelled descriptive rather than exploratory. The one
judgment call is `code_status`, and its rule is mechanical.

| Variable | Values | Decision rule |
|---|---|---|
| `code_status` | online-html | a codified code, served as browsable web pages |
| | online-pdf-only | a codified code, available online only as a PDF |
| | ordinances-only | individual ordinances are published online but have never been codified into a compilation |
| | no-online-code | the official site was read and publishes neither a code nor its ordinances |
| | unknown | no codifier carries it and the survey could not establish what it publishes; the note records what was checked |
| `publisher` | municode, american-legal, general-code, code-publishing, municipal-code-online, elaws, self-hosted, none, unknown | who serves the document at `code_url` |
| `official_status` | official, unofficial, unstated | only where the code or the codifier says so on the page |

`ordinances-only` is the distinction the study exists to draw. A town that posts
its ordinances one PDF at a time has published its law without codifying it, and
answering a question about fences there means reading every ordinance the town
ever passed. Folding those in with the towns that publish a code would hide the
commonest condition in rural Florida.

**Coder:** the build script for every Municode row. A human in a browser for
every row the codifiers do not carry, recorded in `manual.tsv` and committed.

**Two traps that make a mechanical join wrong, both found by probing:**

1. Municode's `ClassificationId` does not encode jurisdiction type. Palmetto
   Bay is 9, Jacksonville is 3, and 80 municipalities sit in 6. Type is taken
   from the Census and never from the vendor.
2. `library.municode.com/fl/<anything>` returns HTTP 200 with a JavaScript
   shell for slugs that do not exist, so a status code cannot verify a URL.
   Every Municode URL in this dataset is verified against the resolver the
   library page itself calls, which returns the client id, and the check is
   recorded in the `checks` table.

## 6. Denominator

All 478 Florida local governments. Coverage rates are reported against that
denominator and separately for counties and for municipalities, because a
county code and a village code are not equally likely to exist.

## 7. Results

Survey date 2026-09-04. All 478 rows, so these are census counts and no
inference is involved.

| Outcome | N | Share |
|---|---:|---:|
| Codified code online, web | 414 | 86.6% |
| Codified code online, PDF only | 9 | 1.9% |
| Ordinances published, never codified | 9 | 1.9% |
| Nothing published online | 2 | 0.4% |
| Could not be confirmed | 44 | 9.2% |

By level of government, 61 of 67 counties and 362 of 411 municipalities publish
a codified code online.

Publishers: Municode 400, self-hosted 18, American Legal Publishing 10,
MunicipalCodeOnline 3, General Code 1, none 2, undetermined 44.

Currency: 1,223 adopted ordinances are awaiting codification across Florida.
16 codes were last codified more than three years ago. A further 15 state a
codification date that falls after the supplement carrying it was published,
which is impossible; those are recorded as notes rather than as dates.

Four findings that no existing list records:

1. **Municode's Florida client list is incomplete.** Lighthouse Point resolves
   in the Municode library as client 3021 and is absent from
   `Clients/stateAbbr?stateAbbr=FL`. Trusting that list alone would have
   published "no online code" for a city whose code is one click away.
2. **A Municode client record is not a published code.** Nine Florida clients
   carry no code product, and three more carry a product whose library address
   no longer resolves. Three of those towns have moved to MunicipalCodeOnline,
   a publisher no law library research guide lists.
3. **A hidden code still serves.** Lighthouse Point's Municode code is flagged
   `hideInLibrary`, was last updated in 2018 and has 60 ordinances pending,
   while the city has since rewritten its code and hosts it elsewhere. The
   Municode page still loads and search engines still index it, with nothing on
   the page to say it is superseded.
4. **Codification is not the same as publication.** Nine jurisdictions publish
   their ordinances without ever compiling them.

## 8. Interpretation

**Findings** are coverage and currency counts. They are census figures, not
estimates, so no inference is involved.

**Hypotheses**, untested and labelled as such: population predicts whether a
municipality publishes a code online, and codification currency tracks whether
the jurisdiction pays for a supplement service rather than jurisdiction size.

## 9. Limitations

- **Point in time.** Codifier contracts move. A jurisdiction that appears here
  as self-hosted may be on a vendor next year. Every row carries the date it
  was checked, and that date is the claim.
- **Currency is the codifier's word.** `codified_through` is parsed from the
  banner the publisher displays. It reports when the code was last compiled,
  not whether the compilation is correct or complete.
- **Official status is mostly unstated.** Florida codes rarely say on the page
  whether the online version is official. The column records what the page
  says and does not infer.
- **General Code coverage is thin here.** The eCode360 library index sits
  behind a bot challenge that this survey does not attempt to circumvent, so
  the one General Code jurisdiction found, South Pasadena, was identified from
  a search rather than from the vendor's index. That is a gap in method rather
  than a gap that was measured.
- **44 rows are unconfirmed and are not a finding of absence.** No codifier
  carries them and the survey could not establish what they publish instead.
  They are almost all municipalities under 1,000 people. Two things blocked
  completion: the browser tooling requires per-domain permission that was not
  available for the long tail, and many of these towns run JavaScript-rendered
  sites that return nothing to a scripted reader. Every such row records what
  was checked, so the next pass starts where this one stopped. Reporting them
  as "no online code" would have been the single most damaging error available,
  because it asserts an absence about a real government.
- **Guessed domains were rejected, not recorded.** An early pass tried to find
  town websites by pattern and accepted an HTTP 200. It matched a domain
  squatter for Punta Gorda and Trenton, Ohio for Trenton, Florida. Nothing from
  that pass survives. The same test later caught Greenwood, Wisconsin posing as
  Greenwood, Florida on a wildcard subdomain.
- **No ordinance text.** This dataset says where the law is, never what it
  says. A reader still has to read the code.

## 10. Data availability

CSV, Parquet, Frictionless datapackage, schema.org and Croissant metadata in
`dist/fl-local-codes/`. Licence CC BY 4.0 for the compilation. The underlying
ordinances are edicts of government and carry no copyright, per Georgia v.
Public.Resource.Org, 590 U.S. 255 (2020).
