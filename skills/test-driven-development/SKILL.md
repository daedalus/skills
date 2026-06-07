---
name: canon-tdd
description: Apply Kent Beck's Canon TDD workflow when implementing new features, fixing bugs, or any task involving writing or changing code behavior. Use this skill whenever the user wants to do TDD, test-driven development, write tests first, red-green-refactor, or asks how to implement something in a test-driven way. Also trigger when the user mentions "make it pass", "write a failing test", or wants to build something incrementally with tests. Do NOT skip this skill just because the task seems simple — Canon TDD applies to even small changes.
---

# Canon TDD

Kent Beck's canonical TDD workflow. Five steps, executed strictly in order.

## The Loop

```
1. Build a Test List
2. Write ONE test (red)
3. Make it pass (green)
4. Optionally refactor
5. If list non-empty → go to 2
```

---

## Step 1: Test List

Before writing any code or any test, enumerate all behavioral scenarios:

- The happy path
- Edge cases (empty input, nulls, boundary values)
- Error/failure paths (timeouts, missing keys, invalid state)
- Cases where existing behavior must not break

**Write these as plain text descriptions, not code.**

> Mistake: mixing in implementation decisions here. Behavioral analysis only.  
> Mistake: skipping this step. Without it you don't know when you're done.

---

## Step 2: Write ONE Test

Pick **one** item from the list. Convert it to a concrete, runnable, automated test with:
- Setup
- Invocation
- Assertions (tip: write assertions first, work backwards)

This step drives **interface** design decisions — how the behavior is invoked, not how it's implemented.

> Mistake: converting the entire test list to concrete tests before making any pass. Causes rework and kills momentum.  
> Mistake: writing tests without assertions (coverage theater).  
> Mistake: picking tests without strategy. Order matters — start with the simplest case that exercises the core path.

---

## Step 3: Make It Pass

Change the code until the new test and all previous tests pass.

- Simplest implementation that makes it green is fine
- If you discover a new scenario mid-implementation, **add it to the list**, don't detour
- If the new scenario invalidates your approach, consider restarting with a different test order
- Mark the test off the list when green

> Mistake: deleting assertions to fake a pass.  
> Mistake: pasting computed values as expected values (defeats double-checking).  
> Mistake: refactoring while going red→green. Two hats problem — pick one at a time.

---

## Step 4: Optionally Refactor

Now and only now: make implementation design decisions.

- Remove duplication — but duplication is a hint, not a command
- Improve names, extract abstractions, restructure internals
- Stop when it's clean enough for the next test, not when it's perfect

> Mistake: abstracting too soon or too aggressively.  
> Mistake: using refactor time to avoid the next scary test.

---

## Step 5: Repeat

Go back to Step 2. Keep going until the test list is empty and your fear has transmuted into boredom.

---

## Interface vs. Implementation Split

TDD separates two design concerns:

| Concern | When | What |
|---|---|---|
| Interface design | Step 2 (writing the test) | How behavior is invoked |
| Implementation design | Step 4 (refactoring) | How behavior is achieved internally |

Conflating these is the root cause of most TDD struggles.

---

## Picking the Next Test

Test order affects both the programming experience and the final design. Heuristics:

1. **Simplest non-trivial case first** — establishes the interface without complex logic
2. **Degenerate cases early** — empty input, zero, null often reveal structural decisions
3. **One new concept per test** — don't introduce two unknowns at once
4. **Error paths after happy path** — once the core works, harden the edges

---

## What Canon TDD Is Not

- ❌ Writing all tests before writing any code
- ❌ 100% coverage as a goal
- ❌ A substitute for thinking about design
- ❌ Applicable only to unit tests

---

## Quick Reference

```
Test List → [pick one] → Write Test (RED)
                              ↓
                         Make it Pass (GREEN)
                              ↓
                         Refactor (optional)
                              ↓
                    [list empty?] → done
                         ↓ no
                    [pick next] → Write Test
```
