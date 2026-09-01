# Legal empirics

Empirical studies of published judicial opinions, mostly Florida, mostly estate
and trust law. Run by [Kevin D. Klagge, Esq.](https://stepuplaw.com),
[ORCID 0009-0002-1385-8498](https://orcid.org/0009-0002-1385-8498).

**Read [METHODOLOGY.md](METHODOLOGY.md) before starting a study**, and
[CORPUS-LINGUISTICS.md](CORPUS-LINGUISTICS.md) if the question is about what
words mean or which words recur. It names the
field, the standard method paper, the reporting conventions, and the two threats
that most often invalidate this kind of work.

## Layout

    protocols/   one protocol per study, pre-registered before analysis
    studies/     the notebooks, one directory each
    data/        derived CSVs, the reusable output
    lib/         shared helpers

## Where the data comes from

Queries go through **`~/caselaw/`**, the shared corpus pipeline, never by
opening `us-opinions.db` directly. That library owns the court-scope
definitions, the `?immutable=1` open and the block decoder, each of which has
been gotten wrong before by someone reinventing it. Its `fl` scope also resolves
to a local SSD slice, so most queries return in well under a second.

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

## Licence

CC BY 4.0 for text and derived data. Not legal advice; empirical research about
published opinions creates no attorney-client relationship.
