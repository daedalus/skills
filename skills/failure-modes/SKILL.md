---
name: failure-modes
version: 2.0
description: >
  Systematically identify, classify, and analyze failure modes for any system,
  process, design, algorithm, or plan. Use this skill whenever the user wants to
  find ways something can break, go wrong, fail silently, degrade, be exploited,
  or produce incorrect results — even if they phrase it as "what could go wrong",
  "find weaknesses", "stress-test this", "where are the edge cases", "audit for
  bugs", "threat model", or "what am I missing". Trigger on any request to
  analyze robustness, reliability, correctness, security, or resilience of any
  artifact — code, architecture, protocol, plan, algorithm, AI/LLM system,
  hardware design, or business process. Also trigger when the user shares
  something and asks for critical feedback or a devil's advocate perspective.
---

# Failure Mode Analysis Skill

A structured methodology for finding, classifying, and communicating failure modes
in any artifact — from code and distributed systems to algorithms, protocols,
plans, AI/LLM pipelines, and hardware designs.

---

## HARD GATE — Read Before Proceeding

**If the artifact to analyze is not in your context, stop and request it now.**
Do not apply heuristics to a description of an artifact. Hallucinated findings
are worse than no findings. Get the actual artifact first.

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

Identify which artifact types apply. Apply all matching taxonomies.

| Artifact Type          | Primary Taxonomy to Apply                                  |
|------------------------|------------------------------------------------------------|
| Code / algorithm       | Correctness, edge cases, complexity, concurrency           |
| Distributed system     | Partial failure, consistency, latency, split-brain         |
| Security protocol      | Cryptographic, authentication, authorization, side-channel |
| AI / LLM system        | Prompt injection, poisoning, tool-call abuse, evasion      |
| Data pipeline          | Corruption, drift, schema mismatch, ordering               |
| Hardware / firmware    | Timing, power, thermal, wear-out, supply chain             |
| Business process       | Incentive misalignment, dependency, human error            |
| Plan / strategy        | Assumption violations, unknown unknowns, cascading         |
| Unknown / novel        | Decompose into constituent types; flag uncovered surface   |

---

### 2. Enumerate Failure Modes

#### Universal Questions (apply to every artifact)

1. **Boundary conditions** — empty input, zero, MAX_INT, null, single element, duplicates
2. **Concurrency / ordering** — simultaneous events, out-of-order arrival
3. **Resource exhaustion** — memory, disk, CPU, file descriptors, connections
4. **Partial failure** — sub-component fails mid-operation; is state consistent?
5. **Adversarial input** — malformed, malicious, or unexpected input
6. **Silent failure** — succeeds but produces wrong results with no error signal
7. **Dependency failure** — external dep (DB, API, clock, RNG) fails or misbehaves
8. **State machine violation** — can the system be driven into an invalid state?
9. **Assumption violation** — what assumptions could be wrong in production?
10. **Cascading failure** — can a localized fault propagate and amplify?

#### Code / Algorithm

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

#### Distributed System

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

#### Security / Cryptographic Protocol

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

#### AI / LLM System

- Prompt injection via user input, RAG documents, or tool results
- Context poisoning — adversarial content shifts model behavior across turns
- Tool-call forgery — model tricked into calling unintended tools or args
- Jailbreak / goal hijacking via system-prompt override attempts
- Hallucination used as a trusted fact by downstream consumers
- Multi-turn state erosion — early instructions forgotten or overridden
- Excessive agency — model takes irreversible actions without confirmation
- Training data leakage via memorization or extraction attacks
- Denial-of-service via unbounded context growth or recursive tool calls
- Eval gaming — model learns to pass evals without achieving real objective

#### Data Pipeline

- Schema drift upstream causes silent type coercion or dropped fields
- Out-of-order events → incorrect windowed aggregations
- Duplicate records → inflated metrics
- NULL / missing value propagation into downstream models
- Timezone/DST ambiguity in timestamp handling
- Large files causing OOM in streaming contexts
- Backfill invalidating downstream caches or aggregates
- PII leaking into debug logs or sample exports

#### Hardware / Firmware

- Setup/hold time violations at temperature or voltage extremes
- Wear-out: flash write endurance, capacitor aging, contact oxidation
- Interrupt latency spikes causing missed deadlines
- Supply chain: counterfeit components with differing specs
- Power sequencing errors on reset / cold boot
- Covert storage in HPA, DCO, or vendor-reserved sectors

#### Business Process

- Single point of failure: key person, single vendor, single region
- Undocumented tribal knowledge lost on personnel change
- Incentive misalignment between teams or stakeholders
- Manual step in an otherwise automated flow → human error
- Audit trail gaps preventing incident reconstruction

#### Plan / Strategy

- Optimistic schedule with no slack for unknowns
- Dependency on external approval/resource not yet secured
- Metric being optimized is a proxy that diverges from real goal
- Plan assumes current environment; black-swan events invalidate it
- Reversibility: no rollback path if this fails midway

---

### 3. Score and Prioritize

For each finding, score on three dimensions (1–3) and compute priority:

```
Failure:       <one-line description>
Category:      <taxonomy label>
Likelihood:    1-Low | 2-Medium | 3-High
Impact:        1-Low | 2-Medium | 3-High | 4-Critical
Detectability: 1-Easy | 2-Hard | 3-Silent
Priority:      Likelihood + Impact + Detectability  (max 10)
Mitigation:    <concrete fix or safeguard>
```

Sort by **Priority descending**. Ties broken by Detectability (Silent first).
Focus prose on Priority ≥ 8.

Default threat model (override if user specifies): opportunistic external
attacker + accidental misuse by authorized users.

---

### 4. Output Format

```
## Failure Mode Analysis: <artifact name>

### Summary
<2-3 sentences: what the artifact does and its primary risk surface>

### High Priority Failures  (score ≥ 8)
<numbered list, full score card per finding>

### Medium Priority Failures  (score 5–7)
<numbered list, abbreviated score cards>

### Low Priority Failures  (score ≤ 4)
<bulleted list, one line each>

### Key Mitigations
<top 3–5 actionable recommendations, priority-ordered>

### Assumptions Made
<operational context, threat model, scope boundaries, what was NOT analyzed>
```

Adjust verbosity to context:
- Quick scan → High only, one-line mitigations
- Deep audit → all tiers, full score cards
- Code review → inline annotations + summary report

---

## Tips for High-Quality Analysis

- **Distinguish silent from loud** — silent correctness failures are often
  far more dangerous than crashes. Penalize them in Detectability.
- **Prioritize ruthlessly** — force-rank; a flat list of 20 equal findings
  is useless. The top 3 should be unambiguous.
- **Pair each failure with a concrete mitigation** — observation without
  remediation has limited value.
- **State what you didn't cover** — explicit scope boundaries prevent false
  confidence more than any checklist.
