#!/usr/bin/env python3
"""Size every pool the trustee protocol depends on, reproducibly.

    python3 size_pools.py                 # Florida slice, fast
    python3 size_pools.py --national      # 51 jurisdictions, slow
    python3 size_pools.py --national --json out.json

WHY THIS FILE EXISTS. The pool tables in `NEXT-PROJECTS.md` and in
`protocols/trustee-litigation.md` were produced by ad-hoc queries in a session
that committed only the markdown. Under this repository's own reporting rules a
table without its runnable query is not a finding, so the numbers stand as
provisional until this script reproduces them. Run it before citing them.

WHAT IT MEASURES, IN THREE GROUPS.

  labels        the phrases the original design proposed to filter on --
                "professional trustee" and friends. The sizing pass found zero
                of the first in Florida. This re-derives that.
  population    the retrieval pool the study actually runs on: a fiduciary
                claim co-occurring with a trustee.
  contaminants  the offices that share the word "trustee" and are not fiduciaries
                of anybody's family. Exclusion 2 in the protocol -- the
                deed-of-trust foreclosure trustee -- is the big one, and it is
                the one the Florida-shaped sizing pass missed, because Florida
                is a judicial-foreclosure state and does not have it.

The contaminant group is reported PER STATE, because its size is a function of
whether the state forecloses by deed of trust. A single national total would
hide exactly the variation that decides how much of the pool survives.

Set intersections are computed on the id sets rather than as new FTS queries.
`A AND B` in FTS5 and `set(A) & set(B)` agree here and the second costs nothing.
"""
import argparse, json, os, sys, time
from collections import Counter, defaultdict

CASELAW = os.environ.get("CASELAW_HOME", os.path.expanduser("~/caselaw"))
sys.path.insert(0, CASELAW)
import clcorpus as cc

COURTS_TSV = os.path.join(CASELAW, "courts-by-state.tsv")

# ---------------------------------------------------------------------------
# The pools. Each is an FTS5 expression, run verbatim, and printed with its
# count so a reader can re-derive any row of any table in the protocol.
#
# NEVER write NEAR("breach fiduciary duty", 25). FTS5 reads a quoted run of
# words as a single PHRASE, so that expression looks for the three words
# adjacent and returned 16 Florida decisions for the most litigated claim in
# American law. Quote each phrase separately or use plain AND.
# ---------------------------------------------------------------------------
POOLS = {
    # -- labels the original design would have filtered on -------------------
    "bfd":                   '"breach of fiduciary duty"',
    "professional_trustee":  '"professional trustee"',
    "corporate_trustee":     '"corporate trustee"',
    "individual_trustee":    '"individual trustee"',
    "independent_trustee":   '"independent trustee"',
    "institutional_trustee": '"institutional trustee"',

    # -- the retrieval pool the study runs on --------------------------------
    # Broad on purpose. Recall lives in the query, precision lives in the
    # filter, and a narrow query leaves no funnel entry to show what was lost.
    "fiduciary_claim": ('"breach of fiduciary duty" OR "breached his fiduciary" '
                        'OR "breached her fiduciary" OR "breached its fiduciary" '
                        'OR "fiduciary duties" OR surcharge OR "self-dealing" '
                        'OR "duty of loyalty" OR "duty of impartiality" '
                        'OR "prudent investor"'),
    "trustee":         'trustee OR trustees OR "successor trustee" OR "co-trustee"',

    # -- contaminants, exclusions 2 to 6 in the protocol ----------------------
    "deed_of_trust":   ('"deed of trust" OR "substitute trustee" OR "trustee\'s sale" '
                        'OR "trustee\'s deed" OR "non-judicial foreclosure" '
                        'OR "nonjudicial foreclosure" OR "power of sale"'),
    "securitisation":  ('"mortgage-backed" OR "mortgage backed" OR "pooling and '
                        'servicing" OR "certificateholders" OR "indenture trustee" '
                        'OR "as trustee for the certificate" OR "asset-backed"'),
    "constructive":    '"constructive trust" OR "constructive trustee" OR "resulting trust"',
    "erisa":           ('ERISA OR "Employee Retirement Income Security" '
                        'OR "pension fund" OR "welfare benefit plan" OR "plan trustees"'),
    "business_trust":  ('"voting trust" OR "liquidating trust" OR "business trust" '
                        'OR "Massachusetts trust" OR "land trust"'),

    # -- the standard the protocol's primary question turns on ---------------
    # UTC s.806 / Fla. s.736.0806. Sizing this decides whether the primary
    # question has a pool at all; if it is tiny, the study is a different study.
    "special_skills":  ('"special skills" OR "special expertise" OR "greater degree '
                        'of skill" OR "higher standard of care" OR "held himself out" '
                        'OR "held itself out" OR "held herself out"'),
    "exculpation":     ('"exculpatory clause" OR "exculpatory provision" '
                        'OR "exculpate" OR "exoneration clause" OR "relieve the trustee"'),
}

