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
# Language-agnostic mode (no C/C++ syntax awareness):
shrinkray --no-clang-delta ./interestingness.sh program.c
```

Other tools: `creduce` (C/C++, language-aware), `cvise` (creduce successor),
`ddmin` (original algorithm, good reference implementation).

**What reducers operate on:** Shrink Ray works at multiple levels — byte ranges,
lines, tokens, and (with `--clang-delta`) syntax-aware C/C++ constructs. For
structured inputs (JSON, YAML, protobuf), reduce the text representation directly.
Binary inputs need special handling: convert to hex/base64 text, or use a
domain-specific reducer.

---

## Writing Interestingness Tests

### Template (shell)
```sh
#! /bin/sh
# Do NOT use set -eu — the program under test exits non-zero intentionally,
# and set -e will abort the script before you can inspect the result.

output="$(timeout 2s ./my_program "$1" 2>&1)"
rc=$?
[ "$rc" -ne 124 ] || exit 1          # timed out → uninteresting
printf '%s\n' "$output" | grep -q "expected error string" || exit 1
exit 0
```

Key points:
- Capture `rc=$?` explicitly rather than using `|| true` (which silently
  swallows timeout and crash codes you may need).
- Exit `1` (uninteresting) on timeout (`rc=124`) so the reducer doesn't
  treat a hung candidate as a match.
- Use `printf '%s\n'` instead of `echo` for portability when output may
  start with `-` or contain escape sequences.

### The Five Rules

**1. Anchor what "interesting" means precisely.**
Don't just check that outputs differ — check that the *right* output is still
present. Vague interestingness tests cause over-reduction (reducer shrinks past
your bug).
```sh
# BAD — accepts any output difference
test "$slow_out" != "$fast_out" || exit 1

# GOOD — anchors the expected "correct" baseline too
test "$slow_out" = "0d754a56" || exit 1
test "$fast_out" != "0d754a56" || exit 1
```
Shrink Ray checks whether an empty input passes your interestingness test on
startup — if it does, your test is wrong.

**2. Make it fast.**
Reducers can call the interestingness test hundreds of times per second over
hundreds of thousands of attempts. Optimizations that feel minor (disabling core
dumps, skipping slow init, tight `timeout` values) compound significantly.
Rule of thumb: set `timeout` to ~1.5–2× the program's initial runtime. Never
use 60s if the program normally runs in 0.1s.

**3. Guard against non-termination.**
Reducers happily delete loop terminators (`i -= 1`, `break`, `return`), turning
fast programs into infinite loops. Always use `timeout` in your test. If the
reducer stalls without progress, this is almost certainly why.

**4. Handle parallelism.**
Shrink Ray runs interestingness tests in parallel, each in its own temp
directory (it `cd`s into it before calling your script). Avoid writing to
absolute shared paths inside the test. Use `$$` (shell PID) or `mktemp`
for build artifacts, and clean them up on exit:
```sh
trap 'rm -f slow_$$ fast_$$' EXIT
```

**5. Suppress subcommand output.**
Redirect stdout/stderr of programs you build or run to `/dev/null` or a temp
file. Stray output confuses the reducer's progress display.
```sh
cc -std=c99 t.c -o my_binary 2>/dev/null || exit 1
```

### When Shrink Ray rejects your test on the original input

This is the most common first obstacle. Causes and fixes:

| Cause | Fix |
|---|---|
| Hardcoded absolute paths that don't exist in the temp dir | Use paths relative to `$1` or copy needed files in |
| Script assumes CWD contains helper binaries | Use full paths, or copy binaries in at the top |
| Compilation produces no output (missing include) | Check the test manually: `bash -x ./interestingness.sh original_input` |
| Over-strict interestingness test | Run manually on the original; confirm it exits 0 |
| `set -e` aborting on the program under test's non-zero exit | Remove `set -eu` |

---

## Handling Nondeterministic Bugs

Flaky bugs (occur in 1/N runs) are the hardest case. Two strategies:

### Strategy A — "At least once in N runs" (permissive, gets started)
```sh
#! /bin/sh
t="$(mktemp)"
trap 'rm -f "$t"' EXIT

