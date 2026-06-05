# org-offshore-wind-galewright — Ground-Truth Design Dossier (DRAFT)

> ⚠️ **DRAFT FOR HUMAN VALIDATION.** This document records the *planted* epistemic
> ground truth for the corpus — the gold the paper's numbers will rest on. It is a
> human-review surface. The machine-readable gold lives (gitignored) under
> `experiments/annotations/{contra_sets,supersession_chains,lifecycle,stance_gold,temporal_queries}/org-offshore-wind-galewright.json`.
> **Before this corpus is sealed as the Phase-4 benchmark, an offshore-wind /
> consenting domain reader and a benchmark reviewer should verify every relation
> below.** Because this file publishes the answer key, decide whether to keep it
> private/redacted before any public dataset release.

## Integrity statement (blindness)

The documents **and** these annotations were authored **without running the corpus
through OIDA or any retrieval system**, and without inspecting any engine output. No
relation was tuned to, or iterated against, a score. The corpus is therefore
*fresh/unseen* for Phase-4 purposes. It is deliberately **not** wired into the harness
(see "Pre-registration wiring" below) so it cannot be accidentally burned.

## Cast

| Person / body | Role |
|---|---|
| Eleanor Vance | Project Director (charter, programme, FID) |
| Ravi Menon | Head of Engineering (turbine selection) |
| Sophie Larsson | Head of Consents & Environment (EIA, landfall) |
| Tom Reilly | Head of Grid & Interconnection (NGESO offers, Grid Code) |
| Priya Shah | CFO / Finance (cost, energy assumption, FID case) |
| James Crowe | Stakeholder & Communications Lead (community, jobs retraction) |
| AeroAssess | Resource consultant (48% CF / 2,950 GWh) |
| Northwind Ecology | EIA ecology consultant (draft bird chapter, ~120/yr) |
| Marrow Bird Trust | Seabird NGO, opposition (~600/yr, objects) |
| Calder Coast Fishermen's Association (CCFA) | Fisheries, opposition |
| NGESO (the System Operator) | Grid connection offers |
| The Crown Estate | Seabed lease (Agreement-for-Lease) |
| Aeolus Turbines | OEM (AT-12 = 12 MW, AT-15 = 15 MW) |

## Timeline

