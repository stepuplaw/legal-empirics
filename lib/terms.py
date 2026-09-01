#!/usr/bin/env python3
"""Extract the DISPUTED TERM from a decision, and say what kind of term it is.

WHY THE WHOLE OPINION, NOT THE AMBIGUITY SENTENCE. The ambiguity-pools study
tried to pull instrument language out of the sentence that called it ambiguous
and got a null result. Its own diagnosis was right: courts quote the disputed
provision in the facts, often pages before the holding. So the ambiguity finding
selects the CASE, and extraction runs over the whole text.

WHY CUE-ANCHORED QUOTES, NOT ALL QUOTES. Every quoted span in an opinion is
mostly noise -- party testimony, case names, doctrinal tags. Measured over 600
Florida decisions, the top raw quoted spans were "and", "yes" and "i'd rather
not talk about it". But courts name the disputed language with a small and
stable set of cues -- `the term "X"`, `the word "X"`, `the phrase "X"`, `"X" as
used in` -- and those return "accident", "occurrence", "arising out of",
"all-risk". The cue is the anchor; the quotation marks alone are not.

WHY THE CATEGORY MATTERS MORE THAN THE TERM. A drafter cannot act on "the word
'occurrence' is litigated in Florida". They can act on "nexus connectors are the
single most litigated class of contract language, and here is what to write
instead". So every term is assigned a functional class, and the class is the
unit the report leads with. The lexicon below is hand-built and therefore
FALLIBLE: `uncategorised` is reported as its own row rather than hidden, because
a taxonomy that silently absorbs what it cannot place is unfalsifiable.
"""
import re

# --------------------------------------------------------------------------
# Sentence splitting
# --------------------------------------------------------------------------
# The ambiguity-pools run split on `(?<=[.;])\s+`, which cuts "So. 2d" and
# "Fla. Stat." in half and truncates the sentence a posture rule needs to read.
_ABBREV = (r"(?:Nos?|Art|Sec|Ch|Fla|Stat|Ann|Supp|Rev|Civ|Crim|Proc|Const|"
           r"Co|Corp|Inc|Ltd|Assn|Bros|Dept|Div|Comm|Ins|Nat|Am|Cas|Sur|"
           r"So|F|S|N|E|W|A|P|U|L|Ed|Cir|Dist|Ct|App|Sup|J|Jr|Sr|Mr|Mrs|Ms|Dr|"
           r"v|vs|etc|eg|ie|cf|id|seq|para|pp|Rptr|Wash|Cal|Tex|Ill|Ariz|Colo|"
           r"Conn|Del|Ga|Ind|Kan|Ky|La|Md|Mass|Mich|Minn|Miss|Mo|Mont|Neb|Nev|"
           r"Okla|Ore|Pa|Tenn|Vt|Va|Wis|Wyo|Ala|Ark|Idaho|Iowa|Utah|Haw)")
_BOUNDARY = re.compile(r"[.;?!][\"'\)\]]?\s+(?=[A-Z\"'\(])")
# Python forbids a variable-width lookbehind, so the abbreviation guard is
# applied to the text before each candidate boundary instead of inside it.
_ENDS_ABBREV = re.compile(r"(?:^|[\s\(\[])" + _ABBREV + r"\.$")
_INITIAL = re.compile(r"(?:^|\s)[A-Z]\.$")


def sentences(text: str) -> list[str]:
    """Split on sentence ends, guarding the abbreviations legal text is full of.

    `So. 2d`, `Fla. Stat.` and `Smith, J.` all end in a period followed by a
    capital, and a naive split cuts them in half -- which truncates exactly the
    sentence a posture rule has to read to classify the holding.
    """
    out, start = [], 0
    for m in _BOUNDARY.finditer(text):
        prefix = text[start:m.start() + 1]
        if _ENDS_ABBREV.search(prefix) or _INITIAL.search(prefix):
            continue
        s = text[start:m.start() + 1].strip()
        if s:
            out.append(s)
        start = m.end()
    tail = text[start:].strip()
    if tail:
        out.append(tail)
    return out


