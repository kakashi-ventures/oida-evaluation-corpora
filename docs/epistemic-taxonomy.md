# Epistemic Class Taxonomy

The epistemic gold layer (`corpora/<id>/epistemic/`) classifies every Knowledge
Object into one of nine epistemic classes and connects them with typed, signed
edges. This page is the reference vocabulary for those `class` and `type` values.

## The Nine Classes

| Class | Epistemic Role |
|---|---|
| DECISION | Binding choice — valid until explicitly superseded |
| CONSTRAINT | Non-negotiable structural boundary |
| EVIDENCE | Verifiable supporting or refuting data |
| NARRATIVE | Persistent contextual anchor |
| PLAN | Structured intention with a time horizon |
| EVALUATION | Informed qualitative assessment |
| OBSERVATION | Weak signal not yet interpreted |
| HYPOTHESIS | Unverified testable claim |
| QUESTION | Open question requiring resolution |

Classes lie on an axis of **epistemic commitment strength**: from explicit
ignorance (QUESTION) through uninterpreted signals (OBSERVATION), provisionally
held claims (HYPOTHESIS, PLAN), evidentially supported assessments (EVIDENCE,
EVALUATION), persistent anchors (NARRATIVE), up to binding commitments
(DECISION, CONSTRAINT). The `confidence` field on each Knowledge Object reflects
how strongly its source asserts the claim.

## Edge Types

Relationships between Knowledge Objects carry signed coefficients. These are the
exact `type` / `coefficient` values used in `epistemic/edges.jsonl`:

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
| CONTRADICTS | -0.6 | A contradicts B (strongest negative relation) |

The CONTRADICTS coefficient of -0.6 (not -1.0) implements **epistemological
tolerance**: contradicted knowledge is suppressed, not erased, reflecting the
organizational reality that contradictions are often unresolved coexistences
rather than logical defeats.

The investigative corpus (`inv-mystery-redhood`) uses a richer, domain-specialized
vocabulary mapped onto these canonical classes and edge types; see that dataset's
card for the mapping table.
