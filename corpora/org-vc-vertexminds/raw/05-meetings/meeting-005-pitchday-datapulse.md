# Meeting Transcript: Demo Day Alpha - DataPulse Pitch
**Date:** November 12, 2025
**Location:** Palazzo delle Industrie, Milan
**Event:** Demo Day Alpha - Fourth Pitch
**Attendees:** Daniel Reeves (CEO, Vertex Minds), Ava Lindström (Co-IC, Vertex Minds), Tomás Herrera (Analyst, Vertex Minds), Simone Marchetti (Founder/CEO, DataPulse), Elena Varga (CTO, DataPulse)

---

[18:28] **Simone Marchetti:** Thank you, thank you everyone. Okay, so, um, we're DataPulse. And if you... if you work in fashion e-commerce, you know this problem intimately. Your customers are bouncing. They're clicking around your site, adding things to carts, and then just... [pauses, gestures widely] ...leaving. Why? You don't know. You have Google Analytics, sure, but it tells you *what* happened, not *why*.

[Simone clicks to next slide — bright, minimalist design with a fashion model silhouette and behavioral arrows overlaid]

**Simone:** We give you the *why*. Our behavioral analytics platform ingests your customer journey — every click, every scroll, every pause — and uses machine learning to predict churn, optimize product placement, and honestly, just make your store feel less like a maze.

[18:32] **Daniel:** [nods, taking notes]

**Simone:** We've got 50,000 monthly active users across our client base right now. Four enterprise clients, ranging from luxury accessories to fast fashion. And, uh, our core metric is this one: [points to slide] we're delivering an average 18% improvement in conversion lift. One client went from 2.1% to 2.48% conversion rate in six weeks.

[Simone clicks through revenue slide]

**Simone:** Current MRR is eight thousand euros. We're growing, we're profitable at the unit level, and our churn — our monthly churn is, um, pretty healthy at six percent.

[Elena Varga nods from the side. Someone in the audience shifts in their seat.]

[18:36] **Ava:** Beautiful deck, Simone. Really well put together. [pauses, looks down at notes] So I want to dig into that 50,000 MAU number. When we accessed the analytics dashboard you shared for due diligence last week, we counted around 38,000 active accounts in October. Can you help us reconcile that discrepancy?