# Reported as `name = A & B`, computed on the id sets.
CROSSES = [
    ("bfd_x_trustee",              "fiduciary_claim", "trustee"),
    ("bfd_x_corporate_trustee",    "bfd",             "corporate_trustee"),
    ("bfd_x_professional_trustee", "bfd",             "professional_trustee"),
    ("pool_x_deed_of_trust",       "bfd_x_trustee",   "deed_of_trust"),
    ("pool_x_securitisation",      "bfd_x_trustee",   "securitisation"),
    ("pool_x_constructive",        "bfd_x_trustee",   "constructive"),
    ("pool_x_erisa",               "bfd_x_trustee",   "erisa"),
    ("pool_x_business_trust",      "bfd_x_trustee",   "business_trust"),
    ("pool_x_special_skills",      "bfd_x_trustee",   "special_skills"),
    ("pool_x_exculpation",         "bfd_x_trustee",   "exculpation"),
]


def court_table():
    """court_id -> (jurisdiction, state). S state supreme, SA state appellate."""
    out = {}
    with open(COURTS_TSV) as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 5:
                out[p[1]] = (p[2], p[0])
    return out


def resolve(con, info, allids):
    """oid -> (decision_key, state), state-appellate only.

    One pass over `opinions` for every pool at once, filtered to the union of
    the hit sets. Scanning it once per pool would be fifteen full-table scans.

    ★ Both corpora share one FTS index. A hit resolved only against `opinions`
    silently drops every case decided since the last bulk snapshot, so
    `incoming` is scanned too and a scraped slip overrides.
    """
    ct = court_table()
    need, cid_of = set(), {}
    t0 = time.time()
    for oid, cid in con.execute("SELECT id, cluster_id FROM opinions"):
        if oid in allids:
            cid_of[oid] = cid
            if cid is not None:
                need.add(cid)
    print(f"# opinions scan: {len(cid_of):,} matched  [{time.time()-t0:.1f}s]",
          file=sys.stderr)

    t0 = time.time()
    court_of = {}
    for cid, court in con.execute("SELECT cluster_id, court FROM cluster_court"):
        if cid in need:
            court_of[cid] = court
    print(f"# cluster_court scan: {len(court_of):,}  [{time.time()-t0:.1f}s]",
          file=sys.stderr)

    inc = {}
    if info["incoming"]:
        for oid, court in con.execute("SELECT id, court FROM incoming"):
            if oid in allids:
                inc[oid] = court

    out, tier = {}, Counter()
    for oid in allids:
        cid = cid_of.get(oid)
        court = court_of.get(cid) or inc.get(oid) or ""
        jur, state = ct.get(court, ("?", "?"))
        tier[jur] += 1
        if jur not in ("S", "SA"):
            continue
        out[oid] = (("c", cid) if cid is not None else ("o", oid), state)
    print(f"# court tiers: {dict(tier.most_common(8))}", file=sys.stderr)
    print(f"# state-appellate opinions in the union: {len(out):,}", file=sys.stderr)
    return out


def tally(ids, resolved):
    """One row per DECISION, not per opinion -- a cluster's concurrence and
    dissent are one decision and counting both doubles the pool."""
    decs, states = set(), set()
    per_state = Counter()
    for oid in ids:
        r = resolved.get(oid)
        if not r:
            continue
        key, state = r
        if key not in decs:
            decs.add(key)
            states.add(state)
            per_state[state] += 1
    return {"decisions": len(decs), "states": len(states),
            "per_state": dict(per_state.most_common())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--national", action="store_true",
                    help="51 jurisdictions. Slow: size on the FL slice first.")
    ap.add_argument("--json", help="write the full result, per-state included")
    a = ap.parse_args()

    con, info = cc.connect(scope="all" if a.national else "fl",
                           national=a.national)

    raw = {}
    for name, q in POOLS.items():
        t0 = time.time()
        raw[name] = set(cc.fts_ids(con, q, warn_at=10_000_000))
        print(f"# {name:24s} {len(raw[name]):>9,} raw  [{time.time()-t0:.1f}s]",
              file=sys.stderr)

    allids = set().union(*raw.values())
    resolved = resolve(con, info, allids)
    con.close()

    for name, l, r in CROSSES:
        raw[name] = raw[l] & raw[r]

    result = {name: tally(ids, resolved) for name, ids in raw.items()}

    print(f"\n{'pool':28s} {'decisions':>10s} {'states':>7s}")
    print("-" * 47)
    for name in list(POOLS) + [c[0] for c in CROSSES]:
        r = result[name]
        print(f"{name:28s} {r['decisions']:>10,} {r['states']:>7d}")

    # The contaminants are reported per state because their size is a function
    # of foreclosure procedure, not of trust law.
    print(f"\ndeed-of-trust contamination of the study pool, top 12 states")
    print("-" * 47)
    pool = result["bfd_x_trustee"]["per_state"]
    dot = result["pool_x_deed_of_trust"]["per_state"]
    rows = sorted(dot.items(), key=lambda kv: -kv[1])[:12]
    for st, n in rows:
        base = pool.get(st, 0)
        share = f"{100*n/base:.0f}%" if base else "--"
        print(f"{st:28s} {n:>10,} {share:>7s} of {base:,}")

    if a.json:
        with open(a.json, "w") as f:
            json.dump({"queries": POOLS, "crosses": CROSSES,
                       "national": a.national, "result": result}, f, indent=2)
        print(f"\n# wrote {a.json}", file=sys.stderr)


if __name__ == "__main__":
    main()
