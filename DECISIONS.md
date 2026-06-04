# Decisions

Dated, tracked record of binding IC (engine-of-record) decisions that change how
the harness or corpora are treated. Each entry is a principled exception, not a
silent tuning step. Never tune to the burned dev corpora; never edit gold labels.

---

## 2026-06-04 — P0-S7: exclude `org-vc-vertexminds` from the ±0.005 baseline gate

**Decision.** Exclude ONLY `org-vc-vertexminds` from the hard
`all_within_tolerance` gate in `experiments/scripts/diff_baseline.py`. The global
tolerance is **unchanged** (`TOLERANCE = 0.005`). The other four corpora remain
gated at ±0.005. The clean **0.5198** NDCG@10 is recorded as the **first valid
Phase-0 baseline** for vertexminds.

**Context.** P0-S7 ran the one authorized live regression. The ±0.005
"engine-unchanged vs archived" gate reproduced bit-for-bit on 4/5 corpora (three
at delta exactly 0.0000), which rules out non-determinism and any broad engine
change. It FAILED on exactly one corpus:

| corpus | archived NDCG@10 | fresh NDCG@10 | delta | within ±0.005 |
|---|---|---|---|---|
| org-consulting-clearpath | 0.4574 | 0.4586 | +0.0013 | ✓ |
| org-iot-fireglass | 0.6081 | 0.6081 | 0.0000 | ✓ |
| **org-vc-vertexminds** | 0.4564 | **0.5198** | **+0.0634** | ✗ |
| inv-mystery-redhood | 0.5162 | 0.5162 | 0.0000 | ✓ |
| inv-ashford-mystery | 0.1982 | 0.1982 | 0.0000 | ✓ |

**Why this is an exclusion, not a regression and not tuning.**

- (a) The **archived** vertexminds number (0.4564) comes from the QUARANTINED
  degenerate-config run, declared **INVALID** by IC decision #1 / the P0-S1
  quarantine README (`archive/degenerate-config-2026-06-01/README.md`:
  "Status: INVALID. Do not cite these numbers as OIDA results."). Gating fresh
  output against a known-invalid reference is meaningless.
- (b) The clean run ingested vertexminds **healthily**. Roadmap §5 recorded the
  degenerate run at `partial_error_count ≈ 2951` vs `kos_created ≈ 1954`. This
  clean run's `harness_health.md` shows **kos_created=5250, partial_error_count=0**.
  That is ~2.7× more knowledge indexed (1954→5250) with zero partial errors
  (2951→0). More knowledge indexed → retrieval improved → NDCG@10 rose +0.0634.
  This is **BETTER**, not a regression.
- (c) The clean **0.5198** is hereby the **first valid Phase-0 baseline** for
  vertexminds. The archived 0.4564 must never be cited.
- The engine, gold (`experiments/annotations/`), and qrels (`corpora/*/qrels/`)
  are **untouched**. Only the harness's treatment of a single documented-invalid
  archived reference value changes.

**Scope guard.** `TOLERANCE` stays 0.005. No global tolerance change. The other
four corpora remain gated at ±0.005. The raw vertexminds delta (+0.0634) is still
computed and surfaced in `diff_vs_baseline.md`; it is shown EXCLUDED-with-reason,
never hidden.

**Implementation.** `BASELINE_GATE_EXCLUSIONS` dict in `diff_baseline.py`
(consulted where `all_within_tolerance` is folded). A comment in
`diff_baseline.py` references this record.

**Open question carried forward (P1-S7).** vertexminds had 19/77 docs produce
0 KOs in the clean ingest (`kos_created=5250`, `0 partial_errs`). Phase 1 / P1-S7
must verify whether 5250 is the correct count or whether ingest still silently
drops content. P0-S7 does NOT resolve this.
