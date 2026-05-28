# Format Specification — the corpus contract

Every dataset under `corpora/` has the **identical** shape below. A loader that
reads one corpus reads all of them. The layout (`corpus.jsonl`, `queries.jsonl`,
`qrels/test.tsv`) is byte-compatible with
[BEIR](https://github.com/beir-cellar/beir); `raw/` preserves the original
source documents for provenance and reproducibility of the build.

```
corpora/<dataset-id>/
├── corpus.jsonl              # REQUIRED — documents to retrieve over   (BEIR core)
├── queries.jsonl             # REQUIRED — evaluation queries           (BEIR core)
├── qrels/
│   └── test.tsv              # REQUIRED — relevance judgments          (BEIR core)
├── raw/                      # PROVENANCE — original source documents, unmodified
└── README.md                 # dataset card
```

`scripts/validate.py` enforces every rule on this page.

---

## `corpus.jsonl` — the documents (BEIR core)

One JSON object per line:

```json
{"_id": "03-internal-comms/email/email-internal-001", "title": "Re: onboarding bottleneck", "text": "…full normalized plaintext…", "metadata": {"category": "internal-comms", "format": "md", "source_path": "raw/03-internal-comms/email/email-internal-001.md", "created": "2025-09-14"}}
```

| Field | Rule |
|---|---|
| `_id` | Stable, unique. Derived from the source path under `raw/` **without extension**, preserving provenance. |
| `title` | H1 / subject line / source short-name. |
| `text` | Full normalized plaintext. Structured sources (Slack `.json`, calendar `.json`/`.jsonl`, tabular `.csv`) are flattened to readable text by `build_corpus.py`; the original stays in `raw/`. |
| `metadata` | Free-form. `category`, `format`, `source_path` always present; `created` when a date is recoverable from the source. **No gold labels here** — `corpus.jsonl` stays neutral so retrieval cannot cheat. |

`corpus.jsonl` is **derived** from `raw/`. Regenerate it deterministically with
`python scripts/build_corpus.py corpora/<dataset-id>`.

---

## `queries.jsonl` — the evaluation queries (BEIR core)

```json
{"_id": "q01", "text": "What were the main operational bottlenecks identified at ClearPath?", "metadata": {"tests": "decision_vs_hypothesis", "difficulty": "medium"}}
```

| Field | Rule |
|---|---|
| `_id` | Unique within the corpus (`q01`, `q02`, …). |
| `text` | Natural-language evaluation question. |
| `metadata.tests` | Short slug naming the situation under test. |
| `metadata.difficulty` | `easy` / `medium` / `hard`. |

---

## `qrels/test.tsv` — relevance judgments (BEIR core)

Tab-separated, BEIR format, with a header line:

```
query-id	corpus-id	score
q01	05-meetings/meeting-005-final-presentation	3
q01	02-subject/observation-001-onboarding	2
```

- `query-id` resolves to a `queries.jsonl` `_id`; `corpus-id` resolves to a
  `corpus.jsonl` `_id`.
- **Graded relevance 0–3** (3 = directly answers / binding source, 2 = strong
  support, 1 = weak/contextual, 0 = explicitly judged non-relevant). The full
  rubric is in [`relevance-guidelines.md`](relevance-guidelines.md).
- Single `test` split: this is an evaluation-only resource, no train/dev.

---

## `raw/` — provenance

The untouched source documents. Organizational corpora keep the 8-category tree
(`01-scope` … `08-agenda`); the investigative corpus is flat (`source_*.md`).
`corpus.jsonl` is generated from here, so `raw/` is the source of truth and the
build is reproducible.
