# Core-Migration Plan v1 — Big-Bang Cutover (Horizon → Unifi)

**Date:** February 1, 2026
**Document type:** Migration plan — controlled document MIG-PLAN-002, version 1
**Author:** Greg Olsen, CIO
**Status:** SUPERSEDED by Migration Plan v2 (phased cutover), March 14, 2026. Retained for provenance. **This big-bang approach is no longer the plan.**

---

> **Status note:** This v1 plan set out the **big-bang single-weekend cutover** for the remaining core domains. Following the March 10 migration risk review and the steering decision of March 20, the approach was changed to a **phased cutover**; this plan is **superseded by Migration Plan v2 (March 14, 2026)**. Retained only to record the prior approach.

## 1. Scope

Cutover of the remaining core domains — deposits/payments, lending, and the data/reporting layer — from legacy Horizon to Unifi. (The general ledger and customer master cut over in January.)

## 2. Approach (v1 — superseded)

**Big-bang single-weekend cutover.** All remaining domains migrate together over one cutover weekend, targeted for late March. At go-live, all downstream consumers — including the transaction-monitoring data layer — re-point to Unifi extracts simultaneously. The legacy Horizon environment is decommissioned shortly after a brief verification window.

## 3. Rationale (as written)

A single-weekend cutover minimizes the duration of dual-running cost and complexity, and avoids a prolonged period of operating two cores in parallel ("rip the band-aid off once"). It is faster and cheaper than a phased migration **if the cutover executes cleanly**.

## 4. Known risk (flagged)

A big-bang cutover concentrates risk into one event with limited fallback. The January general-ledger/customer-master cutover (also executed as a weekend event) produced a transaction-monitoring data-delivery gap during stabilization. Repeating a big-bang for the remaining domains would re-run that monitoring-coverage risk. (This risk is the reason the approach was subsequently changed — see Migration Plan v2.)

## 5. Disposition

Superseded by Migration Plan v2 (phased cutover), March 14, 2026, per the March 10 risk review and the March 20 steering decision.
