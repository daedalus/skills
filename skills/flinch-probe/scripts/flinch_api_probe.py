#!/usr/bin/env python3
"""
flinch_api_probe.py — Flinch probe for API-accessible models (no local weights).

Uses log-probabilities from API completions to estimate token suppression.
Works with OpenAI-compatible APIs that return logprobs.

Supported:
  - OpenAI API (gpt-4o, gpt-3.5-turbo, etc.) — requires logprobs=True
  - Together AI, Perplexity, Fireworks, etc. (OpenAI-compat)
  - Anthropic Claude — approximation via top_k sampling (see note below)

Note on Anthropic models: Claude's API does not expose raw logprobs.
This script estimates flinch by sampling N completions and measuring
how often the target word appears in the first token. This is a rougher
proxy but directionally valid for large flinch gaps.

Usage:
  # OpenAI-compatible (returns logprobs):
  python flinch_api_probe.py \
    --provider openai \
    --model gpt-4o-mini \
    --api-key $OPENAI_API_KEY \
    --corpus references/corpus.json

  # Anthropic (sampling approximation):
  python flinch_api_probe.py \
    --provider anthropic \
    --model claude-sonnet-4-20250514 \
    --api-key $ANTHROPIC_API_KEY \
    --corpus references/corpus.json \
    --samples 50
"""

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np


LP_ZERO_FLINCH = -1.0
LP_MAX_FLINCH  = -16.0

def lp_to_flinch(lp_mean: float) -> float:
    span = LP_MAX_FLINCH - LP_ZERO_FLINCH
    flinch = 100.0 * (lp_mean - LP_ZERO_FLINCH) / span
    return float(np.clip(flinch, 0.0, 100.0))


# ---------------------------------------------------------------------------
# OpenAI-compatible probe
# ---------------------------------------------------------------------------

def probe_openai(client, model: str, prefix: str, target_word: str) -> float | None:
    """
    Use OpenAI logprobs endpoint to get log-probability of target_word
    as the next token after prefix.
    """
    try:
        response = client.completions.create(
            model=model,
            prompt=prefix + " ",
            max_tokens=1,
            logprobs=5,
            temperature=0,
        )
        # Look for target word in top logprobs
        top_logprobs = response.choices[0].logprobs.top_logprobs[0]
        # Try exact match and with leading space
        for variant in [target_word, " " + target_word, target_word.lower(), " " + target_word.lower()]:
            if variant in top_logprobs:
                return top_logprobs[variant]
        # Target not in top-5: use the minimum as a lower bound
        min_lp = min(top_logprobs.values())
        # Return something below min_lp as a conservative estimate
        return min_lp - 2.0
    except Exception as e:
        print(f"  [api] Error: {e}", flush=True)
        return None


# ---------------------------------------------------------------------------
# Anthropic sampling probe
# ---------------------------------------------------------------------------

def probe_anthropic_sampling(client, model: str, prefix: str, target_word: str, n_samples: int) -> float:
    """
    Estimate log-probability by sampling N completions.
    Returns log(hit_rate) where hit_rate = fraction of samples starting with target_word.
    This is a rough proxy — use only for directional comparison.
    """
    hits = 0
    for _ in range(n_samples):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=5,
                temperature=1.0,
                messages=[{"role": "user", "content": prefix + "\n\nComplete the sentence with the next word only."}],
            )
            completion = resp.content[0].text.strip().lower().split()[0] if resp.content else ""
            if target_word.lower() in completion:
                hits += 1
        except Exception:
            pass
        time.sleep(0.1)

    rate = max(hits, 0.5) / n_samples  # smooth to avoid log(0)
    return math.log(rate)


# ---------------------------------------------------------------------------
# Core probing loop (provider-agnostic)
# ---------------------------------------------------------------------------

def probe_corpus_api(
    corpus: dict,
    axes: list[str],
    measure_fn,
    verbose: bool,
) -> dict:
    results = {}
    total_terms = sum(
        len(corpus["axes"][ax]["terms"]) for ax in axes if ax in corpus["axes"]
    )
    done = 0

    for ax_key in axes:
        if ax_key not in corpus["axes"]:
            continue
        ax_data = corpus["axes"][ax_key]
        ax_label = ax_data["label"]
        term_scores = []

        for term_entry in ax_data["terms"]:
            word = term_entry["word"]
            carriers = term_entry["carriers"]
            carrier_lps = []

            for carrier in carriers:
                if "{BLANK}" not in carrier:
                    continue
                prefix = carrier.split("{BLANK}")[0].rstrip()
                lp = measure_fn(prefix, word)
                if lp is not None:
                    carrier_lps.append(lp)
                time.sleep(0.05)  # gentle rate limit

            if not carrier_lps:
                done += 1
                continue

            term_lp = float(np.mean(carrier_lps))
            term_flinch = lp_to_flinch(term_lp)
            term_scores.append({"word": word, "lp_mean": term_lp, "flinch": term_flinch})
            done += 1

            if verbose:
                print(f"  [{ax_label}] {word:20s}  lp={term_lp:7.3f}  flinch={term_flinch:5.1f}", flush=True)
            else:
                print(f"\r[flinch-api] {done}/{total_terms} terms ({100*done//total_terms}%)   ", end="", flush=True)

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
# Main
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--provider", required=True, choices=["openai", "anthropic", "openai-compat"])
    p.add_argument("--model", required=True)
    p.add_argument("--api-key", required=True)
    p.add_argument("--api-base", default=None, help="For openai-compat providers")
    p.add_argument("--corpus", default=str(Path(__file__).parent.parent / "references" / "corpus.json"))
    p.add_argument("--axes", default=None)
    p.add_argument("--output", default="flinch_results.json")
    p.add_argument("--samples", type=int, default=30, help="Samples for Anthropic approximation")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    with open(args.corpus) as f:
        corpus = json.load(f)

    all_axes = list(corpus["axes"].keys())
    axes = [a.strip() for a in args.axes.split(",")] if args.axes else all_axes

    if args.provider in ("openai", "openai-compat"):
        from openai import OpenAI
        client = OpenAI(
            api_key=args.api_key,
            base_url=args.api_base,
        )
        measure_fn = lambda prefix, word: probe_openai(client, args.model, prefix, word)

    elif args.provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=args.api_key)
        print(f"[flinch-api] Using Anthropic sampling proxy ({args.samples} samples per carrier).")
        print("[flinch-api] WARNING: This is an approximation — not equivalent to logprob probe.")
        measure_fn = lambda prefix, word: probe_anthropic_sampling(client, args.model, prefix, word, args.samples)

    print(f"\n[flinch-api] Probing {len(axes)} axes on {args.model} via {args.provider} ...", flush=True)
    results = probe_corpus_api(corpus, axes, measure_fn, args.verbose)

    total = sum(r["flinch"] for r in results.values())
    print("\n" + "="*50)
    print(f"  FLINCH PROFILE: {args.model}")
    print("="*50)
    for ax_key, ax_data in results.items():
        score = ax_data["flinch"]
        bar = "█" * int(score / 2)
        print(f"  {ax_data['label']:15s}  {score:5.1f}  {bar}")
    print(f"  {'TOTAL':15s}  {total:5.1f}")
    print("="*50)

    output = {
        "model": args.model,
        "provider": args.provider,
        "note": "Anthropic values are sampling approximation" if args.provider == "anthropic" else "",
        "scoring": {"lp_zero_flinch": LP_ZERO_FLINCH, "lp_max_flinch": LP_MAX_FLINCH},
        "total_flinch": total,
        "axes": results,
    }
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[flinch-api] Results saved: {args.output}")


if __name__ == "__main__":
    main()
