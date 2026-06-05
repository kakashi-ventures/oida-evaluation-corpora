# Meeting 003: Core-Migration Risk Review

**Date:** March 10, 2026
**Location:** Technology Conference Room / video
**Attendees:** Greg Olsen (CIO, chair), Marcus Hale (CRO), Priya Nair (Head of Financial Crimes), Dana Whitfield (CCO), Unifi Core delivery lead (guest)
**Purpose:** Review the remaining-domain cutover approach in light of the monitoring data gap

---

[10:00] Olsen: We're here to decide the cutover approach for the remaining domains — deposits/payments, lending, and the data/reporting layer. The original plan is a big-bang single-weekend cutover in late March. The question on the table is whether to keep it or go phased, given what happened in January.

[10:05] Nair: What happened in January is Finding 1. The cutover stabilization produced a ~3-week window where the monitoring feed was incomplete and scenarios didn't fire on the affected feeds. We are remediating an MRA that includes that exact gap. If we do another big-bang and it produces another gap, we've re-offended while under supervision.

[10:10] Olsen: I'll own that the January big-bang carried more monitoring-feed risk than we appreciated. The argument for big-bang is that it's faster, cheaper, and you "rip the band-aid off" once instead of living in a dual-run state for a quarter. That argument is real. But it assumes the cutover goes clean, and ours didn't.

[10:15] Hale: During an open MRA, what's our tolerance for a repeat of the coverage gap?

[10:16] Nair: Effectively zero. A second coverage gap during remediation is the kind of thing that turns an MRA into something worse.

[10:18] Olsen: Then the risk review is decisive for me. Phased cutover: migrate one domain group at a time, validate the monitoring data feed after each phase before proceeding, keep the legacy Horizon interface available as a fallback during each phase. It's slower and the dual-running costs more — Unifi's change order reflects that — and we push completion into Q2 instead of a March weekend. But we stop betting the monitoring feed on a single weekend.

[10:24] Unifi delivery lead: We can support phased with a validation window and the parallel legacy interface after each phase, prioritizing monitoring-feed validation at every checkpoint.

[10:27] Whitfield: From a compliance standpoint phased is the only defensible choice while the MRA is open. The cost and the timeline slip are acceptable against the coverage risk.

[10:29] Olsen: Decision: we change the approach to phased. I'll reissue the migration plan as a phased plan; it supersedes the big-bang plan. Steering to confirm.
