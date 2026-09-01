#!/usr/bin/env python3
"""FL-Stale: a benchmark for statutory currency.

    python3 build_benchmark.py --n 600

WHY A BENCHMARK AND NOT JUST A DATASET. Datasets get downloaded; benchmarks get
RUN, and running one produces a citation in a model card or a paper. This one
targets a failure mode that is real, specific and expensive: language models
recite holdings whose governing statute has since changed, because the reports
they were trained on say nothing about the amendment. Florida is a good proving
ground because we hold both halves -- the opinions and 17 editions of the code.

WHY THE ANSWERS ARE DEFENSIBLE. Every item is a mechanical fact about the
statute book, checkable against a named source field:

    amended_since   has s. X been amended after YEAR?          history trail
    last_amended    what year was s. X last amended?           history trail
    text_changed    does the operative text of s. X differ      edition diff
                    between edition A and the current edition?

None of them asks for a legal conclusion, so there is no contestable answer key.
A benchmark whose ground truth is arguable is a benchmark nobody trusts.

WHY THE BINARY TASKS ARE BALANCED. An unbalanced yes/no set is gameable by
answering the majority class every time, and a model that does that looks
competent. Items are sampled to a 50/50 split and the constant-answer baseline
is printed with the benchmark, so any reported score has something honest to
beat.
"""
import argparse, json, os, random, re, sqlite3, sys, difflib
from collections import Counter

# Paths are configurable so a clone runs somewhere other than the machine that
# built it. CASELAW_HOME is the corpus pipeline (~/caselaw); US_LAW_DB is the
# statutes database, which sits on external storage here because it lives beside
# a 66 GB opinion corpus. A repository that hardcodes one laptop's paths is not
# reproducible, whatever its README claims.
CASELAW = os.environ.get("CASELAW_HOME", os.path.expanduser("~/caselaw"))
sys.path.insert(0, CASELAW)
import lawcorpus as L

LAW_DB = os.environ.get("US_LAW_DB",
                        "/Volumes/Elements/cl-data/us-law.db")
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
    return re.sub(r"\s+", " ", re.split(r"\n\s*History\.", t)[0]).strip()


