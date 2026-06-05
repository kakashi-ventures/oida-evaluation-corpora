# org-bank-brightmoor — Dataset Card

**Family:** organizational · **Domain:** Financial services / Bank AML-BSA compliance remediation
**Status:** ⚠️ **DRAFT — Phase-4 candidate, awaiting human sign-off.** Authored blind to the engine (see `DESIGN.md`). Not yet wired into the harness.

## Scenario

Brightmoor Bank, N.A. (a ≈$14bn-asset US regional commercial bank) receives a BSA/AML examination finding — a **Matter Requiring Attention (MRA)** — from its primary federal regulator after December 2025 fieldwork, and runs a remediation program ("Project Cornerstone"). The remediation is complicated by a simultaneous **core-banking platform migration** (legacy "Horizon" core → new "Unifi" core) on which the transaction-monitoring data feed depends. The corpus follows the program end to end: the exam finding, the remediation charter, the alert backlog, transaction-monitoring threshold decisions, the migration plan and its mid-course change, an independent model validation, internal disputes between Risk/Compliance and IT and Retail, the regulator interaction, and the governance change — across internal and external channels.

## Why it is challenging

- **An evolving binding threshold.** The monitoring threshold moves from a **$10,000 fixed** rule (Threshold Policy v1) to a **$5,000 risk-based** rule (Threshold Policy v2) after regulator pushback. "The threshold" is only correct relative to which version is in force.
- **A measured, never-reconciled count conflict.** The alert backlog is reported as **~1,400** (Compliance, counting auto-closed alerts as uninvestigated) and **~900** (the platform dashboard, queue-only) — two numbers measuring different populations, surfaced but not reconciled.
- **A scope-vs-substance data dispute.** IT reports the core migration reconciled **clean, no data loss**; Compliance reports a **~3-week transaction-monitoring data gap** during the cutover. Both are arguably true of different controls (core ledger vs monitoring feed), and the disagreement is live and unresolved in-corpus.
- **A load-bearing unverified vendor claim.** The monitoring vendor advertises a **40% false-positive reduction**; the Bank's independent validation finds only **~15%, not statistically robust**, on its own data — an abstention/NEI target where a correct system must decline to confirm the 40%.
- **A retracted figure.** A preliminary triage memo's claim that "all ~1,400 alerts are SAR-eligible" is **retracted** and corrected; it is wanted as history for one query and a trap for another (a deliberate split).
- **A stale snapshot.** A weekly backlog snapshot (~760, queue-only) is point-in-time and **stale**; surfacing it as the current figure is a staleness failure.

## Contents

| | |
|---|---|
| Documents | 36 (33 Markdown, 2 JSON, 1 CSV) |
| Queries | 17 (3 easy, 10 medium, 4 hard) |
| Qrels | 61 graded judgments (0–3) |
| Planted relations | 3 contradictions · 3 supersessions · 1 retraction · 4 trap (qrels-0) rows · 3 stable-knowledge queries · 1 NEI/abstention |

The two JSON sources are the program Teams chat and the milestone calendar; the CSV is the Sentinel dashboard export.

## Example queries

- **q02** (hard) — alert-backlog count conflict → `02-subject/alert-backlog-report-compliance` (3, ~1,400) and `02-subject/sentinel-dashboard-export` (3, ~900); both sides must be retrieved.
- **q04** (hard) — "does Sentinel actually cut false positives 40%?" → the corpus does **not** confirm it (gold stance NEI); `02-subject/model-validation-report` (3, ~15%-not-robust) answers, and `04-external-comms/email/email-ext-003-sentinel-vendor-claim` (the 40% marketing claim) is a score-0 trap.
- **q01** (medium) — current vs. superseded monitoring threshold → `07-documents/threshold-memo-v2-5k` (3, binding $5k risk-based), `07-documents/threshold-memo-v1-10k` (2, superseded $10k fixed).
- **q14 / q15** (medium) — a deliberate split on the retracted prelim triage memo: it is **wanted** as history in q14 ("what did the prelim claim, and was it upheld?") and a **score-0 trap** in q15 ("what is the *current* authoritative figure?").

## Provenance & format

The 8-category source tree lives in `raw/` (`01-scope` … `08-agenda`); `corpus.jsonl` is generated from it by `scripts/build_corpus.py`. The gold for the adversarial/stance/temporal layers lives in the gitignored `experiments/annotations/` tree; `DESIGN.md` in this directory documents that gold for review. See [`../../docs/format.md`](../../docs/format.md) and [`../../docs/relevance-guidelines.md`](../../docs/relevance-guidelines.md). This is a synthetic scenario; **any resemblance to real people, banks, regulators, or companies is coincidental.** Named external standards and concepts (BSA/AML, FinCEN, SARs, CTRs, MRA, transaction monitoring, CDD) are used as realistic context only; no real institution or examination is depicted.
