---
name: failure-modes
description: >
  Systematically identify, classify, and analyze failure modes for any system,
  process, design, algorithm, or plan. Use this skill whenever the user wants to
  find ways something can break, go wrong, fail silently, degrade, be exploited,
  or produce incorrect results — even if they phrase it as "what could go wrong",
  "find weaknesses", "stress-test this", "where are the edge cases", "audit for
  bugs", "threat model", or "what am I missing". Trigger on any request to
  analyze robustness, reliability, correctness, security, or resilience of any
  artifact — code, architecture, protocol, plan, algorithm, hardware design,
  or business process. Also trigger when the user shares something and asks for
  critical feedback or a devil's advocate perspective.
---

# Failure Mode Analysis Skill

A structured methodology for finding, classifying, and communicating failure modes
in any artifact — from code and distributed systems to algorithms, protocols,
plans, and hardware designs.

---

## When to Use This Skill

- "What could go wrong with X?"
- "Find failure modes / edge cases / weaknesses in X"
- "Stress-test / audit / threat-model this"
- "Where can this break / fail silently / be exploited?"
- "What am I missing?" (when reviewing a design or plan)
- Any robustness, reliability, correctness, or security review

---

## Core Methodology

### 1. Classify the Artifact

Before enumerating failures, identify what kind of artifact you're analyzing.
Different artifact types have distinct failure mode taxonomies:

| Artifact Type        | Primary Taxonomy to Apply                     |
|----------------------|-----------------------------------------------|
| Code / algorithm     | Correctness, edge cases, complexity, concurrency |
| Distributed system   | Partial failure, consistency, latency, split-brain |
| Security protocol    | Cryptographic, authentication, authorization, side-channel |
| Data pipeline        | Corruption, drift, schema mismatch, ordering  |
| Hardware / firmware  | Timing, power, thermal, wear-out              |
| Business process     | Incentive misalignment, dependency, human error |
| Plan / strategy      | Assumption violations, unknown unknowns, cascading |

If the artifact spans multiple types, apply multiple taxonomies.

---

### 2. Enumerate Failure Modes

For each category relevant to the artifact, systematically ask the failure
induction questions below.

#### Universal Questions (apply to every artifact)

1. **Boundary conditions**: What happens at empty input, zero, MAX_INT, null,
   empty string, single element, duplicate elements?
2. **Concurrency / ordering**: What if two events arrive simultaneously?
   What if event B arrives before event A?
3. **Resource exhaustion**: What if memory, disk, CPU, file descriptors, or
   connections are exhausted?
4. **Partial failure**: What if a sub-component fails mid-operation?
   Is state left consistent or corrupted?
5. **Adversarial input**: What happens with malformed, malicious, or
   unexpected input?
6. **Silent failure**: Can this succeed but produce wrong results with no error?
7. **Dependency failure**: What if an external dep (DB, API, clock, RNG) fails
   or misbehaves?
8. **State machine violation**: Can the system be driven into an invalid state?
9. **Assumption violation**: What assumptions does the design make that could
   be wrong in production?
10. **Cascading failure**: Can a localized fault propagate and amplify?

#### Taxonomy-Specific Questions

<details>
<summary>Code / Algorithm</summary>

- Off-by-one errors in loops, array indexing, slice bounds
- Integer overflow/underflow (especially in size/offset calculations)
- Floating-point precision loss, NaN/Inf propagation
- Uninitialized variables or use-after-free (memory-unsafe languages)
- Exception not caught → unchecked propagation or silent swallow
- Race conditions, TOCTOU (time-of-check / time-of-use)
- Algorithmic complexity blowup on adversarial input (quadratic, exponential)
- Incorrect memoization / cache invalidation
- Recursion depth → stack overflow
- Incorrect handling of Unicode, encoding, or locale
</details>

<details>
<summary>Distributed System</summary>

- Network partition (split-brain, conflicting writes)
- Clock skew / NTP drift causing ordering bugs
- Retry storm / thundering herd on recovery
- Message duplication (at-least-once delivery without idempotency)
- Replication lag causing stale reads
- Leader election loop / split votes
- Configuration drift between nodes
- Backpressure absent → upstream buffer overflow
- Cascading timeout → entire call graph stalls
- Inconsistent serialization across versions (rolling deploy)
</details>

<details>
<summary>Security / Cryptographic Protocol</summary>

- Nonce reuse invalidating semantic security
- Timing side-channel leaking key material
- Padding oracle, CBC bit-flip, length-extension attacks
- Weak RNG seeding (low entropy at boot)
- Missing signature verification or algorithm confusion (e.g., RS256→HS256)
- Replay attack (missing nonce or timestamp check)
- Downgrade attack (negotiation to weaker cipher/version)
- Trust anchor confusion (certificate pinning bypass, CA compromise)
- SSRF, path traversal, injection via untrusted input
- Secret material in logs, error messages, or coredumps
</details>

<details>
<summary>Data Pipeline</summary>

- Schema drift upstream causes silent type coercion or dropped fields
- Out-of-order events → incorrect windowed aggregations
- Duplicate records → inflated metrics
- NULL / missing value propagation into downstream models
- Timezone/DST ambiguity in timestamp handling
- Large files causing OOM in streaming contexts
- Backfill invalidating downstream caches or aggregates
- PII leaking into debug logs or sample exports
</details>

<details>
<summary>Plan / Strategy</summary>

- Single point of failure (key person, single vendor, single region)
- Optimistic schedule with no slack for unknowns
- Dependency on external approval/resource not yet secured
- Incentive misalignment between stakeholders
- Metric being optimized is a proxy that diverges from real goal
- Plan assumes current environment; black-swan events invalidate it
- Reversibility: what's the rollback if this fails midway?
</details>

---

### 3. Score and Prioritize

For each identified failure mode, produce a brief risk assessment:

```
Failure: <one-line description>
Category: <taxonomy label>
Likelihood: Low | Medium | High
Impact: Low | Medium | High | Critical
Detectability: Easy | Hard | Silent
Risk = Likelihood × Impact (qualitative: Low / Medium / High / Critical)
Mitigation: <concrete fix or safeguard>
```

Sort output by **Risk** descending. Focus prose on High/Critical items.

---

### 4. Output Format

Default to a structured report:

```
## Failure Mode Analysis: <artifact name>

### Summary
<2-3 sentence overview of the artifact and its main risk surface>

### High / Critical Risk Failures
<numbered list, each with Score card>

### Medium Risk Failures
<numbered list, abbreviated score cards>

### Low Risk Failures (brief)
<bulleted list>

### Key Mitigations
<top 3-5 actionable recommendations>

### Assumptions Made
<what you assumed about the operational context, language, threat model, etc.>
```

Adjust verbosity to the user's apparent depth of interest:
- Quick scan → just High/Critical with one-line mitigations
- Deep audit → full report with all three tiers
- Code review → inline comments alongside the report

---

## Tips for High-Quality Analysis

- **Read the actual artifact** (code, design doc, pseudocode) before applying
  heuristics — pattern-matched heuristics without reading produce noise.
- **Distinguish silent from loud failures** — silent correctness failures are
  often far more dangerous than crashes.
- **Explicitly state your threat model** — an internal tool and an
  internet-facing service have different adversarial failure modes.
- **Prioritize ruthlessly** — a 20-item list of equal severity is useless.
  Force-rank the top 3.
- **Pair each failure with a concrete mitigation** — observation without
  remediation has limited value.
- **Note what you didn't analyze** — scope boundaries prevent false confidence.
