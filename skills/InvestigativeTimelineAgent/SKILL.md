---
name: InvestigativeTimelineAgent
description: >
Stateful system for exploring, validating, and constructing grounded timelines from telemetry data (e.g., Elasticsearch). Assists analysts by following leads, expanding hypotheses, and producing traceable timelines.
---

# Investigative Timeline Agent

## 1. Purpose

The Investigative Timeline Agent is a stateful system designed to iteratively explore, validate,
and construct a grounded timeline of events from large-scale telemetry data (e.g., Elasticsearch).

It assists analysts by:

* Following leads from an initial query
* Expanding and validating hypotheses
* Producing a traceable, evidence-backed timeline
* Maintaining a structured investigation state

---

## 2. Architecture Overview

```
  Query (follow leads) ──┐
                         ▼
  Baseline timeline ──► OpenCode Agent ──► Enriched timeline (Markdown)
                         │    ▲
                         ▼    │
                        MCP   LLM
                         │
                         ▼
                    Elasticsearch
```

**Component roles (strict)**

| Component     | Role                                    | NOT responsible for                        |
|---------------|-----------------------------------------|--------------------------------------------|
| Agent         | Orchestration, state, loop control      | Reasoning, retrieval                       |
| LLM           | Hypothesis generation, query planning   | Factual truth, implicit causality          |
| MCP           | Tool abstraction layer                  | Query logic, evidence interpretation       |
| Elasticsearch | Ground truth (logs, events, telemetry)  | Nothing — all evidence originates here     |
| State store   | Persistent investigation state          | Rendering, reasoning                       |

> **Disambiguation**: "Agent" in this document refers exclusively to the deterministic
> orchestrator. It is *not* an autonomous LLM agent — the LLM is a subroutine.

---

## 3. Core Principles

### 3.1 Grounded Reasoning

* Every claim MUST be backed by one or more event IDs
* No free-form inference without explicit evidence linkage

### 3.2 Separation of Concerns

* Retrieval ≠ reasoning ≠ rendering
* Each stage is independently testable

### 3.3 Deterministic State Evolution

* Investigation state evolves via explicit, logged transitions
* No hidden memory inside the LLM
* All LLM outputs are treated as *proposals*, rejected if not schema-valid or not evidenced

### 3.4 Dual Output Format

* Canonical: JSON (machine-readable, diffable)
* View: Markdown (human-readable)

---

## 4. Data Models

### 4.1 Event

```json
{
  "event_id": "string",
  "timestamp": "datetime",
  "source_ip": "string",
  "destination_ip": "string",
  "process": "string",
  "raw": "object"
}
```

### 4.2 Evidence

```json
{
  "evidence_id": "string",
  "event_ids": ["string"],
  "query": "string",
  "confidence": 0.0
}
```

**Confidence formula:**

```
evidence.confidence = (matching_events / expected_events) * source_reliability_weight
```

Where:
- `matching_events`: events returned by the query that match the hypothesis predicate
- `expected_events`: estimated events based on baseline frequency (see §9)
- `source_reliability_weight`: per-index weight in `[0.5, 1.0]`, configured per deployment

### 4.3 Hypothesis

```json
{
  "hypothesis_id": "string",
  "description": "string",
  "status": "open | supported | rejected",
  "supporting_evidence": ["evidence_id"],
  "confidence": 0.0
}
```

**Confidence formula:**

```
hypothesis.confidence = weighted_mean(evidence.confidence for e in supporting_evidence)
                        * coverage_factor
```

Where `coverage_factor` penalizes hypotheses supported by a single evidence item:

```
coverage_factor = min(1.0, 0.5 + 0.1 * len(supporting_evidence))
```

A hypothesis with one evidence item is capped at 0.6 regardless of evidence confidence.

### 4.4 Lead

```json
{
  "lead_id": "string",
  "type": "ip | user | process | host",
  "value": "string",
  "source_evidence": ["evidence_id"],
  "priority": 0.0,
  "status": "unexplored | exploring | resolved",
  "created_at": "datetime",
  "ttl_iterations": 5
}
```

**Priority formula:**

```
lead.priority = max(e.confidence for e in source_evidence)
                * recency_factor(created_at)
                * type_weight[lead.type]
```

Where:
- `recency_factor = exp(-lambda * iterations_since_creation)`, λ = 0.3 (configurable)
- `type_weight` defaults: `{"ip": 1.0, "process": 0.9, "user": 0.8, "host": 0.7}`
- Leads with `priority < LEAD_PRIORITY_THRESHOLD` (default: 0.2) are pruned

### 4.5 Lead Graph