# --------------------------------------------------------------------------
# Cue-anchored term extraction
# --------------------------------------------------------------------------
_CUE_NOUN = (r"(?:term|terms|word|words|phrase|phrases|language|clause|"
             r"provision|expression|sentence|definition)")
_Q = r"[\"“‘’”']"

# Forward: the term "X"        Reverse: "X" as used in the policy
CUE_FWD = re.compile(
    rf"\b{_CUE_NOUN}\s*,?\s*(?:of\s+|in\s+|is\s+|are\s+)?{_Q}([^\"“”]{{2,70}}?){_Q}",
    re.I)
CUE_REV = re.compile(
    rf"{_Q}([^\"“”]{{2,70}}?){_Q}[,\s]+(?:as\s+)?(?:used|employed|"
    rf"appearing|found|defined|contained)\s+(?:in|within|by)\b", re.I)

# What a term is NOT. Each of these was a visible contaminant in the probe.
_CASE_NAME = re.compile(r"\bv\.\s|\bIn\s+re\b|\bEx\s+parte\b|\d{2,4}\s+(?:So|F|U\.S|"
                        r"N\.E|S\.E|N\.W|S\.W|P|A|Cal|Ill|N\.Y)\b", re.I)
_HAS_DIGIT = re.compile(r"\d")
# Court-speak: dispositions, doctrine names and standards of review are
# litigated constantly but are not language anybody drafts into an instrument.
_COURT_SPEAK = {
    "affirmed", "reversed", "remanded", "quashed", "denied", "granted",
    "order quashing", "per curiam", "res gestae", "res judicata", "dicta",
    "harmless error", "fundamental error", "abuse of discretion", "de novo",
    "competent substantial evidence", "reasonable doubt",
    "beyond a reasonable doubt", "prima facie", "sua sponte", "certiorari",
    "the record", "the evidence", "the trial court", "the court", "the state",
    "the defendant", "the plaintiff", "guilty", "not guilty", "objection",
    "sustained", "overruled", "so help you god", "yes", "no", "okay", "i do",
    "plain meaning", "plain language", "clear and unambiguous", "ambiguous",
    "ambiguity", "unambiguous", "latent ambiguity", "patent ambiguity",
    "great weight", "some weight", "the majority", "the dissent", "we",
}

# A bare article, pronoun or auxiliary is a fragment the cue regex clipped, not
# a disputed term. Function words that ARE genuinely fought over -- and, or,
# any, such, shall -- are deliberately absent from this list: the and/or problem
# and the shall/may problem are two of the oldest known defects in drafted
# language, and a study that filtered them out would be measuring its own filter.
_STOP_ALONE = {
    "the", "a", "an", "of", "as", "at", "by", "in", "on", "to", "for", "with",
    "from", "into", "we", "i", "you", "it", "he", "she", "they", "them", "his",
    "her", "their", "its", "this", "that", "these", "those", "there", "here",
    "also", "made", "make", "been", "being", "was", "were", "is", "are", "be",
    "do", "did", "does", "had", "has", "have", "not", "so", "then", "than",
    "what", "who", "whom", "which", "why", "how", "said", "very", "us",
}
_STRIP = " \t\n\r .,;:!?()[]{}*"


def normalise(term: str) -> str | None:
    """Lowercased, punctuation-stripped, or None if it is not a usable term."""
    t = re.sub(r"\s+", " ", term).strip(_STRIP).lower()
    if not t or len(t) < 2:
        return None
    if len(t.split()) > 6:
        return None
    if _HAS_DIGIT.search(t) or _CASE_NAME.search(t):
        return None
    if t in _COURT_SPEAK or t in _STOP_ALONE:
        return None
    if not re.search(r"[a-z]", t):
        return None
    return t


