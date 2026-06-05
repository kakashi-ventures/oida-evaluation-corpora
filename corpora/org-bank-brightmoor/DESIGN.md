# org-bank-brightmoor — Ground-Truth Design Dossier (DRAFT)

> ⚠️ **DRAFT FOR HUMAN VALIDATION.** This document records the *planted* epistemic
> ground truth for the corpus — the gold the paper's numbers will rest on. It is a
> human-review surface. The machine-readable gold lives (gitignored) under
> `experiments/annotations/{contra_sets,supersession_chains,lifecycle,stance_gold,temporal_queries}/org-bank-brightmoor.json`.
> **Before this corpus is sealed as the Phase-4 benchmark, a BSA/AML subject-matter
> expert + a reviewer should verify every relation below.** Because this file
> publishes the answer key, decide whether to keep it private/redacted before any
> public dataset release.

## Integrity statement (blindness)

The documents **and** these annotations were authored **without running the corpus
through OIDA or any retrieval system**, and without inspecting any engine output. No
relation was tuned to, or iterated against, a score. The corpus is therefore
*fresh/unseen* for Phase-4 purposes. It is deliberately **not** wired into the harness
(see "Pre-registration wiring" below) so it cannot be accidentally burned.

Synthetic scenario: any resemblance to real people, banks, regulators, or companies
is coincidental. BSA/AML, FinCEN, SARs, CTRs, MRA, transaction monitoring, and CDD
are used as realistic context only.

## Cast

| Person | Role |
|---|---|
| Dana Whitfield | Chief Compliance Officer & designated BSA Officer; remediation program lead |
| Marcus Hale | Chief Risk Officer; program sponsor |
| Priya Nair | Head of Financial Crimes / AML; owns the monitoring/backlog workstreams |
| Greg Olsen | Chief Information Officer; owns the core migration (Horizon → Unifi) |
| Lena Cho | Head of Retail Banking (opposes lower thresholds on customer-friction grounds) |
| Raj Patel | Internal Audit (skeptical of the vendor 40% claim) |
| Primary Federal Regulator | Issues the MRA; pushes risk-based thresholds; acknowledges remediation |
| Sentinel Analytics | Transaction-monitoring vendor; claims 40% false-positive reduction |
| Unifi Core | New core-platform vendor; cutover schedule |

## Timeline

2025-12 exam fieldwork (exit 12-18) · 2026-01-15 MRA letter + findings · 01-20 exam-context overview ·
01-23 weekly backlog snapshot (stale) · 01-26 remediation charter · 01-27 kickoff email + chat opens ·
01-28 program kickoff meeting · 01-30 Sentinel vendor 40% claim · 02-01 migration plan v1 (big-bang) ·
02-03 prelim triage memo (later retracted) · 02-06 alert-backlog report (~1,400) · 02-07 Sentinel dashboard export (~900) ·
02-10 model validation (~15%, not robust) · 02-12 Patel audit email · 02-16 IT post-cutover report (no data loss) ·
02-18 monitoring-data-gap memo (~3 weeks) · 02-20 Olsen↔Nair data-gap email · 02-24 threshold memo v1 ($10k) ·
02-25 Unifi schedule email · 03-02 regulator follow-up ($10k inadequate) · 03-05 Nair threshold-change email ·
03-06 threshold debate · 03-10 migration risk review · 03-12 Olsen migration-change email · 03-14 migration plan v2 (phased) ·
03-18 Hale governance-change email · 03-19 revised governance memo (PMO) · 03-20 steering (binding) · 03-22 threshold memo v2 ($5k) ·
04-30 remediation status report · 05-06 regulator validation acknowledgment.

---

## 1. Contradictions (`contra_sets`)

