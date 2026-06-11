---
name: test-case-reducer
description: >
  Apply test-case reduction techniques to shrink failing inputs and isolate bugs.
  Use this skill whenever the user has a crashing input they want to minimize,
  wants to write or improve an interestingness test, is debugging a nondeterministic
  or flaky failure, wants to steer reduction by a secondary metric (trace length,
  wall-clock time, nondeterminism frequency), or is trying to understand why their
  reducer is over-reducing, looping, or not making progress. Trigger on phrases like
  "reduce this test case", "shrink this input", "write an interestingness test",
  "creduce / shrinkray / ddmin", "my bug is nondeterministic", "reduce by trace size",
  or any request to isolate the root cause of a bug through automated input minimization.
---

# Test-Case Reduction Skill

Test-case reducers automatically shrink failing inputs to the smallest version that
still triggers the bug. 95–99% size reductions are common. The reducer has zero
understanding of *why* its reductions work — and that's the source of its power:
it generalizes to any text-based input.

---

## Core Concepts

**Three inputs to a reducer:**
1. The program under test (or build+run script)
2. The failing input (file to be shrunk)
3. An **interestingness test** — a script that exits `0` if the reduced input still
   manifests the bug, non-`0` otherwise

The reducer tries ever-shorter versions of the input, calling the interestingness
test on each candidate.

