"""LightRAG adapter for the BEIR-style comparative retrieval experiment.

Maps LightRAG's in-process Python API onto the uniform adapter contract in
``experiments/EXPERIMENT_PLAN.md`` §6. LightRAG runs entirely local: each
corpus gets its own ``working_dir`` under ``experiments/systems/lightrag-data/<corpus>/``
which gives natural per-corpus isolation (something the deployed OIDA could
not provide).

Retrieval uses ``LightRAG.aquery_data`` (structured, no LLM generation) so
we get back a `chunks` list with ``file_path`` per chunk. At ingest time we
pass each document with ``file_paths=[doc_id]`` so the retrieved chunks
trace back to the BEIR-style ``corpus.jsonl`` ``_id``. Doc-level scores are
aggregated by counting chunks per file_path and reverse-ranking by
appearance order in the returned context.

Embedder: ``text-embedding-3-small`` (matches OIDA for fair-fight).
LLM (for ingest-time entity/relation extraction): ``gpt-4o-mini`` —
LightRAG's documented default. We deliberately keep this rather than
forcing ``gpt-4o`` to (1) stay within the cost cap and (2) reflect each
system's recommended default.

Run modes reported:
  * ``hybrid`` — entity + relationship retrieval combined (LightRAG default)
  * ``naive`` — chunk-only retrieval (no graph), used as a reference

Outputs match the adapter contract in plan §6 (RetrieveResult dataclass
shape). Token usage is captured from LightRAG's internal LLM-call
accounting where available; embed_tokens is null since the embedding
calls are batched internally.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add the cloned LightRAG to sys.path so the module resolves to our
# pinned clone (we install with `pip install -e .` so this should already
# work; the explicit insert is a belt-and-braces guard).
_REPO_ROOT = Path(__file__).resolve().parents[2]
_LIGHTRAG_DIR = _REPO_ROOT / "experiments" / "systems" / "lightrag"
if _LIGHTRAG_DIR.exists():
    sys.path.insert(0, str(_LIGHTRAG_DIR))

from lightrag import LightRAG, QueryParam  # noqa: E402
from lightrag.kg.shared_storage import initialize_pipeline_status  # noqa: E402
from lightrag.llm.openai import openai_complete_if_cache, openai_embed  # noqa: E402
from lightrag.utils import EmbeddingFunc  # noqa: E402


# -- constants ----------------------------------------------------------------

LIGHTRAG_DATA_ROOT = _REPO_ROOT / "experiments" / "systems" / "lightrag-data"

# Match OIDA's embedder for fair-fight comparison
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

# LightRAG default LLM for ingest-time entity/relation extraction
LLM_MODEL = "gpt-4o-mini"

DEFAULT_RETRIEVE_MODE = "hybrid"
DEFAULT_RETRIEVE_TOP_K = 40       # entity-level top_k
DEFAULT_RETRIEVE_CHUNK_TOP_K = 20 # chunk-level top_k (what we ultimately rank by)


# -- result types (contract) --------------------------------------------------


@dataclass
class IngestReport:
    """Per-doc ingest outcome — same shape as the OIDA adapter for uniformity."""

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
    """Per-query retrieval outcome — adapter contract per plan §6."""

    doc_scores: dict[str, float]
    score_components: dict[str, dict[str, float]] | None
    raw_response_text: str | None
    latency_ms: float
    tokens_in: int = 0
    tokens_out: int = 0
    embed_tokens: int = 0
    notes: str | None = None


# -- LLM/embedding wiring -----------------------------------------------------


async def _llm_complete(prompt, system_prompt=None, history_messages=None, **kwargs):
    """LightRAG's expected LLM-callable signature → OpenAI gpt-4o-mini."""
    return await openai_complete_if_cache(
        LLM_MODEL,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages or [],
        **kwargs,
    )


def _make_embedding_func() -> EmbeddingFunc:
    return EmbeddingFunc(
        embedding_dim=EMBEDDING_DIM,
        func=lambda texts: openai_embed(texts, model=EMBEDDING_MODEL),
    )


