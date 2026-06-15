# inv-mystery-redhood — Dataset Card

**Family:** investigative · **Domain:** Multi-source reasoning / evidence grounding

## Scenario

A fictional 1842 village investigation (the "Red Hood" case). Thirty heterogeneous sources — private letters, witness statements, ranger logs, guard reports, medical reports, receipts, rumors, and irrelevant notices — must be combined to reconstruct what happened to Marta Bellandi and identify the most likely culprit. The case is engineered to test whether a system can do more than summarize: it must reconstruct an event timeline, link entity aliases, ground a conclusion in evidence, detect weak contradictions, reject a rumor-driven false lead, and discard noise.

This is the corpus with the richest *native* ground truth, so its qrels are derived deterministically rather than hand-authored.

## Why it is challenging

- **Culprit inference under uncertainty.** The expected answer (Subject B / "Bruno") must be held at calibrated confidence (~0.82), never absolute certainty.
- **A false lead.** Rinaldo Marchi has motive but no physical evidence; the gold requires separating motive from evidence.
- **Weak contradictions.** Two timing tensions (a "voice" heard after the estimated assault window; a ranger's ledger conflict) must be detected but resolved as non-fatal via source-reliability weighting.
- **Noise rejection.** Three on-topic-looking notices are pure distractors.

## Contents

| | |
|---|---|
| Documents | 30 (all Markdown) |
| Queries | 8 (4 hard, 3 medium, 1 easy) |
| Qrels | 51 graded judgments (0–3) |
| Raw size | 120 KB |

The eight queries each target a distinct reasoning task: culprit identification, timeline reconstruction, evidence grounding, contradiction detection, false-lead rejection, entity linking, noise rejection, and causal reasoning.

## Derivation (reproducible from native ground truth)

The gold layer is mapped deterministically from the case's native ground-truth files:

- **`queries.jsonl`** ← the eight `test_question_gold_answers`.
- **`qrels/test.tsv`** ← `required_sources` → 3, `optional_sources` → 2; timeline query maps gold events to supporting sources (must-include events → 3, others → 2); contradiction query takes all sources involved in each gold contradiction → 3; noise-rejection query takes the gold noise sources → 3.

Each `corpus.jsonl` `_id` equals the native `source_id` (filename without extension), so the mapping is one-to-one.

## Example query

- **q01** (hard) — culprit identification → top judged docs `source_008_informal_note_clara_birches` (3), `source_010_witness_nino_dark_shape` (3), `source_016_guard_report_first_inspection` (3), `source_017_medical_report_marta` (3).

## Provenance & format

The 30 canonical sources live in `raw_toy_sized/` as `source_*.md`; `corpus.jsonl` is derived from `raw_toy_sized/`. (This corpus uses a per-tier `raw_<tier>_sized/` layout to host the scaled stress tiers below.) This is a fictional scenario.

## Scaled stress tiers

The 30-document toy case is extended into larger "needle-in-a-haystack" tiers that keep the **same 30 canonical sources verbatim** (the gold in `qrels/test.tsv` references only those) while growing the surrounding haystack. Each larger tier adds:

- **distractors** — high-similarity, epistemically-disqualified traps (other canids/dark shapes in other places/dates, other debt quarrels, entity collisions like a *different* "Marta"/"Bruno", other honey/tincture parcels, other "rough voice" anecdotes) that a similarity retriever pulls but an epistemically-grounded system should reject;
- **noise** — pure off-topic, era-coherent village paperwork (markets, weather, school, recipes, taxes, harvest).

Noise share rises with size (cap ~57%), distractors grow in number, and all timestamps stay internally coherent (retrospective reports carry `TIMESTAMP ≥ event time`; notices precede their announced event).

| Tier | Folder / archive | Documents | Noise | Distractors | Format |
|---|---|---|---|---|---|
| toy | `raw_toy_sized/` | 30 | — | — | `.md` (in Git) |
| medium | `raw_medium_sized/` | 300 | 25% | 35% | `.md` (in Git) |
| big | `raw_big_sized/` | 3,000 | 35% | 40% | `.md` (in Git) |
| very big | `raw_very_big_sized.tar.zst` | 30,000 | 45% | 42% | LFS archive |
| huge | `raw_huge_sized.tar.zst` | 300,000 | 52% | 43% | LFS archive |
| very huge | `raw_very_huge_sized.tar.zst` | 3,000,000 | 57% | 42% | LFS archive (JSONL) |

The three largest tiers are shipped as Git-LFS `*.tar.zst` archives (and mirrored as a HuggingFace dataset); their extracted folders are git-ignored. Extract with `zstd -dc <file>.tar.zst | tar -xf -`.

All tiers are reproducible byte-for-byte via [`_generator/gen_redhood.py`](_generator/gen_redhood.py) (`python3 _generator/gen_redhood.py <tier>`); per-tier composition manifests live in `_generator/manifests/`.
