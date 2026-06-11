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
lines, tokens, and syntax-aware C/C++ constructs (enabled by default; disable
with `--no-clang-delta`). For structured inputs (JSON, YAML, protobuf), reduce
the text representation directly. Binary inputs need special handling: convert
to hex/base64 text, or use a domain-specific reducer.

---

## Writing Interestingness Tests

### Template (shell)
```sh
#! /bin/sh
# Do NOT use set -eu — the program under test exits non-zero intentionally,
# and set -e will abort the script before you can inspect the result.

output="$(timeout 2s ./my_program "$1" 2>&1)"
rc=$?
[ "$rc" -ne 124 ] || exit 1          # timed out (GNU timeout) → uninteresting
printf '%s\n' "$output" | grep -q "expected error string" || exit 1
exit 0
```

Key points:
- Capture `rc=$?` explicitly; avoid `|| true` which silently swallows exit codes.
- Exit `1` (uninteresting) on timeout. Exit code `124` is GNU coreutils
  `timeout(1)` convention; verify on your platform if using macOS/BSD.
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
By default (without `--in-place`), Shrink Ray runs each interestingness test in
its own temp directory and `cd`s into it before calling your script. Avoid
writing to absolute shared paths. Use `$$` (shell PID) or `mktemp` for build
artifacts, and clean them up on exit:
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

This is the most common first obstacle. Diagnose with `bash -x ./interestingness.sh original_input`.

| Cause | Fix |
|---|---|
| Hardcoded absolute paths absent from temp dir | Use paths relative to `$1`, or copy needed files in at the top of the script |
| Script assumes CWD contains helper binaries | Use full paths; or `export PATH` to include the binary's directory |
| `set -e` firing on the program's non-zero exit | Remove `set -eu` from the test |
| Over-strict check that the original doesn't satisfy | Run manually to confirm it exits 0 |
| Compilation fails silently | Remove `2>/dev/null` temporarily to see the error |

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
  # rc=127 means python3 not found — not a real match
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 127 ] && grep -q "ZeroDivisionError" "$t"; then
    exit 0
  fi
  i=$((i-1))
done
exit 1
```
This gets the reducer moving. Often it accidentally eliminates the nondeterminism
entirely as a side-effect of simplification.

> Use `$rc -ne 0` (any non-zero exit) rather than `-eq 1` unless you need
> to distinguish specific exit codes. Also guard against `rc=127`
> (command not found) which would otherwise be a false positive.

### Strategy B — "Every run in N tries" (strict, locks in determinism)
```sh
#! /bin/sh
t="$(mktemp)"
trap 'rm -f "$t"' EXIT

i=5
while [ "$i" -gt 0 ]; do
  python3 "$1" > "$t" 2>&1
  rc=$?
  if [ "$rc" -eq 0 ] || [ "$rc" -eq 127 ] || ! grep -q "ZeroDivisionError" "$t"; then
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

Use a per-invocation temp file for metric capture (avoids parallel write races)
and a shared file for the running best (acknowledged racy — acceptable in practice):

```sh
#! /bin/sh
# No set -eu — interpreter exits non-zero intentionally
# Requires interpreter to be on PATH or use a full path below

trace="$(mktemp)"
trap 'rm -f "$trace"' EXIT

# Primary check: must crash (non-zero exit)
/full/path/to/interpreter "$1" 2>"$trace"
rc=$?
[ "$rc" -ne 0 ] || exit 1   # exit 1 (uninteresting) if it did NOT crash

# Secondary metric: trace length in lines
new_len="$(wc -l < "$trace" | tr -d '[:space:]')"
[ -z "$new_len" ] && new_len=0   # guard: empty trace if program crashed instantly

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
  the metric may occasionally move in the wrong direction, but in practice
  the approach still converges.
- May produce a slightly *larger* input file in exchange for a much better
  secondary metric. That's the point.
- Use a full path for your interpreter (e.g. `/usr/local/bin/myinterp`) since
  Shrink Ray `cd`s into a temp directory where `./interpreter` won't exist.

**Adapt the metric:**
- Wall time: `{ time /path/to/program "$1" 2>/dev/null; } 2>&1 | grep real | awk '{print $2}'`
- Memory peak: `/usr/bin/time -v /path/to/program "$1" 2>&1 | grep "Maximum resident" | awk '{print $NF}'`
- Nondeterminism frequency: run N times, count *non-occurrences* of the error,
  store that count. Lower = the error occurs more consistently. The reducer
  drives the count toward zero (= fully deterministic crash every run).

---

## Debugging a Stuck Reducer

| Symptom | Likely cause | Fix |
|---|---|---|
| Empty input passes interestingness test | Test too permissive / over-reduction | Tighten the test; add positive output anchors |
| Shrink Ray rejects test on original input | Test fails immediately on original | Run `bash -x ./interestingness.sh original` to diagnose |
| No progress after initial acceptance | Non-termination in reduced candidates | Add `timeout`; check loop terminators |
| Reduction stops early, bug gone | Test accepted a different code path | Add stricter output checks |
| Parallel file collisions | Build artifacts written to shared paths | Use `$$`/`mktemp` + `trap ... EXIT` cleanup |
| Secondary metric explodes | Reducer optimizing length only | Switch to global counter technique |
| `set -e` aborts test early | Shell `-e` fires on program's non-zero exit | Remove `set -eu` from interestingness test |
| `rc=127` false positives | Command not found treated as interesting | Guard with `[ "$rc" -ne 127 ]` |

---

## Quick Reference: Shrink Ray Flags

```bash
# Basic
shrinkray ./test.sh input.txt

