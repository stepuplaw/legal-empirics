#!/usr/bin/env python3
"""Trustee compensation challenges: retrieval, the exclusion funnel, and the
sentences a coder needs.

    python3 build_dataset.py                      # Florida slice, validates the code
    python3 build_dataset.py --national --workers 8

WHAT THIS DOES AND DOES NOT DO. Retrieval, the funnel and span extraction are
deterministic and reproducible, and that is all this file does. It does NOT
decide whether a fee was cut. On a Florida sample only 23% of decisions put an
outcome verb in the same sentence as the fee and 11% put a dollar figure there,
so a regex would be guessing. `challenge_outcome` is coded by a model reading
the spans this script extracts, with a human second coder on a random 100 and
Cohen's kappa reported, per `protocols/trustee-fees.md` stage 5.

THE FUNNEL IS THE STUDY. "Trustee" names at least seven offices and only one of
them is a fiduciary of somebody's family. Every exclusion is applied in the
protocol's order, and every one reports its count -- including the ones that make
the pool look small.
"""
import argparse, json, os, re, sqlite3, sys, time
from collections import Counter
from multiprocessing import Pool

CASELAW = os.environ.get("CASELAW_HOME", os.path.expanduser("~/caselaw"))
sys.path.insert(0, CASELAW)
import clcorpus as cc

COURTS_TSV = os.path.join(CASELAW, "courts-by-state.tsv")
OUT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trustee-fees.db")

# ---------------------------------------------------------------------------
# Stage 3. Both vocabularies. Eastern states say commissions (NY SCPA 2309),
# most others say fees, and a lane built on one word measures a region.
# ---------------------------------------------------------------------------
QUERY = ('"trustee\'s compensation" OR "trustees\' compensation" OR "trustee compensation" '
         'OR "trustee\'s fee" OR "trustee\'s fees" OR "trustees\' fees" OR "trustee fees" '
         'OR "trustee\'s commission" OR "trustee\'s commissions" '
         'OR "trustees\' commissions" OR "trustee commissions"')

# ★ Apostrophes are CURLY in this corpus and whitespace is not always one space.
# A straight-quote regex with a literal space silently dropped 9 of 25 Florida
# decisions that the FTS query had matched -- the same failure the statutory
# definitions extraction hit, recorded in METHODOLOGY.md section 9. The FTS index
# normalises punctuation; the raw text does not.
APOS = r"['’ʼ]"
FEE_RX = re.compile(
    rf"trustee(?:{APOS}s|s{APOS}|s)?\s+(?:compensation|fee|fees|commission|commissions)",
    re.I)

# ---------------------------------------------------------------------------
# Stage 4. Exclusions, IN ORDER. Each is a rule with a count.
# ---------------------------------------------------------------------------
EXCLUSIONS = [
 ("attorney_fees_only", re.compile(
     r"attorney'?s?'? fees?|counsel fees?|legal fees?", re.I), "fee-shifting is a different doctrine"),
 ("surplus_trustee", re.compile(
     r"surplus trustee|surplus (?:funds|proceeds)|foreclosure surplus", re.I),
     "a statutory disbursement fee, not fiduciary compensation"),
 ("indenture_bond", re.compile(
     r"indenture trustee|bondholder|certificateholder|pooling and servicing"
     r"|mortgage-backed|debenture", re.I), "a payment-waterfall contract term"),
 ("governing_board", re.compile(
     r"board of trustees|trustees of the internal improvement|board of regents"
     r"|board of governors", re.I), "a university board is not anybody's fiduciary"),
 ("eminent_domain", re.compile(
     r"eminent domain|condemnation|severance damages|taking of the propert", re.I),
     "'the trustees' there are property owners"),
 ("sale_commission", re.compile(
     r"real estate (?:broker|commission)|sales? commission|per cent of the sales price"
     r"|percent of the sales price", re.I), "a brokerage commission styled a trustee's fee"),
 ("erisa_pension_bk", re.compile(
     r"\bERISA\b|Employee Retirement Income Security|pension (?:plan|fund)"
     r"|bankruptcy trustee|trustee in bankruptcy|chapter (?:7|11|13) trustee", re.I),
     "different regimes"),
]
# Exclusion 2 only fires when the trustee's OWN compensation is not also at issue.
OWN_COMP = re.compile(
    rf"trustee(?:{APOS}s|s{APOS}|s)?\s+(?:compensation|commission|commissions)"
    r"|compensation (?:of|to|for) the trustee"
    r"|fee(?:s)? (?:of|to|for|paid to|charged by) the trustee"
    rf"|trustee(?:{APOS}s|s{APOS}|s)?\s+fee(?:s)? (?:was|were|is|are|of|in)", re.I)

