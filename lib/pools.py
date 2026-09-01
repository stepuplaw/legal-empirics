#!/usr/bin/env python3
"""Contrastive pool construction over the case law corpus.

THE PROBLEM THIS SOLVES. "Ambiguity" is not one doctrine. Courts use the word
for statutory interpretation, for contract construction, and for construing
wills and trusts, and those are unrelated bodies of law that happen to share
vocabulary. A single query cannot separate them, so a study that runs one
returns mostly statutory interpretation and calls it estate law.

THE METHOD. Build several pools from the same corpus, one per doctrine, then
use each pool as a NEGATIVE (contrast) set for the others. Terms that are
strongly overrepresented in the statutory pool relative to the testamentary pool
are statutory markers, and they can be fed back into the query as exclusions.
Iterate until the pools stop moving.

This is not a new technique. It is three known ones composed:
  * contrastive / reference corpus analysis, from corpus linguistics, where a
    term's KEYNESS is its overrepresentation against a named reference corpus;
  * bootstrapping in the DIPRE / Snowball lineage, where seeds find patterns and
    patterns find better seeds;
  * relevance feedback from information retrieval, where results refine the
    query that produced them.

Naming it matters for reporting: each is separately criticisable, and a reader
who knows one of them knows what to attack.

    from lib.pools import Pool, keyness
"""
from __future__ import annotations

import math
import pathlib
import re
import sys
from collections import Counter
from dataclasses import dataclass, field

sys.path.insert(0, str(pathlib.Path.home() / "caselaw"))
import clcorpus as cc  # noqa: E402


@dataclass
class Pool:
    """One doctrinal slice of the corpus, with its provenance recorded.

    `query` is kept verbatim so a report can print exactly what produced the
    pool. Reproducibility here is not a nicety: the whole method is query
    refinement, so a pool without its query is uninterpretable.
    """

    name: str
    query: str
    scope: str = "fl"
    courts: tuple[str, ...] | None = None
    cluster_ids: set[int] = field(default_factory=set)
    note: str = ""

    def build(self, db) -> "Pool":
        ids = cc.fts_ids(db, self.query)
        if not ids:
            self.cluster_ids = set()
            return self
        q = ",".join("?" * len(ids))
        sql = (f"SELECT DISTINCT o.cluster_id FROM opinions o "
               f"JOIN cluster_court cc ON cc.cluster_id = o.cluster_id "
               f"WHERE o.id IN ({q})")
        args = list(ids)
        if self.courts:
            sql += f" AND cc.court IN ({','.join('?' * len(self.courts))})"
            args += list(self.courts)
        self.cluster_ids = {r[0] for r in db.execute(sql, args)}
        return self

    def __len__(self) -> int:
        return len(self.cluster_ids)

    def __and__(self, other: "Pool") -> set[int]:
        return self.cluster_ids & other.cluster_ids

    def __sub__(self, other: "Pool") -> set[int]:
        return self.cluster_ids - other.cluster_ids


def log_likelihood(a: int, b: int, c: int, d: int) -> float:
    """Dunning log-likelihood G2 for a term across two corpora.

    a, b = term frequency in target and reference.
    c, d = total tokens in target and reference.

    Preferred over raw ratio because it does not explode on rare terms, and over
    mutual information because MI over-rewards rarity. Sign is carried by the
    caller: G2 alone says "different", not "more".
    """
    if a == 0 or c == 0 or d == 0:
        return 0.0
    e1 = c * (a + b) / (c + d)
    e2 = d * (a + b) / (c + d)
    ll = 0.0
    if a > 0 and e1 > 0:
        ll += a * math.log(a / e1)
    if b > 0 and e2 > 0:
        ll += b * math.log(b / e2)
    return 2 * ll


