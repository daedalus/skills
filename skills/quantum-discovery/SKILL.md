---
name: quantum-discovery
description: >
  Quantum systems discovery skill for finding novelties and pushing the state of the art.
  Use this skill whenever the user wants to: explore quantum phenomena, discover new quantum
  behaviors or algorithms, run quantum circuit experiments, test quantum hypotheses,
  simulate quantum systems with Qiskit, validate results on real IBM quantum hardware,
  find quantum advantage regimes, probe entanglement structure, or do exploratory quantum
  research. Trigger on phrases like "quantum experiment", "run on quantum hardware",
  "discover quantum", "Qiskit simulation", "IBM quantum", "quantum circuit", "quantum
  novelty", "push quantum state of the art", "quantum exploration", or any request to
  investigate a quantum system computationally. This skill manages the full pipeline:
  hypothesis → Qiskit emulation → plausibility check → real hardware submission → result
  analysis.
compatibility:
  python: ">=3.10"
  pip: [qiskit, qiskit-aer, qiskit-ibm-runtime, numpy, scipy, matplotlib, pandas]
---

# Quantum Discovery Skill

A structured pipeline for quantum systems exploration: from hypothesis generation through
Aer simulation to IBM Quantum hardware validation. Designed for open-ended discovery —
finding anomalies, beating classical baselines, and pushing beyond known results.

---

## Pipeline Overview

```
HYPOTHESIS → CIRCUIT DESIGN → AER SIMULATION → PLAUSIBILITY GATE → REAL HW → ANALYSIS
```

Each stage has explicit pass/fail criteria. Only plausible, non-trivial results proceed
to real hardware (limited shots, expensive queue time).

---

## Stage 0 — Environment Setup

Before any experiment, verify and install dependencies:

```bash
pip install qiskit qiskit-aer qiskit-ibm-runtime numpy scipy matplotlib pandas --quiet
```

For IBM Quantum hardware access, the user must provide an API token. Check for it:

```python
import os
token = os.environ.get("IBM_QUANTUM_TOKEN")  # or ask user
```

If no token: run full simulation only, skip hardware stage, note limitation clearly.

Load the setup script:
→ Read `scripts/setup_env.py` for full environment bootstrapping and Aer backend init.

---

## Stage 1 — Hypothesis Generation

Generate a **specific, falsifiable quantum hypothesis**. Good hypotheses have:

