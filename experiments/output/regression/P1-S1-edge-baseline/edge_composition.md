# P1-S1 — Edge-composition baseline (read-only characterization)

**Date:** 2026-06-04 · **Engine deploy:** oida-core `4d2fc49` (origin/main at run time) ·
**Store:** Render Postgres `dpg-d881lq1kh4rs73c92a50-a` (in-network) · **Method:** read-only
in-Render one-off job (the DB is `ipAllowList: null` = in-network only). No mutation.

Reusable tool (the query, versioned): **`oida-core/scripts/characterize-edges.ts`**
(`npx tsx scripts/characterize-edges.ts oida-%`, run as a Render one-off job). This file is the
captured OUTPUT; together they are reproducible evidence (the exact SQL is in `query.sql`, run
metadata in `run_meta.md`).

## Edge composition per bench corpus

| corpus | KOs | source-docs | total edges | edge types present | typed edges (non-DERIVES_FROM) | cross-document edges |
|---|--:|--:|--:|---|--:|--:|
| oida-clearpath   | 4,039 | 190 | 50,111 | DERIVES_FROM only | **0** | **0** |
| oida-fireglass   | 5,924 | 306 | 66,501 | DERIVES_FROM only | **0** | **0** |
| oida-vertexminds | 5,179 | 216 | 68,785 | DERIVES_FROM only | **0** | **0** |
| oida-ashford     |   346 |  29 |  1,989 | DERIVES_FROM only | **0** | **0** |
| oida-redhood     |   169 |  30 |    397 | DERIVES_FROM only | **0** | **0** |

`null_src = 0` for every project → `source_id` is always populated; the cross/intra split is valid.

Non-bench `default` project (`066c1498-…`, not a corpus): 20,754 KOs / 199,291 edges, also 100%
intra-document `DERIVES_FROM`, cross-doc 0 — the stale operator-hygiene pile (RESET does not clear `default`).

## Findings — P1-S1 Acceptance (cross-doc ≈ 0, notes intra-document): CONFIRMED, exactly 0
1. **Zero typed epistemic edges.** Only `DERIVES_FROM` exists. The other 9 schema relations —
   `CONTRADICTS`, `SUPERSEDES`, `SUPPORTS`, `IMPLEMENTS`, `ENABLES`, `BLOCKS`, `PRECEDES`,
   `SYNTHESIZES`, `MONITORS` — have **0 rows** in every project.
2. **Zero cross-document edges.** `cross_doc = 0` everywhere; every edge joins two KOs sharing one `source_id`.
3. **Notes uniformly intra-document.** 100% of edges carry `"Co-extracted from same source document"`.

→ The cross-document epistemic graph does not exist. This is the zero-baseline Phase 1 (P1-S5/S6) must
move off. Re-running the tool after P1-S5/S6 must show typed cross-document edges with a real
distribution (the BEFORE→AFTER this artifact anchors).

## Caveats for Phase 1
- **`source_id` granularity.** `distinct_source_docs` (e.g. vertexminds 216 vs the 77 harness-ingested
  docs) indicates the eval adapter chunks one logical document into multiple `/ingest` calls, each its
  own `source_id`. The engine treats each `source_id` as a "source document" (the fanout note). So
  cross-doc=0 is measured at `source_id` granularity; cross-logical-document ⊆ that, also 0. **P1-S5
  cross-document detection must span all `source_id`s in a project, not a single payload.**
- **Count drift vs P0-baseline.** Current KO rows sit slightly below the P0-baseline `kos_created`
  (vertexminds 5,179 vs 5,250; clearpath 4,039 vs 4,156; fireglass 5,924 vs 6,011) — current-rows vs
  creation-count; immaterial, and separate from the 19/77-zero-KO P1-S7 carry-forward.

_Guardrail: read-only characterization; not an OIDA performance claim._
