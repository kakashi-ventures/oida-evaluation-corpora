# Core-Migration Plan v2 — Phased Cutover (Horizon → Unifi)

**Date:** March 14, 2026
**Document type:** Migration plan — controlled document MIG-PLAN-002, version 2
**Author:** Greg Olsen, CIO
**Status header (as printed):** ACTIVE — **supersedes Migration Plan v1 (big-bang single-weekend cutover, February 2026)**

---

## 1. Purpose

Establish the remediated, **phased** cutover approach for the remaining core domains, replacing the big-bang single-weekend plan. The change responds to the transaction-monitoring data-delivery gap that the January big-bang cutover produced (MRA Finding 1) and the decision of the March 10 risk review, confirmed by steering on March 20.

## 2. Approach (v2 — in force)

**Phased cutover.** The remaining domains migrate in sequence rather than in a single weekend:

- **Phase 1:** deposits/payments.
- **Phase 2:** lending.
- **Phase 3:** data/reporting layer.

After **each** phase:

- A **validation window** confirms complete and correctly formatted data delivery to all downstream consumers, with **explicit validation of the transaction-monitoring data feed** before the next phase proceeds.
- The **legacy Horizon interface is kept available as a fallback** for the migrated domain during the phase, so a feed problem does not become a monitoring-coverage gap.

Completion is targeted across Q2 rather than a single March weekend.

## 3. Rationale

Phasing trades speed and dual-running cost for the elimination of single-event, no-fallback risk. During an open MRA whose Finding 1 is a monitoring-coverage gap from a big-bang cutover, the Bank cannot accept the risk of repeating that gap. Validating the monitoring feed after each phase, with a legacy fallback, directly prevents a recurrence.

## 4. Monitoring-feed checkpoints

Each phase's validation window includes a Financial Crimes sign-off that the monitoring feed is complete for the migrated domain before decommissioning the legacy fallback for that domain. No phase proceeds without that sign-off.

## 5. Supersession

This v2 plan **supersedes Migration Plan v1 (big-bang single-weekend cutover)** in its entirety. The big-bang approach is no longer the plan.
