# org-hospital-stillwater — Dataset Card

**Family:** organizational · **Domain:** Healthcare delivery / Hospital clinical quality improvement
**Status:** ⚠️ **DRAFT — Phase-4 candidate, awaiting human sign-off.** Authored blind to the engine (see `DESIGN.md`). Not yet wired into the harness.

## Scenario

Stillwater Regional Medical Center (a 412-bed community teaching hospital in Calhoun County) launches **Sepsis Pathway 2.0**, a cross-functional quality-improvement initiative, after a January 2026 sentinel event — an adult patient who died of septic shock in the Emergency Department following delays in recognition and antibiotics. The corpus follows the initiative end to end: charter, root-cause analysis, protocol redesign (v1 → v2), a unit pilot, conflicting compliance and mortality data, clinician deliberations over antibiotic timing, an infusion-pump safety recall that intersects the antibiotic-timing goal, and board sign-off — across internal and external channels.

## Why it is challenging

- **An evolving clinical standard.** The binding antibiotic-timing rule moves from a uniform 3-hour target (Protocol v1.0, 2024) to a stratified target (Protocol v2.0, 2026: 1 hour for septic shock, 3 hours for sepsis without shock). "The protocol" is only correct relative to which version is in force.
- **A measured-but-irreconcilable contradiction.** SEP-1 bundle compliance is reported as **62%** (manual CMS abstraction), **84%** (EHR "bundle initiated" flag), and **~70%** (nursing self-report) — three numbers measuring different things, never reconciled.
- **A stale figure that outlives its correction.** The RCA's death count is adjudicated down from **3 (preliminary)** to **2 (final)**, but the board summary still prints "3."
- **A load-bearing unverified claim.** A pilot mortality improvement is visible but explicitly underpowered and confounded; the corpus refuses to claim a mortality effect (an abstention/NEI target).
- **An evidence-basis stance split.** ED advocacy for a universal 1-hour mandate vs. stewardship's evidence that the benefit is shock-specific and a blanket mandate causes harm.
- **A device lifecycle.** An infusion-pump field alert is superseded by a voluntary recall, intersecting the antibiotic-timing goal.

## Contents

| | |
|---|---|
| Documents | 32 (29 Markdown, 2 JSON, 1 CSV) |
| Queries | 17 (3 easy, 10 medium, 4 hard) |
| Qrels | 75 graded judgments (0–3) |
| Planted relations | 3 contradictions · 4 supersessions · 3 traps · 7 stable-knowledge queries · 1 NEI/abstention |

## Example queries

- **q02** (hard) — SEP-1 compliance conflict → `02-subject/bundle-compliance-audit-manual` (3), `02-subject/ehr-sep1-dashboard` (3); both sides must be retrieved.
- **q07** (hard) — "did it reduce mortality?" → the corpus does **not** settle this (gold stance NEI); `02-subject/pilot-interim-report` (3) and the committee/board records all decline the claim. `07-documents/protocol-v2-sepsis-response` is a score-0 trap.
- **q01** (medium) — current vs. superseded antibiotic standard → `07-documents/protocol-v2-sepsis-response` (3, binding), `07-documents/protocol-v1-sepsis-response` (2, superseded).

## Provenance & format

The 8-category source tree lives in `raw/` (`01-scope` … `08-agenda`); `corpus.jsonl` is generated from it by `scripts/build_corpus.py`. The gold for the adversarial/stance/temporal layers lives in the gitignored `experiments/annotations/` tree; `DESIGN.md` in this directory documents that gold for review. See [`../../docs/format.md`](../../docs/format.md) and [`../../docs/relevance-guidelines.md`](../../docs/relevance-guidelines.md). This is a synthetic scenario; any resemblance to real people, hospitals, or companies is coincidental. Named external standards (CMS SEP-1, accreditation expectations) are used as realistic context only.
