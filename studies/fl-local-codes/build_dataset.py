#!/usr/bin/env python3
"""Where every Florida local government publishes its code of ordinances.

    python3 build_dataset.py --limit 20      # try it
    python3 build_dataset.py                 # the full run
    python3 build_dataset.py --worklist      # what still needs a human

THE GAP THIS MEASURES. Municipal law is the hardest layer of American law to
locate. There is no master index, and the Library of Congress guide says so
outright: each commercial codifier lists only its own clients, so a reader who
does not already know who publishes a town's code has nowhere to start. Florida
has 478 local governments with ordinance power. Municode carries roughly 400 of
them, American Legal about eleven, General Code one. The rest self-host a PDF or
publish nothing at all, and NO PUBLIC LIST SAYS WHICH IS WHICH.

That residue is the dataset. Anybody can link to Municode. The citable fact is
which Florida city or county a researcher cannot reach that way, and how stale
the codes are that do exist.

TWO THINGS THAT LOOK TRUE AND ARE NOT, both learned by probing the API:

  ClassificationId is not jurisdiction type. Palmetto Bay is 9, Jacksonville
  is 3, and 80 municipalities sit in 6. Type comes from the Census, and
  Municode rows are joined by normalised name.

  Being a Municode client is not having a code. ClientContent returns an empty
  codes[] for some clients, St. Johns County among them today. "On Municode"
  means a codes[] entry with contentTypeId == CODES, never mere membership.

A THIRD, about verification: library.municode.com/fl/<anything> returns a 200
SPA shell for slugs that do not exist, so a HEAD request proves nothing. The
resolver the page itself calls does prove it, and that is what verify_slug uses.
"""
import argparse, csv, io, json, os, re, sqlite3, subprocess, sys, time
import urllib.error, urllib.request
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "fl-local-codes.db")
MANUAL = os.path.join(HERE, "manual.tsv")
WORKLIST = os.path.join(HERE, "worklist.tsv")

UA = ("StepUpLaw local code finder (Klagge Law PLLC; office@stepuplaw.com) "
      "1 req/sec, public metadata only, no code text")
DELAY = 1.0

API = "https://api.municode.com"
LIB = "https://library.municode.com"
CENSUS_CSV = ("https://www2.census.gov/programs-surveys/popest/datasets/"
              "2020-2024/cities/totals/sub-est2024_12.csv")

STATE = "FL"
STATE_FIPS = "12"

SCHEMA = """
CREATE TABLE IF NOT EXISTS raw (
  url TEXT PRIMARY KEY, fetched TEXT, status INTEGER, body TEXT);
CREATE TABLE IF NOT EXISTS checks (
  url TEXT, method TEXT, status INTEGER, checked TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS jurisdictions (
  geoid TEXT PRIMARY KEY,
  name TEXT, type TEXT, county TEXT, counties TEXT, population INTEGER,
  code_status TEXT, publisher TEXT, code_url TEXT,
  publisher_client_id TEXT, code_product_id TEXT,
  codified_through TEXT, code_last_updated TEXT,
  pdf_available INTEGER, pending_ordinances_count INTEGER,
  official_status TEXT, source TEXT, source_checked_date TEXT,
  notes TEXT, statement TEXT);
CREATE TABLE IF NOT EXISTS chapters (
  geoid TEXT, name TEXT, product_id TEXT, job_id TEXT, node_id TEXT,
  node_order INTEGER, chapter_label TEXT, chapter_heading TEXT,
  url TEXT, statement TEXT);
"""

_last_hit = [0.0]


