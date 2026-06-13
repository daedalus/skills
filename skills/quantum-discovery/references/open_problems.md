# Open Problems in Quantum Systems

Reference for cross-checking experimental results against known open questions.
If a result bears on any of these, flag it prominently in the discovery report.

---

## Complexity and Advantage

- **OP-C1**: Does quantum advantage exist for any practical (non-cryptographic) problem
  in the NISQ era? Characterizing the exact frontier is open.
- **OP-C2**: What is the minimum circuit depth for quantum advantage over classical
  simulation for random circuit sampling? Google/USTC results are contested.
- **OP-C3**: Are there exponential quantum speedups for optimization problems beyond
  Grover-type speedups? QAOA landscape remains poorly understood.

## Noise and Error

- **OP-N1**: What is the exact threshold for fault-tolerant quantum computation under
  realistic correlated noise models (not i.i.d.)?
- **OP-N2**: Can error mitigation (ZNE, PEC) provide a useful computational advantage
  on NISQ hardware for any practically relevant problem?
- **OP-N3**: What is the maximum useful circuit depth for NISQ devices as a function
  of qubit count and error rates?

## Entanglement and Many-Body Physics

- **OP-E1**: Full characterization of measurement-induced phase transitions (MIPT) in
  hybrid quantum-classical circuits. Critical exponents are debated.
- **OP-E2**: Is there a sharp entanglement phase transition in random circuits on
  non-all-to-all connectivity (e.g., heavy-hex)?
- **OP-E3**: Relationship between magic (non-stabilizerness) and classical simulability —
  precise boundary is unknown for structured circuits.

## Quantum Simulation

- **OP-S1**: Can near-term quantum devices simulate classically intractable condensed
  matter problems (e.g., Hubbard model at finite doping) with useful accuracy?
- **OP-S2**: Floquet pre-thermalization timescales in interacting quantum systems —
  exact dependence on frequency and interaction strength is open.
- **OP-S3**: Quantum advantage for simulating open quantum systems (Lindblad dynamics)?

## Metrology

- **OP-M1**: Can entangled states provide practical metrological advantage in the
  presence of realistic decoherence (beyond toy models)?
- **OP-M2**: Tight bounds on quantum Fisher information under depolarizing noise for
  multi-qubit states beyond GHZ.

## Algorithms

- **OP-A1**: Does QAOA achieve better-than-classical approximation ratios for MaxCut
  at finite depth? P=1 is solved; P≥2 on large instances is open.
- **OP-A2**: Barren plateau characterization: for which ansatz families can they be
  provably avoided while maintaining expressibility?
- **OP-A3**: Quantum speedup for machine learning: separating hype from provable cases.

---

## Landmark Results to Know (don't re-discover these)

- GHZ state preparation: demonstrated up to 1000+ qubits (not novel)
- Quantum supremacy (random circuit sampling): Google 2019, USTC 2020–2021
- VQE ground state for H2, LiH: widely reproduced
- Quantum error correction below threshold: demonstrated 2023 (Google)
- Discrete-time quantum walks: demonstrated on many platforms
- TFIM phase transition via VQE: demonstrated multiple times
- QFI > n for GHZ: well-known, but noise scaling behavior on specific hardware is still mappable

---

## How to Use This File

When you have a discovery report result:
1. Search this file for related open problems
2. If result bears on an OP: flag it as "potentially novel — touches OP-XX"
3. If result matches a landmark: mark as "reproduced known result" (still useful for calibration)
4. If result is unrelated to known OPs: perform a quick web search for recent papers
   before claiming novelty
