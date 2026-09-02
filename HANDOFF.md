# Handoff, 2026-09-02

_Session summary. Read `STATE.md` for what the research says, `NEXT-PROJECTS.md`
for what to build next, and this file for where everything is and what is stuck._

---

## What exists now, and where

| Node | Identifier / URL | State |
|---|---|---|
| GitHub | `github.com/stepuplaw/legal-empirics` | main pushed, 3 releases, topics + description set |
| Zenodo concept DOI | **10.5281/zenodo.22247377** | resolves to newest version |
| Zenodo version DOI | 10.5281/zenodo.22247378 | the `v0.1.2` release |
| DataCite | registered via Zenodo | ORCID attached to the creator |
| ORCID | `0009-0002-1385-8498` | bio, 6 keywords, country, employment, 1 work |
| Website | `stepuplaw.com/research/` | live, 3 schema.org `Dataset` nodes |
| Hugging Face | `huggingface.co/StepUpLaw` | 3 datasets, CSV + Parquet + Croissant + cards |
| Kaggle | `kaggle.com/stepuplaw` | 3 datasets |
| OpenML | `openml.org/d/47289` | FL-Stale benchmark |

**Cite the concept DOI in prose.** Use the version DOI when pinning a number to
the exact release it came from.

## The datasets

| Dataset | Rows | CSV | Parquet |
|---|---:|---:|---:|
| disputed-terms-national | 286,846 | 80.5 MB | 13.5 MB |
| statutory-staleness-fl | 19,085 | 11.9 MB | 4.4 MB |
| reformation-fl | 932 | 0.6 MB | 0.2 MB |
| FL-Stale benchmark | 1,500 items | — | — |

Data is **not in git**. It is derived, rebuilt by the scripts, and published as
citable datasets. `.gitignore` enforces this; the repo is 1.3 MB.

## Corpus

`us-law.db` holds **30 Florida Statutes editions, 1997 to 2026**. Both crawls
finished. That is what makes the text-diff tier of the staleness study possible.

---

## Blocked, each on one credential

**Wikidata.** The item is prepared at `wikidata/legal-empirics.qs` and has never
been run. QuickStatements and wikidata.org both failed to reach `document_idle`
for the browser extension across many attempts, so this is a tooling failure and
not a login problem. The reliable path is the API:

1. `https://www.wikidata.org/wiki/Special:BotPasswords`, name it `legal-empirics`
2. Tick **Edit existing pages** and **Create, edit, and move pages**
3. Hand the credential over; the item and the conflict-of-interest user page go
   up in one call

★ Put the disclosure on `User:StepUpLaw` **before** the item. The account name
matches the subject, and an undisclosed conflict is what gets an item deleted.

**OSF.** Nothing is registered. `protocols/treatment-latency.md` is drafted as
preregistration material, stages 1 to 5 filled and results blank, which is the
only honest state for a study that has not run. Needs a token from
`https://osf.io/settings/tokens` with `osf.full_write`.

**ORCID education.** Employment saved as Owner @ StepUpLaw, Miami. Education is
not added. Suffolk University Law School J.D. 2012 and Boston University B.S.
2007, per the site bio. Needs a working browser session.

---

## Credentials on this machine

All `600`, all outside any git repo.

    ~/.cache/huggingface/token   ~/.huggingface.env
    ~/.kaggle/access_token       ~/.kaggle.env
    ~/.openml/config             ~/.openml.env

**Rotate all three.** Every one has appeared in a chat transcript, and the
Hugging Face token carries write scope on the account.

---

## Next, in order

1. **Re-run statutory-staleness.** One command, and it is the largest available
   improvement to a published result. Text-diff coverage goes from 5.3% of pairs
   to roughly 58%, and the 69.5% discount gets measured across three decades
   instead of four years. Then cut `v0.2.0` for its own version DOI.

       python3 studies/statutory-staleness/build_dataset.py
       python3 -m nbconvert --execute --to notebook --inplace notebooks/statutory-staleness.ipynb

