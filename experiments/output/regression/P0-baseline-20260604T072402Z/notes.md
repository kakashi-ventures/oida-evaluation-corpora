# notes.md — verifier comparison contract + falsification

## Verifier comparison contract

When the verifier re-runs this harness, compare its fresh bundle against
THIS Phase-0 baseline under the following rules.

### MUST-MATCH (deterministic; a mismatch is a real regression)
- per-corpus **L1 NDCG@10 / Recall@10 / MAP@10** (±1e-6) — pure functions of
  runs.json + qrels; the engine is unchanged in Phase 0.
- per-corpus **stance metric (b) `stance_recall_any@k`** — pure retrieval, no
  judge; deterministic from runs.json + annotations + qrels.
- per-corpus **kos_created** (ingest is deterministic + idempotent after a
  clean RESET).

### TOLERATED (non-deterministic or environmental; NOT a regression)
- timestamps, the `<ts>` bundle dir name, the `run_id`.
- retrieve latency (p50/p95) and imputed cost.
- LLM-nondeterministic artifacts: edge counts, contradiction structures, and
  the micro-probe's EXACT label mix. Only the **>=1 CONTRADICTS** invariant
  must hold (the judge can legitimately shift a borderline label run-to-run).

## Falsification contract (what this harness measures / how / where / effect)
- MEASURES: regression — does a clean re-ingest + 5-layer score on the burned
  corpora reproduce the archived NDCG@10 within ±0.005 (engine unchanged),
  with all signals present + non-constant and the judge axis live (>=1
  CONTRADICTS)?
- HOW: clean RESET (Render one-off) -> deterministic 01_ingest -> bounded
  worker drain -> 02 retrieve -> 03..07 layer scorers -> in-harness per-query
  NDCG@10 / score-component spreads + a live micro-probe.
- WHERE: serialized into this bundle (layers/, harness_health.md,
  signal_presence.md, diff_vs_baseline.md, run_manifest.json).
- WHAT CHANGES: nothing in the engine — the harness is read-mostly (it only
  mutates the live bench projects' KOs via the documented RESET + ingest). It
  GATES phase completion: a phase is not done until its bundle is produced and
  no unexplained regression on a non-target metric appears.

## Worker-drain settle-wait: param=90s actual=90.0s health_after=200
LABEL: cosmetic for P0 — cross-document edges arrive in Phase 1; not a claim that draining produced edges

## Guardrail
BURNED dev corpora = regression / sanity ONLY, never an OIDA pass/fail claim.
Pass/fail lives exclusively in the Phase-4 fresh corpora.

## P1-S7 carry-forward (2026-06-04)
vertexminds: 19/77 docs produced 0 KOs in the clean ingest (kos_created=5250, 0
partial_errs) — Phase 1 / P1-S7 must verify whether 5250 is the correct count or
ingest still silently drops content. P0-S7 does NOT resolve this.

## Baseline-gate exclusion (2026-06-04, P0-S7)
org-vc-vertexminds is EXCLUDED from the hard ±0.005 NDCG@10 reproduction gate.
Its archived reference (0.4564) is the QUARANTINED degenerate-config number
(IC decision #1 / archive/degenerate-config-2026-06-01/README.md: INVALID, do not
cite). The clean run ingested it healthily (kos 1954->5250, partial_errs 2951->0),
so NDCG@10 rose +0.0634 (BETTER, not a regression); the clean 0.5198 is the first
valid Phase-0 baseline for vertexminds. The other 4 corpora remain gated at ±0.005
(TOLERANCE unchanged). See DECISIONS.md and diff_vs_baseline.md (raw delta retained,
shown excluded-with-reason). The regenerated diff_vs_baseline.md reports
all_within_tolerance=YES with vertexminds documented-excluded.
