"""
Quantum Discovery — Analysis Toolkit
Entropy, fidelity, distance metrics, and classical baseline computations.
"""

import numpy as np
from collections import Counter
from typing import Union


# ── Type aliases ──────────────────────────────────────────────────────────────
Counts = dict[str, int]
Statevector = np.ndarray


# ── Entropy ───────────────────────────────────────────────────────────────────

def counts_to_probs(counts: Counts) -> dict[str, float]:
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()}

def shannon_entropy(counts: Counts) -> float:
    """Shannon entropy H(X) in bits."""
    probs = counts_to_probs(counts)
    return -sum(p * np.log2(p) for p in probs.values() if p > 0)

def renyi_entropy(counts: Counts, alpha: float = 2.0) -> float:
    """Rényi entropy S_α. α=2 is collision entropy."""
    probs = np.array(list(counts_to_probs(counts).values()))
    if alpha == 1:
        return shannon_entropy(counts)
    return np.log2(np.sum(probs ** alpha)) / (1 - alpha)

def sv_entanglement_entropy(statevector: Statevector, subsystem_a: list[int]) -> float:
    """
    Von Neumann entanglement entropy S(A) from statevector.
    subsystem_a: list of qubit indices in subsystem A
    """
    n = int(np.log2(len(statevector)))
    all_qubits = list(range(n))
    subsystem_b = [q for q in all_qubits if q not in subsystem_a]

    dim_a = 2 ** len(subsystem_a)
    dim_b = 2 ** len(subsystem_b)

    # Reshape into matrix [A, B]
    # Qiskit ordering: qubit 0 is LSB
    perm = subsystem_a + subsystem_b
    sv_reshaped = statevector.reshape([2] * n)
    sv_perm = np.transpose(sv_reshaped, perm).reshape(dim_a, dim_b)

    # Schmidt decomposition via SVD
    _, s, _ = np.linalg.svd(sv_perm)
    s2 = s ** 2
    s2 = s2[s2 > 1e-12]  # filter zeros
    return -np.sum(s2 * np.log2(s2))


# ── Distance Metrics ──────────────────────────────────────────────────────────

def total_variation_distance(counts_a: Counts, counts_b: Counts) -> float:
    """TVD = 0.5 * Σ|p_a(x) - p_b(x)|. Range [0, 1]."""
    all_keys = set(counts_a) | set(counts_b)
    total_a = sum(counts_a.values())
    total_b = sum(counts_b.values())
    tvd = sum(
        abs(counts_a.get(k, 0) / total_a - counts_b.get(k, 0) / total_b)
        for k in all_keys
    ) / 2
    return tvd

def hellinger_distance(counts_a: Counts, counts_b: Counts) -> float:
    """Hellinger distance. Range [0, 1]."""
    all_keys = set(counts_a) | set(counts_b)
    total_a = sum(counts_a.values())
    total_b = sum(counts_b.values())
    h2 = sum(
        (np.sqrt(counts_a.get(k, 0) / total_a) - np.sqrt(counts_b.get(k, 0) / total_b)) ** 2
        for k in all_keys
    ) / 2
    return np.sqrt(h2)

def kl_divergence(counts_p: Counts, counts_q: Counts, epsilon: float = 1e-10) -> float:
    """KL divergence D_KL(P||Q). Asymmetric. Use with caution on sparse counts."""
    all_keys = set(counts_p) | set(counts_q)
    total_p = sum(counts_p.values())
    total_q = sum(counts_q.values())
    kl = sum(
        (counts_p.get(k, 0) / total_p) *
        np.log((counts_p.get(k, 0) / total_p + epsilon) /
               (counts_q.get(k, 0) / total_q + epsilon))
        for k in all_keys
        if counts_p.get(k, 0) > 0
    )
    return kl


# ── Fidelity ──────────────────────────────────────────────────────────────────

def counts_fidelity(counts_ideal: Counts, counts_noisy: Counts) -> float:
    """
    Fidelity estimate from counts: F = (Σ √(p_ideal * p_noisy))²
    Bhattacharyya coefficient squared.
    """
    all_keys = set(counts_ideal) | set(counts_noisy)
    total_i = sum(counts_ideal.values())
    total_n = sum(counts_noisy.values())
    bc = sum(
        np.sqrt(counts_ideal.get(k, 0) / total_i * counts_noisy.get(k, 0) / total_n)
        for k in all_keys
    )
    return bc ** 2

def parity_fidelity_ghz(counts: Counts, n: int) -> float:
    """
    GHZ state fidelity via parity oscillation method.
    Counts must include both Z-basis and X-basis measurements for full estimate.
    Simple version: just check |0...0⟩ + |1...1⟩ overlap.
    """
    total = sum(counts.values())
    zeros = "0" * n
    ones = "1" * n
    p_ghz = (counts.get(zeros, 0) + counts.get(ones, 0)) / total
    return p_ghz  # Lower bound on fidelity


# ── Classical Baselines ───────────────────────────────────────────────────────

