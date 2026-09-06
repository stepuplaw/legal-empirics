#!/usr/bin/env python3
"""Turn a working SQLite database into a publishable dataset.

    python3 scripts/export_dataset.py reformation-fl
    python3 scripts/export_dataset.py --all

SQLITE IS A WORKING FORMAT, NOT A PUBLICATION FORMAT. It is one binary blob
whose schema is only discoverable by opening it with the right tool, which is
exactly the wrong shape for a law reviewer checking a number and for a machine
harvesting the record. Each dataset is therefore emitted three ways:

    <name>.csv          the copy a human opens
    datapackage.json    Frictionless field types and descriptions -- the
                        machine-readable column dictionary
    dataset.jsonld      schema.org/Dataset -- what Google Dataset Search and
                        the citation graph actually read

The SQLite file is still published, as an archival artifact on Zenodo, because
it is what the analysis code runs against and dropping it would break
reproducibility.

EVERY FILE CARRIES ITS SHA-256 AND ROW COUNT. A dataset that cannot be checked
byte-for-byte against the record it claims to be is not published, it is merely
uploaded.
"""
import argparse, csv, hashlib, json, os, sqlite3, subprocess, sys, datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE = "https://stepuplaw.com"
REPO = "https://github.com/stepuplaw/legal-empirics"
HF_ORG = "https://huggingface.co/datasets/stepuplaw"
# The author identifier every record points at. An ORCID is minted by an
# independent registry, which is the whole reason it carries more weight than
# the same name asserted on our own pages.
ORCID = "https://orcid.org/0009-0002-1385-8498"
# The archived CODE, not the data. Each dataset gets its own DOI; until then
# `identifier` stays empty rather than borrowing the software DOI, which would
# tell a harvester the dataset and the code are the same object.
SOFTWARE_DOI = "10.5281/zenodo.22247377"
LICENSE = {"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/"}