[Simone's expression flattens slightly. A beat of silence.]

**Simone:** Oh, um. Right. Yeah, so those numbers, they do fluctuate seasonally, actually. October was a dip for us — summer's usually when fashion retail peaks, and then we see a seasonal drop-off in early fall. So our typical range is... is above 45,000, but October we were closer to the high 30s.

[18:39] **Tomás:** Do you have the September and October cohort data handy? I'm curious about the trajectory.

**Simone:** I, uh... Elena might have the exact figures, but we can definitely pull that post-call. We track it monthly.

[Elena: "Yeah, we have it in our database. I can send a dashboard link."]

**Simone:** Right. So the 50K is not like a, a guaranteed floor, it's more the recent high we're tracking toward.

[18:41] **Ava:** [makes a note] Okay. I want to move to churn. You said six percent monthly. That's... that math works out to about 72% annual churn. That concerns me significantly for a platform business. What's driving that churn?

[Simone leans forward]

**Simone:** So, the thing is — and this is actually something I wish more investors understood — it's not uniform churn. Our enterprise clients, the ones paying 2K, 3K a month, they retain incredibly well. It's mostly the smaller merchants, the solo sellers, who churn out. They try us, they realize they need more hands-on support to really implement the behavioral insights, and they move on. It's, it's almost expected at that segment.

[18:44] **Ava:** Right, I hear you. But let me ask you this then: what percentage of your eight thousand MRR comes from your largest client?

[Simone hesitates. Goes to answer, stops.]

**Simone:** About, um, forty percent. Yeah, roughly forty.

[Someone's phone rings. Loud, distinct ringtone — classical piano piece. A man in the third row fumbles to silence it. Audible apologies.]

[18:46] **Daniel:** [clears throat, maintains focus] Go ahead, Simone.

**Simone:** Sorry, yeah, so, um, forty percent from our top client, but like I said, the enterprise base is really sticky. Our churn at that level is, I'd say, less than two percent monthly.

[Ava nods, writing. Tomás and Daniel exchange a glance.]

[18:48] **Ava:** So you've got concentration risk and then churn risk at the SMB level, which is the bulk of your user base by count. That's the tension I'm seeing.

**Simone:** I mean, yes, but we're actively working on product-market fit at that level. We just released a no-code template system so smaller merchants can, uh, basically configure behavioral flows without engineering support. We think that unlocks retention.

[Elena chimes in: "We have beta data from three pilots. Churn dropped to 4.2% in those cohorts."]

[18:50] **Daniel:** Elena, good. Can you walk us through your technical architecture? I'm curious how you're processing that behavioral data in real-time without creating latency issues for customer-facing pages.

[Elena stands, clicks a slide showing a system diagram]

**Elena:** Yeah, so, um, we don't actually process in real-time for attribution. That would kill performance. Instead, we ingest events asynchronously via a lightweight JavaScript SDK — it's about 12 kilobytes, minified — and batch those into our data pipeline. The latency for dashboard updates is, um, usually within two to four hours. For real-time stuff like churn prediction alerts, we run a separate inference engine that samples data every... [pauses, checking notes on her laptop] ...every thirty minutes.

**Daniel:** And you own the data pipeline end-to-end?

**Elena:** Yep. We're not using third-party analytics vendors. It's all custom-built on top of a TimescaleDB instance, and then we have Python services running the ML models.

[Daniel nods, satisfied]

[18:54] **Tomás:** Simone, I want to ask about competitive moat. I know there's a few other behavioral analytics tools in the e-commerce space now. What's protecting DataPulse from commoditization?

[Simone sits back, more confident now]

**Simone:** Great question. So a lot of what we do is built on proprietary behavioral taxonomy that we've developed over eighteen months. We've categorized, I don't know, maybe five thousand distinct behavior patterns in fashion retail specifically. Our models were trained on that domain-specific data, so they perform way better for apparel merchants than a generic tool like, say, something trained on SaaS or marketplace data.

[Simone clicks to a slide showing accuracy metrics]

**Simone:** We published some of this research at, um, an e-commerce conference last spring. And because of that taxonomy and the domain training, we can make predictions that generic competitors just can't. For instance, we can flag when a customer is likely to buy in a higher price tier, not just whether they'll churn. That's the moat.

[Audience murmurs, a few nods]

[19:00] **Ava:** How long did it take to build that taxonomy?

**Simone:** About sixteen months. We worked with, um, fashion merchants directly, coded up patterns, tested, iterated. It's not something you can, uh, easily replicate if you're a generic analytics company trying to add fashion as a vertical.

[19:02] **Tomás:** And you've kept that proprietary? You haven't open-sourced it?

**Simone:** No, no, it's our core IP. We have a patent pending on the classification methodology, actually. [Elena nods in confirmation] So I think we're well-protected there.

[Daniel taps his pen against his notes]

[19:04] **Daniel:** One last thing from me — you're currently at eight thousand MRR, and you said you're profitable. Where are you putting your focus for the next six months? More customer acquisition, or product development?

**Simone:** Product development, mainly. The no-code template thing Elena mentioned, that's phase one. Phase two is expanding our model coverage — so right now we focus on conversion and churn prediction, but we want to add size recommendation models, return rate prediction, um, fashion trend detection for inventory. We think that gets us closer to being an indispensable platform rather than just an analytics tool.

[19:07] **Daniel:** Okay. And funding needs?

**Simone:** We haven't formally closed a round yet, but yes, we're looking to raise. We'd be talking to investors soon after the new year, probably, to fund the product roadmap and, um, a dedicated sales person.

[Ava raises her eyebrows slightly, makes a note]

[19:08] **Daniel:** Thanks, Simone. [pauses] Elena, thanks for the technical context.

**Simone:** Thank you. [stands, shakes hands with Daniel and Ava. Elena does the same.] Really appreciate the questions.

[Simone and Elena gather their materials. Tomás leans in to Ava and Daniel]

[19:10] **Tomás:** [quietly] The 50K MAU gap is going to be a problem in diligence. And that top-ten-client concentration...

**Ava:** [quietly] Yeah. Product's solid, though. Simone's a good operator. But the metrics don't quite match the narrative.

**Daniel:** [quietly] Let's see if they want to do a follow-up. I want deeper churn data before we move forward.

[The three make notes. An event coordinator signals that the next pitch will begin in five minutes. The audience applauds as Simone and Elena exit the stage.]

[19:12] **[END OF TRANSCRIPT]**

---

## Summary Notes
- **Strength:** Domain-specific behavioral taxonomy, strong CTO, compelling product-market fit narrative
- **Concerns:** MAU verification gap (38K vs. claimed 50K), high SMB churn (6% monthly), revenue concentration (40% from one client)
- **Follow-up Actions:** Request September–October cohort data, churn breakdown by customer segment, patent filing details, product roadmap timeline
- **Investor Sentiment:** Mixed to cautiously interested; diligence required before term sheet

