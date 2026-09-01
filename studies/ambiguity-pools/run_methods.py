#!/usr/bin/env python3
"""Run the corpus-linguistics method suite over the cleaned testamentary pool.

Every step is deterministic. No language model classifies, codes or extracts
anything here, so re-running reproduces the numbers exactly.

    python3 studies/ambiguity-pools/run_methods.py
"""
import collections
import json
import pathlib
import re
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(pathlib.Path.home() / "caselaw"))

import clcorpus as cc  # noqa: E402
from lib.pools import Pool, collocates, dispersion, keyness, ngrams, tokens  # noqa: E402

STATE = ("fladistctapp", "fla")
AMB = re.compile(r"\bambigu\w+", re.I)
STAT = re.compile(r"\b(statut\w+|legislat\w+|plain meaning|ordinance|§|section \d+\.\d+)\b", re.I)
CONT = re.compile(r"\b(contract\w*|polic(y|ies)|lease|indemnit\w+|insur\w+|agreement)\b", re.I)
TEST = re.compile(r"\b(will|testament\w*|codicil|trust\w*|devise\w*|bequest|residuary|testat\w+|beneficiar\w+)\b", re.I)

QUERIES = {
    "testamentary": ('(ambiguous OR ambiguity) AND ("last will" OR testament OR codicil '
                     'OR "trust instrument" OR devise OR bequest OR "residuary")'),
    "statutory": ('(ambiguous OR ambiguity) AND (statute OR statutory OR "legislative intent" '
                  'OR "plain meaning" OR "rules of statutory construction")'),
}


def classify(sent: str) -> str:
    te, st, co = bool(TEST.search(sent)), bool(STAT.search(sent)), bool(CONT.search(sent))
    if te and not (st or co):
        return "testamentary"
    if st and not te:
        return "statutory"
    if co and not te:
        return "contract"
    return "testamentary" if te else "unclear"


def amb_sentences(db, cluster_ids):
    """Ambiguity sentences per cluster, keeping the cluster id for dispersion."""
    out = []
    for cid in cluster_ids:
        try:
            txt = cc.cluster_text(db, cid)
        except Exception:
            continue
        for s in re.split(r"(?<=[.;])\s+", txt):
            if AMB.search(s):
                out.append((cid, s))
    return out


def main():
    db, info = cc.connect(scope="fl", quiet=True)
    t0 = time.time()

    pools = {n: Pool(n, q, courts=STATE).build(db) for n, q in QUERIES.items()}
    tgt_sents = amb_sentences(db, sorted(pools["testamentary"].cluster_ids))
    ref_sents = amb_sentences(db, sorted(pools["statutory"].cluster_ids
                                         - pools["testamentary"].cluster_ids)[:400])

    # Sentence-level screen. Document-level subtraction discards about half of a
    # small pool, because a will case routinely cites a statute in passing.
    kept_ids, kept_sents = set(), []
    per_case = collections.defaultdict(list)
    for cid, s in tgt_sents:
        per_case[cid].append((classify(s), s))
    for cid, rows in per_case.items():
        if any(lbl == "testamentary" for lbl, _ in rows):
            kept_ids.add(cid)
            kept_sents += [s for lbl, s in rows if lbl == "testamentary"]

    report = {
        "corpus": info["ops"],
        "snapshot": db.execute("SELECT v FROM meta WHERE k='source_snapshot'").fetchone()[0],
        "courts": list(STATE),
        "queries": QUERIES,
        "n_testamentary_docs": len(pools["testamentary"]),
        "n_statutory_docs": len(pools["statutory"]),
        "n_kept_docs": len(kept_ids),
        "n_target_sentences": len(kept_sents),
        "n_reference_sentences": len(ref_sents),
    }

    # --- keyness -----------------------------------------------------------
    tc, rc = collections.Counter(), collections.Counter()
    for s in kept_sents:
        tc.update(tokens(s))
    for _, s in ref_sents:
        rc.update(tokens(s))
    report["keyness"] = [
        {"term": t, "target": a, "reference": b, "g2": round(g, 1)}
        for t, a, b, g in keyness(tc, rc, min_count=8, top=25)
    ]

    # --- n-grams, with document frequency so one loud opinion cannot rank ---
    for n in (2, 3, 4):
        docs = collections.defaultdict(set)
        freq = collections.Counter()
        for cid, s in [(c, s) for c, rows in per_case.items()
                       for lbl, s in rows if lbl == "testamentary" for c in [c]]:
            for g in ngrams(tokens(s), n):
                freq[g] += 1
                docs[g].add(cid)
        disp = dispersion(docs, min_docs=3)
        rows = sorted(((" ".join(g), freq[g], d) for g, d in disp.items()),
                      key=lambda r: (-r[2], -r[1]))
        report[f"{n}grams"] = [{"ngram": g, "count": c, "docs": d} for g, c, d in rows[:20]]

    # --- collocation around the doctrinal nodes ----------------------------
    report["collocates"] = {
        node: [{"word": w, "joint": o, "expected": e, "mi": mi, "t": t_, "g2": g}
               for w, o, e, mi, t_, g in collocates(kept_sents, node, window=5,
                                                    min_count=4, top=15)]
        for node in ("latent", "extrinsic", "testator")
    }

    report["elapsed_seconds"] = round(time.time() - t0, 1)
    out = pathlib.Path(__file__).parent / "results.json"
    out.write_text(json.dumps(report, indent=2) + "\n")

    print(f"corpus {info['ops']}  snapshot {report['snapshot']}")
    print(f"docs: testamentary {report['n_testamentary_docs']}, "
          f"kept {report['n_kept_docs']}, target sentences {report['n_target_sentences']}")
    for n in (2, 3, 4):
        print(f"\n{n}-grams by document frequency:")
        for r in report[f"{n}grams"][:8]:
            print(f"   {r['docs']:>3} docs {r['count']:>4}x  {r['ngram']}")
    print(f"\ncollocates of 'latent' (G2):")
    for r in report["collocates"]["latent"][:8]:
        print(f"   {r['word']:16} joint={r['joint']:>3} MI={r['mi']:>6} t={r['t']:>5} G2={r['g2']}")
    print(f"\nwrote {out}  ({report['elapsed_seconds']}s)")


if __name__ == "__main__":
    main()
