#!/usr/bin/env python3
"""Layer 3 — stance & abstention scoring (EXPERIMENT_PLAN.md §5.3).

For each stance-evaluable query, the system's *answer* is judged by gpt-4o into
{SUPPORTS, CONTRADICTS, NEUTRAL, ABSTAIN, INVALID}. The "answer" is the system's
raw response text when it produces one (GraphRAG), otherwise the text of its
top-1 retrieved doc (OIDA / LightRAG / HippoRAG) — per §5.3.

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
    rec = recs.get(qid, {})
    raw = rec.get("raw_response_text")
    if raw:
        return raw[:ANSWER_CHARS]
    # fall back to top-1 retrieved doc text
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
        max_tokens=4,
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
        for system in systems:
            runs = ec.load_runs(corpus, system)
            if runs is None:
                continue
            recs = ec.load_retrieve_records(corpus, system)
            if args.dry_run:
                block = _metrics([])
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
            block = _metrics(judged)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
