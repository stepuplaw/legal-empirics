#!/usr/bin/env python3
"""Florida holdings resting on statutes that have since changed.

    python3 build_dataset.py --limit 2000     # try it
    python3 build_dataset.py                  # the full run

THE GAP THIS MEASURES. A case-law corpus cannot see a holding the legislature
displaced. If a court construes a section, the legislature later amends it, and
no court has spoken since, the case still reads as good law -- to a researcher,
to a citator that only tracks case-to-case treatment, and to every language
model trained on the reports. Reformation of wills in Florida is the clean
example: 36 Florida decisions state the rule that a will cannot be reformed,
s. 732.615 reversed it in 2011, and six appellate decisions have cited the
statute since. Case law alone gets the answer backwards.

TWO TIERS, AND THE SECOND IS THE NEW PART.

  exposed        the section was amended after the decision came down. Cheap,
                 computable for every year, and an OVERSTATEMENT -- legislatures
                 amend sections constantly for unrelated reasons.
  text_changed   the operative text of that section actually differs between
                 the edition in force when the case was decided and the current
                 one. This is the claim worth making, and it needs versioned
                 statutes, which is why the edition backfill exists.

Tier 2 is only computable where an edition at or before the decision year is
held. flsenate.gov serves 2010 onward, so decisions before 2010 get tier 1 only
and say so in the `tier` column rather than being silently pooled.
"""
import argparse, difflib, json, os, re, sqlite3, sys, time
from collections import Counter

# Paths are configurable so a clone runs somewhere other than the machine that
# built it. CASELAW_HOME is the corpus pipeline (~/caselaw); US_LAW_DB is the
# statutes database, which sits on external storage here because it lives beside
# a 66 GB opinion corpus. A repository that hardcodes one laptop's paths is not
# reproducible, whatever its README claims.
CASELAW = os.environ.get("CASELAW_HOME", os.path.expanduser("~/caselaw"))
sys.path.insert(0, CASELAW)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import clcorpus as cc
import lawcorpus as L
from lib import terms as T

LAW_DB = os.environ.get("US_LAW_DB",
                        "/Volumes/Elements/cl-data/us-law.db")
COURTS_TSV = os.path.join(CASELAW, "courts-by-state.tsv")

# Decisions that construe statutory meaning -- not merely cite a statute.
QUERY = ('(ambiguous OR ambiguity OR ambiguities OR construe OR construed OR '
         'construction OR interpret OR interpreted OR interpretation OR '
         '"plain meaning" OR "legislative intent" OR "rules of statutory construction")')

# "section 732.615", "s. 732.615", "§ 732.615", "Fla. Stat. 732.615"
CITE_RX = re.compile(
    r"(?:sections?|ss?\.|§+|Fla\.\s*Stat\.\s*(?:§+\s*)?|Florida\s+Statutes?[,\s]+"
    r"(?:section\s+)?)\s*(\d{1,3}\.\d{2,5})", re.I)
# The sentence must be about meaning, not merely mention a number.
INTERP_RX = re.compile(
    r"\b(ambigu\w+|constru\w+|interpret\w+|plain\s+meaning|legislative\s+intent|"
    r"meaning\s+of|defines?|definition|term\s+|word\s+|language\s+of)\b", re.I)

H_Y4 = re.compile(r"ch\.\s*(\d{4})-\d+")
H_Y2 = re.compile(r"ch\.\s*(\d{2})-\d+")
H_OLD = re.compile(r"ch\.\s*\d{3,5},\s*(\d{4})")


def hist_years(h):
    ys = set()
    for m in H_Y4.finditer(h):
        ys.add(int(m.group(1)))
    for m in H_Y2.finditer(h):
        y = int(m.group(1))
        ys.add(2000 + y if y <= 26 else 1900 + y)
    for m in H_OLD.finditer(h):
        ys.add(int(m.group(1)))
    return ys


