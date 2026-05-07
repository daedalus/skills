---
name: alphaevolve
description: Apply AlphaEvolve-style evolutionary algorithm design to discover, optimize, or improve algorithms and heuristics for well-defined problems with objective, automated evaluators. Use this skill whenever the user wants to: find a better algorithm for a computable problem, optimize a heuristic or scoring function, discover new solutions to math/CS problems with verifiable answers, evolve code toward a measurable objective, or improve data center/kernel/scheduling logic through automated search. Trigger on phrases like "find a better algorithm", "optimize this heuristic", "evolve a solution", "improve this function automatically", "algorithmic search", "automated optimization", or any request to systematically search for improved code where quality can be measured objectively. Also trigger when the user describes a problem with a clear scoring function or verifiable output — even if they don't use the word "evolve". IMPORTANT: Do NOT trigger for subjective requests like "make it elegant", "look nicer", "improve style", "beautify code", or "make it more readable" — these lack automated evaluators and require human judgment. If the user asks for code improvements without a clear automated way to measure "better", explain why AlphaEvolve doesn't apply and suggest alternatives.
---

# AlphaEvolve Skill

A workflow for applying evolutionary LLM-driven algorithm search to problems with **verifiable, automatable evaluators** — modeled on Google DeepMind's AlphaEvolve system.

## Quick Start (TL;DR)

```python
# Minimal working example
from dataclasses import dataclass
from typing import List, Callable
import random

@dataclass
class Program:
    code: str
    score: float

def evaluate(code: str) -> float:
    """Your evaluator here - must be fast and automated."""
    namespace = {}
    exec(code, namespace)
    return namespace.get('algorithm', lambda x: 0)(42)  # Test case

# Run evolution
db: List[Program] = [Program("def algorithm(x): return x", 0.5)]
for _ in range(100):
    parent = random.choice(db)
    # LLM mutates parent.code → new_code
    # new_code = call_llm(prompt_with(parent.code))
    new_program = Program(new_code, evaluate(new_code))
    db.append(new_program)
    
best = max(db, key=lambda p: p.score)
print(f"Best solution score: {best.score}")
```

---

## Core Principle

AlphaEvolve works because it separates **creativity** (LLM proposes mutations) from **truth** (automated evaluator scores them). The key constraint: **the problem must have an objective, fast, automated fitness function**. If you can't score a candidate solution programmatically in seconds, this approach doesn't apply.

---

## Trigger Examples

**YES — Trigger the skill:**

| User says... | Why trigger? |
|-------------|--------------|
| "Find a better sorting algorithm" | Objective: can measure speed with benchmarks |
| "Optimize this heuristic for the knapsack problem" | Automated evaluator: test cases with known solutions |
| "Evolve a faster matrix multiplication" | Objective: runtime benchmark, automated |
| "My scheduler is slow, optimize the priority function" | Evaluator: simulate on historical data |
| "Automatically improve this algorithm's accuracy" | Objective metric available |
| "Find me a better function for X" | Clear scoring function implied |

**NO — Do NOT trigger:**

| User says... | Why skip? |
|------------|------------|
| "Make my code more elegant" | Subjective, no automated evaluator |
| "Beautify this script" | Subjective, needs human judgment |
| "Improve the style of this code" | Subjective criteria |
| "Rewrite this to be more readable" | Subjective (unless paired with objective metric) |
| "Refactor this code" | Standard refactoring, not evolutionary search |
| "Fix this bug" | Deterministic fix, not optimization search |

**Edge case — Ask first:**
- "Improve this algorithm" → Ask: "What does 'improve' mean? Faster? More accurate? I need an automated way to score candidates."

---

## When NOT to Use AlphaEvolve

**CRITICAL: If the user's request is subjective, STOP and explain why AlphaEvolve doesn't apply.**

