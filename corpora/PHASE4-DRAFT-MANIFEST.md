# Phase-4 Fresh Corpora — DRAFT Manifest (for human validation)

> ⚠️ **DRAFT FOR HUMAN VALIDATION — do NOT seal as the Phase-4 benchmark until signed off.**
> These are **fresh / unseen** organizational corpora authored for the OIDA Phase-4 real
> test. They are deliberately *not* wired into the harness and the gold has *not* been
> tuned against any engine output. Each corpus ships a `DESIGN.md` dossier documenting its
> planted ground truth; this manifest is the cross-corpus summary.

## Why these exist

The five existing corpora (`org-consulting-clearpath`, `org-iot-fireglass`,
`org-vc-vertexminds`, `inv-mystery-redhood`, `inv-ashford-mystery`) are a **burned/seen dev
set** — usable only as regression sanity, never for a pass/fail claim. Phase-4 pass/fail must
rest on **fresh** corpora. These three new ORG corpora (org is the thesis focus) are that
fresh set: distinct industries, none a variation of the burned five.

## Integrity / blindness statement (the property the paper's numbers rest on)

1. **Authored blind to the engine.** Every document *and* every ground-truth annotation was
   written without running the corpus through OIDA (or any retrieval system) and without
   inspecting how any system scores them. No relation was iterated against engine output.
   "Teaching to the test" — tuning a corpus until the SUT looks good — was structurally
   impossible because the SUT was never in the loop.
2. **Naturalistic, not contrived.** Contradictions, supersessions, temporal change, and
   stance are woven into believable organizational material (memos, emails, meeting
   transcripts, dashboards, vendor notices) and surfaced *in-world* — a later document states
   a different number, a colleague rebuts another, a memo declares it "supersedes" an
   earlier one — not flagged with neon labels.
3. **Defensible gold.** Every planted relation is annotated with the document pair(s), the
   relation type, and a rationale (see each `DESIGN.md` and the machine-readable gold).
4. **Not yet wired in.** The corpora are kept off the harness's default corpus lists so they
   cannot be accidentally burned before pre-registration (see "Pre-registration wiring").

## The three corpora

| Corpus | Industry / scenario | Docs | Queries | Qrels | Contra · Supers · Traps · NEI · Stable-q |
|---|---|---|---|---|---|
| `org-hospital-stillwater` | Healthcare delivery — a hospital "Sepsis Pathway 2.0" clinical-quality initiative after a sentinel event | 32 | 17 | 75 | 3 · 4 · 3 · 1 · 7 |
| `org-offshore-wind-galewright` | Energy / infrastructure — an offshore wind farm ("Marrowbank") from siting to Final Investment Decision | 37 | 17 | 65 | 3 · 4 · 4 · 1 · 2 |
| `org-bank-brightmoor` | Financial services — a regional bank's AML/BSA remediation + core-banking migration | 36 | 17 | 61 | 3 · 3 · 4 · 1 · 3 |

*All counts above are final and verified — `scripts/validate.py` reports OK on each corpus and
an independent cross-consistency check passes every coverage gate.* **Grand total across the
three fresh corpora: 105 documents · 51 queries · 201 qrels · 9 contradictions · 11
supersessions · 11 traps · stance-evaluable 8 SUPPORTS / 8 CONTRADICTS / 3 NEI.** Lifecycle
across the set exercises all seven states (CANONICAL, ACTIVE, PROVISIONAL, STALE, SUPERSEDED,
ARCHIVED, RETRACTED).

### What each corpus tests (epistemic relations)

- **org-hospital-stillwater** — protocol **v1→v2 supersession** (3-hr → stratified 1-hr-for-shock
  antibiotic timing); a **three-way compliance contradiction** (62% manual / 84% EHR / ~70%
  nursing, never reconciled); a **death-count contradiction** (final RCA 2 vs board slide 3);
  an **evidence-basis stance split** (universal 1-hr mandate vs stewardship); an **unverified
  mortality claim (NEI/abstention)**; a **device-recall temporal chain**; two **stable
  references** (CMS SEP-1, staffing policy) older than the fresh pilot docs (freshness-overbias).
