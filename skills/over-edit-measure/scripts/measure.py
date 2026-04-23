#!/usr/bin/env python3
"""
Over-edit measurement script.
Computes token-level Levenshtein distance and Cognitive Complexity delta
between original and modified Python code, optionally against a ground-truth
minimal fix.

Usage:
    python measure.py --original original.py --modified modified.py [--ground-truth gt.py]
    python measure.py --batch batch.json
    python measure.py --original orig.py --modified mod.py --format json
"""

import argparse
import ast
import json
import sys
import tokenize
import io
from pathlib import Path
from typing import Optional

try:
    from cognitive_complexity.api import get_cognitive_complexity
except ImportError:
    print("ERROR: cognitive-complexity not installed. Run: pip install cognitive-complexity --break-system-packages", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Token-level Levenshtein
# ---------------------------------------------------------------------------

def tokenize_code(code: str) -> list[str]:
    """Tokenize Python source, stripping whitespace/comment/encoding tokens."""
    tokens = []
    skip = {tokenize.NEWLINE, tokenize.NL, tokenize.COMMENT,
            tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            if tok.type not in skip:
                tokens.append(tok.string)
    except tokenize.TokenError:
        # Fallback: split on whitespace
        tokens = code.split()
    return tokens


def levenshtein(a: list, b: list) -> int:
    """Standard DP Levenshtein on arbitrary sequences."""
    m, n = len(a), len(b)
    if m == 0: return n
    if n == 0: return m
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            if a[i-1] == b[j-1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j-1])
            prev = temp
    return dp[n]


def normalized_levenshtein(original: str, modified: str) -> float:
    """Token-level Levenshtein normalized by total token count of both sequences."""
    tok_orig = tokenize_code(original)
    tok_mod  = tokenize_code(modified)
    dist = levenshtein(tok_orig, tok_mod)
    total = len(tok_orig) + len(tok_mod)
    return dist / total if total else 0.0


# ---------------------------------------------------------------------------
# Cognitive Complexity per function
# ---------------------------------------------------------------------------

def get_function_cc(code: str) -> dict[str, int]:
    """Return {function_name: cognitive_complexity} for all top-level functions."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}
    result = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            try:
                result[node.name] = get_cognitive_complexity(node)
            except Exception:
                result[node.name] = 0
    return result


def cc_delta(original: str, modified: str) -> dict:
    """
    Compare Cognitive Complexity per function.
    Returns per-function deltas and aggregate stats.
    """
    orig_cc = get_function_cc(original)
    mod_cc  = get_function_cc(modified)

    all_funcs = set(orig_cc) | set(mod_cc)
    per_func = {}
    for fn in sorted(all_funcs):
        o = orig_cc.get(fn, 0)
        m = mod_cc.get(fn, 0)
        per_func[fn] = {"original": o, "modified": m, "delta": m - o}

    added   = sum(v["delta"] for v in per_func.values() if v["delta"] > 0)
    removed = sum(v["delta"] for v in per_func.values() if v["delta"] < 0)
    net     = sum(v["delta"] for v in per_func.values())

    return {
        "per_function": per_func,
        "added_cc": added,
        "removed_cc": removed,
        "net_cc_delta": net,
    }


# ---------------------------------------------------------------------------
# Patch score (when ground truth is available)
# ---------------------------------------------------------------------------

def patch_score(original: str, modified: str, ground_truth: str) -> dict:
    """
    S(M) = D_model - D_true
    D_true  = levenshtein(ground_truth, original)   -- minimal fix distance
    D_model = levenshtein(modified, original)        -- model's edit distance
    Closer to 0 is better; positive means over-editing.
    """
    d_true  = normalized_levenshtein(original, ground_truth)
    d_model = normalized_levenshtein(original, modified)
    score   = d_model - d_true
    return {
        "d_true": round(d_true, 4),
        "d_model": round(d_model, 4),
        "patch_score": round(score, 4),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

VERDICT_THRESHOLDS = {
    "minimal":    (0.00, 0.05),
    "slight":     (0.05, 0.15),
    "moderate":   (0.15, 0.30),
    "excessive":  (0.30, float("inf")),
}

def verdict(norm_lev: float) -> str:
    for label, (lo, hi) in VERDICT_THRESHOLDS.items():
        if lo <= norm_lev < hi:
            return label
    return "excessive"


# ---------------------------------------------------------------------------
# Single-pair measurement
# ---------------------------------------------------------------------------

def measure_pair(
    original: str,
    modified: str,
    ground_truth: Optional[str] = None,
    name: str = "unnamed",
) -> dict:
    norm_lev = normalized_levenshtein(original, modified)
    cc       = cc_delta(original, modified)

    result = {
        "name": name,
        "normalized_levenshtein": round(norm_lev, 4),
        "verdict": verdict(norm_lev),
        "cognitive_complexity": cc,
    }

    if ground_truth is not None:
        result["patch_score"] = patch_score(original, modified, ground_truth)

    return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

VERDICT_EMOJI = {
    "minimal":   "✅",
    "slight":    "🟡",
    "moderate":  "🟠",
    "excessive": "🔴",
}

def format_report(results: list[dict]) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("  OVER-EDIT MEASUREMENT REPORT")
    lines.append("=" * 60)

    for r in results:
        emoji = VERDICT_EMOJI.get(r["verdict"], "❓")
        lines.append(f"\n📄 {r['name']}")
        lines.append(f"   Verdict:               {emoji} {r['verdict'].upper()}")
        lines.append(f"   Norm. Levenshtein:     {r['normalized_levenshtein']:.4f}  (0=no change, higher=more rewriting)")

        cc = r["cognitive_complexity"]
        lines.append(f"   Added CC:              {cc['added_cc']:+d}")
        lines.append(f"   Net CC delta:          {cc['net_cc_delta']:+d}")

        if cc["per_function"]:
            lines.append("   Per-function breakdown:")
            for fn, vals in cc["per_function"].items():
                d = vals["delta"]
                arrow = "→" if d == 0 else ("↑" if d > 0 else "↓")
                lines.append(f"     {fn}():  CC {vals['original']} {arrow} {vals['modified']}  (Δ{d:+d})")

        if "patch_score" in r:
            ps = r["patch_score"]
            lines.append(f"   Ground-truth comparison:")
            lines.append(f"     D_true (minimal fix):  {ps['d_true']:.4f}")
            lines.append(f"     D_model (this patch):  {ps['d_model']:.4f}")
            lines.append(f"     Patch score (S):       {ps['patch_score']:+.4f}  (0=perfect, positive=over-edit)")

    # Summary if batch
    if len(results) > 1:
        lines.append("\n" + "=" * 60)
        lines.append("  BATCH SUMMARY")
        lines.append("=" * 60)
        avg_lev = sum(r["normalized_levenshtein"] for r in results) / len(results)
        avg_cc  = sum(r["cognitive_complexity"]["added_cc"] for r in results) / len(results)
        counts  = {}
        for r in results:
            counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
        lines.append(f"   Samples:               {len(results)}")
        lines.append(f"   Avg Norm. Levenshtein: {avg_lev:.4f}")
        lines.append(f"   Avg Added CC:          {avg_cc:.2f}")
        lines.append("   Verdict distribution:")
        for v in ["minimal", "slight", "moderate", "excessive"]:
            if v in counts:
                emoji = VERDICT_EMOJI[v]
                lines.append(f"     {emoji} {v}: {counts[v]}")
        if any("patch_score" in r for r in results):
            ps_vals = [r["patch_score"]["patch_score"] for r in results if "patch_score" in r]
            lines.append(f"   Avg patch score S:     {sum(ps_vals)/len(ps_vals):+.4f}")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Measure over-editing in Python code diffs.")
    parser.add_argument("--original",     help="Path to original Python file")
    parser.add_argument("--modified",     help="Path to model-modified Python file")
    parser.add_argument("--ground-truth", help="Path to ground-truth minimal fix (optional)")
    parser.add_argument("--batch",        help="Path to JSON batch file")
    parser.add_argument("--format",       choices=["text", "json"], default="text")
    parser.add_argument("--output",       help="Write results to this file instead of stdout")
    args = parser.parse_args()

    results = []

    if args.batch:
        batch = json.loads(Path(args.batch).read_text())
        for item in batch:
            orig = Path(item["original"]).read_text()
            mod  = Path(item["modified"]).read_text()
            gt   = Path(item["ground_truth"]).read_text() if item.get("ground_truth") else None
            name = item.get("name", Path(item["original"]).stem)
            results.append(measure_pair(orig, mod, gt, name))

    elif args.original and args.modified:
        orig = Path(args.original).read_text()
        mod  = Path(args.modified).read_text()
        gt   = Path(args.ground_truth).read_text() if args.ground_truth else None
        name = Path(args.original).stem
        results.append(measure_pair(orig, mod, gt, name))

    else:
        # Read from stdin as JSON: {"original": "...", "modified": "...", "ground_truth": "..."}
        data = json.load(sys.stdin)
        if isinstance(data, list):
            for item in data:
                results.append(measure_pair(
                    item["original"], item["modified"],
                    item.get("ground_truth"), item.get("name", "sample")
                ))
        else:
            results.append(measure_pair(
                data["original"], data["modified"],
                data.get("ground_truth"), data.get("name", "sample")
            ))

    if args.format == "json":
        out = json.dumps(results, indent=2)
    else:
        out = format_report(results)

    if args.output:
        Path(args.output).write_text(out)
        print(f"Results written to {args.output}")
    else:
        print(out)


if __name__ == "__main__":
    main()
