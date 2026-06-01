"""GraphRAG (Microsoft) adapter for the BEIR-style comparative experiment.

Wraps the GraphRAG 3.1.0 Python API (graphrag.api.basic_search) onto the
uniform adapter contract in ``experiments/EXPERIMENT_PLAN.md`` §6.

Per-corpus storage under ``experiments/systems/graphrag-data/<corpus_slug>/``,
each with its own settings.yaml, input/ (one .txt per doc), and output/
(parquet artifacts). Indexing is done once per corpus by invoking
``graphrag index`` as a subprocess (the Python build_index API requires
significant config wiring we let the CLI handle).

Retrieval uses ``basic_search`` (chunk-level, no graph traversal, cheaper).
For BEIR doc-level scoring we:
  1. Take the returned ``sources`` DataFrame (chunk id + text, ranked).
  2. Look up each chunk's ``document_id`` in text_units.parquet.
  3. Map ``document_id`` → ``title`` via documents.parquet.
  4. Strip the ``.txt`` suffix from the title to recover the corpus.jsonl _id.
  5. Aggregate per doc with 1/sqrt(rank) chunk contributions.

Fair-fight config (init flags):
  * embedding: text-embedding-3-small (matches OIDA + LightRAG + HippoRAG)
  * LLM: gpt-4o-mini (matches LightRAG + HippoRAG defaults)
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

_REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPHRAG_DATA_ROOT = _REPO_ROOT / "experiments" / "systems" / "graphrag-data"

EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
DEFAULT_TOP_K = 20


# -- result types (contract) --------------------------------------------------


@dataclass
class IngestReport:
    doc_id: str
    source_uri: str
    committed: bool
    ko_ids: list[str] = field(default_factory=list)
    candidates_total: int = 0
    kos_created: int = 0
    kos_rejected: int = 0
    kos_quarantined: int = 0
    partial_error_count: int = 0
    chunks_ingested: int = 1
    latency_ms: float = 0.0
    error: str | None = None
    run_ids: list[str] = field(default_factory=list)


@dataclass
class RetrieveResult:
    doc_scores: dict[str, float]
    score_components: dict[str, dict[str, float]] | None
    raw_response_text: str | None
    latency_ms: float
    tokens_in: int = 0
    tokens_out: int = 0
    embed_tokens: int = 0
    notes: str | None = None


# -- client -------------------------------------------------------------------


def _sanitize_filename(doc_id: str) -> str:
    """Encode corpus.jsonl _id (possibly with /) into a flat filename.
    Use a Unicode-safe substitute that decodes uniquely back."""
    return doc_id.replace("/", "__SLASH__") + ".txt"


def _decode_filename(filename: str) -> str:
    """Inverse of _sanitize_filename."""
    stem = filename[:-4] if filename.endswith(".txt") else filename
    return stem.replace("__SLASH__", "/")


class GraphRagClient:
    """Per-corpus GraphRAG project on disk, retrieve via basic_search."""

    def __init__(self, corpus_slug: str, project_dir: Path | None = None) -> None:
        self.corpus_slug = corpus_slug
        self.project_dir = project_dir or (GRAPHRAG_DATA_ROOT / corpus_slug)
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.input_dir = self.project_dir / "input"
        self.output_dir = self.project_dir / "output"
        self._text_units: pd.DataFrame | None = None
        self._documents: pd.DataFrame | None = None
        self._config = None

    # -- init / index --------------------------------------------------------

    def init_project(self, force: bool = False) -> None:
        """Run `graphrag init` on the project dir."""
        if (self.project_dir / "settings.yaml").exists() and not force:
            return
        subprocess.run(
            [
                "graphrag", "init", "--root", str(self.project_dir),
                "--model", LLM_MODEL,
                "--embedding", EMBEDDING_MODEL,
            ] + (["--force"] if force else []),
            check=True, capture_output=True,
        )
        # Write GRAPHRAG_API_KEY into the per-project .env
        env_path = _REPO_ROOT / ".env"
        api_key = None
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip("'").strip('"')
                    break
        if api_key:
            (self.project_dir / ".env").write_text(
                f"GRAPHRAG_API_KEY={api_key}\n", encoding="utf-8"
            )

    def write_input_docs(self, corpus_dir: Path) -> list[str]:
        """Drop each doc as a separate .txt file in input/."""
        self.input_dir.mkdir(exist_ok=True)
        # Wipe any stale input
        for p in self.input_dir.iterdir():
            p.unlink()
        doc_ids: list[str] = []
        with (corpus_dir / "corpus.jsonl").open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                doc = json.loads(line)
                doc_id = doc["_id"]
                fn = _sanitize_filename(doc_id)
                text = (doc.get("title", "") + "\n\n" + doc["text"]).strip()
                (self.input_dir / fn).write_text(text, encoding="utf-8")
                doc_ids.append(doc_id)
        return doc_ids

    def run_index(self) -> tuple[bool, str | None, float]:
        """Run `graphrag index --root <dir>` as a subprocess. Returns
        (success, error_text, elapsed_sec)."""
        # Ensure GRAPHRAG_API_KEY is in env for the subprocess
        env = os.environ.copy()
        env_path = _REPO_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    env["GRAPHRAG_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
                    env["OPENAI_API_KEY"] = env["GRAPHRAG_API_KEY"]
                    break
        t0 = time.perf_counter()
        proc = subprocess.run(
            ["graphrag", "index", "--root", str(self.project_dir)],
            env=env, capture_output=True, text=True,
        )
        elapsed = time.perf_counter() - t0
        if proc.returncode != 0:
            return False, (proc.stderr or proc.stdout)[-2000:], elapsed
        return True, None, elapsed

    def ingest_corpus(self, corpus_dir: Path, force_reindex: bool = False) -> list[IngestReport]:
        """End-to-end: init project, write docs, run index."""
        self.init_project(force=False)
        doc_ids = self.write_input_docs(corpus_dir)
        # Skip indexing if output exists and not forced
        if not force_reindex and (self.output_dir / "documents.parquet").exists():
            elapsed_ms_per_doc = 0.0
            reports = [
                IngestReport(
                    doc_id=did,
                    source_uri=f"beir-corpora://{self.corpus_slug}/{did}",
                    committed=True,
                    latency_ms=elapsed_ms_per_doc,
                    error=None,
                )
                for did in doc_ids
            ]
            return reports
        ok, err, elapsed = self.run_index()
        per_doc_ms = (elapsed * 1000.0) / max(1, len(doc_ids))
        reports = [
            IngestReport(
                doc_id=did,
                source_uri=f"beir-corpora://{self.corpus_slug}/{did}",
                committed=ok,
                latency_ms=per_doc_ms,
                error=None if ok else (err or "")[:200],
            )
            for did in doc_ids
        ]
        return reports

    # -- retrieve ------------------------------------------------------------

    def _load_artifacts(self) -> None:
        if self._text_units is None:
            self._text_units = pd.read_parquet(self.output_dir / "text_units.parquet")
        if self._documents is None:
            self._documents = pd.read_parquet(self.output_dir / "documents.parquet")
        if self._config is None:
            os.environ.setdefault("GRAPHRAG_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
            from graphrag.config.load_config import load_config  # imported lazily
            self._config = load_config(self.project_dir)

    def _doc_id_for_chunk(self, chunk_id: str) -> str | None:
        """``basic_search`` returns ``sources.id`` as the chunk's
        ``human_readable_id`` (a small int rendered as a string), not the
        sha256-ish chunk hash. Match on that, with a hash fallback."""
        if self._text_units is None or self._documents is None:
            return None
        try:
            hr_id = int(chunk_id)
            rows = self._text_units.loc[self._text_units["human_readable_id"] == hr_id]
        except (ValueError, TypeError):
            rows = self._text_units.loc[self._text_units["id"] == chunk_id]
        if len(rows) == 0:
            return None
        document_id = rows.iloc[0]["document_id"]
        docs = self._documents.loc[self._documents["id"] == document_id]
        if len(docs) == 0:
            return None
        title = docs.iloc[0]["title"]
        return _decode_filename(title)

    def retrieve(self, query: str, top_k: int = DEFAULT_TOP_K) -> RetrieveResult:
        self._load_artifacts()
        from graphrag.api.query import basic_search
        result = RetrieveResult(
            doc_scores={},
            score_components={},
            raw_response_text=None,
            latency_ms=0.0,
        )
        t0 = time.perf_counter()
        try:
            response, context = asyncio.run(
                basic_search(
                    config=self._config,
                    text_units=self._text_units,
                    response_type="Single Paragraph",
                    query=query,
                )
            )
        except Exception as e:  # noqa: BLE001
            result.latency_ms = (time.perf_counter() - t0) * 1000.0
            result.notes = f"retrieve_error: {type(e).__name__}: {str(e)[:200]}"
            return result
        result.latency_ms = (time.perf_counter() - t0) * 1000.0
        result.raw_response_text = str(response)[:2000] if response else None

        if not isinstance(context, dict) or "sources" not in context:
            result.notes = "retrieve_failed: no sources in context"
            return result
        sources = context["sources"]
        if not hasattr(sources, "iterrows"):
            result.notes = "retrieve_failed: sources is not a DataFrame"
            return result

        doc_score: dict[str, float] = {}
        doc_components: dict[str, dict[str, float]] = {}
        doc_chunk_count: Counter = Counter()
        doc_first_rank: dict[str, int] = {}

        for rank, (_, row) in enumerate(sources.iterrows(), start=1):
            if rank > top_k:
                break
            chunk_id = row["id"]
            doc_id = self._doc_id_for_chunk(str(chunk_id))
            if not doc_id:
                continue
            score = 1.0 / (rank ** 0.5)
            doc_score[doc_id] = doc_score.get(doc_id, 0.0) + score
            doc_chunk_count[doc_id] += 1
            if doc_id not in doc_first_rank:
                doc_first_rank[doc_id] = rank

        for doc_id, score in doc_score.items():
            doc_components[doc_id] = {
                "graphrag_score": score,
                "contributing_chunks": float(doc_chunk_count.get(doc_id, 0)),
                "first_rank": float(doc_first_rank.get(doc_id, 0)),
            }

        result.doc_scores = dict(sorted(doc_score.items(), key=lambda kv: -kv[1]))
        result.score_components = doc_components
        result.notes = (
            f"basic_search chunks_returned={len(sources)} "
            f"docs_matched={len(doc_score)}"
        )
        return result


# -- env loader (shared shape) ------------------------------------------------


def _load_env(env_path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not env_path.exists():
        return out
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip()
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        elif v.startswith("'") and v.endswith("'"):
            v = v[1:-1]
        else:
            for sep in (" #", "\t#"):
                idx = v.find(sep)
                if idx != -1:
                    v = v[:idx].rstrip()
                    break
        out[k.strip()] = v
    return out


# -- CLI smoke ----------------------------------------------------------------


def _smoke(corpus_dir: Path) -> int:
    env = _load_env(_REPO_ROOT / ".env")
    if not env.get("OPENAI_API_KEY"):
        print("error: OPENAI_API_KEY missing from .env")
        return 2
    os.environ["OPENAI_API_KEY"] = env["OPENAI_API_KEY"]
    os.environ["GRAPHRAG_API_KEY"] = env["OPENAI_API_KEY"]

    corpus_slug = corpus_dir.name.split("-", 1)[-1] if "-" in corpus_dir.name else corpus_dir.name
    client = GraphRagClient(corpus_slug=corpus_slug)
    print(f"project_dir: {client.project_dir.relative_to(_REPO_ROOT)}")

    print(f"\n=== ingest (init + index) ===")
    t0 = time.perf_counter()
    reports = client.ingest_corpus(corpus_dir)
    n_ok = sum(1 for r in reports if r.committed)
    print(f"  {n_ok}/{len(reports)} OK in {(time.perf_counter()-t0):.1f}s")
    if reports and reports[0].error:
        print(f"  error: {reports[0].error[:300]}")

    with (corpus_dir / "queries.jsonl").open(encoding="utf-8") as fh:
        queries = [json.loads(line) for line in fh if line.strip()]
    q = queries[0]
    print(f"\n=== retrieve: {q['_id']} — {q['text'][:80]}... ===")
    res = client.retrieve(q["text"], top_k=10)
    print(f"  latency={res.latency_ms:.0f}ms docs={len(res.doc_scores)}")
    print(f"  notes: {res.notes}")
    for doc_id, score in list(res.doc_scores.items())[:5]:
        c = (res.score_components or {}).get(doc_id, {})
        print(f"  {score:.4f}  {doc_id}  (chunks={int(c.get('contributing_chunks',0))}, first_rank={int(c.get('first_rank',0))})")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python experiments/adapters/graphrag.py <corpus_dir>")
        return 2
    return _smoke(Path(argv[0]).resolve())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