def db_open():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def fetch(con, url, expect_keys=None, refetch=False, want="json"):
    """One cached, rate-limited GET.

    A 200 IS NOT DATA. Municode answers a bad path with a 200 and an HTML
    shell, and GovInfo taught the same lesson in build-usc.py, so the body is
    asserted to parse and to carry the keys the caller named. A response that
    fails the assertion is not cached, because caching a lie makes every later
    run wrong in the same way and hides it.
    """
    if not refetch:
        r = con.execute("SELECT body FROM raw WHERE url=?", (url,)).fetchone()
        if r:
            return json.loads(r["body"]) if want == "json" else r["body"]

    wait = DELAY - (time.time() - _last_hit[0])
    if wait > 0:
        time.sleep(wait)

    body, status = None, 0
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "application/json" if want == "json" else "*/*"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                status = resp.status
                body = resp.read().decode("utf-8", "replace")
            break
        except urllib.error.HTTPError as e:
            status = e.code
            if e.code in (204, 404):
                body = ""
                break
            if attempt == 2:
                raise
        except Exception:
            if attempt == 2:
                raise
        time.sleep(DELAY * (attempt + 2) * 2)
    _last_hit[0] = time.time()

    if want == "json":
        if not body:
            return None
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise RuntimeError(f"{url}: 200 but not JSON, the server served a page")
        if expect_keys:
            probe = data[0] if isinstance(data, list) and data else data
            missing = [k for k in expect_keys if k not in probe]
            if missing:
                raise RuntimeError(f"{url}: JSON without {missing}")
        con.execute("INSERT OR REPLACE INTO raw VALUES (?,?,?,?)",
                    (url, today(), status, body))
        con.commit()
        return data

    con.execute("INSERT OR REPLACE INTO raw VALUES (?,?,?,?)",
                (url, today(), status, body))
    con.commit()
    return body


def today():
    return __import__("datetime").date.today().isoformat()


# --------------------------------------------------------------------------
# The spine: every Florida county and municipality, from one authority.
# --------------------------------------------------------------------------
TYPE_RX = re.compile(r"\b(city|town|village)\b$", re.I)

# The Census carries one Florida legal name that states its own type inside the
# name. Everyone, including its own charter's short title, says "Islamorada".
DISPLAY = {"Islamorada, Village of Islands": "Islamorada"}


def load_census(con, refetch=False):
    body = fetch(con, CENSUS_CSV, refetch=refetch, want="text")
    rows = list(csv.DictReader(io.StringIO(body)))
    counties, places, parts = {}, {}, defaultdict(list)

    for r in rows:
        if r["SUMLEV"] == "050":
            nm = re.sub(r"\s+County$", "", r["NAME"])
            counties[STATE_FIPS + r["COUNTY"]] = {
                "geoid": STATE_FIPS + r["COUNTY"], "name": nm, "type": "county",
                "county": nm, "counties": nm,
                "population": int(r["POPESTIMATE2024"] or 0)}
        elif r["SUMLEV"] == "162":
            m = TYPE_RX.search(r["NAME"])
            if not m:
                continue
            legal = TYPE_RX.sub("", r["NAME"]).strip()
            places[STATE_FIPS + r["PLACE"]] = {
                "geoid": STATE_FIPS + r["PLACE"],
                "name": DISPLAY.get(legal, legal), "legal_name": legal,
                "type": m.group(1).lower(),
                "population": int(r["POPESTIMATE2024"] or 0)}
        elif r["SUMLEV"] == "157":
            parts[STATE_FIPS + r["PLACE"]].append(
                (int(r["POPESTIMATE2024"] or 0), r["COUNTY"]))

    for geoid, p in places.items():
        got = sorted(parts.get(geoid, []), reverse=True)
        names = [counties[STATE_FIPS + c]["name"] for _, c in got
                 if STATE_FIPS + c in counties]
        p["county"] = names[0] if names else ""
        p["counties"] = "|".join(names)

    spine = {**counties, **places}
    if len(counties) != 67:
        sys.exit(f"census: {len(counties)} counties, expected 67")
    if len(places) != 411:
        sys.exit(f"census: {len(places)} municipalities, expected 411")
    return spine


# --------------------------------------------------------------------------
# Municode
# --------------------------------------------------------------------------
def municode_clients(con, refetch=False):
    data = fetch(con, f"{API}/Clients/stateAbbr?stateAbbr={STATE}",
                 expect_keys=["ClientID", "ClientName"], refetch=refetch)
    if not (350 <= len(data) <= 500):
        sys.exit(f"municode: {len(data)} clients, outside the expected band")
    return data


