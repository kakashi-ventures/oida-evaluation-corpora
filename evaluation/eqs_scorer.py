"""
Epistemic Quality Score (EQS) — composite evaluation metric.

Implements the five sub-scores from Section 4.1 of the paper:
  EQS = 0.20·ECA + 0.25·CP + 0.20·CR + 0.20·EC + 0.15·DE

Usage:
  python eqs_scorer.py --responses responses.json --output results.csv
"""

import argparse
import json
import sys

import numpy as np
import pandas as pd
from scipy import stats

# Sub-score weights (Table 5)
WEIGHTS = {
    "ECA": 0.20,  # Epistemic Classification Accuracy
    "CP": 0.25,   # Contextual Precision
    "CR": 0.20,   # Contextual Recall
    "EC": 0.20,   # Epistemic Coherence
    "DE": 0.15,   # Decision Enablement
}


def compute_eqs(subscores: dict[str, float]) -> float:
    """Compute composite EQS from sub-scores."""
    return sum(WEIGHTS[k] * subscores[k] for k in WEIGHTS)


def paired_wilcoxon(condition_a: list[float], condition_b: list[float]):
    """One-sided Wilcoxon signed-rank test (B > A)."""
    stat, p_two = stats.wilcoxon(condition_a, condition_b, alternative="less")
    return {"W": stat, "p": p_two, "n": len(condition_a)}


def cohens_d(a: list[float], b: list[float]) -> float:
    """Cohen's d effect size for paired samples."""
    diff = np.array(b) - np.array(a)
    return float(np.mean(diff) / np.std(diff, ddof=1)) if np.std(diff, ddof=1) > 0 else float("inf")


def main():
    parser = argparse.ArgumentParser(description="Compute EQS scores")
    parser.add_argument("--responses", required=True, help="JSON file with scored response pairs")
    parser.add_argument("--output", default="results.csv", help="Output CSV path")
    args = parser.parse_args()

    with open(args.responses) as f:
        data = json.load(f)

    rows = []
    for pair in data:
        for condition in ("brook", "cowork"):
            s = pair[condition]
            eqs = compute_eqs(s)
            rows.append({
                "pair_id": pair["id"],
                "condition": condition,
                "ECA": s["ECA"],
                "CP": s["CP"],
                "CR": s["CR"],
                "EC": s["EC"],
                "DE": s["DE"],
                "EQS": eqs,
            })

    df = pd.DataFrame(rows)
    df.to_csv(args.output, index=False)

    # Summary statistics
    for cond in ("brook", "cowork"):
        subset = df[df["condition"] == cond]
        print(f"\n{cond.upper()} (n={len(subset)})")
        for col in ["ECA", "CP", "CR", "EC", "DE", "EQS"]:
            print(f"  {col}: {subset[col].mean():.3f} +/- {subset[col].std():.3f}")

    # Paired test on composite EQS
    brook_eqs = df[df["condition"] == "brook"]["EQS"].values
    cowork_eqs = df[df["condition"] == "cowork"]["EQS"].values
    result = paired_wilcoxon(brook_eqs, cowork_eqs)
    d = cohens_d(brook_eqs, cowork_eqs)
    print(f"\nWilcoxon signed-rank: W={result['W']:.1f}, p={result['p']:.6f}")
    print(f"Cohen's d: {d:.3f}")


if __name__ == "__main__":
    main()