# Adjudicated, rather than recited in the procedural history.
ADJUDICATED = re.compile(
    r"\b(reduc\w+|disallow\w+|surcharg\w+|forfeit\w+|reasonabl\w+|unreasonabl\w+"
    r"|excessive|affirm\w+|revers\w+|remand\w+|award\w+|approv\w+|vacat\w+"
    r"|abuse of discretion)\b", re.I)

# Stage 5 signals. Deterministic HINTS for a coder, never the coded value.
BASIS = {
 "published_schedule": re.compile(r"published fee schedule|fee schedule|standard schedule|rate schedule", re.I),
 "percentage":         re.compile(r"per ?cent\w*|percentage of (?:the )?(?:corpus|principal|trust|income|estate)|%", re.I),
 "hourly":             re.compile(r"hourly rate|per hour|hours (?:billed|expended|spent)|time records", re.I),
 "instrument":         re.compile(r"terms of the trust (?:provide|specif)|trust (?:instrument|deed|agreement) (?:provide|specif)"
                                  r"|as provided in the (?:trust|will)|the trust specifically provides"
                                  r"|(?:will|trust|deed) (?:provided|provides) that.{0,120}compensation"
                                  r"|pay to themselves such compensation", re.I|re.S),
 "statutory":          re.compile(r"statutory (?:fee|commission|rate)|by statute|section \d+\.\d+", re.I),
}
SIGNALS = {
 "delegated":        re.compile(r"delegat\w+|outside (?:manager|adviser|advisor)|investment (?:manager|adviser|advisor)|agent", re.I),
 "special_skills":   re.compile(r"special skills?|special expertise|special facilities|greater skill|expertise", re.I),
 "termination_fee":  re.compile(r"termination fee|fee (?:on|upon) termination", re.I),
 "cotrustees":       re.compile(r"co-?trustees?|two trustees|both trustees", re.I),
 "self_dealing":     re.compile(r"self-?dealing|without authoriz\w+|paid (?:her|him|it)self|took (?:fees|commissions) without", re.I),
}
DOLLAR = re.compile(r"\$[\d,]+(?:\.\d{2})?")
SENT = re.compile(r'(?<=[.!?])\s+')

# Trustee role slot -- who occupies it. Proximity does not work; see
# studies/trustee-litigation/CLASSIFIER-NOTES.md section 4.
NAME = r"[A-Z][\w.'&-]*(?:\s+(?:of|the|and|&|N\.A\.|Jr\.|Sr\.|III|II)|\s+[A-Z][\w.'&-]*){0,6}"
SLOTS = [re.compile(rf"({NAME}),?\s+(?:as\s+)?(?:the\s+)?(?:successor|co-?|former|substitute|sole)?\s*-?\s*[Tt]rustees?\b"),
         re.compile(rf"(?:the\s+)?[Tt]rustees?,\s+({NAME}),"),
         re.compile(rf"appointed\s+({NAME})\s+(?:as\s+)?(?:successor\s+)?[Tt]rustee")]
ENTITY = re.compile(r"\b(bank|banking|n\.?\s?a\.?|trust co|trust company|company|co\.|corp"
                    r"|corporation|inc\.?|l\.?l\.?c\.?|ass'?n|association|federal|national"
                    r"|savings|financial|holdings|group|&\s*co|f\.?s\.?b\.?)\b", re.I)
STOP = re.compile(r"^(the|a|an|this|that|his|her|its|their|such|said|no|any|court|trust|section"
                  r"|appellant|appellee|plaintiff|defendant|petitioner|respondent|we|he|she|it"
                  r"|they|there|when|where|because|although|however|under|upon|after|before|as|id)\b", re.I)

_con = None


def court_table():
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
    _con, _ = cc.connect(scope="all" if national else "fl", national=national, quiet=True)


