---
name: validate-before-ship
description: Use this skill before merging, praising, or considering "done" ANY new algorithm, heuristic, scoring function, or statistical technique added to a research-driven codebase — anything with a formula in it. Trigger this whenever a change is justified by theoretical reasoning alone ("this fills a gap," "this is more rigorous," "this generalizes X") rather than a measured before/after comparison. Also trigger when reviewing a pull request or diff that adds a new scoring/weighting term, when a component has never been run end-to-end against a real target, or when asked "does this actually help" about any subsystem. This skill exists because many projects repeatedly ship mathematically-broken code that passed code review and passing tests, because correctness-in-isolation was mistaken for correctness-in-practice.
---

# Validate Before Ship

## The failure mode this skill exists to catch

A new algorithm gets added. It's mathematically sound, well-documented, has unit tests, and the tests pass. It ships. Nobody ever runs the system end-to-end, with and without the new thing, on a real target, and looks at whether it actually improves outcomes. Months later, someone traces through the code line-by-line and discovers the new thing was silently broken or inert the entire time — and the tests passed because they asserted the exact wrong value the bug produces, or never exercised the path that mattered.

Common manifestations of this pattern:
- A scoring function with an inverted sign, silently producing the opposite of intended behavior — for an unknown number of commits.
- A scheduler whose core attribution mechanism never worked, meaning all candidates converged on identical fitness every round.
- A computation that was a mathematical tautology — and the one test written for it asserted the tautological value, so the test could never have caught it.

Each of these was catchable by asking one plain-English sentence about expected behavior. None of them were caught until someone did that specific check. This skill is that check, made mandatory and habitual.

## When to apply this

Any time a change to a codebase does one or more of:
- Adds a new scoring function, weight, distance metric, or probability model
- Adds a new scheduler, bandit, or optimizer variant
- Claims to "fix a gap" or "generalize" something using a new statistical or algorithmic technique
- Is justified primarily by *theoretical* argument ("this is the correct formula for X," "this is more rigorous than Y") rather than a measured outcome
- Has never actually been run against a real, non-toy target for a meaningful duration

If none of the above apply — e.g. a pure refactor, a bug fix with no new behavior, a test-only change — this skill doesn't need to run.

## Integration with AGENTS.md

If the project has an `AGENTS.md` (or `CLAUDE.md`, `COPILOT.md`, or similar agent instruction file), this skill should be referenced there so agents invoke it automatically. Add a rule like:

```markdown
## Validation gate
Before merging any change that adds a new algorithm, scoring function, weight, or statistical technique, invoke the `validate-before-ship` skill. Log the result in `docs/VALIDATION_LOG.md`.
```

This ensures the validation check is part of the project's standard workflow, not dependent on someone remembering to trigger it.

## The checklist

Work through these in order. Do not skip ahead because the code "looks right."

### 1. State the one-sentence sanity check, before reading further code

For any new scoring/weighting function, write down the plain-English statement of what "correct" behavior looks like at the extremes. Not the formula — the *behavior*.

Examples of the right question:
- "Does an extreme outlier get scored as *more* surprising than a typical value?"
- "Can this function ever return anything other than the trivial case, given how its inputs are defined?"
- "Does the fitness-tracking mechanism know *which* candidate actually produced a given outcome?"

If you can't state this sentence, that itself is the finding — write it down as an open question rather than proceeding.

### 2. Check the sentence against the actual code path, not the docstring

Trace the real data flow for the specific case in your sentence. Don't trust a comment or docstring's claim about what the function does — run it, or read it line by line against the concrete case. A three-line inline script (`python3 -c "..."`) that constructs the extreme/edge case and prints the result is usually enough. This is cheap; do it before anything else.

### 3. Check whether the test suite could ever have caught a violation of your sentence

Find the test(s) covering this component. For each one, ask: if the bug your sentence describes were present, would this specific assertion fail? If the test asserts a property the buggy code would *also* satisfy (a vacuous bound, a tautological constant, `isinstance(x, float)`, `x >= 0`), it provides no real coverage — note this explicitly, and either strengthen the test now or flag it as a known gap.

### 4. Never accept "it's mathematically correct" as sufficient justification alone

A correct formula, correctly implemented, is necessary but not sufficient. The actual question is always: *does adding this change measured outcomes for the better*, on a real workload. A theoretically sound addition that changes nothing in practice, or is redundant with something already present, is not worth the complexity it adds — every additional scoring term is something a future person has to understand, maintain, and re-verify.

### 5. Before calling any scheduling/algorithmic change "done," produce a real before/after comparison

Pick a real target — not a synthetic/toy test. Define a baseline configuration (the simplest reasonable prior approach). Run baseline and new-version side by side for a real duration. Compare on the metric that actually matters — not on the intermediate statistic the new algorithm itself produces (e.g. don't validate a new diversity score by checking that the diversity score is high; validate it by checking whether corpus selected using it produces better end-to-end results than corpus selected without it). Write the actual numbers down somewhere durable — not just in a conversation that will be forgotten.

If the comparison shows no measurable improvement, say so plainly rather than keeping the addition on the strength of its theoretical appeal. A simpler codebase that's been honestly validated is worth more than a sophisticated one that hasn't.

### 6. Watch for velocity outpacing validation

If a burst of commits adds several new subsystems in quick succession without any of them being individually run and validated per the above, that's the specific pattern that repeatedly produces silent, long-lived bugs. Flag it explicitly rather than reviewing each commit in isolation and letting the backlog of unvalidated complexity grow. It is better to pause and validate three additions together than to validate zero of them and let a fourth land on top.

## What this skill is not

This isn't a call to slow down experimentation or gatekeep every commit behind a full benchmark suite — small, cheap changes and genuine bug fixes don't need this treatment. It's specifically for the class of change that introduces new algorithmic *judgment* into the system (a new way of deciding what's interesting, what's stale, what's worth trying next) — the exact category where "it compiles and the unit test passes" has, in many projects' own history, repeatedly meant nothing about whether the thing actually worked.

## Validation log

Every time this skill is actually invoked — checked against a real change, in a real review — append an entry to the project's validation log, whether or not it caught anything. The log must live in the **project being validated**, never in this skill's directory. Write to `docs/VALIDATION_LOG.md` (create the directory and file if they don't exist). Do NOT write the log to the skill directory itself.

A project with an empty validation log after months of use is itself a finding: either this skill isn't being invoked, or it's being invoked and never catching anything worth recording, and either case is worth knowing.

Format: `date — what was checked — result (caught something / confirmed clean / skipped and why)`

Example entry:
```
- 2026-07-09 — new diversity scoring function in `src/scoring.py` — caught inverted normalization; baseline outperformed by 12% after fix
```
