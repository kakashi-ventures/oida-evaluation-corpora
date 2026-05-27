# Format Specification — the corpus contract

Every dataset under `corpora/` has the **identical** shape below. A loader that
reads one corpus reads all of them. The BEIR core (`corpus.jsonl`,
`queries.jsonl`, `qrels/test.tsv`) is byte-compatible with
[BEIR](https://github.com/beir-cellar/beir); the `epistemic/` layer is the
OIDA-specific extension.

```
corpora/<dataset-id>/
├── corpus.jsonl              # REQUIRED — documents to retrieve over   (BEIR core)
├── queries.jsonl             # REQUIRED — evaluation queries           (BEIR core)
├── qrels/
│   └── test.tsv              # REQUIRED — relevance judgments          (BEIR core)
├── epistemic/                # OIDA extension — the epistemic gold layer
│   ├── knowledge-objects.jsonl
│   └── edges.jsonl
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
| `metadata` | Free-form. `category`, `format`, `source_path` always present; `created` when a date is recoverable. **No gold or epistemic labels here** — `corpus.jsonl` stays neutral so retrieval cannot cheat. |

`corpus.jsonl` is **derived** from `raw/`. Regenerate it deterministically with
`python scripts/build_corpus.py corpora/<dataset-id>`.

---

## `queries.jsonl` — the evaluation queries (BEIR core)

```json
{"_id": "q01", "text": "What were the main operational bottlenecks identified at ClearPath?", "metadata": {"epistemic_type": "DECISION", "tests": "decision_vs_hypothesis", "difficulty": "medium"}}
```

| Field | Rule |
|---|---|
| `_id` | Unique within the corpus (`q01`, `q02`, …). |
| `text` | Natural-language evaluation question. |
| `metadata.epistemic_type` | What the query *probes*: one of the 9 knowledge-object classes (`DECISION`, `CONSTRAINT`, `EVIDENCE`, `NARRATIVE`, `PLAN`, `EVALUATION`, `OBSERVATION`, `HYPOTHESIS`, `QUESTION`) or `CONTRADICTION`. This is the core novelty versus topical BEIR queries. |
| `metadata.tests` | Short slug naming the epistemic situation under test. |
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

## `epistemic/` — the epistemic gold layer (OIDA extension)

The layer that makes this an *epistemic* retrieval benchmark rather than a
topical one. Classes and edge types follow
[`epistemic-taxonomy.md`](epistemic-taxonomy.md).

### `knowledge-objects.jsonl`

```json
{"ko_id": "KO-014", "class": "QUESTION", "text": "Is the audit workflow the true bottleneck or a symptom?", "source_id": "05-meetings/meeting-003-interim-review", "confidence": 0.30, "salience": "high"}
```

| Field | Rule |
|---|---|
| `ko_id` | Unique within the corpus. |
| `class` | The knowledge-object's epistemic class (see taxonomy). |
| `text` | The claim / decision / question, one sentence. |
| `source_id` | A `corpus.jsonl` `_id` where the object originates. |
| `confidence` | Seed confidence 0.0–1.0 (class-dependent baseline). |
| `salience` | `high` / `medium` / `low`. |

A KO may carry extra fields. The investigative corpus additionally records
`supporting_sources` (full provenance list), `entities`, `causal_role`, a native
domain `class`, and an `oida_class` mapping it to the canonical taxonomy — see
that dataset's card. The validator requires each KO to cite at least one
resolvable corpus id (via `source_id` or `supporting_sources`).

### `edges.jsonl`

```json
{"src": "KO-031", "dst": "KO-014", "type": "CONTRADICTS", "coefficient": -0.6}
```

| Field | Rule |
|---|---|
| `src`, `dst` | Both resolve to a `ko_id` in `knowledge-objects.jsonl`. |
| `type` | An edge type from the taxonomy (`SUPPORTS`, `CONTRADICTS`, `SUPERSEDES`, …). |
| `coefficient` | The signed weight for that type (see taxonomy table). |

---

## `raw/` — provenance

The untouched source documents. Organizational corpora keep the 8-category tree
(`01-scope` … `08-agenda`); the investigative corpus is flat (`source_*.md`).
`corpus.jsonl` is generated from here, so `raw/` is the source of truth and the
build is reproducible.