# Leading "City of" and the trailing " County" only. A TRAILING TYPE WORD IS
# PART OF THE NAME, not a label: Florida has both a Melbourne and a Melbourne
# Village, and stripping the tail collapses them onto each other, which loses
# the real Melbourne to an ambiguous match rather than to a missing code.
_STRIP = re.compile(r"^(city|town|village)\s+of\s+|\s+county$", re.I)

# Legal names the Census carries in full and every codifier shortens.
ALIAS = {"islamorada village of islands": "islamorada"}

# Dropped only on the second matching pass, never the first.
_TYPE_TAIL = re.compile(r"\s+(city|town|village)$", re.I)


def norm_name(s):
    s = s.lower().strip()
    s = s.replace(" - ", "-").replace(" -", "-").replace("- ", "-")
    s = _STRIP.sub("", s).strip()
    s = re.sub(r"^saint\b", "st.", s)
    s = re.sub(r"^st\b(?!\.)", "st.", s)
    s = re.sub(r"[^a-z0-9. ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return ALIAS.get(s, s)


def slug_for(client_name):
    return client_name.lower().replace(" ", "_")


def is_county_client(name):
    return name.strip().lower().endswith("county")


def match_municode(spine, clients):
    """Join Municode clients onto the Census spine by normalised name.

    Counties and municipalities are matched in separate namespaces because
    Florida has a Lake County and a town called Lake Park, and pooling them
    would hand a county's code to a city.
    """
    by_type = defaultdict(dict)
    for g, j in spine.items():
        key = "county" if j["type"] == "county" else "muni"
        by_type[key].setdefault(norm_name(j["name"]), []).append(g)

    # Two passes, and the order is the point. An exact name match is taken
    # first for every client, so "Melbourne" claims Melbourne before anything
    # is allowed to guess. Only then is a trailing type word treated as
    # droppable, which is what lets Municode's "Indian Creek Village" reach the
    # Census's "Indian Creek". Running the loose pass first would let a village
    # steal the city that shares its name.
    matched, pending = {}, []
    for c in clients:
        nm = c["ClientName"]
        key = "county" if is_county_client(nm) else "muni"
        cand = by_type[key].get(norm_name(nm), [])
        if len(cand) == 1 and cand[0] not in matched:
            matched[cand[0]] = c
        else:
            pending.append((c, key))

    unmatched_clients = []
    for c, key in pending:
        loose = norm_name(_TYPE_TAIL.sub("", c["ClientName"]).strip())
        cand = [g for g in by_type[key].get(loose, []) if g not in matched]
        if loose and len(cand) == 1:
            matched[cand[0]] = c
        else:
            unmatched_clients.append(c)
    return matched, unmatched_clients


def municode_content(con, client_id, refetch=False):
    """The published code for a client, or None.

    ★ hideInLibrary IS A PUBLICATION FACT, NOT A DISPLAY PREFERENCE. Lighthouse
    Point carries a Code of Ordinances product last updated in 2018 with 60
    ordinances pending codification, flagged hideInLibrary, while the city
    itself has since rewritten the code and hosts it elsewhere. The Municode
    page still loads and search engines still index it, so a reader who arrives
    from a search reads a superseded code with nothing on the page to say so.
    Those are excluded from `online-html` and reported separately, because
    pointing a reader at one would be worse than pointing them nowhere.
    """
    data = fetch(con, f"{API}/ClientContent/{client_id}", refetch=refetch)
    if not data:
        return None, None
    codes = [c for c in (data.get("codes") or [])
             if c.get("contentTypeId") == "CODES"]
    if not codes:
        return None, None
    codes.sort(key=lambda c: (c.get("productName") != "Code of Ordinances",
                              c.get("productId")))
    live = [c for c in codes if not c.get("hideInLibrary")]
    if live:
        return live[0], None
    return None, codes[0]


BANNER_DATE = re.compile(
    r"[Cc]odified through\s+(?:.*?)\s*adopted\s+([A-Z][a-z]+ \d{1,2}, \d{4})", re.S)
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], 1)}


