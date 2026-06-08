"""
run_pipeline.py
===============
Command-line entry points to run each stage by hand.

WHY:
During development you want to run one step at a time:
  python scripts/run_pipeline.py scrape      # collect documents
  python scripts/run_pipeline.py embed       # build embeddings
  python scripts/run_pipeline.py evaluate    # run the experiments

This file just calls into the src/ modules. It contains no real logic --
it is the "buttons" you press to make things happen.

WHAT IT WILL DO LATER:
- argument parsing for each stage
- wire each command to the matching module
"""


def cmd_scrape():
    """TODO: run the scraper, save raw documents to data/raw/."""
    ...


def cmd_embed():
    """TODO: embed all documents, store vectors in the DB."""
    ...


def cmd_evaluate():
    """TODO: run the evaluation grid, save results."""
    ...


if __name__ == "__main__":
    # TODO: parse sys.argv and dispatch to the right command
    ...
