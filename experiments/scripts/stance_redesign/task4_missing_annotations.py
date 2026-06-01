#!/usr/bin/env python3
"""Task 4 — inventory the stance-bearing gold annotations that metric (b) needs
but that do NOT yet exist, and emit a reviewable scaffold. Read-only, no API.

Metric (b) (Stance-Evidence Recall@k) needs, per stance-evaluable SUPPORTS /
CONTRADICTS query, an explicit set of doc IDs that CARRY the correct stance.
Today the repo has:
  * contra_sets/<corpus>.json  — conflicting 'sides' for SOME contradiction queries
  * qrels score-3 ("binding gold") — a usable PROXY, but "most relevant" != "stance-bearing"
There is no `stance_doc_ids` field anywhere. This script reports exactly which
queries are covered by a purpose-built annotation, which fall back to the proxy,
and which annotation inconsistencies need a human decision. It also writes a
scaffold (annotations/stance_doc_gold/<corpus>.json) pre-filled with the proxy /
contra sides for Carlo+Federico to confirm — NOT a finished annotation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eval_common as ec  # noqa: E402

OUT = ec.REPO_ROOT / "experiments" / "output" / "stance_redesign"
SCAFFOLD_DIR = OUT / "stance_doc_gold_scaffold"
FLAG_WORDS = ("upgrade", "FLAG", "flag", "low-confidence", "low confidence",
              "owners should", "annotators", "JUDGMENT CALL", "verify")


def main():
    inv = {"corpora": {}, "totals": {}}
    tot = {"evaluable_sc": 0, "nei": 0, "non_evaluable": 0,
           "C_with_contra": 0, "C_without_contra": 0, "S_proxy_only": 0,
           "inconsistencies": 0}
    SCAFFOLD_DIR.mkdir(parents=True, exist_ok=True)

    for corpus in ec.ORG_CORPORA:
        sg = ec.load_annotation("stance_gold", corpus) or {}
        qrels = ec.load_qrels(corpus)
        contra = ec.load_annotation("contra_sets", corpus) or {}
        rows = []
        scaffold = {}
        for q, g in sg.items():
            gold = g.get("gold_stance")
            ev = g.get("stance_evaluable")
            notes = g.get("notes", "")
            flags = [w for w in ("upgrade", "FLAG", "low-confidence", "low confidence",
                                 "JUDGMENT CALL") if w in notes]
            has_contra = q in contra
            s3 = sorted(d for d, s in qrels.get(q, {}).items() if s == 3)
            row = {"qid": q, "gold_stance": gold, "stance_evaluable": ev,
                   "has_contra_set": has_contra, "score3_docs": s3, "flags": flags}

            # inconsistency detection
            incons = []
            if not ev and "upgrade" in notes:
                incons.append("notes say UPGRADE to evaluable but field is false")
            if not ev and has_contra:
                incons.append("non-evaluable yet has a contra_set entry")
            if gold == "NEI" and has_contra:
                incons.append("gold=NEI yet has a contra_set entry")
            if ev and not gold:
                incons.append("stance_evaluable=true but gold_stance is null")
            row["inconsistencies"] = incons
            if incons:
                tot["inconsistencies"] += 1

            # classify coverage for metric (b)
            if not ev or not gold:
                row["status"] = "non_evaluable"
                tot["non_evaluable"] += 1
            elif gold == "NEI":
                row["status"] = "NEI_no_positive_evidence (excluded from recall; needs definition)"
                tot["nei"] += 1
            elif gold == "CONTRADICTS":
                tot["evaluable_sc"] += 1
                if has_contra:
                    row["status"] = "C_covered_by_contra_sets"
                    tot["C_with_contra"] += 1
                    scaffold[q] = {"gold_stance": gold, "stance_doc_ids": sorted(
                        {d for side in contra[q]["sides"] for d in side}),
                        "sides": contra[q]["sides"], "source": "contra_sets",
                        "_needs_review": False}
                else:
                    row["status"] = "C_MISSING_contra_set (proxy=score3)"
                    tot["C_without_contra"] += 1
                    scaffold[q] = {"gold_stance": gold, "stance_doc_ids": s3,
                                   "source": "PROXY_qrels_score3", "_needs_review": True}
            elif gold == "SUPPORTS":
                tot["evaluable_sc"] += 1
                row["status"] = "S_MISSING_stance_doc_ids (proxy=score3)"
                tot["S_proxy_only"] += 1
                scaffold[q] = {"gold_stance": gold, "stance_doc_ids": s3,
                               "source": "PROXY_qrels_score3", "_needs_review": True}
            rows.append(row)
        inv["corpora"][corpus] = rows
        (SCAFFOLD_DIR / f"{corpus}.json").write_text(
            json.dumps(scaffold, indent=2, ensure_ascii=False), encoding="utf-8")

    inv["totals"] = tot
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "task4_missing_annotations.json").write_text(
        json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- print ----
    print("\n===== TASK 4 — MISSING STANCE-BEARING ANNOTATIONS (metric b) =====\n")
    for corpus, rows in inv["corpora"].items():
        print(f"--- {corpus} ---")
        for r in rows:
            if r["status"] == "non_evaluable":
                continue
            tag = r["status"]
            extra = ""
            if r["inconsistencies"]:
                extra = "  ⚠ " + "; ".join(r["inconsistencies"])
            print(f"  {r['qid']} {str(r['gold_stance']):11s} contra={int(r['has_contra_set'])} "
                  f"score3={len(r['score3_docs'])}  {tag}{extra}")
        print()
    print("===== TOTALS (3 org corpora) =====")
    for k, v in tot.items():
        print(f"  {k:22s} {v}")
    print(f"\n  -> purpose-built stance docs exist for {tot['C_with_contra']} / {tot['evaluable_sc']} "
          f"evaluable S/C queries (all contradiction).")
    print(f"  -> {tot['S_proxy_only'] + tot['C_without_contra']} queries "
          f"({tot['S_proxy_only']} SUPPORTS + {tot['C_without_contra']} CONTRADICTS) need a "
          f"purpose-built `stance_doc_ids`; currently proxied by qrels score-3.")
    print(f"  -> {tot['nei']} NEI queries need an explicit 'insufficiency-evidence' definition or stay excluded.")
    print(f"  -> {tot['inconsistencies']} annotation inconsistencies need a human decision.")
    print(f"\nscaffold written → {SCAFFOLD_DIR.relative_to(ec.REPO_ROOT)}/<corpus>.json")
    print(f"inventory written → experiments/output/stance_redesign/task4_missing_annotations.json")


if __name__ == "__main__":
    main()
