"""HippoRAG adapter for the BEIR-style comparative retrieval experiment.

Maps HippoRAG 2.x's Python API onto the uniform adapter contract in
``experiments/EXPERIMENT_PLAN.md`` §6. HippoRAG runs entirely local with
per-corpus storage under ``experiments/systems/hipporag-data/<corpus>/``
(BaseConfig.save_dir), giving natural per-corpus isolation like LightRAG.

Key API surface used:
  * ``HippoRAG.index(docs: List[str])`` — OpenIE-based KG construction +
    dense embedding store.
  * ``HippoRAG.retrieve(queries, num_to_retrieve)`` — returns
    ``List[QuerySolution]`` whose ``docs`` and ``doc_scores`` map directly
    to a BEIR-shaped (doc_id → score) dict.

HippoRAG identifies documents by their text content, NOT by an external ID.
To trace the retrieved ``docs`` back to corpus.jsonl ``_id`` we maintain a
text-hash ↔ doc_id map per corpus, written at ingest time and consulted at
retrieve time.

Fair-fight config:
  * embedding_model_name = "text-embedding-3-small" (matches OIDA + LightRAG)
  * llm_name             = "gpt-4o-mini" (HippoRAG documented default)
  * graph_type           = "facts_and_sim_passage_node_unidirectional"
                           (HippoRAG default)

The vendored HippoRAG repo at experiments/systems/hipporag/ has been
patched to lazy-load vLLM / transformers-offline / outlines / bedrock
imports so the package installs and imports cleanly on CPU-only Mac
without those GPU/cloud deps.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ensure the vendored HippoRAG src/ is first on sys.path so the editable
# install resolves there
_REPO_ROOT = Path(__file__).resolve().parents[2]
_HIPPORAG_DIR = _REPO_ROOT / "experiments" / "systems" / "hipporag"
if _HIPPORAG_DIR.exists():
    sys.path.insert(0, str(_HIPPORAG_DIR / "src"))

from hipporag import HippoRAG  # noqa: E402
from hipporag.utils.config_utils import BaseConfig  # noqa: E402


HIPPORAG_DATA_ROOT = _REPO_ROOT / "experiments" / "systems" / "hipporag-data"
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"


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


def _text_for_index(doc_id: str, title: str | None, body: str) -> str:
    """Compose the text we hand to HippoRAG.index — title + body."""
    if title:
        return f"{title}\n\n{body}".strip()
    return body.strip()


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:16]


class HippoRagClient:
    """Sync HippoRAG client. Indexing + retrieve are batched by HippoRAG's
    internal API, so we accumulate docs and ingest them in one shot per
    corpus (matches HippoRAG's intended usage pattern)."""

    def __init__(self, corpus_slug: str, save_dir: Path | None = None) -> None:
        self.corpus_slug = corpus_slug
        self.save_dir = save_dir or (HIPPORAG_DATA_ROOT / corpus_slug)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        # text-hash → corpus.jsonl _id map (round-trip for BEIR scoring)
        self._idmap_path = self.save_dir / "_doc_id_map.json"
        self._idmap: dict[str, str] = {}
        if self._idmap_path.exists():
            try:
                self._idmap = json.loads(self._idmap_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._idmap = {}
        self._rag: HippoRAG | None = None

    def _save_idmap(self) -> None:
        self._idmap_path.write_text(json.dumps(self._idmap, indent=2), encoding="utf-8")

    def _make_rag(self) -> HippoRAG:
        config = BaseConfig()
        config.save_dir = str(self.save_dir)
        config.llm_name = LLM_MODEL
        config.embedding_model_name = EMBEDDING_MODEL
        config.dataset = self.corpus_slug
        # Reduce noisy log output during smoke / batch runs (HippoRAG is verbose)
        config.force_index_from_scratch = False
        config.force_openie_from_scratch = False
        return HippoRAG(global_config=config, save_dir=str(self.save_dir))

    def init(self) -> None:
        if self._rag is None:
            self._rag = self._make_rag()

    # -- ingest --------------------------------------------------------------

    def ingest_corpus(self, corpus_dir: Path, on_progress=None) -> list[IngestReport]:
        """HippoRAG indexes in one batch — we load all docs, register the
        id-map, then call index() once. Per-doc IngestReports are
        synthesized from the batch outcome."""
        self.init()
        assert self._rag is not None

        docs_text: list[str] = []
        doc_ids: list[str] = []
        titles: list[str | None] = []
        with (corpus_dir / "corpus.jsonl").open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                doc = json.loads(line)
                t = _text_for_index(doc["_id"], doc.get("title"), doc["text"])
                docs_text.append(t)
                doc_ids.append(doc["_id"])
                titles.append(doc.get("title"))
                self._idmap[_text_hash(t)] = doc["_id"]
        self._save_idmap()

        t0 = time.perf_counter()
        error: str | None = None
        try:
            self._rag.index(docs_text)
            committed = True
        except Exception as e:  # noqa: BLE001
            committed = False
            error = f"{type(e).__name__}: {str(e)[:200]}"
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        per_doc_latency = elapsed_ms / max(1, len(docs_text))
        reports: list[IngestReport] = []
        for i, doc_id in enumerate(doc_ids, start=1):
            rep = IngestReport(
                doc_id=doc_id,
                source_uri=f"beir-corpora://{self.corpus_slug}/{doc_id}",
                committed=committed,
                latency_ms=per_doc_latency,
                error=error,
            )
            reports.append(rep)
            if on_progress:
                on_progress(i, doc_id, rep)
        return reports

    # -- retrieve ------------------------------------------------------------

    def retrieve(self, query: str, num_to_retrieve: int = 20) -> RetrieveResult:
        self.init()
        assert self._rag is not None
        result = RetrieveResult(
            doc_scores={},
            score_components={},
            raw_response_text=None,
            latency_ms=0.0,
        )
        t0 = time.perf_counter()
        try:
            solutions = self._rag.retrieve(
                queries=[query],
                num_to_retrieve=num_to_retrieve,
            )
        except Exception as e:  # noqa: BLE001
            result.latency_ms = (time.perf_counter() - t0) * 1000.0
            result.notes = f"retrieve_error: {type(e).__name__}: {str(e)[:200]}"
            return result
        result.latency_ms = (time.perf_counter() - t0) * 1000.0

        if not solutions or not isinstance(solutions, list):
            result.notes = "retrieve_failed: empty solutions"
            return result
        sol = solutions[0]
        retrieved_docs = list(sol.docs or [])
        scores = sol.doc_scores
        # Convert numpy array if needed
        try:
            scores_list = list(scores)
        except Exception:  # noqa: BLE001
            scores_list = []

        translated: dict[str, float] = {}
        components: dict[str, dict[str, float]] = {}
        for i, (text, sc) in enumerate(zip(retrieved_docs, scores_list)):
            mapped = self._idmap.get(_text_hash(text), None)
            if mapped is None:
                # try without strip / whitespace nuance
                mapped = self._idmap.get(_text_hash(text.strip()), text[:50])
            score = float(sc)
            if mapped in translated:
                translated[mapped] = max(translated[mapped], score)
            else:
                translated[mapped] = score
            components[mapped] = {
                "hipporag_ppr_score": score,
                "retrieval_rank": float(i + 1),
            }
        result.doc_scores = dict(sorted(translated.items(), key=lambda kv: -kv[1]))
        result.score_components = components
        result.notes = f"retrieved {len(retrieved_docs)} docs, mapped {sum(1 for k in translated if k in self._idmap.values())}"
        return result


# -- env loader (same shape as the other adapters) ----------------------------


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

    corpus_slug = corpus_dir.name.split("-", 1)[-1] if "-" in corpus_dir.name else corpus_dir.name
    client = HippoRagClient(corpus_slug=corpus_slug)
    print(f"save_dir: {client.save_dir.relative_to(_REPO_ROOT)}")

    print(f"\nsmoke index: full corpus in one batch")
    t0 = time.perf_counter()
    reports = client.ingest_corpus(corpus_dir)
    n_ok = sum(1 for r in reports if r.committed)
    print(f"  {n_ok}/{len(reports)} OK in {(time.perf_counter()-t0):.1f}s")

    with (corpus_dir / "queries.jsonl").open(encoding="utf-8") as fh:
        queries = [json.loads(line) for line in fh if line.strip()]
    q = queries[0]
    print(f"\nsmoke retrieve: {q['_id']} — {q['text'][:80]}...")
    res = client.retrieve(q["text"], num_to_retrieve=10)
    print(f"  latency={res.latency_ms:.0f}ms docs={len(res.doc_scores)}")
    print(f"  notes: {res.notes}")
    for doc_id, score in list(res.doc_scores.items())[:5]:
        c = (res.score_components or {}).get(doc_id, {})
        rank = int(c.get("retrieval_rank", 0))
        print(f"  {score:.4f}  rank={rank}  {doc_id}")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python experiments/adapters/hipporag.py <corpus_dir>")
        return 2
    return _smoke(Path(argv[0]).resolve())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