- A measurable observable (fidelity, entropy, correlation, gate depth advantage)
- A classical baseline to beat or compare against
- A regime of interest (qubit count, noise level, circuit depth, connectivity)
- A novelty claim (why this hasn't been trivially observed before)

**Hypothesis template:**
```
System: [what quantum system / circuit family]
Claim:  [what property we expect to observe and in what regime]
Why novel: [what makes this non-obvious]
Classical baseline: [what classical simulation or known result we compare to]
Observable: [how we measure success — fidelity, entropy, speedup, etc.]
Falsification: [what result would prove the hypothesis wrong]
```

For open-ended discovery, generate 3–5 candidate hypotheses across different domains
(variational algorithms, error mitigation, entanglement dynamics, quantum walks, etc.)
and let the user select or combine.

**Read `references/hypothesis_bank.md` for a curated set of high-potential starting points.**

---

## Stage 2 — Circuit Design

Design the minimal circuit that tests the hypothesis.

Key principles:
- Start with the smallest qubit count that demonstrates the effect (n ≥ 2, usually ≤ 10)
- Parameterize depth/entanglement to sweep across regimes
- Include a classical reference circuit (product state or random circuit) as control
- Add measurement barriers to prevent optimizer reordering

Use the circuit builder helper:
→ Read `scripts/circuit_builder.py` for reusable circuit primitives (GHZ, random Clifford,
  hardware-efficient ansatz, quantum walk, QAOA, VQE layers, etc.)

Always print circuit summary before running:
```python
print(circuit.draw(output='text'))
print(f"Depth: {circuit.depth()}, Gates: {circuit.count_ops()}")
```

---

## Stage 3 — Aer Simulation

Run on Qiskit Aer with appropriate noise model:

```python
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

# Noiseless baseline
sim_ideal = AerSimulator(method='statevector')   # for small circuits
sim_ideal = AerSimulator(method='matrix_product_state')  # for larger circuits

# Noisy simulation (use when preparing for hardware)
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke
noise_model = NoiseModel.from_backend(FakeSherbrooke())
sim_noisy = AerSimulator.from_backend(FakeSherbrooke())
```

**Simulation strategy by qubit count:**
| Qubits | Method | Notes |
|--------|--------|-------|
| ≤ 20   | `statevector` | Exact, fast |
| 20–50  | `matrix_product_state` | Good for low entanglement |
| 50+    | `stabilizer` | Clifford only |
| Any    | `aer_simulator` | Auto-select |

Run with sufficient shots (default: 8192 for statistics, 1024 for quick scan):

```python
from qiskit import transpile
tcirc = transpile(circuit, sim_ideal)
job = sim_ideal.run(tcirc, shots=8192)
result = job.result()
counts = result.get_counts()
```

→ Read `scripts/analysis.py` for entropy, fidelity, and correlation extractors.

---

## Stage 4 — Plausibility Gate

Before submitting to real hardware, the simulated result must pass all criteria:

**Hard gates (any failure → do not submit):**
- [ ] Signal is statistically significant (p < 0.05 vs. classical baseline)
- [ ] Result is not trivially explainable (not just |0⟩ state, not uniform distribution)
- [ ] Circuit depth ≤ hardware coherence budget (check `T1/T2` vs gate time × depth)
- [ ] Qubit count ≤ available hardware qubits (default budget: ≤ 127 for IBM Eagle)

**Soft gates (document if failing, still may proceed):**
- [ ] Effect persists under simulated noise (noisy sim matches ideal qualitatively)
- [ ] Effect scales with qubit count in the expected direction
- [ ] No known theorem rules out the hypothesis

**Coherence budget check:**
```python
# Typical IBM Falcon/Eagle: T1 ~ 100μs, 2Q gate ~ 300ns
# Max meaningful depth ≈ T1 / gate_time ≈ 333 gates, but realistically ≤ 100
max_hw_depth = 100  # conservative
if circuit.depth() > max_hw_depth:
    print(f"WARNING: Circuit depth {circuit.depth()} may exceed coherence. Optimize first.")
```

If plausibility gate fails: iterate on circuit design (Stage 2) or refine hypothesis.

---

## Stage 5 — Real Hardware Submission

Only run this stage if Stage 4 passes all hard gates and user explicitly confirms.

```python
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit_ibm_runtime import Session

# Authenticate
service = QiskitRuntimeService(
    channel="ibm_quantum",
    token=os.environ["IBM_QUANTUM_TOKEN"]
)

# Select least-busy backend with enough qubits
from qiskit_ibm_runtime import least_busy
backend = service.least_busy(
    operational=True,
    simulator=False,
    min_num_qubits=circuit.num_qubits
)
print(f"Selected backend: {backend.name}")
print(f"Queue depth: {backend.status().pending_jobs}")

# Transpile for target backend
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
isa_circuit = pm.run(circuit)
print(f"Transpiled depth: {isa_circuit.depth()}")

# Submit with session (batch multiple circuits if possible)
with Session(backend=backend) as session:
    sampler = Sampler(mode=session)
    job = sampler.run([isa_circuit], shots=4096)
    print(f"Job ID: {job.job_id()}")
    hw_result = job.result()
```

**Always save job ID immediately** — hardware jobs are async and may take hours in queue:
```python
with open("hw_job_ids.txt", "a") as f:
    f.write(f"{job.job_id()}\n")
```

→ Read `scripts/hw_retrieval.py` for polling job status and retrieving results later.

---

## Stage 6 — Analysis & Discovery Reporting

Compare simulation vs. hardware results:

```python
# Key metrics to compute and compare
metrics = {
    "sim_entropy":    compute_entropy(sim_counts),
    "hw_entropy":     compute_entropy(hw_counts),
    "fidelity":       state_fidelity(sim_statevector, hw_counts),
    "tvd":            total_variation_distance(sim_counts, hw_counts),
    "classical_bound": compute_classical_baseline(),
}
```

**Novelty assessment checklist:**
- Does the result exceed the classical baseline in the claimed metric?
- Is the hardware result consistent with simulation (TVD < 0.15 is acceptable)?
- Is the effect size large enough to be meaningful (not just noise)?
- Does the result generalize (test at n+2 qubits if possible)?
- Does it relate to known open problems? (Check `references/open_problems.md`)

**Discovery report template** (always produce this):
```
## Discovery Report — [date]

**Hypothesis:** [restate]
**Circuit:** [n qubits, depth, gate count]
**Simulation result:** [key metric + value]
**Hardware result:** [key metric + value, backend name, shots]
**Classical baseline:** [value]
**Quantum advantage:** [yes/no/partial + magnitude]
**Novelty assessment:** [known / related to known / potentially novel]
**Next experiments:** [3 follow-up hypotheses]
**Reproducibility:** Job ID [xxx], circuit saved to [path]
```

→ Read `scripts/analysis.py` for all metric computations.
→ Read `references/open_problems.md` for cross-referencing against known open questions.

---

## Iterative Discovery Loop

After each experiment, generate 3 follow-up hypotheses based on the result:
- **Amplify:** If effect found, push to larger qubit count or deeper circuit
- **Perturb:** Change one parameter (connectivity, gate set, noise level) to isolate cause
- **Contrast:** Find the regime where the effect disappears (boundary exploration)

The goal is to build a **discovery tree** — each result spawns new branches. Document
the tree in `discovery_log.md` (append after each experiment).

---

## Error Mitigation (when hardware results are noisy)

For NISQ-era hardware, apply mitigation before analysis:

```python
from qiskit_ibm_runtime import Options

options = Options()
options.resilience_level = 1        # basic twirling
# options.resilience_level = 2      # ZNE (zero noise extrapolation) — for depth < 50
# options.resilience_level = 3      # PEC — expensive, use sparingly

sampler = Sampler(mode=session, options=options)
```

**Mitigation levels:**
| Level | Method | Cost | Use when |
|-------|--------|------|----------|
| 0 | None | 1x | Clifford benchmarking |
| 1 | Twirling | 1.5x | Default for NISQ |
| 2 | ZNE | 3–5x | Depth < 50, want accuracy |
| 3 | PEC | 30–100x | Small circuits, high fidelity needed |

---

## Quick Reference: Common Experiment Types

| Goal | Circuit type | Qubits | Key metric |
|------|-------------|--------|------------|
| Entanglement dynamics | GHZ / cluster state | 3–10 | Entropy, concurrence |
| Quantum walk | Coined/continuous | 4–12 | Probability distribution |
| VQE / ground state | Hardware-efficient ansatz | 2–8 | Energy convergence |
| QAOA | Problem + mixer layers | 4–16 | Approximation ratio |
| Randomness / chaos | Random Clifford | 10–50 | Porter-Thomas, frame potential |
| Error mitigation | Simple 2Q circuit | 2–5 | Fidelity vs. mitigation cost |
| Quantum advantage | Problem-specific | n | Classical runtime vs. shots |

---

## Files in This Skill

| Path | Purpose |
|------|---------|
| `scripts/setup_env.py` | Environment check, backend initialization |
| `scripts/circuit_builder.py` | Reusable circuit primitives library |
| `scripts/analysis.py` | Entropy, fidelity, TVD, classical bounds |
| `scripts/hw_retrieval.py` | Poll and retrieve async hardware jobs |
| `references/hypothesis_bank.md` | Curated high-potential hypotheses |
| `references/open_problems.md` | Known open questions to cross-reference |
