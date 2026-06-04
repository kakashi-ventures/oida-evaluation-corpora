# P1-S1 run metadata

- **Step:** P1-S1 — characterize current edge formation (read-only).
- **Date:** 2026-06-04.
- **Engine deploy under test:** oida-core `4d2fc49` (origin/main at run time; the deployed SHA is what
  the DB reflects — no re-ingest since the 2026-06-04 P0-baseline).
- **Datastore:** Render Postgres `dpg-d881lq1kh4rs73c92a50-a` (`oida-core-db`, basic_256mb, frankfurt,
  pg17). `ipAllowList: null` → in-network access only (neither the Render query tool nor external psql
  can reach it; external psql is also blocked by the empty allowlist).
- **Method:** read-only one-off job on the oida-core Render service (same mechanism as the RESET job),
  querying the in-network `DATABASE_URL` via the app's `pg` driver. SELECT-only; no mutation.
  Capture job: `job-d8gknv0jo6nc73ella30` (succeeded 2026-06-04T09:57:46Z).
- **Reusable tool:** `oida-core/scripts/characterize-edges.ts` (committed at oida-core `903e6c8`) —
  `npx tsx scripts/characterize-edges.ts oida-%`.
- **Reproduce:** with oida-core deployed, fire a Render one-off job with that start command and read the
  `###CHARACTERIZE###` log lines (the final `JSON` line is the full machine-readable result).
- **Guardrail:** read-only; characterization only; not an OIDA performance claim. Burned corpora remain
  regression/sanity only.
