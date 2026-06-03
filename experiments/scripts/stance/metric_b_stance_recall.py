#!/usr/bin/env python3
"""Metric (b): Stance-Evidence Recall@k — PURE RETRIEVAL, no LLM.

Productionized (P0-S5) as the HEADLINE Layer-3 stance metric. Reads only the
existing retrieve runs + annotations + qrels; does NOT touch oida-core, the
gold/stance labels, or any scored result JSON. Pure offline computation — no
API key, no network.

Falsification contract
----------------------
  MEASURES: does the system's top-k retrieval contain the gold stance-bearing
            documents for each stance-evaluable (SUPPORTS / CONTRADICTS) query?
            Generation is removed entirely (unlike the old LLM-judged
            stance_accuracy, which conflated retrieval with generation).
  HOW:      recall@k over the per-query stance_doc_ids. The explicit
            `stance_doc_ids` annotation is MISSING for 28 queries, so here it is
            computed over a labeled PROXY: the score-3 ("binding gold") qrels
            docs, except CONTRADICTS queries that carry a contra_sets entry use
            the conflicting-doc 'sides' (contra_all_sides@k = every side has >=1
            doc in top-k). NEI queries are EXCLUDED (no positive evidence to
            retrieve). recall_any@k (>=1 stance doc surfaced) is the headline
            number; recall_all@k (fraction of stance docs surfaced) and
            contra_all_sides@k are secondary diagnostics.
  WHERE:    written into each system's `layer_3_stance_abstention` output block
            under `stance_evidence_recall` (headline=True) by the Layer-3 driver
            05_eval_stance_abstention.py.
  WHAT CHANGES: the headline Layer-3 stance figure swaps to (b) recall_any@k.
            The old LLM-judged `stance_accuracy` is RETIRED — its key is still
            populated for 08_report compatibility but stamped
            `stance_accuracy_status: "retired/diagnostic-only"`. Metric (a),
            evidence-grounded stance, is a secondary slot (requires a judge key;
            not run in the offline gate).

PROXY caveat: `stance_doc_ids` is missing for 28 queries; the score-3 proxy is a
stand-in (see report §4). It is labeled `proxy (score-3, 28 stance_doc_ids
missing)` everywhere it is surfaced so no number is read as gold-grounded.

Query selection matches the scored pipeline exactly (stance_evaluable AND
gold_stance truthy) so the ranking is comparable to the old stance_accuracy.

Usage:
    python experiments/scripts/stance/metric_b_stance_recall.py
    python experiments/scripts/stance/metric_b_stance_recall.py --k 5 10 20
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # experiments/scripts
import eval_common as ec  # noqa: E402

# Labels the score-3 stand-in everywhere it is surfaced (output blocks + report
# tables) so no recall number is mistaken for gold (stance_doc_ids) grounding.
PROXY_LABEL = "proxy (score-3, 28 stance_doc_ids missing)"

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


def stance_recall_for_corpus(corpus: str, ks, systems=None) -> dict:
    """Compute stance-evidence recall@k for one corpus (behavior-preserving
    extraction of the per-corpus body of the old `main` loop).

    Returns:
        {
          "proxy_label": PROXY_LABEL,
          "n_sc_queries": int,            # SUPPORTS|CONTRADICTS queries scored
          "n_nei_excluded": int,          # NEI queries dropped (no positive evidence)
          "ks": list[int],
          "queries": {qid: {gold, stance_docs, n_stance_docs, source, is_contra_sides}},
          "systems": {sys: {k: {stance_recall_any, stance_recall_all,
                                contra_all_sides, n_contra_with_sides, per_query}}},
        }

    `systems` selects which SUT slots to score (default: all ec.SYSTEMS). Slots
    with no retrieve run for this corpus are silently skipped (as before).
    """
    systems = list(systems) if systems is not None else list(ec.SYSTEMS)
    sg = ec.load_annotation("stance_gold", corpus) or {}
    qrels = ec.load_qrels(corpus)
    contra = ec.load_annotation("contra_sets", corpus) or {}
    # same selection rule as the scored pipeline, minus NEI (no positive evidence)
    evaluable = {q: g["gold_stance"] for q, g in sg.items()
                 if g.get("stance_evaluable") and g.get("gold_stance")}
    sc = {q: g for q, g in evaluable.items() if g in ("SUPPORTS", "CONTRADICTS")}

    crep = {
        "proxy_label": PROXY_LABEL,
        "n_sc_queries": len(sc),
        "n_nei_excluded": sum(1 for v in evaluable.values() if v == "NEI"),
        "ks": list(ks),
        "queries": {},
        "systems": {},
    }

    # precompute stance docs per query
    qmeta = {}
    for q, gold in sc.items():
        sdocs, sides, src = stance_docs_for(corpus, q, gold, qrels, contra)
        qmeta[q] = {"gold": gold, "stance_docs": sorted(sdocs), "sides": sides, "source": src}
        crep["queries"][q] = {"gold": gold, "stance_docs": sorted(sdocs),
                              "n_stance_docs": len(sdocs), "source": src, "is_contra_sides": bool(sides)}

    for s in systems:
        runs = ec.load_runs(corpus, s)
        if runs is None:
            continue
        srep = {k: {} for k in ks}
        for k in ks:
            anys, alls, sides_list = [], [], []
            qdetail = {}
            for q, gold in sc.items():
                topk = ec.ranked(runs.get(q, {}))[:k]
                ra, rall, asides, hit = eval_query(topk, set(qmeta[q]["stance_docs"]), qmeta[q]["sides"])
                anys.append(ra); alls.append(rall)
                if asides is not None:
                    sides_list.append(asides)
                qdetail[q] = {"recall_any": ra, "recall_all": rall, "all_sides": asides, "hit": hit}
            srep[k] = {
                "stance_recall_any": mean(anys),
                "stance_recall_all": mean(alls),
                "contra_all_sides": mean(sides_list),
                "n_contra_with_sides": len(sides_list),
                "per_query": qdetail,
            }
        crep["systems"][s] = srep
    return crep


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--k", type=int, nargs="+", default=[5, 10])
    ap.add_argument("corpora", nargs="*", default=None)
    args = ap.parse_args(argv)
    corpora = args.corpora or ec.ORG_CORPORA

    report = {"metric": "stance_evidence_recall_at_k", "proxy_label": PROXY_LABEL,
              "ks": args.k, "corpora": {}, "per_system_pooled": {}}
    # pooled accumulators: per system -> per k -> lists
    pooled = {s: {k: {"any": [], "all": [], "sides": []} for k in args.k} for s in ec.SYSTEMS}

    for corpus in corpora:
        crep = stance_recall_for_corpus(corpus, args.k)
        # feed pooled accumulators from the per-query detail (behavior-preserving)
        for s, srep in crep["systems"].items():
            for k in args.k:
                for qd in srep[k]["per_query"].values():
                    pooled[s][k]["any"].append(qd["recall_any"])
                    pooled[s][k]["all"].append(qd["recall_all"])
                    if qd["all_sides"] is not None:
                        pooled[s][k]["sides"].append(qd["all_sides"])
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
    print(f"stance docs: {PROXY_LABEL}")
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