def _one(job):
    """Funnel one decision and pull the spans a coder needs. Runs in a worker."""
    oid, cid, block_id, idx, court, state, filed, name = job
    try:
        text = _con and cc.doc_text(_con, block_id, idx)
    except Exception:
        return ("err", None)
    if not text or len(text) < 400:
        return ("notext", None)

    head = text[:6000]
    # Exclusions, in the protocol's order, first hit wins so the funnel is a
    # partition rather than overlapping sets.
    for tag, rx, _why in EXCLUSIONS:
        if not rx.search(text):
            continue
        if tag == "attorney_fees_only" and OWN_COMP.search(text):
            continue          # both are at issue -- keep it
        if tag in ("indenture_bond", "governing_board", "eminent_domain",
                   "sale_commission", "erisa_pension_bk", "surplus_trustee") \
           and not rx.search(head) and not rx.search(name or ""):
            continue          # a passing mention deep in the opinion is not the case
        return (tag, None)

    all_sents = SENT.split(text)
    hit = [i for i, x in enumerate(all_sents) if FEE_RX.search(x)]
    if not hit:
        return ("no_fee_sentence", None)
    sents = [all_sents[i] for i in hit]
    # ★ How a fee was SET is stated beside the fee sentence, not inside it.
    # Kay v. Bostwick (1922) quotes the trust deed authorising the trustees to
    # "pay to themselves such compensation ... as they may deem reasonable" in a
    # sentence that never contains the words "trustee's fee", so a basis test
    # scoped to fee sentences alone scored it unstated. Same two-sentence window
    # the disputed-terms study calls `proximate`.
    win = sorted({j for i in hit for j in range(max(0, i-2), min(len(all_sents), i+3))})
    near = " ".join(all_sents[j] for j in win)
    if not any(ADJUDICATED.search(x) for x in sents):
        return ("not_adjudicated", None)

    fillers = []
    for rx in SLOTS:
        for m in rx.finditer(text):
            f = " ".join(m.group(1).split()).strip(" ,.")
            if len(f) >= 4 and not STOP.match(f):
                fillers.append(f)
    ents = sorted({f for f in fillers if ENTITY.search(f)})
    pers = sorted({f for f in fillers if not ENTITY.search(f)})

    row = {
      "oid": oid, "cluster_id": cid, "court": court, "state": state,
      "date_filed": filed, "case_name": name,
      "trustee_form": ("both" if ents and pers else "entity" if ents else
                       "natural_person" if pers else "unclear"),
      "trustee_entities": "; ".join(ents[:5]),
      "trustee_persons": "; ".join(pers[:5]),
      "n_trustees_named": len(set(ents) | set(pers)),
      "fee_sentences": " ⏎ ".join(" ".join(s.split()) for s in sents[:8])[:4000],
      "n_fee_sentences": len(sents),
      "dollar_amounts": "; ".join(sorted(set(DOLLAR.findall(" ".join(sents))))[:8]),
      "vocabulary": ("commission" if re.search(r"commission", " ".join(sents), re.I)
                     else "fee_or_compensation"),
    }
    for k, rx in BASIS.items():
        # 2 = stated in the fee sentence itself, 1 = within two sentences, 0 = absent.
        # Tiers are kept apart rather than pooled, as everywhere else here.
        row[f"basis_{k}"] = (2 if any(rx.search(x) for x in sents)
                             else 1 if rx.search(near) else 0)
    for k, rx in SIGNALS.items():
        row[f"sig_{k}"] = 1 if rx.search(text) else 0
    return ("kept", row)


