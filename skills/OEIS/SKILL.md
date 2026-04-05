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
| Dual implementation disagrees | Off-by-one in unitary filter or wrong prime-power formula | Test against divisors(n) directly; verify f(p^k) for k=1,2,3 |
| Multiplicativity test passes but formula is wrong | Coprime pairs too small | Include pairs with p² and p³ |
| Growth estimate unstable | Dominated by n=1 and n=2 | Start regression from n=10 |
| "Novel" sequence is A000010 (Euler phi) | Didn't check base cases | Always check standard functions first |
| `phi(rad(n))` errors for n=1 | sympy's `rad` is symbolic (radians!), not integer radical | Implement manually: `rad(n) = prod(p for p in factorint(n))` |
| Weak zone test reports "non-numeric" for valid integers | sympy.Integer vs Python int | Check `hasattr(val, 'is_Integer')` or use `int(val)` |
| `Σ_{d|n} gcd(d,n/d)` formula fails at p^k | Wrong piecewise formula | Use: even k → 2(p^{k/2}-1)/(p-1) + p^{k/2}; odd k → 2(p^{(k+1)/2}-1)/(p-1) |

---

## §10 · Meta-Insight Tracking

After running multiple candidates, record which constructions tend to produce
useful sequences and which are dead ends. Updated after Batch 1 and Batch 2.

**Productive:**
- φ(n)·c^{ω(n)} family — multiplicative for any constant c; f(p^k) = c·p^{k-1}(p-1); c=2-6 confirmed OEIS-READY
- n·2^{Ω(n)} — "totally doubled" variant of n; f(p^k) = (2p)^k; exact closed form
- Σ_{d|n} d²·φ(n/d) — Dirichlet id²★φ; f(p^k) = p^{2k} + p^{k-1}(p^k - 1); near-quadratic (α≈2)
- Σ_{d|n} φ(d)² — Dirichlet φ²★1; f(p^k) = 1+(p-1)²(p^{2k}-1)/(p²-1); near-quadratic (α≈2)
- Σ_{d|n} gcd(d, n/d) — multiplicative; piecewise formula for even/odd exponents; slow growth (α≈0.2)
- ∏_{p^a ∥ n} φ(p^a + 1) — product of φ of prime-power+1; α≈0.8; OEIS-READY
- Completely additive g(a) family (Σ_{p^a ∥ n} g(a)); prime-signature only; slow growth (α≈0.1)
  · g(a) = a(a+1)/2  — triangular of exponent; f(p^k) = k(k+1)/2 (same all p)
  · g(a) = 2^a       — exponential exponent;   f(p^k) = 2^k        (same all p)
  · g(a) = a²         — squared exponent;       f(p^k) = k²         (same all p)
- Dirichlet convolutions involving μ and φ (when convergent)
- Products over unitary divisors (when α < 3.0)

**Dead ends:**
- φ ∘ (∏_{d|n} φ(d)) — non-multiplicative, hard to characterize
- gcd(σ(n), φ(n)) — non-multiplicative, already in OEIS
- lcm(σ(n), φ(n)) — non-multiplicative, complex growth
- σ(rad(n)), rad(σ(n)), Σ rad(d) — sympy's `rad` is symbolic (radians!), not integer radical;
  implement manually: `rad(n) = prod(p for p in factorint(n))`
- φ(n)·σ(n)/n — only integer at specific n; not a well-defined integer sequence
- Σ_{d|n, d sqfree} φ(d) = rad(n) — A007947; see §11
- Σ_{d|n, d sqfree} d = σ(rad(n)) = ∏_{p|n}(1+p) — derivable from known; see §11
- ∏_{d unitary|n} (d+1) — α>3.0 (too fast, out of range)

