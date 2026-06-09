# eureg-evolution — R1.2 re-authoring note (2026-06-09)

**Author role:** corpus author (file-level re-authoring only). NOT the gold adjudicator (the
blind human D-B pass comes after, on THIS version), no engine/staging/prod touched, no pilot run.
**Branch:** `phase4/eureg-corpus` · **Source of truth edited:** `_build_pilot.py` (gitignored),
then deterministically re-emitted → `corpus.jsonl` / `queries.jsonl` / `qrels/` / annotations.
**Gold semantics:** **unchanged** — zero qrels score changes, zero annotation-structure changes.
Every edit below is doc/query *text only*.

## Result

| gate | before | after |
|---|---|---|
| **R1.2 current-is-top-cosine** | **100% (6/6) FAIL** | **16.7% (1/6) PASS** (target ≤ ~40%) |
| R1.1 freshest-is-current | 100% (4/4) PASS | 100% (4/4) PASS |
| R1.3 supersession cue in-text | 100% (4/4) PASS | 100% (4/4) PASS |
| R1.4 temporal mix | 50/25/25 PASS | 50/25/25 PASS |
| R2.1 short-comms gold | 5 pairs PASS | 5 pairs PASS |
| R4 cross-doc contradictions | 3 PASS | 3 PASS |
| R5 trap pairs | 86 PASS | 86 PASS |
| R3 authority-conflict | 2 (1:1) REVIEW (M not locked) | unchanged (pre-existing) |
| R2.2 / R6 | PENDING (engine, pilot) | unchanged |

Verified with `experiments/scripts/p4s1_corpus_stats.py eureg-evolution` (OpenAI
`text-embedding-3-small`, offline; report → `/tmp/p4s1-eureg-reauth`). R1.2 denominator = the 6
temporal queries with `gold_current_docs` (q01–q04 freshness + q07/q08 distractor); stable
q05/q06 are excluded by construction (no `gold_current_docs`) and were **not touched**.

## Per-query changes

Final per-query cosine state (`rank` = the answer/current doc's plain-cosine rank over all 38
docs; `gap` = cos(answer) − cos(best other doc); negative = de-confounded):

| q | levers used | top-cosine doc now | answer rank / gap |
|---|---|---|---|
| **q01** | (a) densified the **interim** guidance to mirror the final's vocabulary ("transparency and technical-documentation obligations of GPAI model providers", documentation-set terms; interim status + dates kept) · (b) query de-cued: dropped "current" + "did the interim position change?" (tail was answerable from the score-3 doc alone — also removes the HC-5 ambiguity) | `gpai-transparency-interim-2025-02` (superseded, the intended competitor) | 2 / **−0.053** |
| **q02** | (a) densified **v1** ("incident-reporting timeline under CS-NIS2-07 … the incident-reporting timeline we follow under our NIS2 standard") · (b) query de-cued: dropped "today" + "what changed from the earlier version"; added neutral anchor "CS-NIS2-07" (in both v1+v2 titles) | `nis2-incident-reporting-v1-2024-01` (superseded) | 3 / **−0.102** |
| **q03** | (a) densified **v1** ("This standard-contractual-clause configuration is what our data-transfer policy DT-03 requires…"; dropped one "Current" from v1) · (b) query de-cued: dropped "current"; added neutral anchor "DT-03" | `gdpr-transfer-policy-v1-2023` (superseded) | 2 / **−0.034** |
| **q04** | (a) densified the **limited-risk** opinion ("AI Act risk classification of the CV-Screening Assistant … risk classification of record") · (b) query de-cued: dropped "current" + "was it reclassified?" | `risk-class-cv-tool-limited-2024-05` (superseded) | 2 / **−0.057** |
| **q07** | (b) dropped "currently" from the query · densified the WITHDRAWN amendment (it now recites the Art 5 list it amends — realistic for an amendment; WITHDRAWN/false-cue text intact). **Still top-is-current (+0.231)** — the in-force statute inevitably dominates its own enumeration query; this is the 1/6 residual and is accepted: the distractor mechanic (fresh false-cue must not displace the older statute) is recency-side, not cosine-side. | `aiact-prohibited-practices-current` (current) | 1 / +0.231 |
| **q08** | (b) dropped "current" from the query · densified the false-cue **email** (DPIA vocabulary; unratified-musing register intact) · densified **Art 35** ("sets when a data protection impact assessment is required…") | `gdpr-art35-dpia` (score-2 supporting statute — current no longer top) | 2 / **−0.003** |
| **q12** (authority-ii, not in R1.2 — mandated raglit-style inversion) | query rewritten colloquial ("Which provision sets the maximum fine we risk for an unlawful transfer of personal data outside the EU?") · **fines-blog** retitled + densified on exactly those terms (still never names Art 83 → still not the answer) · Art 83's final sentence de-verbatimed ("…highest tier of administrative fines") | `blog-gdpr-fines-explained` (the designed high-cosine lure) | **Art 83 rank 2 / −0.026** |
| **q13** (authority-i, not in R1.2 — mandated inversion) | query rewritten in the standard's vocabulary ("submit the early warning to the national CSIRT within 24 hours under CS-NIS2-07") · **v2 standard** retitled ("…& 24h Early Warning…") + one added sentence ("the standard does not name the specific submission channel or endpoint — see operational guidance", which also sharpens the authority-i design) · the answer **email** de-magnetized (title "re: where we actually file the early warning"; "CS-NIS2-07" token removed from its body; portal/early-warning-form/NW-441 answer content intact) | `nis2-incident-reporting-v2-2025-03` (authoritative-but-not-answer) | **email rank 2 / −0.048** |

Untouched: q05/q06 (stable — current=top is correct there), q09/q10/q11 (contradictions — not in
R1.2; minimal-touch), all of raglit-evolution, all gold scores.

## Constraints honored

- **R1.1**: no dates changed. **R1.3**: all supersession cues in the *current* docs untouched
  (the competitor was strengthened; the cue never removed). **R1.4**: `temporal_class` metadata
  untouched. **R4/R5**: no qrels rows added/removed/rescored (86 traps, 3 contra sets).
- **No tuning to engine output**: every check in this pass is a *corpus statistic* (offline
  embeddings via the official stats script); the engine was never queried.
- **Adjudication interplay (deliberate):** the 3 eureg FIXes and the 4 FLAG text repairs from
  `ADJUDICATION-FABLE5.md` are **NOT applied here** — per DR-P4-001 D-B(iii) they go in the
  single regeneration at the blind-pass reconciliation. The only FLAG-adjacent change is the
  q01 query-tail removal (HC-5), which is a query edit, not a gold/text-fix, and removes an
  ambiguity rather than deciding one. The q07 amendment densification recites the Art 5 list but
  does not touch the FLAGged premise (workplace emotion-recognition) — that stays for
  reconciliation.
- **Recall sanity**: every answer doc remains at cosine rank ≤ 3 of 38 — de-confounded, not
  buried (the engine must re-rank it to the top, not first re-find it).

## Status

This version is the input to the **blind human D-B pass** (which adjudicates the 216 labels on
THIS text), then the single reconciliation regeneration, then freeze. **No merge, no freeze
here.** Gold remains gitignored/private.
