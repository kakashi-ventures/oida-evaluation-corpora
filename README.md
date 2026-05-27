# OIDA Benchmark Corpora

**A Resource for Evaluating Epistemic Retrieval in Organizations**

Companion data for the paper:

> **Retrieval Is Not Enough: Why Organizational AI Needs Epistemic Infrastructure**
>
> Federico Bottino, Carlo Ferrero, Nicholas Dosio, Pierfrancesco Beneventano

## Abstract

Most retrieval benchmarks reward *topical* relevance: did the system find documents about the right subject? Organizational knowledge work needs more. It needs **epistemic** retrieval — distinguishing a binding decision from a discarded hypothesis, surfacing the contradiction between two teams' assessments, and recognizing which questions are still open. The OIDA Benchmark Corpora is a heterogeneous, BEIR-style retrieval benchmark built to measure exactly this. Four corpora — three synthetic-but-realistic organizational knowledge bases and one investigative multi-source reasoning case — share one uniform `corpus / queries / qrels` layout, plus an OIDA-specific **epistemic gold layer** (typed knowledge objects and signed edges) that turns each dataset from a document dump into a test of epistemic structure.

## Datasets

Following [BEIR](https://github.com/beir-cellar/beir), every dataset is a sibling folder under `corpora/` with an identical shape. The family is encoded in the slug prefix (`org-*`, `inv-*`).

| Dataset | Family | Domain | Docs | Queries | Qrels | Raw size |
|---|---|---|---|---|---|---|
| [`org-consulting-clearpath`](corpora/org-consulting-clearpath) | organizational | Consulting / Operations | 46 | 26 | 107 | 420 KB |
| [`org-iot-fireglass`](corpora/org-iot-fireglass) | organizational | IoT / Product development | 47 | 20 | 82 | 672 KB |
| [`org-vc-vertexminds`](corpora/org-vc-vertexminds) | organizational | Venture capital | 77 | 20 | 89 | 572 KB |
| [`inv-mystery-redhood`](corpora/inv-mystery-redhood) | investigative | Multi-source reasoning | 30 | 8 | 51 | 120 KB |

`org-consulting-clearpath` ("ClearPath") is the primary corpus referenced in the paper (Section 4.2).

## Format

Every corpus is identical in shape — the full contract is in [`docs/format.md`](docs/format.md):

```
corpora/<dataset-id>/
├── corpus.jsonl              # documents to retrieve over          (BEIR core)
├── queries.jsonl             # evaluation queries                  (BEIR core)
├── qrels/test.tsv            # graded relevance judgments (0–3)     (BEIR core)
├── epistemic/                # OIDA epistemic gold layer
│   ├── knowledge-objects.jsonl
│   └── edges.jsonl
├── raw/                      # untouched source documents (provenance)
└── README.md                 # dataset card
```

`corpus.jsonl` is BEIR-compatible: `{"_id", "title", "text", "metadata"}`, one JSON object per line. It is **derived** from `raw/` by `scripts/build_corpus.py`, so the pipeline is reproducible and the source of truth is preserved. No gold or epistemic labels live in `corpus.jsonl` — retrieval cannot cheat.

## Quick start

The scripts use only the Python standard library — no install needed:

```bash
git clone https://github.com/kakashi-ventures/oida-benchmark-corpora.git
cd oida-benchmark-corpora

# Inspect any corpus (BEIR-shaped dicts: corpus / queries / qrels)
python scripts/load_example.py corpora/org-consulting-clearpath

# Rebuild corpus.jsonl from raw sources (deterministic)
python scripts/build_corpus.py

# Validate schema + qrels/epistemic integrity (CI gate)
python scripts/validate.py
```

Loading is BEIR-native (`pip install beir` for the helper below, optional):

```python
from beir.datasets.data_loader import GenericDataLoader
corpus, queries, qrels = GenericDataLoader(
    corpus_file="corpora/org-consulting-clearpath/corpus.jsonl",
    query_file="corpora/org-consulting-clearpath/queries.jsonl",
    qrels_file="corpora/org-consulting-clearpath/qrels/test.tsv",
).load_custom()
```

## What makes it *epistemic*

A topical retriever asks "is this document about bottlenecks?" An epistemic retriever must answer harder questions:

- **Evolving decisions** — the onboarding target moves 6wk → 3wk → 7wk → 4wk → 3–4wk across the engagement; which document holds the *binding* version?
- **Contradictions** — two IC members disagree on NovaTech's investment amount (€320K vs €200K); a field-test report says one thing internally and another to the client.
- **Open questions** — an audit-workflow bottleneck whose true cause is never measured; a vendor's firmware docs that never arrive.
- **Refuted hypotheses** — a rumor-driven suspect with motive but no evidence.

Each `queries.jsonl` query is tagged with the `epistemic_type` it probes (`DECISION`, `CONTRADICTION`, `QUESTION`, `HYPOTHESIS`, …). The `epistemic/` layer ships the gold answer: typed **knowledge objects** and signed **edges** (`SUPPORTS`, `CONTRADICTS`, `SUPERSEDES`, `IMPLEMENTS`, …) following the 9-class / 10-edge taxonomy in [`docs/epistemic-taxonomy.md`](docs/epistemic-taxonomy.md). Relevance grades were assigned with the rubric in [`docs/relevance-guidelines.md`](docs/relevance-guidelines.md).

## Repository layout

```
README.md                     # this file
LICENSE                       # CC BY 4.0
CITATION.cff
CHANGELOG.md                  # dataset versioning (v1.0.0 = first public release)
docs/
  format.md                   # the corpus/queries/qrels/epistemic contract
  epistemic-taxonomy.md       # 9 knowledge-object classes + 10 edge types
  relevance-guidelines.md     # how qrels grades were assigned
corpora/                      # the four datasets (see table above)
scripts/
  build_corpus.py             # raw → corpus.jsonl (deterministic normalizer)
  validate.py                 # schema + qrels/epistemic integrity checks
  load_example.py             # minimal BEIR-compatible loader
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

All organizational corpora are synthetic; any resemblance to real companies is coincidental. The investigative corpus (`inv-mystery-redhood`) is a fictional scenario.
