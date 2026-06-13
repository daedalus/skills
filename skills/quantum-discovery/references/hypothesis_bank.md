# Hypothesis Bank

Curated high-potential starting points for quantum discovery experiments.
Ordered by tractability (most tractable first within each domain).

---

## Domain 1: Entanglement Dynamics

**H1.1 — Entanglement Phase Transition in Random Circuits**
- Claim: Random 2-local circuits on n qubits exhibit a volume-to-area law entanglement
  transition as measurement rate p crosses a critical threshold p_c ≈ 0.16 (for n=10)
- Observable: Half-chain entanglement entropy S(n/2) vs. p
- Novelty angle: Exact p_c location shifts with qubit connectivity; map the phase boundary
  for IBM's heavy-hex topology
- Qubits: 6–12, Depth: 4–20 layers

**H1.2 — Magic State Concentration**
- Claim: Random Clifford + T circuits concentrate non-stabilizerness (magic) faster than
  predicted by random unitary theory for heavy-hex connectivity
- Observable: Stabilizer Rényi entropy M2
- Classical baseline: Haar-random prediction
- Qubits: 4–8

**H1.3 — Quantum Discord Without Entanglement**
- Claim: Two-qubit mixed states near the boundary of separable/entangled regime show
  non-zero quantum discord that is detectable under realistic noise
- Observable: Quantum discord via tomography
- Qubits: 2–4

---

## Domain 2: Quantum Algorithms

**H2.1 — QAOA Warm-Starting Advantage**
- Claim: QAOA initialized from a classical rounding heuristic solution achieves
  higher approximation ratio with 50% fewer layers than random initialization
- Observable: Approximation ratio for MaxCut on random 3-regular graphs
- Qubits: 6–14, Layers: 1–5
- Novelty: Characterize the advantage as a function of graph structure

**H2.2 — VQE Landscape Flatness Mitigation**
- Claim: Rotosolve optimizer escapes barren plateaus more reliably than COBYLA
  for hardware-efficient ansatz beyond 6 qubits under realistic noise
- Observable: Convergence rate, final energy, landscape gradient variance
- Qubits: 4–10

**H2.3 — Quantum Amplitude Estimation Without QPE**
- Claim: Iterative QAE (Grinko et al. 2021) achieves Heisenberg-limited scaling
  on IBM hardware for depth ≤ 30, but degrades to standard scaling for depth > 50
- Observable: Estimation error vs. oracle calls
- Qubits: 3–7

---

## Domain 3: Quantum Error and Noise

**H3.1 — Correlated Errors in IBM Heavy-Hex**
- Claim: Cross-resonance gate errors on IBM heavy-hex are spatially correlated
  beyond nearest-neighbor, detectable via simultaneous randomized benchmarking
- Observable: IRB decay rates, ZZ crosstalk matrix
- Novelty: Map full crosstalk graph for a 10+ qubit patch
- Qubits: 6–15

**H3.2 — Noise Tailoring for Discovery**
- Claim: Probabilistic error cancellation (PEC) improves fidelity for circuits with
  depth ≤ 30 but provides no advantage beyond depth 50 due to sampling overhead
- Observable: Fidelity vs. circuit depth for PEC vs. raw vs. ZNE
- Qubits: 4–6

**H3.3 — Leakage Characterization**
- Claim: State leakage to |2⟩ on transmon qubits is measurable via population
  imbalance in repeated X gate sequences and exceeds manufacturer specs at depth > 20
- Observable: Population in computational vs. leakage subspace
- Qubits: 1–3

---

## Domain 4: Quantum Walks and Dynamics

**H4.1 — Anderson Localization in Disordered Quantum Walk**
- Claim: A 1D discrete-time quantum walk with random coin operators exhibits
  Anderson localization (sub-diffusive spreading) for disorder strength W > 0.5
- Observable: Position variance σ²(t) vs. t; classical diffusion σ²(t) ~ t
- Qubits: 6–12 (encoding position in binary)
- Novelty: First observation on heavy-hex; localization length vs. W mapping

**H4.2 — Topological Quantum Walk Edge States**
- Claim: Split-step quantum walk on a finite 1D chain shows topologically protected
  edge states robust to local perturbations, observable in probability distribution
- Observable: Probability concentration at chain endpoints vs. bulk disorder
- Qubits: 8–12

---

## Domain 5: Quantum Simulation

**H5.1 — Ising Model Phase Transition**
- Claim: 1D transverse-field Ising model (TFIM) shows a phase transition at J/h = 1
  detectable via second-order Rényi entropy peak in VQE ground state preparation
- Observable: S2 vs. J/h ratio
- Qubits: 4–8, linear connectivity
- Classical baseline: Exact diagonalization (up to 20 qubits)

**H5.2 — Floquet Heating Rate**
- Claim: Periodically driven (Floquet) Ising chain heats to infinite temperature
  at a rate that depends non-monotonically on drive frequency, with a slow-heating
  plateau (pre-thermal regime) detectable at intermediate frequencies
- Observable: Energy density vs. drive cycles
- Qubits: 6–10

---

## Domain 6: Benchmarking and Metrology

**H6.1 — GHZ State Fidelity Scaling**
- Claim: GHZ state fidelity on IBM hardware scales as F(n) ~ exp(-α·n) where α
  deviates from single-qubit error rates by > 20%, suggesting multi-qubit correlated errors
- Observable: GHZ fidelity via parity oscillation for n = 2..10
- Novelty: Extract α and compare to manufacturer error rates

**H6.2 — Quantum Fisher Information in Noisy GHZ**
- Claim: Noisy GHZ states remain metrologically useful (QFI > n, Heisenberg-like)
  for n ≤ 5 on IBM hardware despite decoherence, but fall below shot-noise limit for n > 7
- Observable: QFI via variance of parity operator
- Qubits: 2–10

---

## Selection Criteria

When choosing a hypothesis to test, prefer:
1. **Low circuit depth** (depth ≤ 50 for hardware viability)
2. **Clear classical baseline** (makes novelty unambiguous)
3. **Parameterizable** (can sweep a parameter to map a regime)
4. **Falsifiable on simulator first** (don't burn hardware shots on a trivially wrong hypothesis)
5. **Related to an open problem** (see `open_problems.md`)
