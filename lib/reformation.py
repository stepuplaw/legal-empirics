#!/usr/bin/env python3
"""Classifiers for Florida reformation decisions: instrument, error, outcome.

WHY REFORMATION IS THE RIGHT NARROWING. Ambiguity litigation tells you a clause
was argued about. A reformation petition tells you the drafter got it WRONG and
somebody paid a lawyer to fix it. It is the closest thing in the reports to an
admitted drafting defect, which makes it the sharpest available measure of
preventive-law failure.

WHY FLORIDA CAN CARRY A PUBLISHED STUDY ON IT. Three regimes coexist in one
state, with dated statutory breaks:

    deeds, contracts      reformation in equity, always available
    trusts                s. 736.0415, ch. 2006-217, effective 2007
    wills                 s. 732.615, ch. 2011-183, effective 2011

Before 2011 Florida followed the traditional rule that a will could not be
reformed at all. So the same remedy has three different start dates inside one
jurisdiction, one court hierarchy and one appellate corpus -- a within-state
natural experiment that needs no cross-state comparison to be interpretable.

THE `reform` STEM IS POLYSEMOUS AND MUST BE FILTERED, NOT TRUSTED. Tort reform,
prison reform, reform school, welfare reform and the Reformed Church all match
it. Retrieval is deliberately wide; these rules do the hard filtering, and the
exclusion funnel is reported with counts.
"""
import re

# --------------------------------------------------------------------------
# Is this decision about reforming an instrument at all?
# --------------------------------------------------------------------------
REFORM_RX = re.compile(
    r"\b(reformation|reform(?:ed|ing|s)?)\b|\bscrivener\b|"
    r"\b(?:mutual|unilateral)\s+mistake\b|\bdrafting\s+(?:error|mistake)\b|"
    r"\bdraftsman'?s?\s+error\b", re.I)

# Every one of these was a visible contaminant when the stem was left unfiltered.
# `reform should come by constitutional and statutory amendment` is law reform,
# not instrument reformation, and it read as the latter until it was caught by
# reading the output rather than by reasoning about the pattern.
NOT_REFORMATION = re.compile(
    r"\b(?:tort|prison|welfare|campaign|election|school|penal|legislative|"
    r"medicaid|health\s*care|civil\s*service|pension|insurance\s+market|"
    r"tax|regulatory|structural)\s+reform"
    r"|\breform\s+(?:school|movement|act\s+of|party|legislation)"
    r"|\breformator(?:y|ies)\b|\bReformed\s+Church\b|\breform\s+jud"
    r"|\breform\s+(?:should|must|can)\s+come\b"
    r"|\b(?:constitutional|statutory|legislative)\s+(?:amendment|reform)\b"
    r"|\bwill\s+of\s+the\s+(?:people|voters|electorate)\b"
    r"|\b(?:free|good|ill)\s+will\b", re.I)

# ★ `will` IS AN AUXILIARY VERB, and treating it as a noun put Bush v. Gore in
# a study about testamentary drafting. `Gore v. Harris`, a utility rate case
# ("will dispose of United's 1987 savings"), and a rules-amendment order all
# matched a bare \bwill\b. The word is only evidence of a testamentary
# instrument when something around it makes it a noun, so it is never matched
# bare -- anywhere in this module.
_WILL_NOUN = (r"(?:last\s+will|will\s+and\s+testament|wills\b|"
              r"(?:the|his|her|their|decedent'?s?|testator'?s?|testatrix'?s?|"
              r"deceased'?s?)\s+will\b|will\s+of\s+(?:the\s+)?(?:decedent|"
              r"testator|testatrix|deceased))")

INSTRUMENT_RX = re.compile(
    rf"\b(?:{_WILL_NOUN}|codicil|testament\w*|trust|deed|conveyance|mortgage|"
    r"contract|agreement|polic(?:y|ies)|settlement|instrument|beneficiar\w+|"
    r"settlor|grantor|testat\w+)\b", re.I)


def is_reformation(sent: str) -> bool:
    """A sentence about reforming a legal instrument."""
    if not REFORM_RX.search(sent):
        return False
    if NOT_REFORMATION.search(sent):
        return False
    return bool(INSTRUMENT_RX.search(sent))