| ID | Query | Side A | Side B | The conflict |
|---|---|---|---|---|
| **C1** | q02 | `02-subject/alert-backlog-report-compliance` (~1,400) | `02-subject/sentinel-dashboard-export` (~900) | Inclusive backlog (counts auto-closed alerts as uninvestigated) vs platform "open alerts" (live analyst queue only, excludes auto-closed). Never reconciled; both score-3. Echoed in the Teams chat ("which number do we use?") and disclosed in the status report. The stale ~760 weekly snapshot is **not** a side. |
| **C2** | q03 | `07-documents/it-migration-report` (no data loss) | `02-subject/monitoring-data-gap-memo` (~3-week gap) | IT: core-ledger reconciliation clean, no data loss. Compliance: monitoring feed incomplete for ~3 weeks. Reconcilable in principle (different controls) — both docs carve out the ledger-vs-monitoring distinction — but the headline answers conflict. The Olsen↔Nair email (`email-internal-005`) is the dispute in motion. **q03 is a contradiction for the RETRIEVAL layer only** (surface both, so a reader is not misled by IT's headline); its **stance gold is SUPPORTS** — the corpus establishes a monitoring gap DID occur. See §4 and §6. |
| **C3** | q12 | `04-external-comms/email/email-ext-003-sentinel-vendor-claim` (40%) | `02-subject/model-validation-report` (~15%, not robust) | Vendor marketing 40% vs independent on-Bank-data validation ~15% (not statistically robust). Direct conflict over a measured claim. Patel's audit email corroborates the validation side. **The same doc pair powers q04, but on a different axis (see §4).** |

## 2. Supersessions (`supersession_chains`)

| ID | Query | Binding (current) | Superseded | Note |
|---|---|---|---|---|
| **S1** | q01 | `07-documents/threshold-memo-v2-5k` | `07-documents/threshold-memo-v1-10k` | $10,000 fixed → $5,000 risk-based; v2 prints "supersedes Threshold Policy v1." Driven by the regulator follow-up; confirmed at steering. |
| **S2** | q05 | `07-documents/migration-plan-phased` | `07-documents/migration-plan-bigbang` | Big-bang single-weekend cutover → phased cutover with per-phase monitoring-feed validation; v2 prints "supersedes Migration Plan v1." Driven by the Jan cutover gap; decided at the risk review. |
| **S3** | q06 | `07-documents/governance-memo-revised-pmo` | `01-scope/remediation-charter` | AML-team-owned program (charter §5) → dedicated remediation PMO under the CCO; the PMO memo prints "supersedes the charter's governance section." **Partial supersession** — only the charter's governance section is superseded; the charter as a whole stays ACTIVE. See §3 lifecycle note and §6. |

## 3. Temporal structure (`temporal_queries` + `lifecycle`)

- **CURRENT_STATE (13 queries):** q01, q02, q03, q04, q05, q06, q07, q08, q12, q13, q15, q16, q17. Each has `gold_current_docs` (the binding "now") and, where relevant, `gold_superseded_docs` (the obsolete version) — drives current-state accuracy and superseded-leakage.
- **HISTORICAL (2):** q11 (why the threshold was lowered — the rationale/evolution is wanted) and q14 (the prelim triage claim and its correction — the retracted memo is wanted as the "before").
- **STABLE_KNOWLEDGE (2 by intent):** q09 (`bsa-aml-regulation-reference`, 2025-10-01) and q10 (`risk-appetite-statement`, 2025-01-01). A third query (q02) carries a stable background ref. The two stable docs are **older** than the fresh 2026 remediation churn — they test **freshness-overbias** (a recency-biased ranker that buries the older durable reference beneath newer initiative docs is penalized) and **stable-knowledge retention**.
- **Lifecycle** (all 36 docs annotated): CANONICAL 14 · ACTIVE 16 · SUPERSEDED 2 · RETRACTED 1 (`backlog-triage-prelim`) · STALE 1 (`backlog-snapshot-weekly`) · ARCHIVED 2 (`remediation-teams` chat, `calendar-events`). (PROVISIONAL is not used here; it is exercised in the sibling hospital corpus.)
- **OBSOLETE set** (={SUPERSEDED, RETRACTED, ARCHIVED, STALE}): the two superseded version-1 documents, the retracted prelim memo, the stale weekly snapshot, and the two archived logs.

### Lifecycle note — the partially-superseded charter (S3)

`01-scope/remediation-charter` is lifecycle **ACTIVE** with `superseded_by = null`, even though its governance section is superseded by the PMO memo. Rationale: only §5 (program ownership) is superseded; the charter's objectives/scope/workstreams remain in force, so the document as a whole is not obsolete. The supersession is captured (a) in `supersession_chains` (q06, binding=PMO memo, superseded=[charter]) and (b) in the PMO memo's printed "supersedes the charter's governance section" language. For the **temporal** axis of q06, the charter is placed in `gold_superseded_docs` because the specific fact the query asks about (program ownership) *is* the superseded part. This is an intentional, documented asymmetry between the lifecycle state (whole-doc) and the temporal gold (fact-specific).

## 4. Stance & abstention (`stance_gold`)

6 stance-evaluable queries: **SUPPORTS** q01, q03, q08 · **CONTRADICTS** q02, q12 · **NEI** q04. 11 factoid (non-evaluable).

- **NEI / abstention (q04)** is the load-bearing abstention case: "what false-positive reduction does the Sentinel model achieve on Brightmoor's data?" The vendor claims 40%; the Bank's **independent validation found only ~15% on its own data, and not statistically robust** — explicitly cannot be distinguished from no effect. So no reliable figure can be given (the true reduction is somewhere between zero and ~15%, and definitely not the advertised 40%). A correct system **abstains / says the evidence is insufficient to give a figure**; asserting "40%" (or treating ~15% as reliable) is a false commitment — and asserting 40% would mean swallowing the vendor's marketing doc, the trap here.
- **The q04 / q12 split is deliberate.** q12 asks whether *conflicting evidence exists* about the model's FP performance → **CONTRADICTS** (both the vendor doc and the validation are relevant, both score-3). q04 asks the *substantive* question → **NEI**, and the vendor doc becomes a **score-0 trap / should-not-retrieve**. Same C3 doc pair, two epistemic axes. Validators should confirm this is coherent and not a labeling slip.
- **q03 is similarly dual-layered.** It is a contradiction for the adversarial RETRIEVAL layer (surface BOTH the IT "no data loss" headline and the Compliance gap memo) but its STANCE gold is **SUPPORTS** — the corpus establishes a monitoring gap DID occur, and a system that answers "no loss" from IT's scope-limited headline is wrong. Two independent layers, intentionally different.

## 5. Traps (qrels score-0)

| Query | Trap doc | Why it's a trap |
|---|---|---|
| q04 | `04-external-comms/email/email-ext-003-sentinel-vendor-claim` | The vendor's 40% marketing claim — topically magnetic for "does it reduce FPs 40%?" but it is unsubstantiated on Bank data; answering "40%" from it is a confabulation. (It is a *wanted* contra side on q12.) |
| q09 | `02-subject/sentinel-dashboard-export` | Topically about "alerts," but it is a compliance data export, not the BSA/AML *requirements* the query asks for. |
| q15 | `02-subject/backlog-triage-prelim` | The **retracted** prelim figure — surfacing it as the current authoritative backlog is retraction-leakage. (It is a *wanted* historical doc on q14.) |
| q15 | `02-subject/backlog-snapshot-weekly` | The **stale** ~760 weekly snapshot — surfacing it as the current figure is a staleness failure. |

Two deliberate "same doc, opposite role" splits — q04/q12 (vendor doc) and q14/q15 (prelim memo) — are the corpus's sharpest tests of epistemic (not topical) retrieval.

## 6. Human-validation checklist

1. **Domain plausibility** — would a real bank BSA/AML remediation plant these exact figures/decisions ($10k→$5k risk-based; ~1,400 vs ~900 backlog; ~3-week monitoring gap; 40% vs ~15%; big-bang→phased; AML-line→PMO)? Flag anything contrived to a SME.
2. **C2 / q03** — IT "no core data loss" vs Compliance "~3-week monitoring gap" are *true of different controls* (ledger vs monitoring feed). q03 is annotated as a contradiction FOR RETRIEVAL (surface both, so a reader is not misled by IT's reassuring headline) but its STANCE gold is **SUPPORTS** (the corpus establishes a monitoring gap occurred). Confirm this two-layer treatment is fair, or decide to downgrade the retrieval-layer contradiction to a scope-difference. (Owner decision.)
3. **q04 NEI** — confirm the corpus genuinely cannot give a reliable FP-reduction figure (the only on-Bank-data evidence is ~15%, not statistically robust, cannot be distinguished from no effect; 40% is unvalidated vendor marketing). Confirm the q04/q12 split (NEI vs CONTRADICTS over the same pair) is coherent.
4. **S3 partial supersession** — confirm the charter is correctly ACTIVE (whole-doc) while the temporal gold for q06 treats its ownership fact as superseded. Confirm this asymmetry is acceptable.
5. **q14/q15 split** — confirm the retracted prelim memo is rightly *wanted* in q14 (historical) and a *trap* in q15 (current). Likewise confirm the stale snapshot trap in q15.
6. **qrels grades** — spot-check that score-3 docs each *fully* answer their query and score-2 docs *materially* support it; confirm both sides of each contradiction score 3.
7. **Lifecycle** — confirm CANONICAL vs ACTIVE assignments (e.g., the two co-equal backlog measurements are both current — the Compliance report is ACTIVE, the dashboard export ACTIVE — and only `backlog-snapshot-weekly` is STALE).
8. **No leakage** — confirm no annotation was influenced by engine output (it was not).

## 7. Pre-registration wiring (NOT done here — Phase-4 step)

To make this corpus scorable by the full harness after sign-off:
- add `"org-bank-brightmoor"` to `experiments/scripts/eval_common.py::ALL_CORPORA`;
- add an `org-bank-brightmoor` route to `run_regression`'s `OIDA_CORE_PROJECT_IDS` + the matching `OIDA_CORE_KEY_<SLUG>` in `.env`;
- (optional) add a `CUTOFFS["org-bank-brightmoor"]` entry for the per-cutoff temporal diagnostic (suggested: `["2026-02-16","2026-03-20","2026-05-06"]` — pre-decision baseline, post-steering binding state, post-regulator-ack);
- the gold annotation files are already in place under `experiments/annotations/` (gitignored).

Until then, individual layers can be run by passing the corpus id explicitly (e.g. `04_eval_adversarial.py org-bank-brightmoor`), subject to whatever corpus-set filter each layer applies.
