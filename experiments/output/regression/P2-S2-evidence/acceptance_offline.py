#!/usr/bin/env python3
"""P2-S2 OFFLINE ACCEPTANCE — drives the REAL adapter aggregation code path
(OidaClient.retrieve) against a synthesized post-P2-S2 v0 response, proving the
four additive components (freshness/decay/supersession_penalty/salience) flow to
per-doc score_components and VARY across docs (non-constant), while doc_scores /
the ranking are unchanged.

WHY OFFLINE: the live staging service (oida-core.onrender.com) is still on the
integration HEAD (P2-S1b @ 29d9cbe) and does not yet emit ko["score_components"].
This driver exercises the adapter exactly as 02_retrieve.py does (it monkeypatches
only the HTTP boundary, OidaClient._post), so it proves the harness-side plumbing
is correct and reproducible. The live Acceptance is the SAME assertion against a
real retrieve once roadmap/P2-S2 is deployed (see P2-S2-evidence.md §Reproduction).

Run:  python experiments/output/regression/P2-S2-evidence/acceptance_offline.py
"""
import json
import sys
from pathlib import Path

# Import the adapter under test from the repo (stdlib-only; no install).
# __file__ = <repo>/experiments/output/regression/P2-S2-evidence/acceptance_offline.py
# → parents[3] = <repo>/experiments
REPO_EXPERIMENTS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_EXPERIMENTS / "adapters"))
import oida  # noqa: E402


# A synthesized v0 /retrieve/full-oida response shaped EXACTLY as the engine
# emits post-P2-S2: each KO carries ko["score_components"] derived from swept
# state. Three docs, several KOs each, with varied temporalStatus/decay/kScore
# and one DEPRECATED (superseded) KO. Source URIs use the ingest prefix so the
# adapter's source-prefix filter matches them.
PREFIX = oida.DEFAULT_SOURCE_URI_PREFIX  # "beir-corpora"
CORPUS = "clearpath"


def _ko(doc_id, sim, kge, ras, freshness, decay, supersession, salience):
    return {
        "ko_id": f"ko-{doc_id}-{sim}",
        "supporting_sources": [f"{PREFIX}://{CORPUS}/{doc_id}"],
        "similarity": sim,
        "kge_score": kge,
        "regime_adjusted_score": ras,
        # the existing per-KO salience-metadata object is UNTOUCHED by P2-S2 —
        # the numeric salience lives only under score_components.
        "salience": {"s_epi": 0.1, "s_act": 0.2, "gravity": 0.3, "computed_at": None},
        "score_components": {
            "freshness": freshness,
            "decay": decay,
            "supersession_penalty": supersession,
            "salience": salience,
        },
    }


FAKE_RESPONSE = {
    "subgraph": {
        "kos": [
            # doc-A: best KO (highest ras) is CURRENT/fresh, high decay/salience
            _ko("docA", 0.91, 0.70, 0.88, 1.0, 0.95, 0.0, 0.34),
            _ko("docA", 0.60, 0.40, 0.55, 0.5, 0.50, 0.0, 0.18),
            # doc-B: best KO is AGING, mid decay
            _ko("docB", 0.80, 0.62, 0.77, 0.5, 0.41, 0.0, 0.20),
            _ko("docB", 0.50, 0.30, 0.45, 0.0, 0.06, 0.0, 0.05),
            # doc-C: best KO is OBSOLETE and DEPRECATED (superseded) — penalty 1.0
            _ko("docC", 0.72, 0.50, 0.66, 0.0, 0.05, 1.0, 0.02),
        ],
        "edges": [],
        "composition_metadata": {"stopping_criterion": "solver_completed"},
        "dialectic_resolutions": [],
    },
    "metadata": {"elapsed_ms": 12},
}


def main() -> int:
    client = oida.OidaClient(admin_key="offline-fake-key", base_url="http://offline")
    # Patch ONLY the HTTP boundary — everything below (parse, aggregation) is the
    # real shipped adapter code that 02_retrieve.py calls.
    client._post = lambda path, payload: (200, FAKE_RESPONSE, 1.0)

    res = client.retrieve("staging acceptance probe", project_id="oida-clearpath",
                          top_k=10, corpus_slug=CORPUS, compute_query_stance=False)

    print("=== doc_scores (RANKING — must be the regime_adjusted_score of doc-best KO) ===")
    print(json.dumps(res.doc_scores, indent=2))

    print("\n=== per-doc score_components (existing keys + 4 P2-S2 additive) ===")
    print(json.dumps(res.score_components, indent=2))

    sc = res.score_components or {}
    # ---- Acceptance assertions (IC-#2) -------------------------------------
    fresh = [sc[d].get("freshness") for d in sc]
    decay = [sc[d].get("decay") for d in sc]
    sal = [sc[d].get("salience") for d in sc]
    supers = [sc[d].get("supersession_penalty") for d in sc]

    print("\n=== distributions (prove NON-CONSTANT) ===")
    print(f"freshness            distinct={sorted(set(fresh))}")
    print(f"decay                distinct={sorted(set(decay))}")
    print(f"salience             distinct={sorted(set(sal))}")
    print(f"supersession_penalty distinct={sorted(set(supers))}  (sparse: 1.0 only where a DEPRECATED KO is doc-best)")

    checks = []
    checks.append(("freshness present on every doc", all("freshness" in sc[d] for d in sc)))
    checks.append(("decay present on every doc", all("decay" in sc[d] for d in sc)))
    checks.append(("salience present on every doc", all("salience" in sc[d] for d in sc)))
    checks.append(("supersession_penalty present on every doc", all("supersession_penalty" in sc[d] for d in sc)))
    checks.append(("freshness NON-CONSTANT (>1 distinct)", len(set(fresh)) > 1))
    checks.append(("decay NON-CONSTANT (>1 distinct)", len(set(decay)) > 1))
    checks.append(("salience NON-CONSTANT (>1 distinct)", len(set(sal)) > 1))
    checks.append(("supersession_penalty has a 1.0 (the DEPRECATED doc)", 1.0 in supers))
    # doc-best snapshot: docA best KO is the CURRENT/high one → freshness 1.0
    checks.append(("doc-best snapshot correct (docA freshness=1.0)", sc["docA"]["freshness"] == 1.0))
    checks.append(("doc-best snapshot correct (docC supersession=1.0)", sc["docC"]["supersession_penalty"] == 1.0))
    # RANKING UNCHANGED: doc_scores are the regime_adjusted_score of the doc-best
    # KO (score_field default), independent of the new components.
    checks.append(("ranking = regime_adjusted_score of doc-best KO (docA=0.88)", abs(res.doc_scores["docA"] - 0.88) < 1e-9))
    checks.append(("ranking unchanged: docA > docB > docC", res.doc_scores["docA"] > res.doc_scores["docB"] > res.doc_scores["docC"]))
    # existing keys preserved
    checks.append(("existing keys preserved (similarity/kge_score/regime_adjusted_score/contributing_kos)",
                   all(all(k in sc[d] for k in ("similarity", "kge_score", "regime_adjusted_score", "contributing_kos")) for d in sc)))

    print("\n=== ACCEPTANCE CHECKLIST ===")
    ok = True
    for name, passed in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
        ok = ok and passed

    print(f"\nRESULT: {'ALL PASS' if ok else 'FAILURE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
