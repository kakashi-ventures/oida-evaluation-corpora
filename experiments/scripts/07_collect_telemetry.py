#!/usr/bin/env python3
"""Layer 5 — practicality telemetry (EXPERIMENT_PLAN.md §5.5).

Fills ``layer_5_practicality`` of each ``corpora/<id>/results/<system>_*.json``
from artefacts already on disk:

  - retrieve_latency_ms_p50 / _p95          ← retrieve_runs/<>/summary.json
  - ingest_wall_clock_sec_per_doc_median    ← ingest_reports (per-doc latency_ms)
  - retrieve_cost_usd_per_query_median      ← imputed from per-query token counts
  - ingest_cost_usd_total                   ← imputed from ingest-report tokens (if any)

Costs are *imputed* (tokens × published rate), not billed — OIDA's real spend
is on the deploy, not us; this normalises systems on a like-for-like basis.
gpt-4o-mini rates are used for the three baselines (their configured LLM); OIDA
LLM tokens are not exposed externally, so OIDA retrieve cost reflects only the
embedded query.

Usage:
    python experiments/scripts/07_collect_telemetry.py
    python experiments/scripts/07_collect_telemetry.py --system lightrag
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import eval_common as ec  # noqa: E402

INGEST_ROOT = ec.REPO_ROOT / "experiments" / "output" / "ingest_reports"

# USD per 1M tokens (published rates, 2026-05-28).
PRICE = {
    "embed": 0.02,            # text-embedding-3-small
    "llm_in": 0.15,           # gpt-4o-mini input  (baselines)
    "llm_out": 0.60,          # gpt-4o-mini output (baselines)
}


def _imputed_cost(rec: dict) -> float:
    ti = rec.get("tokens_in") or 0
    to = rec.get("tokens_out") or 0
    te = rec.get("embed_tokens") or 0
    return (ti * PRICE["llm_in"] + to * PRICE["llm_out"] + te * PRICE["embed"]) / 1_000_000


def _ingest_report_path(corpus: str, system: str) -> Path | None:
    """Per-deploy OIDA report lives under ingest_reports/<system>/<corpus>.jsonl;
    baselines under ingest_reports/<corpus>__<system>.json[l]."""
    cands = [
        INGEST_ROOT / system / f"{corpus}.jsonl",
        INGEST_ROOT / f"{corpus}__{system}.jsonl",
        INGEST_ROOT / f"{corpus}__{system}.json",
    ]
    for p in cands:
        if p.exists():
            return p
    return None


def _ingest_stats(corpus: str, system: str) -> tuple[float | None, float | None]:
    """(median_sec_per_doc, imputed_total_cost_usd)."""
    path = _ingest_report_path(corpus, system)
    if path is None:
        return None, None
    secs: list[float] = []
    cost = 0.0
    saw_tokens = False
    text = path.read_text(encoding="utf-8")
    records: list[dict] = []
    if path.suffix == ".json":
        try:
            data = json.loads(text)
            records = data if isinstance(data, list) else data.get("docs", []) or []
        except json.JSONDecodeError:
            records = []
    else:
        for line in text.splitlines():
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    for rec in records:
        if rec.get("committed") is False:
            continue
        lat = rec.get("latency_ms")
        if lat is not None:
            secs.append(float(lat) / 1000.0)
        for tk in ("tokens_in", "tokens_out", "embed_tokens"):
            if rec.get(tk):
                saw_tokens = True
        cost += _imputed_cost(rec)
    median = statistics.median(secs) if secs else None
    return median, (cost if saw_tokens else None)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("corpora", nargs="*")
    p.add_argument("--system", choices=ec.SYSTEMS)
    args = p.parse_args(argv)

    corpora = args.corpora or ec.ALL_CORPORA
    systems = [args.system] if args.system else ec.SYSTEMS

    rows = []
    for corpus in corpora:
        for system in systems:
            recs = ec.load_retrieve_records(corpus, system)
            summ = ec.retrieve_summary(corpus, system)
            if not recs and not summ:
                continue
            per_q_cost = [_imputed_cost(r) for r in recs.values()] if recs else []
            ingest_med, ingest_cost = _ingest_stats(corpus, system)
            block = {
                "ingest_wall_clock_sec_per_doc_median": ingest_med,
                "retrieve_latency_ms_p50": summ.get("latency_ms_p50"),
                "retrieve_latency_ms_p95": summ.get("latency_ms_p95"),
                "retrieve_cost_usd_per_query_median": (
                    statistics.median(per_q_cost) if per_q_cost else None
                ),
                "ingest_cost_usd_total": ingest_cost,
            }
            path = ec.update_layer(corpus, system, "layer_5_practicality", block)
            rows.append((corpus, system, block, "wrote" if path else "NO RESULT FILE"))

    print("\n===================== LAYER 5 — PRACTICALITY =====================")
    print(f"{'corpus':<26s} {'system':<16s} p50ms   p95ms   ingest_s/doc  $/query")
    for corpus, system, b, status in rows:
        if status != "wrote":
            print(f"{corpus:<26s} {system:<16s} -- {status}")
            continue
        p50 = b["retrieve_latency_ms_p50"]; p95 = b["retrieve_latency_ms_p95"]
        print(
            f"{corpus:<26s} {system:<16s} "
            f"{(f'{p50:.0f}' if p50 else '—'):>6s}  {(f'{p95:.0f}' if p95 else '—'):>6s}  "
            f"{ec.fmt(b['ingest_wall_clock_sec_per_doc_median'],2):>11s}  "
            f"{(f'${b['retrieve_cost_usd_per_query_median']:.5f}' if b['retrieve_cost_usd_per_query_median'] is not None else '—')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
