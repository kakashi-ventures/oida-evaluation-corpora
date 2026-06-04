# oida-evaluation-corpora

The OIDA benchmark harness: BEIR-style corpora, qrels/gold, and Python scripts that ingest into
a retrieval system and score it across five layers. The engine under test lives in `../oida-core`.

## Stack & commands

Python 3, **standard library only** for `scripts/` (no install). The
`experiments/scripts/` runners call OpenAI / OIDA over HTTP and read keys from
`.env` (gitignored): `OPENAI_API_KEY`, plus `OIDA_BASE_URL`/`OIDA_ADMIN_KEY`
(angelica-db) and `OIDA_CORE_BASE_URL`/`OIDA_CORE_ADMIN_KEY` (oida-core).

```bash
# Corpus tooling (stdlib only)
python scripts/load_example.py corpora/org-consulting-clearpath  # inspect
python scripts/build_corpus.py                                   # raw/ → corpus.jsonl (deterministic)
python scripts/validate.py                                       # schema + qrels CI gate

# Experiment pipeline (numbered = run order; --system selects the SUT slot)
python experiments/scripts/01_ingest.py   --system oida-core            # clean-ingest all 5 corpora
python experiments/scripts/02_retrieve.py --system oida-core --run-id <id>   # → output/retrieve_runs/
python experiments/scripts/03_eval_static_ir.py --run-id <id> --system oida-core   # one layer
```
Append a corpus dir name to any runner to limit it to one corpus (e.g. `... inv-ashford-mystery`).

## Layout

- `corpora/<id>/` — `corpus.jsonl` (BEIR `{_id,title,text,metadata}`), `queries.jsonl`,
  `qrels/test.tsv` (TSV: `query-id  corpus-id  score`, graded 0–3), `raw/` (provenance), `README.md`.
- `experiments/scripts/0X_*.py` — `01` ingest, `02` retrieve, **`03`–`07` = the five eval layers**,
  `08` report (rolls up F-conditions → `RESULTS.md`). `eval_common.py` = shared loaders.
- `experiments/adapters/*.py` — one per system; **`oida.py` is the OIDA adapter**, reused twice
  (`oida-angelicadb`, `oida-core`); also `graphrag_msft.py`, `lightrag.py`, `hipporag.py`.
- gitignored: `experiments/annotations/` (private gold: stance, contra sets, supersession, temporal),
  `experiments/systems/` (cloned baselines), `experiments/output/` (run artifacts).

## Pointing a system at a corpus / where results go

System slots: `oida-angelicadb`, `oida-core`, `graphrag`, `lightrag`, `hipporag`. Each doc is
ingested with source URI `beir-corpora://<corpus>/<doc_id>` and isolated at retrieve time by
source-prefix filter. `02_retrieve.py` writes runs to `experiments/output/retrieve_runs/<corpus>/<system>_<run_id>/`;
the layer scorers create/update the committed report at `corpora/<id>/results/<system>_<run_id>.json`.

## The five evaluation layers

1. **Static IR (`03`)** — plain BEIR topical relevance: NDCG / recall / MAP / precision @k.
2. **Adversarial (`04`)** — contradiction recall, supersession (binding vs superseded), trap rejection.
3. **Stance & abstention (`05`)** — S/C/NEI stance + abstention thresholds (gpt-4o judge; `--run` costs money).
4. **Temporal (`06`)** — lifecycle/current-state retrieval, superseded leakage, freshness overbias.
5. **Practicality (`07`)** — cost & latency telemetry (tokens, wall-clock p50/p95).

## Regression Harness (the oracle)

`run_regression.sh` does **not exist yet** — it is created in Phase 0 (**P0-S7**). It is the single
command run after every phase: clean-ingest fresh into isolated per-corpus projects on `oida-core`,
run all five layers, and emit a timestamped Evidence Bundle under
`experiments/output/regression/<phase>-<ts>/`. A phase is not done until its bundle is produced.

## ⚠️ BURNED DEV SET — never tune or gate against these

The five existing corpora (`org-consulting-clearpath`, `org-iot-fireglass`, `org-vc-vertexminds`,
`inv-mystery-redhood`, `inv-ashford-mystery`) are a **seen/burned dev set**. Use them only as
regression sanity signal. **Never** tune thresholds/weights to them and **never** base any pass/fail
claim on them — pass/fail comes **only** from the Phase 4 fresh corpora. Do not modify gold labels
(`qrels/`, `experiments/annotations/`).

## Roadmap

Active spec: `../doc/oida-core_remediation_roadmap.md`. **Phases 0 and 4 are implemented in THIS
repo** (Phases 1–3 are in `oida-core`); read phase scope there, do not invent it.
