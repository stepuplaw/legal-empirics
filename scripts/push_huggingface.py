#!/usr/bin/env python3
"""Publish the exported datasets to Hugging Face.

    python3 scripts/push_huggingface.py            # all
    python3 scripts/push_huggingface.py reformation-fl

WHAT GOES UP. The CSV, plus the three metadata files that describe it, plus a
dataset card. The card is not decoration: Hugging Face renders the YAML
frontmatter into facets people actually filter on, and the body is where a
reader finds out what the columns mean and what the data cannot support.

WHAT THE CARD MUST SAY. Every one of these studies is exploratory, the coded
samples behind them were coded once, and statutory exposure is not abrogation.
A dataset card that omits the limits is how a number ends up in somebody's paper
carrying more weight than it earned.

THIS IS A DISTRIBUTION, NOT THE CANONICAL RECORD. Every card points back at the
DOI, the repository and the research page rather than presenting itself as the
source of truth.
"""
import argparse, json, os, sys, pathlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export_dataset import DATASETS, SITE, REPO, ORCID, SOFTWARE_DOI, HERE

from huggingface_hub import HfApi

# ★ Taken from the token, never hardcoded. The account is "StepUpLaw" and the
# URL form is lowercase; huggingface.co redirects between them, but the create
# API does not, and it answers a lowercase namespace with a 403 that reads like
# a permissions problem rather than a spelling one.
OWNER = None


def size_category(n):
    if n < 1_000:
        return "n<1K"
    if n < 10_000:
        return "1K<n<10K"
    if n < 100_000:
        return "10K<n<100K"
    if n < 1_000_000:
        return "100K<n<1M"
    return "1M<n<10M"


def card(name, spec, dp):
    res = dp["resources"][0]
    rows, fields = res["rows"], res["schema"]["fields"]
    tags = ["legal", "law", "empirical-legal-studies"] + [
        k.replace(" ", "-").replace("'", "") for k in spec["keywords"][:6]]

    fm = {
        "license": "cc-by-4.0",
        "language": ["en"],
        "pretty_name": spec["title"],
        "size_categories": [size_category(rows)],
        "tags": tags,
        "configs": [{"config_name": "default",
                     "data_files": [{"split": "train", "path": f"{name}.csv"}]}],
    }
    import yaml
    head = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n"

    cols = "\n".join(f"| `{f['name']}` | {f['type']} | {f['description']} |"
                     for f in fields)

    return head + f"""
# {spec['title']}

{spec['description']}

**{rows:,} rows.** Licence CC BY 4.0. Not legal advice.

## Where this comes from

| | |
|---|---|
| Canonical record | https://doi.org/{SOFTWARE_DOI} |
| Code and methodology | {REPO} |
| Research page | {SITE}/research/ |
| Author | Kevin D. Klagge, [ORCID 0009-0002-1385-8498]({ORCID}) |
| Source corpus | CourtListener bulk export, snapshot 2026-06-30 |

The DOI above identifies the **code**, which is a different object from this
dataset. Cite the code when you are describing the method and cite this dataset
when you are using the numbers.

## Columns

| Column | Type | Meaning |
|---|---|---|
{cols}

Every row carries a `statement` column, which is the row written as one
self-contained English sentence. A row of codes can be downloaded but not
retrieved or quoted, and the sentence is what makes each row usable on its own.

## How it was built

Retrieval and extraction are deterministic code over a local corpus of 10.8M US
judicial opinions. Classification uses rules written against a hand-coded sample
that ship with their measured accuracy, so the error rate is reported rather
than assumed. Every study states its exclusion funnel with counts, because
silent filtering is the commonest defect in research on opinions and it is
invisible in the result.

`datapackage.json` carries the Frictionless schema, `croissant.json` the
MLCommons Croissant description, and `dataset.jsonld` the schema.org form.

## Limits

**This is exploratory.** The coded samples behind it were coded once, so it
supports a described pattern rather than a measurement. Inter-annotator
reliability has not been established.

**Published appellate opinions are not disputes.** Most disputes settle, most
settlements are unpublished, and appellate coverage varies by court and decade.
Any rate here is a rate among decisions that reached an appellate court and were
published, which is not the same population a drafter cares about.

**Read the study's own limitations section** in the repository before quoting a
number. Each one names the specific threats to its own validity, including the
ones that are unflattering.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("datasets", nargs="*")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    names = a.datasets or list(DATASETS)
    api = HfApi()
    who = api.whoami()
    owner = OWNER or who["name"]
    print(f"# authenticated as {who.get('name')} ({who.get('type')}), "
          f"pushing under {owner}", file=sys.stderr)

    for name in names:
        spec = DATASETS[name]
        outdir = os.path.join(HERE, "dist", name)
        dp = json.load(open(os.path.join(outdir, "datapackage.json")))
        text = card(name, spec, dp)
        pathlib.Path(os.path.join(outdir, "README.md")).write_text(text)

        repo_id = f"{owner}/{name}"
        if a.dry_run:
            print(f"  [dry run] would push {repo_id} "
                  f"({dp['resources'][0]['rows']:,} rows)")
            continue

        api.create_repo(repo_id, repo_type="dataset", exist_ok=True)
        api.upload_folder(
            repo_id=repo_id, repo_type="dataset", folder_path=outdir,
            commit_message="Dataset, metadata and card from legal-empirics")
        print(f"  pushed https://huggingface.co/datasets/{repo_id}")


if __name__ == "__main__":
    main()
