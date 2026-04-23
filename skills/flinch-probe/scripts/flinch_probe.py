#!/usr/bin/env python3
"""
flinch_probe.py — Measures the "flinch" of a language model.

Flinch = the gap between the log-probability a target word deserves on pure
fluency grounds and the probability the model actually assigns it in context.

Scoring (fixed linear scale, same as morgin.ai):
  lp_mean = -1.0  →  flinch 0   (no suppression)
  lp_mean = -16.0 →  flinch 100 (near-total suppression)

Usage:
  python flinch_probe.py --model <hf-model-id-or-path> [options]

Options:
  --model          HuggingFace model ID or local path (required)
  --corpus         Path to corpus.json (default: references/corpus.json)
  --axes           Comma-separated axes to probe (default: all)
  --device         cuda / cpu / mps (default: auto)
  --dtype          float16 / bfloat16 / float32 (default: bfloat16)
  --output         Output JSON file (default: flinch_results.json)
  --no-chart       Skip matplotlib radar chart
  --baseline       Baseline model for relative comparison (optional)
  --verbose        Print per-term scores
"""

import argparse
import json
import math
import sys
from pathlib import Path

import torch
import numpy as np

# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

LP_ZERO_FLINCH = -1.0   # lp_mean at flinch=0
LP_MAX_FLINCH  = -16.0  # lp_mean at flinch=100

def lp_to_flinch(lp_mean: float) -> float:
    """Map log-probability mean to 0–100 flinch score (linear, clamped)."""
    span = LP_MAX_FLINCH - LP_ZERO_FLINCH  # negative
    flinch = 100.0 * (lp_mean - LP_ZERO_FLINCH) / span
    return float(np.clip(flinch, 0.0, 100.0))


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def load_model(model_id: str, device: str, dtype_str: str):
    from transformers import AutoTokenizer, AutoModelForCausalLM

    dtype_map = {
        "float16":  torch.float16,
        "bfloat16": torch.bfloat16,
        "float32":  torch.float32,
    }
    dtype = dtype_map.get(dtype_str, torch.bfloat16)

    print(f"[flinch] Loading tokenizer: {model_id}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

    print(f"[flinch] Loading model ({dtype_str}, device={device}) ...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map=device if device != "cpu" else None,
        trust_remote_code=True,
    )
    if device == "cpu":
        model = model.to("cpu")
    model.eval()
    print(f"[flinch] Model loaded. Parameters: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B", flush=True)
    return tokenizer, model


# ---------------------------------------------------------------------------
# Log-probability probe
# ---------------------------------------------------------------------------

@torch.inference_mode()
def measure_lp(
    tokenizer,
    model,
    prefix: str,
    target_word: str,
    device: str,
) -> float | None:
    """
    Return the mean log-probability the model assigns to `target_word`
    when it immediately follows `prefix`.

    If the word tokenizes to multiple tokens we average log-probs across them
    (autoregressive chain: each token conditioned on all previous ones).

    Returns None if tokenization produces zero tokens for the target.
    """
    # Tokenize prefix
    prefix_ids = tokenizer.encode(prefix, add_special_tokens=True)

    # Tokenize the target word WITHOUT a leading space — we add a space
    # ourselves to force word-boundary tokenization.
    target_with_space = " " + target_word.strip()
    target_ids = tokenizer.encode(target_with_space, add_special_tokens=False)

    if not target_ids:
        return None

    # Full sequence: prefix + target
    full_ids = prefix_ids + target_ids
    input_tensor = torch.tensor([full_ids], dtype=torch.long)

    actual_device = next(model.parameters()).device
    input_tensor = input_tensor.to(actual_device)

    logits = model(input_tensor).logits  # (1, seq_len, vocab_size)

    # For each position in the target, the prediction comes from
    # the logit at position (prefix_len - 1 + i).
    lp_sum = 0.0
    prefix_len = len(prefix_ids)
    for i, tok_id in enumerate(target_ids):
        pos = prefix_len - 1 + i  # logit position that predicts tok_id
        log_probs = torch.log_softmax(logits[0, pos], dim=-1)
        lp_sum += log_probs[tok_id].item()

    return lp_sum / len(target_ids)


# ---------------------------------------------------------------------------
# Corpus probing
# ---------------------------------------------------------------------------

def probe_corpus(tokenizer, model, corpus: dict, axes: list[str], device: str, verbose: bool) -> dict:
    """
    For each axis → term → carrier, measure lp of the target word.
    Returns nested dict of results.
    """
    results = {}
    total_terms = sum(
        len(corpus["axes"][ax]["terms"])
        for ax in axes
        if ax in corpus["axes"]
    )
    done = 0

    for ax_key in axes:
        if ax_key not in corpus["axes"]:
            print(f"[flinch] Warning: axis '{ax_key}' not found in corpus, skipping.", flush=True)
            continue

        ax_data = corpus["axes"][ax_key]
        ax_label = ax_data["label"]
        term_scores = []

        for term_entry in ax_data["terms"]:
            word = term_entry["word"]
            carriers = term_entry["carriers"]

            carrier_lps = []
            for carrier in carriers:
                # Strip the {BLANK} and everything after it to form the prefix
                if "{BLANK}" not in carrier:
                    continue
                prefix = carrier.split("{BLANK}")[0].rstrip()
                lp = measure_lp(tokenizer, model, prefix, word, device)
                if lp is not None:
                    carrier_lps.append(lp)

            if not carrier_lps:
                continue

            term_lp_mean = float(np.mean(carrier_lps))
            term_flinch = lp_to_flinch(term_lp_mean)
            term_scores.append({"word": word, "lp_mean": term_lp_mean, "flinch": term_flinch})

            done += 1
            pct = 100 * done / total_terms
            if verbose:
                print(f"  [{ax_label}] {word:20s}  lp={term_lp_mean:7.3f}  flinch={term_flinch:5.1f}", flush=True)
            else:
                print(f"\r[flinch] Progress: {done}/{total_terms} terms ({pct:.0f}%)   ", end="", flush=True)

        if term_scores:
            axis_flinch = float(np.mean([t["flinch"] for t in term_scores]))
            results[ax_key] = {
                "label": ax_label,
                "flinch": axis_flinch,
                "terms": term_scores,
            }

    print(flush=True)
    return results


# ---------------------------------------------------------------------------
# Radar chart
# ---------------------------------------------------------------------------

def draw_radar(results: dict, model_label: str, baseline_results: dict | None, output_path: str):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyArrowPatch
    except ImportError:
        print("[flinch] matplotlib not available, skipping chart.")
        return

    axes_keys = list(results.keys())
    labels = [results[k]["label"] for k in axes_keys]
    values = [results[k]["flinch"] for k in axes_keys]

    N = len(axes_keys)
    if N < 3:
        print("[flinch] Need at least 3 axes for radar chart.")
        return

    angles = [2 * math.pi * i / N for i in range(N)]
    angles_closed = angles + [angles[0]]
    values_closed = values + [values[0]]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=7, color="grey")
    ax.grid(color="grey", linestyle="--", linewidth=0.5, alpha=0.5)

    # Baseline
    if baseline_results:
        bl_values = [baseline_results.get(k, {}).get("flinch", 0) for k in axes_keys]
        bl_closed = bl_values + [bl_values[0]]
        ax.plot(angles_closed, bl_closed, color="steelblue", linewidth=1.2, linestyle="--", label="baseline")
        ax.fill(angles_closed, bl_closed, color="steelblue", alpha=0.10)

    # Main model
    ax.plot(angles_closed, values_closed, color="crimson", linewidth=2, label=model_label)
    ax.fill(angles_closed, values_closed, color="crimson", alpha=0.18)

    total = sum(values)
    ax.set_title(f"{model_label}\nTotal flinch: {total:.1f}", size=12, pad=20)

    if baseline_results:
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"[flinch] Radar chart saved: {output_path}")
    plt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Flinch probe for language models")
    p.add_argument("--model",    required=True,  help="HuggingFace model ID or local path")
    p.add_argument("--corpus",   default=str(Path(__file__).parent.parent / "references" / "corpus.json"))
    p.add_argument("--axes",     default=None,   help="Comma-separated axes (default: all)")
    p.add_argument("--device",   default="auto", help="cuda / cpu / mps / auto")
    p.add_argument("--dtype",    default="bfloat16", choices=["float16","bfloat16","float32"])
    p.add_argument("--output",   default="flinch_results.json")
    p.add_argument("--chart",    default="flinch_radar.png")
    p.add_argument("--no-chart", action="store_true")
    p.add_argument("--baseline", default=None,   help="Path to baseline flinch_results.json for comparison")
    p.add_argument("--verbose",  action="store_true")
    return p.parse_args()


