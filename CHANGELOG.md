# Changelog

Dataset versioning for the OIDA Benchmark Corpora. This is a *data* release; the
version tracks the benchmark contents, not code. Versions follow
[Semantic Versioning](https://semver.org/): a MAJOR bump signals a
backward-incompatible change to ids, schema, or judgments.

## [2.0.0] — 2026-05-28

**Breaking change.** The benchmark is now a pure BEIR-compatible retrieval
resource. All system-specific gold artifacts have been removed so the public
release contains *only* the inputs and the relevance judgments — not the
output of any particular extraction pipeline. Users who relied on the v1.0.0
epistemic layer can pin to the `v1.0.0` git tag for archival reproducibility.

### Removed
- `corpora/*/epistemic/` — the `knowledge-objects.jsonl` + `edges.jsonl` gold
  layer is no longer part of the public release. These artifacts mirrored the
  output of a specific extraction system and are therefore implementation
  scaffolding rather than benchmark gold.
- `docs/epistemic-taxonomy.md` — the 9-class / 10-edge typed vocabulary is
  removed for the same reason.
- `metadata.epistemic_type` field on every `queries.jsonl` record across all
  five corpora.
- `scripts/validate.py` no longer checks an epistemic layer.

### Changed
- `docs/format.md` — contract reduced to BEIR core (`corpus.jsonl`,
  `queries.jsonl`, `qrels/test.tsv`) plus `raw/` provenance.
- `docs/relevance-guidelines.md` — rubric reworded to be system-agnostic
  while preserving the principles (epistemic primacy, evolving decisions,
  contradictions, traps).
- Top-level `README.md` and per-corpus dataset cards — repositioned as a
  BEIR-style benchmark with adversarial query design; counts and per-class
  taxonomy distributions removed.
- `inv-ashford-mystery/README.md` — re-aligned to the BEIR sibling layout;
  references to the legacy `ground_truth/`, `corpus/clean/`, `metadata/`
  directories removed.

## [1.0.0] — 2026-05-27

First public release.

### Added
- Uniform, BEIR-style layout across all four corpora: `corpus.jsonl` +
  `queries.jsonl` + `qrels/test.tsv`, plus an `epistemic/` gold layer
  (`knowledge-objects.jsonl`, `edges.jsonl`) — *removed in v2.0.0*.
- Four datasets as flat siblings under `corpora/` with family-prefixed slugs:
  - `org-consulting-clearpath` — 46 docs, 26 queries, 107 qrels.
  - `org-iot-fireglass` — 47 docs, 20 queries, 82 qrels.
  - `org-vc-vertexminds` — 77 docs, 20 queries, 89 qrels.
  - `inv-mystery-redhood` — 30 docs, 8 queries, 51 qrels.
- `scripts/build_corpus.py` (deterministic `raw/` → `corpus.jsonl` normalizer),
  `scripts/validate.py` (schema + qrels/epistemic integrity), and
  `scripts/load_example.py` (BEIR-compatible loader).
- Documentation: `docs/format.md` (the contract), `docs/relevance-guidelines.md`
  (grading rubric), `docs/epistemic-taxonomy.md` (9 classes + 10 edge types —
  *removed in v2.0.0*), and a dataset card per corpus.

### Changed
- Reorganized from the previous three-case, 8-category document-dump layout into
  the uniform BEIR-style benchmark described above.
- Renamed the corpora from Italian working titles (`caso-a/b/c`) to English
  domain slugs; promoted the investigative case to a first-class dataset.

### Removed
- Experimental scaffolding vendored from the investigative source repository
  (model baselines, run logs, scores, build scripts, nested git history, and the
  nested license/citation/readme), which are not part of a data release.
