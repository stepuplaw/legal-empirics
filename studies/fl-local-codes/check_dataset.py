#!/usr/bin/env python3
"""Refuse to publish a Florida local code table that is wrong.

    python3 check_dataset.py

Every assertion here is one that failed, or could silently have failed, while
the dataset was being built. The name join is the dangerous part: Florida has a
Melbourne and a Melbourne Village, an Indian Creek and an Indian Creek Village,
and a normaliser that treats a trailing type word as a label rather than as part
of the name hands one town's code to another. A wrong URL is worse than a
missing one, because a reader who follows it reads the wrong law and has no
reason to doubt it.
"""
import csv, os, re, sqlite3, sys, datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "fl-local-codes.db")

EXPECT_TYPE = {"county": 67, "city": 267, "town": 123, "village": 21}
STATUS = {"online-html", "online-pdf-only", "ordinances-only",
          "no-online-code", "unknown"}
PUBLISHER = {"municode", "american-legal", "general-code", "code-publishing",
             "municipal-code-online", "elaws", "self-hosted", "none", "unknown"}
SOURCE = {"municode-api", "browser", "manual", ""}
OFFICIAL = {"official", "unofficial", "unstated"}
DASHES = re.compile(r"[‒–—―−]")

fails, warns = [], []


def bad(msg):
    fails.append(msg)


def warn(msg):
    warns.append(msg)


def main():
    if not os.path.exists(DB):
        sys.exit("no database; run build_dataset.py first")
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM jurisdictions")]
    today = datetime.date.today().isoformat()

    if len(rows) != 478:
        bad(f"row count {len(rows)}, expected 478")

    types = Counter(r["type"] for r in rows)
    for t, n in EXPECT_TYPE.items():
        if types.get(t) != n:
            bad(f"{t}: {types.get(t, 0)} rows, expected {n}")

    geoids = Counter(r["geoid"] for r in rows)
    dupes = [g for g, n in geoids.items() if n > 1]
    if dupes:
        bad(f"duplicate geoid(s): {dupes[:5]}")

    counties = {r["name"] for r in rows if r["type"] == "county"}
    if len(counties) != 67:
        bad(f"{len(counties)} distinct county names, expected 67")

    # A municipality whose county is not a Florida county means the spine join
    # went wrong, and every county-scoped match downstream is suspect.
    for r in rows:
        if r["type"] != "county" and r["county"] and r["county"] not in counties:
            bad(f"{r['name']}: county {r['county']!r} is not a Florida county")

    # No two jurisdictions may share a code URL. This is the check that catches
    # a name collision handing one town's code to another.
    seen = {}
    for r in rows:
        u = (r["code_url"] or "").strip().lower()
        if not u:
            continue
        if u in seen:
            bad(f"{r['name']} and {seen[u]} share code_url {u}")
        seen[u] = r["name"]

    for r in rows:
        nm = r["name"]
        if r["code_status"] not in STATUS:
            bad(f"{nm}: code_status {r['code_status']!r}")
        if r["publisher"] not in PUBLISHER:
            bad(f"{nm}: publisher {r['publisher']!r}")
        if (r["source"] or "") not in SOURCE:
            bad(f"{nm}: source {r['source']!r}")
        if r["official_status"] not in OFFICIAL:
            bad(f"{nm}: official_status {r['official_status']!r}")

        online = (r["code_status"] or "").startswith("online") or \
            r["code_status"] == "ordinances-only"
        if online and not r["code_url"]:
            bad(f"{nm}: online but no code_url")
        if not online and r["code_url"]:
            bad(f"{nm}: not online but carries a code_url")
        if online and not re.match(r"^https://", r["code_url"] or ""):
            bad(f"{nm}: code_url is not https")
        if online and r["publisher"] in ("none", "unknown"):
            bad(f"{nm}: online with publisher {r['publisher']!r}")

        for f in ("codified_through", "code_last_updated", "source_checked_date"):
            v = (r[f] or "")[:10]
            if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
                bad(f"{nm}: {f} {v!r} is not an ISO date")
            elif v and v > today:
                bad(f"{nm}: {f} {v} is in the future")

        if not r["statement"]:
            bad(f"{nm}: no statement")
        elif nm not in r["statement"]:
            bad(f"{nm}: statement does not name the jurisdiction")

        # These three columns render into HTML. seo-lint.mjs fails the site
        # build on any dash character, so a dash arriving from an API is a
        # broken deploy, caught here rather than at 3am on the Pages build.
        for f in ("name", "notes", "statement"):
            if DASHES.search(r[f] or ""):
                bad(f"{nm}: {f} contains a dash character")
            if re.search(r"\w: ", r[f] or ""):
                warn(f"{nm}: {f} contains a mid-sentence colon")

    # Every Municode URL must have a resolver check that passed. A 200 from the
    # library host proves nothing, because it serves a shell for any slug.
    ok_checks = {r["url"] for r in con.execute(
        "SELECT url FROM checks WHERE status=200")}
    for r in rows:
        if r["publisher"] == "municode" and r["code_url"]:
            slug = r["code_url"].split("/fl/")[-1].split("/")[0]
            probe = ("https://library.municode.com/localapi/Organizations/"
                     f"GetByUrlEncodedNames/fl/{slug}/")
            if probe not in ok_checks:
                bad(f"{r['name']}: Municode URL never verified by the resolver")
        elif r["code_url"] and r["publisher"] != "municode":
            if (r["source"] or "") not in ("browser", "manual"):
                bad(f"{r['name']}: non-Municode URL with source {r['source']!r}; "
                    f"those hosts refuse scripted requests and must be read in "
                    f"a browser")

    # `unknown` is a permitted terminal value, but only when it is honest about
    # itself. A row that says "we do not know" without saying what was checked
    # is indistinguishable from a row nobody looked at.
    unresolved = [r for r in rows if r["code_status"] == "unknown"]
    for r in unresolved:
        if not (r["notes"] or "").strip():
            bad(f"{r['name']}: status unknown with no note saying what was checked")
    if unresolved:
        warn(f"{len(unresolved)} row(s) are recorded as unknown; each states "
             f"what was checked, and the published counts report them "
             f"separately rather than folding them into a finding")

    st = Counter(r["code_status"] for r in rows)
    pub = Counter(r["publisher"] for r in rows if r["publisher"] != "unknown")
    print(f"rows {len(rows)}  " + "  ".join(f"{k} {v}" for k, v in st.most_common()))
    print("publishers: " + "  ".join(f"{k} {v}" for k, v in pub.most_common()))
    for w in warns:
        print(f"  warn  {w}")
    for f in fails:
        print(f"  FAIL  {f}", file=sys.stderr)
    if fails:
        sys.exit(f"\n{len(fails)} check(s) failed")
    print("all checks passed" if not warns else f"\n{len(warns)} warning(s)")


if __name__ == "__main__":
    main()
