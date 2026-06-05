# Email: Migration approach change — moving from big-bang to phased cutover

**From:** Greg Olsen (CIO)
**To:** Marcus Hale (CRO); Dana Whitfield (CCO); Priya Nair (Head of Financial Crimes)
**Cc:** Project Cornerstone distribution; Unifi Core program
**Sent:** March 12, 2026, 2:15 PM
**Subject:** Migration approach change — moving from big-bang to phased cutover

---

All,

After the migration risk review, we are changing the core-migration approach. We are moving **from the big-bang single-weekend cutover to a phased cutover.**

Why: the January cutover stabilization caused exactly the kind of monitoring data-delivery gap that put Finding 1 in the MRA. A second big-bang event for the remaining domains would re-run that risk — a single weekend gives us no fallback if a feed silently fails, and Compliance can't afford another coverage gap while we're mid-remediation. A phased cutover lets us migrate domains in sequence, validate the monitoring data feed after each phase before proceeding, and keep the legacy Horizon feed available as a fallback during each phase.

This is slower and it costs more in dual-running, and I've heard the argument that big-bang "rips the band-aid off." But the risk review was decisive: the monitoring-coverage risk of another big-bang is not acceptable during an open MRA. So the plan changes. The migration plan will be reissued as a phased plan (this supersedes the big-bang plan); steering will confirm.

Greg
