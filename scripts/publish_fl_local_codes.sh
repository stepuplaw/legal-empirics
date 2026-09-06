#!/usr/bin/env bash
# Copy the exported Florida local code dataset into the data repo and write the
# trimmed JSON the site page renders.
#
# The data repo is a separate checkout on purpose. legal-empirics is the code
# and the method; the data belongs in a repo that Zenodo can archive on its own
# and that GitHub can serve raw files from, so the site never pays the download
# bandwidth. Run after export_dataset.py.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$HERE/dist/fl-local-codes"
REPO="${FL_LOCAL_CODES_REPO:-$HOME/fl-local-codes}"

[ -d "$DIST" ] || { echo "no export at $DIST; run export_dataset.py fl-local-codes" >&2; exit 1; }
[ -d "$REPO" ] || { echo "no data repo at $REPO" >&2; exit 1; }

mkdir -p "$REPO/data"
cp "$DIST/fl-local-codes.csv" "$REPO/data/"
[ -f "$DIST/fl-local-codes.parquet" ] && cp "$DIST/fl-local-codes.parquet" "$REPO/data/"
# Both locations, deliberately. The metadata files advertise their own URLs
# under data/, so a copy has to exist there or the record points at a 404,
# which tells a harvester the dataset is a page about data rather than data.
# Frictionless and most repo tooling look for datapackage.json at the root.
# Both copies are written from the same dist/ files in one run, so they cannot
# drift apart.
cp "$DIST/datapackage.json" "$DIST/dataset.jsonld" "$DIST/croissant.json" "$REPO/"
cp "$DIST/datapackage.json" "$DIST/dataset.jsonld" "$DIST/croissant.json" "$REPO/data/"

