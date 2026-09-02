# Identifying the trustee: terminology, and what actually works

_Written 2026-09-02, before any study run. Two questions answered here: what the
law calls these two kinds of trustee, and how to tell which one a decision is
about. The second is answered with a measurement, not an opinion._

---

## 1. The vocabulary, from the drafters rather than from practice

The scoping pass looked for the terminology in **opinions** and found almost
none — nationally 135 decisions say "professional trustee" against 7,061 in the
study pool. That is the right answer to the wrong corpus. Courts assume the
vocabulary; the drafters define it. This repeats the alias-mining lesson in
`METHODOLOGY.md` §9: *legal vocabulary lives in statutes, dictionaries and
treatises, not in opinions.*

### The contrast pair is professional / amateur, and it is the drafters' own

**Uniform Prudent Investor Act §2(f)**, official comment, headed *Professional
fiduciaries* — verified in the FDIC *Trust Examination Manual*, Appendix C,
"Fiduciary Law Excerpts":

> "The distinction taken in subsection (f) between **amateur and professional
> trustees** is familiar law. The prudent investor standard applies to a range of
> fiduciaries, from the most sophisticated professional investment management
> firms and **corporate fiduciaries**, to **family members of minimal
> experience**. Because the standard of prudence is relational, it follows that
> the standard for professional trustees is the standard of prudent
> professionals; for amateurs, it is the standard of prudent amateurs."

That paragraph is the whole design in miniature. It names the axis
(professional/amateur), it names the standard (relational), and it says the axis
runs from institutions to family members without claiming those are the same
thing.

### Every term of art, and where each comes from

| Term | Source | Note |
|---|---|---|
| **professional / amateur trustee** | UPIA §2(f) cmt | the drafters' own pair. The axis that matters |
| **corporate fiduciary** | UPIA §2(f) cmt; OCC and FDIC usage | the regulatory term for the entity |
| **bank or trust company** vs **an individual trustee** | Restatement (2d) Trusts §174 | the doctrinal pair, and the older one |
| **family trustee** vs **corporate trustee** | UTC §807 cmt | "delegating some administrative and reporting duties might be prudent for a family trustee but unnecessary for a corporate trustee" |
| **institutional trustee** | UTC §706 cmt; §108 cmt | used for removal and for principal place of administration |
| **financial institution trustee** | UTC §708 cmt | "normally base their fees on **published fee schedules**" |
| **licensed professional fiduciary** | Cal. Prof. Fiduciaries Act, B&P Code §6500 et seq., licensing from 2009 | licenses **non-family** fiduciaries serving **for a fee** — a statutory definition of the professional/lay line |
| **licensed fiduciary** | Ariz., certified by the Supreme Court from 1999-04-01 | "persons serving as fiduciaries for a fee must be licensed" |
| **family trust company** | Nev. NRS 669A; several states | corporate **form**, family **capacity**. Breaks the proxy in the other direction |

**The UTC has no statutory definition of either kind.** §103's definition of
"trustee" covers original, successor and cotrustees and draws no
professional/individual line; the differentiation lives entirely in the comments
and in the standard-setting sections. That is itself the finding Leslie (27
Cardozo L. Rev. 2713) complains about, and it is why judicial behaviour is the
place to look.

### What the courts actually say, counted

National, all courts, **opinions** matching each phrase (`scratchpad/count2.py`,
2026-09-02). This is a vocabulary triage, not a funnel — opinions, not decisions,
and no court filter.

| Corporate side | Opinions | | Individual side | Opinions |
|---|---:|---|---|---:|
| corporate trustee | **2,572** | | individual trustee | **994** |
| corporate fiduciary | **1,710** | | family trustee | 55 |
| professional fiduciary | 394 | | lay trustee | 19 |
| professional trustee | 192 | | nonprofessional trustee | 16 |
| institutional trustee | 134 | | **amateur trustee** | **0** |
| licensed professional fiduciary | 10 | | | |
| financial institution trustee | 3 | | family trust company | 11 |

Three things fall out of this table.

