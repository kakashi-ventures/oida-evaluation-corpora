# Demo Day Pitch: MindBridge
**Date:** November 12, 2025
**Time:** 18:03–18:23 CET
**Location:** Palazzo delle Industrie, Milan
**Participants:** Anna Kowalski (MindBridge CEO), Raj Patel (MindBridge CTO), Daniel Reeves (IC), Ava Lindström (IC), Tomás Herrera (Analyst)

---

[18:03] Daniel: Alright, welcome back everyone. Short break and then we move forward with MindBridge. Anna, Raj, come on up.

[18:05] [scattered applause, some people still getting back to their seats with drinks]

[18:07] Anna: Thank you. Um, hi. I'm Anna Kowalski, CEO of MindBridge. This is Raj Patel, our CTO. [pause, Anna glances at her notes] So, um, the problem we're solving is actually a pretty expensive one for companies. Employee turnover costs are massive. When someone leaves, a company loses 50% to 200% of that person's annual salary in replacement costs. That's recruiting, onboarding, lost productivity, knowledge transfer. It's a big number.

[18:27] Anna: Most companies only realize someone's about to leave when they hand in their resignation. But what if we could predict it? Weeks or months in advance?

[18:35] Anna: [clicks to product slide] We built MindBridge. It's a platform that analyzes internal communications — email, Slack messages, meeting behavior — and it predicts employee engagement and flight risk. Our dashboard gives HR leaders real-time visibility into team health.

[18:47] Raj: [taking over] From the tech side, we're using a combination of NLP and graph analysis. So we tokenize sentiment from written communications, we build an interaction graph to identify isolation or lack of connection, and then we feed those signals into a predictive model. The model is trained on historical data from our pilot customers. And it's achieving, um, 72% accuracy on identifying employees at high risk of leaving within the next quarter.

[19:07] Anna: [taking back] We've got three enterprise pilots right now. They're with mid-sized companies in tech and financial services. No revenue yet, but the pilots are generating a lot of interest. We're seeing strong engagement with the dashboard.

[19:18] Anna: [clicks to funding slide] We're asking for €180K for 8%. We'll use this to accelerate the go-to-market process and, um, hopefully convert these pilots to paying customers.

[19:27] Anna: That's the pitch. Questions?

[19:28] [Ava and Daniel exchange a glance, then Ava raises her hand]

[19:30] Daniel: So, Raj, the 72% accuracy — is that on historical data or live predictions?

[19:35] Raj: That's on historical data. We took a dataset from, um, from a partner company, and we backtested the model. So we trained on, like, 18 months of communication and, um, labeled outcomes of who actually left. And the model gets 72% AUC on that task.

[19:49] Daniel: But you haven't deployed this in production with a live cohort?

[19:52] Raj: [pause] Not yet, no. The pilots are, um, the pilots are early. They're just now starting to use it. So we won't have ground truth for a few months.

[19:59] Daniel: So in other words, you don't actually know how accurate it is when it's making real predictions.

[20:04] Raj: [defensively] The backtesting is pretty rigorous. We use cross-validation, we separate train and test sets. So I'm fairly confident the results will hold.

[20:11] Ava: But you don't know. You're confident, but you don't know.

[20:14] Raj: [quiet] That's fair.

[20:15] Ava: Okay, so, Anna, bigger question. You're analyzing employee communications. That's GDPR territory. Walk me through how you're handling data privacy.

[20:24] Anna: Right, great question. So we've, um, we've built in a few safeguards. First, we're processing only anonymized communications. And second, we've implemented data minimization — so we're only retaining the signals we need for the model, not the actual text of messages.

[20:38] Ava: Anonymized how?

[20:40] Anna: [pause] Well, so, um, we're stripping email addresses and names from the communication metadata. And then we're just looking at the graph structure and the sentiment signals.

[20:50] Ava: But you can probably re-identify people pretty easily from the graph structure. If I know someone works at a certain company and I see an interaction graph, I can figure out who's who.

[20:59] Anna: [uncomfortable pause] That's... that's a fair point. We haven't actually tested for re-identification risk. But we're, um, we're working with a GDPR consultant on this.

[21:08] Ava: Who's the consultant?

[21:10] Anna: Um, I can give you the name after the pitch.

[21:12] Ava: [skeptical] Okay. So in other words, the GDPR strategy is not fully baked.

[21:16] Anna: We're still refining it, yes.

[21:18] Tomás: Can I ask about the pilots? You said three enterprise pilots. How close are they to converting to paid?

[21:24] Anna: Um, so we're... we're optimistic. We're running pilots through Q4, and we expect at least two of them to sign contracts by Q1.

[21:32] Tomás: Based on what? Like, have they given you verbal commitments? What's the basis for that expectation?

[21:38] Anna: [hesitant] So, um, we've had positive feedback from the pilot sponsors. They're using the tool regularly. Um, but I won't say we have, like, signed LOIs yet.

[21:47] Tomás: So it's optimism.

[21:48] Anna: [defensive] It's based on actual usage, but yes, it's still optimistic.

[21:52] Ava: What's the pricing model? How much would you charge if they convert?

[21:56] Anna: So we're thinking, um, a per-employee seat model. So for a company with 500 people, maybe €2,000 a month. That's, like, €4 per person per month.

[22:04] Ava: So a 500-person company pays €24K per year. What's your CAC? What does it cost you to close that deal?

[22:10] Anna: We're not sure yet, since we haven't actually closed one.

[22:12] Ava: [laughs, not unkindly] Right. So you're at the stage where you're making pricing assumptions based on comparable products, but you don't have any real data.

[22:20] Anna: [quietly] That's accurate.

[22:21] Daniel: [interjecting, slightly more gently] So, Anna, I think the problem is real. I know a lot of HR leaders who would pay for better visibility into team health. But, um, you're still pretty early. The model isn't validated in production. The GDPR story isn't finalized. And you don't have paying customers yet.

[22:37] Daniel: [continues] The good news is the team is solid. Raj clearly understands the tech. And you're getting good traction in the pilots. But you need to de-risk a few things before we're comfortable investing.

[22:48] Anna: [nods] I understand. Um, what would it take to move from, like, conditional interest to a yes?

[22:53] Ava: [jumping in] Get one pilot to convert. Get external validation on your model accuracy. And get a definitive GDPR sign-off from a qualified DPA or legal counsel.

[23:01] Anna: Okay, so those are the three things.

[23:02] Ava: Yep. If you can do those in the next, um, three to six months, we'd be very interested in revisiting the conversation.

[23:09] Anna: [nods] Thank you. That's really helpful.

[23:10] Daniel: [standing slightly] Good luck with the pilots. [handshake]

[23:12] [polite applause, quieter than NovaTech but warmer than GreenLoop. Some people in the audience are nodding — there's a sense of respect for the team but skepticism about the maturity]

[23:16] Tomás: [to Daniel, quietly] I'd put that as conditional, no higher.

[23:18] Daniel: [whispers back] Yeah. They need to prove something real first.

[23:21] [END]