def municode_job(con, product_id, refetch=False):
    """Job id and the codification date the publisher states.

    ★ THE BANNER IS NOT ALWAYS A DATE. Cocoa's reads "Ordinance No. 11-2025,
    adopted October 14, 2026" on a supplement Municode itself published on
    2025-10-28. A code cannot be codified through an ordinance adopted after it
    was published, so the year is a typo at the source. Guessing the intended
    year would be inventing data, so a date that fails the test is dropped from
    the date column and the banner's own words are carried in a note instead.
    The reader learns both that the date is unusable and exactly why.
    """
    data = fetch(con, f"{API}/Jobs/latest/{product_id}", refetch=refetch)
    if not data:
        return None, None, None
    job_id = data.get("Id")
    codified, suspect = None, None
    m = BANNER_DATE.search(data.get("BannerText") or "")
    if m:
        mon, day, yr = re.match(r"([A-Z][a-z]+) (\d{1,2}), (\d{4})",
                                m.group(1)).groups()
        codified = f"{yr}-{MONTHS[mon]:02d}-{int(day):02d}"
        published = (data.get("PublishDate") or "")[:10]
        if codified > today() or (published and codified > published):
            suspect = (
                "the publisher states codification through an ordinance "
                f"adopted {m.group(1)}, which postdates the supplement it "
                f"published on {published or 'an earlier date'}, so the stated "
                "date is not recorded")
            codified = None
    return job_id, codified, suspect


def hint_alive(url):
    """Does the website Municode holds for this client actually resolve?

    * THE HINT IS MUNICODE'S CLAIM, NOT THIS SURVEY'S FINDING. Hamilton County
    is carried as client 11540 with Website www.hamiltoncountyflorida.com,
    which refuses connections; the county's live site is hamiltoncountyfl.com.
    A bare URL in the worklist reads as a checked address, so a researcher who
    follows it concludes the county has no web presence when it has one.
    Recording whether it answers costs one HEAD and keeps the column honest.
    """
    if not url:
        return ""
    u = url if url.startswith("http") else "https://" + url
    req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return "live" if r.status < 400 else "http-%d" % r.status
    except urllib.error.HTTPError as e:
        return "live" if e.code in (403, 405, 406) else "http-%d" % e.code
    except Exception as e:
        return "unreachable (%s)" % type(e).__name__


def resolve_by_slug(con, name, kind, refetch=False):
    """Ask the library directly whether a slug exists, ignoring the client list.

    ★ THE STATE CLIENT LIST IS INCOMPLETE. Lighthouse Point resolves in the
    library as ClientID 3021 and serves a full code of ordinances, and it does
    not appear in Clients/stateAbbr?stateAbbr=FL at all. Trusting that list
    alone would have published "no online code" for a city whose code is one
    click away, which is the single worst error this dataset can make. So every
    jurisdiction the list does not account for is asked about by name as well.
    """
    base = name.lower().replace(" ", "_")
    cands = [base + "_county"] if kind == "county" else [base]
    if kind != "county":
        cands += [base + "_beach", "city_of_" + base, "town_of_" + base]
    for slug in cands:
        url = (f"{LIB}/localapi/Organizations/GetByUrlEncodedNames/"
               f"{STATE.lower()}/{slug}/")
        try:
            data = fetch(con, url, refetch=refetch)
        except Exception:
            continue
        if data and data.get("ClientID") and \
                (data.get("State") or {}).get("StateAbbreviation") == STATE:
            con.execute("INSERT INTO checks VALUES (?,?,?,?,?)",
                        (url, "api", 200, today(), "resolved outside the client list"))
            return data["ClientID"], f"{LIB}/{STATE.lower()}/{slug}"
    return None, None


def verify_slug(con, client_name, client_id, refetch=False):
    """Prove the library URL resolves to THIS client.

    library.municode.com/fl/<anything> is a 200 SPA shell, so the only honest
    check is the resolver the page itself calls.
    """
    slug = slug_for(client_name)
    url = f"{LIB}/localapi/Organizations/GetByUrlEncodedNames/{STATE.lower()}/{slug}/"
    try:
        data = fetch(con, url, refetch=refetch)
    except Exception as e:
        con.execute("INSERT INTO checks VALUES (?,?,?,?,?)",
                    (url, "api", 0, today(), f"{type(e).__name__}"))
        return None
    ok = bool(data) and str(data.get("ClientID")) == str(client_id)
    con.execute("INSERT INTO checks VALUES (?,?,?,?,?)",
                (url, "api", 200 if ok else 404, today(),
                 "" if ok else "slug did not resolve to this client"))
    return f"{LIB}/{STATE.lower()}/{slug}" if ok else None


