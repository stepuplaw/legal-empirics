#!/usr/bin/env python3
"""Which categories of drafted language get litigated for ambiguity, and how often.

    python3 extract_terms.py --scope fl            # Florida, SSD, ~2 min
    python3 extract_terms.py --national --workers 8  # 51 jurisdictions, ~3 h

UNIT OF ANALYSIS is the (term, decision) pair. A decision that fights over
"occurrence" and "arising out of" contributes two rows, because a drafter cares
about the clause, not the case.

THE THREE NUMBERS, per term and per category:
  exposure    decisions in which the term was litigated at all
  found       the court held it ambiguous          -- the anti-pattern
  rejected    the court held it clear              -- the safe harbour
  risk        found / (found + rejected)

`found` and `rejected` are never pooled: a term that draws challenges and always
survives them is GOOD language carrying precedent, and a term that draws few
challenges and loses them is bad language nobody has got to yet. Exposure and
risk answer different drafting questions and are always reported together.

COURT SCOPE is state appellate only -- supreme and intermediate appellate, all
51 jurisdictions. Trial-court coverage in the bulk export is uneven by state
(New York has decades, most states have almost none), so including it would make
a state-to-state comparison an artefact of CourtListener's ingest rather than a
fact about the law.
"""
import argparse, json, os, sqlite3, sys, time
from collections import Counter
from multiprocessing import Pool

# Paths are configurable so a clone runs somewhere other than the machine that
# built it. CASELAW_HOME is the corpus pipeline (~/caselaw); US_LAW_DB is the
# statutes database, which sits on external storage here because it lives beside
# a 66 GB opinion corpus. A repository that hardcodes one laptop's paths is not
# reproducible, whatever its README claims.
CASELAW = os.environ.get("CASELAW_HOME", os.path.expanduser("~/caselaw"))
sys.path.insert(0, CASELAW)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import clcorpus as cc
from lib import terms as T
from lib import posture as P

AMB_QUERY = "(ambiguous OR ambiguity OR ambiguities)"
AMB_RX = P.re.compile(r"ambigu\w+", P.re.I)
COURTS_TSV = os.path.join(CASELAW, "courts-by-state.tsv")
# Sentences either side of an ambiguity holding that still count as "beside" it.
# Three is the width at which a quoted clause and the sentence ruling on it are
# still plainly the same passage; widening it further starts to sweep in the
# next issue in the opinion.
PROX = 3

_con = None


# --------------------------------------------------------------------------
def court_table():
    """court_id -> (jurisdiction, state). CourtListener codes: S state supreme,
    SA state appellate, ST state trial, F federal appellate."""
    out = {}
    with open(COURTS_TSV) as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                out[p[1]] = (p[2], p[0])
    return out


def _init(national):
    global _con
    _con, _ = cc.connect(scope="all" if national else "fl",
                         national=national, quiet=True)


