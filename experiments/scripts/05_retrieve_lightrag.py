#!/usr/bin/env python3
"""Phase D — bulk LightRAG retrieve over all queries in all 5 corpora.

Async counterpart to 02_retrieve.py. Uses ``aquery_data`` (structured
retrieval, no LLM generation) and aggregates chunks/entities/relationships
to doc-level scores via the ``file_path`` set at ingest time.

Outputs to ``experiments/output/retrieve_runs/<corpus>/lightrag_<run_id>/``
matching the OIDA layout:
  runs.tsv         BEIR shape — qid\tdoc_id\tscore
  runs.json        {qid: {doc_id: score}}
  queries.jsonl    rich per-query record
  summary.json     aggregate stats

Usage:
    python experiments/scripts/05_retrieve_lightrag.py
    python experiments/scripts/05_retrieve_lightrag.py inv-mystery-redhood --run-id smoke
    python experiments/scripts/05_retrieve_lightrag.py --mode hybrid --top-k 20
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))

from adapters.lightrag import LightRagClient, _load_env  # noqa: E402

OUTPUT_ROOT = REPO_ROOT / "experiments" / "output" / "retrieve_runs"
DEFAULT_TOP_K = 20

CORPORA = [
    "org-consulting-clearpath",
    "org-iot-fireglass",
    "org-vc-vertexminds",
    "inv-mystery-redhood",
    "inv-ashford-mystery",
]


async def _retrieve_corpus(
    corpus_name: str,
    run_id: str,
    top_k: int,
    chunk_top_k: int,
    mode: str,
) -> dict:
    corpus_dir = REPO_ROOT / "corpora" / corpus_name
    if not corpus_dir.exists():
        print(f"  ! skip {corpus_name}: directory not found")
        return {"corpus": corpus_name, "skipped": True, "reason": "missing"}

    corpus_slug = corpus_name.split("-", 1)[-1] if "-" in corpus_name else corpus_name
    out_dir = OUTPUT_ROOT / corpus_name / f"lightrag_{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    with (corpus_dir / "queries.jsonl").open(encoding="utf-8") as fh:
        queries = [json.loads(line) for line in fh if line.strip()]

    # LightRAG normalizes file_paths to basenames at storage time. Build a
    # basename → full _id map from corpus.jsonl so the doc_scores keys
    # round-trip back to the BEIR qrels IDs.
    basename_to_id: dict[str, str] = {}
    with (corpus_dir / "corpus.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            doc = json.loads(line)
            full = doc["_id"]
            basename_to_id[full.split("/")[-1]] = full

    client = LightRagClient(corpus_slug=corpus_slug)
    await client.init()

    runs_beir: dict[str, dict[str, float]] = {}
    latencies: list[float] = []
    failures: list[str] = []
    t_start = time.perf_counter()
    print(f"\n[{corpus_name}] {len(queries)} queries | mode={mode} top_k={top_k} chunk_top_k={chunk_top_k}")
    try:
        with (out_dir / "queries.jsonl").open("w", encoding="utf-8") as fh_q:
            for i, q in enumerate(queries, 1):
                qid = q["_id"]
                qtext = q["text"]
                t_q = time.perf_counter()
                try:
                    res = await client.retrieve(
                        query=qtext, mode=mode, top_k=top_k, chunk_top_k=chunk_top_k,
                    )
                except Exception as e:  # noqa: BLE001
                    from adapters.lightrag import RetrieveResult
                    res = RetrieveResult(
                        doc_scores={}, score_components={}, raw_response_text=None,
                        latency_ms=(time.perf_counter() - t_q) * 1000.0,
                        notes=f"retrieve_error: {type(e).__name__}: {str(e)[:200]}",
                    )
                dt = time.perf_counter() - t_q
                latencies.append(res.latency_ms)
                # Translate basenames back to full BEIR _id where possible
                translated: dict[str, float] = {}
                unmatched = 0
                for k, v in res.doc_scores.items():
                    full = basename_to_id.get(k, k)
                    if full not in basename_to_id.values() and full == k:
                        unmatched += 1
                    translated[full] = max(translated.get(full, 0.0), v)
                runs_beir[qid] = translated
                res.doc_scores = translated
                rec = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "qid": qid,
                    "query": qtext,
                    "metadata": q.get("metadata", {}),
                    "top_k": top_k,
                    "chunk_top_k": chunk_top_k,
                    "mode": mode,
                    "doc_scores": res.doc_scores,
                    "score_components": res.score_components,
                    "latency_ms": res.latency_ms,
                    "tokens_in": res.tokens_in,
                    "tokens_out": res.tokens_out,
                    "embed_tokens": res.embed_tokens,
                    "notes": res.notes,
                }
                fh_q.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh_q.flush()
                ndocs = len(res.doc_scores)
                top1 = next(iter(res.doc_scores), None)
                if res.notes and "retrieve_error" in res.notes:
                    failures.append(qid); tag = "FAIL"
                elif not res.doc_scores:
                    tag = "EMPTY"
                else:
                    tag = "OK"
                print(
                    f"  [{i:3d}/{len(queries)}] {tag:5s} {qid:5s} docs={ndocs:3d} "
                    f"top1={(top1[:42]+'..') if top1 and len(top1)>42 else (top1 or '-'):44s} "
                    f"({dt:5.2f}s)"
                )
    finally:
        await client.close()

    elapsed = time.perf_counter() - t_start

    with (out_dir / "runs.tsv").open("w", encoding="utf-8") as fh:
        for qid, scores in runs_beir.items():
            for doc_id, score in sorted(scores.items(), key=lambda kv: -kv[1]):
                fh.write(f"{qid}\t{doc_id}\t{score}\n")
    with (out_dir / "runs.json").open("w", encoding="utf-8") as fh:
        json.dump(runs_beir, fh, ensure_ascii=False, indent=2)

    summary = {
        "corpus": corpus_name,
        "run_id": run_id,
        "system": "lightrag",
        "ts": datetime.now(timezone.utc).isoformat(),
        "queries_total": len(queries),
        "queries_with_docs": sum(1 for s in runs_beir.values() if s),
        "queries_empty": sum(1 for s in runs_beir.values() if not s),
        "queries_failed": len(failures),
        "top_k": top_k,
        "chunk_top_k": chunk_top_k,
        "mode": mode,
        "latency_ms_p50": sorted(latencies)[len(latencies)//2] if latencies else None,
        "latency_ms_p95": sorted(latencies)[int(0.95*len(latencies))] if len(latencies) >= 20 else None,
        "latency_ms_mean": sum(latencies)/len(latencies) if latencies else None,
        "elapsed_sec": round(elapsed, 1),
        "failures": failures,
    }
    with (out_dir / "summary.json").open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    print(
        f"[{corpus_name}] done: {summary['queries_with_docs']}/{summary['queries_total']} "
        f"with docs | {summary['queries_empty']} empty | {summary['queries_failed']} failed | "
        f"p50={summary['latency_ms_p50']:.0f}ms | {elapsed:.0f}s"
    )
    return summary


async def _main_async(args: argparse.Namespace) -> int:
    env = _load_env(REPO_ROOT / ".env")
    if not env.get("OPENAI_API_KEY"):
        print("error: OPENAI_API_KEY missing from .env")
        return 2
    os.environ["OPENAI_API_KEY"] = env["OPENAI_API_KEY"]

    targets = args.corpora if args.corpora else CORPORA
    summaries = []
    grand_t0 = time.perf_counter()
    for corpus_name in targets:
        summaries.append(await _retrieve_corpus(
            corpus_name, args.run_id, args.top_k, args.chunk_top_k, args.mode,
        ))
    grand_elapsed = time.perf_counter() - grand_t0

    print("\n=========================== SUMMARY ===========================")
    for s in summaries:
        if s.get("skipped"):
            print(f"  {s['corpus']}: SKIPPED ({s['reason']})")
        else:
            print(
                f"  {s['corpus']}: {s['queries_with_docs']}/{s['queries_total']} with docs, "
                f"{s['queries_empty']} empty, {s['queries_failed']} failed | "
                f"p50={s['latency_ms_p50']:.0f}ms | {s['elapsed_sec']:.0f}s"
            )
    print(f"  TOTAL wall-clock: {grand_elapsed:.0f}s ({grand_elapsed/60:.1f} min)")
    print(f"  Outputs under: experiments/output/retrieve_runs/<corpus>/lightrag_{args.run_id}/")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("corpora", nargs="*", help="optional corpus dir names")
    parser.add_argument(
        "--run-id",
        default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%HZ"),
    )
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--chunk-top-k", type=int, default=20)
    parser.add_argument(
        "--mode", default="hybrid",
        choices=["naive", "local", "global", "hybrid", "mix"],
    )
    args = parser.parse_args(argv)
    return asyncio.run(_main_async(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
