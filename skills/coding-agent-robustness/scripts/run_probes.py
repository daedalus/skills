#!/usr/bin/env python3
"""
run_probes.py — Batch probe runner for coding agent robustness evaluation.

Usage:
    python run_probes.py --probes probes.json --agent-cmd "python my_agent.py" --output results/
    python run_probes.py --probes probes.json --agent-url http://localhost:8080/v1/chat --output results/

probes.json schema:
{
  "dimensions": ["adversarial_correctness", "hallucination", ...],
  "probes": [
    {
      "id": "AC-01",
      "dimension": "adversarial_correctness",
      "prompt": "...",
      "test_script": "tests/ac01_test.py",   // optional: run output in sandbox
      "ground_truth": "should_pass|should_refuse|manual"
    }
  ]
}
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


SANDBOX_DOCKER_IMAGE = "python:3.12-slim"
SANDBOX_TIMEOUT = 10  # seconds


def run_agent_cmd(cmd: str, prompt: str) -> str:
    """Submit prompt to agent via CLI command. Agent reads from stdin, writes to stdout."""
    result = subprocess.run(
        cmd,
        shell=True,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Agent exited {result.returncode}: {result.stderr[:500]}")
    return result.stdout.strip()


def run_agent_api(url: str, prompt: str, api_key: str = "") -> str:
    """Submit prompt to OpenAI-compatible chat endpoint."""
    import urllib.request
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
    }).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"].strip()


def extract_code_block(text: str) -> str:
    """Extract first fenced code block from markdown response."""
    lines = text.split("\n")
    in_block = False
    code_lines = []
    for line in lines:
        if line.startswith("```") and not in_block:
            in_block = True
            continue
        if line.startswith("```") and in_block:
            break
        if in_block:
            code_lines.append(line)
    return "\n".join(code_lines) if code_lines else text


def run_in_sandbox(code: str, test_script_path: str | None) -> dict:
    """
    Run agent-generated code in a Docker sandbox.
    Returns {"returncode": int, "stdout": str, "stderr": str, "timed_out": bool}
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        agent_file = os.path.join(tmpdir, "agent_code.py")
        with open(agent_file, "w") as f:
            f.write(code)

        if test_script_path:
            test_dest = os.path.join(tmpdir, "test_script.py")
            with open(test_script_path) as src, open(test_dest, "w") as dst:
                dst.write(src.read())
            run_cmd = ["python", "-m", "pytest", "test_script.py", "-x", "-q"]
        else:
            run_cmd = ["python", "agent_code.py"]

        docker_cmd = [
            "docker", "run", "--rm",
            "--network=none",
            "--memory=256m",
            "--cpus=0.5",
            f"--volume={tmpdir}:/workspace:ro",
            "--workdir=/workspace",
            SANDBOX_DOCKER_IMAGE,
        ] + run_cmd

        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=SANDBOX_TIMEOUT,
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:2000],
                "timed_out": False,
            }
        except subprocess.TimeoutExpired:
            return {"returncode": -1, "stdout": "", "stderr": "TIMEOUT", "timed_out": True}
        except FileNotFoundError:
            # Docker not available — fall back to subprocess (UNSAFE, dev only)
            print("[WARNING] Docker not found. Running code unsandboxed. DO NOT USE IN PRODUCTION.", file=sys.stderr)
            try:
                result = subprocess.run(
                    ["python", agent_file],
                    capture_output=True,
                    text=True,
                    timeout=SANDBOX_TIMEOUT,
                )
                return {
                    "returncode": result.returncode,
                    "stdout": result.stdout[:2000],
                    "stderr": result.stderr[:2000],
                    "timed_out": False,
                }
            except subprocess.TimeoutExpired:
                return {"returncode": -1, "stdout": "", "stderr": "TIMEOUT", "timed_out": True}


def process_probe(probe: dict, agent_fn, output_dir: Path, run_sandbox: bool) -> dict:
    probe_id = probe["id"]
    dimension = probe["dimension"]
    prompt = probe["prompt"]
    ground_truth = probe.get("ground_truth", "manual")
    test_script = probe.get("test_script")

    print(f"  [{probe_id}] {dimension} ... ", end="", flush=True)
    t0 = time.time()

    result = {
        "probe_id": probe_id,
        "dimension": dimension,
        "prompt": prompt,
        "ground_truth": ground_truth,
        "raw_output": None,
        "extracted_code": None,
        "sandbox": None,
        "duration_s": None,
        "error": None,
    }

    try:
        raw = agent_fn(prompt)
        result["raw_output"] = raw
        code = extract_code_block(raw)
        result["extracted_code"] = code

        if run_sandbox and (dimension in ("adversarial_correctness", "hallucination", "error_recovery")):
            sandbox_result = run_in_sandbox(code, test_script)
            result["sandbox"] = sandbox_result
            status = "PASS" if sandbox_result["returncode"] == 0 else ("TIMEOUT" if sandbox_result["timed_out"] else "FAIL")
            print(status, end="")
        else:
            print("OK (manual grade)", end="")

    except Exception as e:
        result["error"] = str(e)
        print(f"ERROR: {e}", end="")

    result["duration_s"] = round(time.time() - t0, 2)
    print(f" ({result['duration_s']}s)")

    # Save individual result
    out_file = output_dir / f"{probe_id}.json"
    with open(out_file, "w") as f:
        json.dump(result, f, indent=2)

    return result


def main():
    parser = argparse.ArgumentParser(description="Batch coding agent robustness probe runner")
    parser.add_argument("--probes", required=True, help="Path to probes.json")
    parser.add_argument("--agent-cmd", help="Shell command. Agent reads prompt from stdin.")
    parser.add_argument("--agent-url", help="OpenAI-compatible chat completion endpoint URL")
    parser.add_argument("--api-key", default="", help="API key for --agent-url")
    parser.add_argument("--output", required=True, help="Output directory for results")
    parser.add_argument("--dimensions", nargs="*", help="Only run these dimensions")
    parser.add_argument("--no-sandbox", action="store_true", help="Skip Docker sandbox execution")
    args = parser.parse_args()

    if not args.agent_cmd and not args.agent_url:
        parser.error("Must provide --agent-cmd or --agent-url")

    with open(args.probes) as f:
        config = json.load(f)

    probes = config["probes"]
    if args.dimensions:
        probes = [p for p in probes if p["dimension"] in args.dimensions]

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.agent_cmd:
        def agent_fn(prompt):
            return run_agent_cmd(args.agent_cmd, prompt)
    else:
        def agent_fn(prompt):
            return run_agent_api(args.agent_url, prompt, args.api_key)

    print(f"Running {len(probes)} probes → {output_dir}")
    all_results = []
    for probe in probes:
        r = process_probe(probe, agent_fn, output_dir, run_sandbox=not args.no_sandbox)
        all_results.append(r)

    summary_path = output_dir / "results.json"
    with open(summary_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nAll results saved to {summary_path}")
    print("Run score.py on this file to compute dimension scores.")


if __name__ == "__main__":
    main()
