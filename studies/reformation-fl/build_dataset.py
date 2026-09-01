#!/usr/bin/env python3
"""Build the Florida reformation dataset.

    python3 build_dataset.py            # ~2 min on the SSD slice

UNIT is the decision. One row per Florida appellate decision that litigates the
reformation of an instrument, carrying: which instrument, what went wrong,
whether the court reformed it, and which statutory regime was in force.

RETRIEVE WIDE, FILTER HARD. `reform` is polysemous -- tort reform, prison
reform, reform school -- so the query is deliberately over-inclusive and
lib/reformation.py does the work. Every stage of the funnel is counted and
reported; silent filtering is the commonest defect in this kind of study and
this project has already been bitten by it once.
"""
import argparse, json, os, sqlite3, sys, time
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
from lib import reformation as R
from lib import terms as T

QUERY = ('(reformation OR reformed OR reforming OR reform OR scrivener '
         'OR "mutual mistake" OR "unilateral mistake" OR "drafting error" '
         'OR "732.615" OR "736.0415" OR "732.616") AND '
         '(will OR trust OR deed OR codicil OR testament OR contract OR policy '
         'OR beneficiary OR settlor OR grantor OR conveyance)')

COURTS_TSV = os.path.join(CASELAW, "courts-by-state.tsv")

# Court rule amendments, bar admissions and advisory opinions are published in
# the same reporters as decisions and match the same words. They are not cases.
ADMIN_RX = __import__("re").compile(
    r"^In\s+Re:?\s+Amendments?\b|^Amendments?\s+to\s+the\s+Florida\b"
    r"|^In\s+Re:?\s+(?:Florida\s+)?(?:Rules?|Standard\s+Jury)\b"
    r"|^Advisory\s+Opinion\b|^In\s+Re:?\s+(?:Petition|Report)\s+of\b", __import__("re").I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out = a.out or os.path.join(here, "reformation-fl.db")

    jur = {}
    with open(COURTS_TSV) as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                jur[p[1]] = p[2]

    con, info = cc.connect(scope="fl")
    t0 = time.time()
    ids = cc.fts_ids(con, QUERY, warn_at=10_000_000)
    print(f"# retrieved {len(ids):,} opinions [{time.time()-t0:.1f}s]", file=sys.stderr)

    con.execute("DROP TABLE IF EXISTS temp.h")
    con.execute("CREATE TEMP TABLE h(id INTEGER PRIMARY KEY)")
    con.executemany("INSERT OR IGNORE INTO h VALUES (?)", [(i,) for i in ids])
    rows = con.execute("""
        SELECT h.id AS oid, o.cluster_id AS cid,
               COALESCE(cc2.court, i.court) AS court,
               COALESCE(o.block_id, i.block_id) AS b,
               COALESCE(o.idx, i.idx) AS i,
               COALESCE(m.date_filed, i.date_filed) AS filed,
               COALESCE(m.case_name, i.case_name) AS name,
               COALESCE(m.citation_count, 0) AS cites
        FROM h LEFT JOIN opinions o ON o.id = h.id
        LEFT JOIN cluster_court cc2 ON cc2.cluster_id = o.cluster_id
        LEFT JOIN m.cluster_meta m ON m.cluster_id = o.cluster_id
        LEFT JOIN incoming i ON i.id = h.id""").fetchall()

    F = Counter()
    F["opinions_retrieved"] = len(rows)
    seen, work = set(), []
    for r in rows:
        if jur.get(r["court"] or "") not in ("S", "SA"):
            F["dropped_not_state_appellate"] += 1
            continue
        if r["b"] is None:
            F["dropped_no_text_pointer"] += 1
            continue
        k = r["cid"] if r["cid"] is not None else ("o", r["oid"])
        if k in seen:
            F["dropped_duplicate_cluster"] += 1
            continue
        # Rule-amendment orders are administrative, not litigation. Four of them
        # were sitting in the will set, and one was the leading row in a table
        # about how often courts reform wills.
        nm = (r["name"] or "")
        if ADMIN_RX.search(nm):
            F["dropped_administrative_order"] += 1
            continue
        seen.add(k)
        work.append(r)
    F["decisions_to_read"] = len(work)
    print(f"# {len(work):,} appellate decisions to read", file=sys.stderr)

    db = sqlite3.connect(out)
    db.executescript("""
        PRAGMA journal_mode=WAL;
        DROP TABLE IF EXISTS decisions;
        CREATE TABLE decisions(
            oid INTEGER, cid INTEGER, name TEXT, court TEXT, year INTEGER,
            cites INTEGER, instrument TEXT, outcome TEXT, regime TEXT,
            errors TEXT, n_reform_sents INTEGER, cites_statute INTEGER,
            key_sentence TEXT);
    """)

    kept = 0
    t0 = time.time()
    for k, r in enumerate(work):
        if k and k % 500 == 0:
            print(f"#   {k}/{len(work)} {time.time()-t0:.0f}s", file=sys.stderr)
        try:
            txt = cc.doc_text(con, r["b"], r["i"])
        except Exception:
            F["dropped_text_error"] += 1
            continue
        if not txt:
            F["dropped_empty_text"] += 1
            continue

        sents = T.sentences(txt)
        rs = [s for s in sents if R.is_reformation(s)]
        if not rs:
            F["dropped_no_reformation_sentence"] += 1
            continue

        blob = " ".join(rs)
        inst = R.instrument(blob)
        if inst == "uncertain":
            inst = R.instrument(txt)          # fall back to the whole opinion
        year = int(r["filed"][:4]) if r["filed"] and r["filed"][:4].isdigit() else None

        # Decision-level outcome: a holding beats a petition, and a petition
        # beats a rule statement. `authority` never contributes -- a sentence
        # describing another case says nothing about how this one came out.
        outs = [R.outcome(s) for s in rs]
        out_lbl = ("granted" if "granted" in outs else
                   "denied" if "denied" in outs else
                   "sought" if "sought" in outs else
                   "rule_stated" if "rule_stated" in outs else
                   "authority" if "authority" in outs else "uncertain")
        key = next((s for s in rs if R.outcome(s) == out_lbl), rs[0])

        errs = R.error_type(blob)
        cites_stat = int(any(c in txt for c in ("732.615", "736.0415", "732.616")))

        db.execute("INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (r["oid"], r["cid"], r["name"], r["court"], year, r["cites"],
                    inst, out_lbl, R.regime(inst, year), ",".join(errs),
                    len(rs), cites_stat, key[:600]))
        kept += 1
        F[f"kept_{inst}"] += 1

    db.commit()
    F["decisions_kept"] = kept
    meta = {"query": QUERY, "scope": "fl state appellate (S+SA)",
            "corpus": "CourtListener bulk snapshot 2026-06-30",
            "funnel": dict(F), "kept": kept,
            "runtime_minutes": round((time.time() - t0) / 60, 1)}
    with open(out.replace(".db", "-run.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta, indent=1), file=sys.stderr)


if __name__ == "__main__":
    main()
