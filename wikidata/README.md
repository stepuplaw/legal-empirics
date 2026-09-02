# Wikidata

## What to create, and what not to

**Create an item for the WORK. Do not create one for the practice, and not yet
for the person.**

Wikidata's notability policy admits an entity that is "clearly identifiable" and
"can be described using serious and publicly available references". A software
release with a DOI, a Zenodo record and a public repository meets that plainly,
which is why millions of scholarly works have items. A small law firm probably
does not, and a deleted item is a worse signal than no item, because the
deletion discussion is permanent and public.

A person item is also premature. One deposit is a thin basis for one, and the
work item carries the author as a name string in the meantime. When there are
papers and several DOIs, the name string upgrades to a linked person item and
the graph gets better without anything being rewritten.

## Conflict of interest, which is the part that actually protects the item

The account name matches the subject. That is exactly the pattern reviewers look
for, and the defence is disclosure rather than discretion.

**Before making the edit**, put a line on the user page at
`https://www.wikidata.org/wiki/User:StepUpLaw`:

> I am Kevin D. Klagge ([ORCID 0009-0002-1385-8498](https://orcid.org/0009-0002-1385-8498)).
> I edit items about my own open-source research software and datasets, and I
> disclose that connection. I do not create items about my law practice.

An undisclosed conflict is what gets an item deleted. A disclosed one is
ordinary editing.

## How to make the edit

Use **QuickStatements**, the community's own tool, rather than hand-filling
forms. It is reviewable before it runs and it leaves a clean, attributable edit
history.

1. Go to `https://quickstatements.toolforge.org/`
2. Authorise it against the Wikidata account, once.
3. Choose **New batch**, paste the contents of `legal-empirics.qs`, and select
   the V1 (tab-separated) format.
4. Read the preview. It should create one item with ten statements.
5. Run it.

## What the statements say

| Property | Value | Meaning |
|---|---|---|
| P31 | Q7397 | instance of software |
| P1476 | title | the full title as deposited |
| P356 | 10.5281/zenodo.22247377 | the **concept** DOI, which always resolves to the newest version |
| P2093 | Kevin D. Klagge | author as a name string, since no person item exists |
| P275 | Q20007257 | CC BY 4.0 |
| P577 | 2026-09-02 | publication date |
| P1324 | GitHub URL | source code repository |
| P953 | doi.org URL | work available at |
| P973 | stepuplaw.com/research/ | described at |

## Afterwards

Record the Q-number here once it exists, and add it to `DISTRIBUTION.md`. The
datasets get their own items only after they have their own DOIs; until then the
work item is the single node and that is the honest shape of it.
