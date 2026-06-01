#!/usr/bin/env python3
"""Metric (a): Evidence-Grounded Stance Accuracy — generation held constant.

Prototype for the stance-metric redesign (read-only diagnostic). Does NOT touch
oida-core, the scored Layer-3 pipeline, or any result JSON. New artifacts only.

Idea
----
The shipped Layer-3 metric judges GraphRAG on the prose it generates and the
doc-returning systems (OIDA / LightRAG / HippoRAG) on the raw text of their
*top-1* doc. So it measures "did the system argue a position", not "did the
system retrieve the evidence to argue it". This metric removes that confound:

    every system's top-k retrieved docs  ->  ONE fixed reader LLM  ->  answer
    answer  ->  the stance judge  ->  {SUPPORTS,CONTRADICTS,NEUTRAL,ABSTAIN,INVALID}

Generation (reader model + prompt + k + per-doc budget) is identical across all
five systems; only the retrieved documents differ.

The judge prompt / model / normalisation are imported verbatim from
05_eval_stance_abstention.py. The ONE change: max_tokens is raised from 4 to 12.
The shipped value (4) truncates "CONTRADICTS" (5 tokens under o200k_base) to
"CONTRADICT", which the normaliser maps to INVALID -- so the shipped judge never
records a single contradiction (0 / 181 cached judgements). Raising max_tokens
lets the judge emit the labels it was designed to emit; nothing else changes.

Four-way decomposition (all on the same evaluable queries):
    OLD               published metric (top-1 doc / prose, max_tokens=4 judge)
    OLD + fix-judge   re-judge the SAME old answers with the label-complete judge
                      -> isolates the max_tokens truncation bug
    a@k1              fixed reader over each system's top-1 doc, label-complete judge
                      -> isolates the GENERATION confound (depth matched to old)
    a@k10             fixed reader over each system's top-10 docs
                      -> adds retrieval depth

Usage:
    python .../metric_a_evidence_grounded.py --run --k 1 10
    python .../metric_a_evidence_grounded.py --run --smoke
    python .../metric_a_evidence_grounded.py --recover-only   # OLD preds from cache, no API
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]            # experiments/scripts
sys.path.insert(0, str(SCRIPTS))
import eval_common as ec  # noqa: E402

# ---- import the SHIPPED stance scorer (judge prompt + metrics) verbatim ----
_spec = importlib.util.spec_from_file_location("stance05", SCRIPTS / "05_eval_stance_abstention.py")
stance05 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(stance05)  # side-effect-free at import (main is __main__-guarded)

READER_MODEL = "gpt-4o"          # fixed generator, identical for ALL systems
JUDGE_MODEL = stance05.JUDGE_MODEL
JUDGE_MAXTOK = 12                # shipped=4 truncates "CONTRADICTS"->INVALID; see module docstring
PERDOC_CHARS = 1200              # per-doc text budget fed to the reader
SCORED_CACHE = ec.REPO_ROOT / "experiments" / "output" / "stance_judge_cache.json"
OUT_DIR = ec.REPO_ROOT / "experiments" / "output" / "stance_redesign"
CACHE_PATH = OUT_DIR / "metric_a_cache.json"             # our own cache; scored cache untouched

READER_SYSTEM = (
    "You are a careful research assistant answering a question using ONLY the provided "
    "DOCUMENTS, which are evidence retrieved for the question. Base every statement on the "
    "documents and do not use outside knowledge. If the documents affirm the claim in the "
    "question, say so and cite the grounds. If they refute it or contain conflicting evidence, "
    "say so and surface the conflict. If the documents do not contain enough information to "
    "settle the question, say the evidence is insufficient. Answer in 2-5 sentences."
)


def load_env(path: Path) -> dict:
    env = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_cache(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_cache(p: Path, c: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")


def build_context(topk: list[str], docs: dict) -> str:
    parts = []
    for i, did in enumerate(topk, 1):
        d = docs.get(did, {})
        body = (d.get("text", "") or "")[:PERDOC_CHARS]
        parts.append(f"[{i}] {d.get('title','')}\n{body}")
    return "\n\n".join(parts)


def reader_answer(client, query: str, context: str, cache: dict) -> str:
    if not context.strip():
        return ""
    key = "reader\0" + hashlib.sha256(
        f"{READER_MODEL}\0{READER_SYSTEM}\0{query}\0{context}".encode()).hexdigest()
    if key in cache:
        return cache[key]
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=READER_MODEL, temperature=0, max_tokens=320,
                messages=[
                    {"role": "system", "content": READER_SYSTEM},
                    {"role": "user", "content": f"QUESTION:\n{query}\n\nDOCUMENTS:\n{context}\n\nANSWER:"},
                ],
            )
            ans = (resp.choices[0].message.content or "").strip()
            cache[key] = ans
            return ans
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                print(f"  reader error (giving up): {e}", file=sys.stderr, flush=True)
                return ""
            time.sleep(2 * (attempt + 1))


def judge_fixed(client, query: str, answer: str, cache: dict) -> str:
    """Identical to stance05._judge (same prompt/model/normalise) but max_tokens=12."""
    if not answer.strip():
        return "INVALID"
    key = "judgefix\0" + hashlib.sha256(
        f"{JUDGE_MODEL}\0{JUDGE_MAXTOK}\0{query}\0{answer}".encode()).hexdigest()
    if key in cache:
        return cache[key]
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=JUDGE_MODEL, temperature=0, max_tokens=JUDGE_MAXTOK,
                messages=[
                    {"role": "system", "content": stance05.JUDGE_SYSTEM},
                    {"role": "user", "content": f"QUESTION:\n{query}\n\nSYSTEM ANSWER:\n{answer}\n\nLabel:"},
                ],
            )
            raw = (resp.choices[0].message.content or "").strip().upper()
            label = stance05.NORMALIZE.get(raw.split()[0] if raw.split() else "EMPTY", "INVALID")
            cache[key] = label
            return label
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                print(f"  judge error (giving up): {e}", file=sys.stderr, flush=True)
                return "INVALID"
            time.sleep(2 * (attempt + 1))


def old_answers(corpus: str, system: str, evaluable: dict, docs: dict):
    """Replay the shipped _answer_for to get each system's OLD answer string + the
    published (cached, max_tokens=4) label. NO API."""
    runs = ec.load_runs(corpus, system)
    recs = ec.load_retrieve_records(corpus, system)
    queries = ec.load_queries(corpus)
    scored_cache = load_cache(SCORED_CACHE)
    rows = []
    for qid, gold in evaluable.items():
        ans = stance05._answer_for(system, qid, recs, docs, runs)
        q = queries.get(qid, {}).get("text", "")
        if ans.strip():
            key = hashlib.sha256(f"{JUDGE_MODEL}\0{q}\0{ans}".encode()).hexdigest()
            old_pred = scored_cache.get(key)
        else:
            old_pred = "INVALID"
        rows.append({"qid": qid, "gold": gold, "query": q, "answer": ans, "old_pred": old_pred})
    return rows


def run_metric_a(corpora, systems, ks, client, cache):
    report = {"metric": "evidence_grounded_stance_accuracy",
              "reader_model": READER_MODEL, "judge_model": JUDGE_MODEL,
              "judge_max_tokens": JUDGE_MAXTOK, "shipped_judge_max_tokens": 4,
              "perdoc_chars": PERDOC_CHARS, "ks": ks, "corpora": {}}
    cols = ["old", "old_fixjudge"] + [f"a_k{k}" for k in ks]
    pooled = {s: {c: [] for c in cols} for s in systems}

    for corpus in corpora:
        sg = ec.load_annotation("stance_gold", corpus) or {}
        evaluable = {q: g["gold_stance"] for q, g in sg.items()
                     if g.get("stance_evaluable") and g.get("gold_stance")}
        docs = ec.load_corpus_docs(corpus)
        queries = ec.load_queries(corpus)
        crep = {"n_evaluable": len(evaluable), "systems": {}}
        for s in systems:
            runs = ec.load_runs(corpus, s)
            if runs is None:
                continue
            srep = {"per_query": {q: {"gold": g} for q, g in evaluable.items()}}

            # OLD (published, cached) + OLD answers re-judged with the label-complete judge
            rows = old_answers(corpus, s, evaluable, docs)
            old_j, oldfix_j = [], []
            misses = 0
            for r in rows:
                qid, gold = r["qid"], r["gold"]
                if r["old_pred"] is None:
                    misses += 1
                else:
                    old_j.append((gold, r["old_pred"]))
                fix = judge_fixed(client, r["query"], r["answer"], cache)
                oldfix_j.append((gold, fix))
                srep["per_query"][qid]["old"] = r["old_pred"]
                srep["per_query"][qid]["old_fixjudge"] = fix
            save_cache(CACHE_PATH, cache)
            srep["old"] = stance05._metrics(old_j)
            srep["old_fixjudge"] = stance05._metrics(oldfix_j)
            srep["old_cache_misses"] = misses
            pooled[s]["old"].extend(old_j)
            pooled[s]["old_fixjudge"].extend(oldfix_j)

            # METRIC (a) for each k: fixed reader over top-k + label-complete judge
            for k in ks:
                judged = []
                for qid, gold in evaluable.items():
                    topk = ec.ranked(runs.get(qid, {}))[:k]
                    ctx = build_context(topk, docs)
                    q = queries.get(qid, {}).get("text", "")
                    ans = reader_answer(client, q, ctx, cache)
                    pred = judge_fixed(client, q, ans, cache)
                    judged.append((gold, pred))
                    srep["per_query"][qid][f"a_k{k}"] = pred
                    srep["per_query"][qid][f"a_k{k}_answer"] = ans
                save_cache(CACHE_PATH, cache)
                srep[f"a_k{k}"] = stance05._metrics(judged)
                pooled[s][f"a_k{k}"].extend(judged)

            crep["systems"][s] = srep
            line = (f"  {s:16s} old={ec.fmt(srep['old'].get('stance_accuracy'))}"
                    f"  old+fixJ={ec.fmt(srep['old_fixjudge'].get('stance_accuracy'))}")
            for k in ks:
                line += f"  a@k{k}={ec.fmt(srep[f'a_k{k}']['stance_accuracy'])}"
            if misses:
                line += f"  (old misses:{misses})"
            print(line, flush=True)
        report["corpora"][corpus] = crep
        print(f"[done] {corpus}", flush=True)

    report["per_system_pooled"] = {}
    for s in systems:
        report["per_system_pooled"][s] = {c: stance05._metrics(pooled[s][c]) for c in cols}
    return report


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--k", type=int, nargs="+", default=[1, 10])
    ap.add_argument("--smoke", action="store_true", help="1 corpus, oida-core+graphrag only")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--run", action="store_true", help="call the reader + judge (costs money)")
    g.add_argument("--recover-only", action="store_true", help="OLD preds from cache only, no API")
    args = ap.parse_args(argv)

    corpora = ec.ORG_CORPORA
    systems = ec.SYSTEMS
    if args.smoke:
        corpora = ["org-iot-fireglass"]
        systems = ["oida-core", "graphrag"]

    client = None
    cache = load_cache(CACHE_PATH)
    if args.run:
        from openai import OpenAI
        env = load_env(ec.REPO_ROOT / ".env")
        key = env.get("OPENAI_API_KEY")
        if not key:
            print("error: OPENAI_API_KEY missing from .env"); return 2
        client = OpenAI(api_key=key)
    elif not args.recover_only:
        print("specify --run or --recover-only"); return 2

    print(f"\n===== METRIC (a) EVIDENCE-GROUNDED STANCE ACCURACY =====", flush=True)
    print(f"reader={READER_MODEL}  judge={JUDGE_MODEL}(max_tokens {JUDGE_MAXTOK})  k={args.k}  "
          f"corpora={len(corpora)} systems={len(systems)}\n", flush=True)

    if args.recover_only:
        for corpus in corpora:
            sg = ec.load_annotation("stance_gold", corpus) or {}
            evaluable = {q: g["gold_stance"] for q, g in sg.items()
                         if g.get("stance_evaluable") and g.get("gold_stance")}
            docs = ec.load_corpus_docs(corpus)
            print(f"--- {corpus} (n={len(evaluable)}) ---")
            for s in systems:
                if ec.load_runs(corpus, s) is None:
                    continue
                rows = old_answers(corpus, s, evaluable, docs)
                m = stance05._metrics([(r["gold"], r["old_pred"]) for r in rows if r["old_pred"] is not None])
                print(f"  {s:16s} old_acc={ec.fmt(m['stance_accuracy'])} mf1={ec.fmt(m['stance_macro_f1'])}")
        return 0

    report = run_metric_a(corpora, systems, args.k, client, cache)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "metric_a_evidence_grounded.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n--- POOLED over org corpora (stance_accuracy) ---", flush=True)
    hdr = f"{'system':16s}  old    old+fixJ  " + "  ".join(f"a@k{k}" for k in args.k)
    print(hdr, flush=True)
    for s in systems:
        ps = report["per_system_pooled"][s]
        row = (f"{s:16s}  {ec.fmt(ps['old']['stance_accuracy'])}  {ec.fmt(ps['old_fixjudge']['stance_accuracy'])}   ")
        for k in args.k:
            row += f"  {ec.fmt(ps[f'a_k{k}']['stance_accuracy'])}"
        print(row, flush=True)
    print(f"\nwrote {out.relative_to(ec.REPO_ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
