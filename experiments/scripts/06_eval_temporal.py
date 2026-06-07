#!/usr/bin/env python3
"""Layer 4 — temporal / lifecycle-aware retrieval (EXPERIMENT_PLAN.md §5.4).

Doc-level adaptation of the spec's KO-level temporal layer. Computes the subset
of metrics feasible on the doc-level public corpora, from the MAIN retrieve run
plus annotations/{lifecycle,temporal_queries}/<corpus>.json:

  T1  current_state_accuracy_at_{1,5,10}
  T4  superseded_leakage_at_10
  T6  temporal_ndcg_at_10
  T9  stable_knowledge_retention_at_10
  T10 freshness_overbias_rate
  T11 lifecycle_ranking_agreement

and stamps the per-corpus temporal F-conditions (F-TEMP-1/2/4/5/6) into
``f_conditions``. The per-cutoff NDCG vector and F-TEMP-7 (lift vs B0
similarity-only) require the time-sliced retrieve runs and are left null here —
they are filled by the (paid) cutoff-slice pass. Org-* corpora only.

Usage:
    python experiments/scripts/06_eval_temporal.py
    python experiments/scripts/06_eval_temporal.py --system oida-core
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import eval_common as ec  # noqa: E402

CUTOFFS = {
    "org-consulting-clearpath": ["2025-09-30", "2025-11-01", "2025-12-15"],
    "org-iot-fireglass":         ["2025-08-31", "2025-09-30", "2025-10-31"],
    "org-vc-vertexminds":        ["2025-10-31", "2025-11-10", "2025-11-20"],
}

OBSOLETE_STATES = {"SUPERSEDED", "RETRACTED", "ARCHIVED", "STALE"}
PRIORITY = {  # higher = should rank earlier
    "CANONICAL": 6, "ACTIVE": 5, "PROVISIONAL": 4, "STALE": 3,
    "SUPERSEDED": 2, "ARCHIVED": 1, "RETRACTED": 0,
}

F_TEMP = {
    "F-TEMP-1": (0.80, "ge"), "F-TEMP-2": (0.10, "le"), "F-TEMP-4": (0.75, "ge"),
    "F-TEMP-5": (0.15, "le"), "F-TEMP-6": (0.70, "ge"),
}
F_TEMP7_THRESHOLD = 0.10  # TemporalNDCG@10(B2 full-OIDA) − (B0 similarity-only) ≥ 0.10


def _ranking_by_component(recs: dict, qid: str, field: str) -> list[str]:
    """Re-rank a query's docs by one score_components field (OIDA B0/B2 ablation).

    field='similarity' → B0 (similarity-only); field='regime_adjusted_score' → B2
    (full OIDA). Returns [] when components are unavailable for the query.
    """
    sc = (recs.get(qid, {}) or {}).get("score_components") or {}
    scored = {d: (comp or {}).get(field) for d, comp in sc.items()}
    scored = {d: v for d, v in scored.items() if isinstance(v, (int, float))}
    return [d for d, _ in sorted(scored.items(), key=lambda kv: -kv[1])]


def _temporal_gains(spec: dict) -> dict[str, int]:
    gains: dict[str, int] = {}
    for d in (spec.get("gold_current_docs") or []): gains[d] = 3
    for d in (spec.get("gold_stable_docs") or []): gains.setdefault(d, 2)
    for d in (spec.get("gold_historical_docs") or []): gains.setdefault(d, 1)
    for d in (spec.get("gold_superseded_docs") or []): gains.setdefault(d, 0)
    for d in (spec.get("gold_should_not_retrieve") or []): gains[d] = 0
    return gains


def _ndcg_graded(ranked: list[str], gains: dict[str, int], k: int) -> float:
    dcg = sum((2 ** gains.get(d, 0) - 1) / math.log2(i + 1)
              for i, d in enumerate(ranked[:k], start=1) if gains.get(d, 0) > 0)
    ideal = sorted(gains.values(), reverse=True)[:k]
    idcg = sum((2 ** g - 1) / math.log2(i + 1) for i, g in enumerate(ideal, start=1) if g > 0)
    return dcg / idcg if idcg > 0 else 0.0


def score(corpus, system, lifecycle, tqs, docs):
    runs = ec.load_runs(corpus, system)
    if runs is None:
        return None
    recs = ec.load_retrieve_records(corpus, system)
    def state(d): return (lifecycle.get(d, {}) or {}).get("lifecycle_state", "ACTIVE")

    cs_q = {q: s for q, s in tqs.items() if s.get("temporal_intent") == "CURRENT_STATE"}
    stable_q = {q: s for q, s in tqs.items() if s.get("gold_stable_docs")}

    # T1 current-state accuracy@k
    csa = {}
    for k in (1, 5, 10):
        if not cs_q:
            csa[k] = None
            continue
        hit = 0
        for q, s in cs_q.items():
            topk = set(ec.ranked(runs.get(q, {}))[:k])
            gold = set(s.get("gold_current_docs") or [])
            if gold and topk & gold:
                hit += 1
        csa[k] = hit / len(cs_q)

    # T4 superseded leakage@10
    leaks = []
    for q, s in tqs.items():
        required = set((s.get("gold_current_docs") or []) + (s.get("gold_historical_docs") or [])
                       + (s.get("gold_stable_docs") or []))
        top10 = ec.ranked(runs.get(q, {}))[:10]
        if not top10:
            continue
        obsolete = sum(1 for d in top10
                       if (state(d) in OBSOLETE_STATES or d in set(s.get("gold_superseded_docs") or []))
                       and d not in required)
        leaks.append(obsolete / 10.0)
    t4 = (sum(leaks) / len(leaks)) if leaks else None

    # T6 temporal NDCG@10 (shifted gains) — main (B2) ranking
    ndcgs = []
    for q, s in tqs.items():
        gains = _temporal_gains(s)
        if not any(gains.values()):
            continue
        ndcgs.append(_ndcg_graded(ec.ranked(runs.get(q, {})), gains, 10))
    t6 = (sum(ndcgs) / len(ndcgs)) if ndcgs else None

    # F-TEMP-7 — B2 (full OIDA, regime_adjusted) vs B0 (similarity-only), from the
    # same run's per-doc score_components. OIDA deploys only (baselines expose no
    # comparable similarity/composite split). No re-ingest / time-slice needed.
    #
    # P3-S2 adds a NEW B3 diagnostic alongside (NOT replacing) B0/B2: temporal NDCG
    # under a recency/decay-aware re-rank (score_components.recency_adjusted_score =
    # oida-core max(0, similarity × decayScore)). It is a separate metric key
    # (temporal_ndcg_at_10_b3_recency); F-TEMP-7's locked B2−B0 threshold is untouched.
    # GRACEFUL DEGRADE: when the engine lacks the field (pre-deploy, live=6962929) the
    # per-doc recency values are uniformly 0.0 → _ranking_by_component is a flat tie
    # over a constant → t6_b3 is a flat/degenerate number, NOT a crash. (Reads null
    # when components are entirely absent.) NO new tuned constant.
    t6_b0 = t6_b2 = ftemp7 = t6_b3 = None
    if system in ec.OIDA_SYSTEMS and recs:
        b0s, b2s, b3s = [], [], []
        for q, s in tqs.items():
            gains = _temporal_gains(s)
            if not any(gains.values()):
                continue
            r_b0 = _ranking_by_component(recs, q, "similarity")
            r_b2 = _ranking_by_component(recs, q, "regime_adjusted_score")
            r_b3 = _ranking_by_component(recs, q, "recency_adjusted_score")
            if r_b0:
                b0s.append(_ndcg_graded(r_b0, gains, 10))
            if r_b2:
                b2s.append(_ndcg_graded(r_b2, gains, 10))
            if r_b3:
                b3s.append(_ndcg_graded(r_b3, gains, 10))
        t6_b0 = (sum(b0s) / len(b0s)) if b0s else None
        t6_b2 = (sum(b2s) / len(b2s)) if b2s else None
        t6_b3 = (sum(b3s) / len(b3s)) if b3s else None
        if t6_b0 is not None and t6_b2 is not None:
            ftemp7 = t6_b2 - t6_b0

    # ndcg_at_10_per_cutoff — diagnostic. Doc-level retrieve-time-filter
    # approximation of the spec's re-ingested time slices: at cutoff t we mask
    # both the ranking and the gold gains to docs with metadata.created <= t.
    # (True per-slice re-ingest was infeasible on the live deploys within budget;
    # this measures ranking quality restricted to the time-appropriate universe.)
    def created(d): return docs.get(d, {}).get("created") or "9999-12-31"
    per_cutoff = []
    for cut in CUTOFFS.get(corpus, []):
        vals = []
        for q, s in tqs.items():
            gains = {d: g for d, g in _temporal_gains(s).items() if created(d) <= cut}
            if not any(gains.values()):
                continue
            rk = [d for d in ec.ranked(runs.get(q, {})) if created(d) <= cut]
            vals.append(_ndcg_graded(rk, gains, 10))
        per_cutoff.append((sum(vals) / len(vals)) if vals else None)
    while len(per_cutoff) < 3:
        per_cutoff.append(None)

    # T9 stable knowledge retention@10
    rets = []
    for q, s in stable_q.items():
        gold = s.get("gold_stable_docs") or []
        if not gold:
            continue
        top10 = set(ec.ranked(runs.get(q, {}))[:10])
        rets.append(sum(1 for d in gold if d in top10) / len(gold))
    t9 = (sum(rets) / len(rets)) if rets else None

    # T10 freshness overbias rate (over stable-knowledge queries)
    overbias = 0
    for q, s in stable_q.items():
        rk = ec.ranked(runs.get(q, {}))
        gold = s.get("gold_stable_docs") or []
        gold_ranks = [rk.index(d) for d in gold if d in rk]
        if not gold_ranks:
            continue
        best_gold_pos = min(gold_ranks)
        best_gold_created = max((docs.get(d, {}).get("created") or "") for d in gold)
        # a non-gold doc, newer than the gold, ranked above it
        flag = any(
            d not in gold
            and (docs.get(d, {}).get("created") or "") > best_gold_created
            and i < best_gold_pos
            for i, d in enumerate(rk[:best_gold_pos])
        )
        if flag:
            overbias += 1
    t10 = (overbias / len(stable_q)) if stable_q else None

    # T11 lifecycle ranking agreement (pairwise, over top-20 retrieved with a state)
    consistent = 0
    comparable = 0
    for q in tqs:
        rk = [d for d in ec.ranked(runs.get(q, {}))[:20] if d in lifecycle]
        for i in range(len(rk)):
            for j in range(i + 1, len(rk)):
                pi, pj = PRIORITY.get(state(rk[i]), 5), PRIORITY.get(state(rk[j]), 5)
                if pi == pj:
                    continue
                comparable += 1
                if pi > pj:  # higher priority ranked earlier → consistent
                    consistent += 1
    t11 = (consistent / comparable) if comparable else None

    block = {
        "cutoffs": CUTOFFS.get(corpus, []),
        "ndcg_at_10_per_cutoff": per_cutoff,
        "temporal_ndcg_at_10_b0_similarity": t6_b0,
        "temporal_ndcg_at_10_b2_full_oida": t6_b2,
        "temporal_ndcg_lift_b2_minus_b0": ftemp7,
        # P3-S2 — NEW recency-ranked diagnostic (B3); separate key, no F-condition,
        # does not touch the locked F-TEMP-7 B2−B0 threshold. null/flat when the
        # recency component is uniform/absent (pre-deploy graceful degrade).
        "temporal_ndcg_at_10_b3_recency": t6_b3,
        "current_state_accuracy_at_1": csa[1],
        "current_state_accuracy_at_5": csa[5],
        "current_state_accuracy_at_10": csa[10],
        "superseded_leakage_at_10": t4,
        "temporal_ndcg_at_10": t6,
        "stable_knowledge_retention_at_10": t9,
        "freshness_overbias_rate": t10,
        "lifecycle_ranking_agreement": t11,
        "as_of_accuracy_at_10": None,
        "decay_sensitivity_pairwise": None,
        "reinforcement_lift_mean": None,
        "n_current_state_queries": len(cs_q),
        "n_stable_knowledge_queries": len(stable_q),
    }
    fconds = {}
    metric_for = {
        "F-TEMP-1": csa[10], "F-TEMP-2": t4, "F-TEMP-4": t9,
        "F-TEMP-5": t10, "F-TEMP-6": t11,
    }
    for fid, (thr, direction) in F_TEMP.items():
        v = metric_for[fid]
        passed = None if v is None else (v >= thr if direction == "ge" else v <= thr)
        fconds[fid] = {"passed": passed, "value": v, "threshold": thr}
    # F-TEMP-7 — OIDA-only lift of full salience over similarity-only
    fconds["F-TEMP-7"] = {
        "passed": (ftemp7 >= F_TEMP7_THRESHOLD) if ftemp7 is not None else None,
        "value": (round(ftemp7, 4) if ftemp7 is not None else None),
        "threshold": F_TEMP7_THRESHOLD,
        "b2_full_oida": (round(t6_b2, 4) if t6_b2 is not None else None),
        "b0_similarity": (round(t6_b0, 4) if t6_b0 is not None else None),
    }
    return block, fconds


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("corpora", nargs="*")
    p.add_argument("--system", choices=ec.SYSTEMS)
    args = p.parse_args(argv)

    corpora = [c for c in (args.corpora or ec.ORG_CORPORA) if c in ec.ORG_CORPORA]
    systems = [args.system] if args.system else ec.SYSTEMS

    rows = []
    for corpus in corpora:
        lifecycle = ec.load_annotation("lifecycle", corpus)
        tqs = ec.load_annotation("temporal_queries", corpus)
        if lifecycle is None or tqs is None:
            for system in systems:
                rows.append((corpus, system, None, "missing lifecycle/temporal_queries annotation"))
            continue
        docs = ec.load_corpus_docs(corpus)
        for system in systems:
            res = score(corpus, system, lifecycle, tqs, docs)
            if res is None:
                continue
            block, fconds = res
            path = ec.resolve_result_file(corpus, system)
            if path is None:
                rows.append((corpus, system, None, "NO RESULT FILE"))
                continue
            result = ec.load_result(path)
            result["layer_4_temporal"] = block
            result.setdefault("f_conditions", {}).update(fconds)
            ec.save_result(path, result)
            rows.append((corpus, system, block, "wrote"))

    print("\n===================== LAYER 4 — TEMPORAL =====================")
    print(f"{'corpus':<24s} {'system':<16s} CSA@10  SupLeak  TmpNDCG  StableRet  Fresh  LifeRank")
    for corpus, system, b, status in rows:
        if b is None:
            print(f"{corpus:<24s} {system:<16s} -- {status}")
            continue
        print(
            f"{corpus:<24s} {system:<16s} "
            f"{ec.fmt(b['current_state_accuracy_at_10']):>6s}  {ec.fmt(b['superseded_leakage_at_10']):>6s}  "
            f"{ec.fmt(b['temporal_ndcg_at_10']):>6s}  {ec.fmt(b['stable_knowledge_retention_at_10']):>8s}  "
            f"{ec.fmt(b['freshness_overbias_rate']):>5s}  {ec.fmt(b['lifecycle_ranking_agreement']):>6s}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
