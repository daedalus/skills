---
name: integer-sequence-research
description: >
  Autonomous research pipeline for discovering, validating, and characterizing
  integer sequences suitable for OEIS submission. Use this skill whenever the
  user wants to generate new sequences from arithmetic constructions, test
  whether a formula is correct, falsify a conjecture about number-theoretic
  functions, check multiplicativity, profile prime-power behavior, or search
  for OEIS collisions. Also triggers for requests like "find me a new sequence",
  "is this formula right", "does f(n) = phi(n) * 2^omega(n) have a closed form",
  "test this divisor sum for multiplicativity", or "is this OEIS-worthy". The
  core philosophy: treat every formula as guilty until proven robust. Prefer
  counterexamples over confirmations. Elegance is suspicious. Survival under
  adversarial attack is the only meaningful validation.
---

# Autonomous Integer Sequence Research System

Adversarial + generative pipeline for OEIS-grade sequence discovery. The
system generates candidates, cross-validates them, aggressively tries to break
conjectured formulas, and scores survivors on a confidence scale.

**Reference implementation:** `seq_research.py`  
Run with `python seq_research.py` (full sweep) or  
`python seq_research.py --single <NAME>` (single sequence).

---

## Pipeline Overview

```
Generator → Evaluator → Conjecturer → Falsifier → Classifier → Report
                ↑_____________________________|
                     (loop until validated or discarded)
```

Each stage is described below. Read all sections before starting work; the
adversarial falsifier (§4) is the most important stage and the one most
commonly skipped too early.

---

## §1 · Sequence Generation

### Grammar

Build candidates compositionally from:

| Category | Elements |
|---|---|
| **Base functions** | `n`, `φ(n)`, `σ(n)`, `τ(n)`, `rad(n)`, `ω(n)`, `Ω(n)`, `μ(n)` |
| **Operators** | `+`, `×`, `^`, composition |
| **Divisor structures** | `Σ_{d\|n}`, `Π_{d\|n}`, unitary filter `gcd(d, n/d)=1` |
| **Bit/hybrid** | XOR, popcount, parity |

### Bias Rules

Prefer candidates that are likely to be **multiplicative** — they are richer,
easier to characterize at prime powers, and more likely to be novel. Structural
signals to pursue:

- φ compositions over divisors
- Products involving unitary divisors
- Dirichlet convolutions (μ ★ f, id ★ φ, etc.)
- Functions of the prime signature only (depend on exponents, not primes)

Avoid: trivial linear combinations of known sequences, constant multiples of
φ or σ, anything obviously reducible by inspection.

### Example Constructions Worth Exploring

```
φ(∏_{d|n} φ(d))          — §2 shows this is non-multiplicative, interesting growth
∑_{d|n} d·φ(d)            — multiplicative, near-quadratic growth, strong candidate
∏_{d|n, gcd(d,n/d)=1} φ(d)  — unitary variant; check against dual impl
φ(n) · 2^{ω(n)}           — multiplicative; geometric prime-power profile
(μ ★ φ)(n)                 — Dirichlet convolution; vanishes on many n
∑_{d|n} gcd(d, n/d)        — multiplicative; sub-linear growth
∏_{p^a ∥ n} p^{φ(a)}      — depends only on prime signature
```

---

## §2 · Multi-Implementation Evaluation

**Rule:** every sequence must have ≥2 independent implementations before
conjecture work begins.

### Implementation Types

**A. Definition-based** — iterate over `divisors(n)` directly.

**B. Factorization-based** — exploit the prime factorization `n = ∏ pᵢ^aᵢ`.
For multiplicative functions this gives a cleaner formula:
`f(n) = ∏ f(pᵢ^aᵢ)`, computable from `factorint(n)` alone.

**C. Hybrid** — cached + partial symbolic where helpful for large n.

### Differential Validation

Run both implementations on n = 1…30 plus the weak zones (§4). If they
disagree at **any** n: the sequence definition is ambiguous or one
implementation is wrong. Fix before proceeding. Do not conjecture on a
sequence with unresolved implementation disagreements.

---

## §3 · Multiplicativity Detection

Test `f(ab) = f(a)·f(b)` for `gcd(a,b) = 1` across:

- Pairs of distinct primes: `(2,3)`, `(2,5)`, `(3,7)`, `(5,11)`, …
- Prime × prime square: `(2, 9)`, `(4, 3)`, `(4, 25)`, …
- Larger coprime products: `(4, 9)`, `(8, 25)`, `(16, 27)`, …

**If multiplicative:** proceed to prime-power profiling (§3.1) and enforce
multiplicative modeling in conjecture work (§5).

