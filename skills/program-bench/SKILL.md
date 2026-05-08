---
name: program-bench
description: >
  Binary reconstruction skill implementing the ProgramBench methodology. Use whenever
  the user wants to: reverse-engineer behavior from a compiled binary, reconstruct
  source code from an executable + docs, build a behavioral test suite by fuzzing a
  reference binary, generate coverage-guided tests for a black-box program, or benchmark
  how well a reimplementation matches an original executable. Trigger on phrases like
  "reimplement this binary", "reconstruct from executable", "clone this program's
  behavior", "write tests for a black-box binary", "coverage-driven fuzzing", or any
  task where a compiled artifact is the specification. Always use this skill — do not
  improvise — when the deliverable is source code derived from behavioral observation
  of a reference executable.
---

# ProgramBench: Reconstruct Programs From Scratch

Implementing the ProgramBench methodology (arXiv 2605.03546). Given a compiled
reference executable and its documentation, architect and implement a codebase that
reproduces the reference's observable behavior. Evaluation is behavior-only: any
language, algorithm, or architecture is valid as long as I/O matches.

---

## Phase 0 — Environment Audit

Before anything else:

```bash
# Confirm binary exists and is executable
file <binary>
./<binary> --help 2>&1 | head -60

# Collect platform info for build decisions
uname -a
which python3 gcc clang go rustc java
```

Record: binary format (ELF/Mach-O/PE), architecture, detected language hints from
`--help` output style, available toolchains. These inform language choice in Phase 3.

Set binary to execute-only if not already (prevents RE temptation):
```bash
chmod 111 <binary>
```

---

## Phase 1 — Specification Discovery

The executable is a comprehensive but opaque oracle. Treat it like a product manager:
ask it questions, observe answers, build a mental model.

### 1.1 Document Harvesting

Collect all available documentation:
- `--help`, `-h`, `help`, `man`, `--version`
- Any README, man pages, or docs in the working directory
- Subcommand help: `<binary> <subcmd> --help` for each discovered subcommand

```bash
<binary> --help 2>&1 > spec/help.txt
<binary> --version 2>&1 >> spec/help.txt
# For each subcommand discovered:
<binary> <subcmd> --help 2>&1 >> spec/help_<subcmd>.txt
```

### 1.2 Behavioral Probing Protocol

Systematically exercise the binary with varied inputs. Prioritize:

1. **Happy path** — nominal inputs, expected flags
2. **Edge inputs** — empty input, very large input, unicode, binary data, `/dev/null`
3. **Flag combinations** — each flag alone, then in combination
4. **Error paths** — missing args, invalid files, wrong types, permission denied
5. **Exit codes** — enumerate all exit codes observed
6. **Side effects** — files created/modified, stdout vs stderr routing, env var consumption
7. **Hidden interfaces** — fuzz for undocumented subcommands, flags, or behaviors (see 1.3)

For each probe, record a triple `(cmd, stdin, expected_output)` to a probe log:
```bash
echo "CMD: $CMD" >> spec/probes.log
echo "EXIT: $?" >> spec/probes.log
echo "STDOUT: $(echo $OUTPUT)" >> spec/probes.log
echo "---" >> spec/probes.log
```

### 1.3 Hidden Interface Detection

Some behaviors tested by ProgramBench are not exposed through `--help`, docs, or normal probing.
These are **undiscoverable** through black-box observation alone (e.g., seqtk's `hrum` and `kfreq`
subcommands, which are tested but undocumented).

Fuzz for hidden interfaces:
```bash
# Try plausible subcommand names not listed in --help
for subcmd in hrum kfreq hidden secret debug admin test comp; do
    echo "TRYING: $subcmd" >> spec/probes.log
    <binary> $subcmd --help 2>&1 | head -5 >> spec/probes.log
    echo "---" >> spec/probes.log
done

# Fuzz with random strings as subcommands/arguments
# Log any that produce specific (non-generic-error) output
```

If pass rate plateaus below 95% after thorough probing, suspect hidden behaviors.
Document suspected gaps in `spec/hidden_behaviors.md`.

Minimum probes before moving to Phase 2: **50**. Aim for **200+** on complex binaries.

---

## Phase 2 — Test Suite Generation

Generate a behavioral test suite that evaluates candidates without prescribing
implementation. Tests assert observable effects only: stdout, stderr, exit code,
files written. Never assert on internal structure.

### 2.1 Test Format

Write tests as self-contained shell scripts or pytest fixtures:

