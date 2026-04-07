"""
QUESTION declaration rate analysis.

Computes the Fisher's exact test and Haldane-Anscombe odds ratio
for the QUESTION mechanism evaluation (Section 4.2, Table 4).

Usage:
  python question_analysis.py --brook brook.json --baseline baseline.json
"""

import argparse
import json

import numpy as np
from scipy import stats


def haldane_anscombe_or(table: list[list[int]]) -> float:
    """Odds ratio with Haldane-Anscombe correction for zero cells."""
    a, b = table[0]
    c, d = table[1]
    return ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5))


def main():
    parser = argparse.ArgumentParser(description="QUESTION declaration analysis")
    parser.add_argument("--brook", required=True, help="Brook responses JSON")
    parser.add_argument("--baseline", required=True, help="Baseline responses JSON")
    args = parser.parse_args()

    with open(args.brook) as f:
        brook = json.load(f)
    with open(args.baseline) as f:
        baseline = json.load(f)

    brook_decl = sum(1 for r in brook if r["has_ignorance_declaration"])
    brook_no = len(brook) - brook_decl
    base_decl = sum(1 for r in baseline if r["has_ignorance_declaration"])
    base_no = len(baseline) - base_decl

    table = [[brook_decl, brook_no], [base_decl, base_no]]

    print("Contingency table:")
    print(f"  Brook:    {brook_decl} declared, {brook_no} not declared")
    print(f"  Baseline: {base_decl} declared, {base_no} not declared")

    odds_ratio, p_fisher = stats.fisher_exact(table, alternative="two-sided")
    or_ha = haldane_anscombe_or(table)

    print(f"\nFisher's exact test (two-sided): p = {p_fisher:.4f}")
    print(f"Odds ratio (Fisher): {odds_ratio:.1f}")
    print(f"Odds ratio (Haldane-Anscombe): {or_ha:.1f}")

    if p_fisher < 0.05:
        print("\nResult: Statistically significant difference (p < 0.05)")
    else:
        print("\nResult: No significant difference at alpha = 0.05")


if __name__ == "__main__":
    main()