- **Subjective criteria**: "Make it more elegant", "look nicer", "improve style", "beautify code" → NO automated evaluator possible
- **No automated evaluator**: If you need human judgment to score solutions → Use standard refactoring instead
- **Extremely slow evaluation**: If each evaluation takes minutes/hours (try surrogates first)
- **Tiny search space**: Brute force or standard optimization would work better
- **Safety-critical code**: Evolutionary search doesn't guarantee correctness

**How to handle subjective requests:**
If user asks to "make code elegant" or similar, respond:
> "AlphaEvolve requires an **objective, automated evaluator** that can score solutions programmatically. 'Making code elegant' is subjective and needs human judgment. I'd recommend using standard refactoring techniques instead, or if you have a specific measurable goal (faster runtime, fewer lines, better test coverage), I can help set up AlphaEvolve for that."

---

## Phase0: Problem Qualification

Before doing anything else, check:

1. **Is there an automatable evaluator?** Can correctness/quality be measured by running code — no human in the loop?
2. **Is the evaluator fast?** Under ~10 seconds per evaluation is ideal. Minutes is workable. Slower than that, discuss with the user.
3. **Is there a current baseline?** What's the best known solution? Establish this first.
4. **What's the search space?** What parts of the code/algorithm are mutable? Constrain this early.

If the problem **doesn't** have an automatable evaluator, tell the user and help them design one, or explain why this approach won't work.

**Red flags to watch for:**
- Evaluator requires human judgment → Not suitable
- Evaluator takes >60 seconds → Discuss with user, consider sampling
- No clear "better" definition → Define success criteria first
- Search space is trivial → Use standard optimization instead

---

## Phase1: Problem Formalization

Structure the problem as a Python triple:

```python
# 1. The candidate program (what gets evolved)
def algorithm(input):
    # ... implementation to evolve ...
    return output

# 2. The evaluator (never mutated — ground truth)  
def evaluate(algorithm, test_cases) -> float:
    # Returns scalar score, higher = better
    score = 0.0
    for case in test_cases:
        result = algorithm(case.input)
        score += score_result(result, case.expected)
    return score / len(test_cases)

# 3. The baseline (current best)
baseline_score = evaluate(current_best_algorithm, test_cases)
```

Help the user write all three. The evaluator is sacred — it should be correct, comprehensive, and never modified during the search.

**Common evaluator patterns:**
- **Time Metric (Correctness + Speed)**: When two solutions are correct, faster wins:
  ```python
  def evaluate(algorithm) -> float:
      # Correctness gate: must pass all tests
      if not passes_all_tests(algorithm):
          return 0.0
      # Speed matters: faster = higher score
      runtime = benchmark(algorithm)
      return baseline_runtime / runtime  # >1.0 if faster than baseline
  ```
- **Pure optimization**: `objective_value(candidate_solution)`  
- **Mathematical**: `verify_proof(candidate)` or `measure_construction(candidate)`
- **Multi-objective**: Return dict with `fitness` + behavioral dimensions (speed, memory, accuracy)

**Evaluator debugging checklist:**
- [ ] Test on baseline first — does it return expected score?
- [ ] Test on known-good solution — does it score higher?
- [ ] Test on known-bad solution — does it score lower?
- [ ] Edge cases handled (division by zero, empty inputs, etc.)
- [ ] Evaluator runs in <10 seconds per candidate

**Advanced Evaluation Techniques:**
- **Cascaded Evaluation**: Run cheap, fast checks first (syntax, basic unit tests) before expensive full evaluations. Cuts eval cost 2–5× (AlphaEvolve paper, 2025).
- **Surrogate Models**: Use fast approximations (Gaussian Processes, KPLS, RBF networks) to predict fitness without full evaluation. 3× fewer full evals needed (Surrogate-Assisted EA Survey, 2011).
- **Expected Improvement (EI)**: Prioritize candidates with high potential for improvement, not just current score. Boosts sample efficiency (NeuroLGP-SM, 2024).
- **Evaluator Reliability Checks**:
  - *Consistency*: Measure variance across multiple test runs (low variance = stable evaluator)
  - *Robustness*: Track minimum score across test cases (catches edge case failures)
  - *Behavioral Correlation*: Verify evaluator aligns with actual problem goals (prevents misaligned incentives)

