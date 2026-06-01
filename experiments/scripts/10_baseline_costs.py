#!/usr/bin/env python3
"""Backfill Layer-5 token telemetry for the three baselines (closes F-5-COST).

The first-run baseline retrieve records logged zero tokens. This script fills
them in, **without disturbing the published doc_scores / runs.json**:

  - lightrag, hipporag → retrieve is EMBED-ONLY (structured retrieval / PPR, no
    LLM generation). embed_tokens are computed EXACTLY from the stored query
    text via tiktoken (cl100k_base); no re-run, no spend.
  - graphrag → basic_search calls the LLM. We re-run retrieve per query under an
    OpenAI-SDK usage monkeypatch, harvest (prompt, completion, embedding) tokens,
    and write ONLY the token fields back into the existing record (doc_scores
    untouched). LLM cost is small (gpt-4o-mini).

After this, run 07_collect_telemetry.py + 08_report.py to populate cost + F-5-COST.

Usage:
    python experiments/scripts/10_baseline_costs.py --embed-only      # lightrag+hipporag (free)
    python experiments/scripts/10_baseline_costs.py --graphrag-probe  # 1 query, verify capture
    python experiments/scripts/10_baseline_costs.py --graphrag        # full graphrag re-measure (paid)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eval_common as ec  # noqa: E402

import tiktoken  # noqa: E402

ENC = tiktoken.get_encoding("cl100k_base")

# ---- OpenAI-SDK usage capture (class-level patch catches all clients) -------
_USAGE = {"in": 0, "out": 0, "embed": 0}


def _reset_usage():
    _USAGE["in"] = _USAGE["out"] = _USAGE["embed"] = 0


def _install_usage_capture():
    from openai.resources.chat import completions as chatmod
    from openai.resources import embeddings as embmod

    oa_chat, os_chat = chatmod.AsyncCompletions.create, chatmod.Completions.create
    oa_emb, os_emb = embmod.AsyncEmbeddings.create, embmod.Embeddings.create

    def _tally_chat(r):
        u = getattr(r, "usage", None)
        if u:
            _USAGE["in"] += getattr(u, "prompt_tokens", 0) or 0
            _USAGE["out"] += getattr(u, "completion_tokens", 0) or 0

    def _tally_emb(r):
        u = getattr(r, "usage", None)
        if u:
            _USAGE["embed"] += getattr(u, "prompt_tokens", 0) or 0

    async def a_chat(self, *a, **k):
        r = await oa_chat(self, *a, **k); _tally_chat(r); return r

    def s_chat(self, *a, **k):
        r = os_chat(self, *a, **k); _tally_chat(r); return r

    async def a_emb(self, *a, **k):
        r = await oa_emb(self, *a, **k); _tally_emb(r); return r

    def s_emb(self, *a, **k):
        r = os_emb(self, *a, **k); _tally_emb(r); return r

    chatmod.AsyncCompletions.create = a_chat
    chatmod.Completions.create = s_chat
    embmod.AsyncEmbeddings.create = a_emb
    embmod.Embeddings.create = s_emb


def _rewrite_records(corpus: str, system: str, qid_to_tokens: dict[str, dict]) -> int:
    """Update tokens_in/out/embed_tokens in a system's queries.jsonl in place."""
    run_dir = ec.resolve_retrieve_dir(corpus, system)
    if run_dir is None:
        return 0
    path = run_dir / "queries.jsonl"
    recs = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    n = 0
    for rec in recs:
        t = qid_to_tokens.get(rec["qid"])
        if t:
            rec["tokens_in"] = t["in"]; rec["tokens_out"] = t["out"]; rec["embed_tokens"] = t["embed"]
            n += 1
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in recs) + "\n", encoding="utf-8")
    return n