def _one(job):
    """Extract every disputed term from one decision. Runs in a worker."""
    oid, cid, block_id, idx, court, state, filed = job
    try:
        text = cc.doc_text(_con, block_id, idx)
    except Exception:
        return ("err", oid, [])
    if not text:
        return ("notext", oid, [])

    sents, spans = T.sentence_spans(text)
    amb_idx = [i for i, s in enumerate(sents) if AMB_RX.search(s)]
    if not amb_idx:
        return ("noamb", oid, [])

    # Decision-level fallback posture, used only where nothing links the term to
    # a holding. Recorded as `inferred` so the weakest link stays visible.
    dec_post = [P.posture(sents[i]) for i in amb_idx]
    fallback = ("found" if "found" in dec_post else
                "rejected" if "rejected" in dec_post else
                "alleged" if "alleged" in dec_post else "uncertain")

    found = T.extract_terms(text)
    if not found:
        return ("noterm", oid, [])

    def resolve(ps):
        return ("found" if "found" in ps else
                "rejected" if "rejected" in ps else
                "alleged" if "alleged" in ps else "uncertain")

    rows = []
    year = int(filed[:4]) if filed and filed[:4].isdigit() else None
    for term, (window, pos) in found.items():
        # THREE TIERS OF EVIDENCE, kept apart rather than pooled.
        #   direct     an ambiguity sentence names the term -- the holding is
        #              about this language and nothing else has to be assumed
        #   proximate  the term is quoted within PROX sentences of an ambiguity
        #              sentence; courts routinely quote a clause and then hold
        #              on it without repeating the words
        #   inferred   neither; the decision's posture is carried over, which is
        #              the assumption the ambiguity-pools run made everywhere
        hits = [sents[i] for i in amb_idx if term in sents[i].lower()]
        if hits:
            post, link = resolve([P.posture(s) for s in hits]), "direct"
        else:
            si = next((k for k, (a, b) in enumerate(spans) if a <= pos < b),
                      None)
            near = ([i for i in amb_idx if abs(i - si) <= PROX]
                    if si is not None else [])
            if near:
                post = resolve([P.posture(sents[i]) for i in near])
                link = "proximate"
            else:
                post, link = fallback, "inferred"
        rows.append((term, T.category(term), T.source(window), post, link,
                     oid, cid, court, state, year))
    return ("ok", oid, rows)


