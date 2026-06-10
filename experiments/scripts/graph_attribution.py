#!/usr/bin/env python3
"""T4 — Graph-attribution decomposition (GC / RR / CF) for the Five-Layer protocol.

Separates extraction failures (GC) from retrieval failures (RR) from composition
failures (CF) so a per-query miss is attributable (paper §5.1.4):

  Ideal(q)     = graded-relevant gold docs for q (qrels score >= ideal_min_rel)
  Materialized = docs extraction placed in the graph (ingest-report kos_created > 0)
  Retrieved(q) = top-k docs the system returned (ranked doc_scores)
  Used(q)      = generator-referenced docs — NOT emitted by OIDA's retrieval path,
                 so CF is reported N/A in a retrieval-only eval (never faked).

  GC(q) = |Materialized ∩ Ideal(q)| / |Ideal(q)|                         (Graph Coverage)
  RR(q) = |Retrieved(q) ∩ Materialized ∩ Ideal(q)| / |Materialized ∩ Ideal(q)|  (Retrieval Recall)
  CF(q) = |Used(q) ∩ Retrieved(q) ∩ Ideal(q)| / |Retrieved(q) ∩ Ideal(q)|       (Composition Fidelity)
  S(q)  = GC·RR·CF      (CF N/A here → S reported as GC·RR)

Empty-denominator ratio := 1 (paper §5.1.4). Pre-registered gate **F-2-ATTRIB**:
mean GC >= 0.60 across conditions; below it, downstream metrics are reported as
"conditional on extraction quality" (paper §5.4 last row).

Usage:
  python3 experiments/scripts/graph_attribution.py <corpus> [--system oida-core] [--k 10] [--json]
Read-only, file-based (qrels + per-doc ingest report + retrieve run). No engine call.
"""
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "scripts"))
import eval_common as ec  # noqa: E402  (load_qrels, load_runs, ranked, REPO_ROOT)

GC_FLOOR = 0.60  # F-2-ATTRIB


def load_materialized(corpus: str, system: str = "oida-core") -> set[str]:
    """Docs extraction placed in the graph: kos_created > 0 in the per-doc ingest
    report JSONL (experiments/output/ingest_reports/<system>/<corpus>.jsonl).
    Reflects what ingestion materialized, independent of any later DB state."""
    p = ec.REPO_ROOT / "experiments" / "output" / "ingest_reports" / system / f"{corpus}.jsonl"
    out: set[str] = set()
    if not p.exists():
        return out
    for ln in p.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        if r.get("committed") and int(r.get("kos_created") or 0) > 0:
            out.add(r["doc_id"])
    return out


def _ratio(num: int, den: int) -> float:
    return 1.0 if den == 0 else num / den  # empty-denominator := 1 (paper §5.1.4)


def compute_attribution(corpus: str, system: str = "oida-core", k: int = 10,
                        ideal_min_rel: int = 1) -> dict:
    qrels = ec.load_qrels(corpus)               # {qid: {doc: rel}}
    runs = ec.load_runs(corpus, system) or {}   # {qid: {doc: score}} (newest run)
    materialized = load_materialized(corpus, system)
    has_run = bool(runs)

    per_q: list[dict] = []
    for qid, rels in sorted(qrels.items()):
        ideal = {d for d, s in rels.items() if s >= ideal_min_rel}
        if not ideal:
            continue
        mat_ideal = ideal & materialized
        retrieved = set(ec.ranked(runs.get(qid, {}))[:k])
        gc = _ratio(len(mat_ideal), len(ideal))
        rr = _ratio(len(retrieved & mat_ideal), len(mat_ideal))
        per_q.append({
            "qid": qid, "ideal": len(ideal), "materialized_ideal": len(mat_ideal),
            "retrieved_ideal": len(retrieved & mat_ideal),
            "GC": round(gc, 4), "RR": round(rr, 4), "CF": None, "S": round(gc * rr, 4),
        })

    n = len(per_q)
    def _mean(key: str):
        return round(sum(r[key] for r in per_q) / n, 4) if n else None
    means = {"GC": _mean("GC"), "RR": _mean("RR"), "CF": None, "S": _mean("S"), "n_queries": n}
    return {
        "corpus": corpus, "system": system, "k": k, "ideal_min_rel": ideal_min_rel,
        "materialized_docs": len(materialized), "has_run": has_run,
        "per_query": per_q, "means": means,
        "f_2_attrib": {
            "floor": GC_FLOOR, "mean_GC": means["GC"],
            "pass": (means["GC"] is not None and means["GC"] >= GC_FLOOR),
        },
    }


def render_md(res: dict) -> str:
    m = res["means"]; fa = res["f_2_attrib"]
    run_note = "" if res["has_run"] else " · **no retrieve run found → RR is vacuous (1.0); GC is still valid**"
    out = [
        f"## {res['corpus']} / {res['system']} — attribution (GC/RR/CF)",
        "",
        f"- k={res['k']} · Ideal = qrels rel ≥ {res['ideal_min_rel']} · "
        f"Materialized = ingest-report kos_created>0 ({res['materialized_docs']} docs){run_note}",
        "- **CF = N/A**: the retrieval path emits no generator-referenced set (Used); "
        "CF needs a composition/citation step. S = GC·RR.",
        "",
        "| metric | mean | meaning |",
        "|---|---|---|",
        f"| GC | {m['GC']} | gold docs extraction placed in the graph |",
        f"| RR | {m['RR']} | of graph-present gold, fraction retrieved in top-{res['k']} |",
        "| CF | N/A | (no generator-referenced set in a retrieval-only eval) |",
        f"| S = GC·RR | {m['S']} | extraction × retrieval (CF omitted) |",
        "",
        f"**F-2-ATTRIB** (mean GC ≥ {fa['floor']}): mean GC = {fa['mean_GC']} → "
        f"**{'PASS' if fa['pass'] else 'FAIL'}**"
        + ("" if fa["pass"] else " — downstream metrics are CONDITIONAL ON EXTRACTION QUALITY."),
        "",
        f"per-query (n={m['n_queries']}):",
        "",
        "| qid | Ideal | Mat∩Ideal | Retr∩Mat∩Ideal | GC | RR | S |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in res["per_query"]:
        out.append(f"| {r['qid']} | {r['ideal']} | {r['materialized_ideal']} | "
                   f"{r['retrieved_ideal']} | {r['GC']} | {r['RR']} | {r['S']} |")
    return "\n".join(out) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("corpus")
    p.add_argument("--system", default="oida-core")
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--ideal-min-rel", type=int, default=1)
    p.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    a = p.parse_args()
    res = compute_attribution(a.corpus, a.system, a.k, a.ideal_min_rel)
    print(json.dumps(res, indent=2) if a.json else render_md(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
