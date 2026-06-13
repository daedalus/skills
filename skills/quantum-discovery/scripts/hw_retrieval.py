"""
Quantum Discovery — Hardware Job Retrieval
Poll and retrieve async IBM Quantum hardware jobs.
"""

import time
import json
import os
from pathlib import Path


JOB_LOG = Path("hw_job_ids.txt")


def save_job(job_id: str, metadata: dict | None = None):
    """Persist a job ID with optional metadata."""
    entry = {"job_id": job_id, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
    if metadata:
        entry.update(metadata)
    with open(JOB_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[HW] Job saved: {job_id}")


def list_saved_jobs() -> list[dict]:
    """List all saved job IDs."""
    if not JOB_LOG.exists():
        return []
    jobs = []
    with open(JOB_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    jobs.append(json.loads(line))
                except json.JSONDecodeError:
                    jobs.append({"job_id": line})
    return jobs


def poll_job(service, job_id: str, timeout_sec: int = 300,
             poll_interval: int = 10) -> dict | None:
    """
    Poll a job until done or timeout.
    Returns result dict or None on timeout.
    """
    job = service.job(job_id)
    elapsed = 0
    while elapsed < timeout_sec:
        status = job.status()
        print(f"[HW] Job {job_id}: {status} ({elapsed}s elapsed)")
        if status in ("DONE", "ERROR", "CANCELLED"):
            break
        time.sleep(poll_interval)
        elapsed += poll_interval

    if job.status() == "DONE":
        result = job.result()
        print(f"[HW] Job {job_id}: completed successfully")
        return result
    else:
        print(f"[HW] Job {job_id}: final status = {job.status()}")
        return None


def retrieve_counts(result, pub_index: int = 0) -> dict[str, int]:
    """
    Extract counts from SamplerV2 result.
    pub_index: which circuit in the batch (usually 0).
    """
    pub_result = result[pub_index]
    # SamplerV2 returns BitArray
    bit_array = pub_result.data.meas
    counts = bit_array.get_counts()
    return counts


def retrieve_all_pending(service, timeout_sec: int = 60) -> dict[str, dict]:
    """
    Check status of all saved jobs. Return dict of {job_id: result or status}.
    """
    jobs = list_saved_jobs()
    results = {}
    for entry in jobs:
        jid = entry["job_id"]
        try:
            job = service.job(jid)
            status = job.status()
            if status == "DONE":
                result = job.result()
                results[jid] = {"status": "DONE", "result": result}
                print(f"[HW] {jid}: DONE")
            else:
                results[jid] = {"status": str(status)}
                print(f"[HW] {jid}: {status}")
        except Exception as e:
            results[jid] = {"status": "ERROR", "error": str(e)}
            print(f"[HW] {jid}: ERROR — {e}")
    return results


def compare_sim_hw(sim_counts: dict, hw_counts: dict,
                   n_qubits: int | None = None) -> dict:
    """
    Quick comparison between simulation and hardware counts.
    Returns metrics dict.
    """
    from analysis import total_variation_distance, counts_fidelity, shannon_entropy
    return {
        "tvd":        total_variation_distance(sim_counts, hw_counts),
        "fidelity":   counts_fidelity(sim_counts, hw_counts),
        "sim_entropy": shannon_entropy(sim_counts),
        "hw_entropy":  shannon_entropy(hw_counts),
        "hw_consistent": total_variation_distance(sim_counts, hw_counts) < 0.15,
    }


def plausibility_gate(circuit, sim_counts: dict, n_qubits: int,
                      max_depth: int = 100) -> tuple[bool, list[str]]:
    """
    Run all plausibility checks before hardware submission.
    Returns (pass: bool, reasons: list[str]).
    """
    from scipy.stats import chisquare
    import numpy as np

    fails = []
    warns = []

    # Hard gate 1: Circuit depth
    if circuit.depth() > max_depth:
        fails.append(f"Circuit depth {circuit.depth()} > max {max_depth}")

    # Hard gate 2: Statistical significance vs. uniform
    n = 2 ** n_qubits
    total = sum(sim_counts.values())
    expected = total / n
    all_keys = [format(i, f"0{n_qubits}b") for i in range(n)]
    observed = [sim_counts.get(k, 0) for k in all_keys]
    try:
        _, pval = chisquare(observed, f_exp=[expected] * n)
        if pval > 0.05:
            fails.append(f"Result not statistically significant (p={pval:.3f} > 0.05)")
    except Exception:
        warns.append("Could not run chi-squared test")

    # Hard gate 3: Not trivially |0⟩
    zeros = "0" * n_qubits
    if sim_counts.get(zeros, 0) / total > 0.95:
        fails.append("Result is trivially |0⟩ state (>95% probability)")

    # Hard gate 4: Not uniform
    probs = np.array(observed) / total
    ideal_uniform = np.ones(n) / n
    tvd = np.sum(np.abs(probs - ideal_uniform)) / 2
    if tvd < 0.05:
        fails.append("Result is indistinguishable from uniform distribution (TVD < 0.05)")

    passed = len(fails) == 0
    all_msgs = [f"FAIL: {f}" for f in fails] + [f"WARN: {w}" for w in warns]
    return passed, all_msgs


# ── CLI usage ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="List saved jobs")
    parser.add_argument("--poll", type=str, help="Poll a specific job ID")
    parser.add_argument("--token", type=str, default=None)
    args = parser.parse_args()

    if args.list:
        jobs = list_saved_jobs()
        for j in jobs:
            print(j)
    elif args.poll:
        token = args.token or os.environ.get("IBM_QUANTUM_TOKEN")
        if not token:
            print("No IBM token. Set IBM_QUANTUM_TOKEN.")
        else:
            from qiskit_ibm_runtime import QiskitRuntimeService
            service = QiskitRuntimeService(channel="ibm_quantum", token=token)
            poll_job(service, args.poll, timeout_sec=600)
