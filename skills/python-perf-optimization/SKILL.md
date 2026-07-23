---
name: python-perf-optimization
description: Systematic workflow for optimizing a Python project's runtime performance, memory footprint, or startup time. Use whenever the user asks to make Python code faster, reduce memory usage, profile a Python project, fix slow tests/CI, or generally "optimize" a Python codebase. Always measure before and after changes — never optimize on vibes. Covers profiling (cProfile, py-spy, memray, line_profiler), algorithmic fixes, C-extension/native acceleration (Cython, Numba, Rust via PyO3), concurrency (asyncio, multiprocessing, GIL/free-threading), memory optimization (__slots__, generators, numpy), and packaging/startup optimization.
---

# Python Project Optimization

A measure-first workflow. The failure mode this skill guards against: rewriting
code based on assumption instead of profile data, and declaring victory
without a benchmark showing improvement.

## Step 0: Establish the actual problem

Don't start optimizing until you know what "slow" means concretely. Ask (or infer
from context) which of these applies — they require completely different tools:

| Symptom | Category | Go to |
|---|---|---|
| Function/pipeline takes too long | CPU-bound latency | Step 1 (CPU profiling) |
| Uses too much RAM, OOMs, swaps | Memory | Step 4 (memory profiling) |
| Slow to import / `python -c "import x"` takes seconds | Startup | Step 5 |
| Handles too few requests/sec, blocks on I/O | Concurrency/I-O bound | Step 3 |
| Slow test suite / CI | Usually I/O or fixture overhead, not algorithmic | Step 3 + Step 5 |

If ambiguous, ask a single clarifying question rather than guessing. Do not
proceed past this step without at least a rough baseline number (wall-clock
seconds, RSS in MB, or requests/sec) — this is what "improved" will be measured
against later.

## Step 1: CPU profiling — find where time actually goes

Never optimize the function you *assume* is slow. Profile first, every time.

### Quick pass: `cProfile` (stdlib, deterministic, function-level)
```bash
python -m cProfile -o out.prof your_script.py
python -c "
import pstats
p = pstats.Stats('out.prof')
p.sort_stats('cumulative').print_stats(20)
"
```
Or interactively with `snakeviz` for a flamegraph-style view:
```bash
pip install snakeviz
snakeviz out.prof
```
Caveats: cProfile adds per-call overhead that distorts timing for code with
many small function calls, and it can't see into C extensions. This overhead
is not just theoretical — profiling a fork/waitpid-heavy benchmark showed
unprofiled wall time of 4.50s vs. 5.27s under `python -m cProfile` (~17%
overhead), even though most of that workload's time is spent inside syscalls
cProfile can't instrument at all. When most of the wall time is syscall time
rather than Python bytecode, treat cProfile's absolute numbers as suspect and
its *relative* ranking (which function dominates `tottime`/`cumtime`) as the
reliable signal; get the real wall-clock baseline from an unprofiled run (or
`os.times()`/`time.perf_counter()` around the whole thing) and use that for
any before/after comparison you report.

Also cross-check any hand-rolled instrumentation (a manual counter of
syscalls, iterations, cache hits) against the profiler's own `ncalls` for the
same function — a counting bug in ad-hoc instrumentation is easy to introduce
and easy to miss, and the profiler gives you that check for free.

### Sampling profiler: `py-spy` (no code changes, works on running processes, low overhead)
```bash
pip install py-spy
py-spy record -o profile.svg -- python your_script.py
# or attach to a running PID (great for stuck/slow production processes):
py-spy dump --pid 12345
```
Use this over cProfile when overhead must be near-zero, when you need to
profile something already running, or when you suspect the GIL/native code.