# --------------------------------------------------------------------------
# Which instrument was reformed?
# --------------------------------------------------------------------------
# Ordered most specific first. A trust case mentions "will" constantly
# (pourover wills), so trust and will are separated on their own vocabulary
# rather than on which word appears more often.
_INSTRUMENT = [
    ("will",     rf"\b({_WILL_NOUN}|codicil|testat(?:or|rix)|"
                 r"devise\w*|bequest|bequeath\w*|residuary\s+(?:clause|estate)|"
                 r"732\.615|732\.616)\b"),
    ("trust",    r"\b(trust\s+(?:instrument|agreement|document)?|settlor|trustee|"
                 r"revocable\s+trust|irrevocable\s+trust|736\.0415|"
                 r"trust\s+amendment)\b"),
    ("deed",     r"\b(deed|conveyance|legal\s+description|metes\s+and\s+bounds|"
                 r"easement|quitclaim|warranty\s+deed|grantor\s+and\s+grantee)\b"),
    ("insurance", r"\b(polic(?:y|ies)|insur\w+|endorsement|coverage|premium)\b"),
    ("contract", r"\b(contract|agreement|promissory\s+note|mortgage|lease|"
                 r"purchase\s+and\s+sale|settlement\s+agreement)\b"),
]
INSTRUMENT = [(n, re.compile(p, re.I)) for n, p in _INSTRUMENT]


def instrument(text: str) -> str:
    for name, rx in INSTRUMENT:
        if rx.search(text):
            return name
    return "uncertain"


# --------------------------------------------------------------------------
# What went wrong?
# --------------------------------------------------------------------------
_ERROR = [
    ("wrong_description", r"\b(legal\s+description|metes\s+and\s+bounds|"
                          r"wrong\s+(?:lot|parcel|property)|misdescri\w+|"
                          r"incorrect\s+description|scrivener'?s?\s+error\s+in\s+the\s+"
                          r"description)\b"),
    ("wrong_person",      r"\b(wrong\s+(?:beneficiar\w+|name|person|party)|"
                          r"misnomer|incorrectly\s+named|name\s+of\s+the\s+"
                          r"beneficiar\w+|omitted\s+(?:child|spouse|heir))\b"),
    ("tax_objective",     r"\b(tax\s+(?:objective|consequence|purpose)|marital\s+"
                          r"deduction|generation[- ]skipping|qualified\s+"
                          r"terminable|732\.616|estate\s+tax|GST)\b"),
    ("omitted_provision", r"\b(omitted|left\s+out|failed\s+to\s+include|"
                          r"inadvertently\s+(?:omitted|deleted)|missing\s+"
                          r"(?:clause|provision|page))\b"),
    ("scriveners_error",  r"\b(scrivener'?s?\s+error|drafting\s+(?:error|mistake)|"
                          r"draftsman'?s?\s+error|typographical\s+error|clerical\s+"
                          r"error)\b"),
    ("mutual_mistake",    r"\bmutual\s+mistake\b"),
    ("unilateral_mistake", r"\bunilateral\s+mistake\b"),
]
ERROR = [(n, re.compile(p, re.I)) for n, p in _ERROR]


def error_type(text: str) -> list[str]:
    """Every error type present. Deliberately multi-label: a scrivener's error
    IS the mechanism and `wrong_description` is what it produced, and collapsing
    them to one would throw away the half a drafter can act on."""
    return [n for n, rx in ERROR if rx.search(text)] or ["unspecified"]


# --------------------------------------------------------------------------
# Did the court actually reform it?
# --------------------------------------------------------------------------
# Negation first, for the same reason posture.py tests `rejected` first: a
# sentence saying reformation was NOT warranted also matches the grant patterns.
# ★ THREE WAYS A SENTENCE CAN MENTION REFORMATION AND NOT BE A HOLDING, each of
# which the first version of this classifier scored as one. They were found by
# reading its output, not by reasoning about it:
#
#   describing authority  "the grantee was held entitled to reformation,
#                          Tampa Northern R. Co. v. City of Tampa, 140 So. 311"
#   stating the rule      "a mistake on one side is no ground for reformation"
#   posing the question   "is Brogdon, through his remote grantor, entitled
#                          to reformation?"
#
# All three are excluded before any outcome is read, which loses recall and
# protects precision -- the same trade posture.py makes deliberately.
_AUTHORITY = re.compile(
    r"\b\d+\s+(?:So|F|U\.S|N\.E|S\.E|N\.W|S\.W|P|A)\.\s?\d?d?\s+\d+"
    r"|\bv\.\s+[A-Z]|\bSee\s|\bCf\.|\baccord\b|\bquoting\b|\bciting\b", re.I)
_RULE_STATED = re.compile(
    r"\b(?:must\s+be|is|are)\s+(?:occasioned|established|allowed|available|"
    r"required|governed)\b"
    r"|\bno\s+ground\s+for\b|\bin\s+order\s+to\s+(?:obtain|justify)\b"
    r"|\bgeneral(?:ly)?\b|\bit\s+is\s+well[- ]settled\b|\bthe\s+rule\s+is\b"
    r"|\bburden\s+of\s+proof\b|\bclear\s+and\s+convincing\s+evidence\s+is\b", re.I)
_QUESTION = re.compile(r"\?\s*$")

