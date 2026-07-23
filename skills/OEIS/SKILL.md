---
name: integer-sequence-research
description: >
  Autonomous research pipeline for discovering, validating, and characterizing
  integer sequences suitable for OEIS submission. Use this skill whenever the
  user wants to generate new sequences from arithmetic constructions, test
  whether a formula is correct, falsify a conjecture about number-theoretic
  functions, check multiplicativity, profile prime-power behavior, or search
  for OEIS collisions. Also covers combinatorics research (Catalan/Motzkin/
  Narayana/Bell families, restricted permutations, lattice paths), prime
  number and prime gap research (gap records, twin primes, Cramér heuristics),
  PSLQ integer-relation search for constant identities, Stirling numbers
  (first and second kind), Bernoulli numbers, factorial prime decomposition
  (Legendre's formula), harmonic and generalized harmonic numbers, and the
  Riemann zeta function (special values, Euler product, high-precision zero
  work), and integer partitions (partition function p(n), restricted and
  colored partitions, Ramanujan congruences, conjugate partitions, rank and
  crank statistics). Also triggers for requests like "find me a new sequence",
  "is this formula right", "does f(n) = phi(n) * 2^omega(n) have a closed form",
  "test this divisor sum for multiplicativity", "is this OEIS-worthy",
  "find an integer relation for this constant", "characterize this prime gap
  sequence", "verify this Stirling/Bernoulli/harmonic identity", or "check
  this partition congruence". The
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

## §13 · Combinatorics Research

Same generator → falsifier → classifier loop as §1–§5, applied to counting
sequences instead of arithmetic functions. The key difference: ground truth
usually comes from **direct enumeration** on small n, not from a second
symbolic formula, so brute-force enumeration is the "definition-based"
implementation (§2.A) and the closed form is the "factorization-based" one
(§2.B).

### 13.1 · Grammar

| Family | Elements |
|---|---|
| **Classical counting** | binomial `C(n,k)`, Catalan `C_n`, Motzkin `M_n`, Narayana `N(n,k)`, Bell `B_n`, Schröder, Delannoy |
| **Structures** | set partitions, restricted permutations (avoiding a pattern, derangements, involutions), lattice paths (Dyck/Motzkin paths), plane trees, non-crossing partitions |
| **Operators** | binomial transform, INVERT transform, Euler transform, boustrophedon transform |
| **Constraints** | pattern avoidance (single/multiple 123-type patterns), bounded height/width, colored variants (k-colored Motzkin, etc.) |

### 13.2 · Ground-Truth-First Workflow

1. **Brute-force enumerate** the combinatorial objects for small n (n ≤ 12–15
   depending on growth rate) — generate every object explicitly, don't just
   trust a recursive count.
2. Derive or guess a closed form / generating function from the counted
   values.
3. Cross-check the closed form against the brute-force counts on the *same*
   range before extending further (mirrors §2's differential validation).
4. Only then extend via the closed form or recurrence to get 100+ terms for
   the OEIS collision check (§6).

### 13.3 · Adversarial Checks Specific to Combinatorics

- **Off-by-one on n=0**: does the sequence start counting at the empty
  structure? Half of all combinatorics bugs live here.
- **Symmetry checks**: many combinatorial arrays are symmetric or
  palindromic by row (Narayana numbers, Eulerian numbers) — a broken
  symmetry is a fast falsifier.
- **Row-sum checks**: if the object is a triangle (Stirling-like, Narayana),
  verify row sums against a known sequence (e.g. Narayana row sums = Catalan,
  Eulerian row sums = n!).
- **Generating function sanity**: if a GF is conjectured, expand it
  symbolically (`sympy.series`) to as many terms as were enumerated and
  diff against the brute-force list.

### 13.4 · Known Identities (Do Not Resubmit)

| Candidate | Identity |
|---|---|
| Row sums of Narayana triangle | Catalan numbers `C_n` |
| Row sums of unsigned Stirling first kind | `n!` |
| Row sums of Stirling second kind | Bell numbers `B_n` |
| Central binomial `C(2n,n)` | A000984 |
| `C(2n,n)/(n+1)` | Catalan A000108 |
| Number of Dyck paths of semilength n | Catalan A000108 |
| `\|Av_n(132,213)\|` (permutations avoiding both 132 and 213) | `2^{n-1}` — confirmed by brute force n=1..8 (§22 Run 3) |
| Number of set partitions with no singleton | related to Bell via inclusion-exclusion; check before submitting |

---

## §14 · Prime Numbers and Prime Gaps Research

### 14.1 · Core Objects

| Object | Definition | OEIS anchor |
|---|---|---|
| `p(n)` | n-th prime | A000040 |
| `π(x)` | prime counting function | A000720 |
| `g(n) = p(n+1) - p(n)` | prime gaps | A001223 |
| Maximal gaps | records in `g(n)` | A005250 (gap value), A005669 (index) |
| Merit `g(n) / ln(p(n))` | normalized gap size | used for record-hunting, not itself an integer sequence |
| Twin primes | `p, p+2` both prime | A001359 / A006512 |
| Prime constellations | k-tuples with fixed admissible pattern | check admissibility (Hardy–Littlewood) before searching |

### 14.2 · Generation and Ground Truth

Use `sympy.nextprime` / `sympy.prevprime` / `sympy.primerange` for ground
truth — never hand-roll a primality sieve for validation purposes, only for
performance-critical generation that is then cross-checked against sympy on
an overlapping range (mirrors §2's dual-implementation rule).

```python
from sympy import primerange, isprime, nextprime

def prime_gaps(limit):
    primes = list(primerange(2, limit))
    return [primes[i+1] - primes[i] for i in range(len(primes) - 1)]
```

### 14.3 · Falsification Specific to Prime Gaps

- **Record claims are the highest-risk output.** A "new maximal gap" claim
  must be verified by regenerating the prime list independently (e.g. via
  Miller–Rabin at high witness count, or a second sieve implementation) —
  do not report a gap record from a single code path.
- **Compare against the Cramér model** (expected max gap near `x` scales as
  `(ln x)^2`) to sanity-check whether an observed gap is plausible or a bug.
- **Off-by-one at the boundary**: verify gap counting includes/excludes the
  correct endpoints; check the first few known values (2,1,2,2,4,2,4,2,4,6...)
  against A001223 before trusting a bulk computation.
- **Twin-prime-like patterns**: verify the constellation pattern is
  *admissible* (no residue class mod every small prime is fully blocked)
  before searching for it — inadmissible patterns provably have finitely
  many (usually zero) instances and will silently return empty or garbage.

### 14.4 · Verified Reference Records (Dogfood-Confirmed)

Independently regenerated via `sympy.primerange` up to 300,000 and cross-checked
against the pipeline's own gap-tracking logic; use this as a fast local sanity
table before trusting a bulk maximal-gap computation elsewhere in this range:

```
(p, gap, merit=gap/ln(p)):
(2,1,1.443)  (3,2,1.821)   (7,4,2.056)   (23,6,1.914)   (89,8,1.782)
(113,14,2.962) (523,18,2.876) (887,20,2.946) (1129,22,3.130) (1327,34,4.728)
(9551,36,3.928) (15683,44,4.555) (19609,52,5.261) (31397,72,6.954) (155921,86,7.192)
```

All 15 match A005250/A005669's published prefix. If a new run disagrees with
this table anywhere in `p ≤ 155921`, the bug is in the new run, not here.

### 14.5 · Worked Constellation Example (Dogfood-Confirmed)

Pattern `(p, p+2, p+6, p+8)` (prime quadruplets) tested for admissibility
(§14.3) and then actually searched, rather than left as a described-but-
unexercised procedure:

- **Admissibility**: no prime `q ≤ 50` blocks every residue class → pattern
  is admissible.
- **Real search to 2,000,000**: 295 quadruplets found; first few start at
  p = 5, 11, 101, 191, 821, 1481, 1871, 2081, 3251, 3461.
- **Hardy–Littlewood cross-check**: numerically integrating the singular-
  series estimate (`C₄ ≈ 4.1512`) over the same range gives ≈365, so the
  actual/estimate ratio is ≈0.81 — the right order of magnitude for a
  heuristic asymptotic at this range (convergence is slow; treat as a
  plausibility check per §14.4's Statistical/Heuristic caveat, not a
  precision match).

### 14.6 · Statistical / Heuristic Checks (Not Proof)

Use these to flag "interesting" candidates for further exploration, never as
a substitute for exact verification:

- Gap distribution vs. Cramér–Granville heuristic model
- Hardy–Littlewood constant estimates for k-tuple density
- Bertrand's postulate as a trivial sanity floor (`p(n+1) < 2 p(n)` must
  always hold — if a generated table violates this, the table is wrong)

---

## §15 · PSLQ / Integer Relation Search

Used to discover (or rule out) linear integer relations among a vector of
real constants — e.g. testing whether some combination of `ζ(3)`, `π²`,
`ln 2`, Catalan's constant `G`, and `γ` satisfies `Σ c_i x_i = 0` for integers
`c_i`. This is the constants-analogue of §1–§6: generate candidate constant
vectors, run the relation search, then adversarially confirm or falsify.

### 15.1 · Tooling

```python
from mpmath import mp, mpf, pslq, zeta, pi, euler, catalan, log

mp.dps = 100  # decimal digits of precision; see §15.3

vec = [zeta(3), pi**2, log(2), catalan, euler, mpf(1)]
relation = pslq(vec, maxsteps=10**6)
```

`pslq` returns `None` if no relation is found within the given precision and
bound, or a list of integer coefficients `c_i` such that `Σ c_i · vec[i] ≈ 0`
to the working precision.

### 15.2 · Candidate Constant Construction

- Mix constants from different "families" (zeta values, logs of small
  integers, Catalan-type constants, algebraic numbers, powers of π) —
  same-family combinations mostly rediscover trivial/known identities.
  Search first for a term like `daedalus/skills` history of resubmitted
  relations before reporting.
- Include a constant `1` in the vector so PSLQ can find relations with a
  free rational/integer term, not only homogeneous ones.
- Prefer small vectors (4–8 constants) — PSLQ's cost and false-positive risk
  both grow with vector length.

### 15.3 · Precision Is the Entire Ballgame

**The single most important rule for this section:** a relation found at
precision `P` digits is only credible if a coefficient vector with
`max|c_i|` bits requires roughly `n · max|c_i-bits|` digits of precision to
distinguish from a numerical coincidence (`n` = vector length). Rules of
thumb:

1. Always run PSLQ at **two different precisions** (e.g. 50 and 100 digits).
   If the same relation (same integer vector, possibly up to sign/scale)
   appears at both, it survives the first falsification pass.
2. After finding a candidate relation, **substitute it back** and evaluate
   the residual at 2–3× the discovery precision. The residual must shrink
   roughly in proportion to the added precision (i.e., actually go to zero),
   not merely stay "small."
3. Reject any relation whose smallest nonzero coefficient is implausibly
   large relative to the precision used — that is the classic PSLQ
   false-positive signature (an artifact of insufficient precision, not a
   real identity).
4. Treat rediscovery of a **known** identity (e.g. Euler's reflection
   formula, standard zeta value relations from §20) as a successful
   validation of the pipeline, not a novel result — check §20.4 and
   standard constant tables before claiming novelty.

### 15.4 · Adversarial Falsification

- Run PSLQ on a vector of algebraically **independent** constants (e.g.
  `π`, `e`, `ln 2`, `ln 3`) as a negative control — it must return `None`
  (or only the trivial/garbage relation at insufficient precision). If it
  "finds" a relation here, precision is too low or the implementation is
  buggy.
- Randomize the order of the input vector; a real relation's coefficients
  permute consistently, a precision artifact often doesn't reproduce.

### 15.5 · Confirmed Negative Results (Dogfood Reference)

Broader constant vectors actually run (not just described) at 50 and 100
digits, both returning no relation at either precision — recorded so a
future pass doesn't re-spend a search budget rediscovering the same
absence of a low-degree relation:

| Vector | Result |
|---|---|
| `[Catalan's constant G, ζ(3), γ, ln2, π, 1]` | no relation found (dps 50, 100) |
| `[ζ(3), π³, 1]` | no relation found (dps 50, 100) — consistent with ζ(3) (Apéry's constant) having no known simple closed form in π |

A clean `None` at two precisions for a *plausible-looking* vector is itself
a useful (negative) result: it's evidence against a simple low-degree
relation existing among those specific constants at that vector length,
not just an untested gap. Widening the vector (more constants) or its
precision is the natural next step if this combination is revisited.

---

## §16 · Stirling Numbers

### 16.1 · Definitions

| Type | Notation | Meaning |
|---|---|---|
| Unsigned first kind | `c(n,k)` or `[n,k]` | number of permutations of n elements with k cycles |
| Signed first kind | `s(n,k)` | coefficients of `x(x-1)...(x-n+1)` (falling factorial expansion) |
| Second kind | `S(n,k)` or `{n,k}` | number of ways to partition an n-set into k nonempty blocks |

### 16.2 · Recurrences (Ground Truth A)

```
c(n,k) = c(n-1,k-1) + (n-1)·c(n-1,k)     # unsigned first kind
s(n,k) = s(n-1,k-1) - (n-1)·s(n-1,k)      # signed first kind
S(n,k) = S(n-1,k-1) + k·S(n-1,k)          # second kind
```

Base cases: `c(0,0)=s(0,0)=S(0,0)=1`; `c(n,0)=s(n,0)=S(n,0)=0` for `n>0`;
`c(n,k)=s(n,k)=S(n,k)=0` for `k>n`.

### 16.3 · Closed Form (Ground Truth B, Second Kind Only)

```
S(n,k) = (1/k!) · Σ_{i=0}^{k} (-1)^i · C(k,i) · (k-i)^n
```

Use this as the independent cross-check against the recurrence (§2-style
dual implementation) — sympy exposes both via `sympy.functions.combinatorial.numbers.stirling`.

### 16.4 · Known Row/Column Identities (Do Not Resubmit)

| Candidate | Identity |
|---|---|
| Row sums of unsigned first kind | `n!` (A000142) |
| Row sums of second kind | Bell numbers (A000110) |
| `S(n,1)` | 1 |
| `S(n,n)` | 1 |
| `S(n,2)` | `2^{n-1} - 1` |
| `S(n,n-1)` | `C(n,2)` |
| `c(n,1)` | `(n-1)!` |
| `Σ_k s(n,k)·x^k` at `x=1` | `0` for `n>1` (falling factorial at x=1 has a zero root unless n≤1) |

### 16.5 · Falsification Checklist

1. Verify recurrence and closed form (second kind) agree for n=1…20, all k.
2. Verify row sums against factorial / Bell numbers.
3. Check sign convention explicitly before submitting — mixing up `s(n,k)`
   (signed) and `c(n,k)` (unsigned) is the single most common submission
   error for this family.

---

## §17 · Bernoulli Numbers

### 17.1 · Definition

Generating function:

```
t / (e^t - 1) = Σ_{n=0}^∞ B_n · t^n / n!
```

**Sign convention warning:** this convention gives `B_1 = -1/2`. The "other"
convention (`t/(1-e^{-t})`) gives `B_1 = +1/2`. State the convention
explicitly in any report — this is the #1 source of disagreement when
cross-checking against a second source.

**Dogfood-confirmed:** implementing the §17.2 recurrence directly and diffing
against `sympy.bernoulli(n)` for n=0..20 produces exactly **one** disagreement
— at n=1 (`-1/2` from the recurrence vs sympy's `+1/2`) — with n=0 and all
n=2..20 agreeing exactly (including B₁₂). This is the textbook signature of a
sign-convention mismatch rather than an implementation bug: a real bug would
also perturb the even-indexed terms or fail von Staudt–Clausen (§17.4), which
it does not. Treat a lone n=1 disagreement as "check your convention," not
"something is broken."

### 17.2 · Recurrence (Ground Truth A)

```
Σ_{k=0}^{n} C(n+1, k) · B_k = 0   for n ≥ 1,   B_0 = 1
```

Solve for `B_n` by isolating the `k=n` term.

### 17.3 · Closed Form via Zeta (Ground Truth B)

```
B_{2n} = (-1)^{n+1} · 2 · (2n)! · ζ(2n) / (2π)^{2n}     for n ≥ 1
```

Cross-check numerator/denominator against `sympy.bernoulli(n)` (exact
rational) — this ties directly into §20 (Riemann zeta).

### 17.4 · Structural Facts (Use as Falsifiers, Not Just Trivia)

- **Odd-index vanishing**: `B_n = 0` for all odd `n ≥ 3`. Any nonzero
  "novel" odd-index Bernoulli-like sequence should be treated as a bug or a
  different (non-Bernoulli) object.
- **von Staudt–Clausen theorem**: the denominator of `B_{2n}` is
  `Π_{(p-1) | 2n} p` (product over primes p such that `p-1` divides `2n`).
  Use this to verify a computed denominator without needing the full
  numerator.
- **Irregular primes**: a prime `p` is irregular if it divides the numerator
  of some `B_{2k}` for `2k ≤ p-3`. Relevant if the research touches
  Bernoulli numerators as a sequence in their own right (A092132 numerators,
  A002445 denominators) — check against known irregular prime tables
  (37, 59, 67, 101, 103, ... ) before claiming a new pattern.

### 17.5 · Weak Zones

Test `n = 0,1,2,3,4,6,8,10,12` explicitly — `B_{12} = -691/2730` is the
classical stress test because 691 is the first "irregular-adjacent"
numerator prime that trips up naive implementations using floating point
instead of exact rationals.

---

## §18 · Factorial Decomposition

### 18.1 · Legendre's Formula (Ground Truth)

The exponent of prime `p` in the factorization of `n!`:

```
e_p(n!) = Σ_{i=1}^{∞} floor(n / p^i)          (finite sum, stops when p^i > n)
        = (n - s_p(n)) / (p - 1)               (s_p(n) = digit sum of n in base p)
```

Both forms must agree — use the digit-sum form as the independent
cross-check (§2-style dual implementation) against the floor-sum form.

```python
def legendre_exponent(n, p):
    e, pk = 0, p
    while pk <= n:
        e += n // pk
        pk *= p
    return e

def digit_sum_base(n, p):
    s = 0
    while n:
        s += n % p
        n //= p
    return s

def legendre_via_digitsum(n, p):
    return (n - digit_sum_base(n, p)) // (p - 1)
```

### 18.2 · Derived Sequences

| Object | Definition | Notes |
|---|---|---|
| Trailing zeros of `n!` in base 10 | `min(e_2(n!) // 1, e_5(n!))` more precisely `e_5(n!)` since `e_2 ≥ e_5` always | A027868 |
| Trailing zeros in base b | requires factoring `b` and taking `min` over `e_p(n!) / a_p` for each `p^{a_p} ‖ b` | generalizes A027868 |
| `n!` squarefree part / kernel | `∏_{p: e_p(n!) odd} p` | check parity of each `e_p(n!)` |
| Largest `k` such that `k! | n` | inverse problem; brute force upward from `k=1` |

### 18.3 · Falsification Checklist

1. Verify `e_2(n!) ≥ e_p(n!)` for all `p > 2` at the same `n` (2 is always
   the most abundant prime factor of a factorial) — a violation means a bug.
2. Cross-check trailing-zero counts against direct string manipulation
   (`str(math.factorial(n)).rstrip('0')`) for `n` up to a few hundred before
   trusting the Legendre-based formula for larger `n`.
3. Weak zones: `n` = powers of `p` and `p-1` below/above a power (e.g. for
   `p=5`: `n = 24, 25, 26, 124, 125, 126`) — these are where `floor(n/p^i)`
   terms change discontinuously and where off-by-one bugs surface.

---

## §19 · Harmonic Numbers

### 19.1 · Definitions

```
H_n       = Σ_{k=1}^{n} 1/k                  (ordinary harmonic number)
H_n^{(m)} = Σ_{k=1}^{n} 1/k^m                 (generalized / order-m harmonic number)
```

`H_n^{(1)} = H_n`. As `m → ∞` the generalized harmonic numbers relate
directly to `ζ(m)` (§20) since `H_n^{(m)} → ζ(m)` as `n → ∞` for `m > 1`.

### 19.2 · Exact Arithmetic Is Mandatory

Always compute with `fractions.Fraction` (or `sympy.Rational`), never
floats — harmonic number numerators/denominators are OEIS objects in their
own right (A001008 numerators, A002805 denominators), and float
accumulation silently corrupts the denominator's prime structure.

```python
from fractions import Fraction

def harmonic(n, m=1):
    return sum(Fraction(1, k**m) for k in range(1, n + 1))
```

### 19.3 · Structural Falsifiers

- **Wolstenholme's theorem**: for prime `p ≥ 5`, the numerator of `H_{p-1}`
  is divisible by `p²`, and the numerator of the second-order sum
  `Σ_{k=1}^{p-1} 1/k²` is divisible by `p`. Use this as a targeted
  correctness check at `p = 5, 7, 11, 13, ...` — a computed numerator that
  fails this divisibility signals a bug, not a mathematical exception.
- **Denominator growth**: `denominator(H_n) | lcm(1, 2, ..., n)`, with
  equality failing only at specific `n` — verify this containment rather
  than assuming exact equality.
- **Digamma connection**: `H_n = γ + ψ(n+1)` where `ψ` is the digamma
  function — useful as a high-precision numeric cross-check via
  `mpmath.digamma` independent of the exact-fraction computation.

### 19.4 · Known Identities (Do Not Resubmit)

| Candidate | Identity |
|---|---|
| `Σ_{k=1}^{n} H_k` | `(n+1)·H_n - n` (well-known summation identity) |
| `Σ_{k=1}^{n} H_k / k` | `(H_n² + H_n^{(2)}) / 2` |
| `H_n - ln(n)` | → `γ` (Euler–Mascheroni constant) as `n → ∞`; not itself a new sequence |

---

## §20 · Riemann Zeta Function

### 20.1 · Scope and Caution

This section covers **numerical and special-value** work with `ζ(s)` —
computing special values, verifying identities, and locating zeros to high
precision. It does **not** cover, and this skill should not be used to
claim, progress on the Riemann Hypothesis itself. Zero-location work is
purely numerical verification (checking known zeros / hunting for
counterexamples to RH within a numerically verified range), never a
symbolic proof attempt.

### 20.2 · Special Values (Ground Truth via Known Closed Forms)

```
ζ(2)  = π²/6
ζ(4)  = π⁴/90
ζ(2k) = (-1)^{k+1} · B_{2k} · (2π)^{2k} / (2 · (2k)!)     (ties to §17.3)
ζ(-1) = -1/12
ζ(-2k) = 0   for k ≥ 1  (trivial zeros)
ζ(0)  = -1/2
```

Cross-check any computed `ζ(2k)` against the Bernoulli-number closed form
(§17.3) — this is the primary dual-implementation check for even integer
arguments.

### 20.3 · Numerical Tooling

```python
from mpmath import mp, zeta, mpc

mp.dps = 50  # working precision; raise for zero-hunting (§20.5)

# Euler product sanity check (finite truncation) for Re(s) > 1
def euler_product_approx(s, num_primes=2000):
    from sympy import primerange
    from mpmath import mpf
    result = mpf(1)
    for p in primerange(2, num_primes):
        result *= 1 / (1 - mpf(p) ** (-s))
    return result
```

The Euler product only converges for `Re(s) > 1`; use it strictly as a
sanity check against `mpmath.zeta(s)` there, never as a definition for
`Re(s) ≤ 1` (that requires analytic continuation, which `mpmath.zeta`
already handles correctly).

### 20.4 · Known Relations (Do Not Resubmit)

| Candidate | Identity |
|---|---|
| `ζ(2)` | `π²/6` (Basel problem) |
| `ζ(2k)/π^{2k}` rational for all `k≥1` | consequence of §17.3; the rational values themselves (A046988/A002432-type numerator/denominator pairs) are already in OEIS |
| `ζ(s)·(1-2^{1-s})` | Dirichlet eta function `η(s)`; standard, not novel |
| Trivial zeros | negative even integers |
| Functional equation | `ζ(s) = 2^s π^{s-1} sin(πs/2) Γ(1-s) ζ(1-s)` |

### 20.5 · Falsification / Verification for Zero Work

1. **Always verify against a published table** of the first N nontrivial
   zeros' imaginary parts (widely available to high precision) before
   reporting a "new" zero location — the first few are approximately
   14.134725, 21.022040, 25.010858...; a computed value that doesn't match
   these to the working precision indicates an implementation bug, not a
   discovery. **Dogfood-confirmed through zero 10** (imaginary parts up to
   ≈49.7738), all matching the known table and all on `Re(s)=1/2` — see
   §22 Run 3.
2. Zero-finding must report the **precision used** and the **verification
   method** (e.g. sign change of `Z(t)` the Riemann–Siegel function, or
   root isolation via `mpmath.findroot` seeded near a known approximate
   location) — a zero claimed without a stated precision is not
   verifiable and should be discarded per §7's scoring philosophy.
3. Treat any claimed zero off the critical line `Re(s) = 1/2` within
   verified numerical range as **overwhelmingly likely to be a bug**
   (RH has been numerically verified for a very large number of zeros) —
   apply the same "guilty until proven robust" prior from the skill's
   core philosophy, and re-derive with an independent high-precision
   implementation before reporting anything.

---

## §21 · Integer Partitions

### 21.1 · Core Objects

| Object | Definition | OEIS anchor |
|---|---|---|
| `p(n)` | number of partitions of n (order doesn't matter) | A000041 |
| `p(n,k)` | partitions of n into exactly k parts | A008284 |
| `q(n)` | partitions into distinct parts | A000009 |
| Partitions into odd parts | equals `q(n)` (Euler's theorem, §21.5) | A000009 |
| Conjugate partition | transpose of the Young diagram; swaps "largest part" with "number of parts" | — |
| Rank | `largest part − number of parts` (Dyson's rank) | used for congruence explanations |
| Crank | Andrews–Garvan statistic explaining all three Ramanujan congruences | — |

### 21.2 · Generating Function (Conceptual Ground Truth)

```
Σ p(n) x^n = ∏_{k=1}^∞ 1/(1 - x^k)
```

Restricted variants swap the product range/step: distinct parts →
`∏(1+x^k)`; odd parts only → `∏_{k odd} 1/(1-x^k)`; parts ≤ m →
truncate the product at `k=m`.

### 21.3 · Two Independent Implementations (§2-Style Dual Check)

**A. Pentagonal number recurrence** (fast, exact, no partition objects
generated — analogous to the "factorization-based" implementation in §2.B):

```python
def pentagonal_recurrence(N):
    p = [0]*(N+1)
    p[0] = 1
    for n in range(1, N+1):
        total, k = 0, 1
        while True:
            g1 = k*(3*k-1)//2
            g2 = k*(3*k+1)//2
            if g1 > n and g2 > n:
                break
            sign = 1 if k % 2 == 1 else -1
            if g1 <= n: total += sign * p[n-g1]
            if g2 <= n: total += sign * p[n-g2]
            k += 1
        p[n] = total
    return p
```

Uses Euler's pentagonal number theorem:
`p(n) = Σ_{k≠0} (-1)^{k+1} p(n - k(3k-1)/2)`, generalized pentagonal
numbers `k(3k-1)/2` for `k = 1,-1,2,-2,3,-3,...`.

**B. Direct enumeration / DP over parts** (definition-based, §2.A analogue)
— restricted-partition DP, e.g. for distinct-parts or bounded-part variants:

```python
def count_partitions_odd_parts(n):
    dp = [0]*(n+1); dp[0] = 1
    for o in range(1, n+1, 2):
        for s in range(o, n+1):
            dp[s] += dp[s-o]
    return dp[n]
```

Cross-check A against `sympy.functions.combinatorial.numbers.partition`
(the modern location; `sympy.npartitions` is deprecated) before trusting a
hand-rolled recurrence at scale.

### 21.4 · Falsification Specific to Partitions

- **p(0) = 1, not 0** — the empty partition is a valid partition of 0; this
  is the single most common off-by-one in partition code (mirrors the
  n=0 edge case rule of §4.4).
- **Weak zones**: pentagonal numbers themselves (`1, 2, 5, 7, 12, 15, 22,
  26, ...`) and their neighbors — recurrence implementations most often
  break exactly at these indices since that's where the sign/term pattern
  changes.
- **Growth sanity**: `p(n)` grows like `exp(π√(2n/3)) / (4n√3)` (Hardy–
  Ramanujan asymptotic) — a computed value wildly off this envelope at
  moderate n (≥50) signals a bug rather than a genuinely different
  sequence.
- **Congruence checks as fast correctness probes** (§21.5) — cheaper than
  re-deriving p(n) independently, and catch a large class of off-by-one and
  indexing bugs immediately.

### 21.5 · Known Identities and Congruences (Do Not Resubmit)

| Candidate | Identity |
|---|---|
| Partitions into distinct parts | equals partitions into odd parts (Euler, A000009) |
| Self-conjugate partitions | equal partitions into distinct odd parts |
| `p(n,k)` summed over k | `p(n)` |
| `p(n,1)` | 1 |
| `p(n,2)` | `floor(n/2)` |
| `p(n,n)` | 1 (all parts = 1) |
| `p(n,n-1)` | 1 |
| Ramanujan's congruences | `p(5n+4) ≡ 0 (mod 5)`; `p(7n+5) ≡ 0 (mod 7)`; `p(11n+6) ≡ 0 (mod 11)` |
| Partitions with parts differing by ≥2 | equal partitions into parts `≡ 1, 4 (mod 5)` — first Rogers–Ramanujan identity, confirmed n=0..20 (§22 Run 3) |

Ramanujan's three congruences are explained uniformly by the crank
statistic (Andrews–Garvan): the crank mod 5/7/11 partitions the residue
classes evenly. If a "new" congruence is conjectured for a modulus outside
{5,7,11} (or a prime power thereof, per later work by Ono and others),
treat it with extra suspicion — check the literature before claiming
novelty, since sporadic-looking partition congruences are a well-mined area.

### 21.6 · Dogfood-Confirmed (Run 2)

Verified directly: the pentagonal-number recurrence (§21.3.A) matches
`sympy`'s partition function exactly for n=0..60 (0 mismatches); all three
Ramanujan congruences hold on every tested residue in range (5n+4 up to
n=11, 7n+5 up to n=7, 11n+6 up to n=30); and Euler's distinct-parts/
odd-parts equality holds exactly for n=1..20 via two independent DP
implementations. See §22.3 for the consolidated log entry.

---

## §22 · Dogfood Validation Log

This section is updated whenever §13–§20 are actually exercised end-to-end
against real computation (not just read) — same spirit as §10's meta-insight
tracking, but for the newer research domains rather than arithmetic-function
sequence generation.

### 22.1 · Run 1 (initial validation of §13–§20)

Full pipeline exercised with real code (sympy + mpmath) across all eight new
sections in one pass. Every check either confirmed a known identity/theorem
or correctly rejected a negative control — this run's purpose was validating
the *methodology itself*, not discovering novel sequences.

| Section | Check | Result |
|---|---|---|
| §13 Combinatorics | Brute-force 132-avoiding permutations (n=1..8) vs Catalan | Exact match |
| §14 Prime gaps | First 10 gaps vs A001223; Bertrand's postulate to 300,000; 15 maximal-gap records vs A005250/A005669 | All match (see §14.4) |
| §15 PSLQ | `[ζ(2), π², 1]` at 50 and 100 digits | Stable relation `[-6,1,0]` at both precisions (⇒ 6ζ(2)=π²) |
| §15 PSLQ | Negative control `[π, e^γ-family, ln2, 1]` | Correctly returned no relation |
| §16 Stirling | Recurrence vs closed form, n,k ≤ 15; row sums vs Bell numbers | 0 mismatches; row sums match exactly |
| §17 Bernoulli | Recurrence vs `sympy.bernoulli`, n=0..20; von Staudt–Clausen denominators n=1..6 | 1 expected sign-convention mismatch at n=1 (see §17.4); all else exact |
| §18 Factorial decomposition | Legendre vs digit-sum, 45 (n,p) pairs incl. weak zones; trailing zeros n<300 vs string method | 0 mismatches |
| §19 Harmonic numbers | Wolstenholme's theorem, p=5,7,11,13,17,19,23 | Holds for every tested prime |
| §20 Zeta | ζ(2)=π²/6; ζ(2k) via Bernoulli formula k=1..4; truncated Euler product (3000 primes) vs ζ(2),ζ(3); first 3 nontrivial zeros vs known table | All match; zeros confirmed on Re(s)=1/2 |

**Takeaway:** no section required a methodology fix. The only flagged item
(Bernoulli n=1) was correctly diagnosable as a documented convention
difference rather than a bug, which is itself a validation of §17.4's
warning — the pitfall is real and reproduces on the first attempt, not a
hypothetical.

### 22.2 · Run 2 (validation of §21 Integer Partitions)

| Check | Result |
|---|---|
| Pentagonal recurrence vs `sympy` partition function, n=0..60 | 0 mismatches |
| `p(5n+4) ≡ 0 (mod 5)`, n=0..11 | Holds for every tested n |
| `p(7n+5) ≡ 0 (mod 7)`, n=0..7 | Holds for every tested n |
| `p(11n+6) ≡ 0 (mod 11)`, n=0..30 | Holds for every tested n |
| Euler distinct-parts = odd-parts, n=1..20 (two independent DP implementations) | Exact match at every n |

**Takeaway:** same pattern as Run 1 — the pentagonal recurrence and all
three Ramanujan congruences confirmed on first attempt with no
implementation fixes needed. No novel partition-related sequence was
generated in this run; still open for a future pass (e.g. a genuinely new
restricted-partition variant, per §21's grammar).

### 22.3 · Run 3 (resolving the prior open follow-ups)

Each item explicitly left open after Run 1 was actually exercised this
time, rather than re-validating already-confirmed sections:

| Follow-up | What was run | Result |
|---|---|---|
| §13: novel pattern-avoidance class | Brute-force `Av(132,213)` (double avoidance, not tested before), n=1..8 | `= 2^{n-1}` exactly (now in §13.4) |
| §14: constellation admissibility on a real search | Prime quadruplet pattern `(0,2,6,8)`: admissibility check + real search to 2,000,000 | Admissible; 295 quadruplets found; Hardy–Littlewood ratio ≈0.81 (now §14.5) |
| §15: broader PSLQ vector | `[G, ζ(3), γ, ln2, π, 1]` and `[ζ(3), π³, 1]` at dps 50 and 100 | No relation found at either precision, both vectors (now §15.5) |
| §20: zeros beyond the first 3 | Zeros 4 through 10 | All match known table, all on `Re(s)=1/2` (now folded into §20.5) |
| §21: new restricted-partition variant | First Rogers–Ramanujan identity (min-gap-2 partitions vs. parts ≡1,4 mod 5), n=0..20, two independent implementations | Confirmed exactly (now in §21.5) |

**Takeaway:** this run pushed past re-validation into genuinely
not-yet-tried territory (the gaps identified after Run 1) and every result landed on
a side of "confirms known math" — none were bugs, and none were novel
discoveries. The PSLQ negative results (§15.5) are the most valuable
outcome of this run precisely *because* they're negative: they save a
future pass from re-searching the same constant combinations.

### 22.4 · Open Follow-Ups (as of Run 3)

- §13: still no genuinely *novel* (not-already-classified) combinatorial
  construction has been generated — every construction tried so far
  (§21.4's example included) turned out to be classically known once
  checked. A real generative pass through §13.1's grammar, biased toward
  understudied colored/weighted variants, is still open.
- §14: only one constellation pattern (prime quadruplets) has been
  searched; k-tuples with k≥5 or alternative admissible patterns at the
  same k are untested.
- §15: only two constant-family vectors have been tried; combinations
  involving Stirling-related constants, Bernoulli-derived constants (§17),
  or algebraic irrationals are unexplored.
- §16–§19 (Stirling, Bernoulli, factorial decomposition, harmonic numbers):
  no follow-up runs yet beyond Run 1 — these sections have only ever been
  validated against known recurrences/theorems, never pushed into a
  generative or record-hunting mode the way §14 now has been.

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