def extract_terms(text: str, context: int = 160) -> dict[str, tuple[str, int]]:
    """Every cue-anchored term, mapped to (context window, character offset).

    The window is kept because the term alone does not say what document it came
    out of: `"occurrence" as used in the policy` is contract language and
    `"issue" as used in the will` is testamentary, and the same word can be both.

    The offset is kept so a term can be located in the opinion relative to the
    sentence that makes the ambiguity holding. A term quoted three sentences
    from the holding is far better evidence than one quoted twenty pages away,
    and without the offset those two are indistinguishable.
    """
    found: dict[str, tuple[str, int]] = {}
    for rx in (CUE_FWD, CUE_REV):
        for m in rx.finditer(text):
            t = normalise(m.group(1))
            if not t:
                continue
            if t not in found:
                lo = max(0, m.start() - context)
                found[t] = (text[lo:m.end() + context].replace("\n", " "),
                            m.start())
    return found


def sentence_spans(text: str) -> tuple[list[str], list[tuple[int, int]]]:
    """The sentences, plus each one's (start, end) character offsets.

    `sentences()` alone loses position, and position is what turns "this term
    appears somewhere in this opinion" into "this term appears beside this
    holding".
    """
    sents = sentences(text)
    spans, cursor = [], 0
    for s in sents:
        i = text.find(s, cursor)
        if i < 0:                       # whitespace normalisation lost it
            i = cursor
        spans.append((i, i + len(s)))
        cursor = i + len(s)
    return sents, spans


# --------------------------------------------------------------------------
# What document did the term come out of?
# --------------------------------------------------------------------------
# Decided on the context window around the quote, not on the decision as a
# whole. A trust case cites statutes; the question is which document the
# disputed words sit in.
_SOURCE = [
    ("testamentary", r"\b(will|codicil|testament\w*|trust\s+(?:instrument|agreement|"
                     r"document)?|testat\w+|devise|bequest|residuary|settlor)\b"),
    ("deed",         r"\b(deed|conveyance|easement|covenant|plat|restriction\w*|"
                     r"declaration\s+of\s+(?:condominium|restrictions))\b"),
    ("insurance",    r"\b(polic(?:y|ies)|insur\w+|endorsement|coverage|insured)\b"),
    ("contract",     r"\b(contract|agreement|lease|note|mortgage|guarant\w+|"
                     r"indemnit\w+|release|settlement)\b"),
    ("statute",      r"\b(statut\w+|section\s+\d|§|ordinance|legislat\w+|code|"
                     r"rule\s+\d|regulation)\b"),
    ("constitution", r"\b(constitution\w*|amendment|ballot)\b"),
]
SOURCE = [(n, re.compile(p, re.I)) for n, p in _SOURCE]


def source(window: str) -> str:
    """Which instrument the disputed words sit in. Private documents first:
    an insurance case cites the code, a will case cites the probate statute,
    and in both the drafted document is the thing being construed."""
    for name, rx in SOURCE:
        if rx.search(window):
            return name
    return "uncertain"


