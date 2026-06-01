#!/usr/bin/env python3
"""Phase A — bulk OIDA ingest of all 5 corpora into isolated bench projects.

Each doc in ``corpora/<id>/corpus.jsonl`` is POSTed to /ingest with
``source: beir-corpora://<corpus_slug>/<doc_id>`` so its KOs can be traced
back via ``supporting_sources`` at retrieve time. Per-doc reports are
appended to ``experiments/output/ingest_reports/<system>/<corpus>.jsonl``
(gitignored), where ``<system>`` is the OIDA deploy under test
(``oida-angelicadb`` or ``oida-core``).

Resumable: re-running the script skips any ``doc_id`` already recorded as
``committed=true`` in the corpus's report. Append-only design — never
overwrites prior records, so partial runs can be picked up. Resume state
is **per-system** so an angelica-db re-run doesn't skip docs based on an
oida-core report or vice versa.

Backward compat: when ``--system oida-angelicadb`` is requested (the
default) and the new per-system report path does not yet exist, a legacy
``experiments/output/ingest_reports/<corpus>.jsonl`` file (from before
this script grew the ``--system`` flag) is **copied** into the new path
so prior progress is preserved.

Usage:
    python experiments/scripts/01_ingest.py                # all 5 corpora on angelica-db (default)
    python experiments/scripts/01_ingest.py --system oida-core
    python experiments/scripts/01_ingest.py inv-mystery-redhood  # one corpus
    python experiments/scripts/01_ingest.py --dry-run      # print plan, no calls
"""
from __future__ import annotations

import argparse
import json
import shutil
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

OUTPUT_DIR = REPO_ROOT / "experiments" / "output" / "ingest_reports"


def _already_committed(report_path: Path) -> set[str]:
    """Return doc_ids whose latest report row says committed=true."""
    if not report_path.exists():
        return set()
    seen: set[str] = set()
    failed_again: set[str] = set()
    for line in report_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        doc_id = rec.get("doc_id")
        if not doc_id:
            continue
        if rec.get("committed"):
            seen.add(doc_id)
            failed_again.discard(doc_id)
        else:
            failed_again.add(doc_id)
    return seen


