#!/usr/bin/env python3
"""Metric (b): Stance-Evidence Recall@k — PURE RETRIEVAL, no LLM.

Prototype for the stance-metric redesign (read-only diagnostic). Does NOT touch
oida-core, the scored Layer-3 pipeline (05_eval_stance_abstention.py), or any
result JSON. It reads only the existing retrieve runs + annotations.

Why this metric
---------------
The shipped Layer-3 stance metric conflates RETRIEVAL with GENERATION: GraphRAG
is judged on the argued prose it generates (`raw_response_text`), while OIDA /
LightRAG / HippoRAG are judged on the raw text of their *top-1* retrieved doc
(05_eval_stance_abstention.py:_answer_for). This metric removes generation
entirely and asks only: did the system's top-k surface the documents that carry
the correct stance?

Stance-bearing gold docs per query
-----------------------------------
  * CONTRADICTS with a contra_sets entry  -> the conflicting doc 'sides'
    (purpose-built annotation). `all_sides@k` = every side has >=1 doc in top-k.
  * otherwise (SUPPORTS, or CONTRADICTS lacking a contra_set) -> PROXY = the
    score-3 ("binding gold") docs from qrels. This is a stand-in: the real
    missing annotation is an explicit per-query `stance_doc_ids` (see report §4).
  * NEI queries are EXCLUDED (no positive stance evidence to retrieve).

Query selection matches the scored pipeline exactly (stance_evaluable AND
gold_stance truthy) so the ranking is comparable to the old stance_accuracy.

Usage:
    python experiments/scripts/stance_redesign/metric_b_stance_recall.py
    python experiments/scripts/stance_redesign/metric_b_stance_recall.py --k 5 10 20
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # experiments/scripts
import eval_common as ec  # noqa: E402

OUT_DIR = ec.REPO_ROOT / "experiments" / "output" / "stance_redesign"


def stance_docs_for(corpus: str, qid: str, gold: str, qrels: dict, contra: dict):
    """Return (stance_doc_set, sides_or_None, source_tag)."""
    entry = (contra or {}).get(qid)
    if entry and entry.get("sides"):
        sides = [list(s) for s in entry["sides"]]
        docs = {d for side in sides for d in side}
        return docs, sides, "contra_sets"
    # proxy: score-3 binding gold docs
    rel = qrels.get(qid, {})
    s3 = {d for d, s in rel.items() if s == 3}
    return s3, None, "qrels_score3_proxy"


def eval_query(topk: list[str], stance_docs: set, sides):
    tk = set(topk)
    hit = tk & stance_docs
    recall_any = 1.0 if hit else 0.0
    recall_all = (len(hit) / len(stance_docs)) if stance_docs else None
    if sides:
        all_sides = 1.0 if all(any(d in tk for d in side) for side in sides) else 0.0
    else:
        all_sides = None
    return recall_any, recall_all, all_sides, sorted(hit)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else None


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--k", type=int, nargs="+", default=[5, 10])
    ap.add_argument("corpora", nargs="*", default=None)
    args = ap.parse_args(argv)
    corpora = args.corpora or ec.ORG_CORPORA

    report = {"metric": "stance_evidence_recall_at_k", "ks": args.k,
              "corpora": {}, "per_system_pooled": {}}
    # pooled accumulators: per system -> per k -> lists
    pooled = {s: {k: {"any": [], "all": [], "sides": []} for k in args.k} for s in ec.SYSTEMS}
    pooled_n = {s: 0 for s in ec.SYSTEMS}

    for corpus in corpora:
        sg = ec.load_annotation("stance_gold", corpus) or {}
        qrels = ec.load_qrels(corpus)
        contra = ec.load_annotation("contra_sets", corpus) or {}
        # same selection rule as the scored pipeline, minus NEI (no positive evidence)
        evaluable = {q: g["gold_stance"] for q, g in sg.items()
                     if g.get("stance_evaluable") and g.get("gold_stance")}
        sc = {q: g for q, g in evaluable.items() if g in ("SUPPORTS", "CONTRADICTS")}

        crep = {"n_sc_queries": len(sc), "n_nei_excluded": sum(1 for v in evaluable.values() if v == "NEI"),
                "queries": {}, "systems": {}}

        # precompute stance docs per query
        qmeta = {}
        for q, gold in sc.items():
            sdocs, sides, src = stance_docs_for(corpus, q, gold, qrels, contra)
            qmeta[q] = {"gold": gold, "stance_docs": sorted(sdocs), "sides": sides, "source": src}
            crep["queries"][q] = {"gold": gold, "stance_docs": sorted(sdocs),
                                  "n_stance_docs": len(sdocs), "source": src, "is_contra_sides": bool(sides)}

        for s in ec.SYSTEMS:
            runs = ec.load_runs(corpus, s)
            if runs is None:
                continue
            srep = {k: {} for k in args.k}
            for k in args.k:
                anys, alls, sides_list = [], [], []
                qdetail = {}
                for q, gold in sc.items():
                    topk = ec.ranked(runs.get(q, {}))[:k]
                    ra, rall, asides, hit = eval_query(topk, set(qmeta[q]["stance_docs"]), qmeta[q]["sides"])
                    anys.append(ra); alls.append(rall)
                    if asides is not None:
                        sides_list.append(asides)
                    qdetail[q] = {"recall_any": ra, "recall_all": rall, "all_sides": asides, "hit": hit}
                    pooled[s][k]["any"].append(ra)
                    pooled[s][k]["all"].append(rall)
                    if asides is not None:
                        pooled[s][k]["sides"].append(asides)
                srep[k] = {
                    "stance_recall_any": mean(anys),
                    "stance_recall_all": mean(alls),
                    "contra_all_sides": mean(sides_list),
                    "n_contra_with_sides": len(sides_list),
                    "per_query": qdetail,
                }
            crep["systems"][s] = srep
            pooled_n[s] = pooled_n.get(s, 0)
        report["corpora"][corpus] = crep

    for s in ec.SYSTEMS:
        report["per_system_pooled"][s] = {}
        for k in args.k:
            report["per_system_pooled"][s][k] = {
                "stance_recall_any": mean(pooled[s][k]["any"]),
                "stance_recall_all": mean(pooled[s][k]["all"]),
                "contra_all_sides": mean(pooled[s][k]["sides"]),
                "n_queries": len(pooled[s][k]["any"]),
                "n_contra_with_sides": len(pooled[s][k]["sides"]),
            }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"metric_b_recall.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- printed tables ----
    def f(v):
        return f"{v:.3f}" if isinstance(v, float) else "  — "
    print("\n===== METRIC (b) STANCE-EVIDENCE RECALL@k  (pure retrieval, no LLM) =====")
    for corpus in corpora:
        cr = report["corpora"][corpus]
        print(f"\n--- {corpus}  (n_SC={cr['n_sc_queries']}, NEI excluded={cr['n_nei_excluded']}) ---")
        hdr = f"{'system':16s}"
        for k in args.k:
            hdr += f"  any@{k}  all@{k} sides@{k}"
        print(hdr)
        for s in ec.SYSTEMS:
            if s not in cr["systems"]:
                continue
            row = f"{s:16s}"
            for k in args.k:
                b = cr["systems"][s][k]
                row += f"  {f(b['stance_recall_any'])} {f(b['stance_recall_all'])} {f(b['contra_all_sides'])}"
            print(row)
    print("\n--- POOLED over 3 org corpora ---")
    hdr = f"{'system':16s}"
    for k in args.k:
        hdr += f"  any@{k}  all@{k} sides@{k}"
    print(hdr + "   n")
    for s in ec.SYSTEMS:
        ps = report["per_system_pooled"][s]
        row = f"{s:16s}"
        for k in args.k:
            row += f"  {f(ps[k]['stance_recall_any'])} {f(ps[k]['stance_recall_all'])} {f(ps[k]['contra_all_sides'])}"
        row += f"   {ps[args.k[0]]['n_queries']}"
        print(row)
    print(f"\nwrote {out.relative_to(ec.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