### Line-level: `line_profiler`
When cProfile/py-spy point at a function but you need to know *which line*:
```bash
pip install line_profiler
kernprof -l -v script_with_at_profile_decorator.py
```
Decorate the suspect function with `@profile` (kernprof injects it, don't import it).

### Reading the output
- High `cumtime` but low `tottime` → the function itself is fine, something it
  calls is slow. Drill into cumulative time descendants.
- High `tottime` with high `ncalls` → algorithmic issue (called too often) or
  needs micro-optimization.
- Check `ncalls` for anything with 4+ digits you didn't expect — often the
  smoking gun (e.g. quadratic-blowup calling a helper N² times).

## Step 2: Fix the algorithm before reaching for native code

In order of typical ROI, cheapest first:

1. **Complexity class.** O(n²) → O(n log n) or O(n) via better data structure
   (set/dict membership instead of list scan, sorting once instead of
   re-sorting per iteration). This dwarfs any constant-factor trick.
2. **Avoid redundant work.** Memoize (`functools.lru_cache` / `functools.cache`),
   hoist loop-invariant computation out of loops, avoid recomputing
   `len()`/attribute lookups inside hot loops (bind to locals).
3. **Use the right built-in/stdlib tool.** `collections.deque` for queue
   operations, `bisect` for sorted insert, `itertools` for lazy pipelines
   instead of building intermediate lists, `array`/`struct` for packed
   numeric data instead of lists of Python objects.
4. **Vectorize.** If touching numeric arrays, replace Python-level loops with
   `numpy` vectorized ops or `pandas` vectorized methods — this alone is
   often a 10–100x win and should come before any Cython/Numba effort.
5. **String building.** Use `''.join(parts)` instead of repeated `+=` in a loop.

Re-profile after each fix category — algorithmic fixes often eliminate the
need for the native-code escalation below entirely.

## Step 2.5: Busy-poll loops — treat as both a perf AND a correctness audit

Any loop of the shape `while not_done: check_status(); if not_ready: sleep(); continue`
(common around `os.waitpid(..., WNOHANG)`, socket polling, file-lock polling,
job-queue polling) deserves extra scrutiny beyond "this burns CPU":

- **Check every return value used in the loop condition, not just one field.**
  A recurring real bug: `os.waitpid(pid, os.WNOHANG)` returns `(0, 0)` when
  nothing is ready yet, but a child that exited normally with code 0 also
  produces a raw wait status of `0` — so code that branches on `status == 0`
  alone (discarding the returned pid) cannot tell "not ready" from "reaped,
  exited cleanly." This is not a hypothetical: profiling a fork/ptrace-based
  process-execution loop for a fuzzer surfaced exactly this, with clean
  (non-crashing) target runs being silently misclassified as errors 100% of
  the time in a reproduction. Always check the *identity/pid* field returned
  by a wait/poll call, not just a status field that can legitimately be zero
  for a valid terminal state.
- **Quantify the busy-poll tax before rewriting.** Count syscalls per
  logical operation (a poll loop calling `waitpid` 5x per exec instead of
  once is a 5x syscall multiplier, invisible in wall-clock time but visible
  in `os.times()` CPU seconds or `strace -c`) — this is often a bigger win
  once fixed than the correctness bug's blast radius suggests, because it's
  paid on every single iteration of a hot loop (e.g. every fuzz execution).
- **Prefer blocking waits with a deadline** (blocking `os.waitpid` + `SIGALRM`,
  `select`/`poll` with a timeout, `threading.Event.wait(timeout=)`) over
  sleep-based polling wherever the underlying primitive supports it — it's
  simultaneously faster (fewer wakeups) and removes the whole class of "is
  zero the sentinel or a real value" bugs that manual polling invites.
- When writing a microbenchmark to isolate a suspected loop bug like this,
  copy the *exact* conditional logic from the real code rather than a
  paraphrase — the bug is often in the specific comparison, and a paraphrased
  reproduction can accidentally "fix" it without noticing.

## Step 2.6: Hot path micro-optimization — once the hot path is identified, not before

A "hot path" is the small fraction of code that runs a disproportionate number
of times (the inner loop of a fuzzer's exec cycle, a per-request handler, a
per-row transform) — profiling (Step 1) is what tells you *which* code
qualifies. Do not micro-optimize anything the profiler didn't point at; a
1μs saving repeated 10M times/sec matters, the same saving in code that runs
10 times/run doesn't.

Once a hot path is confirmed, in order of typical payoff:

1. **Minimize work per iteration first, not per-call overhead.** Check for
   accidental O(n) or allocation work hiding inside what looks like O(1) —
   e.g. rebuilding a regex, re-parsing a struct format string, or
   re-resolving a dict of options on every single call inside the loop
   instead of once outside it.
2. **Cache attribute/global lookups into locals before the loop.** `x.y.z`
   and module-global lookups cost real time inside a tight loop; bind
   `z = x.y.z` (or `append = list.append`) once above the loop, use the
   local inside.
3. **Reduce per-iteration allocations.** Reusing a buffer (e.g. a
   pre-allocated `bytearray`/`ctypes` struct) beats allocating a new object
   every iteration — this is exactly why re-creating a `ctypes.CDLL`,
   struct-format string, or regex inside a per-execution function is a hot
   path anti-pattern; hoist it to module scope or `__init__`.
4. **Count syscalls per iteration, not just Python-level ops**, for any hot
   path that forks, reads/writes, or waits — see Step 2.5. A hot path with
   1 syscall/iteration vs 5 is a 5x difference invisible in a plain cProfile
   run (which only sees Python-level time) but visible in wall-clock/CPU-time
   deltas or `strace -c`.
5. **Split fast path from slow path.** Handle the common case with minimal
   branching and push rare/expensive validation, error formatting, or
   logging behind a cheap guard so the common case doesn't pay for it (e.g.
   don't build a detailed error/debug string every iteration "just in case" —
   build it only once the rare branch is actually taken).
