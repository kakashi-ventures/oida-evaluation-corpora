#!/usr/bin/env python3
"""Phase C — Layer 1 BEIR-standard IR scoring on Phase B retrieve runs.

For each (corpus, retrieve_run) pair, computes:

  - NDCG@k (graded relevance — gain = 2^rel − 1)
  - Recall@k (binary: rel ≥ 1 counts as relevant)
  - MAP@k (binary)
  - P@k (binary)

and writes a per-result JSON to ``corpora/<id>/results/<system>_<run_id>.json``
following the EXPERIMENT_PLAN.md §7 schema. This is the **public** output —
versioned in the repo for community inspection.

Layers 2-5 fields are emitted as ``null`` in this script except the parts of
Layer 5 (practicality) that the retrieve run already collected
(p50/p95 latency). Other layers are filled by their dedicated scripts
(04-07) once those annotations exist.

Usage:
    python experiments/scripts/03_eval_static_ir.py \\
        --run-id 2026-05-29T09Z \\
        --system oida \\
        --system-version angelica-db@d1cad80b
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))

from adapters.oida import CORPUS_TO_PROJECT_SLUG  # noqa: E402

RETRIEVE_ROOT = REPO_ROOT / "experiments" / "output" / "retrieve_runs"
INGEST_ROOT = REPO_ROOT / "experiments" / "output" / "ingest_reports"
RESULTS_DIRNAME = "results"

NDCG_KS = (1, 5, 10, 20)
RECALL_KS = (5, 10, 100)
PRECISION_KS = (1, 5)
MAP_KS = (10,)
SCHEMA_VERSION = "2"
DATASET_VERSION = "v2.1.0"


# ---------------------------------------------------------------------------
# qrels + runs loaders
# ---------------------------------------------------------------------------


def load_qrels(qrels_path: Path) -> dict[str, dict[str, int]]:
    """Return {qid: {doc_id: relevance_int}} from a BEIR-style test.tsv."""
    out: dict[str, dict[str, int]] = {}
    lines = qrels_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return out
    header = lines[0].split("\t")
    if header != ["query-id", "corpus-id", "score"]:
        raise ValueError(f"unexpected qrels header in {qrels_path}: {header}")
    for line in lines[1:]:
        if not line.strip():
            continue
        qid, cid, score = line.split("\t")
        out.setdefault(qid, {})[cid] = int(score)
    return out


def load_runs(runs_path: Path) -> dict[str, dict[str, float]]:
    return json.loads(runs_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# metric primitives
# ---------------------------------------------------------------------------


def _ranked_doc_ids(scores: dict[str, float]) -> list[str]:
    """Stable descending sort by score."""
    return [doc for doc, _ in sorted(scores.items(), key=lambda kv: -kv[1])]


def ndcg_at_k(retrieved: list[str], qrels_q: dict[str, int], k: int) -> float:
    """Graded NDCG with gain = 2^rel − 1, discount = 1/log2(rank + 1)."""
    if not qrels_q:
        return 0.0
    dcg = 0.0
    for i, doc in enumerate(retrieved[:k], start=1):
        rel = qrels_q.get(doc, 0)
        if rel > 0:
            dcg += (2 ** rel - 1) / math.log2(i + 1)
    ideal_rels = sorted(qrels_q.values(), reverse=True)[:k]
    idcg = sum((2 ** rel - 1) / math.log2(i + 1)
               for i, rel in enumerate(ideal_rels, start=1) if rel > 0)
    return dcg / idcg if idcg > 0 else 0.0


def recall_at_k(retrieved: list[str], qrels_q: dict[str, int], k: int) -> float:
    relevant = {d for d, r in qrels_q.items() if r > 0}
    if not relevant:
        return 0.0
    hits = sum(1 for d in retrieved[:k] if d in relevant)
    return hits / len(relevant)


def precision_at_k(retrieved: list[str], qrels_q: dict[str, int], k: int) -> float:
    relevant = {d for d, r in qrels_q.items() if r > 0}
    if k == 0:
        return 0.0
    hits = sum(1 for d in retrieved[:k] if d in relevant)
    return hits / k


def average_precision_at_k(retrieved: list[str], qrels_q: dict[str, int], k: int) -> float:
    relevant = {d for d, r in qrels_q.items() if r > 0}
    if not relevant:
        return 0.0
    hits = 0
    score = 0.0
    for i, doc in enumerate(retrieved[:k], start=1):
        if doc in relevant:
            hits += 1
            score += hits / i
    return score / len(relevant)


# ---------------------------------------------------------------------------
# per-corpus scoring
# ---------------------------------------------------------------------------


def _retrieve_summary(run_dir: Path) -> dict | None:
    p = run_dir / "summary.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _retrieve_top_k_seen(run_dir: Path) -> int | None:
    s = _retrieve_summary(run_dir) or {}
    return s.get("top_k")


def _ingest_median_sec_per_doc(corpus_name: str, system: str | None = None) -> float | None:
    # 01_ingest.py writes per-system reports under ingest_reports/<system>/.
    # Prefer that; fall back to the legacy flat path for pre-multi-deploy runs.
    p = (INGEST_ROOT / system / f"{corpus_name}.jsonl") if system else None
    if p is None or not p.exists():
        p = INGEST_ROOT / f"{corpus_name}.jsonl"
    if not p.exists():
        return None
    secs: list[float] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not rec.get("committed"):
            continue
        latency_ms = rec.get("latency_ms")
        if latency_ms is None:
            continue
        secs.append(float(latency_ms) / 1000.0)
    return statistics.median(secs) if secs else None


def score_corpus(corpus_name: str, run_id: str, system: str, system_version: str) -> dict | None:
    corpus_dir = REPO_ROOT / "corpora" / corpus_name
    if not corpus_dir.exists():
        return None
    run_dir = RETRIEVE_ROOT / corpus_name / f"{system}_{run_id}"
    if not run_dir.is_dir():
        print(f"  ! skip {corpus_name}: no retrieve run at {run_dir.relative_to(REPO_ROOT)}")
        return None
    qrels_path = corpus_dir / "qrels" / "test.tsv"
    runs_path = run_dir / "runs.json"
    if not (qrels_path.exists() and runs_path.exists()):
        print(f"  ! skip {corpus_name}: missing qrels or runs.json")
        return None

    try:
        qrels = load_qrels(qrels_path)
    except ValueError as e:
        print(f"  ! skip {corpus_name}: {e}")
        return None
    runs = load_runs(runs_path)

    rsum = _retrieve_summary(run_dir) or {}
    top_k_run = _retrieve_top_k_seen(run_dir) or 20

    # Aggregate per-query metrics, averaged over queries that have qrels gold.
    n = 0
    ndcg_sum = {k: 0.0 for k in NDCG_KS}
    recall_sum = {k: 0.0 for k in RECALL_KS}
    map_sum = {k: 0.0 for k in MAP_KS}
    precision_sum = {k: 0.0 for k in PRECISION_KS}
    qids_with_gold = 0
    qids_with_retrieved = 0
    for qid, qrels_q in qrels.items():
        if not qrels_q:
            continue
        qids_with_gold += 1
        retrieved = _ranked_doc_ids(runs.get(qid, {}))
        if retrieved:
            qids_with_retrieved += 1
        for k in NDCG_KS:
            ndcg_sum[k] += ndcg_at_k(retrieved, qrels_q, k)
        for k in RECALL_KS:
            recall_sum[k] += recall_at_k(retrieved, qrels_q, k)
        for k in MAP_KS:
            map_sum[k] += average_precision_at_k(retrieved, qrels_q, k)
        for k in PRECISION_KS:
            precision_sum[k] += precision_at_k(retrieved, qrels_q, k)
        n += 1

    def _mean(d: dict, denom: int) -> dict:
        return {str(k): (v / denom) if denom > 0 else None for k, v in d.items()}

    layer_1 = {
        "ndcg": _mean(ndcg_sum, n),
        "recall": _mean(recall_sum, n),
        "map": _mean(map_sum, n),
        "precision": _mean(precision_sum, n),
    }
    # Recall@k for k > top_k_run is not measurable from this run — set null.
    for k in RECALL_KS:
        if k > top_k_run:
            layer_1["recall"][str(k)] = None

    # Layer 5 partial fill (what we measured)
    ingest_median = _ingest_median_sec_per_doc(corpus_name, system)
    layer_5 = {
        "ingest_wall_clock_sec_per_doc_median": ingest_median,
        "retrieve_latency_ms_p50": rsum.get("latency_ms_p50"),
        "retrieve_latency_ms_p95": rsum.get("latency_ms_p95"),
        "retrieve_cost_usd_per_query_median": None,  # OpenAI billing not visible
        "ingest_cost_usd_total": None,
    }

    report = {
        "$schema_version": SCHEMA_VERSION,
        "corpus_id": corpus_name,
        "system": system,
        "system_version": system_version,
        "run_id": run_id,
        "dataset_version": DATASET_VERSION,
        "common_setup": {
            "embedder": "openai/text-embedding-3-small",
            "ingest_llm": "(OIDA deployed default)",
            "stance_judge_llm": None,  # Layer 3 not run yet
            "top_k_reported": [1, 5, 10, 20],
            "retrieve_top_k_used": top_k_run,
            "retrieve_v0_thresholds": {"tauBind": 0.2, "tauFallback": 0.1},
        },
        "layer_1_static_ir": layer_1,
        "layer_2_adversarial": {
            "contradiction_recall_at_10": None,
            "mean_rank_binding": None,
            "superseded_above_rate": None,
            "trap_in_top_5": None,
            "n_contradiction_queries": 0,
            "n_supersession_queries": 0,
            "n_trap_pairs": 0,
        },
        "layer_3_stance_abstention": {
            "stance_accuracy": None,
            "stance_macro_f1": None,
            "contradiction_recall": None,
            "stance_coverage": None,
            "epistemic_abstention_accuracy": None,
            "false_commitment_rate": None,
            "false_ignorance_rate": None,
            "selective_stance_precision": None,
            "abstention_commitment_balance": None,
            "epistemic_risk_score": None,
            "n_gold_nei": 0,
            "n_false_commitments": 0,
            "n_false_ignorance": 0,
            "n_non_neutral_predictions": 0,
        },
        "layer_4_temporal": {
            "cutoffs": [],
            "ndcg_at_10_per_cutoff": [],
            "current_state_accuracy_at_1": None,
            "current_state_accuracy_at_5": None,
            "current_state_accuracy_at_10": None,
            "superseded_leakage_at_10": None,
            "temporal_ndcg_at_10": None,
            "stable_knowledge_retention_at_10": None,
            "freshness_overbias_rate": None,
            "lifecycle_ranking_agreement": None,
            "as_of_accuracy_at_10": None,
            "decay_sensitivity_pairwise": None,
            "reinforcement_lift_mean": None,
            "n_current_state_queries": 0,
            "n_stable_knowledge_queries": 0,
        },
        "layer_5_practicality": layer_5,
        "f_conditions": {
            # cross-system F-conditions are computed in the comparison roll-up,
            # not per-result. Per-result we only stamp the abstention/temporal
            # F-conditions that *could* be evaluated from this corpus alone
            # — none yet, since L3/L4 require annotations.
        },
        "n_queries_total": len(qrels),
        "n_queries_with_gold": qids_with_gold,
        "n_queries_with_retrieved_docs": qids_with_retrieved,
        "notes": _build_notes(system, top_k_run, rsum),
    }
    return report


def _build_notes(system: str, top_k_run: int, rsum: dict) -> str:
    """Run-specific notes for the result JSON (no longer hardcoded to the
    handicapped 2026-05-29 angelica-db run)."""
    n_empty = rsum.get("queries_empty", 0)
    recall100 = (
        "Recall@100 is measurable (run reached top_k>=100)."
        if top_k_run >= 100
        else f"Recall@100 is null because the run capped at top_k={top_k_run}."
    )
    base = (
        f"Layer 1 only. Retrieve run used OIDA v0 (tauBind=0.2, tauFallback=0.1). "
        f"top_k={top_k_run}; {recall100} "
        f"{n_empty} queries returned empty subgraph from OIDA."
    )
    if system == "oida-core":
        return (
            base
            + " Remediated run on the oida-core deploy: per-corpus project "
            "isolation (each corpus in its own project, not the shared default), "
            "widened server-side commit transaction window, and /health warm-up "
            "(tobefixed/REMEDIATION.md items A/C/E). This is the fair-conditions "
            "OIDA comparison surface; see experiments/EXPERIMENT_PLAN.md §1 (oida-core row)."
        )
    return base + " See experiments/EXPERIMENT_PLAN.md §10."


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--run-id", required=True, help="retrieve run id (must match dir name suffix)")
    parser.add_argument("--system", default="oida")
    parser.add_argument("--system-version", default="angelica-db@d1cad80b")
    parser.add_argument("corpora", nargs="*", help="optional corpus dir names to limit the run")
    args = parser.parse_args(argv)

    targets = args.corpora if args.corpora else list(CORPUS_TO_PROJECT_SLUG.keys())
    written: list[Path] = []
    grand_summary: list[tuple[str, dict]] = []

    for corpus_name in targets:
        report = score_corpus(corpus_name, args.run_id, args.system, args.system_version)
        if report is None:
            continue
        out_dir = REPO_ROOT / "corpora" / corpus_name / RESULTS_DIRNAME
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{args.system}_{args.run_id}.json"
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        written.append(out_path)
        grand_summary.append((corpus_name, report["layer_1_static_ir"]))
        print(f"  wrote {out_path.relative_to(REPO_ROOT)}")

    print("\n=========================== LAYER 1 SUMMARY ===========================")
    print(f"{'corpus':<30s}  NDCG@10  NDCG@5  NDCG@1  Rec@10  Rec@5   MAP@10  P@5")
    for corpus_name, l1 in grand_summary:
        ndcg = l1["ndcg"]; rec = l1["recall"]; mp = l1["map"]; pr = l1["precision"]
        def _f(v, w=7): return f"{v:.4f}" if v is not None else f"{'—':<{w}}"
        print(
            f"  {corpus_name:<28s}  {_f(ndcg.get('10'))}  {_f(ndcg.get('5'))}  "
            f"{_f(ndcg.get('1'))}  {_f(rec.get('10'))}  {_f(rec.get('5'))}  "
            f"{_f(mp.get('10'))}  {_f(pr.get('5'))}"
        )
    print(f"\n{len(written)} result file(s) written under corpora/<id>/results/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
