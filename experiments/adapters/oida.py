"""OIDA HTTP-API adapter for the BEIR-style comparative retrieval experiment.

Maps the OIDA `/ingest` + `/retrieve/full-oida` endpoints onto the uniform
adapter contract in `experiments/EXPERIMENT_PLAN.md` §6. v0 retrieve mode is
used (not the newer v1 probe configuration) because v0 is the only one that
exposes `supporting_sources` per KO — the back-link we need to map KOs to
the corpus.jsonl `_id` for BEIR scoring. The v0 thresholds are pinned to
`tauBind=0.2, tauFallback=0.1` (the calibration sweet spot found in the
2026-05-19 SciFact run; see EXPERIMENT_PLAN.md §10).

Smoke-tested 2026-05-28 against deploy `d1cad80b` on
`https://angelicadb-kva.onrender.com`. Two operational findings carried
forward into this adapter:

  1. **Prisma transaction timeout (5 s).** Dense documents that decompose into
     ~100+ candidate KOs blow the interactive transaction window. We slice
     long documents into smaller chunks at ingest time (default ≤ 4000 chars
     per chunk), each ingested as a separate `/ingest` call sharing the same
     ``source`` URI so retrieval still aggregates them to the right doc.

  2. **Project isolation.** The deployed ``default`` project carries residual
     KOs from prior tests (SciFact, smoke runs). The public API surface does
     not expose project creation, so per-corpus isolation requires either
     (a) a fresh project + API key minted via Render Shell out of band, or
     (b) tolerating the residue and filtering by ``source`` URI prefix at
     retrieve time. This adapter defaults to (b) — it filters the v0
     response to only KOs whose ``supporting_sources[0]`` starts with the
     configured ``source_uri_prefix``.

Doc ↔ KO mapping convention: every doc is ingested with
``source = "<source_uri_prefix>/<corpus.jsonl _id>"`` (e.g.
``beir-corpora://clearpath/05-meetings/meeting-005-final-presentation``).
At retrieve time, KOs whose ``supporting_sources[0]`` matches that pattern
are aggregated to their parent doc and scored with
``max(regime_adjusted_score)`` across all KOs sharing the same source.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest


# -- defaults / constants -----------------------------------------------------

DEFAULT_BASE_URL = "https://angelicadb-kva.onrender.com"
DEFAULT_SOURCE_URI_PREFIX = "beir-corpora"  # → beir-corpora://<corpus>/<doc_id>
DEFAULT_INGEST_CHUNK_CHARS = 2000  # smaller chunks → fewer KOs per commit (remediation B);
# pairs with the server-side widened Prisma tx window (remediation C) for margin.
DEFAULT_RETRIEVE_LIMIT = 100
DEFAULT_TAU_BIND = 0.2
DEFAULT_TAU_FALLBACK = 0.1
DEFAULT_TIMEOUT_SEC = 600  # dense meeting transcripts can take 5-10 min server-side
DEFAULT_RETRY_ATTEMPTS = 1  # retries waste time when the call is intrinsically slow; fail fast
DEFAULT_RETRY_BACKOFF_SEC = 5.0

# All ingest/retrieve calls authenticate via OIDA_ADMIN_KEY and land in the
# shared ``default`` project. This is a deliberate workaround for an
# operational reality of the deployed angelica-db:
#
#   • The admin bearer auth bypass forces every request into the ``default``
#     project regardless of ``x-project-id`` header or ``projectId`` body
#     field (tested 2026-05-28).
#   • Minting per-corpus project-scoped api_keys directly in Postgres
#     produced rows with matching sha256 hashes but auth still returned
#     ``INVALID_API_KEY`` — likely an in-app key cache or alternate auth
#     path not documented in the oida-core subset docs.
#
# Per-corpus isolation is therefore enforced **at retrieve time** by
# filtering KOs whose ``supporting_sources[0]`` starts with the corpus-
# specific URI prefix ``beir-corpora://<corpus_slug>/...``. The ingest side
# tags every document at write time with this URI; retrieve drops any KO
# from the response whose source does not match the corpus_slug we are
# scoring for. SciFact residue and cross-corpus KOs are excluded by this
# filter even though they share the same project.
#
# This shared-project model is acceptable for a one-shot benchmark run; it
# is documented in EXPERIMENT_PLAN.md §10.
CORPUS_TO_PROJECT_SLUG: dict[str, str] = {
    "org-consulting-clearpath": "default",
    "org-iot-fireglass":         "default",
    "org-vc-vertexminds":        "default",
    "inv-mystery-redhood":       "default",
    "inv-ashford-mystery":       "default",
}

# Registry of supported OIDA deploys. Each entry is `{ base_url_env,
# admin_key_env, default_base_url }`. The CLI scripts (01_ingest.py,
# 02_retrieve.py) expose `--system` with `OIDA_DEPLOYS.keys()` as choices
# and resolve env via `resolve_deploy(system, env)` below. Adding a new
# deploy means adding a row here and exporting the matching env vars; no
# other code change required.
OIDA_DEPLOYS: dict[str, dict[str, str]] = {
    "oida-angelicadb": {
        "base_url_env":     "OIDA_BASE_URL",
        "admin_key_env":    "OIDA_ADMIN_KEY",
        "default_base_url": "https://angelicadb-kva.onrender.com",
        "description":      "Full AngelicaDB binary (kakashi-ventures/angelicadb), Render Oregon.",
    },
    "oida-core": {
        "base_url_env":     "OIDA_CORE_BASE_URL",
        "admin_key_env":    "OIDA_CORE_ADMIN_KEY",
        "default_base_url": "https://oida-core.onrender.com",
        "description":      "Scaffold B-Vendor (kakashi-ventures/oida-core), Render Frankfurt.",
    },
}


def resolve_deploy(system: str, env: dict[str, str]) -> tuple[str, str]:
    """Return ``(base_url, admin_key)`` for the named OIDA deploy.

    ``system`` must be a key of ``OIDA_DEPLOYS``. Raises ``ValueError`` for
    an unknown system, ``RuntimeError`` if the corresponding admin-key env
    var is missing.
    """
    if system not in OIDA_DEPLOYS:
        raise ValueError(
            f"unknown OIDA system: {system!r} (allowed: {sorted(OIDA_DEPLOYS)})"
        )
    cfg = OIDA_DEPLOYS[system]
    admin = env.get(cfg["admin_key_env"], "")
    if not admin:
        raise RuntimeError(
            f"{cfg['admin_key_env']} missing from .env for system={system}. "
            f"It should be the admin bearer for {cfg['default_base_url']}."
        )
    base = env.get(cfg["base_url_env"], cfg["default_base_url"])
    return base, admin


# Per-corpus project isolation (remediation A) — oida-core only.
#
# On oida-core each corpus lives in its OWN project (seeded by
# ``scripts/seed-bench-projects.ts``), so the projectId-scoped solver +
# pgvector search walk only that corpus's KOs (a few hundred) instead of the
# shared ``default`` pile (~7,700). This is what makes ``top_k=100`` feasible
# and brings retrieve latency back to sub-second. Ingest lands in the API
# key's OWN project (the ``x-project-id`` header is ignored for Bearer-key
# auth), so each corpus also has its own key ``OIDA_CORE_KEY_<SLUG>``.
#
# angelica-db keeps the legacy shared-``default`` + source-URI-filter path
# (it is a black box we cannot re-seed); see resolve_corpus_routing below.
OIDA_CORE_PROJECT_IDS: dict[str, str] = {
    "org-consulting-clearpath": "oida-clearpath",
    "org-iot-fireglass":         "oida-fireglass",
    "org-vc-vertexminds":        "oida-vertexminds",
    "inv-mystery-redhood":       "oida-redhood",
    "inv-ashford-mystery":       "oida-ashford",
}


def resolve_corpus_routing(
    system: str, corpus: str, env: dict[str, str]
) -> tuple[str, str]:
    """Return ``(project_id, api_key)`` for a (deploy, corpus) pair.

    - ``oida-core``: the corpus's dedicated project id (``oida-<slug>``) plus
      its per-corpus key ``OIDA_CORE_KEY_<SLUG>`` (falls back to
      ``OIDA_CORE_ADMIN_KEY`` if the per-corpus key is absent — but then ingest
      would land in the admin key's project, defeating isolation, so a missing
      per-corpus key is reported loudly).
    - ``oida-angelicadb`` (legacy): shared ``default`` project + ``OIDA_ADMIN_KEY``.
    """
    if system == "oida-core":
        project_id = OIDA_CORE_PROJECT_IDS.get(corpus)
        if not project_id:
            raise ValueError(f"no oida-core project mapping for corpus {corpus!r}")
        slug = project_id.split("-", 1)[1]
        key = env.get(f"OIDA_CORE_KEY_{slug.upper()}")
        if not key:
            raise RuntimeError(
                f"OIDA_CORE_KEY_{slug.upper()} missing from .env. "
                f"Run oida-core scripts/seed-bench-projects.ts and add the minted key. "
                f"Without a per-corpus key, ingest cannot isolate {corpus!r} into "
                f"project {project_id!r}."
            )
        return project_id, key
    # angelica-db / default path
    admin = env.get("OIDA_ADMIN_KEY", "")
    if not admin:
        raise RuntimeError("OIDA_ADMIN_KEY missing from .env for system=oida-angelicadb")
    return "default", admin


def warmup(base_url: str, timeout_sec: float = 90.0, poll_interval: float = 5.0) -> bool:
    """Ping ``GET /health`` until it returns 200 (remediation E).

    Render Starter sleeps after 15 min idle; the first real request would
    otherwise eat the 30-60 s cold-start. Returns True once warm, False on
    timeout (the caller proceeds either way — warm-up is best-effort).
    """
    url = base_url.rstrip("/") + "/health"
    deadline = time.time() + timeout_sec
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            req = urlrequest.Request(url, method="GET")
            with urlrequest.urlopen(req, timeout=20) as resp:
                if resp.status == 200:
                    if attempt > 1:
                        print(f"  warmup: {url} ready after {attempt} attempt(s)")
                    return True
        except (TimeoutError, urlerror.URLError, ConnectionError, OSError):
            pass
        time.sleep(poll_interval)
    print(f"  warmup: {url} not ready after {timeout_sec:.0f}s — proceeding anyway")
    return False


def resolve_corpus_credentials(corpus_dir: Path, env: dict[str, str]) -> tuple[str, str]:
    """Look up the (admin_key, project_slug) for a corpus by directory name.

    Legacy single-deploy helper kept for backward compatibility with the
    adapter's `_smoke` entrypoint. All corpora authenticate with
    ``OIDA_ADMIN_KEY`` and use the shared ``default`` project. New CLI
    scripts should use ``resolve_deploy(system, env)`` instead so they can
    select between angelica-db and oida-core. See the module docstring for
    why per-corpus project routing was abandoned in favor of source-URI
    filtering at retrieve.
    """
    admin = env.get("OIDA_ADMIN_KEY", "")
    if not admin:
        raise RuntimeError(
            "OIDA_ADMIN_KEY missing from .env. "
            "It should be the env-var admin bearer of the angelica-db deploy."
        )
    project_slug = CORPUS_TO_PROJECT_SLUG.get(corpus_dir.name, "default")
    return admin, project_slug

# OpenAI pricing as of 2026-05-28 (USD per 1M tokens). Used for layer-5 cost
# accounting at adapter level — the live cost is whatever OpenAI bills the
# OIDA deploy, not us; this is an *imputed* per-query cost so we can compare
# systems on a like-for-like basis.
PRICE_PER_M_TOKENS = {
    "openai/text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "openai/gpt-4o": {"input": 2.5, "output": 10.0},
}


# -- result shape (contract) --------------------------------------------------


@dataclass
class IngestReport:
    """Per-doc ingest outcome."""

    doc_id: str  # corpus.jsonl _id
    source_uri: str  # the URI we passed in `source`
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
class DocScore:
    """A doc-level score aggregated from one or more KOs."""

    doc_id: str
    score: float
    contributing_kos: int
    score_components: dict[str, float]  # similarity, kge_score, regime_adjusted_score, ...


@dataclass
class RetrieveResult:
    """Per-query retrieval outcome (adapter contract — EXPERIMENT_PLAN.md §6)."""

    doc_scores: dict[str, float]
    score_components: dict[str, dict[str, float]] | None
    raw_response_text: str | None
    latency_ms: float
    tokens_in: int = 0
    tokens_out: int = 0
    embed_tokens: int = 0
    notes: str | None = None
    # --- v0 epistemic retention (P0-S6) ---------------------------------------
    # Falsification contract (these three fields):
    #   WHAT they measure: the dialectical content the v0 /retrieve/full-oida
    #     server already emits — `subgraph.dialectic_resolutions` (verbatim) and
    #     the subset of `subgraph.edges` whose `contradiction_flag is True`, plus
    #     a count of that subset. NOT raw_response_text (v0 never populates it)
    #     and NOT a `subgraph.contradictions` key (v0 does not emit one).
    #   HOW computed: pure structural retention — copied/filtered straight from
    #     the response JSON, no scoring/derivation/inference. count == len(subset).
    #   WHERE stored: serialized into each `02_retrieve.py` per-query record
    #     (output/retrieve_runs/.../*.jsonl) alongside doc_scores; NOT written to
    #     runs_beir / runs.json / runs.tsv (BEIR ranking inputs stay byte-identical).
    #   WHAT behavior changes: NONE today — no scored consumer reads these fields
    #     (S4/S5 ignore them; proven inert in the P0-S6 acceptance gate). They are
    #     additive plumbing so a later layer can exercise v0 dialectics without
    #     re-running retrieval. Defaults keep every existing constructor valid.
    dialectic_resolutions: list = field(default_factory=list)
    contradiction_edges: list = field(default_factory=list)
    contradiction_edge_count: int = 0


# -- HTTP client --------------------------------------------------------------


class OidaClient:
    """Thin synchronous client over the two OIDA HTTP endpoints."""

    def __init__(
        self,
        admin_key: str,
        base_url: str = DEFAULT_BASE_URL,
        source_uri_prefix: str = DEFAULT_SOURCE_URI_PREFIX,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
        ingest_chunk_chars: int = DEFAULT_INGEST_CHUNK_CHARS,
        project_id_override: str | None = None,
    ) -> None:
        if not admin_key:
            raise ValueError("OIDA admin key is required")
        self.admin_key = admin_key
        self.base_url = base_url.rstrip("/")
        self.source_uri_prefix = source_uri_prefix
        self.timeout_sec = timeout_sec
        self.ingest_chunk_chars = ingest_chunk_chars
        self.project_id_override = project_id_override

    # -- low-level HTTP -------------------------------------------------------

    def _post(self, path: str, payload: dict) -> tuple[int, dict, float]:
        url = f"{self.base_url}{path}"
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.admin_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.project_id_override:
            headers["x-project-id"] = self.project_id_override
        last_err: str | None = None
        t0 = time.perf_counter()
        for attempt in range(DEFAULT_RETRY_ATTEMPTS):
            req = urlrequest.Request(url, data=body, headers=headers, method="POST")
            try:
                with urlrequest.urlopen(req, timeout=self.timeout_sec) as resp:
                    raw = resp.read().decode("utf-8")
                    status = resp.status
                latency_ms = (time.perf_counter() - t0) * 1000.0
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    data = {"error": {"message": "non-JSON response", "raw": raw[:500]}}
                return status, data, latency_ms
            except urlerror.HTTPError as e:
                raw = e.read().decode("utf-8") if e.fp else "{}"
                latency_ms = (time.perf_counter() - t0) * 1000.0
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    data = {"error": {"message": "non-JSON response", "raw": raw[:500]}}
                return e.code, data, latency_ms
            except (TimeoutError, urlerror.URLError, ConnectionError, OSError) as e:
                last_err = type(e).__name__ + ": " + str(e)[:200]
                if attempt < DEFAULT_RETRY_ATTEMPTS - 1:
                    time.sleep(DEFAULT_RETRY_BACKOFF_SEC * (attempt + 1))
        # All retries exhausted — return as a structured error rather than raising
        latency_ms = (time.perf_counter() - t0) * 1000.0
        return 0, {"error": {"code": "NETWORK_ERROR", "message": last_err or "unknown"}}, latency_ms

    # -- ingest ---------------------------------------------------------------

    def _build_source_uri(self, corpus_slug: str, doc_id: str) -> str:
        # canonical form: beir-corpora://<corpus_slug>/<doc_id>
        return f"{self.source_uri_prefix}://{corpus_slug}/{doc_id}"

    def _split_text(self, text: str) -> list[str]:
        """Split long text into chunks at paragraph boundaries when possible."""
        if len(text) <= self.ingest_chunk_chars:
            return [text]
        chunks: list[str] = []
        remaining = text
        while remaining:
            if len(remaining) <= self.ingest_chunk_chars:
                chunks.append(remaining)
                break
            window = remaining[: self.ingest_chunk_chars]
            # prefer to break at the last double-newline (paragraph)
            split = window.rfind("\n\n")
            if split < self.ingest_chunk_chars // 2:
                # fall back to single newline
                split = window.rfind("\n")
            if split < self.ingest_chunk_chars // 2:
                # fall back to whitespace, then to hard char split
                split = window.rfind(" ")
            if split <= 0:
                split = self.ingest_chunk_chars
            chunks.append(remaining[:split].rstrip())
            remaining = remaining[split:].lstrip()
        return chunks

    @staticmethod
    def _infer_source_type(doc: dict) -> tuple[str, str]:
        """Map corpus.jsonl metadata.category → (sourceType, ingestionMode)."""
        cat = (doc.get("metadata", {}) or {}).get("category", "").lower()
        if cat in {"email", "internal-comms", "external-comms"} or "email" in cat:
            return "EMAIL", "Capture"
        if cat in {"meetings", "meeting"}:
            return "MEET", "Meeting"
        if cat in {"market-context", "documents"}:
            return "RESEARCH", "Curated"
        if cat in {"slack"}:
            return "SLACK", "Capture"
        if cat in {"agenda", "scope", "subject"}:
            return "NOTION", "Curated"
        return "MANUAL", "Capture"

    def ingest_doc(self, corpus_slug: str, doc: dict, author: str | None = None) -> IngestReport:
        """Ingest one corpus.jsonl record. Splits into chunks if needed."""
        doc_id = doc["_id"]
        source_uri = self._build_source_uri(corpus_slug, doc_id)
        title = doc.get("title", "") or ""
        text_full = (title + "\n\n" + doc["text"]).strip()
        chunks = self._split_text(text_full)
        source_type, ingestion_mode = self._infer_source_type(doc)
        report = IngestReport(
            doc_id=doc_id,
            source_uri=source_uri,
            committed=False,
            chunks_ingested=len(chunks),
        )
        wall_clock_t0 = time.perf_counter()
        for chunk_idx, chunk in enumerate(chunks):
            payload = {
                "source": source_uri if len(chunks) == 1 else f"{source_uri}#chunk-{chunk_idx}",
                "sourceType": source_type,
                "ingestionMode": ingestion_mode,
                "author": author or f"bench@{corpus_slug}.local",
                "text": chunk,
                "mode": "commit",
                "permissions": {"scope": "project", "sensitivity": 1, "visibleTo": []},
                # P2-S1a — per-document effective date (corpus metadata.created).
                # None when the doc has no `created` → engine stores NULL.
                "effectiveDate": (doc.get("metadata") or {}).get("created"),
            }
            status, data, _ = self._post("/ingest", payload)
            if status == 401:
                report.error = "INVALID_KEY"
                break
            committed = bool(data.get("committed"))
            report.committed = report.committed or committed  # any chunk that committed counts
            report.candidates_total += int(data.get("candidatesTotal") or data.get("eipResult", {}).get("candidatesTotal") or 0)
            report.kos_created += int(data.get("kosCreated") or 0)
            report.kos_rejected += int(data.get("kosRejected") or 0)
            report.kos_quarantined += int(data.get("kosQuarantined") or 0)
            partial = data.get("partialErrors") or []
            report.partial_error_count += len(partial)
            run_id = data.get("runId") or data.get("eipResult", {}).get("runId")
            if run_id:
                report.run_ids.append(run_id)
            for ko in data.get("created", []) or []:
                kid = ko.get("id")
                if kid:
                    report.ko_ids.append(kid)
            if not committed and data.get("error"):
                err = data["error"]
                report.error = err if isinstance(err, str) else json.dumps(err)[:200]
        report.latency_ms = (time.perf_counter() - wall_clock_t0) * 1000.0
        return report

    def ingest_corpus(
        self,
        corpus_dir: Path,
        on_progress=None,
    ) -> list[IngestReport]:
        """Ingest every record in <corpus_dir>/corpus.jsonl."""
        corpus_slug = corpus_dir.name.split("-", 1)[-1] if "-" in corpus_dir.name else corpus_dir.name
        path = corpus_dir / "corpus.jsonl"
        reports: list[IngestReport] = []
        with path.open(encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                doc = json.loads(line)
                rep = self.ingest_doc(corpus_slug, doc)
                reports.append(rep)
                if on_progress:
                    on_progress(i, doc["_id"], rep)
        return reports

    # -- retrieve -------------------------------------------------------------

    @staticmethod
    def _parse_source_uri(uri: str, prefix: str, corpus_slug: str | None = None) -> str | None:
        """Extract the corpus.jsonl _id from a source URI we issued at ingest."""
        # canonical: beir-corpora://<corpus_slug>/<doc_id>(#chunk-N)?
        wanted_head = f"{prefix}://"
        if not uri.startswith(wanted_head):
            return None
        body = uri[len(wanted_head):]
        if "/" not in body:
            return None
        slug, doc_id = body.split("/", 1)
        if corpus_slug and slug != corpus_slug:
            return None
        # strip chunk suffix
        if "#chunk-" in doc_id:
            doc_id = doc_id.split("#chunk-", 1)[0]
        return doc_id

    def retrieve(
        self,
        query: str,
        project_id: str = "default",
        top_k: int = DEFAULT_RETRIEVE_LIMIT,
        corpus_slug: str | None = None,
        tau_bind: float = DEFAULT_TAU_BIND,
        tau_fallback: float = DEFAULT_TAU_FALLBACK,
        compute_query_stance: bool = True,
        score_field: str = "regime_adjusted_score",
    ) -> RetrieveResult:
        """Run a v0 retrieve and aggregate KOs to doc-level scores.

        ``score_field`` chooses which of {similarity, kge_score, regime_adjusted_score}
        is used for ranking. ``regime_adjusted_score`` is the OIDA composite
        and the default; the other two are exposed for ablation/debugging.

        Returned ``doc_scores`` is filtered to docs whose ingest source URI
        used the configured prefix (and corpus slug, if provided) — this is
        how we strip residual KOs from the contaminated ``default`` project.
        """
        payload = {
            "query": query,
            "projectId": project_id,
            "limit": min(top_k, 100),  # v0 hard caps at 100
            "include": [
                "edges",
                "contradictions",
                "salience_metadata",
                "composition_metadata",
                "dialectic_resolutions",
            ],
            "tauBind": tau_bind,
            "tauFallback": tau_fallback,
            "computeQueryStance": compute_query_stance,
        }
        status, data, latency_ms = self._post("/retrieve/full-oida", payload)
        result = RetrieveResult(
            doc_scores={},
            score_components={},
            raw_response_text=None,
            latency_ms=latency_ms,
        )
        if status != 200 or "error" in data:
            err = data.get("error") or f"HTTP {status}"
            result.notes = f"retrieve_error: {err if isinstance(err, str) else json.dumps(err)[:200]}"
            return result

        kos = data.get("subgraph", {}).get("kos", []) or []
        per_doc_components: dict[str, dict[str, float]] = defaultdict(
            lambda: {"similarity": 0.0, "kge_score": 0.0, "regime_adjusted_score": 0.0, "contributing_kos": 0.0}
        )
        per_doc_best: dict[str, float] = {}

        for ko in kos:
            srcs = ko.get("supporting_sources") or []
            if not srcs:
                continue
            # Scan ALL supporting_sources for the first one matching our ingest
            # URI prefix (not just srcs[0]): the server may surface extra
            # metadata-derived sources ahead of the provenance URI, which would
            # otherwise drop a legitimately-matched KO.
            doc_id = None
            for src in srcs:
                doc_id = self._parse_source_uri(src, self.source_uri_prefix, corpus_slug)
                if doc_id is not None:
                    break
            if doc_id is None:
                continue
            sim = float(ko.get("similarity") or 0.0)
            kge = float(ko.get("kge_score") or 0.0)
            ras = float(ko.get("regime_adjusted_score") or 0.0)
            chosen = {"similarity": sim, "kge_score": kge, "regime_adjusted_score": ras}[score_field]
            if doc_id not in per_doc_best or chosen > per_doc_best[doc_id]:
                per_doc_best[doc_id] = chosen
            comp = per_doc_components[doc_id]
            comp["similarity"] = max(comp["similarity"], sim)
            comp["kge_score"] = max(comp["kge_score"], kge)
            comp["regime_adjusted_score"] = max(comp["regime_adjusted_score"], ras)
            comp["contributing_kos"] += 1.0

        # Cap at top_k after aggregation
        ranked = sorted(per_doc_best.items(), key=lambda kv: -kv[1])[:top_k]
        result.doc_scores = {doc_id: score for doc_id, score in ranked}
        result.score_components = {doc_id: dict(per_doc_components[doc_id]) for doc_id, _ in ranked}

        # P0-S6: retain v0 epistemic content verbatim (no computation/fabrication).
        # Independent of the kos->doc_scores mapping above, so BEIR is unperturbed.
        subgraph = data.get("subgraph", {}) or {}
        result.dialectic_resolutions = list(subgraph.get("dialectic_resolutions", []) or [])
        edges = subgraph.get("edges", []) or []
        result.contradiction_edges = [e for e in edges if e.get("contradiction_flag") is True]
        result.contradiction_edge_count = len(result.contradiction_edges)

        meta = data.get("metadata", {}) or {}
        comp_meta = data.get("subgraph", {}).get("composition_metadata", {}) or {}
        result.notes = (
            f"v0 elapsed_ms={meta.get('elapsed_ms')} "
            f"stopping={comp_meta.get('stopping_criterion')} "
            f"kos_returned={len(kos)} docs_matched={len(per_doc_best)}"
        )
        return result


# -- CLI ----------------------------------------------------------------------


def _load_env(env_path: Path) -> dict[str, str]:
    """Minimal .env parser: ``KEY=value`` per line, optional ``#`` comments,
    optional surrounding quotes. Inline comments after the value are stripped
    only if the value is not wrapped in quotes (so URLs containing ``#`` are
    not corrupted unless the user intends a comment)."""
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
            # only strip inline comment if value is unquoted, and only when
            # the '#' is preceded by whitespace (so '#' inside a value like a
            # bash command-style token still works)
            for sep in (" #", "\t#"):
                idx = v.find(sep)
                if idx != -1:
                    v = v[:idx].rstrip()
                    break
        out[k.strip()] = v
    return out


def _smoke(corpus_dir: Path) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    env = _load_env(repo_root / ".env")
    base_url = env.get("OIDA_BASE_URL", DEFAULT_BASE_URL)
    try:
        api_key, project_slug = resolve_corpus_credentials(corpus_dir, env)
    except RuntimeError as e:
        print(f"error: {e}")
        return 2
    print(f"using project={project_slug} (key prefix {api_key[:8]}...)")
    client = OidaClient(api_key, base_url=base_url)
    corpus_slug = corpus_dir.name.split("-", 1)[-1]

    # Pick the first short-ish doc
    with (corpus_dir / "corpus.jsonl").open(encoding="utf-8") as fh:
        candidates = [json.loads(line) for line in fh if line.strip()]
    short = sorted(candidates, key=lambda r: len(r["text"]))[0]
    print(f"smoke ingest: {short['_id']} ({len(short['text'])} chars)")
    rep = client.ingest_doc(corpus_slug, short)
    print(f"  committed={rep.committed} kosCreated={rep.kos_created} chunks={rep.chunks_ingested} latency={rep.latency_ms:.0f}ms")
    if rep.error:
        print(f"  error: {rep.error}")

    # First query in queries.jsonl
    with (corpus_dir / "queries.jsonl").open(encoding="utf-8") as fh:
        queries = [json.loads(line) for line in fh if line.strip()]
    q = queries[0]
    print(f"\nsmoke retrieve: {q['_id']} — {q['text'][:80]}...")
    res = client.retrieve(q["text"], project_id=project_slug, top_k=10, corpus_slug=corpus_slug)
    print(f"  latency={res.latency_ms:.0f}ms docs={len(res.doc_scores)}")
    print(f"  notes: {res.notes}")
    for doc_id, score in list(res.doc_scores.items())[:5]:
        c = (res.score_components or {}).get(doc_id, {})
        print(f"  {score:.4f}  {doc_id}  (kos={int(c.get('contributing_kos',0))}, sim={c.get('similarity',0):.3f}, kge={c.get('kge_score',0):.3f})")
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python -m experiments.adapters.oida <corpus_dir>")
        print("   or: python experiments/adapters/oida.py <corpus_dir>")
        raise SystemExit(2)
    raise SystemExit(_smoke(Path(sys.argv[1]).resolve()))