2. **Per-dataset landing pages** at `/research/<name>/`. The single biggest
   structural gap. Google Dataset Search works far better with one canonical
   page per dataset than with three `Dataset` nodes on one page, and it unlocks
   the data dictionary and derived-dataset pages cheaply, because the field
   descriptions already exist in `datapackage.json`.

3. **Run the USC reload.** `build-usc.py` was fixed to populate `history` from
   the GovInfo amendment notes and **the reload was never run**. All five title
   zips are cached locally, so it is local reparse with no download.

4. **Cohen's kappa.** Still the cheapest step with the largest effect. Every
   study is exploratory until one 50-item set is double-coded.

5. See `NEXT-PROJECTS.md` for the scoped candidates, including the trustee study
   and why its question had to change.

---

## Traps this session paid for, so nobody pays twice

**Corpus and storage**

- Reading `us-law.db` with `?immutable=1` **while a crawl is writing** reports
  `database disk image is malformed` on a perfectly healthy database.
  `PRAGMA quick_check` says `ok`. Drop the flag during ingests.
- `us-law.db` takes **one writer**. Queue statute ingests behind each other.
- On the external platter, **scan tables, do not probe them**. Driving a join
  from 486k hit ids is 486k seeks at 14 ms and runs for two hours; reading the
  tables start to finish takes under a minute.
- A national in-memory map of 6.7M opinion ids gets the process OOM-killed on
  this box. Stage per pool instead.

**Retrieval**

- A `NEAR` with the terms quoted together reads as a **single phrase**. It
  returned 16 Florida decisions for breach of fiduciary duty, the most litigated
  claim in American law.
- **`will` is an auxiliary verb.** Matching it bare put *Gore v. Harris*, the
  Bush v. Gore litigation, into a dataset about testamentary drafting.
- **Reversal direction cuts both ways.** "We reverse the dismissal of the
  reformation claim" is a **grant**. Scoring `reverse ... reform` as one thing
  gets half of them backwards.
- **A 200 is not data.** Texas answers 200 with a 250 KB JavaScript shell for
  every statute path. Verify by content.

**Publishing**

- Zenodo validates a deposition **atomically**. One bad enum value, a
  `resource_type` of `publication-webpage`, rejected the entire submission with
  no record created. The webhook still returned 202.
- Zenodo **only archives releases created after the webhook exists**. It will
  not backfill. That is why there are three tags for one set of code.
- The Hugging Face **create API is case-sensitive**. The account is `StepUpLaw`;
  a lowercase namespace returns `403 Forbidden ... you don't have the rights`,
  which reads like permissions and is spelling.
- ORCID's Organization field is an **Angular autocomplete**. Setting the value
  programmatically leaves it looking filled while the form still says "Please
  enter an organization". It only registers real keystrokes.
- The Astro site build is **OOM-killed at `--max-old-space-size=6144` and
  succeeds at 3072**. A lower cap makes V8 collect instead of ballooning until
  macOS kills it.

**Florida Statutes**

- The chapter view `/Laws/Statutes/<year>/Chapter<n>/All` works from **2010**.
  Earlier years answer 200 with a table-of-contents shell.
- Pre-2010 statutes **are** served, per section, back to at least 1997. The
  first conclusion that they were not was wrong and came from testing only the
  chapter form.
- 2010 to 2012 put the section number and history on **divs**; 2013 onward uses
  **spans**. Mapping only the span form drops every pre-2013 section silently,
  with an empty number.
- Pre-2010 section pages nest **a whole second HTML document**, preceded by a
  hidden metadata table reading `732.401000000000 / 732 / 2005.00000000000`.
  Parsing the container div captures that table as the statute text, and it
  diffs clean against every year, so it would have reported "no change"
  everywhere.

---

## Standing rules that did not change

- Query through `~/caselaw/`, never open the corpus directly.
- Report the exclusion funnel with counts.
- Rates, never raw counts, for anything over time.
- Findings and hypotheses visibly separate.
- Never pool measures that point in opposite directions.
- Single-coded studies are exploratory and must say so.
- **Read the output before trusting the pattern.** Every classifier bug this
  session was found by reading rows, not by reasoning about regexes.
