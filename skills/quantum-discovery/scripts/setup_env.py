"""
Quantum Discovery — Environment Setup
Checks dependencies, initializes Aer backends, optionally connects to IBM Quantum.
Run this at the start of every session.
"""

import sys
import os
import importlib

# ── Dependency check ──────────────────────────────────────────────────────────

REQUIRED = {
    "qiskit":               "1.0.0",
    "qiskit_aer":           "0.14.0",
    "qiskit_ibm_runtime":   "0.20.0",
    "numpy":                "1.24.0",
    "scipy":                "1.10.0",
    "matplotlib":           "3.7.0",
    "pandas":               "2.0.0",
}

def check_deps():
    missing = []
    outdated = []
    for pkg, min_ver in REQUIRED.items():
        try:
            mod = importlib.import_module(pkg)
            ver = getattr(mod, "__version__", "0.0.0")
            from packaging.version import Version
            if Version(ver) < Version(min_ver):
                outdated.append((pkg, ver, min_ver))
        except ImportError:
            missing.append(pkg)
    return missing, outdated

missing, outdated = check_deps()
if missing:
    print(f"[SETUP] Installing missing packages: {missing}")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet"] + missing)
if outdated:
    for pkg, ver, req in outdated:
        print(f"[SETUP] Warning: {pkg}=={ver} < required {req}")

# ── Aer Backend Initialization ────────────────────────────────────────────────

from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

def get_ideal_backend(method: str = "auto") -> AerSimulator:
    """
    Return an ideal (noiseless) Aer backend.
    method: 'statevector' | 'matrix_product_state' | 'stabilizer' | 'auto'
    """
    if method == "auto":
        return AerSimulator()
    return AerSimulator(method=method)

def get_noisy_backend(fake_backend_name: str = "FakeSherbrooke") -> AerSimulator:
    """
    Return an Aer backend with noise model from a fake IBM backend.
    Available fakes: FakeSherbrooke (127q), FakeNairobi (7q), FakeMontreal (27q)
    """
    from qiskit_ibm_runtime import fake_provider
    fb_cls = getattr(fake_provider, fake_backend_name)
    fb = fb_cls()
    return AerSimulator.from_backend(fb)

# ── IBM Quantum Connection ─────────────────────────────────────────────────────

def get_ibm_service(token: str | None = None):
    """
    Connect to IBM Quantum. Returns QiskitRuntimeService or None if no token.
    Looks for token in: argument → IBM_QUANTUM_TOKEN env var → ~/.qiskit/qiskit-ibm.json
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    token = token or os.environ.get("IBM_QUANTUM_TOKEN")
    if not token:
        # Try saved credentials
        try:
            service = QiskitRuntimeService()
            print("[SETUP] IBM Quantum: connected via saved credentials")
            return service
        except Exception:
            print("[SETUP] IBM Quantum: no token found. Simulation-only mode.")
            return None

    try:
        QiskitRuntimeService.save_account(
            channel="ibm_quantum", token=token, overwrite=True
        )
        service = QiskitRuntimeService(channel="ibm_quantum", token=token)
        print(f"[SETUP] IBM Quantum: connected. Plan: {service.active_account().get('plan', 'unknown')}")
        return service
    except Exception as e:
        print(f"[SETUP] IBM Quantum: connection failed — {e}")
        return None

def select_backend(service, min_qubits: int = 5, prefer_fast: bool = True):
    """
    Select the least-busy real backend with enough qubits.
    Returns backend or None.
    """
    if service is None:
        return None
    try:
        backends = service.backends(
            operational=True,
            simulator=False,
            min_num_qubits=min_qubits,
        )
        if not backends:
            print(f"[SETUP] No real backends with >= {min_qubits} qubits available")
            return None
        # Sort by queue length
        ranked = sorted(backends, key=lambda b: b.status().pending_jobs)
        best = ranked[0]
        print(f"[SETUP] Selected backend: {best.name} | Qubits: {best.num_qubits} | Queue: {best.status().pending_jobs}")
        return best
    except Exception as e:
        print(f"[SETUP] Backend selection failed: {e}")
        return None

# ── Quick Sanity Test ─────────────────────────────────────────────────────────

def sanity_test():
    """Run a 2-qubit Bell state on Aer to verify setup."""
    from qiskit import QuantumCircuit, transpile
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    sim = get_ideal_backend("statevector")
    tcirc = transpile(qc, sim)
    result = sim.run(tcirc, shots=1024).result()
    counts = result.get_counts()
    assert set(counts.keys()) <= {"00", "11"}, f"Unexpected counts: {counts}"
    fidelity = (counts.get("00", 0) + counts.get("11", 0)) / 1024
    print(f"[SETUP] Sanity test: Bell state fidelity = {fidelity:.3f} (expect ~1.0)")
    return fidelity > 0.95

if __name__ == "__main__":
    print("=== Quantum Discovery Environment Setup ===")
    ok = sanity_test()
    print(f"[SETUP] Status: {'READY' if ok else 'FAILED'}")