**`corporate fiduciary` is the missing half of the corporate vocabulary, and the
scoping pass never searched it.** 1,710 opinions, against 2,572 for "corporate
trustee" — and unioned, **4,097**, a 59% gain over the trustee form alone. On the
professional axis the gain is larger still: `professional trustee` OR
`professional fiduciary` is **573** against 192, which nearly triples it. Every label pool in `NEXT-PROJECTS.md` was built on `* trustee` forms
alone, so all of them understate the corporate side. The same holds on the
professional axis, where the *fiduciary* form beats the *trustee* form outright —
**professional fiduciary 394 against professional trustee 192**. The label lane
has to be `(corporate|professional|institutional) NEAR (trustee|fiduciary)`.

**`amateur trustee` returns zero.** The drafters' own word for the low end does
not exist in judicial usage. Use `professional / amateur` as the name of the
axis, because it is the uniform acts' name and it is precise. Never use it as a
query.

**The vocabulary is asymmetric, and that is the whole problem in one number.**
Roughly 4,200 opinions on the corporate side against roughly 1,100 on the
individual side. Courts **mark** the corporate trustee — they say bank, trust
company, corporate, institutional — and leave the individual trustee unmarked,
because an unmodified "trustee" is presumed to be a person. A label-based design
therefore has one arm built from what courts name and the other from what they
decline to name, which is not a comparison. This is the quantitative form of the
finding the Florida modifier list reached qualitatively, and it is the reason the
identification has to come from the role slot.

### Two things this settles

**Use `professional` / `amateur` as the axis name, not `professional` /
`individual`.** The second pair mixes an axis of capacity with an axis of form,
which is the conflation the protocol's codebook already splits. The drafters
supply the word for the low end and it is `amateur`; `lay` and `family` are the
readable synonyms.

**`corporate fiduciary` is the term for the entity**, and it is the term the
regulators use, so it is also the term that connects to Call Report data.

---

## 2. The statutory hook, and why it is better than a label

UTC **§806** — *"A trustee who has special skills or expertise, or is named
trustee in reliance upon the trustee's representation that the trustee has
special skills or expertise, shall use those special skills or expertise."*

Its own comment gives the citation family, which is what makes it findable in
opinions of any vintage:

    UTC §806  ==  UPC §7-302  ==  Restatement (2d) Trusts §174 (1959)  ==  UPIA §2(f)

Four citeable forms of one rule, two of them predating the UTC by four decades.
A decision invoking **any** of them is a decision where the professional standard
was in issue — stated by the court, in its own words, with no classifier in
between.

Restatement (2d) §174 goes further than the UTC text and says the quiet part:

> "if the trustee is a bank or trust company, it must use in selecting
> investments the facilities which it has or should have, and it may properly be
> required to show that it has made a more thorough and complete investigation
> than would ordinarily be expected from an individual trustee."

⚠ That sentence is quoted from a secondary source and **must be checked against
the printed Restatement before it is cited**. The §174 black letter itself is
verified via the FDIC excerpt.

There is also a ready-made case list: **Annot., *Standard of Care Required of
Trustee Representing Itself to Have Expert Knowledge or Skill*, 91 A.L.R.3d 904
(1979)**, cited in the UPIA comment. An A.L.R. annotation is a curated set of
decisions on exactly this question — a validation set somebody else already
built. Get it before hand-coding anything.

### ⚠ The exact statutory phrase is rare. The Restatement phrasing is where the volume is.

Counted before designing around it, which is the point of counting.

| Phrase | Opinions, national, all courts | Source |
|---|---:|---|
| **"special skills or expertise"** | **88** | the exact UTC §806 / UPIA §2(f) words |
| "special facilities" | 786 | Restatement (2d) §174 |
| "greater skill" | 668 | Restatement (2d) §174 |
| "prudent professional(s)" | 168 | UPIA §2(f) cmt |
| "Uniform Prudent Investor" | 101 | the act, cited by name |
| "held itself out" | 4,381 | generic — any corporate representation, not trustee-specific |
| "7-302" | 3,898 | **unusable.** A bare number string matches dockets, dates and every other code |

**Eighty-eight opinions nationally, across every court, for the phrase the
uniform acts actually use.** A lane built on §806's exact wording would find
almost nothing and would read as evidence that courts do not apply the standard,
when it is evidence about how they phrase it.

But the raw phrase counts mislead in the other direction too, and crossing each
form with `trustee` is what settles it:

| Form, **crossed with `trustee`** | Opinions |
|---|---:|
| "special skills" | **366** |
| "greater skill" | 132 |
| "special facilities" | 100 |
| "held itself out" | 793 (generic — any corporate representation) |
| **the four forms unioned, AND trustee** | **1,748** |