def norm(t):
    """Operative text, comparable across editions.

    The history trail is stripped before diffing: it changes at EVERY amendment
    by definition, so leaving it in would mark every section as changed and the
    tier-2 measurement would be a tautology.
    """
    t = re.split(r"\n\s*History\.", t)[0]
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def load_statutes():
    """cite -> {last_amended, years, editions {year: normalised text}}."""
    con = sqlite3.connect(f"file:{LAW_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    secs = {}
    rows = con.execute(
        "SELECT cite, edition, history, block_id, idx FROM sections "
        "WHERE corpus='flstat'").fetchall()
    editions = sorted({r["edition"] for r in rows})
    print(f"# statute editions held: {', '.join(editions)}", file=sys.stderr)
    for r in rows:
        d = secs.setdefault(r["cite"], {"years": set(), "editions": {}})
        if r["history"]:
            d["years"] |= hist_years(r["history"])
        try:
            txt = L.section_text(con, r["block_id"], r["idx"])
        except Exception:
            txt = None
        if txt:
            d["editions"][int(r["edition"])] = norm(txt)
    for c, d in secs.items():
        d["last_amended"] = max(d["years"]) if d["years"] else None
    con.close()
    print(f"# sections: {len(secs):,}", file=sys.stderr)
    return secs, sorted(int(e) for e in editions)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out = a.out or os.path.join(here, "statutory-staleness.db")

    secs, editions = load_statutes()
    current = max(editions) if editions else None

    jur = {}
    with open(COURTS_TSV) as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                jur[p[1]] = p[2]

    con, info = cc.connect(scope="fl")
    ids = cc.fts_ids(con, QUERY, warn_at=10_000_000)
    print(f"# retrieved {len(ids):,} opinions", file=sys.stderr)
    con.execute("DROP TABLE IF EXISTS temp.h")
    con.execute("CREATE TEMP TABLE h(id INTEGER PRIMARY KEY)")
    con.executemany("INSERT OR IGNORE INTO h VALUES (?)", [(i,) for i in ids])
    rows = con.execute("""
        SELECT h.id AS oid, o.cluster_id AS cid,
               COALESCE(cc2.court,i.court) AS court,
               COALESCE(o.block_id,i.block_id) AS b, COALESCE(o.idx,i.idx) AS i,
               COALESCE(m.date_filed,i.date_filed) AS filed,
               COALESCE(m.case_name,i.case_name) AS name,
               COALESCE(m.citation_count,0) AS cites
        FROM h LEFT JOIN opinions o ON o.id=h.id
        LEFT JOIN cluster_court cc2 ON cc2.cluster_id=o.cluster_id
        LEFT JOIN m.cluster_meta m ON m.cluster_id=o.cluster_id
        LEFT JOIN incoming i ON i.id=h.id""").fetchall()

    F = Counter()
    seen, work = set(), []
    for r in rows:
        if jur.get(r["court"] or "") not in ("S", "SA"):
            F["dropped_not_state_appellate"] += 1
            continue
        if r["b"] is None or not r["filed"]:
            F["dropped_no_text_or_date"] += 1
            continue
        k = r["cid"] if r["cid"] is not None else ("o", r["oid"])
        if k in seen:
            F["dropped_duplicate"] += 1
            continue
        seen.add(k)
        work.append(r)
    if a.limit:
        work = work[:a.limit]
    F["decisions_to_read"] = len(work)
    print(f"# {len(work):,} appellate decisions to read", file=sys.stderr)

    db = sqlite3.connect(out)
    db.executescript("""
        PRAGMA journal_mode=WAL;
        DROP TABLE IF EXISTS holdings;
        CREATE TABLE holdings(
            oid INTEGER, cid INTEGER, name TEXT, court TEXT, year INTEGER,
            cites INTEGER, section TEXT, last_amended INTEGER,
            amendments_since INTEGER, gap_years INTEGER, exposed INTEGER,
            tier TEXT, text_changed INTEGER, similarity REAL,
            edition_at_decision INTEGER, sentence TEXT, statement TEXT);
    """)

    t0, n_rows = time.time(), 0
    for k, r in enumerate(work):
        if k and k % 2000 == 0:
            el = time.time() - t0
            print(f"#   {k:,}/{len(work):,} {el/60:.1f}m "
                  f"eta {(el/k*(len(work)-k))/60:.0f}m", file=sys.stderr, flush=True)
        try:
            txt = cc.doc_text(con, r["b"], r["i"])
        except Exception:
            F["dropped_text_error"] += 1
            continue
        if not txt:
            continue
        year = int(r["filed"][:4])

        # Strict screen: the section must be cited IN a sentence that is about
        # meaning. Document-level co-occurrence overstates this by threefold and
        # is the error METHODOLOGY.md lesson 1 already paid for once.
        found = {}
        for s in T.sentences(txt):
            if not INTERP_RX.search(s):
                continue
            for m in CITE_RX.finditer(s):
                c = m.group(1)
                if c in secs and c not in found:
                    found[c] = s
        if not found:
            F["dropped_no_construed_section"] += 1
            continue

        for c, sent in found.items():
            d = secs[c]
            la = d["last_amended"]
            after = sorted(y for y in d["years"] if y > year)
            exposed = int(bool(after))

            tier, changed, sim, ed_at = "amendment-screen", None, None, None
            avail = [e for e in d["editions"] if e <= year]
            if avail and current in d["editions"]:
                ed_at = max(avail)
                a_txt, b_txt = d["editions"][ed_at], d["editions"][current]
                sim = difflib.SequenceMatcher(None, a_txt, b_txt).ratio()
                changed = int(sim < 0.995)
                tier = "text-diff"
            F[f"tier_{tier}"] += 1

            stmt = (f"{r['name']} ({year}) construes Fla. Stat. s. {c}; "
                    f"the section was last amended in {la}"
                    if la else
                    f"{r['name']} ({year}) construes Fla. Stat. s. {c}")
            if exposed:
                stmt += (f", {len(after)} amendment(s) after the decision"
                         f" (most recent {after[-1]}).")
            else:
                stmt += ", with no amendment after the decision."
            if changed is not None:
                stmt += (" The operative text has changed since."
                         if changed else
                         " The operative text is unchanged since.")

            db.execute("INSERT INTO holdings VALUES "
                       "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (r["oid"], r["cid"], r["name"], r["court"], year,
                        r["cites"], c, la, len(after),
                        (after[-1] - year) if after else None, exposed,
                        tier, changed, sim, ed_at, sent[:500], stmt))
            n_rows += 1
    db.commit()
    db.executescript("CREATE INDEX ix_sec ON holdings(section);"
                     "CREATE INDEX ix_yr ON holdings(year);")

    F["rows"] = n_rows
    meta = {"query": QUERY, "scope": "fl state appellate (S+SA)",
            "corpus": "CourtListener bulk snapshot 2026-06-30",
            "statute_editions": editions, "current_edition": current,
            "funnel": dict(F), "runtime_minutes": round((time.time()-t0)/60, 1)}
    with open(out.replace(".db", "-run.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
