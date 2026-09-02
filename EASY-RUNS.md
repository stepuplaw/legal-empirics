# Cheap runs: clean numbers that need no coding

_Written 2026-09-02. Everything here is mechanical — retrieval and arithmetic on
fields the corpus already holds. No codebook, no model, no reliability debt, so
none of it is exploratory for want of a second coder. That is the whole appeal._

---

## The trap in "appeals went up this year"

The obvious cheap study is a count of decisions per year, and it is the one
`METHODOLOGY.md` §5 forbids. A rise in decisions matching a lane can mean three
different things and the raw count cannot separate them:

1. more disputes reached and were decided on appeal
2. the same disputes, but a larger share got **published**
3. neither — the corpus simply holds more of that year

Two of the three are fixed by the same discipline: a **rate**, against a
denominator drawn from **the same courts in the same years**. Restricting
numerator and denominator to one fixed court set also controls for ingest
composition, which will otherwise manufacture a trend out of nothing.

The third — publication — is not fixed by a rate. It is measurable, and that is
run **B** below.

⚠ Note what an opinion corpus can never see: appeals *filed*. It holds decided
appeals that were published. "Appeal volume" is not the available quantity, and
saying so out loud is cheaper than being corrected later.

---

## A. Build the denominator table first. It is infrastructure, not a study.

One pass: **decisions × court × year**, national, state appellate. Cache it to a
small table beside the studies.

Every prevalence run afterwards costs one FTS query and a join. The rule that
makes trend claims honest stops being an obstacle and becomes free. Nothing else
on this list should be started before it exists, and it is an afternoon.

Add the court-set mask alongside it: for any date window, which courts were
reporting throughout. A trend computed over a shifting court set is an artefact,
and the mask makes that impossible to do by accident.

---

## B. Publication rate by court and year

`cluster_meta.precedential` is already in the corpus. The share of decisions
published, per court, per year, is a groupby.

**Why this one first.** Every study in this repository carries the same
limitation paragraph — *published appellate opinions are a biased sample, most
appeals are not published* — and every one of them states it rhetorically. This
run turns the repository's most-repeated caveat into a measured number, per
court, per decade. It also calibrates every other trend here: a doctrine whose
rate rises in a court whose publication rate rose the same amount has not risen.

Cheap, mechanical, and it improves work already published rather than adding to
the pile.

*Status of the field: `precedential` exists on `cluster_meta`. Its value
vocabulary has not been inspected — check it before designing around it.*

---

## C. Vocabulary diffusion across the states

Pick a term. Report its first appearance and its rate curve in each of the 51
jurisdictions. One FTS query per term against the denominator table, no coding
at all, and the output is 51 adoption curves.

Terms worth the run, each a real doctrinal innovation with a spread to trace:

    decanting · trust protector · directed trustee · silent trust
    no-contest clause / in terrorem · transfer on death deed
    enhanced life estate deed / Lady Bird deed · electronic will
    digital assets · self-settled asset protection trust

**This is the best value on the list.** It is a genuine empirical result — how
legal innovations propagate between state courts — it needs nothing but the
denominator table, and the Lady Bird deed curve feeds `NEXT-PROJECTS.md` §3,
which is the commercial project. One run, two audiences.

The known trap is the corpus-coverage one: an early first-appearance date in a
well-digitised state and a late one in a thin state is a fact about the corpus.
Report first appearance **and** the state's coverage in that decade, together.

---

## D. The UTC adoption event study

Roughly two thirds of the states enacted the Uniform Trust Code, on dates that
are public and staggered from 2001. Non-adopters are controls. Rate of
trust-related appellate decisions per court-year, before and after each state's
adoption, differences in differences.

No text coding whatsoever. The inputs are the denominator table, one FTS lane,
and a table of adoption dates from uniformlaws.org.

This is the most publishable thing on the list and still costs no coding. It is
also the natural companion to `protocols/trustee-litigation.md`, since UTC §806
and §1008 arrive with adoption — so the same event study answers whether
codifying the professional standard changed anything.

*The reformation-fl study already does this shape for one state with two dated
breaks — trusts from 2007, wills from 2011. This is that trick, national.*

---

## E. Runs off the citation graph

77.5M edges in `us-meta.db`, the largest unused asset here, and every one of
these is arithmetic on it.

- **Citation half-life** by court and decade. How fast does a state's case law
  stop being cited? Feeds `NEXT-PROJECTS.md` §2 directly.
- **Insularity index.** Share of a state supreme court's outbound citations that
  point at its own prior decisions. Cheap, comparative, and nobody publishes it.
- **Cross-state borrowing matrix.** Which states cite which. A 51×51 heatmap
  from one groupby.

All three are one query and a division. None needs a single opinion to be read.

---

## F. Mechanical court-behaviour metrics

From fields already in the corpus, no retrieval at all:

- **Dissent and concurrence rate** by court and year, from `opinions.type`.
- **Opinion length** by court and year, from `opinions.nchars`.
- **Citations received** in the first five years, by court and year, from
  `cluster_meta.citation_count`.

Modest novelty — dissent rates in particular have a literature — but they are
close to free, and they double as corpus-health checks: a discontinuity in mean
opinion length at a year boundary is an ingest problem, not a jurisprudential
one, and better found here than inside a study.

*Status: `opinions.type` and `nchars` exist. The `type` value vocabulary has not
been inspected.*

---

## What NOT to put on this list

**Reversal rate.** It sounds mechanical and is not. The reformation-fl run found
a machine-readable holding in **51 of 932** decisions, because opinions state
their disposition in a sentence that never repeats the operative word. Anything
shaped like "who won" is outcome coding, with a codebook and a second coder, and
it belongs with the studies rather than here.

**Time to decision.** Needs docket dates the opinion corpus does not carry.

---

## Suggested order

1. **A**, the denominator table — everything else depends on it
2. **B**, publication rate — improves what is already published
3. **C**, vocabulary diffusion — best result per unit of work, and it feeds the
   commercial project
4. **D**, the UTC event study — the one that could be a paper
