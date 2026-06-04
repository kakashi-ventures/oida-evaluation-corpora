# harness_health.md

## DB infrastructure (Render Postgres, read-only snapshot)

Records the managed Postgres conditions the run executed against
(pulled READ-ONLY from the Render API; the API key is never recorded).

- endpoint: `https://api.render.com/v1/postgres/dpg-d881lq1kh4rs73c92a50-a`
- fetch_ok: **True** (HTTP 200)
- name: `oida-core-db`
- **status: `available`**
- plan: `basic_256mb`
- diskSizeGB: `5`
- region: `frankfurt`  |  version: `17`  |  suspended: `not_suspended`

## Micro-probe — judge label distribution (clearpath, live, cold cache)

Judges the 13 stance-evaluable clearpath queries (5 gold-CONTRADICTS:
q03/q04/q16/q19/q25).

- emitted label distribution (n=13): `{'INVALID': 6, 'NEUTRAL': 5, 'SUPPORTS': 1, 'CONTRADICTS': 1}`
- **CONTRADICTS count: 1** (>=1 invariant: HELD)

### Before/after framing vs the old judge bug
Pre P0-S3 the judge ran with `max_tokens=4` and (pre P0-S4) was fed a
GraphRAG-only prose shortcut; on the burned set that produced **0/181**
CONTRADICTS (every label collapsed to INVALID/NEUTRAL). With
`max_tokens=16` (P0-S3), top-1 doc-text input for ALL systems (P0-S4),
and the P0-S7 cache re-key (so those fixes are no longer masked by stale
cache hits), CONTRADICTS is now reachable. This proves the judge axis is
live; it is NOT an OIDA stance score (the burned set is sanity-only).

## Per-corpus ingest health

| corpus | docs | committed | all_committed | kos_created | 0-KO docs | partial_errs | partial-err docs |
|---|---|---|---|---|---|---|---|
| org-consulting-clearpath | 46 | 46 | True | 4156 | 1 | 0 | 0 |
| org-iot-fireglass | 47 | 47 | True | 6011 | 0 | 0 | 0 |
| org-vc-vertexminds | 77 | 77 | True | 5250 | 19 | 0 | 0 |
| inv-mystery-redhood | 30 | 30 | True | 172 | 0 | 0 | 0 |
| inv-ashford-mystery | 30 | 30 | True | 348 | 1 | 0 | 0 |

## P0-S6 adapter-retained epistemic fields

The retrieve adapter retains `dialectic_resolutions`, `contradiction_edges`,
and `contradiction_edge_count` per query (P0-S6). Pre-Phase-2 these are
EMPTY by design (the cross-document epistemic graph is built in Phase 1 and
the contradiction path activates in Phase 2). Presence of the fields (not
their values) is the P0 check; per-corpus presence:

- org-consulting-clearpath: fields present on 26/26 query records; dialectic_resolutions total=0, contradiction_edge_count total=0 (EMPTY pre-Phase-2, LABELED so)
- org-iot-fireglass: fields present on 20/20 query records; dialectic_resolutions total=0, contradiction_edge_count total=0 (EMPTY pre-Phase-2, LABELED so)
- org-vc-vertexminds: fields present on 20/20 query records; dialectic_resolutions total=0, contradiction_edge_count total=0 (EMPTY pre-Phase-2, LABELED so)
- inv-mystery-redhood: fields present on 8/8 query records; dialectic_resolutions total=0, contradiction_edge_count total=0 (EMPTY pre-Phase-2, LABELED so)
- inv-ashford-mystery: fields present on 6/6 query records; dialectic_resolutions total=0, contradiction_edge_count total=0 (EMPTY pre-Phase-2, LABELED so)

## RESET-job confirmation

- reset line: `# RESET_BENCH_KOS: deleted 14916 KOs (before=14916, after=0) across oida-clearpath, oida-fireglass, oida-vertexminds, oida-redhood, oida-ashford`
- **# All bench keys already existed; no new plaintext minted.** present: True
- minted slugs (must be empty): []
