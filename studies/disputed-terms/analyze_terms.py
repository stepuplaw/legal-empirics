#!/usr/bin/env python3
"""Rank disputed terms and term categories, and write the report tables.

    python3 analyze_terms.py --db terms-national.db --out .

THREE NUMBERS, NEVER ONE.
  exposure    decisions in which the term was litigated
  risk        found / (found + rejected) -- how often the challenge succeeds
  dispersion  how many states it has been litigated in

Exposure without risk says a term is popular. Risk without exposure says a rare
term lost once. Dispersion separates a general defect in drafted language from
one state's quirk, and it is the number the single-state study could not
produce at all.

WILSON, NOT WALD. Risk is a proportion on small counts -- some terms have four
classified decisions -- and the textbook normal interval gives impossible bounds
below 0 and above 1 there. The Wilson score interval stays inside [0,1] and is
the reason a term with 3/4 is not reported as though it were 300/400.

LINKED, NOT INFERRED, IS THE DEFENSIBLE NUMBER. A term is `direct` when an
ambiguity sentence names it and `proximate` when it is quoted within three
sentences of one; either way the holding and the language are the same passage.
It is `inferred` when the decision's posture is merely carried over, which is
the assumption the earlier ambiguity-pools run made everywhere and the reason
its instrument-language result was null. Headline numbers use direct +
proximate; the inferred rows are counted and reported but never pooled in.
"""
import argparse, json, math, os, sqlite3, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from lib import terms as T


def wilson(k, n, z=1.96):
    """Score interval for a proportion. Returns (lo, hi), or (0,1) at n=0."""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - m), min(1.0, c + m)


def stats(rows):
    """(exposure, found, rejected, risk, lo, hi, states) for a set of rows."""
    exposure = len(rows)
    found = sum(1 for r in rows if r["posture"] == "found")
    rej = sum(1 for r in rows if r["posture"] == "rejected")
    n = found + rej
    risk = found / n if n else None
    lo, hi = wilson(found, n)
    states = len({r["state"] for r in rows})
    return exposure, found, rej, risk, lo, hi, states


