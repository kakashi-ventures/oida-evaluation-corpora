# Epistemic Class Taxonomy

OIDA classifies every Knowledge Object into one of nine epistemic classes. Classification occurs at ingestion (LLM-assisted); all subsequent maintenance is deterministic.

## The Nine Classes

| Class | Seed K | Decay | Half-life | Epistemic Role |
|---|---|---|---|---|
| DECISION | 1.00 | None | Infinite | Binding choice — valid until explicitly superseded |
| CONSTRAINT | 0.90 | None | Infinite | Non-negotiable structural boundary |
| EVIDENCE | 0.80 | Exponential | ~365 days | Verifiable supporting or refuting data |
| NARRATIVE | 0.70 | None | Infinite | Persistent contextual anchor |
| PLAN | 0.65 | Exponential | ~69 days | Structured intention with time horizon |
| EVALUATION | 0.55 | Exponential | ~198 days | Informed qualitative assessment |
| OBSERVATION | 0.40 | Exponential | ~90 days | Weak signal not yet interpreted |
| HYPOTHESIS | 0.30 | Exponential | ~50 days | Unverified testable claim |
| QUESTION | 0.30 | Inverse | Urgency grows | Open question requiring resolution |

## Design Axes

Classes are determined by crossing two orthogonal axes:

### Axis 1: Epistemic Commitment Strength
From explicit ignorance (QUESTION) through uninterpreted signals (OBSERVATION), provisionally held claims (HYPOTHESIS, PLAN), evidentially supported assessments (EVIDENCE, EVALUATION), persistent anchors (NARRATIVE), up to binding commitments (DECISION, CONSTRAINT).

### Axis 2: Temporal Behavior Under Absence of Reinforcement
- **Non-decaying**: DECISION, CONSTRAINT, NARRATIVE — remain valid until explicitly superseded
- **Exponentially decaying**: EVIDENCE, PLAN, EVALUATION, OBSERVATION, HYPOTHESIS — lose weight if unreinforced
- **Inversely decaying**: QUESTION — gains urgency over time; unresolved uncertainty becomes more costly

## QUESTION as Modeled Ignorance

QUESTION is the only class with inverse decay. Unresolved questions become *more* urgent, not less. This operationalizes accumulated organizational decision risk: each day a QUESTION remains unresolved, the organization makes decisions in its shadow, accumulating risk.

When a QUESTION is resolved (typically by a DECISION linked via IMPLEMENTS), its urgency drops to zero.

## Edge Types

Relationships between Knowledge Objects carry signed coefficients:

| Type | Coefficient | Semantics |
|---|---|---|
| SUPPORTS | +1.0 | A provides evidence strengthening B |
| BASED_ON | +0.8 | A is the logical grounding of B |
| IMPLEMENTS | +0.7 | A operationally realizes B |
| SUPERSEDES | +0.6 | A replaces B (B is demoted, not deleted) |
| REFINES | +0.5 | A narrows B without contradiction |
| DERIVES_FROM | +0.5 | A follows logically from B |
| ENABLES | +0.4 | A is a necessary condition for B |
| PRECEDES | +0.3 | A temporally precedes B |
| BLOCKS | -0.4 | A actively prevents B |
| CONTRADICTS | -0.6 | A contradicts B (strongest negative gravity) |

The CONTRADICTS coefficient of -0.6 (not -1.0) implements **epistemological tolerance**: contradicted knowledge is suppressed, not erased, reflecting the organizational reality that contradictions are often unresolved coexistences rather than logical defeats.
