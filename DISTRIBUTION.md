# Distribution checklist

_Live document. Update the status column as things land._

The goal is not "how many platforms can we be on". It is **how many independent,
reputable systems legitimately identify and connect the same person, the same
work and the same data**. Ten mirrors of one CSV with no differentiation reads as
spam and dilutes the signal. Three that reach genuinely different audiences, each
pointing back at the canonical record, does the job.

**One canonical record, several distributions.** Zenodo holds the citable
identity. Everything else is a copy that names it.

---

## Status

| # | Platform | Status | What it buys |
|---|---|---|---|
| 1 | ORCID | **done** 2026-09-01 | person identity from an independent registry |
| 2 | GitHub | **done** | code, notebooks, version history |
| 3 | stepuplaw.com/research/ | **done** 2026-09-02 | canonical human page, schema.org Dataset markup |
| 4 | Zenodo | **done** 2026-09-02, concept `10.5281/zenodo.22247377` | the DOI. Feeds DataCite, which auto-populates ORCID |
| 5 | Hugging Face | **account ready** (`stepuplaw`, write token saved) | reaches ML and AI people; Croissant makes data loadable, not just downloadable |
| 6 | Google Dataset Search | **automatic** | harvests the schema.org markup already on /research/ |
| 7 | DataCite / OpenAIRE / OpenAlex | **automatic once the DOI exists** | three more independent systems, no extra work |
| 8 | Kaggle | **metadata built**, needs `~/.kaggle/kaggle.json` | large data-science audience, Croissant support, Google-owned so it indexes well |
| 9 | OSF | **protocol drafted** for the next study, needs an OSF token | **preregistration**, which `protocols/` already assumes |
| 10 | SSRN | not started | where legal academics and practitioners actually look |
| 11 | Wikidata | not started | knowledge-graph node. Do it for a DATASET, after the DOI |
| 12 | Google Scholar profile | not started | links publications to the ORCID |
| 13 | llms.txt + Markdown twins | not started | cheap, unproven, do last |
| 14 | ISNI | deprioritised | usually assigned via a registration agency, duplicates ORCID |

---

## Blocking, in order

1. **Cut the GitHub release** (`v0.1.0`). Everything below waits on the DOI.
2. Fill the DOI into `CITATION.cff`, the datapackages, the Croissant files, the
   JSON-LD and the research page.
3. Host the CSVs. Until then no platform gets a download link, because a
   `distribution` pointing at a file that does not exist sends every harvester
   to a 404.
4. Push the three datasets to Hugging Face with a card that names the DOI, the
   repo and the research page.

---

## Per-platform notes

### Kaggle
Free, large audience, and it reads Croissant, which we already emit. Google owns
it, so a dataset page there is indexed well. It is a **distribution channel, not
an identity anchor**, so the card must point at the DOI rather than pretending to
be the canonical record. Low effort, do it after Hugging Face.

### OSF
The one nobody thinks of and the best fit for this project's own standards.
`METHODOLOGY.md` requires a protocol written before analysis, and `protocols/`
exists for exactly that. OSF is where preregistration is normally recorded, with
a timestamp nobody can quietly revise. That converts "we pre-registered" from a
claim into a record, which is worth more than another dataset mirror.

### SSRN
For a legal audience this outranks every data platform on the list. Lawyers and
law professors search SSRN; they do not search Hugging Face. It wants a paper
rather than a dataset, so it is gated on writing one. The reformation study is
the obvious first candidate because it is bounded, Florida-specific and has a
clean natural experiment in it.

### Harvard Dataverse
A credible second home for social-science and legal datasets, with its own DOI.
Consider it only if the audience is academic; otherwise it duplicates Zenodo.
Redundancy across two DOI-minting repositories is a mild negative, not a
positive, because it splits the citation count.

### Wikidata
Create the item for a **dataset with a DOI**, never for the practice. A dataset
with a DOI is a defensible item that survives review; a small firm probably
fails notability, and a deleted item is a worse signal than no item. The dataset
item carries an author property pointing at the ORCID, which puts the person into
the graph legitimately.

### llms.txt and Markdown twins
`llms.txt` is a convention, not a standard, and no major system has committed to
reading it. It costs almost nothing so it is worth having, but it should not be
mistaken for an indexing mechanism. The stronger version of the same idea is a
Markdown twin of every research page at a predictable URL, which helps text
extraction whether or not any crawler adopts the convention.

---

## What NOT to do

- **Do not mirror the same CSV to every platform that accepts uploads.** Pick the
  ones whose audiences differ and let the rest be links.
- **Do not mint a second DOI for the same dataset** at another repository. It
  splits citations and looks like padding.
- **Do not publish a download link before the file exists.** A 404 in a
  `distribution` field is worse than an absent field.
- **Do not create Wikidata items for the practice or its pages.** That is the
  fastest route to a deletion discussion, which is a negative signal that is
  hard to undo.
