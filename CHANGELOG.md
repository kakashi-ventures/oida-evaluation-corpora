# Changelog

Dataset versioning for the OIDA Benchmark Corpora. This tracks the benchmark
*contents*; versions follow [Semantic Versioning](https://semver.org/), where a
MAJOR bump signals a backward-incompatible change to ids, schema, or judgments.

## [2.1.0] — 2026-05-28

Additive release: optional temporal metadata for time-aware evaluation.

### Added
- `queries.jsonl[].metadata.query_time` — optional ISO-8601 field: the narrative
  time at which the query is asked. Documented in `docs/format.md`.
- `corpus.jsonl` documents carry `metadata.created` — the narrative event time of
  each document, in ISO-8601, when extractable from the source.

## [2.0.0] — 2026-05-28

The benchmark is a pure BEIR-compatible retrieval resource: each corpus is its
inputs (`corpus.jsonl`, `queries.jsonl`) plus graded relevance judgments
(`qrels/test.tsv`) and the untouched sources under `raw/`.

## [1.0.0] — 2026-05-27

First public release.

### Added
- Uniform, BEIR-style layout across all corpora: `corpus.jsonl` +
  `queries.jsonl` + `qrels/test.tsv`, plus `raw/` provenance.
- Datasets as flat siblings under `corpora/` with family-prefixed slugs
  (`org-*` organizational, `inv-*` investigative).
- Documentation: `docs/format.md` (the contract), `docs/relevance-guidelines.md`
  (grading rubric), and a dataset card per corpus.