def _ingest_corpus(
    corpus_name: str,
    env: dict[str, str],
    dry_run: bool,
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
    # Ingest authenticates with the per-corpus key; the KO's project is the
    # key's OWN project (the x-project-id header is ignored for Bearer auth),
    # so no project_id_override is needed at ingest time.
    client = OidaClient(
        admin_key=corpus_key,
        base_url=base_url,
        project_id_override=None,
    )

    with (corpus_dir / "corpus.jsonl").open(encoding="utf-8") as fh:
        docs = [json.loads(line) for line in fh if line.strip()]

    report_dir = OUTPUT_DIR / system
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{corpus_name}.jsonl"
    # Backward-compat: pre-multi-deploy runs wrote to
    # experiments/output/ingest_reports/<corpus>.jsonl with no system
    # subfolder. If we are running angelica-db (the historical default)
    # and the per-system file doesn't exist yet, seed it from the legacy
    # path so resume picks up where prior runs left off. We *copy* rather
    # than move so the legacy artifact stays put.
    legacy_path = OUTPUT_DIR / f"{corpus_name}.jsonl"
    if (
        system == "oida-angelicadb"
        and not report_path.exists()
        and legacy_path.exists()
    ):
        shutil.copyfile(legacy_path, report_path)
        print(f"  ↳ seeded {report_path.relative_to(REPO_ROOT)} from legacy {legacy_path.name}")
    already = _already_committed(report_path)

    print(
        f"\n[{corpus_name}] system={system} → project={project_id} ({base_url}) | "
        f"{len(docs)} docs total, {len(already)} already committed, "
        f"{len(docs) - len(already)} to ingest"
    )
    if dry_run:
        return {
            "corpus": corpus_name,
            "system": system,
            "project": project_id,
            "docs_total": len(docs),
            "docs_to_ingest": len(docs) - len(already),
            "dry_run": True,
        }

    # The corpus_slug used for source URIs is the trailing segment of the
    # corpus dir name (e.g. org-consulting-clearpath → clearpath).
    corpus_slug_short = corpus_name.split("-", 1)[-1] if "-" in corpus_name else corpus_name

    committed = 0
    failed = 0
    total_kos = 0
    total_chunks = 0
    t_start = time.perf_counter()
    with report_path.open("a", encoding="utf-8") as fh_out:
        for i, doc in enumerate(docs, 1):
            doc_id = doc["_id"]
            if doc_id in already:
                continue
            t_doc = time.perf_counter()
            try:
                rep = client.ingest_doc(corpus_slug_short, doc)
            except Exception as e:  # noqa: BLE001 — never let one bad doc crash the run
                from adapters.oida import IngestReport
                rep = IngestReport(
                    doc_id=doc_id,
                    source_uri="",
                    committed=False,
                    error=f"{type(e).__name__}: {str(e)[:200]}",
                )
            dt = time.perf_counter() - t_doc
            rec = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "doc_id": rep.doc_id,
                "source_uri": rep.source_uri,
                "committed": rep.committed,
                "kos_created": rep.kos_created,
                "candidates_total": rep.candidates_total,
                "kos_rejected": rep.kos_rejected,
                "kos_quarantined": rep.kos_quarantined,
                "partial_error_count": rep.partial_error_count,
                "chunks_ingested": rep.chunks_ingested,
                "latency_ms": rep.latency_ms,
                "error": rep.error,
                "run_ids": rep.run_ids,
            }
            fh_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh_out.flush()
            if rep.committed:
                committed += 1
                total_kos += rep.kos_created
                total_chunks += rep.chunks_ingested
                tag = "OK"
            else:
                failed += 1
                tag = "FAIL"
            err = f" err={rep.error[:60]}" if rep.error else ""
            print(
                f"  [{i:3d}/{len(docs)}] {tag:4s} {doc_id[:50]:50s} "
                f"chunks={rep.chunks_ingested} kos={rep.kos_created:3d} ({dt:5.1f}s){err}"
            )
    elapsed = time.perf_counter() - t_start
    print(
        f"[{corpus_name}] done: {committed} OK / {failed} FAIL / {len(already)} skipped | "
        f"{total_kos} KOs / {total_chunks} chunks | {elapsed:.0f}s wall-clock"
    )
    return {
        "corpus": corpus_name,
        "system": system,
        "project": project_id,
        "docs_total": len(docs),
        "docs_committed_this_run": committed,
        "docs_failed_this_run": failed,
        "docs_skipped_resume": len(already),
        "kos_created_this_run": total_kos,
        "elapsed_sec": round(elapsed, 1),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("corpora", nargs="*", help="optional corpus dir names to limit the run")
    parser.add_argument("--dry-run", action="store_true", help="print plan, no API calls")
    parser.add_argument(
        "--system",
        choices=sorted(OIDA_DEPLOYS.keys()),
        default="oida-angelicadb",
        help=(
            "which OIDA deploy to target. "
            "oida-angelicadb (default, status quo) reads OIDA_BASE_URL + OIDA_ADMIN_KEY; "
            "oida-core reads OIDA_CORE_BASE_URL + OIDA_CORE_ADMIN_KEY. "
            "Reports are isolated under experiments/output/ingest_reports/<system>/."
        ),
    )
    args = parser.parse_args(argv)

    env = _load_env(REPO_ROOT / ".env")
    try:
        base_url, admin_key = resolve_deploy(args.system, env)
    except (ValueError, RuntimeError) as e:
        print(f"error: {e}")
        return 2

    targets = args.corpora if args.corpora else list(CORPUS_TO_PROJECT_SLUG.keys())
    print(f"\n>>> OIDA deploy: {args.system} ({base_url})")
    if not args.dry_run:
        warmup(base_url)  # remediation E — beat the Render cold-start before timing
    summaries = []
    grand_t0 = time.perf_counter()
    for corpus_name in targets:
        summaries.append(
            _ingest_corpus(corpus_name, env, args.dry_run, args.system, base_url)
        )
    grand_elapsed = time.perf_counter() - grand_t0

    print("\n=========================== SUMMARY ===========================")
    print(f"  System: {args.system}  ({base_url})")
    for s in summaries:
        if s.get("skipped"):
            print(f"  {s['corpus']}: SKIPPED ({s['reason']})")
        elif s.get("dry_run"):
            print(f"  {s['corpus']} → {s['project']}: {s['docs_to_ingest']}/{s['docs_total']} to ingest")
        else:
            print(
                f"  {s['corpus']} → {s['project']}: "
                f"{s['docs_committed_this_run']} OK, {s['docs_failed_this_run']} FAIL, "
                f"{s['docs_skipped_resume']} skipped | "
                f"{s['kos_created_this_run']} KOs | {s['elapsed_sec']:.0f}s"
            )
    print(f"  TOTAL wall-clock: {grand_elapsed:.0f}s ({grand_elapsed/60:.1f} min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