So the Restatement wording does **not** dominate once a trustee is required:
*special facilities* drops from 786 to 100 and *greater skill* from 668 to 132,
because most opinions using those words are not about trustees at all. The
workhorse is the relaxed UTC form — **"special skills", 366** — which is four
times the exact four-word phrase. The Restatement forms add roughly 230 more.

**Correction to a first reading of this table.** The nine-to-one Restatement
advantage is an artefact of counting phrases in isolation. Count every candidate
*crossed with the thing you are studying*, never on its own.

Two consequences, and the second is a design change:

**Build the lane on the union of all four citeable forms**, relaxed to "special
skills" rather than the full statutory phrase. §806's own comment supplies the
equivalence, so this is the drafters' authority and not a liberty.

**The primary question is a small-pool study, not a corpus-scale one.**
**1,748 opinions** nationally across all courts, before the state-appellate
filter and before the donative-trust exclusions. Call it a few hundred decisions
after both. That is not a defect. A few hundred decisions is exactly the scale at
which a written codebook, a human second coder and a real Cohen's kappa are
affordable — which is the reliability debt `STATE.md` has been carrying since the
beginning. It also makes the name classifier much less load-bearing, because a
few hundred trustees can be identified by reading.

### Contaminant sizes, national

| Class | Opinions |
|---|---:|
| **`board of trustees`** | **68,284** |
| `substitute trustee` (deed-of-trust foreclosure) | 3,891 |
| `indenture trustee` | 3,308 |

Sixty-eight thousand. Against a study pool of 7,061. Exclusion 4b is not a
tidying step, it is the largest single filter in the funnel, and it was not in
the design two hours ago.

### Structures where a professional is involved with an amateur trustee

| Term | Opinions |
|---|---:|
| trust protector | 222 |
| directed trustee | 172 |
| corporate co-trustee | 136 |
| administrative trustee | 71 |

Small but real, and each names a distinct configuration from §3 above.

### Other sections that key off professional status

| Section | What it keys off | Why it is a signal |
|---|---|---|
| §806 | held-out expertise | the primary outcome variable |
| §807 (= UPIA §9) | delegation to **agents** | the comment says the section exists because "many trustees are not professionals" |
| §703(e) | delegation to a **cotrustee** | different standard, because the settlor picked each trustee for a reason |
| §708 | compensation | "financial institution trustees normally base their fees on published fee schedules" |
| §1008(b) | exculpatory term **drafted by the trustee** | invalid unless fair and communicated. Aimed squarely at the trustee who supplies the form |

**Behavioural signatures beat labels**, and they size well. Crossed with
`trustee`, nationally: `trust officer` **2,099**, `fee schedule` **1,232**,
`termination fee` 1,435 (uncrossed). The exact phrase `published fee schedule` is
only **50** — precise but too rare to filter on, and the earlier 12,102 for it was
almost entirely the generic `fee schedule` arm of an OR. Use `fee schedule AND
trustee`, not the §708 comment's exact words.

Each of these is a thing only one kind of trustee does, and each is stated in the
opinion in plain words.

---

## 3. The corporation involved with an amateur trustee

This is the hard case, and the UTC treats the commonest version of it as the
**recommended design**, not an anomaly. §703 comment:

> "Cotrustees are often appointed to gain the advantage of differing skills,
> perhaps **a financial institution for its permanence and professional skills,
> and a family member to maintain a personal connection with the
> beneficiaries.**"

So a mixed corporate/family cotrusteeship is not an edge case to be dropped. It
is a **third arm**, and probably the interesting one, because it is where the two
standards meet inside one trust.

Six distinct configurations, each separately detectable:

| # | Configuration | Detect by |
|---|---|---|
| 1 | entity alone | role slot returns one entity |
| 2 | natural person alone, amateur | role slot returns one personal name, no fee or expertise language |
| 3 | **natural person, professional** — lawyer, accountant, licensed fiduciary | personal name **plus** licence, fee, or held-out-expertise language. The class a name classifier cannot see |
| 4 | **mixed cotrusteeship** — institution plus family member | role slot returns both. UTC §703 cmt calls this the standard reason to appoint cotrustees |
| 5 | **amateur trustee who delegated** to a corporate agent | UTC §807 / UPIA §9 vocabulary: delegation, agent, outside manager, investment adviser |
| 6 | **family trust company** — corporate form, family capacity | entity whose name carries the family surname; state FTC statutes |

