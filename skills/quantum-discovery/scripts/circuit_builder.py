"""
Quantum Discovery — Circuit Builder
Reusable circuit primitives for experiments.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import (
    QFT, TwoLocal, EfficientSU2, RealAmplitudes,
    PauliEvolutionGate
)


# ── Bell / GHZ States ─────────────────────────────────────────────────────────

def ghz_circuit(n: int, measure: bool = True) -> QuantumCircuit:
    """GHZ state on n qubits: (|0...0⟩ + |1...1⟩)/√2"""
    qc = QuantumCircuit(n, n if measure else 0)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    if measure:
        qc.barrier()
        qc.measure_all()
    return qc

def bell_state(state: int = 0) -> QuantumCircuit:
    """
    Bell states: 0=Φ+, 1=Φ-, 2=Ψ+, 3=Ψ-
    """
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    if state == 1:   qc.z(0)
    elif state == 2: qc.x(1)
    elif state == 3: qc.z(0); qc.x(1)
    return qc


# ── Variational Ansätze ───────────────────────────────────────────────────────

def hardware_efficient_ansatz(n: int, reps: int = 2,
                               entanglement: str = "linear") -> QuantumCircuit:
    """
    Hardware-efficient ansatz: Ry-Rz layers + CNOT entanglement.
    entanglement: 'linear' | 'circular' | 'full'
    """
    return EfficientSU2(num_qubits=n, reps=reps, entanglement=entanglement)

def real_amplitudes_ansatz(n: int, reps: int = 2) -> QuantumCircuit:
    """RealAmplitudes ansatz — good for ground state VQE."""
    return RealAmplitudes(num_qubits=n, reps=reps)

def qaoa_circuit(cost_terms: list[tuple], mixer_beta: float = 0.5,
                 gamma: float = 0.5, p: int = 1) -> QuantumCircuit:
    """
    QAOA circuit for MaxCut / combinatorial problems.
    cost_terms: list of (i, j) edges for ZZ coupling
    p: number of QAOA layers
    """
    n = max(max(i, j) for i, j in cost_terms) + 1
    qc = QuantumCircuit(n)
    # Initial state
    qc.h(range(n))
    for _ in range(p):
        # Cost unitary
        for (i, j) in cost_terms:
            qc.cx(i, j)
            qc.rz(2 * gamma, j)
            qc.cx(i, j)
        qc.barrier()
        # Mixer unitary
        for q in range(n):
            qc.rx(2 * mixer_beta, q)
        qc.barrier()
    qc.measure_all()
    return qc


# ── Quantum Walks ─────────────────────────────────────────────────────────────

def discrete_quantum_walk_1d(n_steps: int, coin_angle: float = np.pi / 4,
                              disorder: float = 0.0) -> QuantumCircuit:
    """
    1D discrete-time quantum walk.
    Position encoded in ceil(log2(2*n_steps+1)) qubits, coin in 1 qubit.
    disorder: random noise on coin angle (0 = no disorder = Anderson localization off)
    """
    n_pos_bits = int(np.ceil(np.log2(2 * n_steps + 3)))
    total_qubits = n_pos_bits + 1  # coin qubit last
    qc = QuantumCircuit(total_qubits)
    coin_q = total_qubits - 1
    pos_qubits = list(range(n_pos_bits))

    # Initialize at center position, coin in |+⟩
    # (simplified: start at |0⟩ position, superposition coin)
    qc.h(coin_q)

    for step in range(n_steps):
        # Coin flip (with optional disorder)
        angle = coin_angle + np.random.uniform(-disorder, disorder) if disorder > 0 else coin_angle
        qc.ry(2 * angle, coin_q)

        # Shift operation (conditional increment/decrement)
        # Simplified: use controlled-X on position register
        qc.cx(coin_q, pos_qubits[0])
        qc.barrier()

    qc.measure_all()
    return qc


# ── Random Circuits ───────────────────────────────────────────────────────────

def random_clifford_circuit(n: int, depth: int,
                             seed: int | None = None) -> QuantumCircuit:
    """Random circuit of Clifford gates (H, S, CNOT, CZ)."""
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n)
    single_gate_fns = [
        lambda q: qc.h(q),
        lambda q: qc.s(q),
        lambda q: qc.sdg(q),
        lambda q: qc.x(q),
        lambda q: qc.y(q),
        lambda q: qc.z(q),
    ]
    for _ in range(depth):
        # Single-qubit layer
        for q in range(n):
            rng.choice(single_gate_fns)(q)
        # Two-qubit layer
        pairs = [(i, i + 1) for i in range(0, n - 1, 2)]
        for (a, b) in pairs:
            if rng.random() < 0.5:
                qc.cx(a, b)
            else:
                qc.cz(a, b)
        qc.barrier()
    qc.measure_all()
    return qc

def hybrid_circuit_with_measurements(n: int, depth: int,
                                      meas_rate: float = 0.1,
                                      seed: int | None = None) -> QuantumCircuit:
    """
    Random circuit with mid-circuit measurements — for MIPT experiments.
    meas_rate: probability of measuring each qubit after each layer.
    """
    rng = np.random.default_rng(seed)
    cr = ClassicalRegister(n * depth, "mid")
    qc = QuantumCircuit(n, cr)
    meas_idx = 0
    for d in range(depth):
        qc.h(range(n))
        pairs = [(i, i + 1) for i in range(0, n - 1, 2)]
        for (a, b) in pairs:
            qc.cx(a, b)
        # Mid-circuit measurements
        for q in range(n):
            if rng.random() < meas_rate:
                qc.measure(q, cr[meas_idx])
                qc.reset(q)  # reset after measurement (feed-forward)
                meas_idx += 1
        qc.barrier()
    qc.measure_all()
    return qc


# ── Hamiltonian Simulation ─────────────────────────────────────────────────────

def tfim_trotter_circuit(n: int, J: float = 1.0, h: float = 1.0,
                          dt: float = 0.1, steps: int = 10) -> QuantumCircuit:
    """
    1D Transverse-Field Ising Model via first-order Trotterization.
    H = -J Σ ZiZi+1 - h Σ Xi
    """
    qc = QuantumCircuit(n)
    qc.h(range(n))  # Start in |+⟩^n (ground state of X term)
    for _ in range(steps):
        # ZZ interaction
        for i in range(n - 1):
            qc.cx(i, i + 1)
            qc.rz(-2 * J * dt, i + 1)
            qc.cx(i, i + 1)
        # Transverse field
        for i in range(n):
            qc.rx(-2 * h * dt, i)
        qc.barrier()
    qc.measure_all()
    return qc

def floquet_circuit(n: int, J: float = 1.0, h_drive: float = 0.5,
                    n_cycles: int = 10, duty_cycle: float = 0.5) -> QuantumCircuit:
    """
    Floquet-driven Ising chain: alternating ZZ and X pulses.
    """
    qc = QuantumCircuit(n)
    qc.h(range(n))
    T_zz = duty_cycle
    T_x = 1 - duty_cycle
    for _ in range(n_cycles):
        for i in range(n - 1):
            qc.cx(i, i + 1)
            qc.rz(-2 * J * T_zz, i + 1)
            qc.cx(i, i + 1)
        for i in range(n):
            qc.rx(-2 * h_drive * T_x, i)
        qc.barrier()
    qc.measure_all()
    return qc


# ── Utility ───────────────────────────────────────────────────────────────────

def circuit_summary(qc: QuantumCircuit) -> dict:
    ops = qc.count_ops()
    return {
        "n_qubits": qc.num_qubits,
        "depth": qc.depth(),
        "gate_counts": dict(ops),
        "total_gates": sum(ops.values()),
        "two_qubit_gates": sum(v for k, v in ops.items() if k in ("cx", "cz", "ecr", "rzz")),
    }

def print_summary(qc: QuantumCircuit):
    s = circuit_summary(qc)
    print(f"Circuit: {s['n_qubits']}q | depth={s['depth']} | "
          f"2Q gates={s['two_qubit_gates']} | total={s['total_gates']}")
    print(qc.draw(output="text", fold=80))