**Watch list (experimental, unresolved):**
- ∑_{d|n} (d XOR n/d) — non-multiplicative but interesting XOR structure
- ω(n)^{φ(n)} mod n — slow growth, heavily prime-power-dominated
- φ(n)·ω(n) — not multiplicative, but residual f(ab)/(f(a)f(b)) is governed exactly
  by the harmonic mean of ω(a) and ω(b); might be worth characterizing as a type
- Σ_{d unitary} φ(d) = ∏(1 + φ(p^a)) — clean but α≈2.9, too fast growth
- (μ ★ φ)(n) = φ(n) — Möbius inversion, known, score 55 (weak zones problematic)
- ∏_{d unitary} φ(d) — non-multiplicative, α≈2.9, experimental

---

## §11 · Confirmed Classical Identities (Do Not Resubmit)

These were rediscovered by the pipeline and confirmed as known. Do not submit.

| Candidate | Identity | Proof sketch |
|---|---|---|
| id ★ μ | φ(n) | Möbius inversion: id = φ ★ 1, so id ★ μ = φ ★ (1 ★ μ) = φ ★ ε = φ |
| σ ★ μ | n (identity) | Möbius inversion: σ = id ★ 1, so σ ★ μ = id ★ ε = id |
| τ ★ μ | 1 (all-ones) | τ = 1 ★ 1, so τ ★ μ = 1 ★ (1 ★ μ) = 1 ★ ε = 1 |
| \|{unitary divisors of n}\| | 2^{ω(n)} | Direct: unitary divs are ∏_{p\|n} {1, p^a}; count = 2^{ω(n)} |
| Σ_{d unitary} d · φ(n/d) | φ(n)·2^{ω(n)} | Equals Batch 1 candidate; not novel |
| ∏_{p^a ∥ n} (p^a + 1) | unitary σ(n) | ∏(p^a+1) = Σ_{d unitary} d by definition |
| Σ_{d\|n, d sqfree} φ(d) | rad(n) (A007947) | Each prime p^k contributes φ(1)+φ(p)=1+(p-1)=p; product = rad(n) |
| Σ_{d\|n, d sqfree} d | σ(rad(n)) = ∏_{p\|n}(1+p) | Squarefree-divisor sum = ∏(1+p) by multiplicativity |
| J₂(n) = n²·∏(1−1/p²) | A007434 | Jordan totient of order 2; classical |
| Σ_{d|n} φ(d) | n | Known: sum of totients = n (A000027) |

---

## §12 · Parameterized Families

When a sequence is confirmed as part of a parameterized family, note which
parameter values are already in OEIS to guide novelty targeting.

**Family: φ(n)·c^{ω(n)} for integer c ≥ 1**

Multiplicative for any constant c. Prime-power formula: f(p^k) = c·p^{k-1}(p-1).

**Family: Σ_{p^a ∥ n} g(a) for various g (completely additive, prime-signature functions)**

| g(a) | Status | α | f(p^k) |
|---|---|---|---|
| a | Known (A001222 Ω(n)) | 0 | k |
| a² | STRONG | 0.11 | k² |
| a(a+1)/2 | STRONG | 0.10 | k(k+1)/2 |
| 2^a | STRONG | 0.11 | 2^k |
| a! | Untested | — | — |
| F(a) (Fibonacci) | Untested | — | — |

**Family: Σ_{d|n} φ(d)^k for k≥1**

| k | Status | α | f(p^a) |
|---|---|---|---|
| 1 | Known = n (A000027) | 1.0 | p^a |
| 2 | OEIS-READY | 2.0 | 1+(p-1)²(p^{2a}-1)/(p²-1) |

**Family: Σ_{d|n} d^k·φ(n/d)**

| k | Status | α | f(p^a) |
|---|---|---|---|
| 1 | Known = n | 1.0 | p^a |
| 2 | OEIS-READY | 2.0 | p^{2a} + p^{a-1}(p^a - 1) |

When testing a new member of a known family, reduce the novelty check burden by
verifying only the first 30 terms against OEIS before full pipeline.

---

## Appendix: Quick Reference