# JSON alongside CSV. A browser cannot parse CSV without a library, and the
# site's sync script and anyone building a tool against this both want objects.
python3 - "$DIST/fl-local-codes.csv" "$REPO/data/fl-local-codes.json" <<'PY'
import csv, json, sys, datetime
src, dst = sys.argv[1], sys.argv[2]
ints = {"population", "pdf_available", "pending_ordinances_count"}
rows = []
with open(src, encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        for k in ints:
            v = r.get(k, "")
            r[k] = int(v) if v not in ("", None) else None
        rows.append(r)
json.dump({"generated": datetime.date.today().isoformat(),
           "count": len(rows), "rows": rows},
          open(dst, "w"), indent=1)
print(f"  {len(rows)} rows -> {dst}")
PY

# The README states counts. GENERATE IT rather than typing them, because a
# headline number that drifts from the CSV underneath it destroys exactly the
# credibility the dataset exists to earn, and a hand-written README drifts on
# the first refresh.
python3 - "$REPO/data/fl-local-codes.json" "$REPO/README.md" <<'PY'
import json, sys, collections, datetime
rows = json.load(open(sys.argv[1]))["rows"]
n = len(rows)
by = lambda f: collections.Counter(r[f] for r in rows)
st, pub, typ = by("code_status"), by("publisher"), by("type")
online = sum(v for k, v in st.items() if k.startswith("online"))
counties = [r for r in rows if r["type"] == "county"]
munis = [r for r in rows if r["type"] != "county"]
con = sum(1 for r in counties if r["code_status"].startswith("online"))
mon = sum(1 for r in munis if r["code_status"].startswith("online"))
del counties, munis
cut = (datetime.date.today() - datetime.timedelta(days=1096)).isoformat()
stale = [r for r in rows if r["codified_through"] and r["codified_through"] < cut]
pending = sum(r["pending_ordinances_count"] or 0 for r in rows)
today = datetime.date.today().isoformat()
html = st.get("online-html", 0)
pdf = st.get("online-pdf-only", 0)
coded = html + pdf
ordonly = st.get("ordinances-only", 0)
nocode = st.get("no-online-code", 0)
unknown = st.get("unknown", 0)
stale_n = len(stale)
suspect = sum(1 for r in rows if "postdates the supplement" in (r["notes"] or ""))

def tbl(c, label):
    w = max(len(label), max((len(str(k)) for k in c), default=0))
    out = [f"| {label:<{w}} | Count |", f"|{'-' * (w + 2)}|------:|"]
    out += [f"| {k:<{w}} | {v:>5} |" for k, v in c.most_common()]
    return "\n".join(out)

open(sys.argv[2], "w").write(f"""# Florida local codes of ordinances

Where each of Florida's {n} local governments publishes its code of ordinances,
who publishes it, and how current that code is. One row per county and per
incorporated municipality: all 67 counties and all 411 cities, towns and
villages.

**Why this exists.** Municipal law is the hardest layer of American law to
locate. There is no master index, and each commercial codifier publishes an
index of its own clients and nothing else, so a reader who does not already
know who publishes a town's code has nowhere to begin. The valuable part of
this table is not the towns on Municode, which anyone can find by searching
Municode. It is everything else, because no vendor index can show you an
absence.

## Findings, as of {today}

Four outcomes, and the middle two are the ones no existing list records.

- **{coded} of {n} publish an actual code of ordinances online.** That is {con} of 67 counties and {mon} of 411 municipalities. {html} serve it as a searchable web code and {pdf} only as a PDF.
- **{ordonly} publish their ordinances but have never codified them.** The documents are online one at a time, so answering a question about fences means reading every ordinance the town ever passed. This is a different condition from having a code, and pooling the two would hide it.
- **{nocode} publish nothing online at all.** To read their ordinances you contact the clerk.
- **{unknown} could not be confirmed.** No commercial codifier carries them, and this survey could not establish what they publish instead. They are almost all towns under 1,000 people. Each row says what was checked; none is a claim that nothing exists.
- **{pending} adopted ordinances are waiting to be codified across Florida.** An ordinance that has passed but is not yet in the code still binds the property.
- **{stale_n} codes were last codified more than three years ago**, and a further **{suspect} state a codification date that postdates the supplement carrying it**, which is impossible and is recorded as a note rather than as a date.
- One publisher, Municode, carries {pub.get("municode", 0)} of them. A single vendor holds most of Florida's municipal law.

### By status

{tbl(st, "Status")}

### By publisher

{tbl(pub, "Publisher")}

### By type

{tbl(typ, "Type")}

## Files

| File | What it is |
|------|------------|
| `data/fl-local-codes.csv` | the table, UTF-8 with a header row |
| `data/fl-local-codes.json` | the same rows as objects |
| `data/fl-local-codes.parquet` | typed columns, for anything loading at scale |
| `datapackage.json` | Frictionless schema, per column types and descriptions, SHA-256 and row count |
| `dataset.jsonld` | schema.org/Dataset |
| `croissant.json` | MLCommons Croissant |

Every row carries a `statement` column, the row written as one English
sentence, so a single row can be retrieved, quoted and checked on its own.

## Method, and the two traps in it

The jurisdiction list comes from the Census Bureau subcounty population file,
vintage 2024, which is independent of every codifier and yields exactly 67
counties and 411 municipalities, matching the Florida League of Cities
directory. Each codifier's public metadata was joined onto that list by
normalised name, and everything left over was opened by hand in a browser.

1. **Municode's classification field is not jurisdiction type.** Palmetto Bay
   is 9, Jacksonville is 3, and 80 municipalities sit in 6. Type comes from the
   Census and never from the vendor.
2. **A 200 does not mean a page exists.** `library.municode.com/fl/<anything>`
   returns success and a JavaScript shell for slugs that do not exist, so a
   status code cannot verify a link. Every Municode address here was checked
   against the resolver the library's own page calls, which returns the client
   id, and the check is stored beside the row.

A third, in the name join: Florida has both a Melbourne and a Melbourne
Village, and both an Indian Creek and an Indian Creek Village. A normaliser
that treats a trailing type word as a label rather than as part of the name
hands one town's code to another. Exact names are matched first for every
jurisdiction, and only then is a trailing type word treated as droppable.

## Limitations

- **Point in time.** Codifier contracts move. Every row carries the date it was
  checked, and that date is part of the claim.
- **Currency is the publisher's word.** `codified_through` reports when the code
  was last compiled, not that the compilation is correct or complete.
- **Official status is usually unstated.** Recorded only where the page says so.
- **Metadata only.** This dataset says where the law is, never what it says.

## Licence and citation

Compilation licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The ordinances themselves carry no copyright; they are edicts of government,
per *Georgia v. Public.Resource.Org*, 590 U.S. 255 (2020). No ordinance text is
included here.

Cite as: Klagge, Kevin D. "Florida local codes of ordinances, 2026." StepUpLaw.

Documented at <https://stepuplaw.com/data/florida-local-codes/>.
Method and build code: <https://github.com/stepuplaw/legal-empirics>
(`studies/fl-local-codes/`, `protocols/fl-local-codes.md`).
""")
print(f"  README.md written")
PY

echo "published to $REPO"
ls -la "$REPO/data"