def jobs_for(national, limit):
    con, info = cc.connect(scope="all" if national else "fl", national=national)
    t0 = time.time()
    ids = set(cc.fts_ids(con, QUERY, warn_at=10_000_000))
    print(f"# fts hits: {len(ids):,} opinions  [{time.time()-t0:.0f}s]", file=sys.stderr)

    hits, need = [], set()
    for oid, cid, block_id, idx in con.execute(
            "SELECT id, cluster_id, block_id, idx FROM opinions"):
        if oid in ids:
            hits.append((oid, cid, block_id, idx))
            if cid is not None:
                need.add(cid)
    court_of = {cid: c for cid, c in con.execute(
        "SELECT cluster_id, court FROM cluster_court") if cid in need}
    meta = {}
    if info["meta"]:
        for cid, d, nm in con.execute(
                "SELECT cluster_id, date_filed, case_name FROM m.cluster_meta"):
            if cid in need:
                meta[cid] = (d, nm)
    inc = {}
    if info["incoming"]:
        for oid, c, d, nm, b, i in con.execute(
                "SELECT id, court, date_filed, case_name, block_id, idx FROM incoming"):
            if oid in ids:
                inc[oid] = (c, d, nm, b, i)
    con.close()

    ct, out, seen, tier = court_table(), [], set(), Counter()
    for oid, cid, block_id, idx in hits:
        court = court_of.get(cid) or ""
        d, nm = meta.get(cid, (None, None))
        if oid in inc:
            c2, d2, nm2, b2, i2 = inc[oid]
            court = court or (c2 or ""); d = d or d2; nm = nm or nm2
            block_id = block_id if block_id is not None else b2
            idx = idx if idx is not None else i2
        jur, state = ct.get(court, ("?", "?"))
        tier[jur] += 1
        if jur not in ("S", "SA") or block_id is None:
            continue
        key = ("c", cid) if cid is not None else ("o", oid)
        if key in seen:
            continue
        # ★ The same decision can appear under two cluster ids with different
        # capitalisation of the caption -- Horgan v. Cosden did, and counting it
        # twice inflates every rate. Collapse on court + date + normalised name.
        nkey = (court, d or "", re.sub(r"[^a-z0-9]", "", (nm or "").lower())[:60])
        if nkey[2] and nkey in seen:
            continue
        seen.add(key); seen.add(nkey)
        out.append((oid, cid, block_id, idx, court, state, d, nm))
    for oid, (c, d, nm, b, i) in inc.items():
        if b is None:
            continue
        jur, state = ct.get(c or "", ("?", "?"))
        if jur not in ("S", "SA") or ("o", oid) in seen:
            continue
        seen.add(("o", oid)); out.append((oid, None, b, i, c, state, d, nm))
    print(f"# court tiers: {dict(tier.most_common(6))}", file=sys.stderr)
    print(f"# state-appellate decisions after dedupe: {len(out):,}", file=sys.stderr)
    return (out[:limit] if limit else out), len(ids), tier


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--national", action="store_true")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    jobs, raw_hits, tier = jobs_for(a.national, a.limit)
    t0 = time.time()
    if a.workers > 1:
        with Pool(a.workers, initializer=_init, initargs=(a.national,)) as p:
            results = p.map(_one, jobs, chunksize=16)
    else:
        _init(a.national)
        results = [_one(j) for j in jobs]

    funnel, rows = Counter(), []
    for tag, row in results:
        funnel[tag] += 1
        if row:
            rows.append(row)
    print(f"# coded {len(rows):,} of {len(jobs):,}  [{time.time()-t0:.0f}s]", file=sys.stderr)

    if os.path.exists(OUT_DB):
        os.remove(OUT_DB)
    db = sqlite3.connect(OUT_DB)
    if rows:
        cols = list(rows[0].keys())
        db.execute(f"CREATE TABLE fees({','.join(c+' TEXT' for c in cols)})")
        db.executemany(f"INSERT INTO fees VALUES ({','.join('?'*len(cols))})",
                       [[r[c] for c in cols] for r in rows])
        db.commit()

    # THE FUNNEL, in the protocol's order, with counts.
    order = ["attorney_fees_only", "surplus_trustee", "indenture_bond",
             "governing_board", "eminent_domain", "sale_commission",
             "erisa_pension_bk", "no_fee_sentence", "not_adjudicated",
             "notext", "err", "kept"]
    n = len(jobs)
    print(f"\n{'stage':22s} {'dropped':>8s} {'remaining':>10s}")
    print("-" * 44)
    print(f"{'retrieved (opinions)':22s} {'':>8s} {raw_hits:>10,}")
    print(f"{'state appellate':22s} {'':>8s} {n:>10,}")
    rem = n
    for k in order[:-3]:
        rem -= funnel[k]
        print(f"{k:22s} {funnel[k]:>8,} {rem:>10,}")
    print(f"{'KEPT':22s} {'':>8s} {funnel['kept']:>10,}")

    if rows:
        print(f"\ntrustee form: {Counter(r['trustee_form'] for r in rows).most_common()}")
        print(f"vocabulary:   {Counter(r['vocabulary'] for r in rows).most_common()}")
        st = Counter(r['state'] for r in rows)
        print(f"states: {len(st)}  top: {st.most_common(8)}")
        for k in BASIS:
            print(f"  basis_{k:20s} {sum(r['basis_'+k] for r in rows):>6,}")
        for k in SIGNALS:
            print(f"  sig_{k:21s} {sum(r['sig_'+k] for r in rows):>6,}")

    meta_out = {"query": QUERY, "national": a.national, "raw_opinion_hits": raw_hits,
                "state_appellate_decisions": n, "funnel": dict(funnel),
                "kept": len(rows), "built": time.strftime("%Y-%m-%dT%H:%M:%S")}
    with open(os.path.join(os.path.dirname(OUT_DB), "trustee-fees-run.json"), "w") as f:
        json.dump(meta_out, f, indent=2)
    print(f"\n# wrote {OUT_DB}", file=sys.stderr)


if __name__ == "__main__":
    main()
