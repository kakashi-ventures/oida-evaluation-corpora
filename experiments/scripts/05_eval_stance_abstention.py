#!/usr/bin/env python3
"""Layer 3 — stance & abstention scoring (EXPERIMENT_PLAN.md §5.3).

For each stance-evaluable query, the system's *answer* is judged by gpt-4o into
{SUPPORTS, CONTRADICTS, NEUTRAL, ABSTAIN, INVALID}. The "answer" is the text of
the system's top-1 retrieved doc, fed identically for every system (OIDA /
GraphRAG / LightRAG / HippoRAG) — no prose shortcut, so the judge sees the same
input KIND for all systems (P0-S4), per §5.3.

Gold stance (S / C / NEI) comes from annotations/stance_gold/<corpus>.json.
Broad abstention (NEUTRAL ∪ ABSTAIN) is used for the abstention metrics (§4.1).

Judge calls are cached to experiments/output/stance_judge_cache.json keyed by
(model, query, answer-hash), so re-runs are free and deterministic.

Usage:
    python experiments/scripts/05_eval_stance_abstention.py --run            # calls gpt-4o
    python experiments/scripts/05_eval_stance_abstention.py --dry-run        # no API; writes nulls
    python experiments/scripts/05_eval_stance_abstention.py --run --system oida-core
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import eval_common as ec  # noqa: E402
from stance import metric_b_stance_recall as mb  # noqa: E402  (headline metric (b), P0-S5)

JUDGE_MODEL = "gpt-4o"
ANSWER_CHARS = 2000
CACHE_PATH = ec.REPO_ROOT / "experiments" / "output" / "stance_judge_cache.json"
ABSTENTION_H5_PATH = ec.REPO_ROOT / "experiments" / "output" / "abstention_h5.json"

# Hypothesis H5 — the four pre-registered abstention F-conditions (plan §4).
# Pooled per system over ALL stance-gold queries (per-corpus n is too small).
F_ABSTAIN = {
    "F-ABSTAIN-1": ("false_commitment_rate", 0.10, "le"),
    "F-ABSTAIN-2": ("epistemic_abstention_accuracy", 0.80, "ge"),
    "F-ABSTAIN-3": ("selective_stance_precision", 0.75, "ge"),
    "F-ABSTAIN-4": ("false_ignorance_rate", 0.20, "le"),
}

NORMALIZE = {
    "SUPPORTS": "SUPPORTS", "SUPPORT": "SUPPORTS",
    "CONTRADICTS": "CONTRADICTS", "REFUTES": "CONTRADICTS",
    "NEI": "NEUTRAL", "NEUTRAL": "NEUTRAL", "NO_EVIDENCE": "NEUTRAL",
    "UNCLEAR": "ABSTAIN", "ABSTAIN": "ABSTAIN",
    "EMPTY": "INVALID", "ERROR": "INVALID", "INVALID": "INVALID",
}

JUDGE_SYSTEM = (
    "You are a strict evaluation judge for an information-retrieval experiment. "
    "Given a QUESTION and a SYSTEM ANSWER (which may be a retrieved document), "
    "classify the stance the SYSTEM ANSWER takes toward the question's claim into "
    "exactly one label: SUPPORTS (answer affirms the claim/states it holds), "
    "CONTRADICTS (answer refutes the claim or surfaces conflicting evidence), "
    "NEUTRAL (answer is on-topic but does not settle the claim / says evidence is "
    "insufficient), ABSTAIN (answer declines or is too vague to take any stance), "
    "INVALID (empty or unintelligible). Reply with ONLY the single label word."
)


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _answer_for(system: str, qid: str, recs: dict, docs: dict, runs: dict) -> str:
    # P0-S4: every system's answer is its top-1 retrieved doc text — fed
    # identically for all systems. The prior GraphRAG-only `raw_response_text`
    # prose shortcut is removed so the judge sees the same input KIND for every
    # system (no prose-vs-doc asymmetry). Feeding prose drawn from the top-k for
    # *all* systems is a separate change (P0-S5); `recs` stays in the signature
    # for that follow-up.
    top = ec.ranked(runs.get(qid, {}))
    if top:
        d = docs.get(top[0], {})
        return (d.get("title", "") + "\n" + d.get("text", ""))[:ANSWER_CHARS]
    return ""


def _judge(client, query: str, answer: str, cache: dict) -> str:
    if not answer.strip():
        return "INVALID"
    key = hashlib.sha256(f"{JUDGE_MODEL}\0{query}\0{answer}".encode()).hexdigest()
    if key in cache:
        return cache[key]
    resp = client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=0,
        max_tokens=16,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": f"QUESTION:\n{query}\n\nSYSTEM ANSWER:\n{answer}\n\nLabel:"},
        ],
    )
    raw = (resp.choices[0].message.content or "").strip().upper()
    label = NORMALIZE.get(raw.split()[0] if raw.split() else "EMPTY", "INVALID")
    cache[key] = label
    return label


def _metrics(judged: list[tuple[str, str]]) -> dict:
    """judged = list of (gold ∈ {SUPPORTS,CONTRADICTS,NEI}, pred_norm)."""
    n = len(judged)
    if n == 0:
        return {k: None for k in (
            "stance_accuracy", "stance_macro_f1", "contradiction_recall", "stance_coverage",
            "epistemic_abstention_accuracy", "false_commitment_rate", "false_ignorance_rate",
            "selective_stance_precision", "abstention_commitment_balance", "epistemic_risk_score")} | {
            # P0-S5: stance_accuracy is RETIRED as the headline (replaced by metric
            # (b) stance_evidence_recall) but its key stays populated for 08_report
            # back-compat; this status flag marks it diagnostic-only.
            "stance_accuracy_status": "retired/diagnostic-only",
            "n_gold_nei": 0, "n_false_commitments": 0, "n_false_ignorance": 0,
            "n_non_neutral_predictions": 0}

    def abstain(p): return p in ("NEUTRAL", "ABSTAIN")
    def committed(p): return p in ("SUPPORTS", "CONTRADICTS")

    def correct(g, p):
        if g == "NEI":
            return abstain(p)
        return p == g

    n_correct = sum(1 for g, p in judged if correct(g, p))
    coverage = sum(1 for _, p in judged if p != "INVALID") / n

    gold_nei = [(g, p) for g, p in judged if g == "NEI"]
    gold_sc = [(g, p) for g, p in judged if g in ("SUPPORTS", "CONTRADICTS")]
    gold_c = [(g, p) for g, p in judged if g == "CONTRADICTS"]

    eaa = (sum(1 for _, p in gold_nei if abstain(p)) / len(gold_nei)) if gold_nei else None
    fcr = (sum(1 for _, p in gold_nei if committed(p)) / len(gold_nei)) if gold_nei else None
    fir = (sum(1 for _, p in gold_sc if abstain(p)) / len(gold_sc)) if gold_sc else None
    contra_recall = (sum(1 for _, p in gold_c if p == "CONTRADICTS") / len(gold_c)) if gold_c else None

    committed_preds = [(g, p) for g, p in judged if committed(p)]
    ssp = (sum(1 for g, p in committed_preds if p == g) / len(committed_preds)) if committed_preds else None

    # macro-F1 over {SUPPORTS, CONTRADICTS, NEI}; pred bucket: abstain→NEI, INVALID→none
    def pred_bucket(p):
        if committed(p):
            return p
        if abstain(p):
            return "NEI"
        return "INVALID"
    f1s = []
    for cls in ("SUPPORTS", "CONTRADICTS", "NEI"):
        tp = sum(1 for g, p in judged if g == cls and pred_bucket(p) == cls)
        fp = sum(1 for g, p in judged if g != cls and pred_bucket(p) == cls)
        fn = sum(1 for g, p in judged if g == cls and pred_bucket(p) != cls)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    macro_f1 = sum(f1s) / len(f1s)

    acb = (ssp - fir) if (ssp is not None and fir is not None) else None
    ers = None
    if fcr is not None and fir is not None and contra_recall is not None:
        ers = 0.5 * fcr + 0.25 * fir + 0.25 * (1 - contra_recall)

    return {
        "stance_accuracy": n_correct / n,
        # P0-S5: RETIRED as headline (see metric (b) stance_evidence_recall); key
        # kept populated for 08_report back-compat, flagged diagnostic-only.
        "stance_accuracy_status": "retired/diagnostic-only",
        "stance_macro_f1": macro_f1,
        "contradiction_recall": contra_recall,
        "stance_coverage": coverage,
        "epistemic_abstention_accuracy": eaa,
        "false_commitment_rate": fcr,
        "false_ignorance_rate": fir,
        "selective_stance_precision": ssp,
        "abstention_commitment_balance": acb,
        "epistemic_risk_score": ers,
        "n_gold_nei": len(gold_nei),
        "n_false_commitments": sum(1 for _, p in gold_nei if committed(p)),
        "n_false_ignorance": sum(1 for _, p in gold_sc if abstain(p)),
        "n_non_neutral_predictions": len(committed_preds),
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("corpora", nargs="*")
    p.add_argument("--system", choices=ec.SYSTEMS)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--run", action="store_true", help="call the gpt-4o judge (costs money)")
    g.add_argument("--dry-run", action="store_true", help="no API; writes null metrics")
    args = p.parse_args(argv)

    corpora = args.corpora or ec.ALL_CORPORA
    systems = [args.system] if args.system else ec.SYSTEMS

    client = None
    cache = _load_cache()
    if args.run:
        from openai import OpenAI  # noqa: E402
        sys.path.insert(0, str(ec.REPO_ROOT / "experiments"))
        from adapters.oida import _load_env  # noqa: E402
        env = _load_env(ec.REPO_ROOT / ".env")
        key = env.get("OPENAI_API_KEY")
        if not key:
            print("error: OPENAI_API_KEY missing from .env")
            return 2
        client = OpenAI(api_key=key)

    from collections import defaultdict
    per_system_judged: dict[str, list] = defaultdict(list)

    rows = []
    for corpus in corpora:
        stance_gold = ec.load_annotation("stance_gold", corpus)
        if stance_gold is None:
            for system in systems:
                rows.append((corpus, system, None, "no stance_gold annotation"))
            continue
        evaluable = {q: g["gold_stance"] for q, g in stance_gold.items()
                     if g.get("stance_evaluable") and g.get("gold_stance")}
        docs = ec.load_corpus_docs(corpus)
        queries = ec.load_queries(corpus)

        # P0-S5: HEADLINE metric (b) — Stance-Evidence Recall@k. Pure retrieval,
        # no judge/key, so it runs in both --run and --dry-run. Computed ONCE per
        # corpus (independent of the judge) and stamped onto each system block.
        brep = mb.stance_recall_for_corpus(corpus, ks=[5, 10])

        def _attach_stance_metrics(block: dict, system: str) -> dict:
            # (b) headline: did top-k surface the gold stance-bearing docs?
            block["stance_evidence_recall"] = {
                "headline": True,
                "proxy_label": brep["proxy_label"],
                "ks": brep["ks"],
                "n_sc_queries": brep["n_sc_queries"],
                "n_nei_excluded": brep["n_nei_excluded"],
                **brep["systems"].get(system, {}),
            }
            # (a) secondary slot: evidence-grounded stance (LLM-judged). Requires a
            # judge key; structural placeholder here, NOT run in the offline gate.
            block["evidence_grounded_stance"] = {
                "headline": False,
                "status": "secondary; requires OPENAI_API_KEY; not run in gate",
                "values": None,
            }
            return block

        for system in systems:
            runs = ec.load_runs(corpus, system)
            if runs is None:
                continue
            recs = ec.load_retrieve_records(corpus, system)
            if args.dry_run:
                block = _attach_stance_metrics(_metrics([]), system)
                ec.update_layer(corpus, system, "layer_3_stance_abstention", block)
                rows.append((corpus, system, block, "dry-run (null)"))
                continue
            judged = []
            for qid, gold in evaluable.items():
                ans = _answer_for(system, qid, recs, docs, runs)
                pred = _judge(client, queries.get(qid, {}).get("text", ""), ans, cache)
                judged.append((gold, pred))
            _save_cache(cache)
            per_system_judged[system].extend(judged)
            block = _attach_stance_metrics(_metrics(judged), system)
            ec.update_layer(corpus, system, "layer_3_stance_abstention", block)
            rows.append((corpus, system, block, f"judged {len(judged)}"))

    # H5 — pooled-per-system abstention F-conditions, written for 08 to stamp.
    # Only (re)write when this was a full run (all corpora + all systems), so a
    # partial invocation can't clobber the pooled file with a subset.
    if not args.dry_run and per_system_judged and not args.corpora and not args.system:
        h5 = {}
        for system, judged in per_system_judged.items():
            m = _metrics(judged)
            conds = {}
            for fid, (metric, thr, direction) in F_ABSTAIN.items():
                v = m.get(metric)
                passed = None if v is None else (v >= thr if direction == "ge" else v <= thr)
                conds[fid] = {"passed": passed, "value": (round(v, 4) if isinstance(v, float) else v),
                              "threshold": thr}
            conds["_pooled_n"] = len(judged)
            conds["_n_gold_nei"] = m.get("n_gold_nei")
            h5[system] = conds
        ABSTENTION_H5_PATH.write_text(json.dumps(h5, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nwrote pooled H5 abstention F-conditions → {ABSTENTION_H5_PATH.relative_to(ec.REPO_ROOT)}")

    print("\n===================== LAYER 3 — STANCE & ABSTENTION =====================")
    print(f"{'corpus':<26s} {'system':<16s} acc    mF1    EAA    FCR    FIR    SSP    (n_nei) {'':<4s}status")
    for corpus, system, b, status in rows:
        if b is None:
            print(f"{corpus:<26s} {system:<16s} -- {status}")
            continue
        print(
            f"{corpus:<26s} {system:<16s} "
            f"{ec.fmt(b['stance_accuracy']):>5s}  {ec.fmt(b['stance_macro_f1']):>5s}  "
            f"{ec.fmt(b['epistemic_abstention_accuracy']):>5s}  {ec.fmt(b['false_commitment_rate']):>5s}  "
            f"{ec.fmt(b['false_ignorance_rate']):>5s}  {ec.fmt(b['selective_stance_precision']):>5s}  "
            f"({b['n_gold_nei']})  {status}"
        )

    # P0-S5 — HEADLINE stance metric is now (b) Stance-Evidence Recall@k.
    # (a) evidence-grounded stance is a secondary slot (judge-gated, not run
    # offline); the old LLM-judged stance_accuracy is RETIRED (diagnostic-only).
    print("\n================ STANCE HEADLINE: (b) Stance-Evidence Recall@k ================")
    printed_proxy = False
    print(f"{'corpus':<26s} {'system':<16s} {'(b) recall_any@10':<20s} {'(a) evidence-grounded':<24s} (old stance_acc)")
    for corpus, system, b, status in rows:
        if b is None:
            print(f"{corpus:<26s} {system:<16s} -- {status}")
            continue
        ser = b.get("stance_evidence_recall", {})
        if not printed_proxy and ser.get("proxy_label"):
            print(f"stance docs: {ser['proxy_label']}")
            printed_proxy = True
        recall_any10 = ser.get(10, {}).get("stance_recall_any") if isinstance(ser.get(10), dict) else None
        print(
            f"{corpus:<26s} {system:<16s} "
            f"{ec.fmt(recall_any10) + ' [HEADLINE]':<20s} "
            f"{'secondary-gated':<24s} "
            f"{ec.fmt(b['stance_accuracy'])} [RETIRED/diagnostic]"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