# --------------------------------------------------------------------------
# Functional taxonomy -- the unit a drafter can act on
# --------------------------------------------------------------------------
# Hand-built, and deliberately not exhaustive. Anything unmatched is reported
# as `uncategorised` so the gap is visible and can be closed by reading it.
_CATEGORY = [
    ("nexus",       r"^(arising\b.*|resulting\b.*|relating\b.*|growing out of|"
                    r"flowing from|originating\b.*|in connection with|"
                    r"connected with|based (?:on|upon)|attributable to|"
                    r"caused by|due to|on account of|with respect to|"
                    r"pertaining to|in relation to|as a result of|by reason of|"
                    r"incident to|arising|out of)$"),
    ("degree",      r"^(reasonabl\w*|unreasonabl\w*|material\w*|substantial\w*|"
                    r"adequate|inadequate|satisfactory|sufficient|excessive|"
                    r"good faith|bad faith|best efforts|due diligence|"
                    r"undue|proper|appropriate|necessary|fair|equitable|"
                    r"significant|serious|severe|major|minor|reasonable care|"
                    r"ordinary care|due care|gross)$"),
    ("temporal",    r"^(sudden\w*|immediat\w*|prompt\w*|forthwith|timely|"
                    r"permanent\w*|temporar\w*|continuous\w*|annual\w*|"
                    r"monthly|during|until|from time to time|"
                    r"within a reasonable time|as soon as (?:practicable|possible)|"
                    r"regular\w*|periodic\w*|current|final|ongoing)$"),
    ("scope",       r"^(any|all|each|every|other|such|including|include\w*|"
                    r"including but not limited to|and|or|and/or|but|"
                    r"whatsoever|thereof|therein|hereunder|same|either|"
                    r"both|among|between|through|solely|only|exclusively|"
                    r"and nothing else|in any manner|generally)$"),
    ("modal",       r"^(shall|may|must|will|should|is entitled|entitled|"
                    r"required|obligated|authorized|permitted|"
                    r"shall not|may not|is required to)$"),
    ("role",        r"^(employee|employer|insured|named insured|resident|"
                    r"occupant|occupied|dependent|child|children|spouse|"
                    r"patient|owner|operator|user|member|partner|agent|"
                    r"contractor|subcontractor|tenant|landlord|purchaser|"
                    r"vendor|customer|consumer|household|family|relative|"
                    r"person|party|parties|principal|driver|passenger)$"),
    ("succession",  r"^(issue|descendant\w*|heir\w*|per stirpes|per capita|"
                    r"survive\w*|surviving|lineal\w*|next of kin|"
                    r"legal representative\w*|estate|residue|residuary\w*|"
                    r"share|shares|equally|children of|grandchildren)$"),
    ("property",    r"^(premises|appurtenance\w*|improvement\w*|fixture\w*|"
                    r"personal (?:effects|property)|contents|structure|"
                    r"building|dwelling|land|lot|parcel|boundary|frontage|"
                    r"common area\w*|unit|facility|facilities|equipment|"
                    r"goods|merchandise|inventory|vehicle|automobile)$"),
    ("event",       r"^(accident|accidental|occurrence|loss|losses|damage\w*|"
                    r"injur\w*|collapse|vandalism|theft|casualty|claim|"
                    r"disability|disabled|death|destruction|failure|"
                    r"default|breach|termination|interruption|"
                    r"bodily injury|property damage|act|acts)$"),
    ("mental",      r"^(knowing\w*|wilful\w*|willful\w*|intentional\w*|"
                    r"negligen\w*|reckless\w*|malicious\w*|deliberate\w*|"
                    r"fraudulent\w*|good cause|cause|intent|purpose)$"),
]
CATEGORY = [(n, re.compile(p, re.I)) for n, p in _CATEGORY]

