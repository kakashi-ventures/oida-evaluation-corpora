# diff_vs_baseline.md

harness-validation (engine unchanged), NOT an OIDA performance claim.

±0.005 L1 NDCG@10, fresh vs archived (degenerate-config run, quarantined for reference). The engine is unchanged in Phase 0, so
fresh must reproduce archived within tolerance — this validates the
HARNESS, it is not an OIDA performance number. Burned corpora are
regression/sanity only; pass/fail lives in the Phase-4 fresh corpora.

| corpus | archived NDCG@10 | fresh NDCG@10 | delta | |delta|<=0.005 |
|---|---|---|---|---|
| org-consulting-clearpath | 0.4574 | 0.4586 | 0.0013 | ✓ |
| org-iot-fireglass | 0.6081 | 0.6081 | 0.0000 | ✓ |
| org-vc-vertexminds | 0.4564 | 0.5198 | 0.0634 | ✗ (EXCLUDED — see below) |
| inv-mystery-redhood | 0.5162 | 0.5162 | 0.0000 | ✓ |
| inv-ashford-mystery | 0.1982 | 0.1982 | 0.0000 | ✓ |

**EXCLUDED from the hard gate: org-vc-vertexminds** (raw delta +0.0634, ±0.005 NOT met, retained above for transparency).

2026-06-04 (P0-S7): EXCLUDED from the hard ±0.005 gate. (a) The archived reference (0.4564) is from the QUARANTINED degenerate-config run, declared INVALID by IC decision #1 / the P0-S1 quarantine README (archive/degenerate-config-2026-06-01/README.md: 'Do not cite these numbers'). (b) The clean run ingested vertexminds HEALTHILY — harness-confirmed kos_created 1954->5250 and partial_error_count 2951->0 (roadmap §5 -> harness_health.md) — i.e. ~2.7x more knowledge indexed, so retrieval improved (NDCG@10 +0.0634, BETTER not a regression). (c) The clean 0.5198 is hereby recorded as the FIRST VALID Phase-0 baseline for vertexminds; the archived 0.4564 must never be cited. No global tolerance change: TOLERANCE stays 0.005 and the other 4 corpora remain gated at ±0.005.

**All within ±0.005 (org-vc-vertexminds excluded per documented IC decision): YES**

Any non-target metric movement beyond tolerance (for a NON-excluded
corpus) is an unexplained regression and MUST be investigated before
the phase is considered done. Exclusions are documented, dated
exceptions (see DECISIONS.md), NOT a tolerance change.
