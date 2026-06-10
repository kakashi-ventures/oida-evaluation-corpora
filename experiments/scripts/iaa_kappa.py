#!/usr/bin/env python3
"""T2 — inter-annotator agreement for the D2 gold gate (GATE 2).

Computes raw agreement + weighted Cohen's kappa (ordinal 0-3) between two graded
qrels label sets over the rows they share: the draft gold and the independent
blind second label set. Stdlib only (eval-repo convention).

The weighting is DECLARED HERE and must be fixed before the blind set is scored
(pre-registration discipline): quadratic disagreement weights w_ij = (i-j)^2 are
the headline; linear |i-j| is reported alongside. Ordinal categories 0..3 =
superseded/trap, historical, stable-support, current-answer.

Usage:
  python experiments/scripts/iaa_kappa.py <draft_qrels.tsv> <blind_qrels.tsv>
  # each TSV: `query-id<TAB>corpus-id<TAB>score`, optional header row.
Agreement is computed ONLY over (query-id, corpus-id) pairs present in BOTH files;
pairs missing from one side are listed (coverage gaps must be resolved before the
agreement number is trusted).
"""
import sys
from pathlib import Path

K = 4  # ordinal categories 0..3


def load(path: Path) -> dict[tuple[str, str], int]:
    out: dict[tuple[str, str], int] = {}
    for ln in path.read_text(encoding="utf-8").splitlines():
        p = ln.rstrip("\n").split("\t")
        if len(p) < 3 or p[0].strip() in ("query-id", "qid", ""):
            continue
        try:
            out[(p[0].strip(), p[1].strip())] = int(float(p[2].strip()))
        except ValueError:
            continue
    return out


def kappa(pairs_a: list[int], pairs_b: list[int], weight: str) -> float:
    n = len(pairs_a)
    if n == 0:
        return float("nan")
    obs = [[0] * K for _ in range(K)]
    for a, b in zip(pairs_a, pairs_b):
        obs[a][b] += 1
    row = [sum(obs[i]) for i in range(K)]
    col = [sum(obs[i][j] for i in range(K)) for j in range(K)]

    def w(i: int, j: int) -> float:
        if weight == "quadratic":
            return ((i - j) ** 2) / ((K - 1) ** 2)
        if weight == "linear":
            return abs(i - j) / (K - 1)
        return 0.0 if i == j else 1.0  # unweighted

    num = sum(w(i, j) * obs[i][j] for i in range(K) for j in range(K))
    den = sum(w(i, j) * (row[i] * col[j] / n) for i in range(K) for j in range(K))
    if den == 0:
        return 1.0  # no expected disagreement → perfect by convention
    return 1.0 - num / den


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    a = load(Path(sys.argv[1]))
    b = load(Path(sys.argv[2]))
    shared = sorted(set(a) & set(b))
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    if not shared:
        print("ERROR: no shared (query-id, corpus-id) pairs between the two files.")
        return 1

    la = [a[k] for k in shared]
    lb = [b[k] for k in shared]
    n = len(shared)
    raw = sum(1 for x, y in zip(la, lb) if x == y) / n

    print(f"shared pairs        : {n}")
    print(f"coverage gaps       : draft-only={len(only_a)}  blind-only={len(only_b)}"
          + ("  <-- resolve before trusting the number" if (only_a or only_b) else ""))
    print(f"raw agreement       : {raw:.4f}  ({sum(1 for x,y in zip(la,lb) if x==y)}/{n})")
    print(f"Cohen's kappa (unwt): {kappa(la, lb, 'unweighted'):.4f}")
    print(f"weighted kappa (lin): {kappa(la, lb, 'linear'):.4f}")
    print(f"weighted kappa (quad): {kappa(la, lb, 'quadratic'):.4f}   <-- HEADLINE (declared a priori)")
    print()
    print("confusion matrix (rows=draft 0..3, cols=blind 0..3):")
    obs = [[0] * K for _ in range(K)]
    for x, y in zip(la, lb):
        obs[x][y] += 1
    print("        b=0   b=1   b=2   b=3")
    for i in range(K):
        print(f"  a={i} " + " ".join(f"{obs[i][j]:5d}" for j in range(K)))
    print()
    print("disagreements (|draft-blind| >= 2 — the reconciliation agenda):")
    big = [(k, a[k], b[k]) for k in shared if abs(a[k] - b[k]) >= 2]
    for k, x, y in big[:200]:
        print(f"  {k[0]:>8}  {k[1]:<48}  draft={x}  blind={y}")
    print(f"  ({len(big)} pairs with |delta| >= 2)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
