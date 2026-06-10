# EXPERIMENT_PLAN_v2 — Phase-4 pre-registration (P4-S2) · **LOCKED**

**Status:** LOCKED pre-registration draft for overviewer review. **Δ thresholds are PLACEHOLDERS** to be filled from the **D3 pilot** variance/effect-size estimate — nothing else is open. **Do NOT run anything against this plan until the Δ are filled and the plan is signed.** Supersedes the Phase-4 portion of `experiments/EXPERIMENT_PLAN.md` (v1).

**Rev 2.1 — 2026-06-10, pre-lock amendments** (made while PR #19 is unmerged; the lock is the merge):
run-1 scope corrected to **recency-only** per **DR-P4-001 §D-A** (contradiction stratum → descriptive-only,
the F-2-CONTRA gate removed from run-1 and deferred); **B-recency-naive** registered as a descriptive
comparator; the trap gate gains a **per-trap-class** breakdown; **per-stratum recall@{10,20,50}** added to
the registered report shape; the **F-TEMP-1 comparator scope** made explicit (verdict vs B0 only).

**Grounding:** roadmap Phase-4 **CONSOLIDATED DECISIONS** (P0 + D1–D5) and the **RATIFICATION LOG** (2026-06-08: **D1 RATIFIED** by Alberto Trivero + Federico co-IC → P4-S2 unblocked). Prerequisites (D5): edge-graph freeze tooling, edge-materialization check (P4-S1), P2-S9 oracle.

---

## 0. What v2 re-registers, and why (the integrity reset)
v1 pre-registered the Phase-4 hypotheses but two things invalidated it; v2 fixes both **before** any number is produced:
1. **Mode drift (flagged, §6):** v1 §3 registered the **v1 probe** mode (`probe_v1:true, top_k=20`), but the adapter/run actually shipped **v0** (`regime_adjusted_score`, `tauBind=0.2/tauFallback=0.1` — v1 §6). The registered mode ≠ the run mode → the v1 pre-registration is **void**. v2 pins the mode + the exact scoring path + the engine commit SHA so the registered mode **is** the run mode.
2. **Mis-scoped F-conditions:** v1's temporal/contradiction gates were absolute thresholds or vs-other-systems; Phase-3 showed the thesis is **query-conditional**, so v2 re-registers them as **per-stratum lifts of the signal over the signal-off baseline** (P0), with Δ from the pilot.

---

## 1. MODE — locked (D1: Option **B refined**)
**Test the epistemic/temporal signals AS the ranker** — NOT the broken v0 default (A), NOT the v1 probe path (C). Signals **modulate field/mass INSIDE the single KGE** — never a parallel ranker (invariant: **KGE = sole ranker**; P3-S2's additive `recency_adjusted_score` already complies). Ratified by Alberto (engine architecture).

- **Run-1 (this pre-registration):** **recency-as-ranker ONLY** (`recency_adjusted_score`, P3-S2) — per **DR-P4-001 §D-A**. Gated stratum: **temporal** (gate: **F-TEMP-1**, §4). The **contradiction stratum is measured DESCRIPTIVE-ONLY** (§4b): no gate, no claim. The two contradiction mechanisms are distinct and only one is in the ranking path: the **`CONTRADICTS` edge graph** is consumed by the subgraph solver (**membership** — which docs enter the scored subgraph), while the **`contradictionExposure` scalar (P2-S4) was never integrated into ranking** — so run-1 has no contradiction ranker to gate.
- **Contradiction lift-gate (deferred):** a gated F-2-CONTRA exists only if/when a contradiction signal actually enters the ranking path; it is re-registered then, in its own separately-scoped pre-registration with its own Δ — not in run-1.
- **Run-2 (appendix, separate pre-registration):** the **authority×relevance redesign** (finding #3, NOT yet built) on the **same** corpus. Stratum: **authority**. Gates: **F-AUTH-\*** — to be written with Alberto; **not folded into run-1** ("change one thing").

**Pinned at run time (closes the v1 drift):** engine **commit SHA** (the prod-path **Postgres** engine on staging); the **`score_field`** carrying each signal; `tauBind/tauFallback`; `top_k`; the **frozen-graph snapshot id** (edge-freeze drain-to-quiescence — D5 #1). The run aborts if the deployed SHA ≠ the registered SHA.

---

## 2. Hypothesis — **STRATIFIED, per-stratum success** (P0)
Phase-3 did not falsify the thesis, it **narrowed** it (recency helps temporal queries *when the corpus has freshest=current*; authority helps when the authoritative doc is relevant and **hurts** when not; the plain-relevance gap is **recall/embedding**, not ranking). So:

> **Defended claim:** *"the epistemic signals improve ranking on the strata they target, given a corpus where the signal is informative."*

- Success is judged **PER-STRATUM**: run-1's gated stratum is **temporal** (F-TEMP-1); the **contradiction stratum is reported descriptively** (§4b, no F-condition); **authority** is run-2.
- **Aggregate NDCG@10 is REPORTED but is NOT the headline** — a per-stratum win can be masked or faked by aggregate movement; the headline is the stratum verdicts.

---

## 3. Strata, baselines, and the paired/frozen design
- **Strata (from P4-S1 query tags):** `temporal` (R1), `contradiction` (R4 — descriptive in run-1, §4b), `authority` (R3, run-2). ≥40–50 queries/stratum (D3 floor; the exact N is the pilot's re-power output — placeholder T below).
- **Baseline = the SAME engine with the signal OFF (B0 / plain cosine).** Mode B is a **self-comparison** (signal-on vs signal-off), not vs other systems — so the gate isolates the signal's contribution, not embedding/recall differences.
  - B0 = similarity-only; signal-on(recency) = `recency_adjusted_score`. (There is no signal-on(contradiction) arm in run-1 — see §1.)
- **B-recency-naive (registered descriptive comparator):** `cosine × exp(−λ·age)` — plain similarity multiplied by an exponential date-decay (λ declared at lock, before any measured run). Computed **paired on the same frozen graph** and reported next to F-TEMP-1. **No threshold, no pass/fail:** it answers *"does the epistemic recency signal beat a naive date prior?"* descriptively. **The locked F-TEMP-1 verdict is vs B0 only** (§4).
- **Paired on a FROZEN graph (D3 + edge-freeze):** signal-on and signal-off are scored over the **same drained-to-quiescence frozen graph**, **paired by query**; the per-stratum lift uses a **paired** statistic (so reproducibility = the edge-freeze guarantee; pairing beats raising N for the small Δ≈0.02–0.07). The frozen graph + the K-ingest variance band come from the edge-freeze harness (`quiescence_drain`); per **R6** the contests must be authored so the signal margin ≫ the measured ~1e-4 jitter (0 reorderings).

---

## 4. Locked F-conditions — **run-1**
Δ values are **[PILOT-Δ]** placeholders (filled from the D3 pilot variance estimate; the full-run pre-registration WAITS for the pilot). Metric definitions inherit v1 §5 unless noted.

| F-condition | stratum | statistic (signal-on − signal-off, paired) | threshold | on FAIL |
|---|---|---|---|---|
| **F-TEMP-1** (re-registered) | temporal | `TemporalNDCG@10(recency) − TemporalNDCG@10(B0_cosine)` (T6 shifted-gain) | **≥ [PILOT-Δ_temporal]** | recency **demoted to a non-default diagnostic** (not the default ranker) |
| **F-2-TRAP** (re-registered) | adversarial (R5, n≥80) | proportional gate — see §5 | **rate ≤ [τ_trap], 95% CI** | reported as a trap-rejection failure (not retuned) |

**Comparator scope (explicit):** the F-TEMP-1 pass/fail verdict is determined **solely** by the B0
comparison above. The B-recency-naive comparison (§3) is reported alongside it, paired, with no
threshold — it can contextualize the verdict but never decide it.

### 4b. Contradiction stratum — DESCRIPTIVE ONLY (no gate, no claim)
Registered report quantities for the contradiction stratum, computed on the same frozen graph:
- **ContraRecall@10** (both members of a contradiction set retrieved), reported with the K-ingest
  variance band.
- **Membership effect (descriptive):** the contribution of `CONTRADICTS`-edge membership to subgraph
  composition — how often contradiction-set docs enter the scored subgraph vs comparable non-members.

No F-condition, no Δ, and no claim attach to this stratum in run-1; the claim-wording template (§7)
may not cite it as a proven signal. The gated version is deferred per §1.

**Mapping vs v1 (so the drift is auditable):**
- v1 **F-TEMP-1** (`CSA@10 ≥ 0.80`, absolute) and v1 **F-TEMP-7** (`TemporalNDCG@10 − B0 ≥ 0.10`, lift) → collapse into v2 **F-TEMP-1** = the **per-stratum recency lift vs B0** (the Δ is now pilot-derived, not the legacy 0.10). v1's absolute CSA@10 and F-TEMP-2/4/5/6 are **retained as reported diagnostics**, not the run-1 headline.
- v1 **F-2-CONTRA** (`− max_baseline ≥ 0.15`, vs other systems) → **retired from run-1**: the contradiction stratum is descriptive-only (§4b) because no contradiction signal is in the ranking path (§1). A lift-gate returns only in the deferred, separately-scoped pre-registration.
- v1 **F-1-PARITY**, **F-ABSTAIN-1..4**: reported (Layer-1 / Layer-3 context), **not** run-1 headline gates.

**Run-2 (appendix):** **F-AUTH-\*** (authority×relevance) — definitions + Δ to be written with Alberto in a separate pre-registration before run-2; the authority stratum is built into the corpus now but **not scored in run-1**.

---

## 5. Trap gate — replaces min-of-3 (robust at n≥80, with CI)
v1's `F-2-TRAP` used a **min-of-3** decision on **n=8** trap pairs → pure noise (CIs overlap, McNemar p=1.00 — roadmap §diagnostic). With the P4-S1 floor of **≥80 trap pairs**, v2 registers a **proportional** gate:

- **Metric:** `TrapInTop5_rate = #(query, trap_doc) with trap_doc in top-5 / #(query, trap_doc) pairs` (n ≥ 80).
- **Interval:** a **95% Wilson** confidence interval on the rate (robust for proportions at this n; report the interval, not just the point).
- **Gate (locked form):** **PASS iff the rate ≤ [τ_trap]** with the 95% CI reported; the **conservative variant** (register one, do not switch post-hoc) is **PASS iff the upper 95% CI bound ≤ [τ_trap]**. `[τ_trap]` is locked at authoring (pilot-informed); the **min-of-3 rule is retired**.
- **Per-trap-class breakdown (registered):** the same rate + 95% Wilson CI is also computed **per trap class** — **false-cue / superseded / round-up** — and reported next to the pooled rate. **The locked pass/fail verdict is the POOLED gate** (per-class n ≈ 25–30 at the floor is too small to gate honestly); a class whose CI **lower bound** exceeds `[τ_trap]` is flagged in the report as a **class-level trap failure** (mandatory to report, descriptive — not the headline gate).

---

## 6. Prior pre-registration drift — **flagged** (do not repeat)
- **What happened:** v1 §3 registered OIDA mode = **v1 probe** (`probe_v1:true, top_k=20`); v1 §6 + the executed run used **v0** (`regime_adjusted_score`). The plan and the run disagreed on the scored path → the v1 Phase-4 pre-registration is **void**.
- **Why it matters:** an F-condition only constrains if the mode it was registered against is the mode that runs. A post-hoc mode swap is exactly the self-deception the discipline forbids.
- **v2 fix:** §1 pins the **mode + `score_field` + engine commit SHA + frozen-graph snapshot**, and the harness **aborts** if the deployed SHA ≠ the registered SHA. The registered mode **is** the run mode by construction.

---

## 7. Integrity / discipline (binding)
- **Do NOT adjust thresholds, Δ, strata, or metrics post-hoc.** The Δ are filled **once** from the D3 pilot, the plan is **signed**, then it is frozen.
- **A failed pre-registered gate is a NULL RESULT** — recorded as such (the signal is demoted / not-promoted per §4), **never** re-tuned to pass. F-TEMP-1 is allowed to let recency *lose*.
- **The corpus is frozen** (P4-S1, no post-hoc edits to make a gate pass) and **the gold stays private/gitignored** until this run.
- **The graph is frozen** (edge-freeze drain-to-quiescence) and the run reports a **per-stratum verdict + per-stratum recall@{10,20,50} (R2.2) + aggregate NDCG + the K-ingest variance band**, never a bare point NDCG. Recall@{10,20,50} per stratum is part of the **registered report shape**, not an optional extra.
- **Paired, self-comparison** (signal-on vs signal-off, same frozen graph) — isolates the signal from recall/embedding confounds.

---

## 8. PLACEHOLDERS to fill from the D3 pilot (the only open values)
| placeholder | source | used by |
|---|---|---|
| `[PILOT-Δ_temporal]` | pilot variance + effect size on the temporal stratum | F-TEMP-1 |
| `[λ]` (naive decay rate) | declared at lock (corpus date-span informed, before any measured run) | B-recency-naive (§3) |
| `[τ_trap]` | pilot trap-rejection rate (locked at authoring) | F-2-TRAP (pooled + per-class report) |
| `T` (N/stratum) | pilot re-power (≥40–50/stratum floor) | §2/§3 power |
| `K` (reorderings retrieves) | edge-freeze pilot (R6.2) | frozen-graph reproducibility check |

## 9. Out of scope (downstream)
- **Run-2 `F-AUTH-*`** (authority×relevance) — separate pre-registration with Alberto.
- **The contradiction lift-gate** — deferred to a separate pre-registration, contingent on a contradiction signal actually entering the ranking path (§1). Run-1 reports the stratum descriptively (§4b).
- The **recall/embedding** fix — a parallel engine workstream. (Measuring recall is **in** scope: per-stratum recall@{10,20,50} is part of the registered report shape, §7 — only the fix is downstream.)
- The OIDA-vs-baselines comparison (other systems) — orthogonal to the mode-B self-comparison that carries the thesis.

> **Review note:** the two load-bearing choices are **mode B + the per-stratum lift framing** (P0/D1 — what makes a stratum win meaningful) and **the paired/frozen design** (D3 + edge-freeze — what makes the small Δ reproducible). Everything else is mechanical. The Δ are deliberately left blank — filling them is the pilot's job, and locking them before the pilot would be the same self-deception this plan exists to prevent.
