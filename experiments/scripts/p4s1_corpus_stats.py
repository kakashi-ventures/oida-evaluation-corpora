#!/usr/bin/env python3
"""P4-S1 corpus-stats acceptance report generator — the §3 DoD table.

Implements the STATIC (Part 1) gates of doc/P4-S1-corpus-design-spec.md §3, READ-ONLY
over corpus data + the (gitignored) gold annotations. No engine run. The two
engine-dependent gates (R2.2 recall@k, R6 signal-margin/reorderings) are Part 2
(via the freeze/pilot harness) and are emitted here as PENDING placeholders.

Static gates computed here:
  R1.1  freshest-is-current rate            target = 100%
  R1.2  current-is-top-cosine rate          target <= ~40%   (needs OpenAI embeddings)
  R1.3  supersession pairs with in-text cue target = 100%
  R1.4  temporal mix freshness/stable/distractor  target ~= 50/25/25, >= T
  R2.1  short-comms gold present            present (+ recall@50 is Part 2)
  R3    authority-conflict pairs, balanced  >= M, ~1:1   (needs authority_class tags)
  R4    cross-doc contradiction pairs       >= K
  R5    trap pairs                          >= 80
  R6    signal-margin / reorderings         PENDING (Part 2, engine)
  gold human-reviewed                       sign-off recorded

Data sources (all read-only):
  corpora/<id>/{corpus.jsonl, queries.jsonl, qrels/test.tsv}
  experiments/annotations/{temporal_queries,supersession_chains,contra_sets,lifecycle}/<id>.json (gitignored)

Each gate degrades GRACEFULLY: if its annotation/tag is absent (e.g. burned corpora
lack the fresh-only authority_class / temporal mix tags), the gate reports value
`n/a` with a reason rather than crashing — so the same generator runs on burned
fixtures now and on fresh corpora later.

Usage (validate on burned corpora as fixtures):
  python experiments/scripts/p4s1_corpus_stats.py            # all corpora under corpora/
  python experiments/scripts/p4s1_corpus_stats.py org-consulting-clearpath
  python experiments/scripts/p4s1_corpus_stats.py --no-cosine     # skip R1.2 (no OpenAI)
  python experiments/scripts/p4s1_corpus_stats.py --summary-out docs/p4s1-burned-fixture-validation.md

Read-only. Reports default to experiments/output/p4s1/ (gitignored — keeps fresh
gold private); pass --summary-out to also write a committed cross-corpus §3 summary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPORA = REPO_ROOT / "corpora"
ANN = REPO_ROOT / "experiments" / "annotations"
OUT_DEFAULT = REPO_ROOT / "experiments" / "output" / "p4s1"
EMB_MODEL = "text-embedding-3-small"  # match the engine (oida-core generate.ts)
CUE_PATTERNS = [
    r"supersed\w*", r"replac\w*", r"\bv\d+\b.{0,40}\b(replac|supersed|over\w*)",
    r"rescind\w*", r"obsolet\w*", r"no longer (valid|current|applies|in effect)",
    r"revis\w*", r"updat\w+ (the|our|this)\b", r"final\w*.{0,30}\b(replac|supersed)",
]

# ---------------------------------------------------------------------------
# loaders (read-only, graceful)
# ---------------------------------------------------------------------------

def _read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def _read_qrels(p: Path) -> dict[str, dict[str, int]]:
    q: dict[str, dict[str, int]] = {}
    if not p.exists():
        return q
    for ln in p.read_text(encoding="utf-8").splitlines():
        parts = ln.split("\t")
        if len(parts) != 3 or parts[0] == "query-id":
            continue
        qid, doc, score = parts
        try:
            q.setdefault(qid, {})[doc] = int(score)
        except ValueError:
            continue
    return q


def _read_ann(kind: str, corpus: str) -> dict:
    p = ANN / kind / f"{corpus}.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


# ---------------------------------------------------------------------------
# effective-date extraction (in-text first — the spec's canonical source —
# then metadata.created fallback)
# ---------------------------------------------------------------------------

_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], start=1)}


def _parse_intext_date(text: str) -> date | None:
    # "Date: August 22, 2025" / "August 22, 2025"
    m = re.search(r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})\b", text, re.I)
    if m:
        return date(int(m.group(3)), _MONTHS[m.group(1).lower()], int(m.group(2)))
    # ISO 2025-08-22
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None


def effective_date(doc: dict) -> date | None:
    # Prefer an explicit "Date:" line, then any in-text date, then metadata.created.
    text = doc.get("text", "") or ""
    m = re.search(r"(?:^|\n)\s*\**\s*Date\s*\**\s*:?\s*\**\s*([A-Za-z0-9,\s-]{6,30})", text)
    if m:
        d = _parse_intext_date(m.group(1))
        if d:
            return d
    d = _parse_intext_date(text[:1500])  # header region
    if d:
        return d
    created = (doc.get("metadata") or {}).get("created")
    if created:
        try:
            return date.fromisoformat(str(created)[:10])
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# embeddings (R1.2) — OpenAI text-embedding-3-small, cached, optional
# ---------------------------------------------------------------------------

def _load_env(env_path: Path) -> dict:
    out: dict = {}
    if not env_path.exists():
        return out
    for ln in env_path.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln:
            continue
        k, v = ln.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


class Embedder:
    def __init__(self, api_key: str, cache_path: Path):
        self.key = api_key
        self.cache_path = cache_path
        self.cache: dict[str, list[float]] = {}
        if cache_path.exists():
            try:
                self.cache = json.loads(cache_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.cache = {}

    def embed(self, text: str) -> list[float]:
        text = (text or "").strip()[:8000]
        h = hashlib.sha1((EMB_MODEL + "\x00" + text).encode("utf-8")).hexdigest()
        if h in self.cache:
            return self.cache[h]
        import urllib.request
        req = urllib.request.Request(
            "https://api.openai.com/v1/embeddings",
            data=json.dumps({"input": text, "model": EMB_MODEL}).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
        )
        vec = json.loads(urllib.request.urlopen(req, timeout=60).read())["data"][0]["embedding"]
        self.cache[h] = vec
        return vec

    def flush(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(self.cache), encoding="utf-8")


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


# ---------------------------------------------------------------------------
# the gates
# ---------------------------------------------------------------------------

SHORT_COMMS = re.compile(r"email|slack|chat|sms|message|memo|note|comms?", re.I)

# Engine-gate constants (Part 2)
RECALL_KS = [10, 20, 50]
JITTER = 1e-4  # measured solver-level raw-score jitter (edge-freeze findings)
MARGIN_DESIGN = 1e-2  # R6.1 design target: signal margin >> jitter


def _mean(xs: list[float]) -> float | None:
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 4) if xs else None


def _load_run(run_dir: Path) -> dict:
    """Load one retrieve run over a frozen graph: {qid: {doc_scores, sc}} from
    queries.jsonl (rich: doc_scores + per-doc score_components) or runs.json."""
    runs: dict = {}
    qj = run_dir / "queries.jsonl"
    if qj.exists():
        for rec in _read_jsonl(qj):
            runs[rec["qid"]] = {"doc_scores": rec.get("doc_scores") or {},
                                "sc": rec.get("score_components") or {}}
        return runs
    rj = run_dir / "runs.json"
    if rj.exists():
        for qid, ds in json.loads(rj.read_text(encoding="utf-8")).items():
            runs[qid] = {"doc_scores": ds, "sc": {}}
    return runs


def _ranked(doc_scores: dict) -> list[str]:
    return [d for d, _ in sorted(doc_scores.items(), key=lambda x: -x[1])]


def compute_engine_gates(run_dirs: list[Path], qrels: dict, temporal: dict,
                         docs: dict, queries: dict) -> dict:
    """R2.2 recall@k per class + R6 signal-margin/reorderings, from K retrieves
    over a FROZEN graph (produced by the freeze harness). Read-only on the runs."""
    runs = [(_load_run(rd), rd.name) for rd in run_dirs]
    runs = [(r, n) for r, n in runs if r]
    if not runs:
        return {"ok": False, "reason": "no readable retrieve runs"}
    primary = runs[0][0]

    def is_short(qid: str) -> bool:
        rel = {d for d, s in qrels.get(qid, {}).items() if s >= 1}
        return any(SHORT_COMMS.search(d) or
                   SHORT_COMMS.search((docs.get(d, {}).get("metadata") or {}).get("category", ""))
                   for d in rel)

    # ---- R2.2 recall@k per class (on the primary frozen-graph retrieve) ----
    def recall_at(qid: str, k: int) -> float | None:
        rel = {d for d, s in qrels.get(qid, {}).items() if s >= 1}
        if not rel:
            return None
        topk = set(_ranked(primary.get(qid, {}).get("doc_scores", {}))[:k])
        return len(topk & rel) / len(rel)

    scored_qids = [q for q in primary if any(s >= 1 for s in qrels.get(q, {}).values())]
    classes = {
        "overall": scored_qids,
        "short_comms": [q for q in scored_qids if is_short(q)],
        "temporal": [q for q in scored_qids if q in temporal],
    }
    recall = {cls: {f"@{k}": _mean([recall_at(q, k) for q in qids]) for k in RECALL_KS}
              for cls, qids in classes.items()}
    recall_n = {cls: len(qids) for cls, qids in classes.items()}

    # ---- R6.1 signal-margin on R1 contests (winner vs top competitor) ----
    def margin(qid: str, field: str) -> float | None:
        cur = set(temporal.get(qid, {}).get("gold_current_docs", []))
        sc = primary.get(qid, {}).get("sc", {})
        if not cur or not sc:
            return None
        def f(d):
            v = (sc.get(d) or {}).get(field)
            return float(v) if isinstance(v, (int, float)) else None
        win = max((f(d) for d in cur if f(d) is not None), default=None)
        comp = max((f(d) for d in sc if d not in cur and f(d) is not None), default=None)
        return None if win is None or comp is None else win - comp

    r1_contests = [q for q in temporal
                   if temporal[q].get("gold_current_docs") and
                   (temporal[q].get("gold_superseded_docs") or temporal[q].get("gold_should_not_retrieve"))]
    r1_margins = [(q, margin(q, "recency_adjusted_score")) for q in r1_contests]
    r1_margins = [(q, m) for q, m in r1_margins if m is not None]
    knife = [q for q, m in r1_margins if abs(m) <= JITTER]
    lost = [q for q, m in r1_margins if m < 0]

    # ---- R6.2 reorderings across the K frozen-graph retrieves ----
    def reorderings(qids: list[str]) -> int:
        n = 0
        for q in qids:
            orders = {tuple(_ranked(r.get(q, {}).get("doc_scores", {}))) for r, _ in runs if q in r}
            if len(orders) > 1:
                n += 1
        return n
    reorder_overall = reorderings(scored_qids)
    reorder_contests = reorderings(r1_contests)

    return {
        "ok": True, "k_retrieves": len(runs), "run_names": [n for _, n in runs],
        "recall": recall, "recall_n": recall_n,
        "r1_contests": len(r1_margins),
        "margin_min": min((m for _, m in r1_margins), default=None),
        "margin_median": (sorted(m for _, m in r1_margins)[len(r1_margins) // 2]
                          if r1_margins else None),
        "knife_edge": len(knife), "winner_lost": len(lost),
        "reorder_overall": reorder_overall, "reorder_contests": reorder_contests,
    }


def compute_gates(corpus: str, embedder: Embedder | None,
                  engine_runs: list[Path] | None = None) -> dict:
    cdir = CORPORA / corpus
    docs = {d["_id"]: d for d in _read_jsonl(cdir / "corpus.jsonl")}
    queries = {q["_id"]: q for q in _read_jsonl(cdir / "queries.jsonl")}
    qrels = _read_qrels(cdir / "qrels" / "test.tsv")
    temporal = _read_ann("temporal_queries", corpus)
    superses = _read_ann("supersession_chains", corpus)
    contra = _read_ann("contra_sets", corpus)
    dates = {did: effective_date(d) for did, d in docs.items()}
    eng = compute_engine_gates(engine_runs, qrels, temporal, docs, queries) if engine_runs else None

    gates: dict[str, dict] = {}

    def g(key, value, target, status, note=""):
        gates[key] = {"value": value, "target": target, "status": status, "note": note}

    # ---- R1.1 freshest-is-current rate ----
    clusters = 0
    fresh_ok = 0
    r11_detail = []
    for qid, t in temporal.items():
        cur = [d for d in t.get("gold_current_docs", []) if dates.get(d)]
        sup = [d for d in t.get("gold_superseded_docs", []) if dates.get(d)]
        if not cur or not sup:
            continue
        clusters += 1
        newest = max((dates[d], d) for d in (cur + sup))[1]
        ok = newest in cur
        fresh_ok += 1 if ok else 0
        r11_detail.append({"qid": qid, "ok": ok, "newest_doc": newest,
                           "cur": cur, "sup": sup})
    if clusters:
        rate = round(100 * fresh_ok / clusters, 1)
        g("R1.1 freshest-is-current rate", f"{rate}% ({fresh_ok}/{clusters})",
          "= 100%", "PASS" if fresh_ok == clusters else "FAIL", f"{clusters} dated clusters")
    else:
        g("R1.1 freshest-is-current rate", "n/a", "= 100%", "N/A",
          "no temporal clusters with both current+superseded dated docs")

    # ---- R1.2 current-is-top-cosine rate (needs embeddings) ----
    if embedder is None:
        g("R1.2 current-is-top-cosine rate", "n/a", "<= ~40%", "N/A",
          "cosine skipped (--no-cosine or no OPENAI_API_KEY)")
    else:
        cand = [qid for qid, t in temporal.items() if t.get("gold_current_docs")]
        if not cand:
            g("R1.2 current-is-top-cosine rate", "n/a", "<= ~40%", "N/A",
              "no temporal queries with gold_current_docs")
        else:
            doc_vecs = {did: embedder.embed((d.get("title") or "") + "\n" + (d.get("text") or ""))
                        for did, d in docs.items()}
            top_is_current = 0
            n = 0
            for qid in cand:
                q = queries.get(qid)
                if not q:
                    continue
                qv = embedder.embed(q.get("text", ""))
                best = max(doc_vecs, key=lambda did: _cosine(qv, doc_vecs[did]))
                n += 1
                if best in set(temporal[qid].get("gold_current_docs", [])):
                    top_is_current += 1
            rate = round(100 * top_is_current / n, 1) if n else 0.0
            g("R1.2 current-is-top-cosine rate", f"{rate}% ({top_is_current}/{n})",
              "<= ~40%", "PASS" if rate <= 40 else "FAIL", "top-1 cosine over all corpus docs")

    # ---- R1.3 supersession pairs with in-text cue ----
    cue_re = re.compile("|".join(CUE_PATTERNS), re.I)
    total_pairs = 0
    cued_pairs = 0
    miss = []
    for qid, s in superses.items():
        binding = s.get("binding")
        if not binding or binding not in docs:
            continue
        btext = docs[binding].get("text", "") or ""
        has_cue = bool(cue_re.search(btext))
        for _sup in s.get("superseded", []):
            total_pairs += 1
            if has_cue:
                cued_pairs += 1
            else:
                miss.append({"qid": qid, "binding": binding})
    if total_pairs:
        rate = round(100 * cued_pairs / total_pairs, 1)
        g("R1.3 supersession cue present", f"{rate}% ({cued_pairs}/{total_pairs})",
          "= 100%", "PASS" if cued_pairs == total_pairs else "FAIL",
          f"{total_pairs} supersession pairs")
    else:
        g("R1.3 supersession cue present", "n/a", "= 100%", "N/A",
          "no supersession pairs annotated")

    # ---- R1.4 temporal mix freshness/stable/distractor ----
    cls = {"freshness": 0, "stable": 0, "distractor": 0, "other": 0}
    for qid, t in temporal.items():
        cur = t.get("gold_current_docs", [])
        sup = t.get("gold_superseded_docs", [])
        stable = t.get("gold_stable_docs", [])
        nono = t.get("gold_should_not_retrieve", [])
        if stable:
            cls["stable"] += 1
        elif nono:
            cls["distractor"] += 1
        elif cur and sup:
            # freshness-helps iff the freshest dated doc is current
            dd = [(dates[d], d, d in cur) for d in (cur + sup) if dates.get(d)]
            if dd and max(dd)[2]:
                cls["freshness"] += 1
            else:
                cls["other"] += 1
        else:
            cls["other"] += 1
    tot = sum(cls.values())
    if tot:
        pct = {k: round(100 * v / tot) for k, v in cls.items()}
        val = f"fresh {pct['freshness']}% / stable {pct['stable']}% / distractor {pct['distractor']}% / other {pct['other']}% (n={tot})"
        # informational on burned fixtures (not designed for the mix)
        near = abs(pct["freshness"] - 50) <= 15 and abs(pct["stable"] - 25) <= 15 and abs(pct["distractor"] - 25) <= 15
        g("R1.4 temporal mix", val, "~= 50/25/25", "PASS" if near else "REVIEW",
          "fixture: burned corpora not authored for the calibrated mix")
    else:
        g("R1.4 temporal mix", "n/a", "~= 50/25/25", "N/A", "no temporal queries")

    # ---- R2.1 short-comms gold present ----
    short_gold = []
    for qid, dd in qrels.items():
        for did, sc in dd.items():
            if sc >= 1 and (SHORT_COMMS.search(did) or SHORT_COMMS.search((docs.get(did, {}).get("metadata") or {}).get("category", ""))):
                short_gold.append((qid, did))
    g("R2.1 short-comms gold present", f"{len(short_gold)} gold short-comms (q,doc) pairs",
      "present (recall@50 = Part 2)", "PASS" if short_gold else "FAIL",
      "recall@50 reported in Part 2 (engine)")

    # ---- R2.2 recall@k per class (engine, Part 2 — frozen-graph retrieve) ----
    if eng and eng.get("ok"):
        rc, rn = eng["recall"], eng["recall_n"]
        ov, sh = rc["overall"], rc["short_comms"]
        val = (f"overall R@10/20/50 = {ov['@10']}/{ov['@20']}/{ov['@50']} (n={rn['overall']}); "
               f"short-comms R@50 = {sh['@50']} (n={rn['short_comms']})")
        gap = (sh['@50'] is not None and ov['@50'] is not None and sh['@50'] < ov['@50'] - 0.1)
        g("R2.2 recall@k per class", val, "recall@50 logged",
          "MEASURED" + (" — short-comms gap → embedding/ingestion item" if gap else ""),
          f"frozen-graph retrieve; K={eng['k_retrieves']} ({', '.join(eng['run_names'][:1])}…)")
    else:
        g("R2.2 recall@k per class", "PENDING", "recall@50 logged", "PENDING",
          "engine gate — pass --engine-runs (K frozen-graph retrieves)")

    # ---- R3 authority-conflict pairs (needs authority_class tags) ----
    auth = [q for q in queries.values() if (q.get("metadata") or {}).get("authority_class")]
    if auth:
        cls_i = sum(1 for q in auth if (q["metadata"]["authority_class"]) in ("i", "authoritative_not_answer", "conflict_i"))
        cls_ii = sum(1 for q in auth if (q["metadata"]["authority_class"]) in ("ii", "authoritative_is_answer", "conflict_ii"))
        bal = f"{cls_i}:{cls_ii}"
        g("R3 authority-conflict pairs", f"{len(auth)} (i:ii = {bal})", ">= M, ~1:1",
          "REVIEW", "balance check vs locked M")
    else:
        g("R3 authority-conflict pairs", "n/a", ">= M, ~1:1", "N/A",
          "no authority_class query tags (fresh-corpus gate; burned corpora untagged)")

    # ---- R4 cross-doc contradiction pairs ----
    crossdoc = 0
    for qid, c in contra.items():
        sides = c.get("sides", [])
        if len(sides) >= 2 and sides[0] and sides[1]:
            if set(sides[0]).isdisjoint(set(sides[1])):
                crossdoc += 1
    g("R4 cross-doc contradiction pairs", str(crossdoc), ">= K",
      "PASS" if crossdoc else "FAIL", "genuine two-sided cross-doc (disjoint sides)")

    # ---- R5 trap pairs (explicit-zero qrels) ----
    traps = sum(1 for dd in qrels.values() for sc in dd.values() if sc == 0)
    g("R5 trap pairs", str(traps), ">= 80", "PASS" if traps >= 80 else "FAIL",
      "explicit-zero (query,doc) qrels")

    # ---- R6 signal-margin / reorderings (engine, Part 2 — frozen graph) ----
    if eng and eng.get("ok"):
        mm, nrc = eng["margin_min"], eng["r1_contests"]
        val = (f"R1 contests={nrc}; margin_min={mm}; knife-edge(<={JITTER})={eng['knife_edge']}; "
               f"winner-lost={eng['winner_lost']}; reorderings contest/overall="
               f"{eng['reorder_contests']}/{eng['reorder_overall']} over K={eng['k_retrieves']}")
        ok_reorder = eng["reorder_overall"] == 0
        ok_margin = (mm is not None and mm >= MARGIN_DESIGN) if nrc else True
        status = "PASS" if (ok_reorder and ok_margin) else ("REVIEW" if ok_reorder else "FAIL")
        g("R6 signal-margin / reorderings", val, "design >= ~1e-2; 0 reorderings", status,
          "0 reorderings ⇒ reproducible NDCG; any margin < design ⇒ widen the signal margin (re-author)")
    else:
        g("R6 signal-margin / reorderings", "PENDING", "design >= ~1e-2; 0 reorderings",
          "PENDING", "engine gate — Part 2 via freeze/pilot harness (quiescence_drain + edge_freeze_measure)")

    # ---- gold human-reviewed ----
    g("gold human-reviewed", "n/a (burned fixture)", "sign-off recorded", "N/A",
      "fresh corpora record the human gold-review sign-off here (D2 protocol)")

    return {
        "corpus": corpus,
        "counts": {"docs": len(docs), "queries": len(queries),
                   "temporal_queries": len(temporal), "supersession": len(superses),
                   "contra_sets": len(contra)},
        "gates": gates,
        "_detail": {"R1.1": r11_detail, "R1.3_missing_cue": miss, "R1.4_classes": cls},
    }


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

GATE_ORDER = [
    "R1.1 freshest-is-current rate", "R1.2 current-is-top-cosine rate",
    "R1.3 supersession cue present", "R1.4 temporal mix",
    "R2.1 short-comms gold present", "R2.2 recall@k per class", "R3 authority-conflict pairs",
    "R4 cross-doc contradiction pairs", "R5 trap pairs",
    "R6 signal-margin / reorderings", "gold human-reviewed",
]


def render_md(rep: dict) -> str:
    c = rep["counts"]
    out = [f"## {rep['corpus']} — P4-S1 corpus-stats (§3 DoD)", "",
           f"_docs={c['docs']} queries={c['queries']} temporal_q={c['temporal_queries']} "
           f"supersession={c['supersession']} contra_sets={c['contra_sets']}_", "",
           "| gate | value | target | status |", "|---|---|---|---|"]
    for k in GATE_ORDER:
        g = rep["gates"].get(k)
        if not g:
            continue
        out.append(f"| {k} | {g['value']} | {g['target']} | **{g['status']}** |")
    notes = [f"- *{k}*: {rep['gates'][k]['note']}" for k in GATE_ORDER
             if rep["gates"].get(k, {}).get("note")]
    out += ["", "**Notes:**", *notes, ""]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("corpora", nargs="*", help="corpus dir names (default: all under corpora/)")
    p.add_argument("--no-cosine", action="store_true", help="skip R1.2 (no OpenAI)")
    p.add_argument("--env-file", default=str(REPO_ROOT / ".env"))
    p.add_argument("--out", default=str(OUT_DEFAULT), help="per-corpus report dir (gitignored)")
    p.add_argument("--summary-out", default=None,
                   help="also write a combined cross-corpus §3 summary (e.g. a committed doc)")
    p.add_argument("--engine-runs", default=None,
                   help="comma-separated retrieve-run dirs (K retrieves over a FROZEN graph, "
                        "from the freeze harness) to compute the engine gates R2.2 + R6. "
                        "Applies to the corpus(es) processed — intended for a single corpus.")
    args = p.parse_args(argv)

    engine_runs = ([Path(p) for p in args.engine_runs.split(",") if p.strip()]
                   if args.engine_runs else None)

    corpora = args.corpora or sorted(
        d.name for d in CORPORA.iterdir() if d.is_dir() and (d / "corpus.jsonl").exists())

    embedder = None
    if not args.no_cosine:
        env = _load_env(Path(args.env_file))
        key = env.get("OPENAI_API_KEY", "")
        if key:
            embedder = Embedder(key, OUT_DEFAULT / "emb_cache.json")
        else:
            print("  [warn] no OPENAI_API_KEY — R1.2 will be n/a")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_parts = ["# P4-S1 corpus-stats — §3 DoD report", "",
                     "Generated by `experiments/scripts/p4s1_corpus_stats.py` (read-only). "
                     "Static gates (Part 1); R2.2/R6 are engine gates (Part 2).", ""]
    for corpus in corpora:
        print(f"\n=== {corpus} ===")
        rep = compute_gates(corpus, embedder, engine_runs)
        md = render_md(rep)
        (out_dir / f"{corpus}.md").write_text(md, encoding="utf-8")
        (out_dir / f"{corpus}.json").write_text(json.dumps(rep, indent=2, default=str), encoding="utf-8")
        print(md)
        summary_parts.append(md)
    if embedder:
        embedder.flush()

    if args.summary_out:
        Path(args.summary_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.summary_out).write_text("\n".join(summary_parts), encoding="utf-8")
        print(f"\nwrote combined summary -> {args.summary_out}")
    print(f"\nper-corpus reports -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