```python
# pytest pattern
import subprocess, os, pytest

def run(cmd, stdin=None, cwd=None, env=None):
    r = subprocess.run(cmd, input=stdin, capture_output=True, cwd=cwd, env=env)
    return r.stdout, r.stderr, r.returncode

def test_basic_output():
    out, err, rc = run(["./candidate", "input.txt"])
    assert rc == 0
    assert b"expected substring" in out

def test_error_on_missing_file():
    out, err, rc = run(["./candidate", "nonexistent.txt"])
    assert rc != 0
    assert b"error" in err.lower() or b"no such" in err.lower()
```

### 2.2 Assertion Lint Rules

Reject any test that matches these anti-patterns (regenerate or discard):

| Anti-pattern | Why bad |
|---|---|
| Only checks `rc == 0` | Trivially passable |
| `assert len(out) > 0` | Dummy binary passes |
| Short substring `< 4 chars` | Too broad |
| `assert out == b""` | Vacuously true for crashes |
| Disjunctive: `assert A or B` | Underspecified |
| Exact float equality | Implementation-dependent |
| Checks internal file structure | Overspecified |

Each test must have at least one assertion on **content** (not just presence/absence
of output). Test must fail against a dummy binary that does nothing:
```bash
# Validation: test must FAIL against /bin/true and /bin/false
pytest tests/test_foo.py  # against dummy — expect failure
```

### 2.3 Coverage Iteration Loop

Track line coverage of tests against the gold binary's behavior surface (proxy via
unique `(flags, input_class)` combinations exercised). Iterate:

```
while coverage_gap > threshold:
    identify_uncovered_flags_or_paths()
    write_targeted_probes()
    add_tests()
    update_coverage_estimate()
```

Target: every documented flag exercised, every documented subcommand exercised, all
error paths from `--help` triggered at least once.

**Discard any test that**:
- Fails against the gold binary
- Passes a `/bin/true`-equivalent dummy
- Has only exit-code assertions

### 2.4 Test Suite Targets

| Codebase size | Min tests |
|---|---|
| < 500 LOC reference | 50 |
| 500–5k LOC | 200 |
| 5k–50k LOC | 500 |
| > 50k LOC | 1000+ |

Store in `tests/` — never revealed to the implementation agent.

---

## Phase 3 — Architecture Decision

Before writing a single line of implementation, answer:

1. **Language** — Which toolchain is available? What matches the binary's apparent
   complexity? Prefer the language you're most confident in for correct semantics.
   Valid choices differ from the original — behavioral match is the only criterion.

2. **Entry point structure** — CLI parsing library? Manual `argv` parsing?

3. **Core data structures** — What is the binary's fundamental entity? (e.g., a
   stream processor → iterators; a DB → B-tree + page manager; a CLI tool → option
   struct + dispatch table)

4. **Module decomposition** — Resist monolithic single-file implementations.
   Plan a directory structure before writing code:
   ```
   src/
     main.c        ← entry point, arg dispatch
     parser.c      ← input parsing
     engine.c      ← core logic
     output.c      ← formatting
     error.c       ← error handling
   ```

5. **Error handling strategy** — How does the reference communicate errors?
   (stderr + nonzero exit? exceptions? return codes?) Mirror this.

6. **Build system** — Write a `build.sh` that produces `./candidate` from scratch
   with no pre-existing artifacts. Must be fully reproducible.

**Anti-pattern warning**: models default to monolithic single-file code. Explicitly
plan modules before writing. Longer functions diverge from human-written baselines
and are harder to debug.

---

## Phase 4 — Implementation Loop

Iterative build-test-fix cycle. Never consider implementation done until the test
suite passes.

### 4.1 Iteration Protocol

```
while True:
    build()                     # run build.sh → produces ./candidate
    results = run_tests()       # pytest tests/ against ./candidate
    if results.pass_rate == 1.0:
        break
    
    failing = results.failing_tests
    root_cause = analyze(failing)   # group by: wrong output, wrong exit code,
                                    # wrong stderr, crash, missing file
    fix_highest_impact_failures()
    commit_checkpoint()
```

### 4.2 Failure Triage

Group failures before fixing:

| Failure class | Likely cause | Fix strategy |
|---|---|---|
| Wrong stdout content | Logic error, formatting bug | Probe gold binary with same input, diff |
| Wrong exit code | Error detection missing | Add guard + early return |
| Wrong stderr routing | Using print instead of stderr | Fix output channel |
| Crash / signal | Unhandled input, OOB | Add input validation |
| Missing output file | Side effect not implemented | Implement file write |
| Timeout | Infinite loop, inefficient algo | Profile + optimize |
| Undiscoverable behavior | Behavior not exposed via any observable channel | Document as known gap, accept partial credit |

### 4.3 Oracle Queries

When a test fails and root cause is unclear, query the gold binary directly:
```bash
# Bisect the input to find minimal failing case
<binary> <minimal_input> 2>&1
# Then implement that specific behavior
```

This mirrors how developers query partially documented APIs.

