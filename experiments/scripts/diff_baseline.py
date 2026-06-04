#!/usr/bin/env python3
"""Diff fresh L1 NDCG@10 vs the archived Phase-0 baseline (HARNESS VALIDATION).

The engine is UNCHANGED through Phase 0, so a clean re-ingest + re-score on the
burned corpora must reproduce the archived NDCG@10 within ±0.005. This is a
**harness-validation** check (the harness itself reproduces the archived run),
NOT an OIDA performance claim. The burned corpora are regression/sanity signal
only; pass/fail lives in the Phase-4 fresh corpora.

Falsification contract
----------------------
  MEASURES: |fresh NDCG@10 - archived NDCG@10| per corpus, against a fixed
            ±0.005 tolerance. Reads `layer_1_static_ir.ndcg["10"]`.
  HOW:      archived values come from
            archive/degenerate-config-2026-06-01/corpora/<id>/results/oida-core_*.json
            (the quarantined degenerate-config run, kept for reference). Fresh
            values come from the current bundle's copied result JSONs (or a live
            corpora/<id>/results/oida-core_<run_id>.json). Pure arithmetic; no
            network, no LLM, no gold mutation.
  WHERE:    writes diff_vs_baseline.md into the Evidence Bundle and returns the
            structured deltas (so run_regression.py and the verifier share one
            implementation).
  WHAT CHANGES: nothing — read-only. The harness's ACCEPTANCE gate consults
            `all_within_tolerance`; a breach flags an unexplained regression on a
            non-target metric.

stdlib only. Reusable two ways:
  * imported:  diff_baseline.diff_and_write(out_md, fresh_ndcg10)
  * standalone (verifier): point --bundle at a regression bundle's layers/ dir,
    or pass --run-id to read live corpora/<id>/results/oida-core_<run_id>.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SYSTEM = "oida-core"
ARCHIVE_DIR = REPO_ROOT / "archive" / "degenerate-config-2026-06-01" / "corpora"
TOLERANCE = 0.005

# Canonical 5 burned corpora (ordered).
CORPORA = [
    "org-consulting-clearpath",
    "org-iot-fireglass",
    "org-vc-vertexminds",
    "inv-mystery-redhood",
    "inv-ashford-mystery",
]

DIFF_HEADER = "harness-validation (engine unchanged), NOT an OIDA performance claim."


def _ndcg10_from_result(path: Path) -> float | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    v = ((data.get("layer_1_static_ir") or {}).get("ndcg") or {}).get("10")
    return float(v) if isinstance(v, (int, float)) else None


def archived_ndcg10(corpus: str) -> float | None:
    """Newest archived oida-core_*.json for this corpus -> NDCG@10."""
    base = ARCHIVE_DIR / corpus / "results"
    if not base.is_dir():
        return None
    cands = sorted(base.glob(f"{SYSTEM}_*.json"))
    if not cands:
        return None
    return _ndcg10_from_result(max(cands, key=lambda p: p.stat().st_mtime))


def fresh_ndcg10_from_live(corpus: str, run_id: str | None) -> float | None:
    """Live corpora/<id>/results/oida-core_<run_id>.json (or newest if run_id None)."""
    base = REPO_ROOT / "corpora" / corpus / "results"
    if not base.is_dir():
        return None
    if run_id:
        return _ndcg10_from_result(base / f"{SYSTEM}_{run_id}.json")
    cands = sorted(base.glob(f"{SYSTEM}_*.json"))
    if not cands:
        return None
    return _ndcg10_from_result(max(cands, key=lambda p: p.stat().st_mtime))


def fresh_ndcg10_from_bundle(corpus: str, layers_dir: Path) -> float | None:
    """A regression bundle copies result JSONs as
    layers/oida-core_<run_id>__<corpus>.json — find this corpus's copy."""
    if not layers_dir.is_dir():
        return None
    cands = sorted(layers_dir.glob(f"{SYSTEM}_*__{corpus}.json"))
    if not cands:
        return None
    return _ndcg10_from_result(max(cands, key=lambda p: p.stat().st_mtime))


