---
name: agentic-pbt
description: >
  Autonomously find bugs in Python code using property-based testing (Hypothesis).
  Use this skill whenever the user wants to: find bugs in a Python package or module,
  write property-based tests, generate Hypothesis tests from docstrings/type annotations,
  audit a PyPI package for correctness issues, or apply fuzz-style testing to discover
  edge cases. Trigger on phrases like "find bugs in", "write property tests", "test this
  module with Hypothesis", "audit this package", "what invariants does this function have",
  or any request to systematically test Python code beyond hand-written unit tests.
---

# Agentic Property-Based Testing

An agent workflow for discovering bugs in Python code by inferring invariants from context
and testing them with [Hypothesis](https://hypothesis.readthedocs.io/).

Based on the methodology from:
> *Finding bugs across the Python ecosystem with Claude and property-based testing*
> Maaz et al., NeurIPS 2025 DL4C Workshop. [Paper](https://arxiv.org/abs/2510.09907) · [Repo](https://github.com/mmaaz-git/agentic-pbt)

---

## Setup

```bash
pip install hypothesis pytest
```

Ensure the target package is installed in the current environment before running.

---

## Agent Loop

Work through these phases in order. Use a to-do list to track progress across phases.

### Phase 1: Understand the Target

Given a target (file, module, or function), gather:

1. **Signature** — parameter names, types, defaults
2. **Docstring** — stated preconditions, postconditions, raised exceptions, examples
3. **Type annotations** — infer valid input domains from `int`, `float`, `Optional[X]`, etc.
4. **Callers** — how is this called elsewhere in the codebase? What assumptions do callers make?
5. **Existing tests** — what properties are already tested? What edge cases appear?
6. **Mathematical/domain properties** — distributions, ordering, invertibility, idempotence, etc.

**Key sources of invariant ideas:**
- Inverse operations: `deserialize(serialize(x)) == x`
- Output constraints: non-negative samples, sorted results, bounded values
- Commutativity/associativity: `f(a, b) == f(b, a)`
- Idempotence: `f(f(x)) == f(x)`
- Boundary values implied by the domain (e.g., a probability must be in [0, 1])
- Relationships between outputs: for identity-preserving transforms, hash of different inputs should differ (not a general invariant — hash collisions are valid for arbitrary inputs)

**If no docstring or annotations exist:** infer properties from (a) the function name,
(b) callers and their assertions, (c) return type inferred from the implementation body.
If none of these yield a grounded property, skip the target and log it as
**"insufficient context"** — do not speculate.

**If the target is C/Fortran/Cython-backed** (e.g. numpy, scipy): source reading is unavailable. Use `help(target)` for the docstring, inspect `.pyi` stub files for type annotations, and rely on the official API documentation. Properties must be grounded in docs alone — do not infer from implementation.

---

### Phase 2: Propose Properties

For each property you want to test, write it out in plain language first:

```
Property: numpy.random.wald always returns positive values
Rationale: Wald distribution is supported on (0, ∞); negative output is a bug
Hypothesis strategy: <e.g. st.floats(min_value=1e-9) for mean/scale, st.lists(st.integers()) for sequences>
```

Ground every property in explicit evidence from Phase 1 (docstring quote, math definition,
observed caller assumption). Discard speculative properties with no grounding.

Aim for **3–7 properties per function**. Stop proposing when new candidates require speculation or are strict subsets of an existing property. More is not better — precision beats coverage here.

---

### Phase 3: Write Hypothesis Tests

Create `test_properties.py` in the project root (or a temp directory with the target package installed and importable). Template for each property:

```python
from hypothesis import given, assume, settings, HealthCheck, strategies as st
# import pytest  # add if using pytest.raises or fixtures

@given(
    # specify strategy here
)
# max_examples: 500 is a reasonable default;
#   raise to 2000+ for string/unicode/complex strategies;
#   lower to 100 for slow or expensive functions
@settings(max_examples=500)
def test_<property_name>(<args>):
    result = target_function(<args>)
    # assert the property
    assert <invariant>, f"Failed for input: {<args>!r}, got: {result!r}"
```

**Strategy selection guide:**
| Type annotation | Strategy |
|---|---|
| `int` | `st.integers()` |
| `float` | `st.floats(allow_nan=False, allow_infinity=False)` |
| `str` | `st.text()` |
| `List[T]` | `st.lists(strategy_for_T)` |
| `Dict[K, V]` | `st.dictionaries(k_strategy, v_strategy)` |
| Constrained domain | `st.floats(min_value=1e-9)`, `st.integers(min_value=0)`, etc. |
| `Optional[T]` | `st.one_of(st.none(), strategy_for_T)` |
| `Enum` | `st.sampled_from(MyEnum)` |

Use `assume()` to filter invalid inputs rather than catching exceptions in the test body.
**Never wrap the core assertion in try/except** — this masks bugs.

---

### Phase 4: Run and Reflect

Run each test:

```bash
python -m pytest test_properties.py -v --tb=short
```

For each result:

**If the test fails:**
- Is the failure a real bug, or a test defect?
- Common test defects: missing `assume()`, over-broad strategy, wrong expected value
- If it is a test defect: fix the test and re-run from Phase 3.
- If the test is correct and the failure is reproducible: **real bug** → proceed to Phase 5
- If Hypothesis didn't fully minimize: bisect the counterexample manually in a REPL by simplifying inputs until the assertion still fails. If `assume()` loops are filtering shrunk candidates, replace them with constrained strategies (e.g. `st.integers(min_value=0)` instead of `assume(x >= 0)`). Use `suppress_health_check=[HealthCheck.too_slow]` only if example *generation* (not shrinking) is timing out.

**If the test passes:**
- Is the property non-trivial? (Would it catch a mutation of the code?)
- Did you accidentally mask failures (try/except, wrong assertion)?
- Is `max_examples` high enough for the search space?
- → If all three are satisfied: mark property **confirmed-valid**, move to next property.
- → If any fail: revise the test and re-run from Phase 3.

Self-reflection checklist before logging a bug:
- [ ] No try/except wrapping the assertion
- [ ] Property is grounded in documentation or math, not speculation
- [ ] Counterexample pinned: paste the `@reproduce_failure(...)` decorator verbatim from Hypothesis output — do not substitute values — and verify it reruns deterministically
- [ ] Failure is not explained by known undefined behavior or intentional semantics

---

### Phase 5: Write the Bug Report

For confirmed bugs, produce a structured report:

~~~markdown
## Bug: <short title>

**Package:** <name> <version>
**Hypothesis version:** <output of `python -c "import hypothesis; print(hypothesis.__version__)"`>
**Function:** `<fully.qualified.name>`
**Severity:** [critical | high | medium | low]

### Property Violated
<plain-language statement of the invariant>

### Minimal Reproducer
```python
# paste the shrunk counterexample here
# paste the @reproduce_failure(...) decorator verbatim from Hypothesis output — do not substitute values
```

### Expected Behavior
<what should happen>

### Actual Behavior
<what does happen, including output values>

### Root Cause Hypothesis
<your analysis: is this a numerical issue, logic bug, off-by-one, etc.?>

### Suggested Fix (optional)
<patch or direction>
~~~

---

## Scoring Rubric (for triage)

Score each bug report 0–15 across three axes:

| Axis | 0–5 |
|---|---|
| **Validity** | 0 = almost certainly invalid; 5 = definitively a bug |
| **Severity** | 0 = cosmetic/trivial; 5 = data corruption, security, wrong results in common use |
| **Reproducibility** | 0 = flaky/unreproducible; 5 = deterministic minimal reproducer in hand |

Prioritize reports scoring ≥ 10 for human review and upstream filing.
Discard reports scoring ≤ 5. For scores 6–9: keep in a low-priority backlog but do not file upstream without additional manual validation.

---

## Known Failure Modes

- **Implicit semantics:** If a function's behavior is intentionally surprising (e.g., Julian vs.
  Gregorian calendars), the agent may flag valid behavior as a bug. Always check maintainer docs.
- **Numerical edge cases:** `NaN`, `inf`, and subnormal floats trigger many false positives.
  Filter with `st.floats(allow_nan=False, allow_infinity=False)` (preferred) or add `import math` and use `assume(math.isfinite(x))` unless testing float behavior specifically.
- **Mutable defaults / side effects:** Some functions mutate inputs; test on copies if needed.
- **Stochastic functions:** Hypothesis prints a `@reproduce_failure(...)` decorator on any failure — paste it verbatim to pin a specific counterexample for filing. `@settings(database=None)` is a separate concern (CI isolation, prevents Hypothesis re-trying past failures) — it does not substitute for `@reproduce_failure` and should not be used as a reproducibility mechanism.

---

## Example Bugs Found (reference)

| Package | Function | Bug | Fix |
|---|---|---|---|
| numpy | `random.wald` | Returns negative values (catastrophic cancellation) | [PR #29609](https://github.com/numpy/numpy/pull/29609) |
| aws-lambda-powertools | `slice_dictionary` | Returns first chunk repeatedly | [PR #7246](https://github.com/aws-powertools/powertools-lambda-python/pull/7246) |
| cloudformation-cli | `item_hash` | Always returns `hash(None)` due to in-place `.sort()` | [PR #1106](https://github.com/aws-cloudformation/cloudformation-cli/pull/1106) |
| huggingface/tokenizers | `calculate_label_colors` | Missing closing paren → invalid HSL CSS | [PR #1853](https://github.com/huggingface/tokenizers/pull/1853) |
