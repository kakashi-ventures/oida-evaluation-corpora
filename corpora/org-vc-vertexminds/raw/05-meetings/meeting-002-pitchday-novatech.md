# Demo Day Pitch: NovaTech AI
**Date:** November 12, 2025
**Time:** 17:35–17:52 CET
**Location:** Palazzo delle Industrie, Milan
**Participants:** Marco Bianchi (NovaTech CEO), Yara Osman (NovaTech CTO), Daniel Reeves (IC), Ava Lindström (IC), Tomás Herrera (Analyst)

---

[17:35] Daniel: Alright, everyone. Welcome to Demo Day. I'm Daniel Reeves with Vertex Minds. This is our first pitch of the evening, and I'm really excited to introduce NovaTech AI. Marco, Yara, please come on up.

[17:37] [applause, some audience rustling as the founders take their seats]

[17:38] Marco: Thank you. Um, hi everyone. I'm Marco Bianchi, CEO of NovaTech. And this is Yara Osman, our CTO. So, we're here to talk about a problem that costs the European architecture and construction industry billions every single year. [clicks to first slide]

[17:45] Marco: Architectural firms spend on average 40 hours per construction permit. That's one full work week per permit. And that time is spent basically reading, interpreting, and copying regulatory documents. It's boring, it's error-prone, and it's incredibly expensive.

[17:57] Marco: So, what we built is an AI system that automates this process. [clicks to product demo slide] We've fine-tuned a large language model on 200,000 building regulation documents — everything from Italian building codes to EU compliance standards. And now when an architect uploads a project brief, our system automatically extracts the relevant requirements, flags compliance risks, and even generates draft permit documentation.

[18:12] Yara: [takes over] And to be clear, the accuracy is critical here. So we've validated the model on, um, on held-out test sets with F1 scores of 0.92 for requirement extraction and 0.85 for compliance flagging. Which is, you know, in production-quality territory.

[18:27] Marco: We're currently operating with 12 beta customers. Three of them are paying. And the response has been fantastic. One studio in Milan told us, quote, "This saved us basically two weeks per project." That's real money.

[18:38] Marco: The ask is €200,000 for 8% of the company. We'll use this to hire two more engineers, expand our document training set, and begin sales outreach in the German and French markets.

[18:47] Marco: And, um, that's the pitch. Questions?

[18:48] [brief pause, audience leans in]

[18:50] Ava: So, Marco, I want to dig into the TAM. You mentioned architectural firms. But let me ask — how many architects in Europe? How are you thinking about the market size?

[18:59] Marco: Right. So the way we look at it, there's about 150,000 architectural practices in Europe. Average revenue, maybe €800K to €1M per practice. And we estimated, um, based on permit timelines, that the regulatory documentation market — the total addressable value of that time — is about €3.4 billion annually.

[19:19] [Ava makes a note, nods slowly but doesn't look convinced]

[19:20] Ava: Okay. So €3.4B. That's — that's larger than the estimate we had on the intake form. [glances at Tomás]

[19:25] Marco: Well, um, I mean, that's when you factor in, you know, the broader construction consulting market. It's not just pure architecture. It's also engineers, um, permit consultants.

[19:33] Ava: Got it. So the 150,000 architects — how many of those would actually use your product?

[19:39] Marco: We think, um, realistically, in the first three years, maybe 5%. So 7,500 firms. At, um, let's say €1,000 per month per firm, that's €90M ARR in three years.

[19:50] Ava: [pauses] And you're assuming 5% penetration just based on what?

[19:54] Marco: Based on, um, comparable adoption curves for, like, design software. AutoCAD, Revit. Those took several years to hit mainstream adoption.

[20:01] Ava: Right, but those were solving different problems and, um, they didn't require, you know, changing existing workflows the way your product might. Anyway, um, let me ask about validation. Yara, you mentioned 0.92 F1 on held-out test sets. But have you done any external benchmarking? Like, third-party evaluation?

[20:18] Yara: We have, um, we haven't actually done external benchmarking yet. But the test sets we used are pretty comprehensive. They include documents from, like, six different European jurisdictions. So I think the — the generalization should be good.

[20:30] Ava: But you don't know until you test it on data you didn't train on.

[20:33] Yara: That's fair. Yeah. We could do that.

[20:35] Daniel: [interjecting] What about the beta customers? Are they seeing the 0.92 accuracy in production?

[20:39] Marco: Um, it's a bit different in production, honestly. Because, um, the documents are messier. They're scans. Some of them are in Italian, some are in mixed — like, mixed Italian and English. So we're seeing maybe, um, 80 to 85% in actual use.

[20:53] Daniel: And the customers are okay with that?

[20:55] Marco: They are, because it's still saving them time. The product flags issues that, um, human reviewers still need to check. But it's a 5x speed improvement.

[21:03] Tomás: Marco, question on unit economics. You mentioned three paying customers. What's the monthly fee? And what's your customer acquisition cost?

[21:10] Marco: Um, so the first three are paying, I think, around €800 a month. Which is the startup pricing. We're planning to move to, um, to a usage-based model as we get more volume. Each firm essentially gets a bulk seat license.

[21:22] Tomás: So €800 monthly. And your CAC to land each one?

[21:25] Marco: [pause] It's been, um, really low so far because they came through personal networks. I'd say probably €2,000 to €3,000 to acquire each new customer when we go to broad market.

[21:34] Tomás: And your retention? Do you have any churn data?

[21:37] Marco: One beta customer has been with us for six months and is renewing. The other two are newer. So we don't have, um, a lot of data yet. But the initial signals are good.

[21:46] Daniel: [pauses] One more thing — patents. You mentioned patent-pending status in your materials. Can you walk us through what you've filed?

[21:53] Marco: Yeah, so we've, um, we've filed something on the document parsing architecture. The approach to fine-tuning on regulatory documents is somewhat novel. [looks to Yara]

[22:01] Yara: So basically we've built a custom tokenizer and a prompt-chaining architecture that's, um, it's tuned to regulatory language. A lot of existing LLMs don't handle that well. And we think there's some IP there.

[22:11] Daniel: But the filing is still, um, pending?

[22:13] Marco: Yes, it's, um — [pause] — it's currently in draft. We're planning to file within the next month or so.

[22:19] Ava: Okay. So no formal patent application yet.

[22:21] Yara: That's correct.

[22:22] [brief silence, Ava and Daniel exchange a look]

[22:23] Daniel: Alright. I think we're good. You've got a real problem and a real solution. The team clearly understands the tech. A few things to tighten: external benchmarking, actual patent filing, longer cohort of retained customers. But this is exciting. [applause]

[22:37] Marco: Thank you so much.

[22:38] Ava: [nods] We'll be in touch with next steps.

[22:40] [audience applause, some murmuring. A few people in the audience lean over and whisper to neighbors. Energy in the room is visibly higher than before the pitch]

[22:45] Tomás: [to Daniel, quietly] That TAM number was different from the deck we reviewed.

[22:48] Daniel: [whispers back] Yeah. I caught that. We should flag it.

[22:50] [END]
