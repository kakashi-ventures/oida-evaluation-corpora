#!/usr/bin/env python3
"""Phase E — bulk HippoRAG ingest across all 5 corpora.

HippoRAG indexes in one batch per corpus (HippoRAG.index([doc_text_list])),
not per-doc, so this script is a thin wrapper. Per-corpus save_dir under
experiments/systems/hipporag-data/<slug>/ gives natural isolation.

Outputs a single aggregated report JSON per corpus to
experiments/output/ingest_reports/<corpus>__hipporag.json (NOT jsonl —
one row).

Usage:
    python experiments/scripts/06_ingest_hipporag.py
    python experiments/scripts/06_ingest_hipporag.py inv-mystery-redhood
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

from adapters.hipporag import HippoRagClient, _load_env  # noqa: E402

OUTPUT_DIR = REPO_ROOT / "experiments" / "output" / "ingest_reports"

CORPORA = [
    "org-consulting-clearpath",
    "org-iot-fireglass",
    "org-vc-vertexminds",
    "inv-mystery-redhood",
    "inv-ashford-mystery",
]


def _ingest_corpus(corpus_name: str) -> dict:
    corpus_dir = REPO_ROOT / "corpora" / corpus_name
    if not corpus_dir.exists():
        print(f"  ! skip {corpus_name}: directory not found")
        return {"corpus": corpus_name, "skipped": True}

    corpus_slug = corpus_name.split("-", 1)[-1] if "-" in corpus_name else corpus_name
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"{corpus_name}__hipporag.json"

    # Skip if a prior committed report exists (resume semantics)
    if report_path.exists():
        prior = json.loads(report_path.read_text(encoding="utf-8"))
        if prior.get("committed"):
            print(f"  [{corpus_name}] already committed: {prior['docs_committed']}/{prior['docs_total']} — skipping")
            return prior

    client = HippoRagClient(corpus_slug=corpus_slug)
    print(f"\n[{corpus_name}] save_dir=experiments/systems/hipporag-data/{corpus_slug}")
    t0 = time.perf_counter()
    reports = client.ingest_corpus(corpus_dir)
    elapsed = time.perf_counter() - t0

    n_ok = sum(1 for r in reports if r.committed)
    n_fail = len(reports) - n_ok
    err = reports[0].error if reports and reports[0].error else None

    summary = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "corpus": corpus_name,
        "system": "hipporag",
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
    args = parser.parse_args(argv)

    env = _load_env(REPO_ROOT / ".env")
    if not env.get("OPENAI_API_KEY"):
        print("error: OPENAI_API_KEY missing from .env")
        return 2
    os.environ["OPENAI_API_KEY"] = env["OPENAI_API_KEY"]

    targets = args.corpora if args.corpora else CORPORA
    summaries = []
    grand_t0 = time.perf_counter()
    for c in targets:
        summaries.append(_ingest_corpus(c))
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