# One entry per publishable dataset. `fields` is the column dictionary: a
# column without a description here is a column nobody outside this repo can
# interpret, so the exporter refuses to ship one.
DATASETS = {
    "reformation-fl": {
        "kaggle_title": "Florida Instrument Reformation, 1853-2026",
        "kaggle_subtitle": "Every Florida appellate decision reforming a will, trust, deed or policy",
        "db": "studies/reformation-fl/reformation-fl.db",
        "table": "decisions",
        "title": "Florida Reformation of Instruments, 1853-2026",
        "description":
            "Every Florida state appellate decision litigating the reformation "
            "of a legal instrument -- will, trust, deed, contract or insurance "
            "policy -- with the instrument type, the kind of drafting error "
            "alleged, the outcome, and which statutory regime was in force. "
            "Florida authorised trust reformation in 2007 (s. 736.0415) and "
            "will reformation in 2011 (s. 732.615); before those dates the "
            "remedy rested on equity, and for wills was unavailable entirely. "
            "The dataset makes that break observable within one jurisdiction.",
        "keywords": ["reformation", "scrivener's error", "wills", "trusts",
                     "deeds", "legal drafting", "empirical legal studies",
                     "Florida", "preventive law"],
        "fields": {
            "oid": "CourtListener opinion id",
            "cid": "CourtListener cluster id; one decision may hold several opinions",
            "name": "case name as reported",
            "court": "CourtListener court id (fla = Supreme Court of Florida, fladistctapp = District Courts of Appeal)",
            "year": "year the decision was filed",
            "cites": "times the decision has been cited, per CourtListener",
            "instrument": "will | trust | deed | contract | insurance | uncertain",
            "outcome": "granted | denied | sought | rule_stated | authority | uncertain -- see the codebook; only granted and denied are holdings",
            "regime": "statutory | pre-statute | equitable | unknown -- which reformation regime governed that instrument on that date",
            "errors": "comma-separated error types alleged; multi-label by design",
            "n_reform_sents": "count of reformation sentences found in the opinion",
            "cites_statute": "1 where the opinion cites s. 732.615, s. 732.616 or s. 736.0415",
            "key_sentence": "the sentence the outcome label was read from, verbatim",
        },
    },
    "statutory-staleness-fl": {
        "kaggle_title": "Florida Case Law on Amended Statutes",
        "kaggle_subtitle": "Which Florida holdings construe a statute that has since been changed",
        "db": "studies/statutory-staleness/statutory-staleness.db",
        "table": "holdings",
        "title": "Statutory Staleness in Florida Appellate Construction Holdings",
        "description":
            "One row per (decision, statutory section) pair where a Florida "
            "appellate court construed the meaning of a Florida statute, with "
            "whether that section has been amended since the decision and, "
            "where two editions of the code are held, whether the operative "
            "text actually changed. A citator reports whether a case was "
            "overruled by another case; it is far weaker on the other way a "
            "holding dies, which is that the legislature amended the statute "
            "and no court has had occasion to say so. This dataset measures "
            "that gap directly.",
        "keywords": ["statutory interpretation", "abrogation", "citator",
                     "legal research", "empirical legal studies", "Florida",
                     "statutory currency", "legal AI evaluation"],
        "fields": {
            "oid": "CourtListener opinion id",
            "cid": "CourtListener cluster id",
            "name": "case name as reported",
            "court": "CourtListener court id",
            "year": "year the decision was filed",
            "cites": "times the decision has been cited, per CourtListener",
            "section": "Florida Statutes section construed, e.g. 732.615",
            "last_amended": "most recent amendment year in the section history trail",
            "amendments_since": "count of amendments after the decision",
            "gap_years": "years between the decision and the most recent later amendment",
            "exposed": "1 where the section was amended after the decision; an UPPER BOUND, not a finding of abrogation",
            "tier": "amendment-screen | text-diff -- text-diff is only available where an edition at or before the decision year is held",
            "text_changed": "1 where the operative text differs between the edition in force at the decision and the current edition; null outside the text-diff tier",
            "similarity": "SequenceMatcher ratio between the two editions operative text, history trail excluded",
            "edition_at_decision": "the statute edition used as the baseline for the diff",
            "sentence": "the sentence in which the section was construed, verbatim",
            "statement": "the row written as one self-contained English sentence",
        },
    },
    "fl-local-codes": {
        "kaggle_title": "Florida Local Codes of Ordinances, 2026",
        "kaggle_subtitle": "Where all 478 Florida counties and cities publish their ordinances",
        "db": "studies/fl-local-codes/fl-local-codes.db",
        "table": "jurisdictions",
        "title": "Florida Local Codes of Ordinances: Publication and Currency, 2026",
        "homepage": f"{SITE}/data/florida-local-codes/",
        "download_base":
            "https://raw.githubusercontent.com/stepuplaw/fl-local-codes/main/data",
        "repo": "https://github.com/stepuplaw/fl-local-codes",
        "same_as": ["https://github.com/stepuplaw/fl-local-codes"],
        "spatial": "Florida, United States",
        "temporal": "2026",
        "sources": [
            {"title": "US Census Bureau subcounty population estimates, vintage 2024",
             "path": "https://www2.census.gov/programs-surveys/popest/datasets/"
                     "2020-2024/cities/totals/sub-est2024_12.csv"},
            {"title": "Municode public client and content API",
             "path": "https://api.municode.com"},
            {"title": "American Legal Publishing Florida code library",
             "path": "https://codelibrary.amlegal.com/regions/fl"},
        ],
        "measurement_technique":
            "Census enumeration of Florida counties and incorporated places, "
            "joined by normalised name to the public metadata APIs of the "
            "commercial codifiers, with every resulting URL verified against "
            "the publisher's own resolver rather than an HTTP status. "
            "Jurisdictions no codifier carries were resolved by hand in a "
            "browser and recorded separately. Metadata only; no ordinance "
            "text is retrieved or republished.",
        "description":
            "Where each of Florida's 478 local governments publishes its code "
            "of ordinances, who publishes it, and how current that code is. "
            "One row per county and per incorporated municipality, covering "
            "all 67 counties and all 411 cities, towns and villages. "
            "Municipal law is the hardest layer of American law to locate: "
            "there is no master index, and each commercial codifier lists "
            "only its own clients, so a reader who does not already know who "
            "publishes a town's code has nowhere to start. This dataset is "
            "that missing index for one state, and it records the jurisdictions "
            "no codifier carries, which is the part no vendor list can show. "
            "Currency is measured from the codifier's own stated codification "
            "date, so a code that has not been supplemented in years is "
            "visible as such.",
        "card_source":
            "US Census Bureau subcounty population estimates (vintage 2024) "
            "for the jurisdiction frame, joined to the public metadata APIs of "
            "the commercial code publishers. No court opinions are involved.",
        "card_built":
            "The jurisdiction list is the Census Bureau subcounty population "
            "file, which is independent of every codifier and yields exactly 67 "
            "counties and 411 municipalities, matching the Florida League of "
            "Cities directory. Each publisher's public metadata was joined onto "
            "that list by normalised name, and every jurisdiction no publisher "
            "carried was opened by hand in a browser. Two traps had to be "
            "handled: the largest publisher's classification field does not "
            "encode jurisdiction type, so type comes from the Census, and its "
            "library returns HTTP 200 with an empty JavaScript shell for "
            "addresses that do not exist, so every URL is verified against the "
            "resolver the library's own page calls rather than against a status "
            "code. Metadata only. No ordinance text is retrieved or "
            "republished, and the dataset must not be described as ordinance "
            "text.",
        "card_limits":
            "**This is a point in time.** Codifier contracts move. Every row "
            "carries the date it was checked, and that date is part of the "
            "claim rather than a footnote to it.\n\n"
            "**Currency is the publisher's word.** `codified_through` reports "
            "when the code was last compiled, not that the compilation is "
            "correct or complete.\n\n"
            "**Official status is usually unstated.** Most Florida codes do "
            "not say on the page whether the online version is the official "
            "one, and the column records what the page says rather than "
            "inferring it.\n\n"
            "**This says where the law is, never what it says.** There is no "
            "ordinance text here, by design.",
        "keywords": ["municipal law", "ordinances", "local government",
                     "legal research", "Florida", "code of ordinances",
                     "zoning", "code enforcement", "open government data",
                     "legal information retrieval"],
        "fields": {
            "geoid": "Census GEOID: 12 followed by the county FIPS code, or 12 followed by the place FIPS code",
            "name": "jurisdiction name without its type suffix",
            "type": "county | city | town | village, taken from the Census, never from the codifier",
            "county": "the county the jurisdiction sits in; for a county row, itself",
            "counties": "every county the place falls in, pipe separated, largest population share first",
            "population": "Census population estimate, vintage 2024",
            "code_status": "online-html | online-pdf-only | no-online-code | unknown",
            "publisher": "municode | american-legal | general-code | code-publishing | self-hosted | none | unknown",
            "code_url": "the verified URL of the code of ordinances; empty where no code is online",
            "publisher_client_id": "the codifier's own identifier for this jurisdiction, where it has one",
            "code_product_id": "Municode product id for the code of ordinances; the key to its table of contents",
            "codified_through": "date of the most recent ordinance included in the code, as the publisher states it",
            "code_last_updated": "date the publisher last posted an update online",
            "pdf_available": "1 where the publisher offers the code as a downloadable PDF",
            "pending_ordinances_count": "adopted ordinances awaiting codification, per the publisher; null outside Municode",
            "official_status": "official | unofficial | unstated -- recorded only where the page says so, never inferred",
            "source": "municode-api | browser | manual -- how this row was resolved",
            "source_checked_date": "the date this row was checked; codifier contracts move, so the date is part of the claim",
            "notes": "free text, used mainly for jurisdictions no codifier carries",
            "statement": "the row written as one self-contained English sentence, so it can be retrieved, quoted and checked on its own",
        },
    },
    "disputed-terms-national": {
        "kaggle_title": "Disputed Contract Terms, 51 US Jurisdictions",
        "kaggle_subtitle": "Words courts were asked to call ambiguous, and whether the challenge won",
        "db": "studies/disputed-terms/terms-national.db",
        "table": "term_hits",
        "title": "Disputed Contract and Instrument Terms in US State Appellate Courts",
        "description":
            "One row per (term, decision) pair: a word or phrase a court quoted "
            "as the disputed language in a decision containing an ambiguity "
            "holding, across the state appellate courts of all 50 states and DC. "
            "Terms are extracted from the whole opinion by cue-anchored quotation "
            "('the term \"X\"', '\"X\" as used in'), classified into functional "
            "drafting categories, and linked to the holding by three graded "
            "levels of evidence.",
        "keywords": ["contract interpretation", "ambiguity", "corpus linguistics",
                     "legal drafting", "empirical legal studies", "state courts"],
        "fields": {
            "term": "the disputed language, lowercased and normalised, as the court quoted it",
            "category": "functional drafting class: nexus, degree, temporal, scope, modal, role, succession, property, event, conduct, condition, mental, uncategorised",
            "source": "the instrument the words sit in: testamentary, deed, insurance, contract, statute, constitution, uncertain",
            "posture": "found | rejected | alleged | uncertain -- whether the court held the language ambiguous",
            "link": "direct | proximate | inferred -- strength of the link between this term and the holding; inferred rows must not be pooled with the other two",
            "oid": "CourtListener opinion id",
            "cid": "CourtListener cluster id",
            "court": "CourtListener court id",
            "state": "two-letter state postal code",
            "year": "year the decision was filed",
        },
    },
}


