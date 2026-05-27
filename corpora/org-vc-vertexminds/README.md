# org-vc-vertexminds — Dataset Card

**Family:** organizational · **Domain:** Venture capital / Investment decision-making

## Scenario

Vertex Minds LLC is an early-stage VC fund in Milan, Italy, running its inaugural **Demo Day Alpha**. Five startups (NovaTech, GreenLoop, MindBridge, DataPulse, UrbanFlow) are selected from a pipeline of 30 to pitch to the investment committee. The corpus covers the full lifecycle: sourcing, screening, pitch day, IC deliberation, and final allocation. Investment parameters: €100K–400K checks, 5–12% equity, pre-seed to early seed, €600K total from Fund I.

It is the largest corpus (77 docs) and the temporally densest — daily calendar snapshots span the evaluation period.

## Why it is epistemically interesting

- **Decisions that evolve.** NovaTech: invite → pitch → INVEST → term sheet. UrbanFlow: ask negotiated €250K → €180K. MindBridge: PASS → CONDITIONAL.
- **Load-bearing contradictions across documents.**
  - NovaTech amount/instrument: term-sheet email says €320K SAFE / €2.2M cap, while the internal draft and IC memo say €200K / €2.3M.
  - Demo Day venue: the invite says Zurich; the pitch transcript says Palazzo delle Industrie, Milan.
  - DataPulse traction: screening summary says 28 customers (CAC 1.8× LTV); deliberation says only 2–4 customers and 50K claimed vs 38K verified MAU.
  - UrbanFlow milestone: deliberation says "second hub within 9 months"; term sheet says "100 active hubs in 3 cities by Month 9".
- **Open questions that block a decision.** NovaTech's ML-validation ceiling and an unfinished reference check stay open during deliberation.
- **Divergent evaluations.** IC members assess the same startup differently between screening scores and pitch-day impressions.

## Contents

| | |
|---|---|
| Documents | 77 (52 Markdown, 18 JSONL, 4 JSON, 3 CSV) |
| Queries | 20 (11 medium, 6 hard, 3 easy) |
| Qrels | 89 graded judgments (0–3) |
| Knowledge objects | 23 |
| Edges | 24 |
| Raw size | 572 KB |

**Query epistemic types:** CONTRADICTION 6 · DECISION 4 · QUESTION 2 · EVALUATION 2 · PLAN 2 · CONSTRAINT 1 · HYPOTHESIS 1 · NARRATIVE 1 · OBSERVATION 1.

**Knowledge-object classes:** DECISION 8 · EVIDENCE 4 · EVALUATION 3 · CONSTRAINT 2 · QUESTION 2 · OBSERVATION 2 · HYPOTHESIS 1 · PLAN 1.

**Edge types:** BASED_ON 5 · CONTRADICTS 4 · IMPLEMENTS 3 · SUPPORTS 3 · BLOCKS 3 · DERIVES_FROM 2 · SUPERSEDES 1 · ENABLES 1 · PRECEDES 1 · REFINES 1.

## Example queries

- **q06** (CONTRADICTION, hard) — NovaTech amount/instrument disagreement → `04-external-comms/email/founders/email-ext-009-termsheet-novatech` (3), `02-subject/term-sheet-draft-novatech` (3), `07-documents/ic-memo-final` (2).
- **q03** (DECISION) — why PASS on DataPulse despite liking the product → `05-meetings/meeting-007-ic-deliberation` (3), `07-documents/ic-memo-final` (3).

## Provenance & format

The 8-category source tree lives in `raw/`; `corpus.jsonl` is generated from it by `scripts/build_corpus.py`. See [`../../docs/format.md`](../../docs/format.md) and [`../../docs/relevance-guidelines.md`](../../docs/relevance-guidelines.md). This is a synthetic scenario; any resemblance to real companies is coincidental.