# --------------------------------------------------------------------------
# Rows
# --------------------------------------------------------------------------
PUB_SAYS = {
    "municode": "Municode", "american-legal": "American Legal Publishing",
    "general-code": "General Code", "code-publishing": "Code Publishing",
    "municipal-code-online": "MunicipalCodeOnline", "elaws": "eLaws",
    "self-hosted": "its own website", "none": "no publisher",
    "unknown": "an undetermined publisher",
}


def statement(r):
    if r["type"] == "county":
        who, where = f"{r['name']} County, Florida,", ""
    else:
        who = f"The {r['type']} of {r['name']}, Florida,"
        where = f" in {r['county']} County" if r["county"] else ""
        who = f"The {r['type']} of {r['name']}{where}, Florida,"
    st = r["code_status"]
    if st == "no-online-code":
        s = f"{who} publishes no code of ordinances online."
    elif st == "unknown":
        s = (f"{who} is carried by no commercial code publisher, and this "
             f"survey could not confirm what it publishes instead.")
    elif st == "ordinances-only":
        # ★ THE DISTINCTION THE DATASET EXISTS TO DRAW. A jurisdiction that
        # posts its ordinances one PDF at a time has published its law without
        # codifying it, and a reader who wants to know the rule on fences has
        # to read every ordinance ever passed to be sure. Folding these in with
        # the towns that publish a code would hide the commonest condition in
        # rural Florida.
        s = (f"{who} publishes individual ordinances online at {r['code_url']} "
             f"but no codified code of ordinances.")
    else:
        fmt = "as a searchable web code" if st == "online-html" else "as a PDF"
        s = (f"{who} publishes its code of ordinances {fmt} through "
             f"{PUB_SAYS.get(r['publisher'], r['publisher'])} at {r['code_url']}.")
    if r.get("codified_through"):
        s += f" The code is codified through ordinances adopted {r['codified_through']}."
    if r.get("pending_ordinances_count"):
        s += (f" {r['pending_ordinances_count']} adopted ordinance(s) await "
              f"codification.")
    return s + f" Checked {r['source_checked_date']}."


def load_manual():
    """Hand-resolved rows, keyed by geoid. Manual always wins.

    The vendors that 403 a script (American Legal, eCode360) and the towns that
    self-host are read once in a browser and recorded here. This file is the
    part of the dataset no API can produce and is committed to git for that
    reason.
    """
    if not os.path.exists(MANUAL):
        return {}
    out = {}
    with open(MANUAL, encoding="utf-8") as fh:
        for row in csv.DictReader(
                (l for l in fh if not l.startswith("#")), delimiter="\t"):
            if row.get("geoid"):
                out[row["geoid"].strip()] = {k: (v or "").strip()
                                             for k, v in row.items()}
    return out


