# org-hospital-stillwater — Ground-Truth Design Dossier (DRAFT)

> ⚠️ **DRAFT FOR HUMAN VALIDATION.** This document records the *planted* epistemic
> ground truth for the corpus — the gold the paper's numbers will rest on. It is a
> human-review surface. The machine-readable gold lives (gitignored) under
> `experiments/annotations/{contra_sets,supersession_chains,lifecycle,stance_gold,temporal_queries}/org-hospital-stillwater.json`.
> **Before this corpus is sealed as the Phase-4 benchmark, a clinician + a reviewer
> should verify every relation below.** Because this file publishes the answer key,
> decide whether to keep it private/redacted before any public dataset release.

## Integrity statement (blindness)

The documents **and** these annotations were authored **without running the corpus
through OIDA or any retrieval system**, and without inspecting any engine output. No
relation was tuned to, or iterated against, a score. The corpus is therefore
*fresh/unseen* for Phase-4 purposes. It is deliberately **not** wired into the harness
(see "Pre-registration wiring" below) so it cannot be accidentally burned.

## Cast

| Person | Role |
|---|---|
| Yusuf Adeyemi, MD | CMO; executive sponsor |
| Karen Holloway, MD | VP Quality & Patient Safety; initiative lead |
| Marcus Tran, MD | ED Medical Director (pro universal 1-hour) |
| Elena Soto, MD | Infectious Disease / Antimicrobial Stewardship (pro stratification) |
| Priyanka Rao, MD | ICU Director (raised the death reclassification) |
| Janet Mwangi, RN | Nursing Director / Sepsis Coordinator |
| Tom Becker, PharmD | Pharmacy Director (pump recall) |
| Sandra Pell | Quality Data Analyst (manual audit, 62%) |
| David Lin | Clinical Informatics (EHR dashboard, 84%) |

## Timeline

2024-06 protocol v1.0 · 2026-01-12 sentinel event · 01-26 charter · 02-09 prelim RCA ·
02-15 accreditor ack · 02-20/21 compliance audits · 02-24 pilot start · 02-25 M&M ·
02-27 final RCA · 03-05 pump field alert · 03-06 stewardship memo · 03-12 design workshop ·
03-20 escalation draft · 03-30 pump recall · 04-01 escalation adopted · 04-08 pilot interim ·
04-20 v2.0 approved · 05-01 v2.0 effective · 05-05 board report.

---

## 1. Contradictions (`contra_sets`)

| ID | Query | Side A | Side B | The conflict |
|---|---|---|---|---|
| **C1** | q02 | `02-subject/bundle-compliance-audit-manual` (62%) | `02-subject/ehr-sep1-dashboard` (84%) | Manual CMS all-or-none vs EHR "bundle initiated". Third value (~70%) in the Teams chat. Never reconciled. Both sides score-3 in qrels. |
| **C2** | q03 | `02-subject/rca-final` (2 deaths) | `07-documents/board-quality-report` (3 deaths) | Final RCA adjudicated 2 attributable; board slide still prints 3 (carried from preliminary; self-flagged). Also echoed by `rca-preliminary`, `qi-charter` (3). |
| **C3** | q08 | `email-internal-004` + `meeting-003` (Tran: universal 1h) | `stewardship-position-memo` + `sepsis-evidence-landscape` (Soto: shock-only) | Conflict over the *evidence basis* for a 1-hour mandate. Resolved by stratification, but the two evidentiary positions stand. |

## 2. Supersessions (`supersession_chains`)

| ID | Query | Binding (current) | Superseded | Note |
|---|---|---|---|---|
| **S1** | q01 | `07-documents/protocol-v2-sepsis-response` | `07-documents/protocol-v1-sepsis-response` | 3-hour uniform → stratified 1h-shock/3h-nonshock; v2 prints "supersedes v1.0". |
| **S2** | q04 | `02-subject/rca-final` | `02-subject/rca-preliminary` | 3 deaths → 2 (DNR/comfort-care reclassification). |
| **S3** | q05 | `07-documents/escalation-policy-memo-v2` | `07-documents/escalation-policy-memo-v1-draft` | Dedicated sepsis nurse (unfunded under FY26 freeze) → charge-nurse pager. |
| **S4** | q06 | `04-external-comms/email/email-ext-002-pump-recall` | `04-external-comms/email/email-ext-001-pump-field-alert` | "Not a recall, continue use" → voluntary recall; notice prints "supersedes FSN-2026-014". |

