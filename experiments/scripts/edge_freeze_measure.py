#!/usr/bin/env python3
"""edge_freeze_measure — STEP-1 evidence generator for the edge-graph freeze
(D5 MUST #1 / Phase-4 blocker #1; design ../oida-core/doc/findings/edge-freeze-step0.md).

Produces the two artifacts STEP-1 must report, reusing the harness mechanism in
run_regression.py (the quiescence drain + the READ-ONLY probe):

  (A) WITHIN-RUN A/B — over a SINGLE settled/frozen graph, run two retrieves and
      diff their per-query doc_scores (runs.json). The STEP-0 "without freeze"
      baseline was 7/26 & 8/26 queries drifting (P2-S3-evidence.md §4); over a
      frozen graph this must be 0/N (v0 retrieve is read-only on edges/
      contradictions, so re-scoring an un-mutated graph is byte-identical).

  (B) K-INGEST VARIANCE BAND — clean-ingest the SAME corpus K times; for each
      ingest, drain to quiescence, capture the frozen-graph fingerprint + NDCG@10
      (via 03_eval_static_ir), and report the run-to-run band. This is the §7
      cross-ingest signal (LLM re-rolls the graph per clean-ingest) AND the D3
      pilot's variance input — recorded so the pilot reuses it. Distinct
      fingerprints across ingests => the band, not a freeze, is the honest story
      for cross-ingest reproducibility (the surfaced fork's variance-band arm).

STAGING ONLY. Never prod (no --target prod path). Mutates only the burned bench
project being measured (RESET + ingest), exactly like run_regression. Costs
OpenAI credits per ingest (K x).

Usage:
  python experiments/scripts/edge_freeze_measure.py --corpus org-consulting-clearpath --k 3
  python experiments/scripts/edge_freeze_measure.py --corpus org-consulting-clearpath --within-run-only
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "experiments" / "scripts"
sys.path.insert(0, str(REPO_ROOT / "experiments"))
sys.path.insert(0, str(SCRIPTS))

# Reuse the harness mechanism (single source of truth for the freeze + Render
# one-off plumbing). Importing run_regression runs only its module-level setup
# (constants + imports); main() is guarded by __main__.
import run_regression as rr  # noqa: E402
from adapters.oida import OIDA_CORE_PROJECT_IDS, _load_env  # noqa: E402

RETRIEVE_ROOT = REPO_ROOT / "experiments" / "output" / "retrieve_runs"
SYSTEM = "oida-core"


def _runs_json(corpus: str, run_id: str) -> Path:
    return RETRIEVE_ROOT / corpus / f"{SYSTEM}_{run_id}" / "runs.json"


def _diff_runs(path_a: Path, path_b: Path) -> dict:
    """Per-query doc_scores diff between two retrieves (the STEP-0 churn metric).
    A query 'drifts' iff its {doc_id: score} mapping is not identical."""
    a = json.loads(path_a.read_text(encoding="utf-8"))
    b = json.loads(path_b.read_text(encoding="utf-8"))
    qids = sorted(set(a) | set(b))
    drifted = [q for q in qids if a.get(q) != b.get(q)]
    return {
        "n_queries": len(qids),
        "n_drifted": len(drifted),
        "drifted_qids": drifted,
        "byte_identical": len(drifted) == 0,
    }


def _ndcg10(corpus: str, run_id: str, log_lines: list[str]) -> float | None:
    """Run 03_eval_static_ir for one (corpus, run) and read NDCG@10 back."""
    rc, _ = rr._run_script(
        "03_eval_static_ir.py",
        ["--run-id", run_id, "--system", SYSTEM, corpus],
        log_lines, check=False)
    if rc != 0:
        return None
    res = REPO_ROOT / "corpora" / corpus / "results" / f"{SYSTEM}_{run_id}.json"
    if not res.exists():
        return None
    data = json.loads(res.read_text(encoding="utf-8"))
    # tolerant lookup across the report's possible shapes
    for k in ("ndcg@10", "NDCG@10", "ndcg_at_10"):
        if isinstance(data.get(k), (int, float)):
            return float(data[k])
    metrics = data.get("metrics") or data.get("static_ir") or {}
    for k in ("ndcg@10", "NDCG@10", "ndcg_at_10"):
        if isinstance(metrics.get(k), (int, float)):
            return float(metrics[k])
    return None


def _drain_one(corpus: str, base_url: str, service_id: str, render_key: str,
               bundle: Path, log_lines: list[str], floor: int, max_wait: int,
               interval: int) -> dict:
    """Quiescence-drain scoped to ONE corpus's project + snapshot its fingerprint."""
    proj = OIDA_CORE_PROJECT_IDS[corpus]
    return rr.quiescence_drain(
        base_url, service_id, render_key, bundle, log_lines,
        project_ids=[proj], max_wait_sec=max_wait, interval_sec=interval,
        floor_sec=floor, project_filter=proj)


