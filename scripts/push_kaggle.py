#!/usr/bin/env python3
"""Publish the exported datasets to Kaggle.

    python3 scripts/push_kaggle.py                 # all
    python3 scripts/push_kaggle.py reformation-fl

Kaggle is a DISTRIBUTION CHANNEL, not the canonical record. The description
written by export_dataset.py points at the DOI, the repository and the research
page, so a reader who lands here first is told where the real record lives.

The Hugging Face README is deliberately not uploaded. It carries YAML
frontmatter that Hugging Face renders into facets and Kaggle does not, so it
would show up as a file of stray metadata. Kaggle takes its description from
dataset-metadata.json instead.
"""
import argparse, os, shutil, sys, tempfile, warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export_dataset import DATASETS, HERE

os.environ.setdefault(
    "KAGGLE_API_TOKEN",
    open(os.path.expanduser("~/.kaggle/access_token")).read().strip())

from kaggle.api.kaggle_api_extended import KaggleApi

# What a reader needs to interpret the data, and nothing that only makes sense
# on another platform.
KEEP = ("dataset-metadata.json", "datapackage.json", "croissant.json",
        "dataset.jsonld")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("datasets", nargs="*")
    ap.add_argument("--update", action="store_true",
                    help="push a new version of an existing dataset")
    a = ap.parse_args()

    api = KaggleApi()
    api.authenticate()
    print(f"# authenticated as {api.get_config_value('username')}", file=sys.stderr)

    for name in (a.datasets or list(DATASETS)):
        src = os.path.join(HERE, "dist", name)
        with tempfile.TemporaryDirectory() as stage:
            for f in KEEP + (f"{name}.csv",):
                p = os.path.join(src, f)
                if os.path.exists(p):
                    shutil.copy2(p, os.path.join(stage, f))
            try:
                if a.update:
                    api.dataset_create_version(
                        stage, version_notes="Refreshed from legal-empirics",
                        dir_mode="skip")
                else:
                    api.dataset_create_new(stage, dir_mode="skip",
                                           public=True, quiet=False)
                print(f"  pushed https://www.kaggle.com/datasets/stepuplaw/{name}")
            except Exception as e:
                print(f"  {name}: {type(e).__name__} {str(e)[:220]}", file=sys.stderr)


if __name__ == "__main__":
    main()
