---
name: engineering-problem-solving
description: A rigorous, falsification-first methodology for tackling hard problems in engineering, software, systems, and applied science — debugging, algorithm design, formal/mathematical investigation, security research, and architecture decisions. Use this skill whenever the user is stuck on a non-trivial technical problem, asks for a root-cause analysis, wants a design reviewed, is doing iterative code review, is investigating a bug with unclear origin, or is doing exploratory research (math, security, systems) where the path to the answer isn't obvious. Also trigger when the user wants their reasoning process captured alongside the fix — not just the final patch — or asks to log rejected approaches. Do not use for simple, one-shot factual questions or trivial one-line fixes with an obvious cause.
---

# Engineering Problem-Solving

A domain-agnostic method for getting from "something is wrong / unknown" to a
verified answer, without shortcuts that produce false confidence. Applies to
debugging, algorithm/architecture design, formal proofs, combinatorics,
security research, and performance work alike.

Core stance: **truth over comfort**. A wrong answer stated with confidence is
worse than an honest "I don't know yet." Every claim in the final report must
be backed by something reproducible — a test, a trace, a derivation, a
counterexample — not by plausibility.

## 1. Frame the problem before touching anything

- State the observed behavior and the expected behavior as two separate,
  falsifiable statements. If you can't write both precisely, you don't
  understand the problem yet — go get more data, don't guess.
- Identify what class of problem this is: reproducible bug, intermittent/
  race-y bug, design tradeoff, missing proof, performance regression, unknown
  territory (research). The class determines the method below.
- Write down what would count as "solved." Vague success criteria produce
  vague fixes.

## 2. Build the minimal reproduction / minimal model

- Bugs: shrink to the smallest input, smallest call sequence, smallest config
  that still triggers it. Every extra moving part is a confound.
- Math/algorithmic: work the smallest non-trivial case by hand before
  generalizing. Small n reveals structure that asymptotic reasoning hides.
- Systems/architecture: isolate the component under question; don't reason
  about the whole system when the question is local.
- If you can't reduce it, that's a signal the mental model of the system is
  wrong — treat the failure to reduce as data.

## 3. Generate multiple competing hypotheses, not one

- Never commit to the first plausible explanation. List at least 2-3
  candidate root causes before investigating any of them.
- Rank by a cheap discriminating test, not by which one you like. Ask: what
  single observation would rule three of these out at once?
- For each hypothesis, state what evidence would falsify it, before looking
  for evidence that confirms it. Confirmation-seeking is the most common way
  smart people fool themselves.

## 4. Investigate by elimination, not by narrative

- Instrument, don't speculate: add logging/tracing/assertions at the
  boundaries between components rather than reasoning "it's probably X."
- Binary-search the failure: bisect commits, bisect input size, bisect
  code paths. This beats reading code top-to-bottom for anything non-trivial.
- Distinguish **symptom** from **root cause** explicitly. A fix that makes
  the symptom disappear without a mechanistic explanation of why is not done
  — flag it as a workaround, not a fix, until the mechanism is understood.
- For formal/math problems: derive, don't pattern-match. Verify small cases
  numerically before trusting an identity; verify the identity algebraically
  before trusting the numerics. Both directions matter — numeric evidence
  catches algebra mistakes, algebra catches numeric coincidences at small n.

## 5. Verify against ground truth, not against yourself

- Re-derive or re-run independently of the path that produced the candidate
  answer. A proof that only "looks right" on re-reading is not verified — a
  proof that survives an independent derivation or an adversarial test is.
- For code: write the test that would have caught the bug, then confirm it
  fails on the old code and passes on the new code. A fix without a failing-
  then-passing test is a hypothesis, not a fix.
- For sequences/identities/combinatorics: check against known references
  (OEIS, literature) and against independently-written brute-force code for
  small cases, not just against the closed-form derivation.
- Actively look for the counterexample that would break the current answer.
  If you can't find one after real effort, that's evidence, not proof.

## 6. Log rejected alternatives, not just the final answer

- Every real investigation accumulates dead ends that carry information:
  "tried X, ruled out because Y." Keep this alongside the fix/result — it
  prevents re-deriving the same wrong path later and is often the most
  reusable part of the work.
- Structure per candidate: **what was tried → what it predicted → what
  observation contradicted it → why it was rejected**. This is more valuable
  than a narrative of the successful path alone, because it's what makes the
  final answer defensible.

## 7. Report honestly

- State confidence explicitly and calibrate it to the verification actually
  done (unit-tested vs. reasoned-through vs. "should work"). Don't round up.
- Distinguish "fixed" from "mitigated" from "root cause unknown, symptom
  suppressed." Say which one it is.
- If a numeric or empirical claim isn't independently checked, say so rather
  than presenting it as verified.
- No inflation: don't describe an incremental fix as a breakthrough, and
  don't hedge away a genuinely solid result either. Match the language to
  the evidence.

## Quick checklist (apply per problem, not just once at the end)

- [ ] Observed vs. expected stated precisely
- [ ] Minimal repro / minimal case built
- [ ] ≥2 competing hypotheses considered, with a discriminating test chosen
- [ ] Root cause distinguished from symptom
- [ ] Independent verification performed (test, brute-force check, second
      derivation) — not just review of the same reasoning that produced it
- [ ] Rejected alternatives recorded with the reason each was ruled out
- [ ] Confidence in the final report matches the verification actually done
