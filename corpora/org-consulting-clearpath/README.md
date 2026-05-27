# org-consulting-clearpath — Dataset Card

**Family:** organizational · **Domain:** Consulting / Operational process review
**Primary evaluation corpus** for the paper (Section 4.2).

## Scenario

ClearPath Solutions Inc. is a compliance-documentation and regulatory-management firm (78 employees, ~€12M revenue) headquartered in Florence, Italy. Rapid growth has exposed structural weaknesses: slow onboarding (~6 weeks), inconsistent client intake, audit-workflow bottlenecks, and fragmented knowledge sharing. An external consulting firm, Meridian Labs, is engaged for a 12-week process review to identify operational bottlenecks and deliver improvement recommendations.

The corpus follows the engagement lifecycle — kickoff, on-site observation, interim review, workshop design, and final presentation — across internal and client-facing channels.

## Why it is epistemically interesting

- **An evolving decision.** The onboarding target moves across the engagement (6 weeks current → 3-week client goal → 6.5–7-week interim observation → 4-week preview → 3–4-week final), so "the" decision is only correct relative to which document is binding.
- **A measured-but-unmeasured contradiction.** Audit cycle time is quoted as 3–4 days, 6–8 days, and 2–3 days by different team leads, and never objectively measured — feeding an open question that the redesign only partly resolves.
- **A client-load contradiction.** A consultant's caseload is recorded as 3 vs 5 clients across observation versions, contradicted by the liaison's records.
- **A load-bearing unverified figure.** An 18% turnover claim underpins two recommendations while never being verified.

## Contents

| | |
|---|---|
| Documents | 46 (40 Markdown, 3 JSON, 3 CSV) |
| Queries | 26 (16 medium, 7 hard, 3 easy) |
| Qrels | 107 graded judgments (0–3) |
| Knowledge objects | 32 |
| Edges | 30 |
| Raw size | 420 KB |

**Query epistemic types:** DECISION 4 · CONTRADICTION 4 · EVALUATION 4 · CONSTRAINT 3 · HYPOTHESIS 2 · QUESTION 2 · EVIDENCE 2 · OBSERVATION 2 · PLAN 2 · NARRATIVE 1.

**Knowledge-object classes:** DECISION 8 · CONSTRAINT 5 · OBSERVATION 5 · EVIDENCE 4 · EVALUATION 3 · QUESTION 3 · HYPOTHESIS 2 · PLAN 2.

**Edge types:** SUPPORTS 7 · BASED_ON 5 · CONTRADICTS 5 · IMPLEMENTS 3 · REFINES 2 · SUPERSEDES 2 · DERIVES_FROM 2 · ENABLES 2 · PRECEDES 1 · BLOCKS 1.

## Example queries

- **q02** (CONTRADICTION, hard) — audit cycle-time disagreement → top doc `02-subject/observation-003-audit-workflow` (3), `02-subject/bottleneck-analysis` (2).
- **q07** (DECISION) — timeline resequencing → `03-internal-comms/email/email-internal-005` (3, proposal), `03-internal-comms/email/email-internal-006` (3, approval).

## Provenance & format

The 8-category source tree lives in `raw/` (`01-scope` … `08-agenda`); `corpus.jsonl` is generated from it by `scripts/build_corpus.py`. See [`../../docs/format.md`](../../docs/format.md) for the schema and [`../../docs/relevance-guidelines.md`](../../docs/relevance-guidelines.md) for grading. This is a synthetic scenario; any resemblance to real companies is coincidental.
