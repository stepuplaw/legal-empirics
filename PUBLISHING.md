# Where the research lives, and how the pieces name each other

_Last updated 2026-09-01._

Four properties, one job each. The failure mode this design exists to prevent is
the common one: a PDF on a law firm's site, a zip on GitHub, and a dataset on
Hugging Face that do not reference one another, so no reader and no harvester
can tell they are the same work.

| Property | Its one job | Status |
|---|---|---|
| `stepuplaw.com/research/` | canonical landing page per study; the citable human URL and the SEO asset | to build |
| `github.com/stepuplaw/legal-empirics` | code, methodology, reproducibility | live |
| Zenodo | archival copy and the DOI — the permanent identity | to register |
| Hugging Face Datasets | machine-readable distribution and discovery | to register |

**The site is canonical, not the repository.** GitHub is where the method is
audited; the site is what gets cited, indexed and linked. Everything else points
at it.

---

## Data files do not live in the site repository

**Cloudflare Pages caps a single asset at 25 MiB.** This is a measured
constraint, not a guess — it is the same limit that already forces podcast audio
out of the Astro repo and into R2 (see `src/content.config.ts`, which documents
it). The national disputed-terms CSV is **23 MB today** and grows with every
state added, so it would cross that line during ordinary work and the build
would start failing on a data refresh rather than on a code change.

    R2 bucket           the CSV, the Parquet, the SQLite archive
    Pages repo          datapackage.json, dataset.jsonld, the page itself
    site URL            /research/<name>/ redirects downloads to R2

Small files (`datapackage.json`, `dataset.jsonld`, both a few KB) stay in the
repo so the JSON-LD is served from the canonical origin. Search engines weight
structured data served from the page's own domain; a JSON-LD file on an object
store is a weaker signal and a broken-link risk.

---

## Three formats, because three audiences

`scripts/export_dataset.py` emits all of them from the working SQLite:

| File | Who reads it |
|---|---|
| `<name>.csv` | the law reviewer checking a number |
| `datapackage.json` | Frictionless column dictionary — the machine-readable schema |
| `dataset.jsonld` | schema.org `Dataset`, which is what Google Dataset Search actually harvests |
| `<name>.db` | the archival artifact on Zenodo; the analysis code runs against it |

SQLite is a working format, not a publication format: one binary blob whose
schema is discoverable only by opening it with the right tool. It is still
published, because dropping it would break reproducibility of the analysis
scripts — but it is never the *only* thing published.

**The exporter refuses to ship an undocumented column.** Every field needs a
description in the `DATASETS` registry or the run exits. A column nobody outside
this repo can interpret is not data, it is a number with a name on it.

**Every file carries its SHA-256 and row count**, in both the datapackage and
the JSON-LD. A dataset that cannot be checked byte-for-byte against the record
it claims to be has been uploaded, not published.

---

## The identity chain

Each property names the others, so a harvester landing on any one reaches the
rest. This is the part that is usually skipped and is the whole reason the four
properties add up to more than four orphans.

```
site /research/<name>/
    schema.org Dataset
        url          -> itself (canonical)
        identifier   -> Zenodo DOI
        sameAs       -> GitHub repo, Hugging Face dataset
        distribution -> R2 download URLs, with sha256
    ScholarlyArticle
        about        -> the Dataset above
        codeRepository -> GitHub

Zenodo record
    related identifiers -> site URL (isDocumentedBy), GitHub (isSupplementTo)

Hugging Face dataset card
    homepage -> site page
    doi      -> Zenodo

GitHub
    CITATION.cff -> DOI + site URL
    README       -> site page, dataset pages
```

`export_dataset.py` already emits `sameAs` and `distribution`. `identifier` is
left empty until a DOI exists, because a fabricated or placeholder DOI in
published JSON-LD is worse than an absent one.

---

## The site: a `research` content collection

The site already has the pattern — `blog` and `podcast` are Astro content
collections with Zod schemas in `src/content.config.ts`. Research is a third,
and should not be hand-built pages:

```ts
const research = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/research' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    draft: z.boolean().default(true),
    // Slug of the exported dataset; must match a key in export_dataset.py
    dataset: z.string(),
    doi: z.string().optional(),          // absent until Zenodo mints it
    hfDataset: z.string().optional(),
    // nbviewer renders the notebook from GitHub; no notebook server needed
    notebooks: z.array(z.object({ label: z.string(), path: z.string() })).default([]),
    // The three numbers, so the index page can show them without parsing prose
    headline: z.object({ n: z.number(), unit: z.string() }).optional(),
  }),
});
```

Two rules carried over from the site's own conventions: pages are tested with a
**trailing slash** (the site 308-redirects the no-slash form), and a fresh
deploy can serve a cached 404 for a couple of minutes, so verify with a
cache-buster before concluding a page failed.

**Notebooks go in this repo, not the estate-tax repo**, and are linked through
nbviewer rather than rendered by the site — nbviewer reads straight from GitHub,
so there is no notebook server to run and no output to keep in sync.

---

## Versioning

A dataset version is **the corpus snapshot date plus the code commit**, not a
hand-incremented number. Both are already recorded: `datapackage.json` carries
`provenance.commit` and the run manifest carries the snapshot. Two exports of
the same study from different commits are different datasets and must not share
a version string.

Zenodo mints a new DOI per release and a concept DOI for the study as a whole.
Cite the concept DOI in prose; cite the versioned DOI for a specific number.

---

## Licence

CC BY 4.0 for data and text, matching what the ambiguity-pools report already
declares. Not legal advice, and every published page says so.

The underlying opinions are US judicial opinions and uncopyrightable; the
CourtListener bulk export they came from is credited as the source in every
datapackage.

---

## What is built and what is not

**Built:** `scripts/export_dataset.py`, and clean exports of both datasets —
`reformation-fl` (932 rows) and `disputed-terms-national` (286,846 rows) — each
with datapackage, JSON-LD, checksums and provenance.

**Not built, and each needs a decision rather than more code:**

1. **The R2 bucket and its public base URL.** The podcast already uses R2, so
   the account and the pattern exist; this needs a bucket name and whether
   downloads are served from `data.stepuplaw.com` or the existing base.
2. **Zenodo.** Requires connecting the GitHub repo and cutting a release. The
   DOI cannot be written into the JSON-LD until it exists.
3. **Hugging Face org.** `huggingface.co/stepuplaw` is assumed by the exporter
   and is not registered yet.
4. **The Astro `research` collection** and the study pages themselves.

None of the four is blocked by anything in this repository.