def uniform_distribution(n_qubits: int) -> Counts:
    """Uniform distribution over all 2^n bitstrings."""
    n = 2 ** n_qubits
    return {format(i, f"0{n_qubits}b"): 1 for i in range(n)}

def classical_random_counts(n_qubits: int, shots: int,
                             seed: int | None = None) -> Counts:
    """Classically sampled uniform random bitstrings."""
    rng = np.random.default_rng(seed)
    samples = rng.integers(0, 2 ** n_qubits, size=shots)
    counts = Counter(format(s, f"0{n_qubits}b") for s in samples)
    return dict(counts)

def max_classical_entropy(n_qubits: int) -> float:
    """Maximum entropy achievable classically = n bits."""
    return float(n_qubits)


# ── Statistical Significance ──────────────────────────────────────────────────

def chi_squared_vs_uniform(counts: Counts) -> tuple[float, float]:
    """
    Chi-squared test of counts vs. uniform distribution.
    Returns (chi2_stat, p_value).
    """
    from scipy.stats import chisquare
    n_qubits = len(next(iter(counts)))
    expected_count = sum(counts.values()) / (2 ** n_qubits)
    all_keys = [format(i, f"0{n_qubits}b") for i in range(2 ** n_qubits)]
    observed = [counts.get(k, 0) for k in all_keys]
    chi2, pval = chisquare(observed, f_exp=[expected_count] * len(all_keys))
    return chi2, pval

def bootstrap_entropy_ci(counts: Counts, n_bootstrap: int = 1000,
                          alpha: float = 0.05) -> tuple[float, float, float]:
    """
    Bootstrap 95% CI for Shannon entropy.
    Returns (entropy, lower_bound, upper_bound).
    """
    samples = []
    keys = list(counts.keys())
    freqs = np.array(list(counts.values()))
    total = freqs.sum()
    rng = np.random.default_rng(42)
    for _ in range(n_bootstrap):
        resampled = rng.multinomial(total, freqs / total)
        fake_counts = dict(zip(keys, resampled))
        samples.append(shannon_entropy(fake_counts))
    h = shannon_entropy(counts)
    lo = np.percentile(samples, 100 * alpha / 2)
    hi = np.percentile(samples, 100 * (1 - alpha / 2))
    return h, lo, hi


# ── Quantum Fisher Information ────────────────────────────────────────────────

def qfi_parity_ghz(counts_z: Counts, counts_x_phases: list[tuple[float, Counts]],
                   n: int) -> float:
    """
    Estimate QFI for GHZ-like state via parity oscillation.
    counts_z: Z-basis counts
    counts_x_phases: list of (phi, counts) for X(phi) basis measurements
    n: number of qubits
    Returns QFI estimate (shot noise limit = n, Heisenberg limit = n²)
    """
    # Parity operator expectation values
    def parity(counts: Counts) -> float:
        total = sum(counts.values())
        return sum(
            (-1) ** k.count("1") * v / total
            for k, v in counts.items()
        )

    phases = [phi for phi, _ in counts_x_phases]
    parities = [parity(c) for _, c in counts_x_phases]

    # Fit A * cos(n * phi + phi0) to extract contrast
    from scipy.optimize import curve_fit
    def model(phi, A, phi0):
        return A * np.cos(n * np.array(phi) + phi0)
    try:
        popt, pcov = curve_fit(model, phases, parities, p0=[0.8, 0.0])
        contrast = abs(popt[0])
        qfi_estimate = (n * contrast) ** 2  # QFI ≈ (n * contrast)²
        return qfi_estimate
    except Exception:
        return float("nan")


# ── Reporting ─────────────────────────────────────────────────────────────────

def full_report(sim_counts: Counts, hw_counts: Counts | None,
                n_qubits: int, classical_counts: Counts | None = None) -> dict:
    """
    Compute all key metrics and return a report dict.
    """
    report = {}
    report["sim_entropy"]    = shannon_entropy(sim_counts)
    report["sim_renyi2"]     = renyi_entropy(sim_counts, alpha=2)
    report["max_entropy"]    = float(n_qubits)
    report["sim_chi2_pval"]  = chi_squared_vs_uniform(sim_counts)[1]

    if hw_counts:
        report["hw_entropy"]  = shannon_entropy(hw_counts)
        report["sim_hw_tvd"]  = total_variation_distance(sim_counts, hw_counts)
        report["sim_hw_fid"]  = counts_fidelity(sim_counts, hw_counts)

    if classical_counts:
        report["classical_entropy"]   = shannon_entropy(classical_counts)
        report["sim_vs_classical_tvd"] = total_variation_distance(sim_counts, classical_counts)
        report["quantum_advantage"]    = report["sim_entropy"] > report["classical_entropy"]

    return report

def print_report(report: dict):
    print("\n=== Analysis Report ===")
    for k, v in report.items():
        if isinstance(v, float):
            print(f"  {k:30s}: {v:.4f}")
        else:
            print(f"  {k:30s}: {v}")
    print("=" * 40)