Configurations 3 and 6 break form-to-capacity in opposite directions, which is
why the protocol codes `trustee_form` and `trustee_capacity` separately. 4 and 5
are not noise to exclude — they are the structures the doctrine is actually
about, and each has its own governing section.

---

## 4. Proximity does not work. Measured, not asserted.

The open question was whether requiring an entity marker **near** the word
"trustee" would identify a corporate trustee more accurately than looking for
one anywhere in the opinion.

Three methods, run over the same 256 Florida decisions in the study pool
(`scratchpad/slots.py`, 2026-09-02, random seed 11, after removing 44 decisions
that were not about a donative trust at all):

| Method | Calls it corporate | |
|---|---:|---|
| entity marker **anywhere** in the opinion | **95%** | useless — banks, corporations, "State of", law firms are in nearly every opinion |
| entity marker within **±50 words** of "trustee" | 70% | |
| within **±25 words** | 57% | |
| within **±10 words** | 36% | |
| **role-slot extraction** — classify only who occupies the trustee slot | **1% entity, 3% mixed, 41% person** | |

**The tell is that the proximity numbers decline smoothly with the window and
never settle.** A window capturing a real signal would plateau once it was wide
enough to catch the appositive and narrow enough to exclude the rest. This one
just interpolates between the role-slot answer and the document baseline, which
means it is measuring how many entity words the opinion contains, not who the
trustee was.

This is the same lesson the disputed-terms run learned about doctrinal
contamination: *contamination is a property of the extracted span, not of the
distance between two words.* Ask **who occupies the role**, not what is nearby.

### The role slot, and what it costs

The slot has a small set of surface forms — `X, as trustee of the Y Trust`,
`the trustee, X,`, `appointed X as trustee`, `X was the named trustee`, `X in her
capacity as trustee` — and a cue-anchored extractor over them returns the filler
directly. Current state on the Florida sample: **45% of decisions yield a filler,
55% yield nothing.** That is a recall problem, not a precision problem, and it is
the work.

Two defects found by reading the output, which is the standing rule:

**The patterns had no case flag,** so `as Trustee` with a capital T never matched
and `as trustee` did. Fixing it moved recall from 30% to 45% and the personal-name
share from 26% to 41%. A silent halving of recall from one missing `re.I`.

**Mention-level classification truncates entity names.** `Barnett Banks Trust
Co., NA` was extracted as `Barnett` and scored a natural person; `Brown Brothers
Harriman Trust Co` appeared once whole and once as `Brown Brothers`. The fix is
to resolve mentions to a **party** first — longest form wins — and classify the
party once, not each mention.

### A decision usually names more than one trustee

*Holley v. First Guaranty Bank & Trust Co.* (Fla. 1st DCA 1997) names **First
Guaranty Bank** as the acting trustee — it moved for surcharge — and **Paine
Webber Trust Company of Jacksonville** as the successor trustee the revocable
trust designated in case of incompetency. The extractor pulled the second.

Both are entities here, so this decision would still land in the right arm. In a
mixed decision it would not, and mixed decisions are the interesting ones. The
role slot is necessary and not sufficient: it finds the trustees, and something
else has to decide **which trustee's conduct is at issue**. Rank fillers by
proximity to the breach language rather than by order of appearance, and record
`n_trustees_named` so decisions with more than one are visible instead of being
resolved silently.

This also means the caption cannot be trusted either way. It names whoever
appealed, which is sometimes the trustee and sometimes not.

### A contaminant class the protocol did not have

17% of the sampled pool was not about a donative trust at all, and the largest
group is entity-shaped, so it would have landed in the corporate arm:

- **`Board of Trustees`** — universities, hospitals, pension boards.
  *University of Florida Board of Trustees* is in this pool.
- **`Trustees of the Internal Improvement Fund`** — the Florida land board.
- union and pension fund trustees, bankruptcy trustees, escrow "trustees"
- personal representatives and executors, which are a different office
- Bar disciplinary opinions where a lawyer held client money "as trustee"

Add `board of trustees` to exclusion 4 in the protocol and report its count. On
these numbers it is worth roughly a sixth of the raw pool.
