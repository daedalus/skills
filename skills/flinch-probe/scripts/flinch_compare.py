#!/usr/bin/env python3
"""
flinch_compare.py — Overlay radar chart for multiple flinch result files.

Usage:
  python flinch_compare.py results1.json results2.json [results3.json ...] \
         [--output overlay.png] [--table]

Prints a comparison table and saves a radar overlay PNG.
"""

import argparse
import json
import math
import sys
from pathlib import Path


COLORS = ["crimson", "steelblue", "seagreen", "darkorange", "mediumpurple", "saddlebrown"]


def load_result(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def draw_overlay(all_results: list[dict], output: str):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[compare] matplotlib not available.")
        return

    # Collect common axes across all results
    axes_keys = list(all_results[0]["axes"].keys())

    N = len(axes_keys)
    if N < 3:
        print("[compare] Need at least 3 axes.")
        return

    labels = [all_results[0]["axes"][k]["label"] for k in axes_keys]
    angles = [2 * math.pi * i / N for i in range(N)]
    angles_closed = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=7, color="grey")
    ax.grid(color="grey", linestyle="--", linewidth=0.5, alpha=0.5)

    for i, result in enumerate(all_results):
        color = COLORS[i % len(COLORS)]
        label = result["model"].split("/")[-1]  # short name
        total = result.get("total_flinch", 0)
        values = [result["axes"].get(k, {}).get("flinch", 0) for k in axes_keys]
        values_closed = values + [values[0]]
        ax.plot(angles_closed, values_closed, color=color, linewidth=2,
                label=f"{label} ({total:.0f})")
        ax.fill(angles_closed, values_closed, color=color, alpha=0.08)

    ax.legend(loc="upper right", bbox_to_anchor=(1.4, 1.15), fontsize=9)
    ax.set_title("Flinch Overlay", size=13, pad=20)
    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches="tight")
    print(f"[compare] Overlay saved: {output}")
    plt.close()


def print_table(all_results: list[dict]):
    axes_keys = list(all_results[0]["axes"].keys())
    models = [r["model"].split("/")[-1] for r in all_results]

    col_w = max(16, max(len(m) for m in models) + 2)
    ax_w  = 16

    header = f"{'Axis':>{ax_w}}" + "".join(f"  {m:>{col_w}}" for m in models)
    print("\n" + "="*(ax_w + (col_w + 2) * len(models)))
    print(header)
    print("="*(ax_w + (col_w + 2) * len(models)))

    for ax_key in axes_keys:
        label = all_results[0]["axes"][ax_key]["label"]
        row = f"{label:>{ax_w}}"
        for result in all_results:
            score = result["axes"].get(ax_key, {}).get("flinch", float("nan"))
            row += f"  {score:>{col_w}.1f}"
        print(row)

    print("-"*(ax_w + (col_w + 2) * len(models)))
    totals_row = f"{'TOTAL':>{ax_w}}"
    for result in all_results:
        totals_row += f"  {result.get('total_flinch', 0):>{col_w}.1f}"
    print(totals_row)
    print("="*(ax_w + (col_w + 2) * len(models)))


def main():
    p = argparse.ArgumentParser(description="Compare flinch results")
    p.add_argument("results", nargs="+", help="flinch_results.json files")
    p.add_argument("--output", default="flinch_overlay.png")
    p.add_argument("--no-chart", action="store_true")
    args = p.parse_args()

    all_results = [load_result(r) for r in args.results]
    print_table(all_results)

    if not args.no_chart:
        draw_overlay(all_results, args.output)


if __name__ == "__main__":
    main()