**If not multiplicative:** compute the interaction residual `f(ab)/(f(a)·f(b))`
for coprime pairs and check whether the residual has structure. If it does,
the function may be "almost multiplicative" in a useful sense. If it doesn't,
the function is unlikely to have a clean closed form.

### 3.1 · Prime-Power Profiling

For any multiplicative (or candidate-multiplicative) function, compute:

```
f(p^k) for p ∈ {2, 3, 5, 7, 11}, k = 1…8
```

Look for:

| Pattern | Interpretation |
|---|---|
| Constant ratio `f(p^{k+1})/f(p^k)` across all k | f is geometric at p, likely `f(p^k) = p^{αk}` |
| Ratio → p as k grows | f(p^k) ~ p^k (identity-like) |
| Ratio = p-1 | f(p^k) = φ(p^k) = p^{k-1}(p-1) |
| Non-constant but p-independent | f(p^k) = g(k) for some g |
| p-dependent ratio | f encodes the primes, not just exponents |

Once the prime-power formula is identified, the full multiplicative function
follows immediately from `f(n) = ∏ f(p^a)` over the factorization.

---

## §4 · Adversarial Falsification (Most Important Stage)

The goal is to find **the smallest n where the conjecture fails** before
claiming success. Always run this before reporting any formula.

### 4.1 · Weak Zones (Test These First)

These inputs break naive formulas most often:

```python
WEAK_ZONES = (
    # Prime powers
    [p**k for p in [2,3,5,7,11,13] for k in range(1,6)] +
    # Products of two primes and their powers
    [p**a * q**b for p,q in [(2,3),(2,5),(3,5)] for a,b in [(1,1),(2,1),(1,2)]] +
    # Highly composite: 12, 24, 60, 120, 360, 720, 840, 2520
    [12, 24, 60, 120, 360, 720, 840, 2520] +
    # Powers of 2 and near-powers
    [2**k for k in range(1,20)] + [2**k - 1 for k in range(2,20)] +
    # Three-prime products
    [2*3*5, 2*3*7, 2*5*7, 3*5*7, 2*3*5*7]
)
```

### 4.2 · Mutation Attack

Given a failing n₀, propagate:

```
n₀ → n₀ · p   (extend by small prime)
n₀ → n₀ / p   (reduce if p² | n₀)
n₀ → n₀²      (square)
```

This often reveals whether the failure is isolated or structural.

### 4.3 · Delta Debugging

If a counterexample is found at composite n, find the smallest n' where the
formula fails. Prime powers and small semiprimes are the most informative.

### 4.4 · Red Team Checklist

Before accepting any formula, verify:

1. Does it work for n = 1? (edge case: φ(1)=1, σ(1)=1, ω(1)=0, μ(1)=1)
2. Does it work for prime n? For p²? For p³?
3. Does it work for pq (two distinct primes)?
4. Does it work for highly composite n (60, 120, 720)?
5. Is the formula actually a known sequence in disguise? (→ §6 OEIS check)
6. Does the conjectured formula match the factorization-based dual? (→ §2)
7. Is the growth rate consistent across the tested range? (→ §5)

---

## §5 · Conjecture Engine

Only conjecture after multiplicativity testing (§3) and adversarial testing
(§4) have passed.

### 5.1 · Template Hierarchy

Try formulas in this order (simpler first):

1. `f(n) = n`, `f(n) = φ(n)`, `f(n) = σ(n)`, `f(n) = τ(n)`, `f(n) = rad(n)`
2. `f(n) = φ(n)^a`, `f(n) = n^a · φ(n)^b`
3. `f(n) = 2^{g(ω(n))} · h(n)`
4. For multiplicative f: derive from the prime-power formula directly

### 5.2 · Log-Space Regression

For growth estimation and exponent fitting:

```python
alpha = cov(log n, log f(n)) / var(log n)
```

This gives the asymptotic exponent in `f(n) ~ C · n^alpha`. Use n > 10 to
avoid distortion from small-n irregularities.

### 5.3 · Multiplicative Conjecture Construction

If f is multiplicative with prime-power formula `f(p^k) = g(p,k)`, then:

```
f(n) = ∏_{p^a ∥ n}  g(p, a)
```

This is the canonical form. Test the fully reconstructed multiplicative
function against the definition-based implementation on n = 1…100 and all
weak zones.

---

## §6 · OEIS Collision Filter

Compute the first 100 terms and check against:

- Standard arithmetic functions: φ, σ, τ, rad, ω, Ω, μ, id, id²
- Their Dirichlet convolutions
- Known transforms: partial sums, Euler transform, Möbius transform

If the first 30 terms match a known sequence exactly, the candidate is not
novel — report the collision and move on.

If the first 30 terms are unique: compute 100 terms and search OEIS directly
(format: `1, 2, 4, 4, 8, 8, 12, 8, 12, 16` — comma-separated, no spaces
around commas).

---

## §7 · Confidence Scoring

Each sequence receives a score 0–100:

| Criterion | +Points | −Points |
|---|---|---|
| Cross-validation passes | +10 | −20 if fails |
| Multiplicative | +15 | — |
| Passes adversarial falsification | +15 | −15 if fails |
| Surviving closed-form conjecture | +10 | — |
| Consistent growth (0.5 ≤ α ≤ 3.0) | +5 | — |
| No errors in first 100 terms | — | −3 per error |
| OEIS collision detected | — | −20 |

**Confidence levels:**

| Score | Level | Action |
|---|---|---|
| 0–39 | Discard | Fix implementation or abandon |
| 40–69 | Experimental | More terms, more testing |
| 70–89 | Strong candidate | Compute 500 terms, prepare OEIS draft |
| 90–100 | OEIS-ready | Validate formula, write b-file |

---

## §8 · Output Standard (OEIS-Grade)

A sequence report must include:

1. **Definition** — at least two equivalent formulations
2. **First 100–500 terms** — verified across ≥2 implementations
3. **Multiplicativity** — proved or disproved with witness if not
4. **Prime-power characterization** — f(p^k) formula with evidence
5. **Closed form** — if found, with falsification report (how many n tested, result)
6. **Counterexample search** — what was tested, what survived
7. **Growth exponent** — asymptotic α from log-regression
8. **OEIS collision check** — which known sequences were compared
9. **Confidence score** — with breakdown
10. **Reference implementation** — clean Python, importable

---

## §9 · Known Failure Modes and Mitigations

| Failure | Cause | Fix |
|---|---|---|
| Formula works for n ≤ 30, fails at n=36 | Didn't test p²·q | Always include weak zones |
| Dual implementation disagrees | Off-by-one in unitary filter | Test gcd(d, n/d) = 1 carefully; 1 is always a unitary divisor |
| Multiplicativity test passes but formula is wrong | Coprime pairs too small | Include pairs with p² and p³ |
| Growth estimate unstable | Dominated by n=1 and n=2 | Start regression from n=10 |
| "Novel" sequence is A000010 (Euler phi) | Didn't check base cases | Always check standard functions first |
| `phi(rad(n))` errors for n=1 | `rad(1) = 1`, `phi(1) = 1` but sympy may return 0 | Guard: if `rad(n) == 0: return 1` |

---

## §10 · Meta-Insight Tracking

After running multiple candidates, record which constructions tend to produce
useful sequences and which are dead ends. Current priors:

**Productive:**
- Dirichlet convolutions involving μ and φ
- Products over unitary divisors
- Functions of the form φ(n)·g(ω(n))

**Dead ends:**
- φ ∘ (∏_{d|n} φ(d)) — non-multiplicative, hard to characterize
- gcd(σ(n), φ(n)) — non-multiplicative, already in OEIS
- lcm(σ(n), φ(n)) — non-multiplicative, complex growth

**Watch list (experimental, unresolved):**
- ∑_{d|n} (d XOR n/d) — non-multiplicative but interesting XOR structure
- ω(n)^{φ(n)} mod n — slow growth, heavily prime-power-dominated

---

## Appendix: Quick Reference

```python
# Key imports
from sympy import (factorint, totient, divisors, divisor_sigma,
                   divisor_count, isprime, gcd, mobius, rad,
                   primeomega, primenu)

# Core functions
phi   = lambda n: int(totient(n))
tau   = lambda n: int(divisor_count(n))
sigma = lambda n: int(divisor_sigma(n))
Rad   = lambda n: int(rad(n))
omega = lambda n: int(primenu(n))       # distinct prime factors
Omega = lambda n: int(primeomega(n))    # total with multiplicity
mu    = lambda n: int(mobius(n))

# Unitary divisors
def unitary_divisors(n):
    return [d for d in divisors(n) if gcd(d, n // d) == 1]

# Multiplicativity test
def is_multiplicative(fn, trials=40):
    pairs = [(2,3),(2,5),(3,5),(4,9),(2,7),(5,9),(4,25),(8,27)]
    return all(fn(a*b) == fn(a)*fn(b) for a,b in pairs if gcd(a,b)==1)
```
