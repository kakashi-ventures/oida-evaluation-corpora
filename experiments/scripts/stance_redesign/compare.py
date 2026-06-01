#!/usr/bin/env python3
"""Task 3 — compare the new stance metrics to the shipped stance_accuracy and
attribute OIDA's gap. Read-only; consumes the metric (a)/(b) JSON artifacts.

Prints:
  * headline pooled table: OLD stance_acc | (a) evidence-grounded | (b) recall@10
  * rankings under each metric (where does OIDA sit?)
  * decomposition for oida-core vs graphrag:
        OLD -> OLD+fixJudge -> (a)k=1 -> (a)k=10 -> (b)recall@10
    isolating judge-bug, generation, and retrieval-depth effects.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eval_common as ec  # noqa: E402

OUT = ec.REPO_ROOT / "experiments" / "output" / "stance_redesign"
A = json.load(open(OUT / "metric_a_evidence_grounded.json"))
B = json.load(open(OUT / "metric_b_recall.json"))
SYS = ec.SYSTEMS


def acc(system, col):
    m = A["per_system_pooled"][system].get(col, {})
    return m.get("stance_accuracy")


def recall(system, k, kind="stance_recall_all"):
    return B["per_system_pooled"][system][str(k)][kind]


def rank(d):  # dict system->value -> ordered list desc
    return sorted(((s, v) for s, v in d.items() if v is not None), key=lambda kv: -kv[1])


def fmt(v):
    return f"{v:.3f}" if isinstance(v, (int, float)) else "  —  "


def main():
    print("\n================ HEADLINE: POOLED over 3 org corpora ================\n")
    print(f"{'system':16s}  OLD-acc  (a)k1  (a)k10   (b)any@10 (b)all@10 (b)sides@10")
    headline = {}
    for s in SYS:
        old = acc(s, "old"); a1 = acc(s, "a_k1"); a10 = acc(s, "a_k10")
        rany = recall(s, 10, "stance_recall_any"); rall = recall(s, 10, "stance_recall_all")
        rsd = recall(s, 10, "contra_all_sides")
        headline[s] = {"old": old, "a_k1": a1, "a_k10": a10,
                       "b_any10": rany, "b_all10": rall, "b_sides10": rsd}
        print(f"{s:16s}  {fmt(old)}   {fmt(a1)}  {fmt(a10)}   {fmt(rany)}    {fmt(rall)}    {fmt(rsd)}")

    print("\n---- RANKINGS (best -> worst) ----")
    def show_rank(name, d):
        r = rank(d)
        line = "  ".join(f"{i+1}.{s}({v:.2f})" for i, (s, v) in enumerate(r))
        print(f"{name:24s} {line}")
    show_rank("OLD stance_accuracy", {s: acc(s, "old") for s in SYS})
    show_rank("OLD + label-fixed judge", {s: acc(s, "old_fixjudge") for s in SYS})
    show_rank("(a) evidence-grounded k=1", {s: acc(s, "a_k1") for s in SYS})
    show_rank("(a) evidence-grounded k=10", {s: acc(s, "a_k10") for s in SYS})
    show_rank("(b) stance-recall_all@10", {s: recall(s, 10, "stance_recall_all") for s in SYS})
    show_rank("(b) stance-recall_any@10", {s: recall(s, 10, "stance_recall_any") for s in SYS})

    print("\n================ DECOMPOSITION: oida-core vs graphrag ================")
    print("(stance_accuracy unless noted; gap = graphrag - oida-core)\n")
    stages = [
        ("OLD (published)", "old"),
        ("OLD answers + label-fixed judge", "old_fixjudge"),
        ("(a) fixed reader, k=1", "a_k1"),
        ("(a) fixed reader, k=10", "a_k10"),
    ]
    print(f"{'stage':34s} {'oida-core':>10s} {'graphrag':>10s} {'gap':>8s}")
    gaps = {}
    for label, col in stages:
        o = acc("oida-core", col); g = acc("graphrag", col)
        gap = (g - o) if (o is not None and g is not None) else None
        gaps[col] = gap
        print(f"{label:34s} {fmt(o):>10s} {fmt(g):>10s} {fmt(gap):>8s}")
    # metric b rows
    for kind, nm in [("stance_recall_all", "(b) recall_all@10"),
                     ("stance_recall_any", "(b) recall_any@10")]:
        o = recall("oida-core", 10, kind); g = recall("graphrag", 10, kind)
        print(f"{nm:34s} {fmt(o):>10s} {fmt(g):>10s} {fmt(g-o):>8s}")

    print("\n---- GAP ATTRIBUTION (oida-core) ----")
    old_gap = gaps["old"]; a10_gap = gaps["a_k10"]; a1_gap = gaps["a_k1"]
    judge_gap = gaps["old_fixjudge"]
    if old_gap:
        closed_k10 = old_gap - a10_gap
        print(f"  shipped gap (graphrag - oida-core)      = {old_gap:+.3f}")
        print(f"  gap after fixing ONLY the judge          = {judge_gap:+.3f}  "
              f"(judge-bug share: {(old_gap-judge_gap)/old_gap*100:.0f}% of gap)")
        print(f"  gap after holding generation constant k=1= {a1_gap:+.3f}")
        print(f"  gap after generation constant + depth k=10={a10_gap:+.3f}")
        print(f"  => generation confound closed {closed_k10:+.3f} of the {old_gap:+.3f} gap "
              f"({closed_k10/old_gap*100:.0f}%).")
        oc_old = acc("oida-core", "old"); oc_a10 = acc("oida-core", "a_k10")
        print(f"  oida-core's OWN accuracy: OLD {oc_old:.3f} -> (a)k10 {oc_a10:.3f} "
              f"(+{oc_a10-oc_old:.3f}, {(oc_a10-oc_old)/max(oc_old,1e-9)*100:.0f}% relative).")

    comp = {"headline_pooled": headline,
            "decomposition_oida_core_vs_graphrag": {col: gaps[col] for _, col in stages}}
    (OUT / "comparison_stance_redesign.json").write_text(
        json.dumps(comp, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {(OUT/'comparison_stance_redesign.json').relative_to(ec.REPO_ROOT)}")


if __name__ == "__main__":
    main()
