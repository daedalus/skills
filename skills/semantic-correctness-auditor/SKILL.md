---
name: semantic-correctness-auditor
description: >
  A unified framework for auditing code, systems, and skill sets against the limits
  of what can be mechanically verified. Combines Rice's Theorem analysis, emergent
  fairness simulation, and insight operationalization into a single workflow.

  Trigger on ANY of these: "are my tests enough?", "is this correct?", "will this
  always work?", "is this fair?", "why does my code pass tests but fail in
  production?", "can AI verify this?", "turn this article into a skill", "audit my
  skills", "do my skills work together?", "why isn't my skill triggering?",
  "I want Claude to remember this workflow."

  Also trigger when the user shares: a scheduler, load balancer, assignment algorithm,
  rotation system, or any code whose correctness depends on long-run emergent behavior.
  Or when they share a URL/article and want it captured as reusable knowledge.
  Or when they have a collection of skills and want to know if they cover the right
  ground and trigger reliably.

  When in doubt, use this skill. It is designed to be the meta-layer that sees what
  individual tools cannot.
---

# Semantic Correctness Auditor

## Core insight

Rice's Theorem (1953) proves that no algorithm can decide any non-trivial semantic
property of programs — anything about what a program *does*, not just what it *looks
like*. This is not a temporary limitation of tooling or AI capability. It is a
mathematical ceiling that applies equally to humans, machines, and AI agents.

Below that ceiling is enormous useful space. This skill operates there — not claiming
perfect verification, but systematically mapping what can be checked, what can be
simulated, and what must be accepted as irreducibly uncertain.

The same principle applies beyond code: to skill sets, workflows, and any system
whose correctness depends on emergent behavior over time.

---

## When to use which mode

Read the user's request, then select the appropriate mode (or combine):

| Situation | Mode |
|---|---|
| User shares code and asks if it's correct / tested well enough | **A: Semantic Property Analysis** |
| Code involves assignment, scheduling, rotation, or distribution | **B: Emergent Fairness Simulation** |
| User shares a URL, article, or methodology to capture | **C: Insight Operationalization** |
| User has 2+ skills and wants to know if the set works | **D: Skill Set Audit** |
| Any combination of the above | **Run all relevant modes, synthesize at the end** |

---

## Mode A: Semantic Property Analysis

### 1. Classify properties

For the given code, identify all correctness properties and label each:

- ✅ **Decidable** — type checks, syntax, null safety, format
- ⚠️ **Partially testable** — sampled but not exhaustively provable
- ❌ **Undecidable (Rice)** — no general algorithm can verify this

Common undecidable properties: fairness, termination, intent alignment, long-run
correctness, resource bounds, emergent system behavior.

### 2. Audit existing tests

For each test: what property does it cover? Does it create a false sense of
completeness — passing while an undecidable property fails silently?

### 3. Identify hidden assumptions

Where does correctness depend on: inputs staying in expected ranges? State not
accumulating? Fairness only visible over many runs? Rules that look correct
individually but interact badly?

### 4. Output: Semantic Property Report

```
## Semantic Property Report

### Decidable (mechanical verification sufficient)
- [list]

### Undecidable properties present
- [property]: [why undecidable] [what tests miss] [failure mode]

### Recommended verification strategies
- Simulation: run N iterations, observe distribution
- Property-based testing: random valid inputs, check invariants
- Formal specification: define "correct" precisely before coding
- Human review focus: specification–intent gap

### What no reviewer (human or AI) can guarantee
- [honest statement]
```

---

## Mode B: Emergent Fairness Simulation

### 1. Map the system

- Who/what are the participants?
- What is being distributed?
- What constraints exist? (availability, cooldowns, consecutive limits)
- What does "fair" mean here? (equal count? proportional to capacity?)
- What time horizon reveals the true distribution?

### 2. Identify fairness-breaking risk factors

| Pattern | Risk |
|---|---|
| Asymmetric availability | Constrained participants under-assigned; catch-up logic too weak |
| Cooldown + priority interaction | Temporarily depresses frequent assignees, masking dominance |
| Small eligible pools | Same few participants rotate indefinitely |
| Greedy local optimality | Each assignment looks fair; cumulative distribution does not |
| Edge case starvation | Rarely-eligible participant never triggers catch-up |

### 3. Simulate

