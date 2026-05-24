---
name: alphaproof-nexus
description: >
  Knowledge scaffold for building, using, or reasoning about AlphaProof Nexus —
  Google DeepMind's LLM-aided formal proof search system (arXiv:2605.22763).
  Always use this skill for ANY of the following: AI-driven theorem proving in
  Lean 4, reproducing or extending the AlphaProof Nexus agent architecture,
  solving open mathematics problems with formal verification, integrating
  evolutionary algorithms with LLM proof search, applying the system to Erdős
  problems / OEIS conjectures / algebraic geometry / optimization / graph
  theory, understanding the EVOLVE-BLOCK / EVOLVE-VALUE prompt interface,
  comparing the four agent configurations (A/B/C/D), or the Elo/P-UCB sketch
  rating mechanism. Also trigger for adjacent queries like "automate math
  research with AI", "connect Lean compiler feedback to an LLM loop",
  "cheapest way to prove hard math with AI", "reproduce a DeepMind theorem
  prover", "LLM + formal verification pipeline", or anything about AlphaProof,
  AlphaEvolve applied to proofs, or the Formal Conjectures benchmark.
---

# AlphaProof Nexus — Skill

## Overview

AlphaProof Nexus is a framework from Google DeepMind (May 2026, arXiv:2605.22763)
that combines frontier LLMs with the Lean 4 proof assistant and an optional
evolutionary search layer to autonomously solve open mathematics research problems.
Key results: 9/353 open Erdős problems solved, 44/492 OEIS conjectures proved,
plus contributions to algebraic geometry, convex optimization, graph theory, and
quantum optics — all at a cost of a few hundred USD per problem.

---

## Core Concepts

### Lean 4 as Verifier
- Every proof step is machine-checked; no hallucinations can silently survive.
- The `sorry` tactic closes goals without proof — a solved problem has **zero** `sorry` occurrences.
- The Lean compiler returns structured error messages reused as LLM feedback.

### Proof Sketch Interface
The user supplies a `.lean` file with:
- The **target theorem** (with `sorry` as placeholder) — **never modified by the agent**.
- `-- EVOLVE-BLOCK-START / END` markers: regions the agent may rewrite freely (helper lemmas, definitions, tactic blocks).
- `-- EVOLVE-VALUE-START / END` markers: single scalar expressions or answer terms (e.g., `True`/`False`, a numerical bound, an algorithm step-size) the agent may substitute. Not for arbitrary code — use EVOLVE-BLOCK for that.
- Optional natural-language context and domain knowledge encoded in Lean.

The agent outputs a `sorry`-free proof inside those markers, touching nothing else.

**OEIS / sequence conjectures**: Before attempting the main conjecture, require the agent to prove "test lemmas" that verify the first few terms of the sequence against its formal definition. This guards against misformalization silently producing a trivially-provable but wrong statement.

---

## Agent Architecture (A → D)

| Agent | Core loop | AlphaProof tool | Evolution |
|-------|-----------|-----------------|-----------|
| **(A) Basic** | Ralph loop (multi-turn LLM + search-replace + Lean compiler) | ✗ | ✗ |
| **(B) Basic + AP** | Same as A | ✓ | ✗ |
| **(C) Basic + Evolution** | Shares population DB; Elo-rated sketches | ✗ | ✓ |
| **(D) Full** | All of the above; coordinates via P-UCB sampling | ✓ | ✓ |