---

## Phase2: Evolutionary Search Setup

Structure the evolution as a program database + sampling loop:

```python
from dataclasses import dataclass
from typing import Callable, List, Optional
import random

@dataclass
class Program:
    code: str           # source of the candidate
    score: float        # evaluator score
    generation: int     # how many mutations deep

class ProgramDatabase:
    def __init__(self, initial: Program):
        self.programs: List[Program] = [initial]
    
    def sample_for_mutation(self, k: int = 3) -> List[Program]:
        """Sample k programs, biased toward higher scores."""
        if not self.programs:
            return []
        # Island model: sample from top-50% with 80% probability
        top = sorted(self.programs, key=lambda p: p.score, reverse=True)
        cutoff = max(1, len(top) // 2)
        pool = top[:cutoff] if random.random() < 0.8 else top
        return random.sample(pool, min(k, len(pool)))
    
    def add(self, program: Program) -> None:
        self.programs.append(program)
        # Optional: prune to keep database manageable
        if len(self.programs) > 1000:
            self.programs = sorted(
                self.programs, key=lambda p: p.score, reverse=True
            )[:500]
```

**Key parameters to discuss with user:**
- Population size (start small: 20–50)
- Mutation breadth vs. depth (Flash model = broad, Pro model = deep)
- Number of generations / compute budget
- Whether to use "islands" (multiple independent populations that merge)

**Advanced database features to consider:**
- Age-based pruning (remove old, low-scoring programs)
- Diversity preservation (penalize too-similar programs)
- Island model (maintain separate sub-populations)
- Elitism (always keep top-k programs)
- **PDI Tracking**: Calculate Population Diversity Index periodically, target PDI > 0.5
- **Genealogical Diversity**: Track parent-child relationships to preserve novel lineages
- **QD Score**: Track sum of top-performer scores across islands to balance quality + diversity

```python
# Add to ProgramDatabase class
def calculate_pdi(self) -> float:
    """Calculate Population Diversity Index (0=identical, 1=max diverse)."""
    if len(self.programs) < 2:
        return 0.0
    # Normalize Hamming distance by max possible (simplified for code strings)
    total = 0.0
    count = 0
    for i in range(len(self.programs)):
        for j in range(i+1, len(self.programs)):
            # Simple length-normalized difference
            a, b = self.programs[i].code, self.programs[j].code
            max_len = max(len(a), len(b))
            if max_len == 0:
                continue
            diff = sum(1 for c1, c2 in zip(a, b) if c1 != c2) + abs(len(a)-len(b))
            total += diff / max_len
            count += 1
    return total / count if count > 0 else 0.0
```

---

## Strategy Evolution (EvoX)

When progress stagnates (Rt < τ for 10+ gens), evolve the search strategy itself:

1. **Strategy Database**: Store past strategies (prompt templates, sampling rules, mutation params) + their progress rates.
2. **Strategy Selection**: Score-biased select top-performing strategies from history.
3. **Strategy Mutation**: LLM mutates selected strategy, conditioned on current population state (diversity, stagnation metrics).
4. **Validation**: Test new strategy for 5 gens; deploy if progress rate > current strategy.

```python
class StrategyDatabase:
    def __init__(self):
        self.strategies = []  # (strategy, progress_rate, last_used_gen)
    
    def add(self, strategy, progress_rate):
        self.strategies.append((strategy, progress_rate, current_gen))
    
    def sample_for_mutation(self):
        # Bias toward high progress_rate
        weights = [s[1] for s in self.strategies]
        return random.choices(self.strategies, weights=weights, k=1)[0][0]
```

