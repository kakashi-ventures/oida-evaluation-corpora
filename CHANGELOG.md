# Changelog

Dataset versioning for the OIDA Benchmark Corpora. This is a *data* release; the
version tracks the benchmark contents, not code. Versions follow
[Semantic Versioning](https://semver.org/): a MAJOR bump signals a
backward-incompatible change to ids, schema, or judgments.

## [1.0.0] — 2026-05-27

First public release.

### Added
- Uniform, BEIR-style layout across all four corpora: `corpus.jsonl` +
  `queries.jsonl` + `qrels/test.tsv`, plus the OIDA `epistemic/` gold layer
  (`knowledge-objects.jsonl`, `edges.jsonl`).
- Four datasets as flat siblings under `corpora/` with family-prefixed slugs:
  - `org-consulting-clearpath` — 46 docs, 26 queries, 107 qrels.
  - `org-iot-fireglass` — 47 docs, 20 queries, 82 qrels.
  - `org-vc-vertexminds` — 77 docs, 20 queries, 89 qrels.
  - `inv-mystery-redhood` — 30 docs, 8 queries, 51 qrels.
- `scripts/build_corpus.py` (deterministic `raw/` → `corpus.jsonl` normalizer),
  `scripts/validate.py` (schema + qrels/epistemic integrity), and
  `scripts/load_example.py` (BEIR-compatible loader).
- Documentation: `docs/format.md` (the contract), `docs/relevance-guidelines.md`
  (grading rubric), `docs/epistemic-taxonomy.md` (9 classes + 10 edge types), and
  a dataset card per corpus.

### Changed
- Reorganized from the previous three-case, 8-category document-dump layout into
  the uniform BEIR-style benchmark described above.
- Renamed the corpora from Italian working titles (`caso-a/b/c`) to English
  domain slugs; promoted the investigative case to a first-class dataset.

### Removed
- Experimental scaffolding vendored from the investigative source repository
  (model baselines, run logs, scores, build scripts, nested git history, and the
  nested license/citation/readme), which are not part of a data release.
