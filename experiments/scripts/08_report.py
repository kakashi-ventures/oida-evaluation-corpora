#!/usr/bin/env python3
"""Roll-up — cross-system F-conditions, H8 deploy parity, comparison.json,
RESULTS.md (EXPERIMENT_PLAN.md §4, §12).

Reads every ``corpora/<id>/results/<system>_*.json`` (newest per system) and:

  - computes the cross-system F-conditions per OIDA deploy
    (F-1-PARITY, F-2-CONTRA, F-2-SUPER, F-2-TRAP, F-5-COST, F-5-LAT) and stamps
    them into that deploy's result files' ``f_conditions``;
  - computes the H8 deploy-parity diagnostic (oida-angelicadb vs oida-core)
    when both are present;
  - writes experiments/output/comparison.json (gitignored intermediate);
  - writes RESULTS.md at the repo root (the committed human-readable summary).

Per-corpus F-conditions (abstention/temporal) are stamped by 05/06; this script
does not overwrite them.

Usage:
    python experiments/scripts/08_report.py
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import eval_common as ec  # noqa: E402

COMPARISON_PATH = ec.REPO_ROOT / "experiments" / "output" / "comparison.json"
RESULTS_MD = ec.REPO_ROOT / "RESULTS.md"
BASELINES = ["graphrag", "lightrag", "hipporag"]


def gather() -> dict[str, dict[str, dict]]:
    """results[corpus][system] = result dict (newest)."""
    out: dict[str, dict[str, dict]] = {}
    for corpus in ec.ALL_CORPORA:
        out[corpus] = {}
        for system in ec.SYSTEMS:
            path = ec.resolve_result_file(corpus, system)
            if path:
                out[corpus][system] = ec.load_result(path)
    return out


def _ndcg10(r): return (((r or {}).get("layer_1_static_ir") or {}).get("ndcg") or {}).get("10")
def _l2(r, k): return ((r or {}).get("layer_2_adversarial") or {}).get(k)
def _p95(r): return ((r or {}).get("layer_5_practicality") or {}).get("retrieve_latency_ms_p95")
def _cost(r): return ((r or {}).get("layer_5_practicality") or {}).get("retrieve_cost_usd_per_query_median")


def org_mean_ndcg(results, system):
    vals = [_ndcg10(results[c].get(system)) for c in ec.ORG_CORPORA if results[c].get(system)]
    vals = [v for v in vals if v is not None]
    return statistics.mean(vals) if vals else None


def pooled_rate(results, system, rate_key, n_key, corpora):
    num = den = 0.0
    for c in corpora:
        r = results[c].get(system)
        if not r:
            continue
        rate, n = _l2(r, rate_key), _l2(r, n_key)
        if rate is not None and n:
            num += rate * n
            den += n
    return (num / den) if den else None


def median_metric(results, system, fn, corpora):
    vals = [fn(results[c].get(system)) for c in corpora if results[c].get(system)]
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else None


def cross_system_fconditions(results, oida_system):
    """Compute the 6 cross-system F-conditions for one OIDA deploy."""
    fc = {}

    # F-1-PARITY (org-mean NDCG@10)
    oida_n = org_mean_ndcg(results, oida_system)
    base_ns = {b: org_mean_ndcg(results, b) for b in BASELINES}
    max_base = max([v for v in base_ns.values() if v is not None], default=None)
    if oida_n is not None and max_base is not None:
        val = abs(oida_n - max_base)
        fc["F-1-PARITY"] = {"passed": val <= 0.05, "value": round(val, 4), "threshold": 0.05,
                            "oida": round(oida_n, 4), "max_baseline": round(max_base, 4)}
    else:
        fc["F-1-PARITY"] = {"passed": None, "value": None, "threshold": 0.05}

    # F-2-CONTRA (pooled across all corpora)
    oida_cr = pooled_rate(results, oida_system, "contradiction_recall_at_10", "n_contradiction_queries", ec.ALL_CORPORA)
    base_cr = {b: pooled_rate(results, b, "contradiction_recall_at_10", "n_contradiction_queries", ec.ALL_CORPORA) for b in BASELINES}
    max_base_cr = max([v for v in base_cr.values() if v is not None], default=None)
    if oida_cr is not None and max_base_cr is not None:
        val = oida_cr - max_base_cr
        fc["F-2-CONTRA"] = {"passed": val >= 0.15, "value": round(val, 4), "threshold": 0.15,
                            "oida": round(oida_cr, 4), "max_baseline": round(max_base_cr, 4)}
    else:
        fc["F-2-CONTRA"] = {"passed": None, "value": None, "threshold": 0.15}

    # F-2-TRAP (pooled; lower is better; OIDA ≤ strictest baseline)
    oida_tr = pooled_rate(results, oida_system, "trap_in_top_5", "n_trap_pairs", ec.ALL_CORPORA)
    base_tr = {b: pooled_rate(results, b, "trap_in_top_5", "n_trap_pairs", ec.ALL_CORPORA) for b in BASELINES}
    strict_base = min([v for v in base_tr.values() if v is not None], default=None)
    if oida_tr is not None and strict_base is not None:
        fc["F-2-TRAP"] = {"passed": oida_tr <= strict_base, "value": round(oida_tr, 4),
                          "threshold": round(strict_base, 4), "strictest_baseline": round(strict_base, 4)}
    else:
        fc["F-2-TRAP"] = {"passed": None, "value": None, "threshold": None}

    # F-2-SUPER (mean rank binding + superseded-above); aggregate where present
    def agg_super(system):
        ranks, aboves, ns = [], [], 0
        for c in ec.ALL_CORPORA:
            r = results[c].get(system)
            if not r:
                continue
            n = _l2(r, "n_supersession_queries")
            if n:
                mrb, sar = _l2(r, "mean_rank_binding"), _l2(r, "superseded_above_rate")
                if mrb is not None:
                    ranks.append(mrb * n)
                if sar is not None:
                    aboves.append(sar * n)
                ns += n
        if not ns:
            return None, None
        return (sum(ranks) / ns if ranks else None), (sum(aboves) / ns if aboves else None)
    oida_mrb, oida_sar = agg_super(oida_system)
    base_super = {b: agg_super(b) for b in BASELINES}
    best_mrb = min([m for m, _ in base_super.values() if m is not None], default=None)
    best_sar = min([s for _, s in base_super.values() if s is not None], default=None)
    if oida_mrb is not None and best_mrb is not None:
        cond_rank = oida_mrb <= best_mrb
        cond_above = (oida_sar is not None and best_sar is not None and oida_sar <= 0.25 * best_sar) if best_sar else None
        passed = bool(cond_rank) and (cond_above if cond_above is not None else True)
        fc["F-2-SUPER"] = {"passed": passed, "value": {"mean_rank_binding": round(oida_mrb, 3),
                           "superseded_above_rate": (round(oida_sar, 3) if oida_sar is not None else None)},
                           "threshold": {"best_baseline_mean_rank": round(best_mrb, 3),
                           "best_baseline_superseded_above": (round(best_sar, 3) if best_sar is not None else None)}}
    else:
        fc["F-2-SUPER"] = {"passed": None, "value": None, "threshold": None}

    # F-5-LAT (median p95 across corpora; OIDA ≤ 3× median baseline)
    oida_lat = median_metric(results, oida_system, _p95, ec.ALL_CORPORA)
    base_lat = [median_metric(results, b, _p95, ec.ALL_CORPORA) for b in BASELINES]
    base_lat = [v for v in base_lat if v is not None]
    if oida_lat is not None and base_lat:
        med = statistics.median(base_lat)
        fc["F-5-LAT"] = {"passed": oida_lat <= 3 * med, "value": round(oida_lat, 1),
                         "threshold": round(3 * med, 1), "median_baseline_p95": round(med, 1)}
    else:
        fc["F-5-LAT"] = {"passed": None, "value": None, "threshold": 3.0}

    # F-5-COST (median per-query cost; OIDA ≤ 3× median baseline)
    oida_cost = median_metric(results, oida_system, _cost, ec.ALL_CORPORA)
    base_cost = [median_metric(results, b, _cost, ec.ALL_CORPORA) for b in BASELINES]
    base_cost = [v for v in base_cost if v is not None]
    if oida_cost is not None and base_cost:
        med = statistics.median(base_cost)
        passed = oida_cost <= 3 * med if med > 0 else None
        fc["F-5-COST"] = {"passed": passed, "value": round(oida_cost, 6),
                          "threshold": round(3 * med, 6), "median_baseline_cost": round(med, 6)}
    else:
        fc["F-5-COST"] = {"passed": None, "value": None, "threshold": 3.0}

    return fc


def h8_parity(results):
    """|ΔNDCG@10| (org-mean) and top-10 Jaccard between the two OIDA deploys."""
    ang, core = "oida-angelicadb", "oida-core"
    deltas = []
    for c in ec.ORG_CORPORA:
        a, b = _ndcg10(results[c].get(ang)), _ndcg10(results[c].get(core))
        if a is not None and b is not None:
            deltas.append(abs(a - b))
    jacc = []
    for c in ec.ALL_CORPORA:
        ra, rb = ec.load_runs(c, ang), ec.load_runs(c, core)
        if not ra or not rb:
            continue
        for qid in set(ra) & set(rb):
            ta, tb = set(ec.ranked(ra[qid])[:10]), set(ec.ranked(rb[qid])[:10])
            if ta or tb:
                jacc.append(len(ta & tb) / len(ta | tb))
    if not deltas and not jacc:
        return None
    mean_delta = statistics.mean(deltas) if deltas else None
    mean_jacc = statistics.mean(jacc) if jacc else None
    return {
        "F-8-DEPLOY-NDCG": {"passed": (mean_delta <= 0.05) if mean_delta is not None else None,
                            "value": round(mean_delta, 4) if mean_delta is not None else None, "threshold": 0.05},
        "F-8-DEPLOY-TOPK": {"passed": (mean_jacc >= 0.70) if mean_jacc is not None else None,
                            "value": round(mean_jacc, 4) if mean_jacc is not None else None, "threshold": 0.70},
        "n_corpora_compared": len(deltas), "n_queries_compared": len(jacc),
    }


def main() -> int:
    results = gather()
    present = [s for s in ec.SYSTEMS if any(results[c].get(s) for c in ec.ALL_CORPORA)]
    oida_present = [s for s in ec.OIDA_SYSTEMS if s in present]

    comparison = {
        "dataset_version": "v2.1.0",
        "systems_present": present,
        "ndcg_at_10": {c: {s: _ndcg10(results[c].get(s)) for s in present} for c in ec.ALL_CORPORA},
        "cross_system_f_conditions": {},
        "h8_deploy_parity": h8_parity(results),
    }
    for oida in oida_present:
        fc = cross_system_fconditions(results, oida)
        comparison["cross_system_f_conditions"][oida] = fc
        # stamp into this deploy's result files
        for c in ec.ALL_CORPORA:
            path = ec.resolve_result_file(c, oida)
            if path:
                r = ec.load_result(path)
                r.setdefault("f_conditions", {}).update(fc)
                ec.save_result(path, r)

    # H5 — pooled abstention F-conditions (written by 05). Stamp into every
    # system's result files (one pooled verdict per system, repeated per corpus).
    abstention_path = ec.REPO_ROOT / "experiments" / "output" / "abstention_h5.json"
    abstention = json.loads(abstention_path.read_text(encoding="utf-8")) if abstention_path.exists() else {}
    comparison["abstention_h5"] = abstention
    for system, conds in abstention.items():
        fab = {k: v for k, v in conds.items() if k.startswith("F-ABSTAIN")}
        for c in ec.ALL_CORPORA:
            path = ec.resolve_result_file(c, system)
            if path:
                r = ec.load_result(path)
                r.setdefault("f_conditions", {}).update(fab)
                ec.save_result(path, r)

    COMPARISON_PATH.parent.mkdir(parents=True, exist_ok=True)
    COMPARISON_PATH.write_text(json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_results_md(results, comparison, present)
    print(f"wrote {COMPARISON_PATH.relative_to(ec.REPO_ROOT)}")
    print(f"wrote {RESULTS_MD.relative_to(ec.REPO_ROOT)}")
    print(f"systems present: {present}")
    return 0


def _fmt(v, nd=3):
    return f"{v:.{nd}f}" if isinstance(v, (int, float)) else "—"


def _pass(p):
    return {True: "✅ PASS", False: "❌ FAIL", None: "— n/a"}[p]


def _write_results_md(results, comparison, present):
    L = ["# RESULTS — OIDA vs GraphRAG / LightRAG / HippoRAG", ""]
    L += [f"Dataset **v2.1.0**. Systems present: {', '.join(present)}.", ""]
    L += ["> Generated by `experiments/scripts/08_report.py`. F-conditions are "
          "pre-registered in `experiments/EXPERIMENT_PLAN.md` §4; a fail is a "
          "published null result, not a suppressed one.", ""]

    L += ["## Layer 1 — NDCG@10 by corpus", "",
          "| Corpus | " + " | ".join(present) + " |",
          "|" + "---|" * (len(present) + 1)]
    for c in ec.ALL_CORPORA:
        L.append(f"| {c} | " + " | ".join(_fmt(comparison['ndcg_at_10'][c].get(s)) for s in present) + " |")
    L.append("")

    for oida, fc in comparison["cross_system_f_conditions"].items():
        L += [f"## Cross-system F-conditions — {oida}", "",
              "| F-condition | Result | Value | Threshold |", "|---|---|---|---|"]
        for fid in ("F-1-PARITY", "F-2-CONTRA", "F-2-SUPER", "F-2-TRAP", "F-5-LAT", "F-5-COST"):
            e = fc.get(fid, {})
            val = e.get("value")
            val_s = json.dumps(val) if isinstance(val, dict) else _fmt(val, 4)
            thr = e.get("threshold")
            thr_s = json.dumps(thr) if isinstance(thr, dict) else _fmt(thr, 4)
            L.append(f"| {fid} | {_pass(e.get('passed'))} | {val_s} | {thr_s} |")
        L.append("")

    h8 = comparison.get("h8_deploy_parity")
    L += ["## OIDA deploy parity (H8)", ""]
    if not h8:
        L += ["_Not computed — `oida-core` results not present yet._", ""]
    else:
        L += [f"- **F-8-DEPLOY-NDCG**: {_pass(h8['F-8-DEPLOY-NDCG']['passed'])} "
              f"(|Δ NDCG@10| = {_fmt(h8['F-8-DEPLOY-NDCG']['value'],4)}, ≤ 0.05; "
              f"{h8['n_corpora_compared']} org corpora)",
              f"- **F-8-DEPLOY-TOPK**: {_pass(h8['F-8-DEPLOY-TOPK']['passed'])} "
              f"(top-10 Jaccard = {_fmt(h8['F-8-DEPLOY-TOPK']['value'],4)}, ≥ 0.70; "
              f"{h8['n_queries_compared']} queries)", ""]

    # H5 — abstention thresholds (pooled per system)
    abstention = comparison.get("abstention_h5") or {}
    if abstention:
        L += ["## Layer 3 abstention thresholds (H5, pooled per system)", "",
              "_Pooled over all stance-gold queries per system. **Small-sample caveat:** very "
              "few gold-NEI queries exist, so FCR/EAA are near-noise; read as directional._", "",
              "| System | F-ABSTAIN-1 FCR≤.10 | F-ABSTAIN-2 EAA≥.80 | F-ABSTAIN-3 SSP≥.75 | F-ABSTAIN-4 FIR≤.20 | n |",
              "|---|---|---|---|---|---|"]
        for s in present:
            c = abstention.get(s)
            if not c:
                continue
            def cell(fid):
                e = c.get(fid, {})
                return f"{_pass(e.get('passed'))} ({_fmt(e.get('value'),3)})"
            L.append(f"| {s} | {cell('F-ABSTAIN-1')} | {cell('F-ABSTAIN-2')} | {cell('F-ABSTAIN-3')} "
                     f"| {cell('F-ABSTAIN-4')} | {c.get('_pooled_n','—')} |")
        L.append("")

    # Known limitations / not measured
    L += ["## Coverage & known limitations", "",
          "- **F-5-COST is asymmetric — read with care.** Per-query token cost is now "
          "populated: graphrag's LLM tokens are tiktoken-measured from basic_search's real "
          "context+answer; lightrag/hipporag are embed-only (exact); OIDA is imputed at its "
          "query-embedding cost. **Caveat:** OIDA's internal solver/LLM compute is deploy-side "
          "and not billed to us, so OIDA's number reflects only its externally-visible "
          "(embedding) cost — it is NOT a like-for-like total against graphrag's LLM cost. "
          "The verdict favors OIDA for that reason; treat it as 'OIDA is embedding-cheap "
          "externally', not 'OIDA is cheaper than graphrag end-to-end'.",
          "- **OIDA v1 probe mode not tested.** Probing the deploy confirmed v1 returns no "
          "`supporting_sources` (so its results cannot be mapped to corpus doc IDs for BEIR "
          "scoring) and gates out ~half of queries (`EMPTY_DECOMPOSITION`). All OIDA numbers "
          "are the **v0** retrieve mode (`tauBind=0.2, tauFallback=0.1`).",
          "- **Layer-4 per-cutoff** uses a retrieve-time `created<=cutoff` mask, not the "
          "plan's re-ingested time slices (infeasible on the live deploys within budget).",
          "- **oida-core vertexminds** is missing 2 dense gold docs (server commit timeout); "
          "its NDCG/recall are on ~73/75 gold docs.",
          "- **Small stance samples.** Only 3 gold-NEI queries exist pooled across all corpora, "
          "so the H5 abstention verdicts are directional, not robust.",
          "- **Annotations are subagent drafts** pending human (Carlo/Federico) review.", ""]

    # Per-corpus L2/L3/L4 snapshot
    L += ["## Layers 2-4 snapshot (per corpus, per system)", ""]
    for c in ec.ALL_CORPORA:
        L += [f"### {c}", "",
              "| System | Trap@5 | ContraR@10 | StanceAcc | EAA | FCR | CSA@10 | TmpNDCG |",
              "|---|---|---|---|---|---|---|---|"]
        for s in present:
            r = results[c].get(s)
            if not r:
                continue
            l2 = r.get("layer_2_adversarial", {})
            l3 = r.get("layer_3_stance_abstention", {})
            l4 = r.get("layer_4_temporal", {})
            L.append(
                f"| {s} | {_fmt(l2.get('trap_in_top_5'))} | {_fmt(l2.get('contradiction_recall_at_10'))} "
                f"| {_fmt(l3.get('stance_accuracy'))} | {_fmt(l3.get('epistemic_abstention_accuracy'))} "
                f"| {_fmt(l3.get('false_commitment_rate'))} | {_fmt(l4.get('current_state_accuracy_at_10'))} "
                f"| {_fmt(l4.get('temporal_ndcg_at_10'))} |"
            )
        L.append("")

    RESULTS_MD.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
