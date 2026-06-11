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

**What reducers operate on:** Shrink Ray works at multiple levels — byte ranges,
lines, tokens, and (with `--clang-delta`) syntax-aware constructs. For structured
inputs (JSON, YAML, protobuf), either reduce the text representation directly or
pre-process to a flat text form first. Binary inputs need special handling (convert
to hex/base64 text, or use a domain-specific reducer).

---

## Writing Interestingness Tests

### Template (shell)
```sh
#! /bin/sh
# No set -eu here — the program under test exits non-zero intentionally
# Run the program on the candidate input ($1)
output="$(timeout 2s ./my_program "$1" 2>&1)" || true
# Check the error is still present
echo "$output" | grep -q "expected error string" || exit 1
exit 0
```

> **Note:** Avoid `set -eu` at the top of interestingness tests. The programs
> you're testing exit non-zero by design, and `set -e` will abort the script
> before you can inspect the result.

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
Avoid writing to shared paths inside the test. Use `$$` (shell PID) or `mktemp`
to create unique filenames for build artifacts, and clean them up at exit.

**5. Suppress subcommand output.**
If your test builds or runs programs, redirect their stdout/stderr to `/dev/null`
or a temp file. Stray output confuses the reducer's progress display and can
cause subtle interestingness false-positives.
```sh
cc -std=c99 t.c -o my_binary 2>/dev/null || exit 1
```

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
  rc=$?
  if [ "$rc" -ne 0 ] && grep -q "ZeroDivisionError" "$t"; then
    rm "$t"; exit 0
  fi
  rm "$t"
  i=$((i-1))
done
exit 1
```
This gets the reducer moving. Often it accidentally eliminates the nondeterminism
entirely as a side-effect of simplification.

> **Exit code:** Use `$rc -ne 0` (any non-zero exit), not `-eq 1`, unless you
> specifically need to distinguish exit codes. Captures crashes, signals, etc.

### Strategy B — "Every run in N tries" (strict, locks in determinism)
```sh
#! /bin/sh
i=5
while [ "$i" -gt 0 ]; do
  t="$(mktemp)"
  python3 "$1" > "$t" 2>&1
  rc=$?
  if [ "$rc" -eq 0 ] || ! grep -q "ZeroDivisionError" "$t"; then
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
# No set -eu — interpreter exits non-zero intentionally

# Primary check: must crash (non-zero exit)
./interpreter "$1" 2>/tmp/trace_output
rc=$?
[ "$rc" -ne 0 ] || exit 1   # exit 1 (uninteresting) if it did NOT crash

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
- Wall time: capture via `{ time ./program "$1" 2>/dev/null; } 2>&1 | grep real | awk '{print $2}'`
- Memory peak: wrap with `/usr/bin/time -v` and extract "Maximum resident"
- Nondeterminism frequency: run N times, count how often the error appears, store count

---

## Debugging a Stuck Reducer

| Symptom | Likely cause | Fix |
|---|---|---|
| Empty input passes interestingness test | Over-reduction / test too permissive | Tighten the test; add positive anchors |
| No progress at all | Non-termination in reduced candidates | Add `timeout`; check loop terminators |
| Reduction stops early, bug gone | Test accepted a different code path | Add stricter output checks |
| Reduction oscillates | Parallel race on shared files | Use `$$`/`mktemp` for build artifacts |
| Secondary metric explodes | Reducer optimizing length, ignoring metric | Switch to global counter technique |
| `set -e` aborts test early | Program-under-test exits non-zero, triggers shell -e | Remove `set -eu` from interestingness test |

---

## Quick Reference: Shrink Ray Options

```bash
# Basic
shrinkray ./test.sh input.txt

# Language-agnostic (no C/Python syntax awareness)
shrinkray --no-clang-delta ./test.sh input.c

# Set parallelism explicitly
shrinkray -j 8 ./test.sh input.txt
```

Shrink Ray runs each test in its own temp directory automatically — no need to
handle that in your interestingness test. If you want to resume from a partial
reduction, point it at the already-reduced output file as the new input.

---

## Example: C Compiler Differential Bug

```sh
#! /bin/sh
# No set -eu — binaries may exit non-zero
set -e  # only for compilation failures — exit early if cc fails
cp "$1" t.c
# Use $$ to avoid collisions under parallel reduction
cc -std=c99 -O2 -DFAST=0 t.c -o slow_$$ 2>/dev/null || exit 1
cc -std=c99 -O2 -DFAST=1 t.c -o fast_$$ 2>/dev/null || exit 1
set +e  # program outputs may be non-zero; don't abort
slow_out="$(timeout 1s ./slow_$$)" || { rm -f slow_$$ fast_$$; exit 1; }
fast_out="$(timeout 1s ./fast_$$)" || { rm -f slow_$$ fast_$$; exit 1; }
rm -f slow_$$ fast_$$
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
