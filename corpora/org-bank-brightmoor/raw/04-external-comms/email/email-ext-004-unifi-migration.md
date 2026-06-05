# Email: Unifi Core — migration cutover schedule and support

**From:** Unifi Core — Delivery Management
**To:** Greg Olsen (CIO, Brightmoor Bank)
**Cc:** Project Cornerstone distribution (data/migration coordination)
**Sent:** February 25, 2026, 11:00 AM
**Subject:** Unifi Core — migration cutover schedule and support

---

Greg,

Following our migration steering call, here is the consolidated cutover position and our support commitments. We understand the Bank is reconsidering the cutover sequencing in light of the December examination findings, and we want to make sure our schedule supports whichever approach the Bank confirms.

## Current schedule (pre-decision)

- **Remaining domains to migrate:** deposits/payments, lending, and the data/reporting layer (the general ledger and customer master have already cut over).
- **Originally planned approach:** a single big-bang weekend cutover of the remaining domains, targeted for late March.
- **Migration data feeds:** Unifi will deliver the standard transaction extract to the Bank's downstream consumers, including the transaction-monitoring data layer, on the agreed interface specification.

## Our support for a phased option

We can support a **phased cutover** if the Bank elects it. In a phased approach we would migrate one domain group at a time, hold a validation window after each phase, and maintain the parallel legacy interface so the Bank can keep its monitoring feed flowing during each phase. This extends the overall timeline (we would expect completion across Q2 rather than a single March weekend) and incurs additional dual-running cost, which we have noted in the change order.

Please confirm the Bank's chosen approach and we will lock the phase schedule and the monitoring-feed validation checkpoints accordingly. Our delivery team is aware of the Bank's heightened sensitivity to the monitoring data feed and will prioritize feed validation at every checkpoint.

Best,
Unifi Core Delivery Management
