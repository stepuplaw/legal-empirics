# Legal empirics

Empirical studies of published judicial opinions, mostly Florida, mostly estate
and trust law.

Run by **Kevin D. Klagge, Esq.** · [stepuplaw.com](https://stepuplaw.com) ·
[ORCID 0009-0002-1385-8498](https://orcid.org/0009-0002-1385-8498)

**Start with [STATE.md](STATE.md)** for where the project stands, what has been
run, and what is next.

**Read [METHODOLOGY.md](METHODOLOGY.md) before starting a study**, and
[CORPUS-LINGUISTICS.md](CORPUS-LINGUISTICS.md) if the question is about what
words mean or which words recur. It names the field, the standard method paper,
the reporting conventions, and the two threats that most often invalidate this
kind of work.

## The studies

| Study | Unit | Size | What it measures |
|---|---|---:|---|
| [`disputed-terms`](studies/disputed-terms/) | (term, decision) | 286,846 | which drafted words get litigated for ambiguity, across all 51 state appellate jurisdictions, and how often the challenge succeeds |
| [`reformation-fl`](studies/reformation-fl/) | decision | 932 | Florida reformation of wills, trusts, deeds, contracts and policies, 1853–2026, across three statutory regimes with dated breaks |
| [`statutory-staleness`](studies/statutory-staleness/) | (decision, section) | 19,085 | how much Florida case law construes a statute that has since changed — the gap a citator does not cover |
| [`ambiguity-pools`](studies/ambiguity-pools/) | decision | 6,523 | the feasibility study that produced the method, including the extraction that failed and why |

[`notebooks/`](notebooks/) holds the executed analyses, outputs included, so the
result is visible without running anything.

## Layout

    protocols/   one protocol per study, pre-registered before analysis
    studies/     one directory per study: build script, report, run manifest
    notebooks/   executed Jupyter analyses, outputs kept
    lib/         shared classifiers and helpers
    scripts/     the publishing pipeline
    dist/        exported dataset metadata; the data files themselves are not in git

## Where the data comes from

Queries go through **`~/caselaw/`**, the shared corpus pipeline, never by
opening `us-opinions.db` directly. That library owns the court-scope
definitions, the `?immutable=1` open and the block decoder, each of which has
been gotten wrong before by someone reinventing it. Its `fl` scope also resolves
to a local SSD slice, so most queries return in well under a second.

Set `CASELAW_HOME` if the pipeline is not at `~/caselaw`, and `US_LAW_DB` if the
statutes database is elsewhere.

⚠ The `?immutable=1` rule is for the opinion corpus, which is never written
during a query. Do **not** use it on `us-law.db` while a statute crawl is
running: the reader will report `database disk image is malformed` on a database
that is perfectly healthy.

## Data, and why none of it is in this repository

Every dataset here is derived, and every one is rebuilt by a script in this
repository. Git holds the code and the metadata that describes the data —
Frictionless datapackage, schema.org JSON-LD, MLCommons Croissant, with a
SHA-256 and a row count on every file. The data itself is published separately
as a citable dataset, which is also the form to cite.

[PUBLISHING.md](PUBLISHING.md) sets out where each piece lives and how the
records reference one another. Note that the research landing pages and the DOIs
are **not live yet**; the metadata files name their intended locations, and
`identifier` is left empty rather than filled with a placeholder DOI.

## Why this repository exists separately

These studies are not about estate tax, and the first one was living in the
estate tax dataset repo by accident. A study is a different kind of artifact
from a dataset: it has a protocol, a codebook, a reliability figure and a
limitations section, and it makes a claim rather than publishing a table.

## Standing rules

- **State the exclusion funnel with counts.** Silent filtering is the most
  common defect in opinion research.
- **Rates, never raw counts,** for anything over time. The corpus grew; a raw
  count measures the corpus.
- **Findings and hypotheses stay visibly separate.**
- **Say what would make this wrong,** in every study, naming selection effects
  and corpus coverage specifically.
- **Single-coded studies are exploratory** and must be labelled as such.
- **Never pool measures that point in opposite directions.** A holding that
  language is ambiguous and a holding that it is clear are different findings,
  and so are a grant and a denial of reformation.

## Citing this

[CITATION.cff](CITATION.cff) carries the machine-readable form and GitHub renders
it as a "Cite this repository" button. A DOI will be added once the first
archived release exists.

## Licence

CC BY 4.0 for text and derived data. Not legal advice; empirical research about
published opinions creates no attorney-client relationship.