def fmt_risk(risk, lo, hi, n):
    if risk is None:
        return "—"
    return f"{risk:.0%} ({lo:.0%}–{hi:.0%}, n={n})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="terms-national.db")
    ap.add_argument("--out", default=".")
    ap.add_argument("--min-exposure", type=int, default=8,
                    help="minimum decisions for a term to appear in the ranked tables")
    a = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    db_path = a.db if os.path.isabs(a.db) else os.path.join(here, a.db)
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    all_rows = db.execute("SELECT * FROM term_hits").fetchall()
    direct = [r for r in all_rows if r["link"] in ("direct", "proximate")]
    link_counts = Counter(r["link"] for r in all_rows)

    run_meta = {}
    mp = db_path.replace(".db", "-run.json")
    if os.path.exists(mp):
        run_meta = json.load(open(mp))

    by_term_d = defaultdict(list)
    by_cat_d = defaultdict(list)
    by_term_all = defaultdict(list)
    by_cat_all = defaultdict(list)
    by_src_d = defaultdict(list)
    for r in direct:
        by_term_d[r["term"]].append(r)
        by_cat_d[r["category"]].append(r)
        by_src_d[r["source"]].append(r)
    for r in all_rows:
        by_term_all[r["term"]].append(r)
        by_cat_all[r["category"]].append(r)

    out = {"db": os.path.basename(db_path), "run": run_meta,
           "n_term_hits": len(all_rows), "n_linked": len(direct),
           "links": dict(link_counts),
           "n_distinct_terms": len(by_term_all)}

    lines = []
    W = lines.append

    W("## Term categories, ranked by risk\n")
    W(f"Linked rows only — {link_counts['direct']:,} where an ambiguity sentence")
    W(f"names the term and {link_counts['proximate']:,} where it is quoted within")
    W(f"three sentences of one. The remaining {link_counts['inferred']:,} rows carry")
    W("the decision's posture without any link to the specific words, and are")
    W("excluded here. Risk is the share of resolved challenges the language")
    W("*lost*. Wilson 95% interval in brackets.\n")
    W("| Category | Terms | Exposure | Found ambiguous | Upheld | Risk |")
    W("|---|---:|---:|---:|---:|---|")
    cat_rows = []
    for cat, rows in by_cat_d.items():
        e, f, rj, risk, lo, hi, st = stats(rows)
        cat_rows.append((cat, len({r["term"] for r in rows}), e, f, rj, risk, lo, hi))
    cat_rows.sort(key=lambda x: (x[5] is None, -(x[5] or 0)))
    for cat, nt, e, f, rj, risk, lo, hi in cat_rows:
        W(f"| {'**' + cat + '**' if cat != 'uncategorised' else cat} | {nt:,} | "
          f"{e:,} | {f:,} | {rj:,} | {fmt_risk(risk, lo, hi, f + rj)} |")
    out["categories"] = [
        {"category": c, "terms": nt, "exposure": e, "found": f, "rejected": rj,
         "risk": risk, "ci": [lo, hi]}
        for c, nt, e, f, rj, risk, lo, hi in cat_rows]

    W("\n## The most litigated terms\n")
    W(f"Every term with at least {a.min_exposure} linked decisions, ranked by")
    W("exposure. `States` is the dispersion: how many jurisdictions have fought")
    W("over the same word. Dispersion is what separates a general defect in")
    W("drafted language from one state's local quirk, and it is the number a")
    W("single-state study cannot produce at all.\n")
    W("| Term | Category | Source | Exposure | Found | Upheld | Risk | States |")
    W("|---|---|---|---:|---:|---:|---|---:|")
    term_rows = []
    for term, rows in by_term_d.items():
        e, f, rj, risk, lo, hi, st = stats(rows)
        if e < a.min_exposure:
            continue
        src = Counter(r["source"] for r in rows).most_common(1)[0][0]
        term_rows.append((term, rows[0]["category"], src, e, f, rj, risk, lo, hi, st))
    term_rows.sort(key=lambda x: -x[3])
    for t, c, s, e, f, rj, risk, lo, hi, st in term_rows[:60]:
        W(f"| `{t}` | {c} | {s} | {e:,} | {f:,} | {rj:,} | "
          f"{fmt_risk(risk, lo, hi, f + rj)} | {st} |")
    out["top_terms"] = [
        {"term": t, "category": c, "source": s, "exposure": e, "found": f,
         "rejected": rj, "risk": risk, "ci": [lo, hi], "states": st}
        for t, c, s, e, f, rj, risk, lo, hi, st in term_rows]

    W("\n## The worst language: highest risk at meaningful exposure\n")
    W("Terms whose challenges succeed most often. A high number here means the")
    W("language, once fought over, usually fails.\n")
    W("| Term | Category | Exposure | Risk | States |")
    W("|---|---|---:|---|---:|")
    risky = [r for r in term_rows if (r[4] + r[5]) >= 5 and r[6] is not None]
    risky.sort(key=lambda x: -x[6])
    for t, c, s, e, f, rj, risk, lo, hi, st in risky[:30]:
        W(f"| `{t}` | {c} | {e:,} | {fmt_risk(risk, lo, hi, f + rj)} | {st} |")

    W("\n## Safe harbours: language that draws challenges and survives them\n")
    W("Low risk at high exposure is the most useful cell in the study. It means")
    W("the formulation has been attacked repeatedly and upheld, so it carries")
    W("precedent that it is clear — which is a stronger reason to use it than")
    W("never having been litigated at all.\n")
    W("| Term | Category | Exposure | Risk | States |")
    W("|---|---|---:|---|---:|")
    safe = sorted(risky, key=lambda x: x[6])
    for t, c, s, e, f, rj, risk, lo, hi, st in safe[:30]:
        W(f"| `{t}` | {c} | {e:,} | {fmt_risk(risk, lo, hi, f + rj)} | {st} |")

    W("\n## Where the disputed words sit\n")
    W("| Instrument | Exposure | Found | Upheld | Risk |")
    W("|---|---:|---:|---:|---|")
    src_rows = []
    for src, rows in by_src_d.items():
        e, f, rj, risk, lo, hi, st = stats(rows)
        src_rows.append((src, e, f, rj, risk, lo, hi))
    src_rows.sort(key=lambda x: -x[1])
    for src, e, f, rj, risk, lo, hi in src_rows:
        W(f"| {src} | {e:,} | {f:,} | {rj:,} | {fmt_risk(risk, lo, hi, f + rj)} |")
    out["sources"] = [{"source": s, "exposure": e, "found": f, "rejected": rj,
                       "risk": risk} for s, e, f, rj, risk, lo, hi in src_rows]

    with open(os.path.join(a.out, "TABLES.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")

    # ---------------------------------------------------------------- appendix
    app = ["# Appendix — every disputed term",
           "",
           f"All {len(by_term_all):,} distinct terms extracted from "
           f"{run_meta.get('funnel', {}).get('ok', 0):,} decisions, with their",
           "counts. `found` and `rejected` are decisions in which the court held the",
           "language ambiguous or clear; `all` counts every decision the term was",
           "litigated in, including those whose posture could not be classified.",
           "",
           "Terms are listed in descending order of exposure, then alphabetically.",
           "A term appearing once is not evidence of anything on its own; it is",
           "listed because the tail is 52% of the data and hiding it would",
           "misrepresent the shape of the corpus.",
           "",
           "| Term | Category | Source | All | Found | Upheld | States |",
           "|---|---|---|---:|---:|---:|---:|"]
    rows_app = []
    for term, rows in by_term_all.items():
        e, f, rj, risk, lo, hi, st = stats(rows)
        src = Counter(r["source"] for r in rows).most_common(1)[0][0]
        rows_app.append((term, rows[0]["category"], src, e, f, rj, st))
    rows_app.sort(key=lambda x: (-x[3], x[0]))
    for term, cat, src, e, f, rj, st in rows_app:
        app.append(f"| `{term}` | {cat} | {src} | {e} | {f} | {rj} | {st} |")
    with open(os.path.join(a.out, "APPENDIX-TERMS.md"), "w") as fh:
        fh.write("\n".join(app) + "\n")

    out["appendix_rows"] = len(rows_app)
    with open(os.path.join(a.out, "results.json"), "w") as fh:
        json.dump(out, fh, indent=1)

    print("\n".join(lines[:60]))
    print(f"\n# wrote TABLES.md, APPENDIX-TERMS.md ({len(rows_app):,} terms), "
          f"results.json", file=sys.stderr)


if __name__ == "__main__":
    main()