2024-09 seabed AfL · 2024-12 Grid Code reference · 2025-01 market context · 2025-02 charter + kickoff ·
2025-03 initial programme (COD 2029) + initial NGESO offer (Calder 2031) · 2025-04 community brief (1,200 jobs) ·
2025-05 initial layout (AT-12, 58) · 2025-06 resource assessment + initial landfall (Saltmarsh) ·
2025-07 turbine appraisal · 2025-08 AT-15 decision (47) + Aeolus availability · 2025-09 draft bird chapter (~120) + landfall revised (Drover's Gap) + consents review ·
2025-10 board deck (£2.4bn) + Bird Trust submission (~600) + CCFA objection + consultation event ·
2025-11 accelerated NGESO offer (Marrow Bank 2030) + revised programme (COD 2030) + finance model (£2.65bn, 42%) ·
2025-12 jobs retraction + corrected brief · 2026-01 FID memo + FID board (approve).

---

## 1. Contradictions (`contra_sets`)

| ID | Query | Side A | Side B | The conflict |
|---|---|---|---|---|
| **C1** | q02 | `02-subject/resource-assessment-aep` (48% / 2,950 GWh) | `02-subject/financial-model-summary` (42% / 2,580 GWh) | Genuine unreconciled disagreement on the expected capacity factor: AeroAssess stands by 48%; finance rejects it as optimistic/unfinanceable and underwrites 42%. Neither side moved; left to the lenders' technical adviser. Both sides score-3. |
| **C2** | q08 | `02-subject/eia-bird-collision-chapter` (~120/yr, low significance) | `04-external-comms/email/email-ext-003-birdtrust-submission` (~600/yr, high significance) | Same collision-risk model, different avoidance-rate assumption → a 5–6× gap and opposite significance conclusions. Unresolved (to be examined). Both sides score-3. |
| **C3** | q03 | `07-documents/board-deck-investment-case` (£2.4bn, stale) | `07-documents/fid-memo` (£2.65bn, binding) | Pre-finalisation estimate vs committed CAPEX. The deck self-flags as interim and is superseded, but two project docs carry different numbers. Side A (deck) score-2, Side B (FID memo) score-3 — the same 3/2 stale-vs-binding split as the exemplar's q03. |

## 2. Supersessions (`supersession_chains`)

| ID | Query | Binding (current) | Superseded | Note |
|---|---|---|---|---|
| **S1** | q01 | `07-documents/turbine-selection-memo-at15` | `07-documents/layout-plan-at12-initial` | AT-12 (58) → AT-15 (47); memo states it supersedes the AT-12 layout. Conditional on OEM availability (email-ext-005). |
| **S2** | q04 | `07-documents/landfall-decision-revised` | `07-documents/landfall-siting-initial-saltmarsh` | Saltmarsh Point → Drover's Gap; Saltmarsh ruled out on SSSI grounds; memo states it supersedes the initial siting note. |
| **S3** | q05 | `07-documents/programme-revised-cod2030` | `07-documents/programme-initial-cod2029` | COD 2029 → 2030 (net of consent slippage and grid acceleration); states it supersedes the initial programme. |
| **S4** | q06 | `04-external-comms/email/email-ext-002-ngeso-offer-accelerated` | `04-external-comms/email/email-ext-001-ngeso-offer-initial` | Calder/2031 → Marrow Bank/2030; revised offer states it supersedes and withdraws the March offer. Internal cascade email-internal-004 is co-current. |

## 3. Retraction (`lifecycle`)

| Document | State | superseded_by | Note |
|---|---|---|---|
| `07-documents/community-brief-jobs-original` | **RETRACTED** | `07-documents/community-brief-jobs-corrected` | The "1,200 local jobs" figure was disavowed as unsubstantiated for Marrowbank (email-internal-006; FID board), not merely re-versioned. Basis for the q07 NEI and a qrels-0 / should-not-retrieve trap. |

## 4. Temporal structure (`temporal_queries` + `lifecycle`)

- **CURRENT_STATE (13 queries):** q01, q02, q03, q04, q05, q06, q07, q08, q09, q14, q15, q16, q17. Each has `gold_current_docs`; supersession queries also have `gold_superseded_docs`. Drives current-state accuracy and superseded-leakage.
- **HISTORICAL (2):** q12 (why Saltmarsh rejected), q13 (why off the AT-12). The earlier version is *wanted* (in `gold_historical_docs`, not penalized) — deliberately the mirror image of q04/q01, where the same earlier doc is the superseded leakage doc.
- **STABLE_KNOWLEDGE (2):** q10 (`grid-code-reference`, 2024-12-01) and q11 (`crown-estate-seabed-lease`, 2024-09-01). Both stable references are the **two oldest documents in the corpus**, older than every FID-era doc — they test **freshness-overbias** (a recency-biased ranker that buries them under the 2025–2026 churn is penalized) and **stable-knowledge retention**.
- **Lifecycle** (all 37 docs annotated): CANONICAL 13 · ACTIVE 14 · SUPERSEDED 5 · PROVISIONAL 1 (`eia-bird-collision-chapter`) · STALE 1 (`consent-status-tracker`) · RETRACTED 1 (`community-brief-jobs-original`) · ARCHIVED 2 (`marrowbank-teams`, `calendar-events`). All seven states are exercised.

## 5. Stance & abstention (`stance_gold`)

6 stance-evaluable queries: **SUPPORTS** q01, q09 · **CONTRADICTS** q02, q03, q08 · **NEI** q07. 11 factoid (non-evaluable).

- **NEI / abstention (q07)** is the load-bearing abstention case: "how many local jobs will the Marrowbank project create?" The corpus cannot give a number — the 1,200 figure was withdrawn, only ~300 construction FTE are substantiated, and long-term/operational local jobs are explicitly "genuinely uncertain" and under study. A correct system **abstains / says the evidence is insufficient to give a figure**; asserting a number (or citing the retracted 1,200) is a false commitment.

## 6. Traps (qrels score-0)

| Query | Trap doc | Why it's a trap |
|---|---|---|
| q07 | `07-documents/community-brief-jobs-original` | The retracted "1,200 jobs" promise; topically magnetic, but the figure was disavowed. |
| q10 | `04-external-comms/email/email-ext-002-ngeso-offer-accelerated` | Topically "grid", but it is the commercial connection *offer* (point/date), not the Grid Code *requirements*. |
| q16 | `07-documents/board-deck-investment-case` | The stale £2.4bn deck; the wrong (superseded) answer to "current CAPEX figure". |
| q17 | `02-subject/consent-status-tracker` | The STALE "turbine TBC / landfall TBC" snapshot; surfacing its outdated lines as the current status is leakage. |

### Deliberate q03 / q16 split (board deck)

The October board deck (`board-deck-investment-case`, £2.4bn) plays **two roles by design**:
- in **q03** ("is CAPEX reported consistently?") it is a **relevant contradiction side** (qrels-2) — the inconsistency *is* the answer, so both numbers must be retrieved;
- in **q16** ("current CAPEX figure?") it is the **stale trap** (qrels-0, should-not-retrieve) — the current figure is £2.65bn and the deck is the wrong, superseded answer.

This is intentional and mirrors the exemplar's q03/board-report pattern: the same document is relevant or a trap depending on whether the question is about *consistency* or about the *current value*. Its lifecycle state (SUPERSEDED, superseded_by the FID memo) is consistent with both framings. In `temporal_queries`, the deck is left out of q03's gold entirely (so the temporal and adversarial signals do not conflict) and is the should-not-retrieve doc only in q16.

## 7. Human-validation checklist

1. **Domain plausibility** — would a real offshore-wind developer plant these exact figures and decisions (48% vs 42% CF; ~120 vs ~600 kittiwake collisions; £2.4bn → £2.65bn; COD 2029 → 2030; Calder/2031 → Marrow Bank/2030)? Flag anything contrived. The numbers are illustrative-realistic, not benchmarked to a specific real project.
2. **C1** — the 48%/42% gap is a genuine, unreconciled disagreement (AeroAssess stands by 48%; finance rejects it as optimistic and underwrites 42%; referred to the lenders' technical adviser, unresolved at FID). q02 tests detection of the conflict (CONTRADICTS, evaluable); q15 treats the same pair as a descriptive *explain-the-difference* factoid. Confirm the disagreement reads as genuine (not a documented haircut) and that the q02/q15 split is fair.
3. **C3 / board deck** — confirm the 3/2 split (FID memo 3, deck 2) and the q03/q16 dual role are acceptable, as in the exemplar.
4. **q07 NEI** — confirm the corpus genuinely cannot give a local-jobs figure (by construction: the 1,200 figure is retracted, only ~300 construction FTE substantiated, O&M/local jobs explicitly under study).
5. **STALE vs SUPERSEDED** — the consent-status-tracker is STALE (an outdated snapshot, not the prior version of one binding doc) with no `superseded_by`; the version-paired obsolete docs are SUPERSEDED. Confirm this distinction holds.
6. **qrels grades** — spot-check that score-3 docs each *fully* answer their query and score-2 docs *materially* support it; confirm the four score-0 traps are genuinely misleading-but-on-topic.
7. **Freshness-overbias** — confirm the two stable references (seabed lease 2024-09-01, Grid Code 2024-12-01) are the oldest docs and that a fresh-biased ranker would be wrong to bury them.
8. **No leakage** — confirm no annotation was influenced by engine output (it was not).

## 8. Pre-registration wiring (NOT done here — Phase-4 step)

To make this corpus scorable by the full harness after sign-off:
- add `"org-offshore-wind-galewright"` to `experiments/scripts/eval_common.py::ALL_CORPORA`;
- add a `run_regression.sh` `OIDA_CORE_PROJECT_IDS` route + the matching `OIDA_CORE_KEY_<SLUG>` in `.env`;
- (optional) add a `CUTOFFS["org-offshore-wind-galewright"]` entry in `06_eval_temporal.py` for the per-cutoff temporal diagnostic (suggested: `["2025-08-08","2025-11-18","2026-01-20"]` — straddling the turbine, programme/CAPEX, and FID decisions);
- the gold annotation files are already in place under `experiments/annotations/` (gitignored).

Until then, individual layers can be run by passing the corpus id explicitly (e.g. `04_eval_adversarial.py org-offshore-wind-galewright`), except Layer-4 temporal, which filters to `ORG_CORPORA`.