def compute_diff(fresh_ndcg10: dict[str, float | None]) -> dict:
    per_corpus = []
    all_within = True
    for corpus in CORPORA:
        arch = archived_ndcg10(corpus)
        fresh = fresh_ndcg10.get(corpus)
        if arch is None or fresh is None:
            per_corpus.append({
                "corpus": corpus, "archived": arch, "fresh": fresh,
                "delta": None, "within_tolerance": None,
                "note": "missing archived or fresh value",
            })
            all_within = False
            continue
        delta = fresh - arch
        within = abs(delta) <= TOLERANCE
        all_within = all_within and within
        per_corpus.append({
            "corpus": corpus,
            "archived": round(arch, 6),
            "fresh": round(fresh, 6),
            "delta": round(delta, 6),
            "abs_delta": round(abs(delta), 6),
            "within_tolerance": within,
        })
    return {
        "tolerance": TOLERANCE,
        "header": DIFF_HEADER,
        "per_corpus": per_corpus,
        "all_within_tolerance": all_within,
    }


def render_md(diff: dict) -> str:
    lines = ["# diff_vs_baseline.md", "", diff["header"], ""]
    lines.append(f"±{diff['tolerance']} L1 NDCG@10, fresh vs archived (degenerate-config "
                 "run, quarantined for reference). The engine is unchanged in Phase 0, so")
    lines.append("fresh must reproduce archived within tolerance — this validates the")
    lines.append("HARNESS, it is not an OIDA performance number. Burned corpora are")
    lines.append("regression/sanity only; pass/fail lives in the Phase-4 fresh corpora.")
    lines.append("")
    lines.append("| corpus | archived NDCG@10 | fresh NDCG@10 | delta | |delta|<=0.005 |")
    lines.append("|---|---|---|---|---|")
    for r in diff["per_corpus"]:
        def f(v):
            return f"{v:.4f}" if isinstance(v, (int, float)) else "—"
        within = r.get("within_tolerance")
        within_s = ("✓" if within else "✗") if within is not None else "?"
        note = f"  ({r['note']})" if r.get("note") else ""
        lines.append(f"| {r['corpus']} | {f(r['archived'])} | {f(r['fresh'])} | "
                     f"{f(r.get('delta'))} | {within_s}{note} |")
    lines.append("")
    lines.append(f"**All within ±{diff['tolerance']}: "
                 f"{'YES' if diff['all_within_tolerance'] else 'NO'}**")
    lines.append("")
    lines.append("Any non-target metric movement beyond tolerance is an unexplained")
    lines.append("regression and MUST be investigated before the phase is considered done.")
    return "\n".join(lines) + "\n"


def diff_and_write(out_md: Path, fresh_ndcg10: dict[str, float | None]) -> dict:
    """Compute the diff, write the markdown to out_md, and return the structure."""
    diff = compute_diff(fresh_ndcg10)
    out_md.write_text(render_md(diff), encoding="utf-8")
    return diff


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--bundle", help="path to a regression bundle dir (reads layers/)")
    p.add_argument("--run-id", help="read live corpora/<id>/results/oida-core_<run-id>.json")
    p.add_argument("--out", help="output markdown path (default: <bundle>/diff_vs_baseline.md "
                                 "or ./diff_vs_baseline.md)")
    args = p.parse_args(argv)

    fresh: dict[str, float | None] = {}
    if args.bundle:
        layers = Path(args.bundle) / "layers"
        for c in CORPORA:
            fresh[c] = fresh_ndcg10_from_bundle(c, layers)
        default_out = Path(args.bundle) / "diff_vs_baseline.md"
    else:
        for c in CORPORA:
            fresh[c] = fresh_ndcg10_from_live(c, args.run_id)
        default_out = Path("diff_vs_baseline.md")

    out_md = Path(args.out) if args.out else default_out
    diff = diff_and_write(out_md, fresh)

    print(render_md(diff))
    print(f"wrote {out_md}")
    return 0 if diff["all_within_tolerance"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
