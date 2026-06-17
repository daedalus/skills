# Instructions — [Asset Name]

**Owner:** [human name] — this file is edited only by the human, never by Claude.

## Goal
What are we optimizing, and why does it matter? (e.g. "Reduce landing page load time
so fewer visitors bounce before the page renders.")

## The single metric
[Name the one number — e.g. "page load time in ms, measured by score.py"]

Target: [e.g. "under 800ms" / "no fixed target, just keep improving" / "beat current best by 20%"]

## Rules
- Claude may only edit: [path(s) to the ASSET file(s)]
- Claude may read but never edit: [path to score.py / scoring.md]
- One change per round. No bundling multiple hypotheses into a single test.
- A round only counts as "kept" if the scoring file says the new version is better —
  no judgment calls, no "it looks nicer."
- [Any other constraints: things that must never change, brand voice rules, legal
  copy that can't be touched, performance floors that can't be broken, etc.]

## Cadence
Run in short loops, [interval — e.g. "~5 minutes" or "as fast as feedback allows"],
indefinitely, until the goal is hit or the human says stop.

## Stop conditions
- Goal metric reached: [value]
- Human says stop
- [Optional: max rounds without improvement before pausing to check in]
