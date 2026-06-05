# Email: Re: core cutover reconciliation — was there a monitoring data gap or not?

**From:** Greg Olsen (CIO)
**To:** Priya Nair (Head of Financial Crimes)
**Cc:** Dana Whitfield (CCO); Marcus Hale (CRO)
**Sent:** February 20, 2026, 1:30 PM
**Subject:** Re: core cutover reconciliation — was there a monitoring data gap or not?

---

Priya,

I've read your data-gap memo and I want to push back on the framing before it hardens into the regulator narrative.

Our post-cutover reconciliation is **clean. There was no data loss.** Every customer balance, every posting, every account ties out between Horizon and Unifi to the penny — we have the reconciliation report. From a core-banking standpoint the migration was a success and nothing was lost. I'm not comfortable with a memo that reads, to a regulator, as "the bank lost data in the migration," because that is not what happened.

— Greg

> On Feb 20, Priya Nair wrote:
> Greg — I hear you, and I'm not saying the *ledger* lost data. I'm saying the *monitoring system* didn't receive complete data for about three weeks. Those are different controls. Your reconciliation proves the core ledger is whole; it does not prove the monitoring feed was complete, and the alert counts for that window say it wasn't. The ledger can tie out perfectly while scenarios silently failed to fire on feeds that didn't post to the monitoring layer. I'm not writing "the bank lost data." I'm writing "monitoring coverage was incomplete for ~3 weeks," which is true and is exactly Finding 1. We need to reconcile the *monitoring* feed, not just the ledger, and we have to tell the regulator that.

Greg again — understood that you're drawing a ledger-vs-monitoring distinction, and I'll grant the monitoring feed is a different reconciliation. But I'd ask that whatever goes to the regulator says "no core data loss; a monitoring-feed delivery gap is being quantified," not anything that implies the migration lost transactions. Let's align the wording before the status report. This is exactly what the risk review needs to chew on.

Greg