# A second pass for terms the exact list misses. These fire on a STRONG MARKER
# anywhere in the term, so `uninsured motor vehicle` reaches property and
# `within a reasonable time` reaches degree. Ordered: the first match wins, and
# the order encodes which reading dominates when a term carries two markers.
_MARKER = [
    ("nexus",      r"\b(arising|resulting|relating|related to|growing out of|"
                   r"connection with|connected|based (?:on|upon)|attributable|"
                   r"caused by|by reason of|incident to|out of|pertaining)\b"),
    ("degree",     r"\b(reasonabl\w*|unreasonabl\w*|material\w*|substantial\w*|"
                   r"adequate|satisfactor\w*|sufficient|excessive|good faith|"
                   r"bad faith|best efforts|due diligence|undue|proper|"
                   r"necessary|significant|gross|willful\w*|serious)\b"),
    ("condition",  r"\b(subject to|provided that|unless|until|except|"
                   r"notwithstanding|in the event|upon|conditioned|"
                   r"under this (?:chapter|section|act)|by law|as provided|"
                   r"pursuant to|if)\b"),
    ("temporal",   r"\b(sudden\w*|immediat\w*|prompt\w*|forthwith|timely|"
                   r"permanent\w*|temporar\w*|continuous\w*|annual\w*|"
                   r"during|periodic\w*|time|date|day|days|year|years|"
                   r"month|months|week|weeks)\b"),
    ("succession", r"\b(issue|descendant\w*|heir\w*|per stirpes|per capita|"
                   r"surviv\w*|lineal|next of kin|residuar\w*|residue|"
                   r"testat\w*|devise\w*|bequest|legatee|beneficiar\w*)\b"),
    ("role",       r"\b(insured|employee|employer|resident|occupant|dependent|"
                   r"child|children|spouse|patient|owner|operator|member|"
                   r"partner|agent|contractor|tenant|landlord|purchaser|"
                   r"vendor|customer|consumer|household|famil\w*|relative|"
                   r"person|persons|part(?:y|ies)|driver|passenger|borrower|"
                   r"lender|claimant|survivors?)\b"),
    ("property",   r"\b(premises|appurtenance\w*|improvement\w*|fixture\w*|"
                   r"personal effects|contents|structure|building|dwelling|"
                   r"residence|land|lot|parcel|boundary|common area\w*|unit|"
                   r"equipment|goods|merchandise|inventory|vehicle|automobile|"
                   r"auto|weapon|firearm|knife|pocketknife|property|"
                   r"instrument|document|record\w*)\b"),
    ("event",      r"\b(accident\w*|occurrence|loss|losses|damage\w*|injur\w*|"
                   r"collapse|vandalism|theft|casualt\w*|claim\w*|disabilit\w*|"
                   r"disabled|death|destruction|failure|default|breach|"
                   r"termination|interruption|sickness|illness|disease|"
                   r"conviction|convicted|judgment|violation)\b"),
    ("conduct",    r"\b(use|used|using|possession|possess\w*|operation|"
                   r"operating|occupancy|occupied|carry|carrying|"
                   r"maintenance|maintain\w*|construction|performance|"
                   r"delivery|service|services|work|business|conduct)\b"),
    ("mental",     r"\b(knowing\w*|wilful\w*|intentional\w*|negligen\w*|"
                   r"reckless\w*|malicious\w*|deliberate\w*|fraudulent\w*|"
                   r"intent|purpose|cause|motive)\b"),
    ("scope",      r"\b(any|all|each|every|other|such|includ\w*|whatsoever|"
                   r"thereof|therein|solely|only|exclusiv\w*|either|both|"
                   r"among|between|general\w*|entire|whole|full)\b"),
]
MARKER = [(n, re.compile(p, re.I)) for n, p in _MARKER]

CATEGORY_NAMES = ([n for n, _ in _CATEGORY] +
                  [n for n, _ in _MARKER if n not in dict(_CATEGORY)] +
                  ["uncategorised"])

# `the insured`, `any firearm` and `such premises` are the same drafting problem
# as `insured`, `firearm` and `premises`. The determiner is stripped for
# classification only -- the term is reported as the court quoted it.
_DET = re.compile(r"^(?:the|a|an|any|all|such|said|this|that|each|every|"
                  r"his|her|its|their|our|your)\s+(?=\S)", re.I)


def category(term: str) -> str:
    """Functional class of a disputed term, or `uncategorised`.

    Exact match first, then a strong-marker pass, then the determiner is
    stripped and both are retried. `uncategorised` is a real answer and is
    reported rather than absorbed: most of it is one-off language specific to
    one instrument, which is a finding about the tail, not a defect.
    """
    for cand in (term, _DET.sub("", term, count=1)):
        for name, rx in CATEGORY:
            if rx.match(cand):
                return name
        for name, rx in MARKER:
            if rx.search(cand):
                return name
    return "uncategorised"