- **org-offshore-wind-galewright** — **turbine, landfall, programme/COD, and grid-offer
  supersessions**; **energy-yield, bird-collision, and CAPEX contradictions**; a **RETRACTED
  jobs claim** ("1,200 local jobs" withdrawn) feeding an **NEI** on promised benefits;
  pro/anti **stakeholder stance**; **STALE** consent tracker; stable **seabed lease** and
  **grid code** references.
- **org-bank-brightmoor** — **monitoring-threshold, migration-approach, and governance
  supersessions**; **alert-backlog, data-loss, and false-positive contradictions**; a **vendor
  40%-reduction claim (NEI)** vs internal validation (~15%); a **RETRACTED** preliminary triage
  finding; threshold **stance split** (Compliance vs Retail); **STALE** backlog snapshot;
  stable **BSA/AML regulation** and **risk-appetite** references.

Across the three, the lifecycle vocabulary is exercised in full: CANONICAL, ACTIVE,
PROVISIONAL, STALE, SUPERSEDED, ARCHIVED, RETRACTED.

## What is committed vs. gitignored

- **Committed (in this PR):** each `corpora/<id>/` — `raw/`, generated `corpus.jsonl`,
  `queries.jsonl`, `qrels/test.tsv`, `README.md` (dataset card), `DESIGN.md` (ground-truth
  dossier / review surface), plus this manifest.
- **Gitignored (local, harness-ready, NOT in the PR):** the five gold annotation files per
  corpus under `experiments/annotations/{contra_sets,supersession_chains,lifecycle,stance_gold,temporal_queries}/<id>.json`.
  This mirrors the repo's existing privacy model (qrels are public; the epistemic answer key
  stays private so it cannot leak into an engine-tuning loop). The `DESIGN.md` files render
  that gold in human-readable form for review — **decide before any public dataset release on
  `main` whether to keep the DESIGN dossiers private/redacted.**

## Human-validation checklist (per corpus, before sealing)

1. A domain expert confirms each planted relation is **clinically/technically/financially
   plausible** and not contrived.
2. Confirm each **contradiction** is a genuine, unresolved conflict (both sides retrievable),
   not editorial imprecision — note the flagged judgment calls in each `DESIGN.md`.
3. Confirm each **supersession** binding doc is truly the current authority and the superseded
   doc is genuinely obsolete.
4. Confirm each **NEI/abstention** query is genuinely unsettleable from the corpus (a correct
   system should abstain, not commit).
5. Spot-check **qrels** grades against `docs/relevance-guidelines.md` (score-3 fully answers;
   score-0 traps are plausible-but-wrong).
6. Confirm **no annotation was influenced by engine output** (it was not, by construction).
7. Decide the **privacy posture** of the DESIGN dossiers and the gitignored gold for Phase-4.

## Pre-registration wiring (NOT done here — a deliberate Phase-4 step)

These corpora are authored in the canonical format and pass `scripts/validate.py`, but are
**not** registered with the harness, so the regression run and the layer scorers ignore them
by default. After human sign-off and Phase-4 threshold pre-registration, the team must:

1. Add the three ids to `experiments/scripts/eval_common.py::ALL_CORPORA` (this also adds the
   `org-*` ones to `ORG_CORPORA`, which Layer-4 temporal filters on).
2. Add per-corpus routing to `experiments/scripts/run_regression.py::OIDA_CORE_PROJECT_IDS`
   and the matching `OIDA_CORE_KEY_<SLUG>` entries in `.env`.
3. (Optional) Add `CUTOFFS["<id>"]` entries in `06_eval_temporal.py` for the per-cutoff
   temporal diagnostic (suggested cutoffs are in each `DESIGN.md`).
4. Ensure the gitignored gold annotation files are present under `experiments/annotations/`
   (they already are, locally).

Until then, individual layers can be exercised by passing a corpus id explicitly (e.g.
`04_eval_adversarial.py org-hospital-stillwater`), **except** Layer-4 temporal, which filters
to `ORG_CORPORA` and therefore requires step 1.

**Do not lock thresholds here.** Threshold pre-registration is a separate Phase-4 step.

## PR base

This work branches off `roadmap/integration` (which carries the corpus tooling and harness);
`main` is a restricted *published-dataset* view (corpora/ + docs/ only, no `scripts/`), so the
DRAFT PR targets `roadmap/integration`. Retarget if the team prefers a different base.
