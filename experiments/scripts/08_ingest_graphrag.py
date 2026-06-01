#!/usr/bin/env python3
"""Phase F — GraphRAG (Microsoft) ingest across all 5 corpora.

GraphRAG indexes per-project (one project per corpus) via the `graphrag
index` CLI as a subprocess. The python-level adapter handles init + input
placement + invocation. Per-corpus project under
experiments/systems/graphrag-data/<slug>/.

Resume semantics: if output/documents.parquet exists, skip indexing.

Usage:
    python experiments/scripts/08_ingest_graphrag.py
    python experiments/scripts/08_ingest_graphrag.py inv-mystery-redhood --force
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments"))

from adapters.graphrag_msft import GraphRagClient, _load_env  # noqa: E402

OUTPUT_DIR = REPO_ROOT / "experiments" / "output" / "ingest_reports"
CORPORA = [
    "org-consulting-clearpath",
    "org-iot-fireglass",
    "org-vc-vertexminds",
    "inv-mystery-redhood",
    "inv-ashford-mystery",
]


def _ingest_corpus(corpus_name: str, force: bool) -> dict:
    corpus_dir = REPO_ROOT / "corpora" / corpus_name
    if not corpus_dir.exists():
        print(f"  ! skip {corpus_name}: directory not found")
        return {"corpus": corpus_name, "skipped": True}

    corpus_slug = corpus_name.split("-", 1)[-1] if "-" in corpus_name else corpus_name
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"{corpus_name}__graphrag.json"
    client = GraphRagClient(corpus_slug=corpus_slug)

    has_index = (client.output_dir / "documents.parquet").exists()
    if has_index and not force and report_path.exists():
        prior = json.loads(report_path.read_text(encoding="utf-8"))
        if prior.get("committed"):
            print(f"  [{corpus_name}] already indexed — skipping (use --force to rebuild)")
            return prior

    print(f"\n[{corpus_name}] project_dir=experiments/systems/graphrag-data/{corpus_slug}")
    t0 = time.perf_counter()
    reports = client.ingest_corpus(corpus_dir, force_reindex=force)
    elapsed = time.perf_counter() - t0

    n_ok = sum(1 for r in reports if r.committed)
    n_fail = len(reports) - n_ok
    err = reports[0].error if reports and reports[0].error else None

    summary = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "corpus": corpus_name,
        "system": "graphrag",
        "docs_total": len(reports),
        "docs_committed": n_ok,
        "docs_failed": n_fail,
        "committed": n_ok == len(reports),
        "elapsed_sec": round(elapsed, 1),
        "median_sec_per_doc": round(elapsed / max(1, len(reports)), 2),
        "error": err,
    }
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    tag = "OK" if summary["committed"] else "PARTIAL"
    print(f"  {tag}: {n_ok}/{len(reports)} ({elapsed:.0f}s) → {report_path.relative_to(REPO_ROOT)}")
    return summary


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("corpora", nargs="*", help="optional corpus dir names")
    parser.add_argument("--force", action="store_true", help="rebuild index even if it exists")
    args = parser.parse_args(argv)

    env = _load_env(REPO_ROOT / ".env")
    if not env.get("OPENAI_API_KEY"):
        print("error: OPENAI_API_KEY missing from .env")
        return 2
    os.environ["OPENAI_API_KEY"] = env["OPENAI_API_KEY"]
    os.environ["GRAPHRAG_API_KEY"] = env["OPENAI_API_KEY"]

    targets = args.corpora if args.corpora else CORPORA
    summaries = []
    grand_t0 = time.perf_counter()
    for c in targets:
        summaries.append(_ingest_corpus(c, args.force))
    grand = time.perf_counter() - grand_t0

    print("\n=========================== SUMMARY ===========================")
    for s in summaries:
        if s.get("skipped"):
            print(f"  {s['corpus']}: SKIPPED")
        else:
            print(
                f"  {s['corpus']:30s} {s['docs_committed']:3d}/{s['docs_total']:3d} OK | "
                f"{s['elapsed_sec']:.0f}s ({s['median_sec_per_doc']}s/doc)"
            )
    print(f"  TOTAL wall-clock: {grand:.0f}s ({grand/60:.1f} min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