Run the algorithm for at least 4–8× the natural rotation period with realistic
constraint profiles. Track cumulative counts. Measure spread vs. ideal.
Flag as unfair if spread exceeds ~15% of ideal.

### 4. Output: Fairness Report

```
## Fairness Audit Report

### Simulation parameters
- Participants: [list with constraints]
- Simulation length: [X weeks / Y iterations]

### Distribution results
| Participant | Assignments | % of total | vs. ideal |

Spread: [min] to [max] (delta: [N])
Verdict: ✅ FAIR / ⚠️ BORDERLINE / ❌ UNFAIR

### Root cause
[Why the unfairness emerged — which rule interactions caused it]

### Fix recommendations (ranked by invasiveness)
1. [least invasive]
2. ...
```

---

## Mode C: Insight Operationalization

Turn an article, paper, or methodology into a Claude-executable skill.

### 1. Extract

- **Core insight / thesis** — the central claim
- **Workflow steps** — repeatable process
- **Decision criteria** — when to use this vs. alternatives
- **Key terms** — vocabulary needed to apply it
- **Pitfalls** — what the source warns against
- **Examples** — concrete illustrations

### 2. Determine skill shape

| Source type | Skill shape |
|---|---|
| Tutorial / how-to | Step-by-step workflow |
| Theorem / research finding | Analysis framework + report format |
| Design pattern | When-to-use guide + checklist |
| Opinion / essay | Mental model + reasoning prompts |

### 3. Identify trigger contexts

Ask: what would a user type *before* knowing this article exists?
Write triggers that meet users where they are, not at the article's vocabulary.

### 4. Quality checks

- [ ] Triggers match real user phrasings, not just the article's title?
- [ ] Workflow is executable, not just a summary?
- [ ] Key terms defined without assuming the user read the source?
- [ ] Output format specified consistently?
- [ ] Under ~500 lines? If not, split into SKILL.md + references/

### 5. Critical distinction

A skill is not a summary. It is an instruction set. Abstract principles must become
concrete steps. The test: can Claude apply this methodology in a novel context
*without* seeing the source material?

---

## Mode D: Skill Set Audit

Apply the full framework to a collection of skills as a unified system.

### 1. Map trigger surfaces

For each skill: broad / medium / narrow eligibility across realistic user prompts.

### 2. Find the "Cara"

Identify the high-value, low-trigger skill — the one that is conceptually distinctive
but requires users to already be near the right framing before it activates.
This skill will be systematically under-assigned. It is correct, available, and
mostly idle.

### 3. Simulate distribution

Estimate trigger frequency across a realistic population of 100 prompts.
Flag imbalance if any skill gets <15% of triggers while others exceed 40%.

### 4. Check the set's combined promise

Is the skill set's collective goal itself an undecidable semantic property?
(If yes — it almost always is — state this honestly and note what simulation
and human review can do in place of formal verification.)

### 5. Recommend

- Strengthen narrow triggers to meet users earlier in their thinking
- Add a routing/meta skill if the set has 3+ skills with overlapping domains
- Merge skills that are too similar to differentiate in practice
- Note if the set's *interaction effects* produce gaps none of the individual
  skills can see — and whether a new skill is needed to cover that gap

---

## Synthesis step (when multiple modes apply)

After running relevant modes, always close with:

```
## Unified Finding

### What this system can verify
[Decidable properties, testable behaviors, simulatable distributions]

### What this system cannot verify (Rice's ceiling)
[Honest enumeration of undecidable properties]

### The specification–intent gap
[Where the hardest problems live in this specific case]

### What changes would move the most
[Top 1–3 highest-leverage recommendations]
```

---

## Foundational principles

**On verification:** More tests = more confidence, never perfect certainty. The goal
is not to eliminate the undecidable gap but to know exactly where it is.

**On fairness:** A program can follow every rule, pass every test, and produce a
deeply unfair outcome. Emergent behavior requires simulation, not inspection.

**On operationalization:** The gap between *specification* and *intent* is where hard
bugs live. Closing it requires human understanding that transfers across problems —
something today's AI accumulates imperfectly at best.

**On self-application:** Any system built to catch correctness gaps has its own
undecidable properties. This skill is no exception. Its effectiveness — whether it
changes how users think about verification, not just what they produce — cannot be
mechanically verified. That is not a reason to distrust it. It is a reason to use
simulation, iteration, and human judgment alongside it.