i=5
while [ "$i" -gt 0 ]; do
  python3 "$1" > "$t" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] && grep -q "ZeroDivisionError" "$t"; then
    exit 0
  fi
  i=$((i-1))
done
exit 1
```
This gets the reducer moving. Often it accidentally eliminates the nondeterminism
entirely as a side-effect of simplification.

> Use `rc -ne 0` (any non-zero exit) rather than `-eq 1` unless you need
> to distinguish specific exit codes. Captures crashes, signals, and errors.

### Strategy B — "Every run in N tries" (strict, locks in determinism)
```sh
#! /bin/sh
t="$(mktemp)"
trap 'rm -f "$t"' EXIT

i=5
while [ "$i" -gt 0 ]; do
  python3 "$1" > "$t" 2>&1
  rc=$?
  if [ "$rc" -eq 0 ] || ! grep -q "ZeroDivisionError" "$t"; then
    exit 1
  fi
  i=$((i-1))
done
exit 0
```
Hard to get started (the original input may only pass ~3.6% of the time at
N=3), but once the reducer is on a deterministic path it stays there.

### Recommended workflow for nondeterministic bugs

1. Start with Strategy A.
2. Periodically run the current reduced input manually to see if the error rate
   has increased.
3. When it has (the reducer got lucky and stabilised the bug), **switch to
   Strategy B** by overwriting the interestingness test in place. Shrink Ray
   continues from the current reduced file under the stricter constraint.
4. Intuition: subpaths of reduction tend to converge, so a "bad" (still-flaky)
   reduction is usually caught and discarded shortly after.

---

## Steering by Secondary Metric (Global Counter Technique)

Sometimes input length is the wrong objective. You may want to minimize:
- Trace/log length (lines of JIT output, syscall traces)
- Wall-clock execution time
- Memory usage
- Frequency of nondeterminism

Use a per-invocation temp file for the metric capture (avoids a parallel-write
race) and a shared file for the running best (acknowledged race — acceptable):

```sh
#! /bin/sh
# No set -eu — interpreter exits non-zero intentionally

trace="$(mktemp)"
trap 'rm -f "$trace"' EXIT

# Primary check: must crash (non-zero exit)
./interpreter "$1" 2>"$trace"
rc=$?
[ "$rc" -ne 0 ] || exit 1   # exit 1 (uninteresting) if it did NOT crash

# Secondary metric: trace length in lines
new_len="$(wc -l < "$trace" | tr -d '[:space:]')"

if [ ! -f /tmp/global_best ]; then
  echo "$new_len" > /tmp/global_best
fi
old_len="$(cat /tmp/global_best)"

# Reject if trace got longer (equal is fine — lets the input still shrink)
if [ "$new_len" -gt "$old_len" ]; then
  exit 1
fi

echo "$new_len" > /tmp/global_best
exit 0
```

**Caveats:**
- `/tmp/global_best` has a write race under parallel execution. Accept this —
  it means the metric may occasionally move in the wrong direction, but in
  practice the approach still converges.
- May produce a slightly *larger* input file in exchange for a much better
  secondary metric. That's the point.

**Adapt the metric:**
- Wall time: `{ time ./program "$1" 2>/dev/null; } 2>&1 | grep real | awk '{print $2}'`
- Memory peak: `valgrind --tool=massif` or `/usr/bin/time -v`, extract "Maximum resident"
- Nondeterminism frequency: run N times, count hits, store count as metric
  (lower = more deterministic; reducer will drive toward zero)

---

## Debugging a Stuck Reducer

| Symptom | Likely cause | Fix |
|---|---|---|
| Empty input passes interestingness test | Test too permissive / over-reduction | Tighten the test; add positive output anchors |
| Shrink Ray rejects test on original input | Test fails immediately on original | Run `bash -x ./interestingness.sh original` to diagnose |
| No progress after initial acceptance | Non-termination in reduced candidates | Add `timeout`; check loop terminators |
| Reduction stops early, bug gone | Test accepted a different code path | Add stricter output checks |
| Parallel file collisions | Build artifacts written to shared paths | Use `$$`/`mktemp` + `trap ... EXIT` cleanup |
| Secondary metric explodes | Reducer optimizing length, ignoring metric | Switch to global counter technique |
| `set -e` aborts test early | Shell `-e` fires on program's non-zero exit | Remove `set -eu` from interestingness test |

---

## Quick Reference: Shrink Ray Flags

```bash
# Basic
shrinkray ./test.sh input.txt

