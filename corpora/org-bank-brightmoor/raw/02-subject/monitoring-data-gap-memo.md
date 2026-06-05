# Transaction-Monitoring Data Gap During Core Cutover — Compliance Memo

**Date:** February 18, 2026
**Document type:** Compliance findings memo (Financial Crimes / AML)
**Prepared by:** Priya Nair, Head of Financial Crimes
**To:** Dana Whitfield (CCO/BSA Officer); Marcus Hale (CRO); Greg Olsen (CIO)
**Status:** Current Compliance position on the migration-period monitoring gap

---

## Summary

This memo documents what Financial Crimes has established about transaction-monitoring coverage during the core-banking cutover. Our finding, stated plainly: **for approximately three weeks during and after the January core cutover, the transaction-monitoring system did not receive complete transaction data, and monitoring alerts were not generated on all covered activity during that window.** In other words, there is a real monitoring gap, and it is the gap the MRA's Finding 1 anticipated.

## What we found

When we reconciled the alerts the Sentinel platform *generated* during the cutover window against the transaction volumes the business actually processed, the alert counts are anomalously low for the period of roughly **three weeks** beginning at the January cutover. Specifically:

- Several transaction feeds from the new Unifi core did not post to the monitoring data layer in the expected format during the cutover stabilization period; a subset failed silently (they did not error in a way that raised an operational alarm, so the absence was not noticed in real time).
- For that ~3-week window, scenarios that should have fired on the affected feeds did not. We cannot assert that *no* suspicious activity went unalerted; we can only assert that **coverage was incomplete and we have to treat the window as a gap** and re-run monitoring over it.

## On the "no data loss" characterization

We are aware that the IT post-cutover report concludes the migration reconciliation was **clean with no data loss**. We do not dispute that the *core ledger* reconciled — customer balances and postings tie out, and from a core-accounting standpoint nothing was lost. **But "no data loss in the core ledger" is not the same as "complete data delivery to the monitoring system."** The ledger can be whole while the monitoring feed was incomplete for a period; those are different reconciliations against different controls. From an AML-coverage standpoint there *was* a gap, regardless of the core-ledger result. This distinction matters for the MRA, and we are escalating it as an open disagreement with IT.

## Action

- Re-run transaction monitoring across the ~3-week window once the Unifi feeds are confirmed complete (remediation/look-back).
- Quantify the affected transaction population for the regulator, per the MRA corrective-action expectations.
- Resolve the characterization difference with IT before the remediation status report goes to the regulator.