6. **Avoid exceptions as control flow in the hot path.** Exception handling
   has non-trivial cost per raise in CPython; a hot path that relies on
   catching an exception every iteration for an *expected, common* outcome
   (vs a genuinely rare error) should be restructured to check a condition
   instead.
7. **Re-profile after each change** — hot-path work is exactly where
   intuition is least reliable and where the biggest regressions can hide,
   since the same code runs constantly.

Concrete example from a real fuzzer's execution hot path (the fork/exec/wait
cycle run once per test case, i.e. potentially millions of times per run):
`ctypes.CDLL("libc.so.6")` and the ptrace `argtypes`/`restype` setup being
re-declared inside the per-execution function is pure hot-path waste — it
should be resolved once at module or object-init scope and reused, and the
same applies to any `struct.Struct(...)` or compiled regex built freshly
per call inside a loop that runs per-execution.

## Step 2.7: Redundant round trips around "upsert" patterns

A common hot-path cost in caches/stores built on SQLite (or any DB): doing a
`SELECT` to check whether a key exists purely so the caller can maintain its
own counter or branch logic, immediately followed by an `INSERT OR REPLACE`/
`ON CONFLICT DO UPDATE`. This is an extra round trip on every write, and it's
easy to miss because each half looks individually cheap and correct.

- **Look for `SELECT ... WHERE key = ?` immediately preceding an
  upsert on the same key** — that's the pattern. Measured example: a
  cache's `set()` doing this cost **~24.5% extra time per write** (47.1μs
  vs 37.8μs/write over 5,000 writes) versus dropping the check and treating
  the maintained counter as approximate, corrected by a periodic maintenance
  pass the code already ran anyway.
- **Verify any proposed shortcut against the actual engine before
  recommending it — don't assume DB internals.** The first idea for fixing
  the above (use SQLite's `total_changes` delta to distinguish a fresh
  insert from a replace, avoiding the SELECT) turned out to be false when
  tested: `total_changes` increased by 1 in both the insert and the replace
  case in the SQLite build tested, not 2 for a replace as the "REPLACE is
  DELETE+INSERT" mental model would suggest. A three-line test script
  settled it in seconds and prevented recommending a fix that doesn't work.
  The general lesson: when an optimization idea rests on a claim about how a
  database/interpreter/OS internally behaves, write the two-line
  reproduction and check it before proposing the change, rather than
  reasoning from the documented-sounding mental model alone.
- If exact counts genuinely matter every write (not just eventually
  consistent), an `INSERT ... ON CONFLICT(key) DO UPDATE SET ...
  RETURNING (xmax = 0) AS was_insert`-style construct (Postgres) or checking
  `cursor.rowcount`/dialect-specific upsert feedback can sometimes avoid the
  separate SELECT — but confirm the exact semantics for the specific engine
  and version in use rather than assuming portability across engines.

## Step 3: Concurrency — only after confirming it's I/O-bound or embarrassingly parallel

Diagnose first: if profiling shows time in `time.sleep`, socket/file reads, or
subprocess waits, it's I/O-bound. If it's pure Python computation with the GIL
held, threads alone won't help (pre-3.13 non-free-threaded builds).

- **I/O-bound, many concurrent operations** → `asyncio` with async libraries
  (`aiohttp`, `asyncpg`), or a `ThreadPoolExecutor` if the I/O libraries are
  blocking/sync-only. Threads are fine here because the GIL is released during I/O.
- **CPU-bound, need true parallelism** → `multiprocessing` /
  `concurrent.futures.ProcessPoolExecutor`. Mind serialization cost (pickling
  arguments/results) — for large arrays, use `multiprocessing.shared_memory`
  or numpy memmaps to avoid copying.