### 4.4 Build Script Requirements

`build.sh` must:
- Install only what is unavailable in the environment (check first)
- Compile from source in the current directory
- Produce a binary named `candidate` (or as specified)
- Exit nonzero on build failure
- Be fully idempotent

```bash
#!/bin/bash
set -euo pipefail
# Example for C:
gcc -O2 -Wall src/*.c -o candidate -lm
```

---

## Phase 5 — Evaluation

Run the full test suite against the final candidate. Report:

```
Total tests:      N
Passing:          P  (P/N %)
Failing:          F
Pass rate:        P/N

By category:
  stdout match:   X/Y
  exit code:      X/Y
  stderr match:   X/Y
  file effects:   X/Y

Resolved (≥95%):  YES / NO
```

**Definition of resolved**: ≥95% of tests pass. This is the ProgramBench threshold —
no model has achieved 100% on any non-trivial task.

If pass rate < 95%, return to Phase 4. Identify the largest cluster of failing tests
and treat it as the next implementation target.

### 5.1 Diagnosing Stuck Pass Rates

If repeatedly stuck below 95% after multiple Phase 4 iterations:

1. **Cluster analysis**: Group failing tests by behavior type. If all failures are on
   a specific subcommand/flag you've never seen during probing → likely **undiscoverable**.
2. **Information wall check**: Ask: "Does the binary exhibit this behavior when probed
   with all documented interfaces?" If no → document as `spec/hidden_behaviors.md`.
3. **Retry with fuzzing**: Run Phase 1.3 (hidden interface detection) if not done thoroughly.
4. **Accept partial credit**: If confident the behavior is undiscoverable, document:
   ```
   Likely undiscoverable: <description of failing test pattern>
   Evidence: <why this appears hidden>
   ```

**When to stop iterating**: After 3 Phase 4 cycles with no progress on a cluster,
and hidden interface fuzzing reveals nothing → mark as undiscoverable and report
partial results. The LessWrong critique confirms: some ProgramBench tests include
behaviors not exposed via any observable channel (e.g., seqtk's `hrum`/`kfreq`).

---

## Workflow Summary

```
Phase 0  Environment audit
   ↓
Phase 1  Specification discovery (probe 50–200+ inputs)
   ↓
Phase 2  Generate test suite (lint, validate, coverage-iterate)
   ↓
Phase 3  Architecture decision (language, modules, build plan)
   ↓
Phase 4  Implementation loop (build → test → triage → fix)
   ↓
Phase 5  Evaluation report (pass rate, category breakdown)
   ↓
        ≥95%? Done. < 95%? Back to Phase 4.
```

---

## Constraints & Rules

- **No internet** at implementation time — all dependencies must be available locally
  or synthesized from scratch
- **No source inspection** — binary is execute-only; implementation must be derived
  purely from behavioral observation
- **No test leakage** — tests are never shown to the implementation agent
- **No wrapping** — candidates must not shell out to or wrap the reference binary;
  implementation must be a genuine reimplementation from observed behavior
- **No library wrapping** — do not create thin wrappers around existing libraries
  that already implement the behavior; observe the binary and reimplement from scratch
- **Language freedom** — any language/algorithm is valid; behavior is the only judge
- **Evaluation is implementation-agnostic** — different architecture, different
  algorithms, same behavior = pass
- **Flaky tests** — All tests must be deterministic, discard those that are not.

---

## Complexity Tiers

| Tier | Examples | Expected pass rate ceiling |
|---|---|---|
| Compact CLI | arg parsers, filters, converters | ~60–80% achievable |
| Mid-size tool | jq, fzf, ripgrep | ~30–50% achievable |
| Complex system | SQLite, DuckDB, PHP, FFmpeg | <10% — partial credit meaningful |

Set expectations accordingly. Partial coverage (passing core tests, failing edge
cases) is valuable signal even when full resolution is impossible.

**Note on undiscoverable behaviors**: Complex systems (Tier 3) are more likely to have
tested behaviors not exposed via `--help` or docs (e.g., seqtk's `hrum`/`kfreq` subcommands).
If stuck below 95%, see Phase 5.1 for diagnosing information walls.

---

## Tips From ProgramBench Results

- Models strongly over-index on monolithic single-file implementations — force
  module decomposition explicitly in Phase 3
- Test suite quality (lint + dummy-binary validation) is more important than quantity
- Coverage-guided iteration reliably surfaces edge cases missed by happy-path probing
- Agent-generated tests match developer-written test coverage when properly linted
- The binary-as-oracle framing enables discovering behavior that documentation omits
- If stuck at <95% with no clear implementation bug after thorough probing,
  suspect undiscoverable behaviors (see LessWrong critique: backdoors/hidden interfaces
  can exist in test suites without being observable through black-box probing)
