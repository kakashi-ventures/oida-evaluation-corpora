#!/usr/bin/env python3
"""Phase B — bulk OIDA retrieve over all queries in all 5 corpora.

For each query in ``corpora/<id>/queries.jsonl`` we POST to
/retrieve/full-oida (v0 mode, tauBind=0.2, tauFallback=0.1) against the
corpus's bench project, aggregate KOs to doc-level scores via
``supporting_sources``, and emit two artifacts per (corpus, system, run):

  experiments/output/retrieve_runs/<corpus>/<system>_<run_id>/
    runs.tsv         # BEIR-shaped: <qid>\\t<doc_id>\\t<score> — sortable, top-k
    runs.json        # {qid: {doc_id: score}} — direct BEIR loader input
    queries.jsonl    # per-query rich record: doc_scores, score_components,
                     #                        latency, notes, raw retrieve

Where ``<system>`` is the OIDA deploy under test (``oida-angelicadb`` or
``oida-core``). The directory prefix matches what ``03_eval_static_ir.py``
reads via its own ``--system`` flag, so a Layer-1 score on a run produced
here is a one-liner.

The TSV/JSON pair is what BEIR's ``EvaluateRetrieval`` consumes for Layer 1
scoring. The jsonl is the diagnostic layer for §5.6 score-component logging
and for Layers 2-4 evaluation downstream.

Usage:
    python experiments/scripts/02_retrieve.py                            # all 5 corpora on angelica-db
    python experiments/scripts/02_retrieve.py --system oida-core --run-id 2026-05-29T15Z
    python experiments/scripts/02_retrieve.py inv-mystery-redhood
    python experiments/scripts/02_retrieve.py --top-k 20 --run-id smoke
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))

from adapters.oida import (  # noqa: E402
    CORPUS_TO_PROJECT_SLUG,
    OIDA_DEPLOYS,
    OidaClient,
    _load_env,
    resolve_corpus_routing,
    resolve_deploy,
    warmup,
)

OUTPUT_ROOT = REPO_ROOT / "experiments" / "output" / "retrieve_runs"
# After remediation A (per-project isolation), the solver + pgvector search walk
# only the target corpus's few-hundred KOs, so top_k=100 returns in ~seconds and
# Recall@100 is measurable. (On the old shared default project, top_k=100 blew
# past 200 s/query, which forced the 2026-05-29 run down to top_k=20.)
DEFAULT_TOP_K = 100


def _retrieve_corpus(
    corpus_name: str,
    env: dict[str, str],
    run_id: str,
    top_k: int,
    score_field: str,
    system: str,
    base_url: str,
) -> dict:
    corpus_dir = REPO_ROOT / "corpora" / corpus_name
    if not corpus_dir.exists():
        print(f"  ! skip {corpus_name}: directory not found")
        return {"corpus": corpus_name, "skipped": True, "reason": "missing"}

    try:
        project_id, corpus_key = resolve_corpus_routing(system, corpus_name, env)
    except (ValueError, RuntimeError) as e:
        print(f"  ! skip {corpus_name}: {e}")
        return {"corpus": corpus_name, "skipped": True, "reason": str(e)}
    # Retrieve scopes by the projectId in the request body (the corpus's own
    # project). Override the adapter's 600s default — retrieve should fail fast,
    # not hang. Stance is delegated to a separate gpt-4o judge in Layer 3, so we
    # disable OIDA's in-pipeline computeQueryStance.
    client = OidaClient(
        admin_key=corpus_key,
        base_url=base_url,
        project_id_override=None,
        timeout_sec=120,
    )

    with (corpus_dir / "queries.jsonl").open(encoding="utf-8") as fh:
        queries = [json.loads(line) for line in fh if line.strip()]

    out_dir = OUTPUT_ROOT / corpus_name / f"{system}_{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    corpus_slug_short = corpus_name.split("-", 1)[-1] if "-" in corpus_name else corpus_name

    runs_beir: dict[str, dict[str, float]] = {}
    latencies: list[float] = []
    failures: list[str] = []
    t_start = time.perf_counter()

    print(
        f"\n[{corpus_name}] system={system} → {project_id} ({base_url}) | "
        f"{len(queries)} queries | top_k={top_k} | score={score_field}"
    )

    with (out_dir / "queries.jsonl").open("w", encoding="utf-8") as fh_q:
        for i, q in enumerate(queries, 1):
            qid = q["_id"]
            qtext = q["text"]
            t_q = time.perf_counter()
            res = client.retrieve(
                query=qtext,
                project_id=project_id,
                top_k=top_k,
                corpus_slug=corpus_slug_short,
                tau_bind=0.2,
                tau_fallback=0.1,
                compute_query_stance=False,  # delegated to gpt-4o judge in Layer 3
                score_field=score_field,
            )
            dt = time.perf_counter() - t_q
            latencies.append(res.latency_ms)

            runs_beir[qid] = dict(res.doc_scores)

            rec = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "qid": qid,
                "query": qtext,
                "metadata": q.get("metadata", {}),
                "top_k": top_k,
                "score_field": score_field,
                "doc_scores": res.doc_scores,
                "score_components": res.score_components,
                "raw_response_text": res.raw_response_text,
                "dialectic_resolutions": res.dialectic_resolutions,
                "contradiction_edges": res.contradiction_edges,
                "contradiction_edge_count": res.contradiction_edge_count,
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
            top1_score = res.doc_scores.get(top1, 0.0) if top1 else 0.0
            note = res.notes or ""
            if not res.doc_scores and "retrieve_error" in (res.notes or ""):
                failures.append(qid)
                tag = "FAIL"
            elif not res.doc_scores:
                tag = "EMPTY"
            else:
                tag = "OK"
            print(
                f"  [{i:3d}/{len(queries)}] {tag:5s} {qid:5s} docs={ndocs:3d} "
                f"top1={top1[:45]+'..' if top1 and len(top1)>45 else (top1 or '-'):47s} "
                f"score={top1_score:5.3f} ({dt:5.2f}s)"
            )

    elapsed = time.perf_counter() - t_start

    # BEIR runs.tsv: qid \t doc_id \t score, sorted desc within each query
    with (out_dir / "runs.tsv").open("w", encoding="utf-8") as fh:
        for qid, scores in runs_beir.items():
            for doc_id, score in sorted(scores.items(), key=lambda kv: -kv[1]):
                fh.write(f"{qid}\t{doc_id}\t{score}\n")

    # BEIR runs.json: {qid: {doc_id: score}}
    with (out_dir / "runs.json").open("w", encoding="utf-8") as fh:
        json.dump(runs_beir, fh, ensure_ascii=False, indent=2)

    # Run-level summary
    summary = {
        "corpus": corpus_name,
        "system": system,
        "base_url": base_url,
        "project": project_id,
        "run_id": run_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "queries_total": len(queries),
        "queries_with_docs": sum(1 for s in runs_beir.values() if s),
        "queries_empty": sum(1 for s in runs_beir.values() if not s),
        "queries_failed": len(failures),
        "top_k": top_k,
        "score_field": score_field,
        "latency_ms_p50": sorted(latencies)[len(latencies) // 2] if latencies else None,
        "latency_ms_p95": sorted(latencies)[int(0.95 * len(latencies))] if len(latencies) >= 20 else None,
        "latency_ms_mean": sum(latencies) / len(latencies) if latencies else None,
        "elapsed_sec": round(elapsed, 1),
        "failures": failures,
    }
    with (out_dir / "summary.json").open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print(
        f"[{corpus_name}] done: {summary['queries_with_docs']}/{summary['queries_total']} "
        f"with docs | {summary['queries_empty']} empty | {summary['queries_failed']} failed | "
        f"p50={summary['latency_ms_p50']:.0f}ms p95={summary['latency_ms_p95'] or '-'}ms | "
        f"{elapsed:.0f}s wall-clock"
    )
    return summary


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("corpora", nargs="*", help="optional corpus dir names to limit the run")
    parser.add_argument(
        "--run-id",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        help="suffix for the output dir; default = UTC timestamp",
    )
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help="docs per query (max 100)")
    parser.add_argument(
        "--score-field",
        choices=["similarity", "kge_score", "regime_adjusted_score"],
        default="regime_adjusted_score",
        help="which v0 KO score to aggregate to doc level (max across KOs sharing the same source)",
    )
    parser.add_argument(
        "--system",
        choices=sorted(OIDA_DEPLOYS.keys()),
        default="oida-angelicadb",
        help=(
            "which OIDA deploy to target. "
            "oida-angelicadb (default) reads OIDA_BASE_URL + OIDA_ADMIN_KEY; "
            "oida-core reads OIDA_CORE_BASE_URL + OIDA_CORE_ADMIN_KEY. "
            "Output dirs prefix with the system name "
            "(experiments/output/retrieve_runs/<corpus>/<system>_<run_id>/)."
        ),
    )
    args = parser.parse_args(argv)

    env = _load_env(REPO_ROOT / ".env")
    try:
        base_url, _admin_key = resolve_deploy(args.system, env)
    except (ValueError, RuntimeError) as e:
        print(f"error: {e}")
        return 2

    targets = args.corpora if args.corpora else list(CORPUS_TO_PROJECT_SLUG.keys())
    print(f"\n>>> OIDA deploy: {args.system} ({base_url}) | run_id={args.run_id}")
    warmup(base_url)  # remediation E — beat the Render cold-start before timing
    summaries = []
    grand_t0 = time.perf_counter()
    for corpus_name in targets:
        summaries.append(
            _retrieve_corpus(
                corpus_name,
                env,
                args.run_id,
                args.top_k,
                args.score_field,
                args.system,
                base_url,
            )
        )
    grand_elapsed = time.perf_counter() - grand_t0

    print("\n=========================== SUMMARY ===========================")
    print(f"  System: {args.system}  ({base_url})  run_id={args.run_id}")
    for s in summaries:
        if s.get("skipped"):
            print(f"  {s['corpus']}: SKIPPED ({s['reason']})")
        else:
            print(
                f"  {s['corpus']} → {s['project']}: "
                f"{s['queries_with_docs']}/{s['queries_total']} with docs, "
                f"{s['queries_empty']} empty, {s['queries_failed']} failed | "
                f"p50={s['latency_ms_p50']:.0f}ms | {s['elapsed_sec']:.0f}s"
            )
    print(f"  TOTAL wall-clock: {grand_elapsed:.0f}s ({grand_elapsed/60:.1f} min)")
    print(f"  Outputs under: experiments/output/retrieve_runs/<corpus>/{args.system}_{args.run_id}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
