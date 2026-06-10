# RESET job (Render one-off)

- service_id: `srv-d881ojr7uimc73b1berg`
- job_id: `job-d8ghf8rbc2fs73ej1ubg`
- terminal status: **succeeded**
- startCommand: `RESET_BENCH_KOS=1 npx tsx scripts/seed-bench-projects.ts`
- log source: `/v1/logs?resource=job-d8ghf8rbc2fs73ej1ubg`
- logs retrieved: True

## deleted-KOs line (verbatim from job logs)
```
# RESET_BENCH_KOS: deleted 5019 KOs (before=5019, after=0) across oida-clearpath, oida-fireglass, oida-vertexminds, oida-redhood, oida-ashford
```

## exposed-key gate
- minted slug(s): [] (none — SAFE)
- safe-no-mint marker present: **True**
- confirmation: `# All bench keys already existed; no new plaintext minted.`