**Default recommendation**: Use **(B)** for most problems (cost-efficient, high solve rate). Use **(D)** for problems where simpler agents plateau (e.g., Erdős #125 required the evolutionary layer for reliable convergence). **Avoid (C) alone** — evolution without AlphaProof is generally dominated by (A)/(B) on both cost and solve rate; the evolutionary machinery only pays off when combined with AlphaProof in (D).

### Ralph Loop (Basic subagent)
```
episode:
  LLM session (Gemini 3.1 Pro, chain-of-thought)
    ↓ search_replace tool → edit sketch
    ↓ Lean compiler → error / success feedback
    ↓ repeat until budget or sorry-free
  if still sorry: write lessons-learned comment → next episode
```
N subagents run **independently in parallel**; first success terminates all others.

### Full Agent (D) Controller Loop
1. **DB sampling** — select root sketch S_root + 2 inspiration sketches via P-UCB.
2. **Prompt assembly** — problem spec + Lean source + prior AlphaProof feedback + diversity injection ("decompose unsolved goals", "try new approach", …).
3. **Prover subagent** — multi-turn LLM episode; can call AlphaProof mid-episode (max 5 calls, 90 search-replace edits per episode).
4. **Validation** — SafeVerify checks: no axiom injection, no altered theorem statement, proof compiles.
5. **DB registration** — sketch + AlphaProof subgoal feedback added; Elo updated asynchronously by rater subagents.

### AlphaProof Integration
- Called with unsolved Lean subgoals; returns **proof** / **disproof** / **failure message**.
- Runs in low-compute tree-search inference mode (~400 simulations, bounded RPC timeout).
- **Global goal cache**: subgoals hashed by exact Lean state; proven/disproven results reused across the population without re-querying.
- Estimated cost: ~$60 USD per problem on v6e TPUs (not included in reported LLM costs).

### Elo Rating System
- Rater subagents (Gemini 3.0 Flash) run P=7-sketch tournaments continuously.
- Ranking model: Plackett-Luce with hierarchical Gamma prior; Gibbs sampling (I=1000, B=200 burn-in).
- Elo formula: `Elo = 1200 + 400·log10(λ_mean)`
- Criteria (descending priority): strategic robustness & generalizability, decomposition quality of remaining `sorry` gaps, logical correctness.
- **Key rater insight**: "AlphaProof failure ≠ bad sketch." A sketch with well-chosen `sorry` gaps beats one with no gaps but a dead-end strategy.

### P-UCB Sampling
```
score = q + c · sqrt(ΣV_i / (v + 1))
```
- `q` = Elo normalized to [0,1] over top-64 sketches.
- `v` = visit count for this sketch; `ΣV_i` = total visits in elite tier.
- `c = 0.2` (empirically tuned).
- Prevents collapse to a single lineage while exploiting top candidates.

---

## Cost & Scaling Guidelines

| Config | Parallel subagents K | Typical cost range | Best for |
|--------|---------------------|-------------------|----------|
| A/B (K=1–10) | Independent reruns | $10–$600 | Easy–medium problems |
| D (K=10) | 10 async generators | $50–$1000+ | Hard problems |

- Per-problem cost has **high variance** (stochastic search); budget for 3–5× median.
- Exploring all 353 Erdős problems to identify tractable ones was itself a large compute investment — factor this into project planning.
- Smaller models (Gemini 3.0 Flash, Gemini 3.1 Flash-Lite) as provers: **0/9 Erdős problems solved** — don't substitute for 3.1 Pro on the prover.
- AlphaProof standalone tree search (64 TPU-hours/problem): **0/9 solved** — needs LLM orchestration.

---

## Prompt Engineering Notes

### Prover Subagent Prompt (Agent D) — Key Directives
- Think like a mathematician: focus on key insights, not brute-force casework.
- Decompose hard subgoals into simpler lemmas *before* calling AlphaProof — monolithic goals fail.
- Use `have` for intermediate steps; `let` for local definitions.
- Aim for 8–10 `search_replace` calls per episode; use them exhaustively.
- Never use a single `sorry` to cover multiple reasoning steps.
- Write Lean comments (`--`) explaining high-level intuition alongside each step.
- Do NOT add `import` statements — Mathlib is loaded by default.

### Rater Prompt — Key Directives
- Rank from best to worst using `<decision>2 > 1 = 3</decision>` format.
- Penalize "overfitting" (brute-force computation that won't generalize).
- Reward diversity of strategy across the population.
- Ignore timeouts/service errors in feedback.

### Basic Agent Prompt — Key Directives
- George Dantzig framing: approach with confidence, as if the problem is solvable.
- Never end a session with non-compiling code.
- If stuck, explore specializations/generalizations as helper lemmas for insight.
- All findings/plans go as Lean comments — only file content persists to the next episode.

---

## Proven Results by Domain

| Domain | Result |
|--------|--------|
| **Erdős Problems** | 9/353 solved (incl. two open since 1970: #12(i), #12(ii)) |
| **OEIS** | 44/492 open conjectures proved |
| **Optimization** | O(1/t) convergence of Anchored GDA (agent simultaneously found proof + novel learning schedule) |
| **Graph Theory** | Bipartite reconstruction conjecture variant; Graffiti conjecture #2 (spanning tree leaves) |
| **Algebraic Geometry** | Log-concavity of pure O-sequences, codimension 3 type 2 (open ~15 years) |
| **Additive Combinatorics** | Counterexample to Green's problem #57 (complex-valued case) |
| **Quantum Optics** | Monochromatic quantum graph existence for N=d∈{4,6,10} |

---

## Known Failure Modes

1. **Circular sorry**: Agent offloads core difficulty into a helper lemma that simply restates the target. Explicit prompting against this helps but doesn't eliminate it.
2. **Hallucinated lemmas**: Agent cites non-existent established results as `sorry`-ed lemmas. End-to-end formal verification is the only reliable filter.
3. **Misformalization**: Ambiguous natural-language terms (e.g., "density" vs. "lower density" vs. "upper density") can lead to wrong Lean statements. Agent can serve as a diagnostic tool — if it proves the wrong version easily, check the formalization.
4. **Scope limitation**: Current successes concentrated where Mathlib is mature (combinatorics, number theory, convex optimization). Problems requiring extensive new theory remain out of reach.

---

## Implementation Details

- **Language**: Python with `asyncio`; Docker sandboxes for Lean compilation (Lean v4.27 + Pantograph).
- **Lean interface**: Pantograph for stateful proof interaction; SafeVerify for final integrity checks.
- **LLM backend**: Gemini 3.1 Pro (prover), Gemini 3.0 Flash (rater).
- **Code repo**: https://github.com/google-deepmind/alphaproof-nexus-results

---

## Quick Reference: EVOLVE Marker Usage

```lean
-- EVOLVE-BLOCK-START
-- Helper lemmas and definitions go here
-- EVOLVE-BLOCK-END

theorem target_theorem : answer(
  -- EVOLVE-VALUE-START
  default          -- ← agent fills in the answer value
  -- EVOLVE-VALUE-END
) ↔ <condition> := by
  -- EVOLVE-BLOCK-START
  sorry            -- ← agent fills in the proof
  -- EVOLVE-BLOCK-END
```

For optimization problems, place the algorithm parameter inside `EVOLVE-VALUE` so the agent jointly discovers proof + optimal parameter.

---

## References

- Paper: arXiv:2605.22763 (Tsoukalas et al., Google DeepMind, May 2026)
- AlphaProof (RL-based olympiad prover): arXiv via Hubert et al., Nature 2025
- AlphaEvolve (evolutionary algorithm backbone): arXiv:2506.13131
- Formal Conjectures repo (Erdős/OEIS Lean formalizations): github.com/google-deepmind/formal-conjectures
- Terence Tao's AI contributions wiki: github.com/teorth/erdosproblems/wiki/AI-contributions
- ErdosProblems catalog: erdosproblems.com