**When to trigger**: Relative Progress (Rt) < 0.05 for 10+ generations, or PDI < 0.3 for 20+ gens.

---

## Phase3: Mutation Prompt Engineering

The LLM mutation prompt is the core of the system. Structure it as:

```
SYSTEM:
You are an expert algorithm designer. Your task is to propose improvements 
to the following algorithm. You may make any changes — small tweaks or 
complete rewrites — as long as the function signature is preserved.
The algorithm will be automatically evaluated. Focus on [OBJECTIVE].

USER:
Here are some existing algorithms and their scores (higher = better):

--- Algorithm A (score: 0.847) ---
[code]

--- Algorithm B (score: 0.831) ---  
[code]

--- Algorithm C (score: 0.792) ---
[code]

Current best score: 0.847
Baseline score: 0.712

Propose a new algorithm that might score higher. Output ONLY valid Python code.
No explanation. The function must have this exact signature:
def algorithm(input) -> output_type:
```

**Mutation strategies to prompt for explicitly:**
- **Perturbation**: Small change to a constant, threshold, or formula
- **Crossover**: Combine ideas from two high-scoring candidates  
- **Structural**: Change the algorithmic approach entirely
- **Reverse engineering**: Ask the LLM to explain why the best solution works, then improve it

**Advanced prompt techniques:**
- Show diffs between high and low scoring programs
- Ask for "wild ideas" periodically (exploration vs exploitation)
- Include runtime hints if optimizing for speed
- Request specific improvements (e.g., "reduce the constant factor")
- Use chain-of-thought: "Why does A work better than B?"
- **Fine-tuned diff models**: Train on accepted mutations to boost valid output 40%
- **Verbalized Sampling**: Generate K complementary candidates per prompt to reduce redundancy (TurboEvolve, 2025)
- **Strategy Tracking**: Log which prompt strategies yield improvements, evolve them when progress stalls (EvoX, 2025)

---

## Phase4: Run the Loop