def build(args):
    con = db_open()
    t0 = time.time()
    F = Counter()

    spine = load_census(con, args.refetch)
    F["census_rows"] = len(spine)

    clients = municode_clients(con, args.refetch)
    F["municode_clients"] = len(clients)

    matched, unmatched_clients = match_municode(spine, clients)
    F["municode_matched"] = len(matched)
    F["municode_unmatched_clients"] = len(unmatched_clients)

    manual = load_manual()
    F["manual_rows"] = len(manual)

    rows, worklist = [], []
    items = sorted(spine.items())
    if args.limit:
        items = items[:args.limit]

    for i, (geoid, j) in enumerate(items, 1):
        r = {k: v for k, v in j.items() if k != "legal_name"}
        r.update({"code_status": "unknown", "publisher": "unknown",
                  "code_url": "", "publisher_client_id": "",
                  "code_product_id": "", "codified_through": "",
                  "code_last_updated": "", "pdf_available": 0,
                  "pending_ordinances_count": None,
                  "official_status": "unstated", "source": "",
                  "source_checked_date": today(), "notes": ""})

        c = matched.get(geoid)
        if c:
            r["publisher_client_id"] = str(c["ClientID"])
            code, hidden = municode_content(con, c["ClientID"], args.refetch)
            if code:
                url = verify_slug(con, c["ClientName"], c["ClientID"],
                                  args.refetch)
                if url:
                    job_id, codified, suspect = municode_job(
                        con, code["productId"], args.refetch)
                    if suspect:
                        r["notes"] = suspect
                        F["suspect_codified_date"] += 1
                    r.update({
                        "code_status": "online-html", "publisher": "municode",
                        "code_url": url,
                        "code_product_id": str(code["productId"]),
                        "codified_through": codified or "",
                        "code_last_updated":
                            (code.get("latestUpdatedDate") or "")[:10],
                        "pdf_available": int(bool(code.get("hasPdf"))),
                        "pending_ordinances_count": code.get("newOrdCount"),
                        "official_status": "unstated",
                        "source": "municode-api"})
                else:
                    r["notes"] = "Municode client, library slug did not resolve"
            elif hidden:
                r["notes"] = (
                    "Municode carries a hidden code product last updated "
                    f"{(hidden.get('latestUpdatedDate') or '')[:10]} with "
                    f"{hidden.get('newOrdCount') or 0} ordinances pending; "
                    "it is not listed in the library and is treated here as "
                    "superseded")
            else:
                r["notes"] = "Municode client with no published code product"
            F["municode_with_code"] += 1 if r["publisher"] == "municode" else 0

        # Second pass, OUTSIDE the client-list branch on purpose: it exists
        # precisely for the jurisdictions that branch never sees.
        if r["code_status"] == "unknown":
            cid, url = resolve_by_slug(con, j["name"], j["type"], args.refetch)
            if cid:
                code, hidden2 = municode_content(con, cid, args.refetch)
                if not code and hidden2:
                    r["publisher_client_id"] = str(cid)
                    r["notes"] = (
                        "Municode carries a hidden code product last updated "
                        f"{(hidden2.get('latestUpdatedDate') or '')[:10]} with "
                        f"{hidden2.get('newOrdCount') or 0} ordinances pending; "
                        "it is not listed in the library and is treated here as "
                        "superseded")
                    F["municode_hidden"] += 1
                if code:
                    job_id, codified, suspect = municode_job(
                        con, code["productId"], args.refetch)
                    if suspect:
                        r["notes"] = suspect
                    r.update({
                        "code_status": "online-html", "publisher": "municode",
                        "code_url": url, "publisher_client_id": str(cid),
                        "code_product_id": str(code["productId"]),
                        "codified_through": codified or "",
                        "code_last_updated":
                            (code.get("latestUpdatedDate") or "")[:10],
                        "pdf_available": int(bool(code.get("hasPdf"))),
                        "pending_ordinances_count": code.get("newOrdCount"),
                        "source": "municode-api",
                        "notes": "resolved by library slug; absent from the "
                                 "state client list"})
                    F["municode_off_list"] += 1

        m = manual.get(geoid)
        if m:
            for k in ("code_status", "publisher", "code_url", "notes",
                      "official_status", "codified_through"):
                if m.get(k):
                    r[k] = m[k]
            r["source"] = m.get("source") or "browser"
            if m.get("source_checked_date"):
                r["source_checked_date"] = m["source_checked_date"]
            # A hand pass that moves a jurisdiction off Municode must not leave
            # Municode's product id, update date and pending count attached to
            # an American Legal URL. Those columns describe the Municode record
            # and mean nothing once the row points somewhere else.
            # A hand-entered Municode URL is held to the same standard as an
            # automatic one. Duval's code is Jacksonville's by consolidation,
            # but that is a claim about a URL and it gets resolved like any
            # other rather than trusted because a human typed it.
            if r["publisher"] == "municode" and r["code_url"]:
                slug = r["code_url"].split("/fl/")[-1].split("/")[0]
                url = (f"{LIB}/localapi/Organizations/GetByUrlEncodedNames/"
                       f"{STATE.lower()}/{slug}/")
                data = None
                try:
                    data = fetch(con, url, refetch=args.refetch)
                except Exception:
                    pass
                con.execute("INSERT INTO checks VALUES (?,?,?,?,?)",
                            (url, "api", 200 if data else 404, today(),
                             "manual row" if data else "manual row did not resolve"))
                if not data:
                    sys.exit(f"{r['name']}: manual Municode slug {slug!r} does "
                             f"not resolve; fix manual.tsv rather than shipping it")
            if r["publisher"] != "municode":
                r["code_product_id"] = ""
                r["code_last_updated"] = ""
                r["pdf_available"] = 0
                r["pending_ordinances_count"] = None
                if not m.get("publisher_client_id"):
                    r["publisher_client_id"] = ""

        if r["code_status"] == "unknown":
            # Say what was checked. An unexplained "unknown" is indistinguishable
            # from a row nobody looked at, and the checker rejects one.
            base = ("no commercial code publisher carries this jurisdiction, "
                    "having checked the Municode client list and library "
                    "resolver, the American Legal Florida region listing, "
                    "eCode360 and MunicipalCodeOnline")
            r["notes"] = f"{base}; {r['notes']}" if r["notes"] else base
            worklist.append(r)
            F["unresolved"] += 1
        r["statement"] = statement(r)
        rows.append(r)
        if args.verbose and i % 50 == 0:
            print(f"  {i}/{len(items)}", file=sys.stderr)

    con.execute("DELETE FROM jurisdictions")
    cols = ["geoid", "name", "type", "county", "counties", "population",
            "code_status", "publisher", "code_url", "publisher_client_id",
            "code_product_id", "codified_through", "code_last_updated",
            "pdf_available", "pending_ordinances_count", "official_status",
            "source", "source_checked_date", "notes", "statement"]
    con.executemany(
        f"INSERT INTO jurisdictions VALUES ({','.join('?' * len(cols))})",
        [tuple(r.get(c) for c in cols) for r in rows])
    con.commit()

    F["rows"] = len(rows)
    F["online_html"] = sum(1 for r in rows if r["code_status"] == "online-html")
    F["online_pdf"] = sum(1 for r in rows if r["code_status"] == "online-pdf-only")
    F["no_online_code"] = sum(1 for r in rows if r["code_status"] == "no-online-code")

    with open(WORKLIST, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["geoid", "name", "type", "county", "population",
                    "municode_client", "hint", "hint_status", "notes"])
        for r in sorted(worklist, key=lambda x: -x["population"]):
            c = matched.get(r["geoid"])
            hint = (c or {}).get("Website", "")
            w.writerow([r["geoid"], r["name"], r["type"], r["county"],
                        r["population"], c["ClientID"] if c else "",
                        hint, hint_alive(hint), r["notes"]])

    meta = {"state": STATE,
            "sources": {"spine": CENSUS_CSV, "municode_api": API,
                        "manual": "manual.tsv, read in a browser"},
            "funnel": dict(F),
            "runtime_minutes": round((time.time() - t0) / 60, 1)}
    with open(os.path.join(HERE, "fl-local-codes-run.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps(meta, indent=2))
    if F["unresolved"]:
        print(f"\n{F['unresolved']} row(s) need a browser pass: {WORKLIST}",
              file=sys.stderr)


def status():
    con = db_open()
    n = con.execute("SELECT COUNT(*) c FROM jurisdictions").fetchone()["c"]
    if not n:
        print("no rows yet")
        return
    for r in con.execute("SELECT code_status, publisher, COUNT(*) c "
                         "FROM jurisdictions GROUP BY 1,2 ORDER BY c DESC"):
        print(f"  {r['code_status']:18} {r['publisher']:16} {r['c']:4}")
    print(f"  {'TOTAL':18} {'':16} {n:4}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--refetch", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    if a.status:
        status()
    else:
        build(a)


if __name__ == "__main__":
    main()