def balanced(items, key, n, rng):
    """Even split across the values of `key`, so a constant answer scores 50%."""
    buckets = {}
    for it in items:
        buckets.setdefault(it[key], []).append(it)
    per = n // max(len(buckets), 1)
    out = []
    for v, group in buckets.items():
        rng.shuffle(group)
        out.extend(group[:per])
    rng.shuffle(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600, help="items per task")
    ap.add_argument("--seed", type=int, default=20260901)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out = a.out or os.path.join(here, "fl-stale-benchmark.jsonl")
    rng = random.Random(a.seed)

    con = sqlite3.connect(f"file:{LAW_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    secs = {}
    for r in con.execute("SELECT cite, edition, heading, history, block_id, idx "
                         "FROM sections WHERE corpus='flstat'"):
        d = secs.setdefault(r["cite"], {"years": set(), "editions": {},
                                        "heading": r["heading"]})
        if r["history"]:
            d["years"] |= hist_years(r["history"])
        try:
            t = L.section_text(con, r["block_id"], r["idx"])
        except Exception:
            t = None
        if t:
            d["editions"][int(r["edition"])] = norm(t)
    con.close()
    editions = sorted({e for d in secs.values() for e in d["editions"]})
    current = max(editions)
    print(f"# {len(secs):,} sections, editions {editions[0]}-{current}",
          file=sys.stderr)

    items, idn = [], 0

    # ---- task 1: amended_since -------------------------------------------
    pool = []
    for c, d in secs.items():
        if not d["years"]:
            continue
        for probe in (1995, 2005, 2012, 2018):
            after = sorted(y for y in d["years"] if y > probe)
            pool.append({"section": c, "probe": probe,
                         "answer": "yes" if after else "no",
                         "amendments_after": after})
    for it in balanced(pool, "answer", a.n, rng):
        idn += 1
        items.append({
            "id": f"fl-stale-{idn:05d}",
            "task": "amended_since",
            "question": (f"Has Florida Statutes section {it['section']} been "
                         f"amended at any time after {it['probe']}? "
                         f"Answer yes or no."),
            "answer": it["answer"],
            "answer_type": "boolean_yes_no",
            "context": {"section": it["section"], "since_year": it["probe"],
                        "amendment_years_after": it["amendments_after"]},
            "verification": {
                "source": "Florida Statutes history trail, sections.history",
                "url": f"https://www.flsenate.gov/Laws/Statutes/{current}/"
                       f"{it['section'].split('.')[0]}",
                "rule": "the history trail lists every session law amending the "
                        "section; years are parsed from its chapter cites"},
        })

    # ---- task 2: last_amended --------------------------------------------
    cands = [c for c, d in secs.items() if d["years"]]
    rng.shuffle(cands)
    for c in cands[:a.n]:
        idn += 1
        items.append({
            "id": f"fl-stale-{idn:05d}",
            "task": "last_amended",
            "question": (f"In what year was Florida Statutes section {c} most "
                         f"recently amended? Answer with a four-digit year."),
            "answer": str(max(secs[c]["years"])),
            "answer_type": "year",
            "context": {"section": c, "heading": secs[c]["heading"],
                        "all_amendment_years": sorted(secs[c]["years"])},
            "verification": {
                "source": "Florida Statutes history trail, sections.history",
                "url": f"https://www.flsenate.gov/Laws/Statutes/{current}/"
                       f"{c.split('.')[0]}",
                "rule": "maximum year appearing in the section's history trail"},
        })

    # ---- task 3: text_changed --------------------------------------------
    # Only where two editions are actually held. This is the task the versioned
    # backfill exists to make possible, and it is the one a model cannot answer
    # from the reports alone.
    # A section held in an older edition and absent from the current one was
    # repealed, renumbered or transferred. That is a HARDER staleness case than
    # a text change -- the authority a case rests on no longer exists at that
    # number -- so it is counted and reported rather than quietly dropped.
    pool, gone = [], []
    for c, d in secs.items():
        eds = sorted(d["editions"])
        if len(eds) < 2:
            continue
        base = eds[0]
        if base == current:
            continue
        if current not in d["editions"]:
            gone.append(c)
            continue
        sim = difflib.SequenceMatcher(None, d["editions"][base],
                                      d["editions"][current]).ratio()
        pool.append({"section": c, "base": base,
                     "answer": "yes" if sim < 0.995 else "no",
                     "similarity": round(sim, 4)})
    changed = sum(1 for p in pool if p["answer"] == "yes")
    print(f"# text_changed pool: {len(pool):,} sections, "
          f"{changed:,} changed between {min(editions)} and {current}; "
          f"{len(gone):,} present in {min(editions)} but gone by {current}",
          file=sys.stderr)
    for it in balanced(pool, "answer", a.n, rng):
        idn += 1
        items.append({
            "id": f"fl-stale-{idn:05d}",
            "task": "text_changed",
            "question": (f"Does the operative text of Florida Statutes section "
                         f"{it['section']} differ between the {it['base']} "
                         f"edition and the {current} edition? Answer yes or no."),
            "answer": it["answer"],
            "answer_type": "boolean_yes_no",
            "context": {"section": it["section"], "edition_a": it["base"],
                        "edition_b": current, "similarity": it["similarity"]},
            "verification": {
                "source": "diff of the two editions held in us-law.db",
                "url": f"https://www.flsenate.gov/Laws/Statutes/{it['base']}/"
                       f"{it['section'].split('.')[0]}",
                "rule": "SequenceMatcher ratio below 0.995 on the operative "
                        "text with the history trail stripped; the trail is "
                        "excluded because it changes at every amendment by "
                        "definition and would make the task circular"},
        })

    with open(out, "w") as fh:
        for it in items:
            fh.write(json.dumps(it) + "\n")

    by_task = Counter(i["task"] for i in items)
    baselines = {}
    for t in by_task:
        answers = [i["answer"] for i in items if i["task"] == t]
        top, cnt = Counter(answers).most_common(1)[0]
        baselines[t] = {"majority_answer": top,
                        "constant_baseline": round(cnt / len(answers), 3),
                        "n": len(answers)}
    meta = {"name": "FL-Stale", "version": "1.0",
            "editions_held": editions, "current_edition": current,
            "seed": a.seed, "items": len(items),
            "tasks": dict(by_task), "baselines": baselines,
            "sections_repealed_or_renumbered_since_oldest_edition": len(gone),
            "license": "CC BY 4.0"}
    with open(out.replace(".jsonl", "-meta.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
