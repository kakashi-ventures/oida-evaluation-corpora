-- P1-S1 edge-composition baseline — the exact read-only SQL.
-- Canonical re-runnable form: oida-core/scripts/characterize-edges.ts
--   npx tsx scripts/characterize-edges.ts oida-%      (run as a Render one-off job)
-- SELECT-only. Engine deploy 4d2fc49. 2026-06-04.

-- (1) edges by type + cross-document vs intra-document split, per project
SELECT e."projectId" AS project, e."edgeType"::text AS edge_type, COUNT(*)::int AS total,
       COUNT(*) FILTER (WHERE s."source_id" IS NOT DISTINCT FROM t."source_id")::int AS intra_doc,
       COUNT(*) FILTER (WHERE s."source_id" IS DISTINCT FROM t."source_id")::int     AS cross_doc,
       COUNT(*) FILTER (WHERE s."source_id" IS NULL OR t."source_id" IS NULL)::int   AS null_src
FROM "edges" e
JOIN "knowledge_objects" s ON s."id" = e."sourceId"
JOIN "knowledge_objects" t ON t."id" = e."targetId"
GROUP BY e."projectId", e."edgeType"
ORDER BY e."projectId", e."edgeType";

-- (2) edge note distribution per type per project
SELECT e."projectId" AS project, e."edgeType"::text AS edge_type,
       COALESCE(e."note", '<null>') AS note, COUNT(*)::int AS n
FROM "edges" e
GROUP BY e."projectId", e."edgeType", e."note"
ORDER BY e."projectId", e."edgeType", n DESC;

-- (3) KO context per project (rows, distinct source docs, null source_id)
SELECT k."projectId" AS project, COUNT(*)::int AS kos,
       COUNT(DISTINCT k."source_id")::int AS distinct_source_docs,
       COUNT(*) FILTER (WHERE k."source_id" IS NULL)::int AS null_src
FROM "knowledge_objects" k
GROUP BY k."projectId"
ORDER BY kos DESC;
