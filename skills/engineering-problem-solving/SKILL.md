---
name: engineering-problem-solving
description: A rigorous, falsification-first methodology for tackling hard problems in engineering, software, systems, and applied science — debugging, algorithm design, formal/mathematical investigation, security research, and architecture decisions. Use this skill aggressively whenever the user is stuck on a non-trivial technical problem, asks for root-cause analysis, wants a design or PR reviewed, is doing iterative code review, is chasing a bug with unclear or intermittent origin, is verifying a mathematical identity or sequence, or is doing exploratory research (math, security, systems) where the path to the answer isn't obvious. Trigger even if the user just describes symptoms without asking for a "method" by name — "this is failing and I don't know why," "does this proof hold," "is this design sound" all qualify. Also trigger when the user wants their reasoning process captured alongside the fix, wants rejected approaches logged, or is doing a multi-round review cycle. Do not use for simple one-shot factual questions or trivial one-line fixes with an obvious, already-confirmed cause.
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
- Binary-search the failure — concretely:
  - Regression in history: `git bisect start`, mark good/bad, automate the
    check with `git bisect run <script>` if the failure is scriptable.
  - Regression in input size/shape: shrink by half repeatedly, not linearly.
  - Intermittent/race-y: reproduce under a stressor (loop N times, add
    artificial delay/jitter at suspected boundary) before trusting "it's
    fixed" — a race that doesn't reproduce isn't confirmed fixed, just
    unconfirmed.
  - This beats reading code top-to-bottom for anything non-trivial.
- Distinguish **symptom** from **root cause** explicitly. A fix that makes
  the symptom disappear without a mechanistic explanation of why is not done
  — flag it as a workaround, not a fix, until the mechanism is understood.
- For formal/math problems: derive, don't pattern-match. Verify small cases
  numerically (a short brute-force script, or an OEIS b-file cross-check)
  before trusting an identity; verify the identity algebraically before
  trusting the numerics. Both directions matter — numeric evidence catches
  algebra mistakes, algebra catches numeric coincidences at small n.
- For security/vuln work: confirm the primitive first (crash, leak, race)
  with a minimal trigger before reasoning about exploitability or impact —
  don't build a severity narrative on an unconfirmed primitive.

## 5. Verify against ground truth, not against yourself

- Re-derive or re-run independently of the path that produced the candidate
  answer. A proof that only "looks right" on re-reading is not verified — a
  proof that survives an independent derivation or an adversarial test is.
- **If you have tool access (shell, code execution, a REPL), execute the
  verification — don't narrate a hypothetical run.** "This test would fail
  on the old code and pass on the new code" is a prediction, not a result.
  Run it, paste the actual output, then draw the conclusion.
- For code: write the test that would have caught the bug, then confirm it
  fails on the old code and passes on the new code. A fix without a failing-
  then-passing test is a hypothesis, not a fix.
- For sequences/identities/combinatorics: check against known references
  (OEIS, literature) and against independently-written brute-force code for
  small cases, not just against the closed-form derivation. Run the
  brute-force script; don't reason about what it would output.
- Actively look for the counterexample that would break the current answer.
  If you can't find one after real effort, that's evidence, not proof.

## 6. Know when to stop or escalate

- Investigation has no natural end point unless you set one. Before
  starting, decide what "enough evidence" looks like for this problem's
  stakes — a one-off script bug needs less than a security-relevant race
  condition.
- Stop generating alternative hypotheses once one has passed an independent
  verification step (Section 5) and the others have been actively falsified,
  not just deprioritized. "I didn't get around to checking the others" is
  not the same as "the others are ruled out."
- Escalate to the user instead of continuing to grind when: the minimal
  repro requires information only they have (production data, intent behind
  a design decision), two hypotheses both survive verification and the
  discriminating test requires resources you don't have (hardware, access,
  time), or the fix requires a tradeoff call (correctness vs. performance vs.
  scope) rather than a technical determination.
- Time-box exploratory/research problems explicitly and report partial
  progress honestly rather than silently converging on a guess to have an
  answer to give.

## 7. Log rejected alternatives, not just the final answer

- Every real investigation accumulates dead ends that carry information:
  "tried X, ruled out because Y." Keep this alongside the fix/result — it
  prevents re-deriving the same wrong path later and is often the most
  reusable part of the work.
- Structure per candidate: **what was tried → what it predicted → what
  observation contradicted it → why it was rejected**. This is more valuable
  than a narrative of the successful path alone, because it's what makes the
  final answer defensible.
- For multi-round investigations (iterative code review, multi-session
  research), persist this log somewhere durable — a file, a commit message,
  a comment block — rather than letting it live only in the conversation.
  A log that vanishes when the session ends has to be re-derived next time.

## 8. Report honestly

- State confidence explicitly and calibrate it to the verification actually
  done (unit-tested vs. reasoned-through vs. "should work"). Don't round up.
- Distinguish "fixed" from "mitigated" from "root cause unknown, symptom
  suppressed." Say which one it is.
- If a numeric or empirical claim isn't independently checked, say so rather
  than presenting it as verified.
- No inflation: don't describe an incremental fix as a breakthrough, and
  don't hedge away a genuinely solid result either. Match the language to
  the evidence.

## Micro-example

Bug report: "flaky test, fails ~1 in 20 CI runs."

1. Frame: expected = deterministic pass; observed = intermittent failure →
   class = race condition, not logic bug.
2. Minimize: loop the test 100x locally with `-race` / thread sanitizer
   enabled instead of waiting on CI.
3. Hypotheses: (a) shared mutable state between test cases, (b) unawaited
   async cleanup, (c) timing-dependent assertion. Discriminating test: run
   tests in isolation vs. in the full suite — if isolation never fails, it's
   (a) or ordering, not (c).
4. Eliminate: isolation run never fails → rules out (c). Instrument the
   suspected shared fixture → observe write from a previous test still
   in flight.
5. Verify: add an explicit teardown barrier, run the stress loop (100x) —
   actually execute it, 0/100 failures vs. 6/100 before.
6. Stop: verified fix, (b) and (c) actively ruled out by the isolation test
   — not just deprioritized. Done.
7. Log: "(c) rejected — isolation run never reproduced it, ruling out pure
   timing" saved in the PR description for the next person who hits this.
8. Report: "Fixed — root cause was missing teardown barrier, confirmed via
   100x stress run, 0 failures. Not a mitigation."

## Quick checklist (apply per problem, not just once at the end)

- [ ] Observed vs. expected stated precisely
- [ ] Minimal repro / minimal case built
- [ ] ≥2 competing hypotheses considered, with a discriminating test chosen
- [ ] Root cause distinguished from symptom
- [ ] Independent verification performed (test, brute-force check, second
      derivation) — not just review of the same reasoning that produced it
- [ ] Rejected alternatives recorded with the reason each was ruled out
- [ ] Stopping point was a deliberate call (verified + others falsified), not
      just running out of time or interest
- [ ] Confidence in the final report matches the verification actually done