```python
# Key imports
from sympy import (factorint, totient, divisors, divisor_sigma,
                   divisor_count, isprime, gcd, mobius,
                   primeomega, primenu)
import math

# Core functions (all return Python int, not sympy.Integer)
phi   = lambda n: int(totient(n))
tau   = lambda n: int(divisor_count(n))
sigma = lambda n: int(divisor_sigma(n))
omega = lambda n: int(primenu(n))       # distinct prime factors
Omega = lambda n: int(primeomega(n))    # total with multiplicity
mu    = lambda n: int(mobius(n))

# rad(n) - product of distinct prime factors (NOT sympy.rad which is radians!)
def rad(n):
    if n <= 1: return 1
    result = 1
    for p in factorint(n):
        result *= p
    return result

# Unitary divisors
def unitary_divisors(n):
    return [d for d in divisors(n) if gcd(d, n // d) == 1]

# Multiplicativity test
MULT_PAIRS = [(2,3),(2,5),(3,5),(4,9),(2,7),(5,9),(4,25),(8,27),
              (9,25),(16,9),(4,49),(8,125),(27,25),(2,15),(4,21)]

def is_multiplicative(fn):
    for a, b in MULT_PAIRS:
        if gcd(a, b) == 1:
            fa, fb, fab = fn(a), fn(b), fn(a*b)
            if fa * fb != fab:
                return False, (a, b, fa, fb, fab)
    return True, None

# Weak zone test (handles sympy.Integer)
WEAK_ZONES = sorted(set(
    [p**k for p in [2,3,5,7,11,13] for k in range(1,6)] +
    [p**a * q**b for p,q in [(2,3),(2,5),(3,5)] for a,b in [(1,1),(2,1),(1,2)]] +
    [12, 24, 60, 120, 360, 720, 840, 2520] +
    [2**k for k in range(1,20)] + [2**k - 1 for k in range(2,15)] +
    [2*3*5, 2*3*7, 2*5*7, 3*5*7, 2*3*5*7]
))

def test_weak_zones(fn):
    failures = []
    for n in WEAK_ZONES:
        try:
            val = fn(n)
            if hasattr(val, 'is_Integer'):  # sympy.Integer
                val = int(val)
            if not isinstance(val, (int, float)) or (isinstance(val, float) and math.isnan(val)):
                failures.append((n, 'non-numeric'))
        except Exception as e:
            failures.append((n, str(e)))
    return failures

# Dirichlet convolution
def dirichlet(f, g, n):
    return sum(f(d) * g(n // d) for d in divisors(n))

# Prime-power profile
def pp_profile(f, primes=(2,3,5,7,11), kmax=7):
    for p in primes:
        vals = [f(p**k) for k in range(1, kmax+1)]
        ratios = [round(vals[i+1]/vals[i], 5) if vals[i] != 0 else None
                  for i in range(len(vals)-1)]
        print(f"p={p}: {vals}")
        print(f"      ratios: {ratios}")

# Growth exponent (log-space regression)
def growth_alpha(f, lo=10, hi=200):
    pts = [(n, f(n)) for n in range(lo, hi+1) if f(n) > 0]
    if len(pts) < 10:
        return None
    xs = [math.log(n) for n, _ in pts]
    ys = [math.log(v) for _, v in pts]
    xm = sum(xs) / len(xs)
    ym = sum(ys) / len(ys)
    cov = sum((xs[i] - xm) * (ys[i] - ym) for i in range(len(xs)))
    var = sum((x - xm)**2 for x in xs)
    return round(cov / var, 4) if var > 0 else None

# OEIS string format
def oeis_str(f, count=30):
    return ", ".join(str(f(n)) for n in range(1, count + 1))
```

## Appendix 2: Various analysis

Analyze how the sequence behaves for a(n) where n is odd, n is even, n is a perfect square, n=2^k, n=(2^k)-1, n=(2^k)+1 and a(prime(n)).