# --------------------------------------------------------------------------
def build_jobs(national, scope, limit):
    """Resolve the hit ids to (decision, court, date) without random probes.

    ★ SCAN, DO NOT PROBE. The obvious version of this joins `hits` against
    opinions, cluster_court and cluster_meta and lets SQLite drive from the
    486k hit ids. Every one of those is a B-tree seek, and on the external
    platter a seek costs 14 ms -- so the join alone runs for about two hours
    before a single opinion has been decoded. Reading each table start to end
    and filtering in Python is a sequential read of a few hundred MB and
    finishes in under a minute. This is the whole difference between a
    three-hour run and a five-hour one.
    """
    con, info = cc.connect(scope="all" if national else scope, national=national)
    t0 = time.time()
    ids = set(cc.fts_ids(con, AMB_QUERY, warn_at=10_000_000))
    print(f"# fts hits: {len(ids):,} opinions  [{time.time()-t0:.1f}s]", file=sys.stderr)

    t0 = time.time()
    hits = []                                   # (oid, cid, block_id, idx)
    need = set()
    for oid, cid, block_id, idx in con.execute(
            "SELECT id, cluster_id, block_id, idx FROM opinions"):
        if oid in ids:
            hits.append((oid, cid, block_id, idx))
            if cid is not None:
                need.add(cid)
    print(f"# opinions scan: {len(hits):,} matched, {len(need):,} clusters "
          f"[{time.time()-t0:.1f}s]", file=sys.stderr)

    t0 = time.time()
    court_of = {}
    for cid, court in con.execute("SELECT cluster_id, court FROM cluster_court"):
        if cid in need:
            court_of[cid] = court
    print(f"# cluster_court scan: {len(court_of):,} [{time.time()-t0:.1f}s]",
          file=sys.stderr)

    date_of = {}
    if info["meta"]:
        t0 = time.time()
        for cid, d in con.execute("SELECT cluster_id, date_filed FROM m.cluster_meta"):
            if cid in need:
                date_of[cid] = d
        print(f"# cluster_meta scan: {len(date_of):,} [{time.time()-t0:.1f}s]",
              file=sys.stderr)

    # Scraped slips are a small table and have no cluster, so probing it is fine.
    inc = {}
    if info["incoming"]:
        t0 = time.time()
        for oid, court, d, b, i in con.execute(
                "SELECT id, court, date_filed, block_id, idx FROM incoming"):
            if oid in ids:
                inc[oid] = (court, d, b, i)
        print(f"# incoming scan: {len(inc):,} [{time.time()-t0:.1f}s]", file=sys.stderr)
    con.close()

    ct = court_table()
    jobs, seen, tier = [], set(), Counter()
    for oid, cid, block_id, idx in hits:
        court = court_of.get(cid) or ""
        filed = date_of.get(cid)
        if oid in inc:                          # a scraped slip overrides
            c2, d2, b2, i2 = inc[oid]
            court = court or (c2 or "")
            filed = filed or d2
            block_id = block_id if block_id is not None else b2
            idx = idx if idx is not None else i2
        jur, state = ct.get(court, ("?", "?"))
        tier[jur] += 1
        if jur not in ("S", "SA"):              # state appellate only
            continue
        if block_id is None:
            continue
        key = ("c", cid) if cid is not None else ("o", oid)
        if key in seen:                         # one row per decision
            continue
        seen.add(key)
        jobs.append((oid, cid, block_id, idx, court, state, filed))

    # Slips that never appeared in `opinions` at all.
    for oid, (court, d, b, i) in inc.items():
        if b is None:
            continue
        jur, state = ct.get(court or "", ("?", "?"))
        if jur not in ("S", "SA") or ("o", oid) in seen:
            continue
        seen.add(("o", oid))
        jobs.append((oid, None, b, i, court, state, d))

    print(f"# court tiers: {dict(tier.most_common(8))}", file=sys.stderr)
    print(f"# state-appellate decisions after dedupe: {len(jobs):,}", file=sys.stderr)
    return jobs[:limit] if limit else jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", default="fl")
    ap.add_argument("--national", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    out = a.out or os.path.join(
        here, "terms-national.db" if a.national else f"terms-{a.scope}.db")

    jobs = build_jobs(a.national, a.scope, a.limit)

    db = sqlite3.connect(out)
    db.executescript("""
        PRAGMA journal_mode=WAL;
        DROP TABLE IF EXISTS term_hits;
        CREATE TABLE term_hits(
            term TEXT, category TEXT, source TEXT, posture TEXT, link TEXT,
            oid INTEGER, cid INTEGER, court TEXT, state TEXT, year INTEGER);
    """)

    funnel = Counter()
    funnel["decisions_queued"] = len(jobs)
    t0, done = time.time(), 0
    with Pool(a.workers, initializer=_init, initargs=(a.national,)) as pool:
        buf = []
        for status, oid, rows in pool.imap_unordered(_one, jobs, chunksize=8):
            funnel[status] += 1
            done += 1
            buf.extend(rows)
            if len(buf) >= 5000:
                db.executemany("INSERT INTO term_hits VALUES (?,?,?,?,?,?,?,?,?,?)", buf)
                db.commit()
                buf.clear()
            if done % 5000 == 0:
                el = time.time() - t0
                print(f"#   {done:,}/{len(jobs):,}  {el/60:.1f}m  "
                      f"eta {(el/done*(len(jobs)-done))/60:.0f}m", file=sys.stderr, flush=True)
        if buf:
            db.executemany("INSERT INTO term_hits VALUES (?,?,?,?,?,?,?,?,?,?)", buf)
    db.commit()
    db.executescript("""
        CREATE INDEX ix_term ON term_hits(term);
        CREATE INDEX ix_cat  ON term_hits(category);
        CREATE INDEX ix_st   ON term_hits(state);
    """)

    n_rows = db.execute("SELECT COUNT(*) FROM term_hits").fetchone()[0]
    n_terms = db.execute("SELECT COUNT(DISTINCT term) FROM term_hits").fetchone()[0]
    meta = {
        "query": AMB_QUERY,
        "scope": "national state appellate (S+SA)" if a.national else a.scope,
        "corpus": "CourtListener bulk snapshot 2026-06-30",
        "workers": a.workers,
        "runtime_minutes": round((time.time() - t0) / 60, 1),
        "funnel": dict(funnel),
        "term_hits": n_rows,
        "distinct_terms": n_terms,
    }
    with open(out.replace(".db", "-run.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta, indent=1), file=sys.stderr)
    print(f"# wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
