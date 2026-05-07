---
name: alphaevolve
description: Apply AlphaEvolve-style evolutionary algorithm design to discover, optimize, or improve algorithms and heuristics for well-defined problems. Use this skill whenever the user wants to: find a better algorithm for a computable problem, optimize a heuristic or scoring function, discover new solutions to math/CS problems with verifiable answers, evolve code toward a measurable objective, or improve data center/kernel/scheduling logic through automated search. Trigger on phrases like "find a better algorithm", "optimize this heuristic", "evolve a solution", "improve this function automatically", "algorithmic search", "automated optimization", or any request to systematically search for improved code where quality can be measured objectively. Also trigger when the user describes a problem with a clear scoring function or verifiable output — even if they don't use the word "evolve".
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

## When NOT to Use AlphaEvolve

- **No automated evaluator**: If you need human judgment to score solutions
- **Subjective criteria**: "Make it more elegant" (subjective) vs "Make it faster" (objective)
- **Extremely slow evaluation**: If each evaluation takes minutes/hours
- **Tiny search space**: Brute force or standard optimization would work better
- **Safety-critical code**: Evolutionary search doesn't guarantee correctness

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
- Correctness + efficiency: `passes_all_tests(candidate) * (baseline_runtime / candidate_runtime)`
- Pure optimization: `objective_value(candidate_solution)`  
- Mathematical: `verify_proof(candidate)` or `measure_construction(candidate)`

**Evaluator debugging checklist:**
- [ ] Test on baseline first — does it return expected score?
- [ ] Test on known-good solution — does it score higher?
- [ ] Test on known-bad solution — does it score lower?
- [ ] Edge cases handled (division by zero, empty inputs, etc.)
- [ ] Evaluator runs in <10 seconds per candidate

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
    match = re.search(r'```python\n(.*?)```', llm_response, re.DOTALL)
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
for generation in range(N_GENERATIONS):
    parents = db.sample_for_mutation()
    prompt = build_mutation_prompt(parents, db.best_score)
    response = call_llm(prompt)  # Flash for speed, Pro for quality
    code = extract_code(response)
    if code:
        score = safe_evaluate(code, evaluator)
        if score is not None:
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
}

# Update after each generation
metrics["total_evaluations"] += 1
if score > parent_score:
    metrics["successful_mutations"] += 1
metrics["best_score_history"].append(db.best_score)
metrics["mutation_success_rate"] = (
    metrics["successful_mutations"] / metrics["total_evaluations"]
)
```

**What to watch for:**
- Success rate < 10% → Increase mutation diversity
- Best score flat for 20+ generations → Try restart with different strategy
- Score jumping wildly → Evaluator might be stochastic (need more samples)

---

## Troubleshooting

### Evolution stuck at baseline
- Increase mutation breadth (try more diverse mutations)
- Increase temperature in LLM calls
- Try different mutation strategies (structural vs perturbation)
- Check if evaluator is too strict

### All solutions look the same
- Population lacks diversity — increase sample pool size
- Mutation prompt too constrained — ask for "wild ideas"
- Try island model with different mutation strategies per island

### Evaluator too slow
- Profile the evaluator to find bottlenecks
- Reduce test case count (sample subset)
- Cache evaluation results for identical code
- Consider approximate evaluation

### LLM generates invalid code
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

---

## References

- Original AlphaEvolve paper: Google DeepMind (2024)
- Evolutionary computation: "Essentials of Metaheuristics" by Sean Luke
- LLM-guided search: "FunSearch: Making new discoveries with LLMs" (Nature 2024)
- Prompt engineering: "The Prompt Pattern Catalog" (arXiv)

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
