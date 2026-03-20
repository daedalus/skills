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
useful sequences and which are dead ends. Updated after Batch 1 and Batch 2.

**Productive:**
- Dirichlet convolutions involving μ and φ
- Products over unitary divisors
- Functions of the form φ(n)·g(ω(n))
- φ(n)·τ(n) — simple product of two classical multiplicative functions
- n·2^{Ω(n)} — "totally doubled" variant of n; f(p^k) = (2p)^k; exact closed form
- ∏_{p^a ∥ n} (p^a − 1) — generalizes φ beyond squarefree; collapses to φ(n) on squarefrees
- Σ_{d unitary} φ(d) = ∏(1 + φ(p^a)) — clean unitary-φ variant
- (φ ★ φ)(n) = Σ_{d|n} φ(d)·φ(n/d) — Dirichlet self-convolution; prime-power formula
  f(p^k) = p^{k-2}·(p-1)·[2p + (p-1)(k-1)] for k ≥ 2, f(p) = 2(p-1)
- (id ★ φ)(n) = Σ_{d|n} d·φ(n/d) — f(p^k) = p^{k-1}·(p + k(p-1)); f(p) = 2p-1
- Σ_{p^a ∥ n} a² — completely additive, depends only on prime signature; f(p^k) = k²

- Σ_{d|n} φ(d)² — Dirichlet convolution of φ² with 1; f(p^k) = 1+(p-1)²(p^{2k}-1)/(p²-1);
  near-quadratic growth (α≈2)
- Completely additive g(a) family (Σ_{p^a ∥ n} g(a)); prime-signature only; slow growth
  · g(a) = a(a+1)/2  — triangular of exponent; f(p^k) = k(k+1)/2 (same all p)
  · g(a) = 2^a       — exponential exponent;   f(p^k) = 2^k        (same all p)

**Dead ends:**
- φ ∘ (∏_{d|n} φ(d)) — non-multiplicative, hard to characterize
- gcd(σ(n), φ(n)) — non-multiplicative, already in OEIS
- lcm(σ(n), φ(n)) — non-multiplicative, complex growth
- σ(rad(n)), rad(σ(n)), Σ rad(d) — broken by sympy's rad(0) edge case at n=1;
  non-multiplicative with no clean structure even after fixing
- φ(n)·σ(n)/n — only integer at specific n; not a well-defined integer sequence
- Σ_{d|n, d sqfree} φ(d) = rad(n) — A007947; see §11
- Σ_{d|n, d sqfree} d = σ(rad(n)) = ∏_{p|n}(1+p) — derivable from known; see §11
- ∏_{d unitary|n} (d+1) — n=1 edge breaks alt impl; α>3.0 (too fast, out of range)

**Watch list (experimental, unresolved):**
- ∑_{d|n} (d XOR n/d) — non-multiplicative but interesting XOR structure
- ω(n)^{φ(n)} mod n — slow growth, heavily prime-power-dominated
- φ(n)·ω(n) — not multiplicative, but residual f(ab)/(f(a)f(b)) is governed exactly
  by the harmonic mean of ω(a) and ω(b); might be worth characterizing as a type

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

---

## §12 · Parameterized Families

When a sequence is confirmed as part of a parameterized family, note which
parameter values are already in OEIS to guide novelty targeting.

**Family: φ(n)·c^{ω(n)} for integer c ≥ 1**

Multiplicative for any constant c. Prime-power formula: f(p^k) = c·p^{k-1}(p-1).

| c | Status | Notes |
|---|---|---|
| 1 | Known (= φ(n)) | A000010 |
| 2 | Batch 1, score 82 | Likely in OEIS; check before submitting |
| 3 | Batch 2, score 70 | First 20 terms: 1,3,6,6,12,18,18,12,18,36,30,36,36,54,72,24,48,54,54,72 |
| 4 | Batch 3, score 100 | First 20 terms: 1,4,8,8,16,32,24,16,24,64,40,64,48,96,128,32,64,96,72,128 |
| 5 | Batch 3, score 100 | First 20 terms: 1,5,10,10,20,50,30,20,30,100,50,100,60,150,200,40,80,150,90,200 |
| 6 | Untested | Next target |
| 7+ | Untested | Diminishing novelty probability |

**Family: Σ_{p^a ∥ n} g(a) for various g (completely additive, prime-signature functions)**

| g(a) | f(n) | Notes |
|---|---|---|
| a | Ω(n) | A001222 — known |
| a² | Batch 2, score 75 | f(p^k) = k²; depends only on prime signature |
| a(a+1)/2 | Batch 3, score 85 | f(p^k) = T(k) triangular; slow growth α≈0.10 |
| 2^a | Batch 3, score 85 | f(p^k) = 2^k; slow growth α≈0.11 |
| a! | Untested | Fast growth — interesting |
| F(a) (Fibonacci) | Untested | F(1)=1, F(2)=1, F(3)=2, F(4)=3, … |

When testing a new member of a known family, reduce the novelty check burden by
verifying only the first 30 terms against OEIS before full pipeline.

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

# Dirichlet convolution
def dirichlet(f, g, n):
    from sympy import divisors
    return sum(f(d) * g(n // d) for d in divisors(n))

# Completely additive function from exponent map
def additive_from_exp(g, n):
    """f(n) = sum_{p^a || n} g(a)"""
    return sum(g(a) for a in factorint(n).values()) if n > 1 else 0

# Prime-power profile (for multiplicative analysis)
def pp_profile(f, primes=(2,3,5,7,11), kmax=8):
    for p in primes:
        vals = [f(p**k) for k in range(1, kmax+1)]
        ratios = [vals[i+1]/vals[i] for i in range(len(vals)-1)]
        print(f"p={p}: {vals}")
        print(f"      ratios: {[round(r,4) for r in ratios]}")

# Batch OEIS search string (first 20 terms, n=1..20)
def oeis_string(f, start=1, count=20):
    return ", ".join(str(f(n)) for n in range(start, start+count))
```