# The court speaking about THIS case, in its own voice or about the record.
_COURT_VOICE = re.compile(
    r"\bwe\s+(?:affirm|reverse|hold|conclude|find|agree|disagree|remand|reject)\b"
    r"|\b(?:the\s+)?(?:trial\s+)?court\s+(?:properly|correctly|erred|abused)\b"
    r"|\bfinal\s+(?:judgment|decree)\b|\bwe\s+therefore\b"
    r"|\b(?:affirmed|reversed|remanded)\.?\s*$", re.I)

# What was reversed decides the direction. Reversing a DENIAL of reformation is
# a win for reformation; reversing an ORDER of reformation is a loss. Reading
# `reverse ... reform` as one thing gets half of them backwards -- which is
# METHODOLOGY.md lesson 5 in a new costume.
_ANTI_TARGET = re.compile(
    r"\b(?:order|judgment|decree|final\s+judgment)\b[^.]{0,40}\breform", re.I)
_PRO_TARGET = re.compile(
    r"\b(?:denial|dismissal|summary\s+judgment|order\s+denying|"
    r"directed\s+verdict)\b[^.]{0,60}\breform"
    r"|\breform\w*\s+(?:claim|count|action)[^.]{0,40}\b(?:dismiss|denied)", re.I)

_GRANTED = [
    r"\b(?:affirm\w*|uphold|uphel[dt])\b[^.]{0,70}\b(?:reformation|reformed|reforming)\b",
    r"\b(?:properly|correctly)\s+reformed\b",
    r"\breformation\s+(?:is|was)\s+(?:proper|appropriate|warranted|justified)\b",
    r"\bgrant(?:ed|ing)\s+(?:the\s+)?(?:petition\s+for\s+)?reformation\b",
    r"\bremand\w*\s+(?:with\s+(?:directions|instructions)\s+)?(?:to|for)\s+"
    r"(?:the\s+trial\s+court\s+to\s+)?reform\b",
    r"\bwe\s+(?:hold|conclude|find)\b[^.]{0,60}\bentitled\s+to\s+reformation\b",
]
_DENIED = [
    r"\b(?:not|never)\s+entitled\s+to\s+reformation\b",
    r"\breformation\s+(?:is|was|would\s+be)\s+(?:improper|unavailable|"
    r"inappropriate|unwarranted)\b",
    r"\b(?:affirm\w*)\b[^.]{0,60}\b(?:denial|dismissal)\b[^.]{0,40}\breform",
    r"\bfailed\s+to\s+(?:establish|prove|meet)\b[^.]{0,60}\breformation\b",
    r"\breform\w*\s+(?:claim|count|petition)\s+fail",
    r"\bwe\s+(?:reject|disagree)\b[^.]{0,60}\breform",
]
DENIED = [re.compile(p, re.I) for p in _DENIED]
GRANTED = [re.compile(p, re.I) for p in _GRANTED]


def outcome(sent: str) -> str:
    """granted | denied | sought | rule_stated | authority | uncertain.

    Only a sentence in the court's own voice about this case can carry an
    outcome. Everything else is labelled for what it is, so a later reader can
    see how much of the corpus was excluded and why, instead of finding it
    silently pooled into `uncertain`.
    """
    if _AUTHORITY.search(sent):
        return "authority"
    if _QUESTION.search(sent):
        return "uncertain"
    if _RULE_STATED.search(sent) and not _COURT_VOICE.search(sent):
        return "rule_stated"

    # Direction of a reversal, before the generic patterns get a chance.
    if re.search(r"\brevers\w+\b", sent, re.I):
        if _PRO_TARGET.search(sent):
            return "granted"
        if _ANTI_TARGET.search(sent):
            return "denied"

    if any(r.search(sent) for r in DENIED):
        return "denied"
    if any(r.search(sent) for r in GRANTED):
        return "granted"
    if re.search(r"\b(sought|seeks|petition\w*|sued|filed\s+an?\s+action|"
                 r"complaint)\b[^.]{0,70}\breform", sent, re.I):
        return "sought"
    return "uncertain"


RESOLVED = {"granted", "denied"}

# --------------------------------------------------------------------------
# Which statutory regime governed at the time of decision?
# --------------------------------------------------------------------------
REGIME_START = {"will": 2011, "trust": 2007}    # ch. 2011-183 / ch. 2006-217


def regime(inst: str, year: int | None) -> str:
    """`statutory` where a reformation statute was in force for that instrument
    at that date, `equitable` where the remedy rested on general equity, and
    `pre-statute` for wills before 2011 -- when Florida law was that a will
    could not be reformed at all."""
    if year is None:
        return "unknown"
    start = REGIME_START.get(inst)
    if start is None:
        return "equitable"
    return "statutory" if year >= start else "pre-statute"
