# OIDA Benchmark Corpora

**A Resource for Evaluating Adversarial Retrieval in Organizational Knowledge Work**

Companion data for the paper:

> **Retrieval Is Not Enough: Why Organizational AI Needs Epistemic Infrastructure**
>
> Federico Bottino, Carlo Ferrero, Nicholas Dosio, Pierfrancesco Beneventano

## Abstract

Most retrieval benchmarks reward *topical* relevance: did the system find documents about the right subject? Organizational knowledge work needs more. It needs the ability to distinguish a binding decision from a discarded hypothesis, surface the contradiction between two teams' assessments, and recognize which questions are still open. The OIDA Benchmark Corpora is a heterogeneous, BEIR-style retrieval benchmark built to measure exactly this. Five corpora — three synthetic-but-realistic organizational knowledge bases and two investigative multi-source reasoning cases — share one uniform `corpus / queries / qrels` layout, with queries deliberately constructed around contradictions, evolving decisions, open questions, and topically-similar traps.

## Datasets

Following [BEIR](https://github.com/beir-cellar/beir), every dataset is a sibling folder under `corpora/` with an identical shape. The family is encoded in the slug prefix (`org-*`, `inv-*`).

| Dataset | Family | Domain | Docs | Queries | Qrels |
|---|---|---|---|---|---|
| [`org-consulting-clearpath`](corpora/org-consulting-clearpath) | organizational | Consulting / Operations | 46 | 26 | 107 |
| [`org-iot-fireglass`](corpora/org-iot-fireglass) | organizational | IoT / Product development | 47 | 20 | 82 |
| [`org-vc-vertexminds`](corpora/org-vc-vertexminds) | organizational | Venture capital | 77 | 20 | 89 |
| [`inv-mystery-redhood`](corpora/inv-mystery-redhood) | investigative | Multi-source reasoning | 30 | 8 | 51 |
| [`inv-ashford-mystery`](corpora/inv-ashford-mystery) | investigative | Cross-incident reasoning | 30 | 6 | 13 |

`org-consulting-clearpath` ("ClearPath") is the primary corpus referenced in the paper (Section 4.2).

## Format

Every corpus is identical in shape — the full contract is in [`docs/format.md`](docs/format.md):

```
corpora/<dataset-id>/
├── corpus.jsonl              # documents to retrieve over          (BEIR core)
├── queries.jsonl             # evaluation queries                  (BEIR core)
├── qrels/test.tsv            # graded relevance judgments (0–3)    (BEIR core)
├── raw/                      # untouched source documents (provenance)
└── README.md                 # dataset card
```

`corpus.jsonl` is BEIR-compatible: `{"_id", "title", "text", "metadata"}`, one JSON object per line. It is derived from the untouched sources in `raw/`, which remain the source of truth. No gold labels live in `corpus.jsonl` — the relevance judgments are kept separately in `qrels/`.

## Loading

The files are byte-compatible with BEIR, so they load directly — no special tooling required:

```python
from beir.datasets.data_loader import GenericDataLoader
corpus, queries, qrels = GenericDataLoader(
    corpus_file="corpora/org-consulting-clearpath/corpus.jsonl",
    query_file="corpora/org-consulting-clearpath/queries.jsonl",
    qrels_file="corpora/org-consulting-clearpath/qrels/test.tsv",
).load_custom()
```

`corpus.jsonl` and `queries.jsonl` are JSON-lines; `qrels/test.tsv` is a tab-separated `query-id  corpus-id  score` table with a header — all readable with the Python standard library alone.

## What makes it adversarial

A topical retriever asks "is this document about bottlenecks?" This benchmark forces harder questions:

- **Evolving decisions** — the onboarding target moves 6wk → 3wk → 7wk → 4wk → 3–4wk across the engagement; which document holds the *binding* version?
- **Contradictions** — two IC members disagree on NovaTech's investment amount (€320K vs €200K); a field-test report says one thing internally and another to the client.
- **Open questions** — an audit-workflow bottleneck whose true cause is never measured; a vendor's firmware docs that never arrive.
- **Refuted hypotheses** — a rumor-driven suspect with motive but no evidence.

Relevance grades were assigned with the rubric in [`docs/relevance-guidelines.md`](docs/relevance-guidelines.md): graded 0–3, with *epistemic* primacy over topicality — a binding decision scores 3 even if it is shorter and less keyword-rich than the discursive documents that merely discuss the topic.

## Repository layout

```
README.md                     # this file
LICENSE                       # CC BY 4.0
CITATION.cff
CHANGELOG.md                  # dataset versioning
docs/
  format.md                   # the corpus/queries/qrels contract
  relevance-guidelines.md     # how qrels grades were assigned
corpora/                      # the five datasets (see table above)
```

## Citation

```bibtex
@unpublished{bottino2026retrieval,
  title={Retrieval Is Not Enough: Why Organizational AI Needs Epistemic Infrastructure},
  author={Bottino, Federico and Ferrero, Carlo and Dosio, Nicholas and Beneventano, Pierfrancesco},
  year={2026},
  note={Preprint in preparation}
}
```

## License

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — share and adapt with attribution. See [`LICENSE`](LICENSE).

All organizational corpora are synthetic; any resemblance to real companies is coincidental. The investigative corpora (`inv-mystery-redhood`, `inv-ashford-mystery`) are fictional scenarios.