```json
{
  "nodes": ["lead_id"],
  "edges": [
    {
      "from": "lead_id",
      "to": "lead_id",
      "relation": "temporal | causal | correlated",
      "confidence": 0.0
    }
  ]
}
```

**Graph size control:**
- Max nodes: `MAX_GRAPH_NODES` (default: 200)
- On overflow: evict lowest-priority `resolved` nodes first, then lowest-priority `unexplored`
- `exploring` nodes are never evicted mid-iteration

### 4.6 Timeline Entry (Canonical)

```json
{
  "events": [
    {
      "timestamp": "datetime",
      "event_id": "string",
      "description": "string",
      "evidence_ids": ["string"],
      "confidence": 0.0,
      "type": "observed | inferred | uncertain"
    }
  ]
}
```

**Type assignment rules:**

| Type        | Criteria                                                   |
|-------------|------------------------------------------------------------|
| `observed`  | Directly present in raw logs; confidence ≥ 0.8            |
| `inferred`  | Supported by ≥ 2 independent evidence items; conf ≥ 0.5   |
| `uncertain` | Single evidence item, or confidence < 0.5                 |

---

## 5. Execution Loop

### 5.1 Overview

```
┌─────────────────────────────────────────────────────┐
│                  Investigation Loop                 │
│                                                     │
│  1. Hypothesis Generation  (LLM)                    │
│  2. Query Planning         (LLM)                    │
│  3. Retrieval              (MCP → Elasticsearch)    │
│  4. Evidence Validation    (Agent)                  │
│  5. Lead Graph Update      (Agent)                  │
│  6. Timeline Update        (Agent)                  │
│  7. Convergence Check      (Agent)  ──► DONE?       │
│         │                                  │        │
│         └──────────── loop ────────────────┘        │
└─────────────────────────────────────────────────────┘
```

### 5.2 Step 1 — Hypothesis Generation (LLM)

Input:
- current timeline
- lead graph
- unresolved leads (priority-sorted, top N)

Output (schema-validated):
- new hypotheses
- updated lead priorities

Constraints:
- must reference existing leads or evidence IDs — any hypothesis without a valid reference is **rejected**, not retried
- max new hypotheses per iteration: `MAX_HYPOTHESES_PER_ITER` (default: 5)

Validation: output parsed against `Hypothesis` schema via Pydantic; invalid items dropped and logged.

### 5.3 Step 2 — Query Planning (LLM)

Input:
- selected leads (priority ≥ threshold)
- current hypotheses (status: open)

Output (schema-validated):

```json
{
  "queries": [
    {
      "query": "process.name:taskhostw.exe AND source.ip:10.0.0.5",
      "rationale": "string",
      "target_lead_ids": ["lead_id"]
    }
  ]
}
```

Budget enforcement:
- max queries per iteration: `MAX_QUERIES_PER_ITER` (default: 10)
- max total queries per investigation: `MAX_TOTAL_QUERIES` (default: 200)
- queries exceeding budget are queued for next iteration, not dropped

### 5.4 Step 3 — Retrieval (MCP → Elasticsearch)

- Execute queries via MCP tool interface
- Return raw events
- MCP must return a structured error on timeout or unavailability; the agent retries once then marks the lead as `blocked`

**MCP tool contract:**

```json
{
  "tool": "elasticsearch_query",
  "input": { "query": "string", "index": "string", "max_results": 100 },
  "output": { "hits": ["Event"], "total": 0, "error": "string | null" }
}
```

### 5.5 Step 4 — Evidence Validation (Agent)

- Deduplicate events by `event_id`
- Assign `evidence_id` (deterministic: `sha256(sorted(event_ids) + query)`)
- Compute confidence per §4.2 formula
- Discard evidence below `MIN_EVIDENCE_CONFIDENCE` (default: 0.1)

### 5.6 Step 5 — Lead Graph Update (Agent)

- Extract new entities from validated events (IPs, users, processes, hosts)
- Add nodes; skip if graph at `MAX_GRAPH_NODES` and new lead priority < lowest existing node
- Add edges with relation and confidence
- Recompute priorities for all `unexplored` nodes
- Decay priorities: apply `recency_factor` to all nodes not touched this iteration

### 5.7 Step 6 — Timeline Update (Agent)

- Insert new events in strict temporal order
- Assign type per §4.6 rules
- Existing entries are NOT overwritten; a second evidence item for the same `event_id` upgrades the type (uncertain → inferred → observed) and updates confidence

### 5.8 Step 7 — Convergence Check (Agent)

Stop if **any** of the following:

