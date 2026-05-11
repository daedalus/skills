---
name: agent-eval-no-ground-truth
description: >
  Design and reason about evaluation frameworks for production AI agents when no labeled
  dataset or ground truth exists. Use this skill whenever someone asks how to evaluate
  an agent, measure agent quality, build an eval signal stack, assess agent correctness,
  or trust agent outputs in production — especially when benchmarks don't exist for the
  domain, outputs are non-deterministic, or multiple correct answers are possible. Trigger
  on phrases like "how do I know if my agent is right", "eval for my agent", "measure
  agent accuracy", "agent quality signals", "no ground truth", "production agent metrics",
  or any request to evaluate/grade an agentic system's outputs in the real world.
---

# Agent Eval Without Ground Truth

A framework for evaluating production AI agents when you have no labeled dataset,
no replay capability, and no single correct answer.

## Core Insight

Every eval signal in production is a proxy. The goal is to build a *signal stack*
ranked by cleanliness, measure coverage honestly, and triangulate rather than
report one number.

---

## Signal Stack (rank by cleanliness, not volume)

Design your signal stack in this order of trust:

### Tier 1 — Explicit Negative Signals (cleanest, rarest)
- **Dismiss-as-invalid**: User explicitly says "this isn't a real problem"
- **User-initiated reassessment**: User corrects the agent with missing context
- These are floors on the wrong rate, not ceilings. Most wrong answers go untagged.

### Tier 2 — System Self-Correction
- **Reassessments that flip the original conclusion**: When the agent re-investigates
  with new context and reverses itself, that's evidence the original was wrong.
- High volume if you instrument it; noisier than Tier 1 but covers more ground.

### Tier 3 — Passive Outcome Signals
- **Downstream action acceptance rate** (e.g., PR merge, recommendation acted on)
- **Time-to-close on agent-generated items** vs. baseline
- **Reassignment / escalation rate**
- These are noisy. A rejected fix ≠ wrong diagnosis. See the PR merge trap below.

### Tier 4 — Explicit Positive Signals (worst coverage)
- Thumbs-up/thumbs-down buttons, star ratings
- Expect <1% coverage in practice. Engineers act; they don't rate.
- Treat their *absence* as a UX problem, not a data source.

---

## The PR Merge Trap

> "Did the user accept the agent's output?" is not an accuracy signal in isolation.

A rejected PR / declined recommendation can mean:
- Agent was wrong (what you want to measure)
- Agent was right but user prefers a different implementation
- Agent was right but team lacks capacity to act now
- Agent was right but the fix is a workaround, not a root-cause fix

**To disambiguate**: read a sample of rejections manually. If the pattern is
style/preference rather than correctness, segment the signal or drop it from
accuracy metrics entirely.

---

## Confidence Score Pitfalls

If your agent emits confidence scores, watch for:

1. **Bucket crowding**: Models tend to commit at one threshold once they clear
   an evidence gate. A bimodal distribution (e.g., 90% of outputs at confidence=90)
   means the score reflects "passed the gate" not calibrated probability.

2. **Inverted calibration**: Higher stated confidence may correlate with *higher*
   dismiss rates if the model is more aggressive at high confidence. Verify
   empirically: plot dismiss rate by confidence bucket.

3. **Fix**: Build a calibration layer that maps model self-reported confidence
   to empirical resolution rates from historical data. Display the empirical rate
   to end users, not the raw model score.

---

## Common Agent Reasoning Failure Modes

### Log Noise Attribution
**Pattern**: Agent latches onto visible errors in failed runs without checking
if the same errors appear in passing runs.

**Fix**: Add a base-rate check to the reasoning prompt:
> "Does this signal appear equally often in passing and failing cases? If yes,
> it is probably not causal."

### Scope Confusion (Branch vs. Canonical State)
**Pattern**: Agent investigates a non-canonical state (draft branch, staging env,
temp config) and proposes fixes as if the canonical state is broken.

**Fix**: Before proposing any remediation, verify whether the broken state exists
on the canonical branch/environment. Gate auto-remediation on this check.

### Symptom vs. Cause Confusion
**Pattern**: Agent identifies a downstream effect (error message, metric spike)
as the root cause, missing an upstream infrastructure or environmental failure.

**Fix**: Prompt the agent to ask: "Is there a simpler upstream explanation
(infra, network, resource exhaustion) that would produce all of these symptoms?"

---

## Building the Eval Loop

When you lack a labeled dataset, use this loop instead:

1. **Flag bad sessions** via Tier 1 and Tier 2 signals
2. **Pull full session traces** (prompts, tool calls, tool responses, reasoning)
3. **Replay locally** against a model to find where reasoning broke down
4. **Categorize failure modes** (log noise, scope confusion, symptom/cause, etc.)
5. **Fix prompt or tool output** and re-run the flagged session
6. **Ship the fix**; add session to a regression set

**What you don't have yet (build this):**
A golden regression set that runs on every prompt change before it ships.
Without it, you catch regressions only on cases you've already seen.

---

## Latency as an Indirect Quality Signal

As agents scale (more context, more history per investigation):
- Median latency may stay stable while P95 climbs sharply
- P95 growth is structural: larger context windows per investigation
- Prompt caching and vectorized retrieval help but don't eliminate the trend
- Monitor P50 and P95 separately; treat P95 as a system health signal

---

## Multiple Correct Answers

When multiple outputs are all valid (different implementations, different
risk tolerances), standard accuracy metrics fail. Options:

- Have the agent classify its own output as **workaround** vs. **root-cause fix**
- Track outcome by classification separately
- Grade on *whether the agent's chosen class matches the team's context*,
  not on which specific fix was chosen

---

## What to Report

Instead of one accuracy number, report the signal stack with coverage:

| Signal | Count (period) | Coverage | What it measures |
|--------|---------------|----------|-----------------|
| Dismiss-as-invalid | N | N / total | Floor on wrong rate |
| User reassessment | N | N / total | Explicit corrections |
| System flip rate | N | N / reassessments | Self-correction rate |
| Action acceptance | N | N / actions opened | Fix-style + correctness |
| Explicit feedback | N | N / total sessions | Direct sentiment (low coverage) |

Report coverage honestly. A 0.88% floor on wrong rate from dismiss signals
is useful information; presenting it as "accuracy = 99.12%" is not.

---

## Checklist for a New Agent Eval System

- [ ] Instrument dismiss/invalid signal with one-click UX
- [ ] Instrument user-initiated reassessment (with free-text context field)
- [ ] Instrument system reassessment and track diagnosis flips
- [ ] Build confidence distribution dashboard; check for bucket crowding
- [ ] Sample 20+ rejected actions manually; categorize as correctness vs. preference
- [ ] Add base-rate check to agent reasoning prompt
- [ ] Add canonical-state scope check before auto-remediation
- [ ] Start a regression set from first flagged sessions
- [ ] Build calibration layer mapping confidence → empirical resolve rate