## 3. Temporal structure (`temporal_queries` + `lifecycle`)

- **CURRENT_STATE (11 queries):** q01, q02, q03, q06, q07, q08, q12, q13, q14, q16, q17. Each has `gold_current_docs` (the binding "now") and, where relevant, `gold_superseded_docs` (the obsolete version) — drives current-state accuracy and superseded-leakage.
- **HISTORICAL (4):** q04, q05, q09, q15. The earlier version is *wanted* (placed in `gold_historical_docs`, not penalized).
- **STABLE_KNOWLEDGE / stable docs (7 queries reference them):** `cms-sep1-measure-reference` (2025-10-01) and `nurse-staffing-policy` (2025-01-01) are durable references **older** than the fresh pilot/board docs — they test **freshness-overbias** (a recency-biased ranker that buries the older stable reference beneath newer initiative docs is penalized) and **stable-knowledge retention**.
- **Lifecycle** (all 32 docs annotated): CANONICAL 11 · ACTIVE 13 · SUPERSEDED 5 · PROVISIONAL 1 (`pilot-interim-report`) · ARCHIVED 2 (`chat`, `calendar`). (STALE/RETRACTED are exercised in the sibling corpora.)

## 4. Stance & abstention (`stance_gold`)

7 stance-evaluable queries: **SUPPORTS** q01, q09, q16 · **CONTRADICTS** q02, q03, q08 · **NEI** q07. 10 factoid (non-evaluable).

- **NEI / abstention (q07)** is the load-bearing abstention case: "did Sepsis Pathway 2.0 reduce mortality?" The corpus shows an *apparent* improvement but, in the same documents, explicitly disclaims it as underpowered, seasonally confounded, and not risk-adjusted. A correct system **abstains / says evidence insufficient**; asserting a reduction is a false commitment.

## 5. Traps (qrels score-0)

| Query | Trap doc | Why it's a trap |
|---|---|---|
| q07 | `07-documents/protocol-v2-sepsis-response` | The central intervention doc; topically magnetic but makes no mortality claim. |
| q10 | `02-subject/ehr-sep1-dashboard` | Topically "SEP-1" but a data export, not the *requirements*. |
| q12 | `07-documents/protocol-v1-sepsis-response` | The old protocol (no repeat-lactate); wrong answer to a current-protocol question. |

## 6. Human-validation checklist

1. **Clinical plausibility** — would a real QI committee plant these exact figures/decisions? Flag anything contrived.
2. **C2 judgment call** — the board report *self-corrects* the stale "3" in an inline note. Is that still a fair contradiction, or should it be downgraded to a documented stale-figure? (Owner decision.)
3. **q07 NEI** — confirm the corpus genuinely cannot support a mortality claim (we believe it cannot, by construction).
4. **qrels grades** — spot-check that score-3 docs each *fully* answer their query and score-2 docs *materially* support it.
5. **Lifecycle** — confirm CANONICAL vs ACTIVE assignments (e.g., the two co-equal compliance docs are both ACTIVE, deliberately).
6. **No leakage** — confirm no annotation was influenced by engine output (it was not).

## 7. Pre-registration wiring (NOT done here — Phase-4 step)

To make this corpus scorable by the full harness after sign-off:
- add `"org-hospital-stillwater"` to `experiments/scripts/eval_common.py::ALL_CORPORA`;
- add a `run_regression.py::OIDA_CORE_PROJECT_IDS` route + the matching `OIDA_CORE_KEY_<SLUG>` in `.env`;
- (optional) add a `CUTOFFS["org-hospital-stillwater"]` entry in `06_eval_temporal.py` for the per-cutoff temporal diagnostic (suggested: `["2026-02-15","2026-03-31","2026-05-01"]`);
- the gold annotation files are already in place under `experiments/annotations/` (gitignored).

Until then, individual layers can be run by passing the corpus id explicitly (e.g. `04_eval_adversarial.py org-hospital-stillwater`), except Layer-4 temporal, which filters to `ORG_CORPORA`.