# Language-agnostic (no C/C++ syntax awareness)
shrinkray --no-clang-delta ./test.sh input.c

# Set parallelism explicitly
shrinkray --parallelism 8 ./test.sh input.txt

# Set a per-subprocess timeout (seconds)
# If unset, Shrink Ray measures the first run and uses 10× that (max 5 min)
shrinkray --timeout 5 ./test.sh input.txt

# Run in-place (CWD, no temp dir per test) — disable parallelism or handle collisions yourself
shrinkray --in-place --parallelism 1 ./test.sh input.txt

# Non-interactive output (for scripts/CI)
shrinkray --volume quiet ./test.sh input.txt
```

Shrink Ray backs up the original to `<input>.bak` before modifying in place.
To resume from a partial reduction, re-run with the already-reduced output
file as the new input.

---

## Example: C Compiler Differential Bug

```sh
#! /bin/sh
# No set -eu — compiled binaries may exit non-zero
trap 'rm -f slow_$$ fast_$$' EXIT

# Explicit || exit 1 per step; no set -e / set +e toggling needed
cc -std=c99 -O2 -DFAST=0 "$1" -o slow_$$ 2>/dev/null || exit 1
cc -std=c99 -O2 -DFAST=1 "$1" -o fast_$$ 2>/dev/null || exit 1

slow_out="$(timeout 1s ./slow_$$)" || exit 1
fast_out="$(timeout 1s ./fast_$$)" || exit 1

test "$slow_out" = "expected_hash"  || exit 1
test "$fast_out" != "expected_hash" || exit 1
```

Notes:
- `$$` in binary names prevents collision under parallel reduction.
- `trap ... EXIT` ensures cleanup even on early exit or signal.
- Replace `expected_hash` with the actual output of the slow build on the
  original input.
- Shrink Ray `cd`s into a temp dir per test, so `./slow_$$` resolves correctly.
- `!=` in `test` is not strictly POSIX but works on all common `/bin/sh`
  implementations. Use `[ ! "$fast_out" = "expected_hash" ]` for strict portability.

---

## Minimal Reducer (when Shrink Ray isn't available)

Useful in CI containers or constrained environments:

```python
#!/usr/bin/env python3
"""Minimal line-deletion reducer. Usage: reducer.py ./interestingness.sh input.txt"""
import subprocess, sys, os, tempfile

interestingness = sys.argv[1]
input_file = sys.argv[2]
output_file = input_file + ".reduced"

with open(input_file) as f:
    cur = [l.rstrip('\n') for l in f]

def is_interesting(lines):
    src = '\n'.join(lines)
    suffix = os.path.splitext(input_file)[1]
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(src)
        r = subprocess.run(
            [interestingness, path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return r.returncode == 0
    finally:
        os.unlink(path)

i = 0
while i < len(cur):
    cnd = cur[:i] + cur[i+1:]
    if is_interesting(cnd):
        cur = cnd
        # Save progress after each successful reduction
        with open(output_file, 'w') as f:
            f.write('\n'.join(cur))
        # Don't advance i: the line at position i is now the old i+1,
        # so we try removing it next iteration
    else:
        i += 1

print('\n'.join(cur))
```

This is the ddmin forward-scan loop. Single-threaded and slow on large inputs,
but correct and dependency-free. Progress is saved after each reduction so
an interrupted run can be resumed from `<input>.reduced`. For more reductions,
restart `i=0` each time a reduction succeeds (~10× more iterations but finds
disjoint deletions).

---

## Further Reading

- [Shrink Ray](https://github.com/DRMacIver/shrinkray) — recommended reducer
- [creduce paper](https://www.cs.utah.edu/~regehr/papers/pldi11-preprint.pdf) — original influential reducer
- [ddmin](https://www.st.cs.uni-saarland.de/publications/files/hildebrandt-issta-2000.pdf) — foundational algorithm
- [Using reducers as fuzzers](https://blog.regehr.org/archives/1284) — surprising dual use
- [Cause reduction](https://users.cs.utah.edu/~regehr/papers/mintest.pdf) — theoretical basis for secondary-metric steering
