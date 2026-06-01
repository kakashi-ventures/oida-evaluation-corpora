#!/usr/bin/env python3
"""Shared loaders + helpers for the Layer 2-5 evaluation scripts (04-08).

The Layer-1 scorer (03_eval_static_ir.py) *creates* one result JSON per
(corpus, system) under ``corpora/<id>/results/<system>_<run_id>.json``. The
later layer scorers (04 adversarial, 05 stance, 06 temporal, 07 telemetry)
*update* the matching block of that same file in place, and 08_report rolls
the whole set up into cross-system F-conditions + RESULTS.md.

This module centralises the file-resolution, qrels/runs/annotation loaders,
and the merge-into-result-JSON plumbing so the per-layer scripts stay short.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPORA_ROOT = REPO_ROOT / "corpora"
RETRIEVE_ROOT = REPO_ROOT / "experiments" / "output" / "retrieve_runs"
ANNOTATIONS_ROOT = REPO_ROOT / "experiments" / "annotations"

# Canonical system slots (result-JSON `system` field + retrieve-dir prefix).
SYSTEMS = ["oida-angelicadb", "oida-core", "graphrag", "lightrag", "hipporag"]
OIDA_SYSTEMS = ["oida-angelicadb", "oida-core"]

ALL_CORPORA = [
    "org-consulting-clearpath",
    "org-iot-fireglass",
    "org-vc-vertexminds",
    "inv-mystery-redhood",
    "inv-ashford-mystery",
]
ORG_CORPORA = [c for c in ALL_CORPORA if c.startswith("org-")]


# ---------------------------------------------------------------------------
# qrels / runs / corpus / queries
# ---------------------------------------------------------------------------


def load_qrels(corpus: str) -> dict[str, dict[str, int]]:
    """{qid: {doc_id: relevance}} from corpora/<corpus>/qrels/test.tsv."""
    path = CORPORA_ROOT / corpus / "qrels" / "test.tsv"
    out: dict[str, dict[str, int]] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:  # skip header
        if not line.strip():
            continue
        qid, cid, score = line.split("\t")
        out.setdefault(qid, {})[cid] = int(score)
    return out


def resolve_retrieve_dir(corpus: str, system: str) -> Path | None:
    """Newest ``<system>_<run_id>/`` dir (with runs.json) for this corpus."""
    base = RETRIEVE_ROOT / corpus
    if not base.is_dir():
        return None
    cands = [
        d for d in base.iterdir()
        if d.is_dir() and d.name.startswith(f"{system}_") and (d / "runs.json").exists()
    ]
    if not cands:
        return None
    return max(cands, key=lambda d: d.stat().st_mtime)


def run_id_from_dir(run_dir: Path, system: str) -> str:
    return run_dir.name[len(system) + 1:]


def load_runs(corpus: str, system: str) -> dict[str, dict[str, float]] | None:
    run_dir = resolve_retrieve_dir(corpus, system)
    if run_dir is None:
        return None
    return json.loads((run_dir / "runs.json").read_text(encoding="utf-8"))


def load_retrieve_records(corpus: str, system: str) -> dict[str, dict]:
    """{qid: per-query record} from the retrieve run's queries.jsonl.

    Carries doc_scores, score_components, raw_response_text (graphrag),
    latency, tokens — the diagnostic layer used by Layers 3 and 5.
    """
    run_dir = resolve_retrieve_dir(corpus, system)
    if run_dir is None:
        return {}
    path = run_dir / "queries.jsonl"
    if not path.exists():
        return {}
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            out[rec["qid"]] = rec
    return out


def retrieve_summary(corpus: str, system: str) -> dict:
    run_dir = resolve_retrieve_dir(corpus, system)
    if run_dir is None:
        return {}
    p = run_dir / "summary.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def load_corpus_docs(corpus: str) -> dict[str, dict]:
    """{doc_id: {title, text, created, metadata}} from corpus.jsonl."""
    path = CORPORA_ROOT / corpus / "corpus.jsonl"
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        md = rec.get("metadata", {})
        out[rec["_id"]] = {
            "title": rec.get("title", ""),
            "text": rec.get("text", ""),
            "created": md.get("created"),
            "metadata": md,
        }
    return out


def load_queries(corpus: str) -> dict[str, dict]:
    """{qid: {text, metadata}} from queries.jsonl."""
    path = CORPORA_ROOT / corpus / "queries.jsonl"
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        out[rec["_id"]] = {"text": rec.get("text", ""), "metadata": rec.get("metadata", {})}
    return out


def ranked(scores: dict[str, float]) -> list[str]:
    """Doc ids sorted by score desc (stable)."""
    return [d for d, _ in sorted(scores.items(), key=lambda kv: -kv[1])]


# ---------------------------------------------------------------------------
# annotations
# ---------------------------------------------------------------------------


def load_annotation(kind: str, corpus: str) -> dict | None:
    """kind ∈ {stance_gold, contra_sets, supersession_chains, lifecycle,
    temporal_queries}. Returns None if the file is absent (layer not scorable)."""
    path = ANNOTATIONS_ROOT / kind / f"{corpus}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# result JSON read / merge / write
# ---------------------------------------------------------------------------


def resolve_result_file(corpus: str, system: str) -> Path | None:
    """Newest ``corpora/<corpus>/results/<system>_*.json``."""
    base = CORPORA_ROOT / corpus / "results"
    if not base.is_dir():
        return None
    cands = sorted(base.glob(f"{system}_*.json"))
    if not cands:
        return None
    return max(cands, key=lambda p: p.stat().st_mtime)


def load_result(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_result(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_layer(corpus: str, system: str, layer_key: str, block: dict) -> Path | None:
    """Merge ``block`` into result[layer_key] for (corpus, system); write back.

    Returns the path written, or None if no result file exists yet (run 03 first).
    """
    path = resolve_result_file(corpus, system)
    if path is None:
        return None
    result = load_result(path)
    result.setdefault(layer_key, {})
    result[layer_key].update(block)
    save_result(path, result)
    return path


def fmt(v, nd: int = 3) -> str:
    return f"{v:.{nd}f}" if isinstance(v, (int, float)) else "—"