def _fingerprint_of(drain_rep: dict, corpus: str) -> dict | None:
    proj = OIDA_CORE_PROJECT_IDS[corpus]
    for r in drain_rep.get("final_by_project") or []:
        if str(r.get("project")) == proj:
            return {"edges": r.get("edges"), "edge_fp": r.get("edge_fp"),
                    "open_contradictions": r.get("open_contradictions"),
                    "open_contradiction_fp": r.get("open_contradiction_fp")}
    return None


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--corpus", default="org-consulting-clearpath",
                   choices=list(OIDA_CORE_PROJECT_IDS.keys()))
    p.add_argument("--k", type=int, default=3,
                   help="number of clean-ingests for the variance band (>=1)")
    p.add_argument("--within-run-only", action="store_true",
                   help="only the A/B (2 retrieves over one frozen graph); skip the K-band")
    p.add_argument("--env-file", default=str(REPO_ROOT / ".env"))
    p.add_argument("--skip-reset", action="store_true",
                   help="reuse the current ingest for the FIRST band iteration / A-B")
    args = p.parse_args(argv)

    env = _load_env(Path(args.env_file))
    # STAGING ONLY — route at the Option-2 staging deploy (mirror run_regression).
    env["OIDA_CORE_BASE_URL"] = env.get("OIDA_CORE_BASE_URL_STAGING") or rr.STAGING_BASE_URL
    env["OIDA_CORE_RENDER_SERVICE_ID"] = (
        env.get("OIDA_CORE_RENDER_SERVICE_ID_STAGING") or rr.STAGING_SERVICE_ID)
    env["OIDA_CORE_RENDER_DB_ID"] = (
        env.get("OIDA_CORE_RENDER_DB_ID_STAGING") or rr.STAGING_DB_ID)
    base_url = env["OIDA_CORE_BASE_URL"]
    render_key = env.get("RENDER_API_KEY", "")
    floor = int(env.get("OIDA_CORE_SETTLE_SEC", str(rr.QUIESCENCE_FLOOR_SEC)))
    max_wait = int(env.get("OIDA_CORE_QUIESCENCE_MAX_WAIT_SEC", str(rr.QUIESCENCE_MAX_WAIT_SEC)))
    interval = int(env.get("OIDA_CORE_QUIESCENCE_INTERVAL_SEC", str(rr.QUIESCENCE_INTERVAL_SEC)))

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle = rr.OUTPUT / "edge-freeze" / f"{args.corpus}-{ts}"
    bundle.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = [f"# edge_freeze_measure corpus={args.corpus} ts={ts} STAGING"]

    print(f"\n############ edge-freeze measure — corpus={args.corpus} ts={ts} (STAGING) ############")
    print(f"  base_url={base_url}  k={args.k}  within_run_only={args.within_run_only}")

    preflight_rep = rr.preflight(env, base_url, render_key)
    service_id = preflight_rep["service_id"]

    report: dict = {"corpus": args.corpus, "ts": ts, "target": "staging",
                    "within_run": None, "band": None}
    k = 1 if args.within_run_only else max(1, args.k)
    band: list[dict] = []

    for i in range(k):
        first = i == 0
        print(f"\n========== INGEST {i + 1}/{k} ==========")
        # RESET wipes ALL bench projects' KOs (seed-bench); honour --skip-reset on
        # the FIRST iteration only (subsequent band iterations MUST re-ingest fresh).
        rr.reset_bench(service_id, render_key, bundle,
                       skip_reset=(args.skip_reset and first))
        if not (args.skip_reset and first):
            rc, _ = rr._run_script("01_ingest.py", ["--system", SYSTEM, args.corpus], log_lines)
            if rc != 0:
                print("!!! ingest failed — ABORT")
                return 1
        drain_rep = _drain_one(args.corpus, base_url, service_id, render_key,
                               bundle, log_lines, floor, max_wait, interval)
        fp = _fingerprint_of(drain_rep, args.corpus)

        # A/B within-run drift on the FIRST settled graph (the 0/N demo).
        if first:
            run_a, run_b = f"freeze_ab_a_{ts}", f"freeze_ab_b_{ts}"
            for rid in (run_a, run_b):
                rc, _ = rr._run_script("02_retrieve.py",
                                       ["--system", SYSTEM, "--run-id", rid, args.corpus],
                                       log_lines)
                if rc != 0:
                    print("!!! retrieve failed — ABORT")
                    return 1
            diff = _diff_runs(_runs_json(args.corpus, run_a), _runs_json(args.corpus, run_b))
            diff["quiescent"] = drain_rep.get("quiescent")
            diff["band_fallback"] = drain_rep.get("band_fallback")
            report["within_run"] = diff
            print(f"\n  WITHIN-RUN A/B over the frozen graph: {diff['n_drifted']}/"
                  f"{diff['n_queries']} queries drift (byte_identical="
                  f"{diff['byte_identical']}; quiescent={diff['quiescent']})")

        # NDCG@10 for the band (one retrieve + 03 per ingest).
        band_rid = f"freeze_band_{i}_{ts}"
        rc, _ = rr._run_script("02_retrieve.py",
                               ["--system", SYSTEM, "--run-id", band_rid, args.corpus],
                               log_lines, check=False)
        ndcg = _ndcg10(args.corpus, band_rid, log_lines) if rc == 0 else None
        band.append({"ingest": i, "fingerprint": fp, "ndcg@10": ndcg,
                     "quiescent": drain_rep.get("quiescent"),
                     "band_fallback": drain_rep.get("band_fallback")})
        print(f"  ingest {i}: ndcg@10={ndcg} edges={(fp or {}).get('edges')} "
              f"edge_fp={str((fp or {}).get('edge_fp'))[:12]}")

    # band summary
    ndcgs = [b["ndcg@10"] for b in band if isinstance(b["ndcg@10"], (int, float))]
    fps = {b["fingerprint"]["edge_fp"] for b in band if b.get("fingerprint")}
    report["band"] = {
        "k": k,
        "ndcg_values": ndcgs,
        "ndcg_min": min(ndcgs) if ndcgs else None,
        "ndcg_max": max(ndcgs) if ndcgs else None,
        "ndcg_mean": (sum(ndcgs) / len(ndcgs)) if ndcgs else None,
        "ndcg_spread": (max(ndcgs) - min(ndcgs)) if ndcgs else None,
        "distinct_edge_fingerprints": len(fps),
        "per_ingest": band,
    }

    (bundle / "edge_freeze_measure.json").write_text(json.dumps(report, indent=2),
                                                     encoding="utf-8")
    (bundle / "log.txt").write_text("\n".join(log_lines), encoding="utf-8")
    print("\n===================== EDGE-FREEZE MEASURE SUMMARY =====================")
    wr = report["within_run"] or {}
    print(f"  within-run drift over frozen graph: {wr.get('n_drifted')}/{wr.get('n_queries')} "
          f"(byte_identical={wr.get('byte_identical')})")
    b = report["band"]
    print(f"  K={b['k']} ingests: NDCG@10 band=[{b['ndcg_min']}, {b['ndcg_max']}] "
          f"spread={b['ndcg_spread']} mean={b['ndcg_mean']} "
          f"distinct_edge_fingerprints={b['distinct_edge_fingerprints']}")
    print(f"  artifact: {bundle.relative_to(REPO_ROOT)}/edge_freeze_measure.json")
    print("\n  NOTE: this is the D3 pilot's variance input — record it; do not discard.")
    print("  RESTORE staging to integration after this run (see PR notes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