- **Free-threaded CPython (3.13+ `--disable-gil` build)** — check with
  `python -c "import sys; print(sys._is_gil_enabled())"` if the user's on 3.13+;
  changes the threading calculus but ecosystem C-extension compatibility is
  still catching up as of early-2026, so verify third-party deps support it.
- Common trap: wrapping CPU-bound work in `asyncio.to_thread` doesn't parallelize
  it (GIL), it just avoids blocking the event loop — use a process pool instead.

## Step 4: Memory profiling and reduction

### Profiling
```bash
pip install memray
memray run your_script.py
memray flamegraph memray-your_script.py.<pid>.bin   # generates HTML flamegraph
```
`memray` tracks native allocations too (unlike `tracemalloc`), which matters
for numpy/C-extension-heavy code. For a quick stdlib-only check:
```python
import tracemalloc
tracemalloc.start()
# ... run code ...
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:10]:
    print(stat)
```

### Reduction techniques, in order of effort
1. **Generators over lists** for anything consumed once/streamed — replace
   list comprehensions feeding a single loop with generator expressions,
   replace functions returning full lists with `yield`.
2. **`__slots__`** on classes with many instances — removes the per-instance
   `__dict__`, often 40-50% per-object memory reduction.
3. **Numpy/array over lists of Python objects** for homogeneous numeric data —
   a Python `float` object is ~24 bytes of overhead vs 8 bytes packed in a
   numpy array.
4. **Avoid accidental retention**: circular references needing GC, closures
   capturing more than needed, module-level caches that grow unbounded (use
   `functools.lru_cache(maxsize=N)` not `maxsize=None` for unbounded workloads).
5. **Chunk/stream large file or DB reads** instead of loading fully into memory
   (`pandas.read_csv(chunksize=...)`, iterate cursor instead of `.fetchall()`).

## Step 5: Native acceleration (after algorithmic fixes are exhausted)

Only reach here if profiling shows genuine CPU-bound Python-level bottleneck
that can't be vectorized with numpy. In order of effort/risk:

- **Numba** (`@njit` decorator) — best for numeric loops, near-zero code
  rewrite, JIT-compiles a function. Good first stop.
- **Cython** — more control, requires a build step (`.pyx` + `setup.py`/
  `pyproject.toml` build backend), good for wrapping loops with typed
  variables (`cdef`) or wrapping existing C libraries.
- **PyO3 (Rust)** — for new native modules where memory safety and stronger
  guarantees matter, or when the user is already comfortable in Rust
  (worth mentioning given systems-level codebases: fuzzers, binary analysis
  tools benefit from this over Cython for hot inner loops with untrusted input).
- **ctypes/cffi** — only if wrapping an existing C library, not for writing new
  native code from scratch.

Always benchmark the native version against the pure-Python vectorized version
— sometimes numpy alone matches Numba/Cython and isn't worth the build complexity.

## Step 6: Startup time (imports, CLI tools)

```bash
python -X importtime your_script.py 2> importtime.log
# sort by cumulative to find the worst offenders:
sort -t'|' -k2 -n -r importtime.log | head -20
```
Common fixes: lazy-import heavy/rarely-used dependencies inside the functions
that use them rather than at module top-level, avoid importing entire heavy
packages (`pandas`, `torch`) just to use one small piece, check for
`__init__.py` files that eagerly import submodules the CLI path doesn't need.

## Step 7: Verify and lock in the improvement

- Re-run the same profiler/benchmark used in Step 0/1 and diff the numbers —
  state the before/after explicitly (e.g. "cProfile cumtime: 4.2s → 0.3s").
- For anything perf-sensitive going forward, add a regression benchmark using
  `pytest-benchmark` or a simple timing assertion in CI so the win doesn't
  silently regress:
  ```python
  def test_parse_performance(benchmark):
      result = benchmark(parse_large_file, "fixture.dat")
      assert result is not None
  ```
- If the fix changed algorithmic behavior (not just constants), re-run the
  existing test suite — correctness regressions are the most common cost of
  aggressive optimization.

## Anti-patterns to flag if seen

- Optimizing based on "this looks slow" without a profile.
- Micro-optimizing (e.g. `x = x + 1` vs `x += 1`) before checking algorithmic
  complexity — near-zero real-world impact, wastes review time.
- Introducing threading for CPU-bound work expecting parallelism (GIL blocks it
  outside free-threaded builds).
- Premature Cython/Numba before trying numpy vectorization or simpler
  algorithmic fixes.
- Reporting "it's faster" without a number from before and after using the
  same measurement method.