**Recommended tool:** [Shrink Ray](https://github.com/DRMacIver/shrinkray)
```bash
pipx install shrinkray
shrinkray ./interestingness.sh failing_input.txt
# For C without clang-delta (language-agnostic mode):
shrinkray --no-clang-delta ./interestingness.sh program.c
```

Other tools: `creduce` (C/C++, language-aware), `ddmin` (original algorithm),
`cvise` (creduce successor).

---

## Writing Interestingness Tests

### Template (shell)
```sh
#! /bin/sh
set -eu
# Run the program on the candidate input ($1)
output="$(timeout 2s ./my_program "$1" 2>&1)" || exit 1
# Check the error is still present
echo "$output" | grep -q "expected error string" || exit 1
exit 0
```

### The Four Rules

**1. Anchor what "interesting" means precisely.**
Don't just check that outputs differ — check that the *right* output is still present.
Vague interestingness tests cause over-reduction (reducer shrinks past your bug).
```sh
# BAD — accepts any output difference
test "$slow_out" != "$fast_out" || exit 1

# GOOD — anchors the expected "correct" baseline too
test "$slow_out" = "0d754a56" || exit 1
test "$fast_out" != "0d754a56" || exit 1
```
Shrink Ray checks whether an empty input passes your interestingness test on startup —
if it does, your test is wrong.

**2. Make it fast.**
Reducers can run the interestingness test hundreds of times per second.
Optimizations that feel minor (disabling core dumps, skipping slow init, using
`timeout` aggressively) compound over hundreds of thousands of attempts.
Rule of thumb: set `timeout` to ~1.5–2× the program's initial runtime, never 60s
if the program runs in 0.1s.

**3. Guard against non-termination.**
Reducers happily delete loop terminators (`i -= 1`, `break`, `return`), turning
a fast program into an infinite loop. Always use `timeout` in your test.
If the reducer stalls without making progress, non-termination is almost certainly why.

**4. Handle parallelism.**
Shrink Ray runs interestingness tests in parallel, each in its own temp directory.
Avoid writing to shared paths inside the test (e.g., `./slow`, `./fast` as output
binaries). Use `$1`-relative temp files or Shrink Ray's temp dir.

---

## Handling Nondeterministic Bugs

Flaky bugs (occur in 1/N runs) are the hardest case. Two strategies:

### Strategy A — "At least once in N runs" (permissive, gets started)
```sh
#! /bin/sh
i=5
while [ "$i" -gt 0 ]; do
  t="$(mktemp)"
  python3 "$1" > "$t" 2>&1
  if [ "$?" -eq 1 ] && grep -q "ZeroDivisionError" "$t"; then
    rm "$t"; exit 0
  fi
  rm "$t"
  i=$((i-1))
done
exit 1
```
This gets the reducer moving. Often it accidentally eliminates the nondeterminism
entirely as a side-effect of simplification.

### Strategy B — "Every run in N tries" (strict, locks in determinism)
```sh
#! /bin/sh
i=5
while [ "$i" -gt 0 ]; do
  t="$(mktemp)"
  python3 "$1" > "$t" 2>&1
  if [ "$?" -ne 1 ] || ! grep -q "ZeroDivisionError" "$t"; then
    rm "$t"; exit 1
  fi
  rm "$t"
  i=$((i-1))
done
exit 0
```
Hard to get started (low probability the original input passes), but once the
reducer is on a good path it stays there.

### Recommended workflow for nondeterministic bugs

1. Start with Strategy A.
2. Periodically run the current reduced input manually to see if the error rate
   has increased.
3. When it has (i.e. the reducer got lucky), **switch to Strategy B** by overwriting
   the interestingness test in place. Shrink Ray will continue from the current
   reduced file with the stricter constraint.
4. The intuition: subpaths of reduction tend to converge, so a "bad" (still-flaky)
   reduction usually gets caught and discarded shortly after.

---

## Steering by Secondary Metric (Global Counter Technique)

Sometimes input length is the wrong objective. You may want to minimize:
- Trace/log length (lines of JIT output, syscall traces)
- Wall-clock execution time
- Number of nondeterministic paths
- Memory usage

Use a shared counter file as a side-channel to steer the reducer:

```sh
#! /bin/sh
set -eu

# Primary check: must still crash
./interpreter "$1" 2>/tmp/trace_output || exit 1

# Secondary metric: number of lines in trace output
new_len="$(wc -l < /tmp/trace_output | tr -d ' ')"

if [ ! -f /tmp/global_best ]; then
  echo "$new_len" > /tmp/global_best
fi
old_len="$(cat /tmp/global_best)"

# Reject if trace got LONGER (equal is fine — lets input still shrink)
if [ "$new_len" -gt "$old_len" ]; then
  exit 1
fi

echo "$new_len" > /tmp/global_best
exit 0
```

**Caveats:**
- Unsound under parallel execution (race on `/tmp/global_best`). Accept this.
- Can produce a slightly *larger* input file in exchange for a much better secondary metric.
- Highly effective in practice despite the unsoundness — use it without guilt.

**Adapt the metric** by replacing the `wc -l` line with whatever proxy fits:
- Wall time: `{ time ./program "$1"; } 2>&1 | grep real | awk '{print $2}'`
- Memory peak: wrap with `/usr/bin/time -v` and extract "Maximum resident"
- Nondeterminism frequency: run N times and count how often the error appears

---

## Debugging a Stuck Reducer

| Symptom | Likely cause | Fix |
|---|---|---|
| Empty input passes interestingness test | Over-reduction / test too permissive | Tighten the test; add positive anchors |
| No progress at all | Non-termination in reduced candidates | Add `timeout`; check loop terminators |
| Reduction stops early, bug gone | Test accepted a different code path | Add stricter output checks |
| Reduction oscillates | Parallel race on shared files | Move shared state out or serialize |
| Secondary metric explodes | Reducer optimizing length, ignoring metric | Switch to global counter technique |

---

## Quick Reference: Shrink Ray Options

```bash
# Basic
shrinkray ./test.sh input.txt

# Language-agnostic (no C/Python syntax awareness)
shrinkray --no-clang-delta ./test.sh input.c

# Set parallelism explicitly
shrinkray -j 8 ./test.sh input.txt

# Resume from a previous partial reduction
shrinkray --best input.reduced.txt ./test.sh input.txt
```

Shrink Ray runs each test in its own temp directory automatically — no need to
handle that in your interestingness test.

---

## Example: C Compiler Differential Bug

```sh
#! /bin/sh
set -eu
cp "$1" t.c
cc -std=c99 -O2 -DFAST=0 t.c -o slow 2>/dev/null || exit 1
cc -std=c99 -O2 -DFAST=1 t.c -o fast 2>/dev/null || exit 1
slow_out="$(timeout 1s ./slow)" || exit 1
fast_out="$(timeout 1s ./fast)" || exit 1
test "$slow_out" = "expected_hash" || exit 1
test "$fast_out" != "expected_hash" || exit 1
```

Replace `expected_hash` with the actual output of the slow build on the original input.

---

## Further Reading

- [Shrink Ray](https://github.com/DRMacIver/shrinkray) — recommended reducer
- [creduce paper](https://www.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf) — original influential reducer
- [ddmin](https://www.st.cs.uni-saarland.de/publications/files/hildebrandt-issta-2000.pdf) — foundational algorithm
- [Using reducers as fuzzers](https://blog.regehr.org/archives/1284) — surprising dual use
- [Cause reduction](https://users.cs.utah.edu/~regehr/papers/mintest.pdf) — theoretical basis for secondary-metric steering