```python
import subprocess
import textwrap
import re
from typing import Optional, Callable

def extract_code(llm_response: str) -> Optional[str]:
    """Extract Python function from LLM output."""
    # Try fenced code block first
    # Match fenced python blocks: START="```python" END="```"
    START = "```python"
    END = "```"
    match = re.search(f'{START}\n(.*?){END}', llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fall back to raw code if it starts with 'def'
    stripped = llm_response.strip()
    if stripped.startswith('def '):
        return stripped
    return None

def safe_evaluate(code: str, evaluator: Callable, timeout: int = 30) -> Optional[float]:
    """Evaluate candidate code safely, return None on failure."""
    try:
        namespace = {}
        exec(code, namespace)
        candidate_fn = namespace.get('algorithm')
        if candidate_fn is None:
            return None
        # Run evaluator with timeout via subprocess or signal
        return evaluator(candidate_fn)
    except Exception:
        return None

# Main loop
db = ProgramDatabase(baseline_program)
# Optional: Initialize surrogate model (GP/KPLS) for fast fitness prediction
surrogate_model = None  # Train after 10+ full evals

for generation in range(N_GENERATIONS):
    parents = db.sample_for_mutation()
    prompt = build_mutation_prompt(parents, db.best_score)
    response = call_llm(prompt)  # Flash for speed, Pro for quality
    code = extract_code(response)
    if code:
        # Cascaded eval: cheap syntax/unit checks first
        if not passes_basic_checks(code):
            continue
        # Surrogate eval: skip full eval if predicted score < current best
        if surrogate_model and surrogate_model.predict(code) < db.best_score:
            continue
        # Full eval
        score = safe_evaluate(code, evaluator)
        if score is not None:
            # Update surrogate with new data
            if surrogate_model:
                surrogate_model.add_data(code, score)
            db.add(Program(code=code, score=score, generation=generation))
            if score > db.best_score:
                print(f"New best: {score:.4f} (gen {generation})")
```

**Always run candidates in a sandbox** — untrusted code execution. Use `subprocess` with resource limits or a container. Never `exec()` in your main process without at least a timeout.

**Debugging tips:**
- Log failed evaluations (syntax errors, timeouts)
- Track mutation success rate (how often mutations improve score)
- If stuck at baseline, increase mutation diversity
- Monitor for code bloat (programs getting too long)
- **Stagnation Detection**: Track Relative Progress (Rt); if Rt < 0.05 for 10+ gens, trigger strategy change
- **Surrogate Evaluators**: Use GP/KPLS models to predict fitness, run full eval only on top candidates
- **Cascaded Eval**: Run cheap syntax/unit tests first, full eval only for passing candidates

---

## Phase5: Analysis and Extraction

After the search:

1. **Extract the best solution** — get the top-scoring program from the database
2. **Verify independently** — re-run the evaluator on the winner from a clean state
3. **Human-readable pass** — ask the LLM to clean up and comment the winner
4. **Explain the innovations** — ask why it works: what did the evolution discover?
5. **Ablation** — if time allows, test sub-components to understand which mutations matter

```python
# Ask LLM to explain the winner
explanation_prompt = f"""
This algorithm was discovered by automated evolutionary search.
It scores {best_score:.4f} vs. baseline {baseline_score:.4f}.

Code:
{best_code}

Explain in plain language: what is this algorithm doing differently from the 
baseline? What is the key insight? Be specific.
"""
```

**Deliverables to provide:**
- Best algorithm code (cleaned up)
- Performance comparison vs baseline
- Explanation of improvements
- Optional: runner-up solutions with different approaches

---

## Metrics and Tracking

Track these metrics during evolution:

```python
metrics = {
    "total_evaluations": 0,
    "successful_mutations": 0,
    "failed_mutations": 0,
    "best_score_history": [],
    "mutation_success_rate": 0.0,
    # Stagnation detection
    "relative_progress": [],  # Scale-invariant Rt
    "fitness_stagnation_count": 0,
    # Diversity metrics
    "pdi": 0.0,  # Population Diversity Index
    "genealogical_diversity": 0.0,
    "qd_score": 0.0,  # Quality-Diversity score
    # Mutation success
    "valid_diff_rate": 0.0,
    "verbalized_yield": 0.0,
    "strategy_progress_rate": 0.0,
}

# Update after each generation
metrics["total_evaluations"] += 1
if score > parent_score:
    metrics["successful_mutations"] += 1
metrics["best_score_history"].append(db.best_score)
metrics["mutation_success_rate"] = (
    metrics["successful_mutations"] / metrics["total_evaluations"]
)

# Stagnation: Relative Progress (Rt)
G_t = db.best_score - target_r  # target_r = 0 for minimization
if len(metrics["best_score_history"]) > 1:
    G_prev = metrics["best_score_history"][-2] - target_r
    R_t = (G_prev - G_t) / max(G_prev, 1e-9)
    metrics["relative_progress"].append(R_t)
    if R_t < stagnation_threshold:
        metrics["fitness_stagnation_count"] += 1
```

### Stagnation Detection Metrics
- **Relative Progress (Rt)**: Scale-invariant improvement rate = (Gₜ₋₁ - Gₜ)/Gₜ₋₁. Detects stagnation regardless of problem scale (PACEvolve, 2025).
- **Fitness-based Stagnation**: Uses fitness values only (no pairwise distance), 3× faster than Hamming distance (ACM 2014).
- **POSE**: Single scalar for stopping criteria performance (combines final population quality + budget used) (arXiv 2024).
- **Radius Memory (SD-RLSᵐ)**: Tracks last successful mutation strength to escape local optima faster (Algorithmica 2024).

### Diversity Metrics
- **PDI (Population Diversity Index)**: 0–1 normalized, O(n) time. More accurate than entropy/Hamming (GECCO 2011).
- **Genealogical Diversity**: Uses genetic operator history, no domain-specific distance needed (GECCO 2017).
- **QD Score**: Sum of performance of all champions in map. Balances quality + diversity (ELM, 2022).

### Mutation Success Metrics
- **Valid Diff Rate**: % of LLM outputs that parse to valid code. Fine-tuned diff models boost this 40% (ELM, 2022).
- **Verbalized Sampling Yield**: K complementary candidates per LLM call. Cuts LLM cost 2× (TurboEvolve, 2025).
- **Strategy Progress Rate**: Δscore per generation for a given search strategy. Triggers strategy evolution when < τ (EvoX, 2025).

**What to watch for:**
- Success rate < 10% → Increase mutation diversity
- Relative Progress (Rt) < 0.05 for 10+ gens → Stagnation detected, evolve strategy
- PDI < 0.3 → Population lacks diversity, increase sample pool
- Best score flat for 20+ generations → Try restart with different strategy
- Score jumping wildly → Evaluator might be stochastic (need more samples)
- Valid diff rate < 50% → Fine-tune diff model or improve prompt constraints

---

## Troubleshooting

### Evolution stuck at baseline
- Use Relative Progress (Rt) — scale-invariant improvement rate to detect stagnation
- Switch to TurboEvolve-style verbalized sampling (multiple complementary candidates per prompt)
- Evolve search strategies (EvoX) when progress stalls for 20+ generations
- Increase mutation breadth (try more diverse mutations)
- Increase temperature in LLM calls
- Try different mutation strategies (structural vs perturbation)
- Check if evaluator is too strict

### All solutions look the same
- Track PDI (Population Diversity Index) to quantify diversity (0=identical, 1=maximally diverse)
- Use genealogical diversity to measure relatedness without domain-specific distance
- Use QD Score to balance quality and diversity across islands
- Population lacks diversity — increase sample pool size
- Mutation prompt too constrained — ask for "wild ideas"
- Try island model with different mutation strategies per island

### Evaluator too slow
- Use cascaded evaluation (cheap checks first) to cut cost 2–5×
- Deploy surrogate models (GP, KPLS) to predict fitness without full eval
- Use Expected Improvement to prioritize high-potential candidates
- Profile the evaluator to find bottlenecks
- Reduce test case count (sample subset)
- Cache evaluation results for identical code
- Consider approximate evaluation

### LLM generates invalid code
- Fine-tune diff models on accepted mutations to boost valid output 40%
- Use verbalized sampling to generate multiple candidates, increasing valid yield
- Improve prompt with more explicit constraints
- Add "Output ONLY valid Python" reminder
- Show examples of valid outputs
- Use stricter extraction (reject if doesn't parse)

---

## Domain-Specific Notes

### Mathematical optimization
- Evaluator = objective function value or proof verifier
- Search space = construction procedure or optimization routine
- Example: kissing number, matrix multiplication rank, combinatorial bounds
- See `references/math_patterns.md` for common setups

### Systems / kernels
- Evaluator = runtime benchmark (use `timeit`, `perf`, or hardware counters)
- Search space = loop ordering, tiling factors, instruction selection
- Critical: warm up the cache, run multiple times, use geometric mean
- Sandbox requirement is strict here — bad code can hang

### Scheduling / heuristics
- Evaluator = simulation of the scheduler on historical trace data
- Search space = priority function, bin-packing heuristic, threshold values
- Interpretability matters: prefer readable solutions when scores are close

### Combinatorics / number theory
- Evaluator = `verify(construction)` — check the mathematical property directly
- Often the fastest evaluators (pure arithmetic)
- Track whether you're improving lower bounds or upper bounds

---

## Success Stories

AlphaEvolve has been used to:
- **Optimize matrix multiplication**: Discovered faster algorithms for small matrices
- **Improve data center scheduling**: Reduced job completion time by 15%
- **Discover mathematical constructions**: New bounds for combinatorial problems
- **Optimize GPU kernels**: 20% speedup on specific workloads

---

## What AlphaEvolve Gets Right (Design Principles)

These principles from the paper should guide your implementation:

1. **Ensemble of models**: Use a fast model (Flash-equivalent) for volume and a slow model (Pro-equivalent) for quality. Alternate or run in parallel.

2. **Programs database with diversity**: Don't just keep the best — keep a diverse population. Pure elitism converges too fast.

3. **Evolve entire codebases, not just functions**: The mutation can touch any part of the program — loss functions, hyperparameters, data structures, not just the core logic.

4. **Automated evaluators are sacred**: Never relax the evaluator to make solutions look better. The evaluator is ground truth.

5. **Human-readable solutions preferred**: When two solutions score equally, prefer the one a human can read and maintain.

6. **Adaptive strategy evolution**: Evolve search strategies (mutation prompts, sampling rules) when progress stagnates (EvoX, 2025).

7. **Verbalized sampling**: Generate K complementary candidates per LLM call to reduce redundancy and cost (TurboEvolve, 2025).

8. **Surrogate-assisted evaluation**: Use fast approximations to cut eval cost 2–3× (AlphaEvolve, 2025).

9. **Multi-objective optimization**: Optimize multiple metrics (correctness + speed + size) simultaneously (AlphaEvolve, 2025).

---

## References

### Core Papers
- AlphaEvolve: arXiv 2506.13131 (Google DeepMind, 2025)
- FunSearch: "Making new discoveries with LLMs" (Nature 2024, arXiv 2206.08896)
- TurboEvolve: arXiv 2604.18607 (2025)
- EvoX: arXiv 2602.23413 (Strategy Evolution, 2025)
- EvoLattice: arXiv 2512.13857 (Multi-path evolution, 2025)
- PACEvolve: arXiv 2601.10657 (Relative Progress, 2025)

### Surrogate & Evaluation
- Surrogate-assisted EA survey: Swarm and Evolutionary Computation 2011
- NeuroLGP-SM: arXiv 2404.08786 (KPLS surrogate, 2024)
- Expected Improvement: Gaussian Processes for ML (Rasmussen, 2006)

### Diversity & Stagnation
- Population Diversity Index (PDI): GECCO 2011
- Genealogical Diversity: GECCO 2017
- QD Score: arXiv 2206.08896 (ELM, 2022)
- Fitness-based Stagnation: ACM 2014, Algorithmica 2024
- POSE (Stopping Criteria): arXiv 2604.25458 (2025)
- Radius Memory (SD-RLSᵐ): Algorithmica 2024

### Mutation & Prompting
- Fine-tuned Diff Models: arXiv 2206.08896 (ELM, 2022)
- Verbalized Sampling: arXiv 2604.18607 (TurboEvolve, 2025)
- Prompt Engineering: "The Prompt Pattern Catalog" (arXiv)

### General
- Evolutionary computation: "Essentials of Metaheuristics" by Sean Luke
- Genetic Algorithms: "GA in Search, Optimization, ML" by Goldberg

---

## Checklist Before Starting

- [ ] Automated evaluator written and tested on known solutions
- [ ] Baseline score established
- [ ] Mutation scope defined (what parts of code can change?)
- [ ] Sandbox/execution environment set up safely
- [ ] Compute budget decided (how many evaluations?)
- [ ] Success criterion defined (what score is "good enough"?)

---

## Common Pitfalls to Avoid

- **Overfitting to test cases**: Use separate train/test sets if possible
- **Forgetting the baseline**: Always compare against a simple solution
- **Too strict evaluator**: If nothing passes, relax or fix the evaluator
- **Not enough diversity**: If all solutions look same, increase mutation breadth
- **Ignoring runtime**: Fast evaluation enables more iterations
- **Evolving the evaluator**: Never mutate the scoring function mid-search
- **No early stopping**: Set a budget and stick to it
