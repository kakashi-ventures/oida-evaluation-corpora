#!/usr/bin/env python3
"""Phase D — bulk LightRAG ingest across all 5 corpora.

Mirrors 01_ingest.py but talks to LightRAG (async, in-process). Each corpus
gets its own LightRAG ``working_dir`` under
``experiments/systems/lightrag-data/<corpus_slug>/`` (gitignored), so the
per-corpus isolation OIDA could not offer is automatic here.

Per-doc reports are appended to
``experiments/output/ingest_reports/<corpus>__lightrag.jsonl``
(gitignored). Resumable — re-running skips docs already recorded as
``committed=true``.

Usage:
    python experiments/scripts/04_ingest_lightrag.py             # all 5
    python experiments/scripts/04_ingest_lightrag.py inv-mystery-redhood
    python experiments/scripts/04_ingest_lightrag.py --dry-run
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

OUTPUT_DIR = REPO_ROOT / "experiments" / "output" / "ingest_reports"

CORPORA = [
    "org-consulting-clearpath",
    "org-iot-fireglass",
    "org-vc-vertexminds",
    "inv-mystery-redhood",
    "inv-ashford-mystery",
]


def _already_committed(report_path: Path) -> set[str]:
    if not report_path.exists():
        return set()
    seen: set[str] = set()
    for line in report_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("committed"):
            seen.add(rec["doc_id"])
    return seen


async def _ingest_corpus(corpus_name: str, env: dict[str, str], dry_run: bool) -> dict:
    corpus_dir = REPO_ROOT / "corpora" / corpus_name
    if not corpus_dir.exists():
        print(f"  ! skip {corpus_name}: directory not found")
        return {"corpus": corpus_name, "skipped": True, "reason": "missing"}

    corpus_slug = corpus_name.split("-", 1)[-1] if "-" in corpus_name else corpus_name
    with (corpus_dir / "corpus.jsonl").open(encoding="utf-8") as fh:
        docs = [json.loads(line) for line in fh if line.strip()]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"{corpus_name}__lightrag.jsonl"
    already = _already_committed(report_path)

    print(
        f"\n[{corpus_name}] LightRAG working_dir=experiments/systems/lightrag-data/{corpus_slug} | "
        f"{len(docs)} docs total, {len(already)} already committed, "
        f"{len(docs) - len(already)} to ingest"
    )
    if dry_run:
        return {
            "corpus": corpus_name,
            "docs_total": len(docs),
            "docs_to_ingest": len(docs) - len(already),
            "dry_run": True,
        }

    client = LightRagClient(corpus_slug=corpus_slug)
    await client.init()

    committed = 0
    failed = 0
    t_start = time.perf_counter()
    try:
        with report_path.open("a", encoding="utf-8") as fh_out:
            for i, doc in enumerate(docs, 1):
                doc_id = doc["_id"]
                if doc_id in already:
                    continue
                try:
                    rep = await client.ingest_doc(
                        doc_id, doc["text"], title=doc.get("title")
                    )
                except Exception as e:  # noqa: BLE001
                    from adapters.lightrag import IngestReport
                    rep = IngestReport(
                        doc_id=doc_id,
                        source_uri=f"beir-corpora://{corpus_slug}/{doc_id}",
                        committed=False,
                        error=f"{type(e).__name__}: {str(e)[:200]}",
                    )
                rec = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "doc_id": rep.doc_id,
                    "source_uri": rep.source_uri,
                    "committed": rep.committed,
                    "latency_ms": rep.latency_ms,
                    "error": rep.error,
                }
                fh_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh_out.flush()
                if rep.committed:
                    committed += 1
                    tag = "OK"
                else:
                    failed += 1
                    tag = "FAIL"
                err = f" err={rep.error[:60]}" if rep.error else ""
                print(
                    f"  [{i:3d}/{len(docs)}] {tag:4s} {doc_id[:50]:50s} "
                    f"({rep.latency_ms / 1000:5.1f}s){err}"
                )
    finally:
        await client.close()
    elapsed = time.perf_counter() - t_start
    print(
        f"[{corpus_name}] done: {committed} OK / {failed} FAIL / {len(already)} skipped | "
        f"{elapsed:.0f}s wall-clock"
    )
    return {
        "corpus": corpus_name,
        "docs_total": len(docs),
        "docs_committed_this_run": committed,
        "docs_failed_this_run": failed,
        "docs_skipped_resume": len(already),
        "elapsed_sec": round(elapsed, 1),
    }


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
        summaries.append(await _ingest_corpus(corpus_name, env, args.dry_run))
    grand_elapsed = time.perf_counter() - grand_t0

    print("\n=========================== SUMMARY ===========================")
    for s in summaries:
        if s.get("skipped"):
            print(f"  {s['corpus']}: SKIPPED ({s['reason']})")
        elif s.get("dry_run"):
            print(f"  {s['corpus']}: {s['docs_to_ingest']}/{s['docs_total']} to ingest")
        else:
            print(
                f"  {s['corpus']}: {s['docs_committed_this_run']} OK, "
                f"{s['docs_failed_this_run']} FAIL, "
                f"{s['docs_skipped_resume']} skipped | {s['elapsed_sec']:.0f}s"
            )
    print(f"  TOTAL wall-clock: {grand_elapsed:.0f}s ({grand_elapsed/60:.1f} min)")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("corpora", nargs="*", help="optional corpus dir names")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return asyncio.run(_main_async(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
