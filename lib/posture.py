#!/usr/bin/env python3
"""Deterministic domain and posture classifiers for ambiguity sentences.

WHY DETERMINISTIC AT SCALE. Model coding is the better judge but is
non-deterministic and cannot be audited line by line across tens of thousands of
sentences. These rules were written against a hand-coded sample and are
VALIDATED against it, so the error rate is measured rather than assumed. The
model coding becomes the gold standard; these rules are the cheap approximation
whose disagreement with it is reported.

That is distillation: the expensive judge labels a sample, a cheap auditable
rule is induced, and the rule ships with its precision and recall attached.

POSTURE MATTERS AND THE TWO CLASSES POINT OPPOSITE WAYS. `found` means a court
could not determine the meaning, which is an anti-pattern. `rejected` means the
language drew a challenge and survived, which is a safe harbour. Never pool them.
"""
import re

# Order matters: the first pattern that fires wins, so the most specific
# and least ambiguous cues are tested first.

_REJECTED = [
    r"\b(?:not|never|hardly|scarcely)\s+(?:be\s+)?(?:considered\s+|deemed\s+|found\s+)?ambiguous\b",
    r"\bno\s+(?:such\s+|patent\s+|latent\s+|genuine\s+|real\s+)?ambiguit",
    r"\bunambiguous(?:ly)?\b",
    r"\bfinding\s+no\s+ambiguit", r"\bwithout\s+ambiguit",
    r"\bcontains?\s+no\s+ambiguit", r"\bfree\s+(?:of|from)\s+ambiguit",
    r"\bclearly\s+not\s+ambiguous\b",
    r"\bcreat\w+\s+an\s+ambiguity\s+where\s+none\b",
    r"\bdiscern\s+no\s+(?:uncertainty|ambiguit)",
]
_FOUND = [
    r"\bwe\s+(?:find|hold|conclude|agree)\b[^.]{0,80}\bambiguous\b",
    r"\bis\s+(?:clearly\s+|plainly\s+|patently\s+|highly\s+)?ambiguous\b",
    r"\brender(?:ing|ed|s)?\s+(?:it|them|the\s+\w+)\s+ambiguous\b",
    r"\bpresents?\s+a\s+(?:classic\s+|true\s+)?latent\s+ambiguit",
    r"\breflects?\s+a\s+(?:classic\s+)?latent\s+ambiguit",
    r"\bfound\s+[^.]{0,40}\bambiguous\b",
    r"\bthere\s+(?:is|was)\s+an?\s+ambiguit",
    r"\bobscured\s+by\s+ambiguous\b",
]
_ALLEGED = [
    r"\b(?:argues?|argued|contends?|contended|asserts?|asserted|claims?|maintains?)\b[^.]{0,90}\bambigu",
    r"\battempt\w*\s+to\s+show\s+an\s+ambiguit",
    r"\ballegedly\s+ambiguous\b",
]
# Black-letter recitation: a general proposition about the doctrine, with no
# finding about the text in front of the court.
_RULE = [
    r"\ba\s+latent\s+ambiguity\s+(?:in|is|does|arises|exists)",
    r"\blatent\s+ambiguit\w+\s+are\b",
    r"\bambiguity\s+suggests\s+that\b",
    r"\b(?:generally|it\s+is\s+well[- ]established|the\s+rule\s+is)\b[^.]{0,80}ambigu",
    r"\bis\s+a\s+question\s+of\s+law\b",
    r"\bmust\s+(?:be\s+)?constru\w+\b[^.]{0,60}ambigu",
    r"\bonly\s+(?:exists\s+)?when\s+it\s+is\s+susceptible\b",
    r"\bif\s+the\s+(?:statute|text)\s+is\s+(?:silent\s+or\s+)?ambiguous\b",
    r"\bwhere\s+there\s+is\s+some\s+ambiguity\b",
    r"\bcourts?\s+(?:are\s+allowed|must|may)\b[^.]{0,60}ambigu",
]

_DOMAIN = [
    ("testamentary", r"\b(will|wills|testament\w*|codicil|testat\w+|devise\w*|bequest|bequeath\w*|"
                     r"residuary|legatee|trust\s+(?:instrument|document|agreement)|pourover|"
                     r"pour[- ]over|beneficiar\w+\s+of\s+the\s+trust|settlor|grantor)\b"),
    ("contract",     r"\b(contract\w*|lease|polic(?:y|ies)|insur\w+|agreement|note|mortgage|"
                     r"indemnit\w+|venue\s+provision|purchaser|vendor)\b"),
    ("statutory",    r"\b(statut\w+|section\s+\d|§|legislat\w+|rule\s+of\s+lenity|agency)\b"),
    ("constitutional", r"\b(constitution\w*|ballot\s+(?:title|summary)|amendment)\b"),
    ("deed",         r"\b(deed|deeds|conveyance|ingress\s+and\s+egress|fee\s+simple)\b"),
]

_C = lambda pats: [re.compile(p, re.I) for p in pats]
REJECTED, FOUND, ALLEGED, RULE = _C(_REJECTED), _C(_FOUND), _C(_ALLEGED), _C(_RULE)
DOMAIN = [(n, re.compile(p, re.I)) for n, p in _DOMAIN]


def posture(sent: str) -> str:
    """One of: rejected, found, alleged, rule_stated, uncertain.

    Rejected is tested first because negation is the most reliable cue and a
    sentence saying "not ambiguous" also matches "is ambiguous" patterns.
    """
    if any(r.search(sent) for r in REJECTED):
        return "rejected"
    if any(r.search(sent) for r in ALLEGED):
        return "alleged"
    if any(r.search(sent) for r in FOUND):
        return "found"
    if any(r.search(sent) for r in RULE):
        return "rule_stated"
    return "uncertain"


def domain(sent: str) -> str:
    """Most specific matching domain, or 'uncertain'.

    Testamentary is tested first: a trust case routinely mentions a statute,
    and the document being construed is what the label is about.
    """
    for name, rx in DOMAIN:
        if rx.search(sent):
            return name
    return "uncertain"


# Litigated means the language was actually fought over, whatever the outcome.
# rule_stated says nothing about the text at hand; uncertain needs a second round.
LITIGATED = {"found", "rejected", "alleged"}