def sha256(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(buf):
            h.update(chunk)
    return h.hexdigest()


def git_commit():
    try:
        return subprocess.check_output(
            ["git", "-C", HERE, "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


SQL_TO_FRICTIONLESS = {"INTEGER": "integer", "REAL": "number", "TEXT": "string"}
SQL_TO_CROISSANT = {"INTEGER": "sc:Integer", "REAL": "sc:Float", "TEXT": "sc:Text"}

# ★ A ROW OF CODES DOES NOT EMBED. Retrieval-augmented systems fetch chunks, and
# `instrument=will, outcome=denied, year=2012` is not a chunk anyone can retrieve
# or quote. Every dataset therefore carries a `statement` column: the same row
# written as one self-contained English sentence, so each row is independently
# retrievable, citable and checkable. It costs one column and it is the
# difference between a dataset that gets read by machines and one that only gets
# downloaded.
_POSTURE_SAYS = {
    "found": "held the language ambiguous",
    "rejected": "held the language clear",
    "alleged": "was asked to hold the language ambiguous",
    "uncertain": "did not resolve the question in terms this dataset could classify",
}
_OUTCOME_SAYS = {
    "granted": "the court granted reformation",
    "denied": "the court denied reformation",
    "sought": "reformation was sought; the decision does not state the outcome "
              "in a sentence naming the remedy",
    "rule_stated": "the opinion states the reformation rule without holding on it",
    "authority": "the opinion discusses reformation authority rather than holding",
    "uncertain": "the outcome could not be classified",
}


_INSTRUMENT_SAYS = {
    "will": "a will", "trust": "a trust", "deed": "a deed",
    "contract": "a contract", "insurance": "an insurance policy",
    "uncertain": "an instrument of undetermined type",
}


def _stmt_reformation(r):
    err = (r["errors"] or "unspecified").replace(",", ", ")
    inst = _INSTRUMENT_SAYS.get(r["instrument"], f"a {r['instrument']}")
    return (f"{r['name']} ({r['year']}) litigated reformation of "
            f"{inst} in the Florida appellate courts; "
            f"{_OUTCOME_SAYS.get(r['outcome'], r['outcome'])}. "
            f"Alleged error: {err}. Reformation regime in force: {r['regime']}.")


def _stmt_terms(r):
    return (f"A {r['state']} appellate court in {r['year']} considered the "
            f"{r['source']} term \"{r['term']}\" ({r['category']} language); "
            f"the court {_POSTURE_SAYS.get(r['posture'], r['posture'])}. "
            f"Link between term and holding: {r['link']}.")


STATEMENTS = {"reformation-fl": _stmt_reformation,
              "disputed-terms-national": _stmt_terms}


def export(name, spec, outroot):
    db_path = os.path.join(HERE, spec["db"])
    if not os.path.exists(db_path):
        print(f"  ! {name}: {spec['db']} not built yet, skipping", file=sys.stderr)
        return None
    outdir = os.path.join(outroot, name)
    os.makedirs(outdir, exist_ok=True)

    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    cols = [(r["name"], r["type"]) for r in
            con.execute(f"PRAGMA table_info({spec['table']})")]

    missing = [c for c, _ in cols if c not in spec["fields"]]
    if missing:
        sys.exit(f"{name}: no description for column(s) {missing}. "
                 f"An undocumented column cannot be published.")

    stmt_fn = STATEMENTS.get(name)
    has_stmt = any(c == "statement" for c, _ in cols)
    if stmt_fn and not has_stmt:
        cols = cols + [("statement", "TEXT")]
        spec["fields"]["statement"] = (
            "the row written as one self-contained English sentence, so it can "
            "be retrieved, quoted and checked on its own")

    csv_path = os.path.join(outdir, f"{name}.csv")
    n = 0
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([c for c, _ in cols])
        for row in con.execute(f"SELECT * FROM {spec['table']}"):
            vals = []
            for c, _ in cols:
                if c == "statement" and stmt_fn and not has_stmt:
                    vals.append(stmt_fn(row))
                else:
                    vals.append(row[c])
            w.writerow(vals)
            n += 1
    con.close()

    # Provenance: the run manifest the build script wrote beside the database.
    run_meta = {}
    rp = os.path.join(HERE, spec["db"]).replace(".db", "-run.json")
    if os.path.exists(rp):
        run_meta = json.load(open(rp))

    today = datetime.date.today().isoformat()
    digest = sha256(csv_path)
    size = os.path.getsize(csv_path)

    # ★ PARQUET ALONGSIDE CSV, not instead of it. CSV is what a law reviewer
    # opens; Parquet is what anything loading the data at scale wants, and it
    # carries column types so a year does not arrive as a string. It is also
    # roughly five times smaller, which matters because the term table is 80 MB
    # as CSV and that is past the point where a browser download is pleasant.
    try:
        import pandas as pd
        pq_path = os.path.join(outdir, f"{name}.parquet")
        pd.read_csv(csv_path, low_memory=False).to_parquet(pq_path, index=False)
        pq_bytes, pq_sha = os.path.getsize(pq_path), sha256(pq_path)
        print(f"    parquet {pq_bytes/1e6:.1f} MB "
              f"({100*pq_bytes/max(size,1):.0f}% of the CSV)")
    except Exception as e:
        pq_path = pq_bytes = pq_sha = None
        print(f"    parquet skipped: {type(e).__name__} {str(e)[:60]}", file=sys.stderr)


    # Three things used to be hardcoded here and were true only of the
    # CourtListener studies: the homepage, the source, and the download base.
    # A dataset built from a different source was being described as though it
    # came from the opinion corpus, and its `distribution` pointed at a path
    # that has never existed for any dataset. A contentUrl that 404s tells a
    # harvester the record is a page ABOUT data rather than data, which is the
    # one outcome DISTRIBUTION.md is written to prevent.
    homepage = spec.get("homepage", f"{SITE}/research/{name}/")
    dl = spec.get("download_base", f"{SITE}/research/{name}")
    sources = spec.get("sources", [{
        "title": "CourtListener bulk export, topped up nightly from the courts",
        "path": "https://www.courtlistener.com/help/api/bulk-data/",
    }])
    technique = spec.get("measurement_technique",
        "Full-text retrieval over a local CourtListener corpus, followed by "
        "deterministic sentence-level classification. Retrieval is wide and "
        "filtering is explicit; the exclusion funnel is reported with counts.")

    datapackage = {
        "name": name,
        "title": spec["title"],
        "description": spec["description"],
        "licenses": [LICENSE],
        "homepage": homepage,
        "version": today,
        "created": today,
        "sources": sources,
        "resources": ([{
            "name": name,
            "path": f"{name}.csv",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "bytes": size,
            "rows": n,
            "hash": f"sha256:{digest}",
            "schema": {"fields": [
                {"name": c,
                 "type": SQL_TO_FRICTIONLESS.get((t or "TEXT").upper(), "string"),
                 "description": spec["fields"][c]}
                for c, t in cols]},
        }] + ([{"name": f"{name}-parquet", "path": f"{name}.parquet",
                "format": "parquet", "mediatype": "application/vnd.apache.parquet",
                "bytes": pq_bytes, "rows": n, "hash": f"sha256:{pq_sha}"}]
              if pq_bytes else [])),
        "provenance": {"repository": REPO, "commit": git_commit(),
                       "run": run_meta},
    }
    with open(os.path.join(outdir, "datapackage.json"), "w") as fh:
        json.dump(datapackage, fh, indent=2)

    # schema.org/Dataset. `sameAs` and `distribution` are the identity chain:
    # this is where the site, GitHub, Hugging Face and Zenodo name each other,
    # so a harvester landing on any one of them can reach the rest.
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": spec["title"],
        "description": spec["description"],
        "url": homepage,
        "identifier": ([f"https://doi.org/{spec['doi']}"] if spec.get("doi") else []),
        "keywords": spec["keywords"],
        "license": LICENSE["url"],
        "isAccessibleForFree": True,
        "version": today,
        "dateModified": today,
        "creator": {"@type": "Person", "name": "Kevin D. Klagge",
                    "url": SITE, "identifier": ORCID, "sameAs": ORCID},
        "publisher": {"@type": "Person", "name": "Kevin D. Klagge",
                      "url": SITE, "sameAs": ORCID},
        "sameAs": (spec.get("same_as", []) +
                   [REPO, f"{HF_ORG}/{name}", f"https://doi.org/{SOFTWARE_DOI}"]),
        "isBasedOn": {"@type": "SoftwareSourceCode",
                      "identifier": f"https://doi.org/{SOFTWARE_DOI}",
                      "codeRepository": REPO},
        "citation": run_meta.get("query"),
        "measurementTechnique": technique,
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "text/csv",
             "contentUrl": f"{dl}/{name}.csv",
             "contentSize": str(size), "sha256": digest},
            {"@type": "DataDownload", "encodingFormat": "application/json",
             "contentUrl": f"{dl}/datapackage.json"},
        ] + ([{"@type": "DataDownload",
               "encodingFormat": "application/vnd.apache.parquet",
               "contentUrl": f"{dl}/{name}.parquet",
               "contentSize": str(pq_bytes), "sha256": pq_sha}]
             if pq_bytes else []),
        "variableMeasured": [
            {"@type": "PropertyValue", "name": c, "description": spec["fields"][c]}
            for c, _ in cols],
    }
    if spec.get("spatial"):
        jsonld["spatialCoverage"] = {"@type": "Place", "name": spec["spatial"]}
    if spec.get("temporal"):
        jsonld["temporalCoverage"] = spec["temporal"]
    with open(os.path.join(outdir, "dataset.jsonld"), "w") as fh:
        json.dump(jsonld, fh, indent=2)

    # ★ CROISSANT (MLCommons). schema.org/Dataset says a dataset exists;
    # Croissant says what its COLUMNS mean, and it is the format Hugging Face,
    # Kaggle and Google Dataset Search read to render and load data. It is the
    # one metadata addition that lands where AI tooling actually looks, which is
    # why it is emitted alongside rather than instead of the schema.org file.
    file_id = f"{name}.csv"
    croissant = {
        "@context": {
            "@language": "en", "@vocab": "https://schema.org/",
            "cr": "http://mlcommons.org/croissant/",
            "sc": "https://schema.org/",
            "dct": "http://purl.org/dc/terms/",
            "data": {"@id": "cr:data", "@type": "@json"},
            "dataType": {"@id": "cr:dataType", "@type": "@vocab"},
            "extract": "cr:extract", "field": "cr:field",
            "fileObject": "cr:fileObject", "fileProperty": "cr:fileProperty",
            "column": "cr:column", "recordSet": "cr:recordSet",
            "source": "cr:source", "subField": "cr:subField",
            "references": "cr:references", "repeated": "cr:repeated",
            "examples": {"@id": "cr:examples", "@type": "@json"},
            "conformsTo": "dct:conformsTo",
        },
        "@type": "sc:Dataset",
        "conformsTo": "http://mlcommons.org/croissant/1.0",
        "citeAs": f"Klagge, Kevin D. legal-empirics. https://doi.org/{SOFTWARE_DOI}",
        "name": name.replace("-", "_"),
        "description": spec["description"],
        "url": homepage,
        "license": LICENSE["url"],
        "version": today,
        "keywords": spec["keywords"],
        "creator": {"@type": "sc:Person", "name": "Kevin D. Klagge",
                    "sameAs": ORCID},
        "distribution": [{
            "@type": "cr:FileObject",
            "@id": file_id,
            "name": file_id,
            "description": "The dataset as a single UTF-8 CSV with a header row.",
            "contentUrl": f"{dl}/{file_id}",
            "encodingFormat": "text/csv",
            "sha256": digest,
        }],
        "recordSet": [{
            "@type": "cr:RecordSet",
            "@id": "rows",
            "name": "rows",
            "description": spec["title"],
            "field": [{
                "@type": "cr:Field",
                "@id": f"rows/{c}",
                "name": c,
                "description": spec["fields"][c],
                "dataType": SQL_TO_CROISSANT.get((t or "TEXT").upper(), "sc:Text"),
                "source": {"fileObject": {"@id": file_id},
                           "extract": {"column": c}},
            } for c, t in cols],
        }],
    }
    with open(os.path.join(outdir, "croissant.json"), "w") as fh:
        json.dump(croissant, fh, indent=2)

    # Kaggle. A distribution channel, not an identity anchor, so the card points
    # at the canonical record rather than presenting itself as one. Title is
    # capped at 50 characters and the subtitle wants 20 to 80, which is why both
    # are written out per dataset instead of reusing the long scholarly title.
    kag = {
        "title": spec.get("kaggle_title", spec["title"])[:50],
        "subtitle": spec.get("kaggle_subtitle", "")[:80],
        "id": f"stepuplaw/{name}",
        "licenses": [{"name": "CC-BY-4.0"}],
        "keywords": spec["keywords"],
        "description": (
            spec["description"]
            + "\n\nCanonical record and methodology: " + spec.get("repo", REPO)
            + "\nResearch page: " + f"{SITE}/research/"
            + "\nAuthor: Kevin D. Klagge, ORCID " + ORCID
            + "\n\nEvery row carries a `statement` column, which is the row written "
              "as one English sentence so it can be read and quoted on its own. "
              "Column definitions are in datapackage.json; the same data is also "
              "described in MLCommons Croissant."),
        "resources": [{
            "path": f"{name}.csv",
            "description": spec["title"],
            "schema": {"fields": [
                {"name": c, "description": spec["fields"][c],
                 "type": SQL_TO_FRICTIONLESS.get((t or "TEXT").upper(), "string")}
                for c, t in cols]},
        }],
    }
    with open(os.path.join(outdir, "dataset-metadata.json"), "w") as fh:
        json.dump(kag, fh, indent=2)

    print(f"  {name}: {n:,} rows, {size/1e6:.1f} MB, sha256 {digest[:16]}…")
    return {"name": name, "rows": n, "bytes": size, "sha256": digest}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "dist"))
    a = ap.parse_args()

    names = list(DATASETS) if (a.all or not a.dataset) else [a.dataset]
    os.makedirs(a.out, exist_ok=True)
    built = []
    for nm in names:
        if nm not in DATASETS:
            sys.exit(f"unknown dataset {nm}; known: {', '.join(DATASETS)}")
        r = export(nm, DATASETS[nm], a.out)
        if r:
            built.append(r)

    with open(os.path.join(a.out, "manifest.json"), "w") as fh:
        json.dump({"generated": datetime.date.today().isoformat(),
                   "commit": git_commit(), "datasets": built}, fh, indent=2)
    print(f"# {len(built)} dataset(s) -> {a.out}")


if __name__ == "__main__":
    main()