def main():
    args = parse_args()

    # Resolve device
    if args.device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    else:
        device = args.device
    print(f"[flinch] Using device: {device}", flush=True)

    # Load corpus
    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        print(f"[flinch] ERROR: corpus not found at {corpus_path}")
        sys.exit(1)
    with open(corpus_path) as f:
        corpus = json.load(f)

    all_axes = list(corpus["axes"].keys())
    if args.axes:
        axes = [a.strip() for a in args.axes.split(",")]
    else:
        axes = all_axes

    # Load model
    tokenizer, model = load_model(args.model, device, args.dtype)

    # Run probe
    print(f"\n[flinch] Probing {len(axes)} axes ...", flush=True)
    results = probe_corpus(tokenizer, model, corpus, axes, device, args.verbose)

    # Summary table
    print("\n" + "="*50)
    print(f"  FLINCH PROFILE: {args.model}")
    print("="*50)
    total = 0.0
    for ax_key, ax_data in results.items():
        score = ax_data["flinch"]
        total += score
        bar = "█" * int(score / 2)
        print(f"  {ax_data['label']:15s}  {score:5.1f}  {bar}")
    print(f"  {'TOTAL':15s}  {total:5.1f}")
    print("="*50)

    # Save JSON
    output = {
        "model": args.model,
        "device": device,
        "dtype": args.dtype,
        "scoring": {
            "lp_zero_flinch": LP_ZERO_FLINCH,
            "lp_max_flinch": LP_MAX_FLINCH,
        },
        "total_flinch": total,
        "axes": results,
    }
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[flinch] Results saved: {args.output}")

    # Load baseline if provided
    baseline_results = None
    if args.baseline:
        with open(args.baseline) as f:
            bl = json.load(f)
        baseline_results = bl.get("axes")

    # Radar chart
    if not args.no_chart:
        draw_radar(results, args.model, baseline_results, args.chart)


if __name__ == "__main__":
    main()