_WORD = re.compile(r"[a-z][a-z'-]{2,}")
# Function words carry no doctrinal signal and would dominate any frequency
# table. This is a deliberately short list; a full stoplist would also remove
# words like "will" that are doctrinally meaningful here.
STOP = {
    "the", "and", "that", "for", "was", "with", "not", "this", "his", "her",
    "had", "which", "from", "are", "were", "has", "been", "would", "there",
    "said", "any", "all", "but", "its", "him", "she", "who", "may", "shall",
    "such", "under", "upon", "have", "does", "did", "will", "can", "could",
    "than", "then", "them", "they", "their", "our", "you", "your", "one", "two",
}


def tokens(text: str) -> list[str]:
    return [w for w in _WORD.findall(text.lower()) if w not in STOP]


def ngrams(toks: list[str], n: int) -> Counter:
    return Counter(tuple(toks[i:i + n]) for i in range(len(toks) - n + 1))


def keyness(target: Counter, reference: Counter, min_count: int = 5,
            top: int = 40) -> list[tuple[str, int, int, float]]:
    """Terms overrepresented in target vs reference, by log-likelihood.

    Returns (term, target_count, reference_count, G2), descending. Only terms
    that are MORE frequent in the target are returned; a two-sided list would
    mix "marker of A" with "marker of B" and read as noise.
    """
    ct, cr = sum(target.values()), sum(reference.values())
    out = []
    for term, a in target.items():
        if a < min_count:
            continue
        b = reference.get(term, 0)
        if (a / ct) <= (b / cr if cr else 0):
            continue
        out.append((term, a, b, log_likelihood(a, b, ct, cr)))
    out.sort(key=lambda r: -r[3])
    return out[:top]


# ---------------------------------------------------------------------------
# Collocation and dispersion.
#
# These are the remaining corpus-linguistics measures the studies use. They are
# separated from keyness because they answer different questions: keyness asks
# "which terms mark this corpus against another", collocation asks "which terms
# keep company with this one", dispersion asks "is this a pattern or one loud
# document".
# ---------------------------------------------------------------------------

def collocates(sentences, node: str, window: int = 5, min_count: int = 4,
               top: int = 30):
    """Words co-occurring with `node` within `window` tokens, ranked three ways.

    Returns (word, joint, expected, MI, t_score, G2). All three statistics are
    reported rather than one, because they disagree by design and the
    disagreement is informative:

      * MI over-rewards rarity, so it surfaces distinctive but infrequent pairs.
      * t-score rewards frequency, so it surfaces reliable but dull pairs.
      * G2 (log-likelihood) sits between and is the usual default.

    Reporting only the one that flatters a finding is a researcher degree of
    freedom; reporting all three removes it.
    """
    node = node.lower()
    joint, total = Counter(), Counter()
    n_windows = 0
    for s in sentences:
        toks = tokens(s)
        total.update(toks)
        for i, w in enumerate(toks):
            if w != node:
                continue
            n_windows += 1
            lo, hi = max(0, i - window), min(len(toks), i + window + 1)
            joint.update(t for t in toks[lo:i] + toks[i + 1:hi])
    n_tok = sum(total.values())
    if not n_tok or not n_windows:
        return []
    span = 2 * window
    out = []
    for w, o in joint.items():
        if o < min_count:
            continue
        # Expected co-occurrences if the collocate were spread at random.
        e = total[w] * n_windows * span / n_tok
        if e <= 0:
            continue
        mi = math.log2(o / e)
        t = (o - e) / math.sqrt(o)
        g2 = log_likelihood(o, total[w] - o, n_windows * span, n_tok)
        out.append((w, o, round(e, 2), round(mi, 2), round(t, 2), round(g2, 1)))
    out.sort(key=lambda r: -r[5])
    return out[:top]


def dispersion(term_docs: dict, min_docs: int = 3):
    """Keep only terms attested in at least `min_docs` distinct documents.

    The filter that separates a term from a name. A genuine legal alias recurs
    across decisions; a party's a/k/a appears in exactly one. Always report
    document frequency alongside raw count, because a term appearing 400 times
    in one opinion is not a pattern.
    """
    return {t: len(d) for t, d in term_docs.items() if len(d) >= min_docs}
