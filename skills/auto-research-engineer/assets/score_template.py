"""
score.py — the objective measuring stick.

LOCKED: Claude may import/run this file to compute a score, but must never
edit it, and must never change what counts as "better." If the metric needs
to change, that's a human decision that goes through instructions.md, not
a silent edit here.

Usage:
    python score.py <path-to-asset>

Must print a single number to stdout (or write one to a known field) so the
loop can compare round N to round N-1 without ambiguity.
"""

import sys


def score(asset_path: str) -> float:
    """
    Compute and return ONE number for the given asset.

    Replace this with the real measurement:
      - run the code and time it
      - hit an endpoint and measure latency
      - parse a CSV of campaign results and compute open/click/reply rate
      - call an eval rubric and return a numeric grade

    Lower-is-better or higher-is-better should be documented clearly here
    so there's never ambiguity about which direction counts as "winning."
    """
    raise NotImplementedError("Fill in the real scoring logic for this asset.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python score.py <path-to-asset>")
        sys.exit(1)

    result = score(sys.argv[1])
    print(result)
