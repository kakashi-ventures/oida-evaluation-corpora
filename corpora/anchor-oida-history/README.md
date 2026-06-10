# anchor-oida-history — Dataset Card

**Family:** anchor · **Domain:** OIDA program internal history (versioned specs, decision
records, findings, handoffs)
**Phase-4 fresh corpus** (P4-S1, anchor domain). One of the three D2 fresh domains
(anchor / EU-reg / RAG-lit); it **supersedes** the earlier ORG batch (D2, 2026-06-08).

> **PILOT** — calibration corpus. Sized to exercise R1–R6 and estimate variance/effect-size
> before the full re-power (≥40–50 queries/stratum). Not the full corpus.

## Scenario

The internal history of the OIDA remediation program across Phases 0–4: a degenerate-config
run is quarantined; ingest, decay, contradiction-exposure, and recency signals are built and
verified; a regime lever is tried and dropped; and Phase-4 is scoped — retrieval mode,
success metric, edge-graph freeze, and run-1 vs run-2 signal scope. Decisions **evolve over
time**, some are **stable invariants**, and several plausible-but-stale or fresh-but-wrong
documents compete with the binding answer.

Documents are a **pseudonymised** retelling (role-titles kept: IC, overviewer, eng-arch,
corpus-author; personal names removed). `effective_date`s live **in-text** and are spread
across a 2025-09 → 2026-06 timeline that **preserves the true supersession order and the true
"current" designation**; the absolute spread is a design knob for the R6 signal margin.

## Why it is challenging

- **Evolving decisions (R1).** A decision changes over time; the binding answer is the
  latest version (which carries an in-text "supersedes …" cue), not an earlier one.
- **Calibrated temporal mix (R1.4).** 50% freshness-helps / 25% stable (a timeless invariant
  the freshest doc must **not** demote) / 25% fresh-distractor (a fresh-dated doc that is
  wrong) — so a naive "freshest-wins" ranker fails.
- **Cosine can't win (R1.2).** For every evolving-decision query a superseded/competitor doc
  is at least as text-similar as the current one; lifecycle/recency must do the work.
- **Cross-document contradictions (R4).** Doc A asserts X, doc B asserts ¬X (e.g. a §1
  "ingest is clean" diagnosis vs the measured "silent enqueue failure").
- **Authority × relevance (R3).** Some queries are answered by a canonical decision record;
  others by a non-canonical finding while the canonical doc is a stale lure.
- **Traps with false cues (R5).** Several traps carry **false/misleading** "supersedes" /
  "updates" language to catch a keyword-only detector.

## Contents

| | |
|---|---|
| Documents | 37 |
| Queries | 13 (8 temporal clusters + 3 contradiction + 2 authority) |
| Trap pairs | 82 explicit-zero (query, doc) judgments |
| Strata mix | freshness 50% · stable 25% · distractor 25% |

## Gold & integrity

Gold (relevance judgments + temporal/supersession/contradiction annotations) is **private and
gitignored** until the pre-registered run (P4-S2). Public here: `corpus.jsonl`, `queries.jsonl`,
this card. Per the D2 protocol — **AI drafts, human decides**: labels were drafted then
**adjudicated by the human IC**; the corpus is **frozen before each run** (no post-hoc edits to
pass a gate). Authored from ground truth, **never** tuned against OIDA's retrieval output.
Synthetic/pseudonymised; any resemblance to specific individuals is removed by design.
