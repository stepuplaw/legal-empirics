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
