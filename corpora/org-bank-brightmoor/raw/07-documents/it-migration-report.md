# Core-Migration Post-Cutover Report — Horizon → Unifi (General Ledger & Customer Master)

**Date:** February 16, 2026
**Document type:** IT post-implementation report (Office of the CIO)
**Author:** Greg Olsen, CIO
**Scope:** January cutover of the general-ledger and customer-master domains
**Status:** FINAL — authoritative IT record of the January cutover reconciliation

---

## 1. Summary

The January cutover of the general-ledger and customer-master domains from the legacy Horizon core to the Unifi core completed over the planned weekend. **Post-cutover reconciliation is clean: there was no data loss.** All customer balances, account records, and ledger postings reconcile between Horizon and Unifi. From a core-banking accounting standpoint, the migration was successful and complete.

## 2. Reconciliation results

| Reconciliation | Result |
|---|---|
| Customer balances (Horizon vs Unifi) | Tie out to the penny — 0 exceptions |
| Account master records | 100% matched |
| General-ledger postings (cutover window) | Balanced — 0 unexplained variances |
| Customer count | Matched |

We are confident stating, for the core ledger, **no data loss occurred** during the cutover.

## 3. Stabilization notes

The post-cutover stabilization period saw the usual interface re-pointing work as downstream consumers reconnected to Unifi extracts. Some downstream feeds required reconfiguration to the new interface specification during stabilization. These are downstream-consumer integration items and are tracked separately by the consuming teams; they do not affect the core-ledger reconciliation result above, which is the subject of this report.

## 4. Scope note

This report covers the **core-ledger reconciliation** for the January cutover. It does **not** assess the completeness of data delivery to any specific downstream system (such as the transaction-monitoring data layer); downstream feed completeness is the responsibility of, and is being reviewed by, the consuming teams. (See Financial Crimes' separate review of the monitoring data feed for that scope; this report should not be read as a statement about monitoring-feed completeness, which is a different reconciliation against different controls.)

## 5. Conclusion

The January core cutover reconciled cleanly with no core data loss. Remaining stabilization items are downstream-integration tasks owned by the consuming teams.