| Condition                                | Parameter                          |
|------------------------------------------|------------------------------------|
| No new leads with priority ≥ threshold   | `LEAD_PRIORITY_THRESHOLD` = 0.2    |
| Hypothesis confidence delta < ε          | `CONVERGENCE_EPSILON` = 0.02       |
| Max iterations reached                   | `MAX_ITERATIONS` = 20              |
| Query budget exhausted                   | `MAX_TOTAL_QUERIES` = 200          |

"Hypothesis confidence delta" = mean absolute change in `confidence` across all open hypotheses since the previous iteration.

---

## 6. State Store

### 6.1 Schema

The state store holds the complete investigation state as a single versioned document:

```json
{
  "investigation_id": "string",
  "version": 0,
  "created_at": "datetime",
  "updated_at": "datetime",
  "hypotheses": { "hypothesis_id": Hypothesis },
  "evidence":   { "evidence_id":   Evidence   },
  "leads":      { "lead_id":       Lead       },
  "lead_graph": LeadGraph,
  "timeline":   Timeline,
  "queries_executed": ["string"],
  "iteration":  0
}
```

### 6.2 Access Pattern

- **Read**: full state loaded at the start of each iteration
- **Write**: full state written atomically at the end of each iteration (optimistic locking via `version`)
- **Concurrency**: single agent per investigation; parallel investigations use separate `investigation_id`s
- **Backend**: PostgreSQL JSONB (recommended for durability and diff queries) or SQLite for single-node deployments. Redis is appropriate only for the lead priority queue, not for full state.

### 6.3 State Transitions

All transitions are logged as append-only records:

```json
{ "iteration": 2, "type": "lead_added",   "lead_id": "...", "priority": 0.73 }
{ "iteration": 2, "type": "lead_pruned",  "lead_id": "...", "reason": "below_threshold" }
{ "iteration": 2, "type": "hyp_rejected", "hypothesis_id": "...", "reason": "no_evidence_ref" }
```

This log is the authoritative record for debugging and audit.

---

## 7. LLM Output Validation

All LLM outputs pass through a validation pipeline before use:

```
LLM response
    │
    ▼
JSON parse  ──► failure → log + discard
    │
    ▼
Pydantic schema validation  ──► failure → log + discard
    │
    ▼
Reference integrity check   ──► references non-existent lead/evidence? → discard
    │
    ▼
Accepted
```

- **No retries on validation failure** — the item is silently dropped and logged. Retrying
  on schema errors burns query budget and rarely improves output.
- Validation failures are surfaced in the convergence report so the analyst can tune prompts.

---

## 8. Constraints & Safeguards

### 8.1 No Orphan Claims

Every timeline entry MUST reference at least one `evidence_id`. The agent enforces this at
insertion time; entries without evidence references raise a hard error (not a warning).

### 8.2 Confidence Propagation

Evidence → hypothesis → timeline confidence is computed deterministically per the formulas
in §4. The LLM never writes confidence values directly.

### 8.3 Query Budgeting

| Parameter                 | Default | Notes                                   |
|---------------------------|---------|-----------------------------------------|
| `MAX_QUERIES_PER_ITER`    | 10      | Excess queries queued, not dropped      |
| `MAX_TOTAL_QUERIES`       | 200     | Hard stop; triggers convergence check   |
| `MAX_HYPOTHESES_PER_ITER` | 5       | Excess hypotheses discarded by priority |
| `MAX_GRAPH_NODES`         | 200     | Eviction policy: lowest-priority first  |
| `MAX_ITERATIONS`          | 20      | Hard stop                               |

All parameters are configurable per investigation at instantiation.

### 8.4 Infinite Loop Prevention

- Hard iteration cap (`MAX_ITERATIONS`) is enforced by the agent, not the LLM
- Lead priority decay (§4.4) ensures old unexplored leads lose priority over time
- `ttl_iterations` on Lead: a lead not explored within N iterations is auto-resolved as `stale`

---

## 9. Baseline Behavior

Baseline is used in confidence computation (§4.2) to distinguish anomalous from routine activity.

**Minimum viable baseline (required):**
- Per-index event frequency over the prior 7 days: `baseline_event_rate[index][hour_of_day]`
- Per-process execution frequency: `baseline_process_rate[process_name]`

**How it's consumed:**
```
expected_events = baseline_event_rate[index][current_hour] * time_window_seconds
```

If no baseline is available for an index, `source_reliability_weight` is set to 0.5 and the
evidence confidence is capped at 0.5, which prevents any single-source evidence from producing
`observed`-type timeline entries.

**Baseline computation** is outside the agent loop — it is precomputed and loaded at
investigation start. How it is computed (rolling average, percentile, ML model) is a deployment
concern and not prescribed here.

