#!/usr/bin/env python3
"""Layer 2 — adversarial retrieval scoring (EXPERIMENT_PLAN.md §5.2).

Three metrics, each written into ``layer_2_adversarial`` of every matching
``corpora/<id>/results/<system>_<run_id>.json``:

  - contradiction_recall_at_10  (needs annotations/contra_sets/<corpus>.json)
  - mean_rank_binding / superseded_above_rate
                                (needs annotations/supersession_chains/<corpus>.json)
  - trap_in_top_5               (from qrels score==0 rows — no annotation needed)

Metrics whose annotation file is absent are written as ``null`` (not 0) with the
matching count left at 0, so a partially-annotated corpus still scores its
trap-rejection axis.

Usage:
    python experiments/scripts/04_eval_adversarial.py                 # all systems, all corpora
    python experiments/scripts/04_eval_adversarial.py --system oida-core
    python experiments/scripts/04_eval_adversarial.py org-iot-fireglass
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import eval_common as ec  # noqa: E402

K_CONTRA = 10
K_TRAP = 5


def _rank_of(ranked: list[str], doc: str) -> int | None:
    """1-indexed rank of doc in ranked list, or None if absent."""
    try:
        return ranked.index(doc) + 1
    except ValueError:
        return None


def score_contradiction(runs, contra) -> tuple[float | None, int]:
    if not contra:
        return None, 0
    n = 0
    hits = 0
    for qid, spec in contra.items():
        sides = spec.get("sides") or []
        if not sides:
            continue
        n += 1
        topk = set(ec.ranked(runs.get(qid, {}))[:K_CONTRA])
        # pass iff at least one doc from EVERY side is in top-k
        if all(any(d in topk for d in side) for side in sides):
            hits += 1
    return (hits / n if n else None), n


def score_supersession(runs, chains) -> tuple[float | None, float | None, int]:
    if not chains:
        return None, None, 0
    n = 0
    rank_sum = 0.0
    superseded_above = 0
    for qid, spec in chains.items():
        binding = spec.get("binding")
        superseded = spec.get("superseded") or []
        if not binding:
            continue
        n += 1
        rk = ec.ranked(runs.get(qid, {}))
        depth = len(rk)
        b_rank = _rank_of(rk, binding)
        # miss penalty: one past the deepest retrieved item
        rank_sum += b_rank if b_rank is not None else (depth + 1)
        b_eff = b_rank if b_rank is not None else (depth + 1)
        if any((sr := _rank_of(rk, s)) is not None and sr < b_eff for s in superseded):
            superseded_above += 1
    if not n:
        return None, None, 0
    return rank_sum / n, superseded_above / n, n


def score_traps(runs, qrels) -> tuple[float | None, int]:
    pairs = 0
    in_top5 = 0
    for qid, rels in qrels.items():
        traps = [d for d, r in rels.items() if r == 0]
        if not traps:
            continue
        top5 = set(ec.ranked(runs.get(qid, {}))[:K_TRAP])
        for t in traps:
            pairs += 1
            if t in top5:
                in_top5 += 1
    return (in_top5 / pairs if pairs else None), pairs


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("corpora", nargs="*", help="limit to these corpus dir names")
    p.add_argument("--system", choices=ec.SYSTEMS, help="limit to one system")
    args = p.parse_args(argv)

    corpora = args.corpora or ec.ALL_CORPORA
    systems = [args.system] if args.system else ec.SYSTEMS

    rows = []
    for corpus in corpora:
        qrels = ec.load_qrels(corpus)
        contra = ec.load_annotation("contra_sets", corpus)
        chains = ec.load_annotation("supersession_chains", corpus)
        for system in systems:
            runs = ec.load_runs(corpus, system)
            if runs is None:
                continue
            cr, n_cr = score_contradiction(runs, contra)
            mrb, sar, n_sup = score_supersession(runs, chains)
            trap, n_trap = score_traps(runs, qrels)
            block = {
                "contradiction_recall_at_10": cr,
                "mean_rank_binding": mrb,
                "superseded_above_rate": sar,
                "trap_in_top_5": trap,
                "n_contradiction_queries": n_cr,
                "n_supersession_queries": n_sup,
                "n_trap_pairs": n_trap,
            }
            path = ec.update_layer(corpus, system, "layer_2_adversarial", block)
            status = "wrote" if path else "NO RESULT FILE (run 03 first)"
            rows.append((corpus, system, block, status))

    print("\n===================== LAYER 2 — ADVERSARIAL =====================")
    print(f"{'corpus':<26s} {'system':<16s} ContraR@10  MeanRankBind  SupAbove  Trap@5  (n_c/n_s/n_t)")
    for corpus, system, b, status in rows:
        if status != "wrote":
            print(f"{corpus:<26s} {system:<16s} -- {status}")
            continue
        print(
            f"{corpus:<26s} {system:<16s} "
            f"{ec.fmt(b['contradiction_recall_at_10']):>9s}  "
            f"{ec.fmt(b['mean_rank_binding'],1):>11s}  "
            f"{ec.fmt(b['superseded_above_rate']):>7s}  "
            f"{ec.fmt(b['trap_in_top_5']):>5s}  "
            f"({b['n_contradiction_queries']}/{b['n_supersession_queries']}/{b['n_trap_pairs']})"
        )
    missing = [k for k in ("contra_sets", "supersession_chains")
               if any(ec.load_annotation(k, c) is None for c in corpora)]
    if missing:
        print(f"\nnote: some corpora missing annotations {missing} → those metrics are null.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
