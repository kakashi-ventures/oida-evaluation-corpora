# org-offshore-wind-galewright — Dataset Card

**Family:** organizational · **Domain:** Energy / offshore-wind project development
**Status:** ⚠️ **DRAFT — Phase-4 candidate, awaiting human sign-off.** Authored blind to the engine (see `DESIGN.md`). Not yet wired into the harness.

## Scenario

Galewright Energy develops **Marrowbank Offshore Wind**, an approximately 700 MW fixed-bottom wind farm off the fictional Calder coast, from early development through **Final Investment Decision (FID)**. The corpus follows the project end to end: the Crown Estate seabed lease, the consent (DCO/EIA) route, the wind resource assessment, turbine selection, export-cable landfall siting, grid interconnection, the environmental impact assessment (especially seabird collision), community and stakeholder consultation (including organised opposition), the financial case, and the FID itself — across scope documents, internal and external email, a project chat, meeting minutes, market context, formal documents, and a calendar.

## Why it is challenging

- **A project that supersedes its own decisions.** The binding turbine moves from the AT-12 (58 turbines) to the AT-15 (47 turbines); the cable landfall moves from Saltmarsh Point to Drover's Gap; the COD moves from 2029 to 2030; the grid connection moves from Calder (2031) to Marrow Bank (2030). Each "current" answer is only correct relative to which decision is now in force — four clean supersessions.
- **A deliberate, unreconciled energy disagreement.** The resource consultant assesses a **48% capacity factor / ~2,950 GWh/year**; the finance model deliberately underwrites a conservative **42% / ~2,580 GWh/year**. The gap is a prudence margin, not an error — and it is never collapsed to a single number.
- **A contested scientific number.** The draft EIA assesses **~120 kittiwake collisions/year (low significance)**; the seabird NGO submits **~600/year (high significance)** and objects. The 5–6× gap is driven entirely by the avoidance-rate assumption and is unresolved.
- **A stale figure that outlives its estimate.** An October board deck cites **CAPEX £2.4bn**; the FID memo commits **£2.65bn**. The deck is superseded — but it is read one way as a contradiction side (consistency) and another way as a stale trap (current-figure).
- **A retracted promise → an abstention.** A community brief promises **1,200 local jobs**; that figure is formally **withdrawn** as unsubstantiated, leaving only ~300 construction FTE substantiated and operational jobs explicitly uncertain. "Will the promised jobs be delivered?" is therefore **not verifiable** (an NEI/abstention target).
- **A stale interim tracker.** A consent-status snapshot says "turbine TBC, landfall TBC, DCO in preparation" long after those were decided — a leakage trap for current-status queries.

## Contents

| | |
|---|---|
| Documents | 37 (35 Markdown, 2 JSON — a Teams chat export and a calendar) |
| Queries | 17 (2 easy, 11 medium, 4 hard) |
| Qrels | 65 graded judgments (0–3) |
| Planted relations | 3 contradictions · 4 supersessions · 1 retraction · 4 traps · 2 stable-knowledge queries · 1 NEI/abstention |

## Example queries

- **q02** (hard) — energy-yield conflict → `02-subject/resource-assessment-aep` (3, 48%/2,950) and `02-subject/financial-model-summary` (3, 42%/2,580); both sides must be retrieved.
- **q07** (hard) — "will the promised local jobs be delivered?" → the corpus does **not** support a yes (gold stance NEI); `07-documents/community-brief-jobs-corrected` (3) and `05-meetings/meeting-004-fid-board` (2) decline the claim, and `07-documents/community-brief-jobs-original` (the retracted 1,200 figure) is a score-0 trap.
- **q01** (medium) — current vs superseded turbine → `07-documents/turbine-selection-memo-at15` (3, binding AT-15), `07-documents/layout-plan-at12-initial` (2, superseded AT-12).
- **q11** (easy) — durable seabed-lease terms → `01-scope/crown-estate-seabed-lease` (3), the oldest document in the corpus (tests freshness-overbias).

## Provenance & format

The 8-category source tree lives in `raw/` (`01-scope` … `08-agenda`); `corpus.jsonl` is generated from it by `scripts/build_corpus.py`. The gold for the adversarial/stance/temporal layers lives in the gitignored `experiments/annotations/` tree; `DESIGN.md` in this directory documents that gold for review. See [`../../docs/format.md`](../../docs/format.md) and [`../../docs/relevance-guidelines.md`](../../docs/relevance-guidelines.md). This is a synthetic scenario; any resemblance to real people, companies, projects, or organisations is coincidental. Named external frameworks (The Crown Estate seabed lease, the Development Consent Order regime, the GB Grid Code, the System Operator's connection offers, the Contract for Difference) are used as realistic context only.