---

## 10. Output Formats

### 10.1 JSON (Primary)

Used for storage, further processing, and diffing investigations. Two investigations can be
diffed at the evidence level by comparing `evidence_id` sets.

### 10.2 Markdown (Rendered)

```markdown
## Investigation: <investigation_id>
Iterations: 4 | Queries executed: 37 | Leads resolved: 12 | Open hypotheses: 2

---

## Timeline

### 2026-03-03 10:12:01 — observed (confidence: 0.92)
- **Process execution**: taskhostw.exe
- **Source**: 10.0.0.5
- **Evidence**: EVT-123, EVT-124

### 2026-03-03 10:15:44 — inferred (confidence: 0.67)
- **Suspicious lateral movement**
- **Evidence**: EVT-130, EVT-131

---

## Open Hypotheses

| ID    | Description                        | Confidence | Status |
|-------|------------------------------------|------------|--------|
| H-004 | Exfiltration via 10.0.0.9:443      | 0.54       | open   |
| H-007 | Compromised service account        | 0.41       | open   |

---

## Convergence Report

Stopped at iteration 4: no new leads above priority threshold (0.2).
LLM validation failures: 2 hypothesis proposals rejected (missing evidence reference).
```

---

## 11. MCP Tool Interface

Every tool exposed via MCP must conform to this contract:

```json
{
  "tool_name": "string",
  "description": "string",
  "input_schema":  { ... },
  "output_schema": { ... },
  "error_schema": {
    "code": "timeout | not_found | permission_denied | unknown",
    "message": "string"
  }
}
```

The agent handles tool errors as follows:

| Error code         | Agent action                                   |
|--------------------|------------------------------------------------|
| `timeout`          | Retry once; then mark lead as `blocked`        |
| `not_found`        | Log; discard query; continue                   |
| `permission_denied`| Halt investigation; surface to analyst         |
| `unknown`          | Retry once; then halt iteration                |

**Future tools** (threat intel, SIEM, UEBA) plug in here without changes to the agent loop,
provided they implement this contract.

---

## 12. Failure Modes & Mitigations

| Failure mode                          | Root cause                              | Mitigation                                            |
|---------------------------------------|-----------------------------------------|-------------------------------------------------------|
| Infinite exploration loop             | Convergence never triggered             | Hard iteration + query caps (§8.3)                   |
| False causality chains                | LLM proposes unsupported causal edges   | Reference integrity check (§7); causal edges require ≥ 2 independent evidence items |
| Overconfidence from sparse evidence   | Single evidence drives timeline         | `coverage_factor` in hypothesis confidence (§4.3); `observed` requires conf ≥ 0.8 |
| Lead graph explosion                  | Too many extracted entities             | `MAX_GRAPH_NODES` + eviction policy (§4.5)           |
| LLM hallucination                     | Model invents event IDs or IPs          | Schema validation + reference integrity check (§7)   |
| Latency explosion                     | Unbounded MCP + LLM chaining            | Per-iteration query cap; MCP timeout enforcement (§5.4) |
| Stale investigation                   | Old leads never resolved                | `ttl_iterations` lead expiry (§8.4)                  |

---

## 13. Implementation Stack

| Layer         | Component                  | Notes                                              |
|---------------|----------------------------|----------------------------------------------------|
| Agent loop    | Python                     | Pydantic for all LLM output validation             |
| Data store    | Elasticsearch              | Source of truth; never written by the agent        |
| Tool layer    | MCP                        | One tool per data source; contract in §11          |
| Reasoning     | LLM API (any OpenAI-compat)| JSON/structured output mode required               |
| State store   | PostgreSQL JSONB            | SQLite for single-node; Redis for priority queue   |
| State logging | Append-only transition log  | Postgres table or file; never truncated            |

---

## 14. Open Questions (Deliberately Unresolved)

* Should lead priority incorporate graph centrality (hubs vs. leaves)?
* Can the LLM propose edge *deletions* from the lead graph (to correct false causality)?
* Should reinforcement learning guide query selection over multiple investigations?
* How should multi-tenancy affect the state store schema (investigation namespacing)?
* When two independent evidence items contradict each other, how is confidence resolved?

---

## 15. Summary

This system is a constrained reasoning engine over telemetry data.

* **Elasticsearch** provides truth — no evidence exists outside it
* **The agent** enforces structure and loop control — deterministically
* **The LLM** proposes hypotheses and queries — never decides
* **Evidence** is the only authority — every claim must reference it
* **Confidence** is computed, not asserted — formulas in §4 are the source of truth
