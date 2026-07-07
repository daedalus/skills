---
name: approach-extractor
description: Extracts the reasoning behind a solved problem — not just the diff or the fix, but why that approach was chosen, what alternatives were rejected and why, and what generalizes. Use this any time a debugging session, code review, research task, proof attempt, or exploratory investigation reaches a resolution and the user wants it captured as a learnings note, not just closed out. Trigger on explicit requests ("write up what we learned", "extract the approach", "capture this as a pattern", "document the reasoning", "turn this into a note") AND proactively suggest it whenever a nontrivial fix or finding is about to be left undocumented — a solution without a learnings note is unfinished work.
---

# Approach Extractor

A fix or finding is not done when the diff lands. It's done when the reasoning that produced it is written down somewhere it can be reused. This skill turns a session (conversation history, git log, transcript, or diff) into a short, dense **learnings note**: what was actually happening in the search space, not just what the final commit looks like.

## When to run this

- User explicitly asks to extract/capture/write up the approach, reasoning, or learnings from a session.
- A debugging session, code review, or research investigation just concluded with a real fix or finding — proactively offer to extract it rather than letting it evaporate.
- User is closing out a `SKILL.md`, git history, or handoff doc and the "why," not just the "what," matters for future reuse.

Do not run this on trivial changes (typo fixes, formatting, one-line obvious bugs). The bar is: did this involve rejecting at least one plausible alternative, or a non-obvious insight? If not, there's nothing to extract.

## Source material

Identify what you're extracting from, in priority order:

1. **This conversation** — the back-and-forth itself is usually the richest source: dead ends, "wait, that's wrong because...", the moment the real cause surfaced.
2. **Git history** — `git log -p`, commit messages, and diffs across the relevant commits if the fix spans multiple commits (`bash_tool` + `view`).
3. **A transcript or handoff doc** the user points to.

If the source material doesn't actually contain a rejected alternative or a non-obvious insight, say so — don't manufacture one to fill out the template.

## Extraction procedure

Answer these, in order, using only what's actually evidenced in the source — no invented alternatives, no hindsight-smoothed narratives:

1. **Problem** — What was actually broken, unclear, or unknown at the start? One or two sentences, stated as it looked *before* the answer was known.
2. **Search space** — What approaches were tried, considered, or proposed and then rejected? For each: why it looked plausible, and the specific reason it was dropped (not "didn't work" — the actual mechanism of failure).
3. **Chosen approach** — What was actually done. The mechanism, not the summary. If it's code, name the specific technique (e.g. "LSH bucketing with a fallback dense pass," not "optimized the algorithm").
4. **Key insight** — The single non-obvious realization that unlocked the fix. If there isn't one — if this was just careful elimination — say that instead of inventing an insight.
5. **Verification** — How was this actually confirmed (test run, proof check, empirical measurement, reproduction)? Claims without a verification step get flagged as unverified, not silently upgraded to fact.
6. **Generalizable principle** — What's reusable beyond this specific instance? This is the part worth keeping when the specific bug is long forgotten. If it doesn't generalize, say "narrow to this case" rather than stretching for false generality.

## Output format

Write the note directly — skip a preamble summary before it. Use this structure:

```markdown
# <slug>: <one-line problem statement>

**Date:** <date>
**Context:** <repo/file/session this came from>

## Problem
<1-3 sentences, framed as it looked before the answer was known>

## Rejected
- **<approach>** — looked plausible because <reason>; dropped because <specific failure mechanism>
- (repeat per rejected approach; omit section entirely if none were seriously considered)

## Approach
<the actual mechanism, concrete and specific>

## Key insight
<the one non-obvious thing, or "none — this was elimination" if that's the truth>

## Verification
<what was actually run/checked, and what it showed>

## Generalizes to
<the reusable principle, stated so it applies outside this specific case — or "narrow to this case" if it doesn't>
```

Keep it dense. No filler sentences, no restating the problem in the approach section, no motivational framing. If a section is genuinely empty (no rejected alternatives, no single key insight), say so in one line rather than padding it.

## Where to save it

Ask where this should live if it isn't obvious from context — common patterns worth checking for first:
- `LEARNINGS.md` at repo root (append, most recent last)
- `docs/learnings/<date>-<slug>.md` (one file per note)
- Inline in a `SKILL.md` under a "Known pitfalls" or "Lessons" section, if this is feeding back into a skill file

Default to appending to `LEARNINGS.md` at the repo root if one already exists; otherwise ask once rather than guessing a new convention.
