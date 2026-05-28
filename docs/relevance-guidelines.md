# Relevance Guidelines — how qrels grades were assigned

The qrels in this benchmark use **graded relevance on a 0–3 scale**. The grades
are *epistemic*, not merely topical: a document can be entirely on-topic and
still score low if it does not bear on the actual question — the binding
decision, the contradiction, the open question.

## The scale

| Score | Label | Meaning |
|---|---|---|
| **3** | Directly answers / binding source | The document *is* the answer: the binding decision, the document that states the contradiction, the source that resolves (or definitively raises) the question. A complete answer can be written from the score-3 documents alone. |
| **2** | Strong support | Materially advances the answer — corroborating evidence, an earlier version of an evolving decision, one side of a contradiction, the rationale behind a choice. Needed for a *complete* and *well-grounded* answer. |
| **1** | Weak / contextual | Background that a thorough reader would want but that does not by itself move the answer — scene-setting, tangential mentions, scheduling context. |
| **0** | Explicitly non-relevant | A plausible-but-wrong document that a naive topical retriever would surface. Judged non-relevant *on purpose* to penalize topical-only matching. Only a few are recorded per corpus, where the trap is instructive. |

Unjudged documents are treated as non-relevant by standard BEIR scoring (nDCG,
MAP, Recall). The explicit `0` rows are a deliberate signal, not exhaustive.

## Principles applied

1. **Epistemic primacy over topicality.** When a query asks for a *decision*,
   the document holding the binding decision scores 3 even if shorter or less
   keyword-rich than discursive documents that merely discuss the topic.
2. **Evolving decisions are graded by recency of authority.** For a decision
   that changes over time, the *superseding* (final/binding) source scores 3
   and the earlier superseded versions score 2 — they are part of the answer
   (the evolution) but not the binding state.
3. **Both sides of a contradiction score high.** When a query targets a
   conflict, every conflicting source must be retrieved, so each side scores 3
   (or 2 for the weaker side).
4. **Questions reward the raiser and the resolver.** When a query asks an open
   question, the document that frames it and any that resolve it both score 3;
   documents that merely touch the area score 1–2.
5. **Refuted hypotheses: supporting and weakening sources both count.** For a
   false-lead query, both the sources that support the hypothesis and those
   that weaken it are relevant, because the answer is the *adjudication*.
6. **Traps get explicit zeros.** Where a document is strongly on-topic but
   misleading for the query, it is recorded with score 0.

## Per-family notes

- **Organizational corpora (`org-*`).** Grades were authored by reading the
  source documents and tracing each query to the documents that establish,
  support, or contradict the state in question.
- **Investigative corpora (`inv-*`).** Grades are derived deterministically from
  the corpus's native ground truth: a query's `required_sources` → 3,
  `optional_sources` → 2; timeline queries map gold events to their supporting
  sources (must-include events → 3, others → 2); contradiction queries take
  every source involved in the gold contradiction → 3; noise-rejection takes
  the gold noise sources → 3. The mapping is documented in each dataset card.
