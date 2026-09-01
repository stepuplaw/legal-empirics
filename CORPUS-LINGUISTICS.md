# Legal corpus linguistics

What it is, the actual techniques, what it is for, and where the opening is.

> Citations below are given from knowledge and have **not** been verified
> against the published sources. Check every one before relying on it.

---

## 1. The idea

When a judge writes "the ordinary meaning of *vehicle* is X," that is an
**empirical claim about how people use a word**. For most of legal history it
was supported by intuition or a dictionary. Corpus linguistics says: that claim
is testable. Go look at a large body of real language use and measure it.

That is the whole move. It is not a theory of interpretation; it is a method for
answering one factual sub-question that interpretation depends on.

**Is it a subfield of empirical legal studies?** Related but not nested.
Empirical legal studies studies *legal institutions and behaviour* — who sues,
who wins, what judges do. Corpus linguistics studies *language*, and gets used
in law because some legal questions are language questions. Content analysis of
opinions and corpus linguistics share statistical habits and almost nothing
else: different objects, different corpora, different claims.

## 2. Where it came from

- **Stephen Mouritsen**, *The Dictionary Is Not a Fortress*, 2010 BYU L. Rev. —
  the argument that dictionaries cannot settle ordinary meaning.
- **Thomas R. Lee & Stephen C. Mouritsen**, *Judging Ordinary Meaning*, 127 Yale
  L.J. 788 (2018) — the landmark statement of the method for lawyers.
- **State v. Rasabout**, 356 P.3d 1258 (Utah 2015) — Justice Lee's concurrence,
  widely treated as the first serious judicial application.
- **BYU Law** built the corpora the field runs on, including COFEA, the Corpus
  of Founding Era American English, aimed at originalist questions.

The centre of gravity is constitutional and statutory interpretation. That is
important, because it is also where the opening is.

## 3. The actual techniques

These are general corpus linguistics, borrowed wholesale. None is exotic.

**Frequency.** How often does each candidate sense occur? Always report both raw
count and a normalised rate (per million words, or per N documents), because
corpora differ in size.

**Concordance, or KWIC (keyword in context).** Pull every occurrence with a
window of surrounding text and read them. This is the workhorse: most findings
come from reading a few hundred lines, not from a statistic.

**Collocation.** Which words appear near the target more often than chance?
Measured by **mutual information**, **log-likelihood**, or **t-score**. MI
favours rare distinctive pairings; log-likelihood favours frequent ones. Report
which you used, because they rank differently.

**N-grams.** Recurring multi-word sequences. This is what surfaces boilerplate
and formulaic drafting.

**Keyness.** Terms overrepresented in a target corpus compared with a
**reference corpus**, usually by log-likelihood. Keyness is meaningless without
naming the reference.

**Semantic prosody.** Whether a term habitually keeps positive or negative
company. Useful for showing a word carries baggage its dictionary entry omits.

**Dispersion.** Is the term spread across many documents or concentrated in a
few? A term appearing 400 times in one opinion is not a pattern.

## 4. The rules

1. **Choose a corpus that matches the speech community and the period.** Modern
   news text cannot answer what a phrase meant to a testator in 1974. Corpus
   choice drives results, so it is the first thing a critic attacks.
2. **Name your reference corpus** for any keyness or comparison claim.
3. **Normalise.** Raw counts across corpora of different sizes are not
   comparable.
4. **Sample concordance lines randomly** when there are too many to read, and
   say how many you read.
5. **Sense-tag with a codebook and report reliability.** Deciding which sense an
   occurrence carries is coding, with all the obligations from
   [METHODOLOGY.md](METHODOLOGY.md).
6. **Distinguish types from tokens.** One document repeating a phrase forty
   times is one type, forty tokens.
7. **Ambiguity is not vagueness.** Ambiguity means two or more discrete
   competing senses; vagueness means one sense with fuzzy edges. Corpus
   frequency speaks to the first far better than the second.

## 5. The criticisms, which you should know before a critic tells you

- **Frequency is not meaning.** The most common usage is not automatically the
  legal one, and rare senses are not wrong senses.
- **Corpora are not neutral.** Available text over-represents published,
  edited, formal writing.
- **Judges are not linguists**, and neither are lawyers. Misapplied MI scores
  look authoritative and can be badly wrong.
- **It can launder intuition.** Choosing the corpus, the query and the window
  gives many degrees of freedom, which is why pre-registration matters.

A study that names these before being asked is far harder to dismiss.

## 6. What it is for, and where the opening is

Established use is **interpretive**: what did this word mean, so what does the
statute or constitutional clause require. Retrospective, and aimed at courts.

The gap is **prospective and aimed at drafters**. Nobody much is asking: *which
words, in instruments people actually sign, end up being fought over?* That is a
corpus question, it is answerable, and its audience is the person drafting
tomorrow rather than the judge construing yesterday.

**Why it is answerable.** When a court construes a will or a trust, it **quotes
the disputed language**. Those quotations are a naturally occurring corpus of
provisions that failed in practice — already curated by the fact of litigation.
A probe over the Florida corpus extracted them cleanly: `"grandchildren"`,
`"an amount not to exceed $85,000."`, `"the northwest quarter of section 7 north
of Castor river."` The method is concordance plus n-gram extraction over the
quoted spans.

**What it can honestly claim.** A frequency table of judicially disputed
testamentary language: these constructions recur in litigated instruments. That
is a real, novel, useful finding, and it supports drafting guidance of the form
*this phrasing has repeatedly required a court to construe it.*

**What it cannot claim without a control group.** That these phrasings *cause*
litigation. The corpus holds only litigated instruments. If `"per stirpes"`
appears constantly in disputed language it may simply be that `"per stirpes"`
appears constantly in wills. Establishing risk needs a denominator of
unlitigated instruments — form books, published precedents, filed wills — which
is a separate data problem and the reason to state the limit rather than skate
past it.

**So the honest framing is:** a corpus of *judicially construed* testamentary
language, reported as frequency and collocation, offered as drafting
intelligence rather than as causal risk. That is defensible, publishable, and as
far as the evidence reaches.

## 7. A minimal first study

1. **Population:** Florida appellate decisions construing a will or trust.
2. **Retrieval:** construction and ambiguity language co-occurring with
   testamentary document terms, via `~/caselaw/`.
3. **Exclusions:** statutory interpretation, contracts, insurance, deeds.
   Report the funnel.
4. **Extraction:** quoted spans within a window of the construction language.
5. **Normalisation:** lowercase, strip citations, drop spans that are case names
   or statutory cites rather than instrument language.
6. **Analysis:** n-gram frequency, dispersion across documents, collocation.
7. **Coding:** a sample hand-classified by provision type — beneficiary
   designation, class gift, residuary, condition, fiduciary power — with
   reliability reported.
8. **Output:** a frequency table, and drafting notes tied to it.

That is one study, it is genuinely new as far as I know, and it produces
something a practising lawyer can use.
