#!/usr/bin/env python3
"""Distributions over the trustee-fee dataset, and the coding sample.

    python3 analyze.py                 # the tables
    python3 analyze.py --sample 100    # emit the decisions to be coded

WHAT IS REPORTED AND WHAT IS NOT. Everything here is a distribution over
deterministic fields: how the fee was set, which vocabulary the state uses, who
the trustee was, which UTC s.708 signals are present. None of it is an outcome.

`challenge_outcome` -- was the fee cut -- is not in this file and cannot be,
because a regex cannot read a disposition. `--sample` writes the spans out for
coding; the rates come after the coding and after Cohen's kappa, per
protocols/trustee-fees.md stage 5. Reporting a grant rate before that would be
the reformation-fl mistake, which this repository has already made once.
"""
import argparse, json, os, random, sqlite3, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "trustee-fees.db")

# Wilson, because a normal-approximation interval on a small cell is a lie.
def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*((p*(1-p)/n + z*z/(4*n*n)) ** 0.5) / d
    return (p, max(0.0, c-h), min(1.0, c+h))


def table(title, counter, total):
    print(f"\n{title}")
    print("-" * 58)
    for k, v in counter.most_common():
        p, lo, hi = wilson(v, total)
        print(f"  {str(k):28s} {v:>6,}  {100*p:>5.1f}%  ({100*lo:.0f}-{100*hi:.0f})")
    print(f"  {'total':28s} {total:>6,}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, help="write N decisions out for coding")
    a = ap.parse_args()
    if not os.path.exists(DB):
        sys.exit(f"no dataset at {DB}. Run build_dataset.py first.")

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM fees")]
    n = len(rows)
    print(f"# trustee-fee dataset: {n:,} decisions")
    if not n:
        return

    st = Counter(r["state"] for r in rows)
    print(f"# states: {len(st)}   top: {st.most_common(10)}")
    yrs = [r["date_filed"][:4] for r in rows if r["date_filed"]]
    if yrs:
        print(f"# years: {min(yrs)} to {max(yrs)}   (check both extremes before trusting them)")

    table("How the challenged fee was set", Counter(
        next((k for k in ("published_schedule","instrument","percentage","hourly","statutory")
              if r.get(f"basis_{k}") in (1,"1")), "unstated") for r in rows), n)

    table("Trustee form, by role slot", Counter(r["trustee_form"] for r in rows), n)

    table("Which word the state uses", Counter(r["vocabulary"] for r in rows), n)

    print("\nThe vocabulary split, per state -- commissions is a regional term")
    print("-" * 58)
    per = {}
    for r in rows:
        s = per.setdefault(r["state"], [0, 0])
        s[0] += 1
        s[1] += 1 if r["vocabulary"] == "commission" else 0
    for s, (tot, com) in sorted(per.items(), key=lambda kv: -kv[1][1])[:12]:
        print(f"  {s:6s} {com:>4,} of {tot:>4,}   {100*com/tot:>5.0f}% commissions")

    print("\nUTC s.708 signals present (a hint for a coder, not a coded value)")
    print("-" * 58)
    for k in ("delegated", "special_skills", "termination_fee", "cotrustees", "self_dealing"):
        v = sum(1 for r in rows if r.get(f"sig_{k}") in (1, "1"))
        p, lo, hi = wilson(v, n)
        print(f"  {k:28s} {v:>6,}  {100*p:>5.1f}%  ({100*lo:.0f}-{100*hi:.0f})")

    d = sum(1 for r in rows if r["dollar_amounts"])
    print(f"\nDecisions stating a dollar figure in a fee sentence: {d:,} of {n:,} "
          f"({100*d/n:.0f}%)")

    if a.sample:
        random.seed(20260902)
        pick = random.sample(rows, min(a.sample, n))
        out = os.path.join(HERE, f"coding-sample-{len(pick)}.json")
        json.dump([{k: r[k] for k in
                    ("oid","cluster_id","case_name","state","date_filed",
                     "trustee_form","trustee_entities","trustee_persons",
                     "vocabulary","dollar_amounts","n_fee_sentences","fee_sentences")}
                   for r in pick], open(out, "w"), indent=2)
        print(f"\n# wrote {out} -- {len(pick)} decisions for coding")
        print("# seed 20260902, recorded so the sample is reproducible")


if __name__ == "__main__":
    main()
