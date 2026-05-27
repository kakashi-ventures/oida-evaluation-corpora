# Reorganization Spec — OIDA Benchmark Corpora

**Target identity:** *OIDA Benchmark Corpora: A Resource for Evaluating Epistemic Retrieval in Organizations*
**Inspiration:** [BEIR](https://github.com/beir-cellar/beir) — a heterogeneous benchmark where every dataset shares one uniform `corpus / queries / qrels` layout and a single master index.
**Status:** Spec for review. No file has been moved yet; this document is the plan to execute.

---

## 1. Goals

1. **One uniform, BEIR-style layout** across every corpus, so any researcher can clone the repo and load every dataset with the same code.
2. **Real retrieval benchmark**, not just a document dump: each corpus ships `corpus.jsonl` + `queries.jsonl` + `qrels/`, plus an OIDA-specific **epistemic gold** extension.
3. **Clean repo**: no model outputs, no run logs, no nested git history, no experimental scaffolding. Only inputs + ground truth + the minimal tooling to load and score.
4. **Consistent English naming**, domain-based slugs, no Italian leftovers, no typos.
5. **Self-documenting**: a master README with a dataset table, a shared format spec, and a per-corpus dataset card.

---

## 2. Current state (audit)

The working tree is mid-migration. Findings:

| Issue | Detail | Action |
|---|---|---|
| Mid-move not committed | `corpora/caso-{a,b,c}` deleted, re-added under `corpora/organizational-retrive/` (untracked) | Finalize into target layout, then one clean commit |
| Typo | `organizational-retrive` → should be `organizational-retrieval` | Drop the family folder entirely (see §3) |
| Nested git repo | `corpora/investigative-retrieve/red-hood-epistemic-benchmark/.git` (~55 MB), own remote | Remove `.git`; vendor only the corpus + ground truth |
| Experimental bloat | `baselines/` (4 versions), `runs/`, `scores/`, `scripts/`, `config.json`, `CHANGELOG.md`, `oida-bridge/responses/` | Delete — not part of a data release |
| Empty placeholder | `corpora/investigative-retrieve/damer-victims/` (empty) | Delete |
| No queries/qrels | Org corpora are raw 8-category document dumps; not retrieval-evaluable | Author `queries.jsonl` + `qrels/` (§5, §6) |
| Stale master README | Old paper title; mentions only 3 org cases; no investigative family | Rewrite (§7) |
| Language mix | `caso-a/b/c` Italian vs English content | Rename to English domain slugs (§4) |
| Two file-layout conventions | Org = 8 numbered categories; Red Hood = corpus/ground_truth/evaluation | Unify under one schema (§5) |

---

## 3. Target top-level layout

Flat, BEIR-faithful: each dataset is a sibling folder under `corpora/`, the family is encoded in the slug prefix (`org-*`, `inv-*`). No `organizational-retrieval/` or `investigative-retrieve/` wrapper folders.

```
oida-benchmark-corpora/
├── README.md                       # master index: title, abstract, dataset table, format, usage, citation
├── LICENSE                         # CC BY 4.0 (single, repo-wide)
├── CITATION.cff                    # single, repo-wide
├── CHANGELOG.md                    # repo-level dataset versioning (v1.0.0 = first public release)
├── .gitignore
│
├── docs/
│   ├── format.md                   # the corpus/queries/qrels + epistemic schema (the contract)
│   ├── epistemic-taxonomy.md       # 9 KO classes + 10 edge types (shared reference) — keep existing
│   └── relevance-guidelines.md     # how qrels relevance grades were assigned (epistemic rubric)
│
├── corpora/
│   ├── org-consulting-clearpath/   # ex caso-a  (Consulting / Operations — ClearPath/Meridian)
│   ├── org-iot-fireglass/          # ex caso-b  (IoT / Product — FireGlass)
│   ├── org-vc-vertexminds/         # ex caso-c  (Venture Capital — Vertex Minds)
│   └── inv-mystery-redhood/        # ex red-hood-epistemic-benchmark (Investigative)
│
├── scripts/
│   ├── build_corpus.py             # raw source docs → corpus.jsonl (deterministic normalizer)
│   ├── validate.py                 # schema + qrels integrity checks (ids resolve, no orphans)
│   └── load_example.py             # minimal loader; shows BEIR-compatible loading
│
└── evaluation/
    ├── README.md                   # how to score; EQS protocol pointer
    ├── eqs_scorer.py               # keep existing
    ├── question_analysis.py        # keep existing
    └── requirements.txt            # keep existing
```

**Why flat + prefixes (not family wrapper dirs):** BEIR keeps all datasets as siblings; loaders glob `corpora/*`. The `org-`/`inv-` prefix carries the family without an extra path level, and matches the chosen naming convention.

---

## 4. Naming convention

| Old | New dataset id (= folder name) | Domain |
|---|---|---|
| `caso-a` | `org-consulting-clearpath` | Consulting / Operational process review |
| `caso-b` | `org-iot-fireglass` | IoT / Product development |
| `caso-c` | `org-vc-vertexminds` | Venture Capital / Investment committee |
| `red-hood-epistemic-benchmark` | `inv-mystery-redhood` | Investigative / multi-source reasoning |

Rules:
- All lowercase, kebab-case, ASCII.
- Pattern: `{family}-{domain}-{org}` where `family ∈ {org, inv}`.
- No Italian, no version numbers in folder names (versioning lives in `CHANGELOG.md` / git tags).

---

## 5. Per-corpus layout (the uniform contract)

Every folder under `corpora/` is identical in shape:

```
corpora/<dataset-id>/
├── corpus.jsonl            # REQUIRED — the documents to retrieve over (BEIR core)
├── queries.jsonl           # REQUIRED — evaluation queries (BEIR core)
├── qrels/
│   └── test.tsv            # REQUIRED — relevance judgments (BEIR core)
├── epistemic/              # OIDA EXTENSION — the "epistemic retrieval" gold layer
│   ├── knowledge-objects.jsonl
│   └── edges.jsonl
├── raw/                    # PROVENANCE — the original source documents, unmodified
│   └── ...                 # (org: 8-category tree; inv: 30 source_*.md)
└── README.md               # dataset card
```

### 5.1 `corpus.jsonl` (BEIR core)
One JSON object per line. Strictly BEIR-compatible so existing loaders work unchanged.

```json
{"_id": "03-internal-comms/email/email-internal-001", "title": "Re: onboarding bottleneck", "text": "...full document text...", "metadata": {"category": "internal-comms", "format": "md", "source_path": "raw/03-internal-comms/email/email-internal-001.md", "created": "2025-09-14"}}
```

- `_id`: stable, derived from the source path **without extension** (preserves provenance, guaranteed unique).
- `title`: H1 / subject line / source short-name.
- `text`: full normalized plaintext. Structured sources (Slack `.json`, calendar `.jsonl`, `.csv`) are flattened to readable text by `build_corpus.py`; the original stays in `raw/`.
- `metadata`: free-form; **no gold/epistemic labels here** (keep `corpus.jsonl` neutral so retrieval can't cheat).

### 5.2 `queries.jsonl` (BEIR core)
```json
{"_id": "q01", "text": "What were the main operational bottlenecks identified at ClearPath?", "metadata": {"epistemic_type": "DECISION", "tests": "decision_vs_hypothesis", "difficulty": "medium"}}
```
- `epistemic_type` tags what the query probes (DECISION, CONTRADICTION, QUESTION, HYPOTHESIS, …) — the core novelty vs. topical BEIR queries.

### 5.3 `qrels/test.tsv` (BEIR core)
Tab-separated, BEIR format, with header:
```
query-id	corpus-id	score
q01	05-meetings/meeting-005-final-presentation	3
q01	02-subject/observation-001-onboarding	2
```
- Graded relevance **0–3** (3 = directly answers / binding source, 2 = strong support, 1 = weak/contextual, 0 = explicitly judged non-relevant). Rubric in `docs/relevance-guidelines.md`.

### 5.4 `epistemic/` (OIDA extension)
The layer that makes this an *epistemic* retrieval benchmark, not a topical one.

`knowledge-objects.jsonl`:
```json
{"ko_id": "KO-014", "class": "QUESTION", "text": "Is the audit workflow the true bottleneck or a symptom?", "source_id": "05-meetings/meeting-003-interim-review", "confidence": 0.30, "salience": "high"}
```
`edges.jsonl`:
```json
{"src": "KO-031", "dst": "KO-014", "type": "CONTRADICTS", "coefficient": -0.6}
```
Classes/edges follow `docs/epistemic-taxonomy.md` (already correct in the repo).

### 5.5 `raw/` (provenance)
The untouched source documents. `corpus.jsonl` is **derived** from `raw/` by `scripts/build_corpus.py`, so the pipeline is reproducible and the source of truth is preserved.

---

## 6. Per-corpus migration

### 6.1 Org corpora (`org-consulting-clearpath`, `org-iot-fireglass`, `org-vc-vertexminds`)
1. `git mv` the existing 8-category tree (`01-scope` … `08-agenda`) into `corpora/<id>/raw/`.
2. Run `build_corpus.py` → `corpus.jsonl` (flatten `.md/.json/.jsonl/.csv` to text).
3. **Author `queries.jsonl`** — 15–30 queries per corpus spanning the epistemic situations the scenario was designed for (decisions that evolve, contradictions between teams, unresolved questions, confirmed/refuted hypotheses). Caso A is the paper's primary corpus, so prioritize it.
4. **Author `qrels/test.tsv`** — graded judgments per query against `corpus.jsonl` ids.
5. **Author `epistemic/`** — KO + edges gold (can start from the epistemic profiles already described in each case README).
6. Rewrite the case README as a dataset card (§5 README spec).

### 6.2 Investigative corpus (`inv-mystery-redhood`)
Keep **only** the corpus + the ground truth needed to build the BEIR triple. Everything else is deleted.

**Keep → transform:**
- `corpus/clean/source_*.md` (30 docs) → `corpora/inv-mystery-redhood/raw/` → `corpus.jsonl`.
- `metadata/source_metadata_clean.json` → source of `qrels` + `epistemic/` (already contains `reliability_prior`, `expected_salience`, `expected_epistemic_role`, `contains_false_lead`, `contains_contradiction`, `ground_truth_events_referenced`).
- `evaluation/gold_labels_clean.json` + `docs/golden_benchmark_clean.md` → source of `queries.jsonl` (e.g. "Who is the culprit and with what confidence?") + answer key.
- `ground_truth/*.json` → fold into `epistemic/` (KO graph, edges, entities, events).

**Delete (experimental scaffolding, not data):**
- `.git/` (the nested 55 MB repo), `baselines/` (all versions), `runs/`, `scores/`, `scripts/`, `scripts/oida-bridge/responses/`, `config.json`, `CHANGELOG.md`, the nested `CITATION.cff`/`LICENSE`/`README.md` (replaced by repo-level + dataset card).

This corpus has the richest native ground truth — its qrels can use `reliability_prior` × relevance and its `epistemic/` layer is essentially pre-built.

---

## 7. Master README (rewrite)

New top-level README sections:
1. **Title + abstract** — new paper title; one-paragraph what/why.
2. **Dataset table** — id, family, domain, #docs, #queries, #qrels, size, license.
3. **Format** — link to `docs/format.md`; show the `corpus/queries/qrels/epistemic` shape once.
4. **Quick start** — clone, `pip install -r evaluation/requirements.txt`, `python scripts/load_example.py corpora/org-consulting-clearpath`.
5. **What makes it epistemic** — point to `epistemic/` and the taxonomy; contrast with topical retrieval.
6. **Citation** — updated BibTeX + `CITATION.cff`.
7. **License & acknowledgements.**

Updated dataset table (counts to be filled after build):

| Dataset | Family | Domain | Docs | Queries | Size |
|---|---|---|---|---|---|
| `org-consulting-clearpath` | organizational | Consulting / Operations | 46 | TBD | 318 KB |
| `org-iot-fireglass` | organizational | IoT / Product | 47 | TBD | 566 KB |
| `org-vc-vertexminds` | organizational | Venture Capital | 77 | TBD | 376 KB |
| `inv-mystery-redhood` | investigative | Multi-source reasoning | 30 | TBD | TBD |

---

## 8. Cleanup checklist (files that should NOT exist after migration)

- [ ] `corpora/organizational-retrive/` (typo folder) — removed (contents moved into `corpora/<org-id>/raw/`)
- [ ] `corpora/investigative-retrieve/` wrapper — removed
- [ ] `corpora/investigative-retrieve/damer-victims/` (empty) — removed
- [ ] `.../red-hood-epistemic-benchmark/.git/` — removed
- [ ] `.../red-hood-epistemic-benchmark/baselines/` — removed
- [ ] `.../red-hood-epistemic-benchmark/runs/` — removed
- [ ] `.../red-hood-epistemic-benchmark/scores/` — removed
- [ ] `.../red-hood-epistemic-benchmark/scripts/` — removed (incl. `oida-bridge/`)
- [ ] `.../red-hood-epistemic-benchmark/{config.json,CHANGELOG.md}` — removed
- [ ] Nested `CITATION.cff` / `LICENSE` / `README.md` — removed (repo-level versions win)
- [ ] Old top-level `docs/corpus-schema.md` — replaced by `docs/format.md`

---

## 9. Migration steps (execution order)

1. **Branch**: `git checkout -b restructure/beir-layout`.
2. **Stage the org rename** with `git mv` (preserves history) old `caso-*` → `corpora/<org-id>/raw/`.
3. **Vendor Red Hood**: copy the keep-list (§6.2) out, `rm -rf` the nested repo, place files under `corpora/inv-mystery-redhood/`.
4. **Write `scripts/build_corpus.py` + `validate.py`**, generate `corpus.jsonl` for all four.
5. **Author `queries.jsonl` + `qrels/` + `epistemic/`** (Red Hood mostly derived; org authored).
6. **Rewrite** master README, `docs/format.md`, `docs/relevance-guidelines.md`, four dataset cards.
7. **Update** `CITATION.cff` + repo metadata to new title.
8. **Validate**: `python scripts/validate.py` (every qrels id resolves to a corpus/query id; no orphans).
9. **One clean commit** + tag `v1.0.0`.

---

## 10. Open items for confirmation

- **Query authoring volume** per org corpus (proposed: 15–30 each; Caso A richest).
- **Relevance scale**: graded 0–3 (proposed) vs binary 0/1. Graded is more expressive for epistemic relevance.
- **`epistemic/` scope**: ship full KO+edge gold for all four, or only Caso A + Red Hood first (the two with the richest existing material)?
- **Splits**: single `test.tsv` per corpus (proposed) — no train/dev, since this is an evaluation-only resource.