# -- client -------------------------------------------------------------------


class LightRagClient:
    """Async LightRAG client with per-corpus working_dir isolation."""

    def __init__(self, corpus_slug: str, working_dir: Path | None = None) -> None:
        self.corpus_slug = corpus_slug
        self.working_dir = working_dir or (LIGHTRAG_DATA_ROOT / corpus_slug)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self._rag: LightRAG | None = None

    async def init(self) -> None:
        if self._rag is not None:
            return
        rag = LightRAG(
            working_dir=str(self.working_dir),
            embedding_func=_make_embedding_func(),
            llm_model_func=_llm_complete,
        )
        await rag.initialize_storages()
        await initialize_pipeline_status()
        self._rag = rag

    async def close(self) -> None:
        if self._rag is not None:
            # LightRAG storages buffer to disk; finalize gracefully if available.
            finalize = getattr(self._rag, "finalize_storages", None)
            if finalize is not None:
                try:
                    await finalize()
                except Exception:  # noqa: BLE001
                    pass

    # -- ingest --------------------------------------------------------------

    async def ingest_doc(
        self,
        doc_id: str,
        text: str,
        title: str | None = None,
    ) -> IngestReport:
        await self.init()
        assert self._rag is not None
        if title:
            full_text = f"{title}\n\n{text}"
        else:
            full_text = text
        report = IngestReport(
            doc_id=doc_id,
            source_uri=f"beir-corpora://{self.corpus_slug}/{doc_id}",
            committed=False,
        )
        t0 = time.perf_counter()
        try:
            await self._rag.ainsert(
                full_text,
                ids=[doc_id],
                file_paths=[doc_id],
            )
            report.committed = True
        except Exception as e:  # noqa: BLE001
            report.error = f"{type(e).__name__}: {str(e)[:200]}"
        report.latency_ms = (time.perf_counter() - t0) * 1000.0
        return report

    async def ingest_corpus(
        self,
        corpus_dir: Path,
        on_progress=None,
    ) -> list[IngestReport]:
        reports: list[IngestReport] = []
        with (corpus_dir / "corpus.jsonl").open(encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                doc = json.loads(line)
                rep = await self.ingest_doc(
                    doc["_id"],
                    doc["text"],
                    title=doc.get("title"),
                )
                reports.append(rep)
                if on_progress:
                    on_progress(i, doc["_id"], rep)
        return reports

    # -- retrieve ------------------------------------------------------------

    async def retrieve(
        self,
        query: str,
        mode: str = DEFAULT_RETRIEVE_MODE,
        top_k: int = DEFAULT_RETRIEVE_TOP_K,
        chunk_top_k: int = DEFAULT_RETRIEVE_CHUNK_TOP_K,
        enable_rerank: bool = False,
    ) -> RetrieveResult:
        await self.init()
        assert self._rag is not None
        param = QueryParam(
            mode=mode,
            top_k=top_k,
            chunk_top_k=chunk_top_k,
            enable_rerank=enable_rerank,
        )
        result = RetrieveResult(
            doc_scores={},
            score_components={},
            raw_response_text=None,
            latency_ms=0.0,
        )
        t0 = time.perf_counter()
        try:
            data = await self._rag.aquery_data(query, param=param)
        except Exception as e:  # noqa: BLE001
            result.latency_ms = (time.perf_counter() - t0) * 1000.0
            result.notes = f"retrieve_error: {type(e).__name__}: {str(e)[:200]}"
            return result
        result.latency_ms = (time.perf_counter() - t0) * 1000.0

        if not isinstance(data, dict) or data.get("status") != "success":
            result.notes = f"retrieve_failed: status={data.get('status') if isinstance(data, dict) else type(data).__name__}"
            return result

        chunks = (data.get("data") or {}).get("chunks") or []
        # Doc-level score: chunks appear in rank order; we score by
        # 1 / sqrt(rank) and aggregate (sum) per doc. This rewards docs that
        # appear early AND multiple times in the retrieved context.
        doc_score: dict[str, float] = {}
        doc_chunk_count: dict[str, int] = Counter()
        doc_first_rank: dict[str, int] = {}
        for rank, ch in enumerate(chunks, start=1):
            doc_id = ch.get("file_path")
            if not doc_id:
                continue
            doc_score[doc_id] = doc_score.get(doc_id, 0.0) + 1.0 / (rank ** 0.5)
            doc_chunk_count[doc_id] += 1
            if doc_id not in doc_first_rank:
                doc_first_rank[doc_id] = rank
        # Also fold in entities/relationships that have file_paths — weight half.
        for kind in ("entities", "relationships"):
            for item in (data.get("data") or {}).get(kind) or []:
                doc_id = item.get("file_path")
                if not doc_id:
                    continue
                doc_score[doc_id] = doc_score.get(doc_id, 0.0) + 0.5

        # Capture score components for diagnostics
        comp: dict[str, dict[str, float]] = {}
        for doc_id, score in doc_score.items():
            comp[doc_id] = {
                "lightrag_score": score,
                "contributing_chunks": float(doc_chunk_count.get(doc_id, 0)),
                "first_rank": float(doc_first_rank.get(doc_id, 0)),
            }
        result.doc_scores = dict(sorted(doc_score.items(), key=lambda kv: -kv[1]))
        result.score_components = comp

        meta = data.get("metadata") or {}
        pinfo = meta.get("processing_info") or {}
        result.notes = (
            f"mode={mode} chunks_returned={len(chunks)} "
            f"docs_matched={len(doc_score)} "
            f"entities={pinfo.get('entities_after_truncation','?')} "
            f"relations={pinfo.get('relations_after_truncation','?')}"
        )
        return result


# -- env loader (mirrors oida adapter's _load_env) ----------------------------


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


# -- CLI smoke test -----------------------------------------------------------


async def _smoke(corpus_dir: Path) -> int:
    env = _load_env(_REPO_ROOT / ".env")
    if not env.get("OPENAI_API_KEY"):
        print("error: OPENAI_API_KEY missing from .env")
        return 2
    # Push key into env for the OpenAI client used by LightRAG
    os.environ["OPENAI_API_KEY"] = env["OPENAI_API_KEY"]

    corpus_slug = corpus_dir.name.split("-", 1)[-1] if "-" in corpus_dir.name else corpus_dir.name
    client = LightRagClient(corpus_slug=corpus_slug)
    print(f"working_dir: {client.working_dir.relative_to(_REPO_ROOT)}")
    await client.init()

    # Pick the shortest doc for smoke
    with (corpus_dir / "corpus.jsonl").open(encoding="utf-8") as fh:
        candidates = [json.loads(line) for line in fh if line.strip()]
    short = sorted(candidates, key=lambda r: len(r["text"]))[0]
    print(f"\nsmoke ingest: {short['_id']} ({len(short['text'])} chars)")
    rep = await client.ingest_doc(short["_id"], short["text"], title=short.get("title"))
    print(f"  committed={rep.committed} latency={rep.latency_ms:.0f}ms err={rep.error}")

    # First query
    with (corpus_dir / "queries.jsonl").open(encoding="utf-8") as fh:
        queries = [json.loads(line) for line in fh if line.strip()]
    q = queries[0]
    print(f"\nsmoke retrieve: {q['_id']} — {q['text'][:80]}...")
    res = await client.retrieve(q["text"], top_k=20, chunk_top_k=10)
    print(f"  latency={res.latency_ms:.0f}ms docs={len(res.doc_scores)}")
    print(f"  notes: {res.notes}")
    for doc_id, score in list(res.doc_scores.items())[:5]:
        c = (res.score_components or {}).get(doc_id, {})
        print(f"  {score:.4f}  {doc_id}  (chunks={int(c.get('contributing_chunks',0))}, first_rank={int(c.get('first_rank',0))})")

    await client.close()
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python experiments/adapters/lightrag.py <corpus_dir>")
        return 2
    return asyncio.run(_smoke(Path(argv[0]).resolve()))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