# Language-agnostic (no C/Python syntax awareness)
shrinkray --no-clang-delta ./test.sh input.c

# Set parallelism explicitly
shrinkray --parallelism 8 ./test.sh input.txt

# Set a global timeout per subprocess (seconds)
shrinkray --timeout 5 ./test.sh input.txt

# Run in-place (CWD, no temp dir) — requires serial execution or careful test design
shrinkray --in-place --parallelism 1 ./test.sh input.txt

# Quiet output (for scripted use)
shrinkray --volume quiet ./test.sh input.txt
```

Shrink Ray runs each test in its own temp directory by default and `cd`s into
it before calling your script. To resume from a partial reduction, just run
again with the already-reduced file as the new input — it picks up where it
left off.

---

## Example: C Compiler Differential Bug

```sh
#! /bin/sh
# No set -eu — compiled binaries may exit non-zero
trap 'rm -f slow_$$ fast_$$' EXIT

# Compilation: explicit || exit 1, no set -e needed
cc -std=c99 -O2 -DFAST=0 "$1" -o slow_$$ 2>/dev/null || exit 1
cc -std=c99 -O2 -DFAST=1 "$1" -o fast_$$ 2>/dev/null || exit 1

slow_out="$(timeout 1s ./slow_$$)" || exit 1
fast_out="$(timeout 1s ./fast_$$)" || exit 1

test "$slow_out" = "expected_hash" || exit 1
test "$fast_out" != "expected_hash" || exit 1
```

Notes:
- `$$` in binary names prevents collision under parallel reduction.
- `trap ... EXIT` ensures cleanup even on early exit.
- No `set -e` / `set +e` toggling needed — explicit `|| exit 1` is clearer.
- Replace `expected_hash` with the actual output of the slow build on the
  original (unfailed) input.
- Shrink Ray CDs into a temp dir per test, so `./slow_$$` is safe.

---

## Minimal Reducer (when Shrink Ray isn't available)

Useful in CI containers or constrained environments:

```python
#!/usr/bin/env python3
import subprocess, sys, tempfile, os

interestingness = sys.argv[1]
input_file = sys.argv[2]

with open(input_file) as f:
    cur = [l.rstrip('\n') for l in f]

i = 0
while i < len(cur):
    cnd = cur[:i] + cur[i+1:]
    with tempfile.NamedTemporaryFile(mode='w', suffix=os.path.splitext(input_file)[1], delete=False) as p:
        p.write('\n'.join(cnd))
        p.flush()
        result = subprocess.run(
            [interestingness, p.name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    os.unlink(p.name)
    if result.returncode == 0:
        cur = cnd   # keep reduction, retry from same position
    else:
        i += 1      # no reduction possible here, advance

print('\n'.join(cur))
```

This is the ddmin line-deletion loop. Single-threaded, slow on large inputs,
but correct and dependency-free. For faster results: restart from `i=0` each
time a reduction succeeds (costs ~10× more iterations but finds more
reductions).

---

## Further Reading

- [Shrink Ray](https://github.com/DRMacIver/shrinkray) — recommended reducer
- [creduce paper](https://www.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf) — original influential reducer
- [ddmin](https://www.st.cs.uni-saarland.de/publications/files/hildebrandt-issta-2000.pdf) — foundational algorithm
- [Using reducers as fuzzers](https://blog.regehr.org/archives/1284) — surprising dual use
- [Cause reduction](https://users.cs.utah.edu/~regehr/papers/mintest.pdf) — theoretical basis for secondary-metric steering