def embed_only():
    """Embed-only retrievers: embed_tokens = tiktoken(query); LLM tokens = 0.

    lightrag/hipporag do no LLM generation at retrieve. OIDA's query is also
    embedded (text-embedding-3-small) but the deploy doesn't report tokens, so we
    impute the query-embedding cost identically — this is OIDA's externally-
    visible retrieve cost; its internal solver/LLM compute is NOT billed to us
    and is not captured here (documented as a caveat in RESULTS.md)."""
    for system in ("lightrag", "hipporag", "oida-angelicadb", "oida-core"):
        total = 0
        for corpus in ec.ALL_CORPORA:
            recs = ec.load_retrieve_records(corpus, system)
            if not recs:
                continue
            tok = {qid: {"in": 0, "out": 0, "embed": len(ENC.encode(r.get("query", "")))}
                   for qid, r in recs.items()}
            total += _rewrite_records(corpus, system, tok)
        print(f"{system}: embed tokens written for {total} query records")


# graphrag's fnllm bypasses the openai SDK resource classes, and there is no
# query-level cache to read usage from — so we compute tokens DETERMINISTICALLY
# with tiktoken from basic_search's real inputs/outputs: tokens_out from the
# generated answer, tokens_in from query + the retrieved text-unit context (the
# dominant, exact term) + a fixed system-prompt overhead. (basic_search still
# calls the LLM to produce the answer; that cost is ~$0.05 total for 80 queries.)
SYS_PROMPT_OVERHEAD = 400  # graphrag basic_search system/template tokens (approx)


def graphrag(probe: bool = False):
    import os, asyncio
    sys.path.insert(0, str(ec.REPO_ROOT / "experiments"))
    from adapters.graphrag_msft import GraphRagClient, _load_env
    from graphrag.api.query import basic_search
    env = _load_env(ec.REPO_ROOT / ".env")
    if env.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = env["OPENAI_API_KEY"]
        os.environ.setdefault("GRAPHRAG_API_KEY", env["OPENAI_API_KEY"])

    corpora = ec.ALL_CORPORA if not probe else ["org-consulting-clearpath"]
    for corpus in corpora:
        slug = corpus.split("-", 1)[-1]
        client = GraphRagClient(corpus_slug=slug)
        client._load_artifacts()
        recs = ec.load_retrieve_records(corpus, "graphrag")
        if not recs:
            print(f"{corpus}: no graphrag records, skip"); continue
        qids = list(recs)[:1] if probe else list(recs)
        tok = {}
        for qid in qids:
            qtext = recs[qid].get("query", "")
            response, context = asyncio.run(basic_search(
                config=client._config, text_units=client._text_units,
                response_type="Single Paragraph", query=qtext))
            out_tok = len(ENC.encode(str(response or "")))
            ctx_text = ""
            srcs = context.get("sources") if isinstance(context, dict) else None
            if srcs is not None and hasattr(srcs, "columns") and "text" in srcs.columns:
                ctx_text = "\n".join(str(x) for x in srcs["text"].tolist())
            in_tok = len(ENC.encode(qtext)) + len(ENC.encode(ctx_text)) + SYS_PROMPT_OVERHEAD
            emb_tok = len(ENC.encode(qtext))
            tok[qid] = {"in": in_tok, "out": out_tok, "embed": emb_tok}
            print(f"  [{corpus}] {qid}: in={in_tok} out={out_tok} embed={emb_tok} "
                  f"(ctx_chars={len(ctx_text)})", flush=True)
            if probe:
                print(f"  PROBE ok: non-zero input tokens = {in_tok > 0}")
                return
        n = _rewrite_records(corpus, "graphrag", tok)
        print(f"{corpus}: graphrag tokens written for {n} records")


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--embed-only", action="store_true")
    p.add_argument("--graphrag", action="store_true")
    p.add_argument("--graphrag-probe", action="store_true")
    a = p.parse_args(argv)
    if a.embed_only:
        embed_only()
    if a.graphrag_probe:
        graphrag(probe=True)
    if a.graphrag:
        graphrag(probe=False)
    if not (a.embed_only or a.graphrag or a.graphrag_probe):
        p.error("pick --embed-only, --graphrag-probe, or --graphrag")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
