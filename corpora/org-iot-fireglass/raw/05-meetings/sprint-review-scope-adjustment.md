# Meeting Transcript: Sprint Review & Scope Adjustment

**Date:** 2025-10-06
**Time:** 10:30 – 11:45 (CET)
**Location:** Video Call
**Attendees:** Alberto Neri (CEO, Innovative Windows LLC), Lucia Ferretti (Assistant, Innovative Windows LLC), Samir Osei (Tech Lead/PM, Atlas Forge), Clara Duval (Junior Developer, Atlas Forge)
**Facilitator:** Samir Osei
**Note-taker:** Lucia Ferretti

---

## Agenda
1. Sprint progress review and current state demo
2. Scope prioritization for remaining 4–5 weeks
3. Compliance reporting requirements and timeline
4. Feature trade-offs: CSV export vs. notification system
5. MQTT broker production readiness
6. UAT planning

---

## Transcript

**Samir:** Alright, everyone, thanks for joining. We're at a pretty critical juncture here. We're about halfway through the contract timeline, and I want to make sure we're all aligned on what gets built in the time remaining. So I'm going to do a quick demo of where we are, and then we need to have some honest conversations about scope.

**Alberto:** Sounds good. What's the current state?

**Samir:** Okay, so the core platform is solid. Authentication is complete — user login, role-based access, all that. CRUD operations for windows, sensors, installations — all working. The sensor data ingestion is working with, um, some workarounds I'll talk about in a second. We've got a partially functional offline mode for forms, not for sensor data. And our reports module is in progress. Let me show you the dashboard.

**Samir:** [shares screen] So this is the live sensor dashboard. Real data coming from the three Milan sites that John just finished installing. You can see window-level detail, sensor status, temperature readings coming in, um, refresh rate is about every five seconds. This is pulling from our MQTT broker, aggregating the data, and rendering it live.

**Alberto:** This is... this is nice. I mean, it's clean. The layout makes sense. But, um — and I don't want this to come across the wrong way — this is pretty, Samir. But Argus Safety Group doesn't care about pretty dashboards. They care about signed PDFs with compliance reports. They need to see that we've documented installation dates, sensor configurations, maintenance schedules, all with dual signatures. The ASG-FP Level 2 audit requires dual-signed PDFs with EPFC-2201 metadata fields. So, um, what's the status on that?

**Samir:** Right, yes. That's, um, that's the big missing piece. The reports module is maybe 30% done. We have the data structure laid out, we know what needs to go into the PDF — installation date, technician name, sensor model, calibration info, all of it. We'll need to ensure the PDF generation includes the EPFC-2201 certification data block. But the actual PDF generation with proper formatting, the signature capture and storage, the audit trail... that's the work that's remaining.

**Alberto:** Okay. And what does that timeline look like?

**Samir:** Uh, realistically, um, I'd say two to two-and-a-half weeks of focused work for Clara. But here's the thing — we need to make a choice about what else gets done in the time we have left. I've got a list here of what could fit into the remaining four to five weeks depending on what we prioritize.

**Lucia:** Can you walk us through the options?

**Samir:** Yes. So, I'm grouping these by tier. Tier 1 is must-have for launch: compliance PDF reports with dual signatures, full installation management with client records, and this dashboard. Those three things are non-negotiable. They're what you need to go live.

**Clara:** And we can hit all three of those in the time we have.

**Samir:** We can, yeah. Tier 2 is should-have but not critical: maintenance scheduling, which is basically a calendar view where you can track when sensors need recalibration or inspection. And a notification system — alerts when sensors detect issues, that sort of thing. Both of those are doable but they add complexity.

**Alberto:** How much complexity?

**Samir:** Um, maintenance scheduling is probably one week. Notifications, um... actually, notifications might be two weeks because we need to think about delivery method, real-time updates, how that integrates with MQTT. So realistically, you pick one of those, not both.

**Alberto:** And Tier 3?

**Samir:** Tier 3 is defer. Full offline sync for sensor readings — we've got partial offline for forms, but syncing actual sensor data would require local queuing and some complexity. CSV export so you can take your data and use it elsewhere. And, um, user manual polish. These are all nice-to-have, but they don't block launch.

**Alberto:** [pause] Okay, so CSV export. That's in Tier 3.

**Samir:** Yeah. I know you and your team have mentioned that resellers are asking for it.

**Alberto:** They absolutely are. Like, I've got, um, I've got three different resellers who've specifically asked about being able to export their installation data and client data into CSV so they can import it into their own systems. It's a selling point for us.

**Samir:** I understand. And, um, I don't want to be flippant about that. But here's the hard constraint: you can have CSV export or you can have the notification system. We don't have time for both. The notifications, though, are things like real-time alerts when a sensor detects an issue, temperature anomalies, that kind of thing. What would be more valuable for your business?

**Alberto:** [pause] That's... that's tough. Um, Lucia, what are you hearing from resellers?

**Lucia:** CSV export comes up more often in conversations. The notifications thing — I mean, it's nice, but most of them are managing their own monitoring anyway. The integration point that keeps coming up is, they want to export the data and plug it into their own workflows.

**Alberto:** Okay. CSV export, then. We go with that.

**Samir:** Alright. So that bumps CSV export to Tier 1. That means maintenance scheduling and notifications get deferred to post-launch.

**Clara:** That works from a dev perspective.

**Alberto:** Good. Um, what about documentation? Lucia was asking about training and end-user materials. Where does that fit in?

**Lucia:** Yeah, I was going to ask. We're going to have users coming in for UAT, and then we're going to have live customers. They're going to need to know how to use this.

**Samir:** Documentation is, um, it's partly in my wheelhouse and partly in yours. I can do technical documentation for the API and system architecture. For end-user stuff — how to install a sensor, how to use the dashboard, how to generate reports — that's probably better coming from you and your team, since you understand the actual workflows better than we do.

**Lucia:** Right. So you'll give me material to work with, and I'll shape it for the audience.

**Samir:** Exactly. And, um, we should probably do a walkthrough session — me and Clara and you and Alberto — to make sure I'm explaining things correctly and we're building the right docs.

**Alberto:** Yeah, let's schedule that. Um, one other thing. Clara, you mentioned in the email that the MQTT broker is still on dev Mosquitto. What does that mean for production?

**Clara:** So, um, Mosquitto is a lightweight MQTT broker. We're using it locally for development and testing. It's fine for that. But for production, we need something more robust. We could move to a managed service like AWS IoT or, um, we could set up a production-grade Mosquitto instance with proper TLS, authentication, all that.

**Samir:** And we haven't done load testing yet, which is the thing we really need before we make that decision. We need to know, like, how many concurrent sensor connections can we handle? What's the latency under load? All that. So my recommendation is we get load testing data this sprint, and then we make the broker decision.

**Alberto:** When would that load testing happen?

**Samir:** Um, we can spin up a test environment this week, run some simulations with, um, let's say a hundred concurrent sensor connections to start. See what the performance looks like. That gives us real data for the decision.

**Alberto:** Okay, good. I like that. Um, one more thing, and then I'll stop peppering you with questions. [laughs] The UAT timeline. When can my team get hands on?

**Samir:** We're targeting the week of October 27th. So that's, um, three weeks out. We'll have a staging environment set up, it'll have all the Tier 1 features plus CSV export, and your team can run through realistic scenarios.

**Lucia:** Who's running that UAT?

**Alberto:** I'm going to do it, and I want you involved. And, um, Marco from Reseller Solutions. I want his perspective on the export and reporting features.

**Samir:** Marco hasn't been involved in the project until now, has he?

**Alberto:** No, no, he hasn't. But he's going to be our first external customer, I think. So it makes sense for him to validate that the product actually works for a reseller workflow.

**Samir:** That's smart. Um, does he know that? Should we brief him beforehand?

**Lucia:** I'll reach out to Marco. He's aware this is coming, so it shouldn't be a surprise.

**Samir:** Okay, good. Um, I think — is there anything else, or are we good?

**Alberto:** I think we're in okay shape, actually. I had some anxiety about the timeline, but hearing that Tier 1 is solid and we're making conscious choices about what goes in and what doesn't... that feels right. The compliance reporting is the critical thing, and if that's on track, we can launch.

**Samir:** It is on track. Clara and I are both focused on that.

**Clara:** I've blocked out a full week starting tomorrow specifically for the PDF generation and signature logic.

**Alberto:** Excellent. Okay, I feel better. Let's make sure we lock in that UAT date and that walkthrough session for documentation.

**Samir:** Yeah, we'll send out a Doodle poll for the walkthrough. And I'll prep a staging environment schedule for UAT week.

**Lucia:** I'll get that on the calendar.

**Samir:** Perfect. Um, alright. I think we're done. Anything else from anyone?

**Alberto:** No, I think we're good. Thanks, all of you. This is, um, this is going in the right direction.

**Clara:** Thanks, Alberto. We're excited to get to UAT and see how users interact with it.

---

## Action Items
- [ ] **Samir & Clara**: Conduct MQTT broker load testing with 100+ concurrent sensor connections to validate performance — Due: 2025-10-13
- [ ] **Clara**: Complete Tier 1 priority features: compliance PDF reports with dual signature support — Due: 2025-10-20
- [ ] **Samir & Clara**: Implement CSV export functionality for installation and client data — Due: 2025-10-20
- [ ] **Samir**: Schedule technical documentation walkthrough session with Alberto, Lucia, and Clara — Due: 2025-10-08
- [ ] **Samir**: Prepare staging environment and UAT plan for week of October 27th — Due: 2025-10-20
- [ ] **Lucia**: Reach out to Marco from Reseller Solutions to brief on UAT participation and expectations — Due: 2025-10-08
- [ ] **Lucia & Samir**: Develop end-user documentation for sensor installation, dashboard usage, and report generation — Due: 2025-10-22

## Decisions Made
- **Tier 1 (Launch-Critical)**: Compliance PDF reports with dual signatures, installation management, sensor dashboard, CSV data export
- **Tier 2 (Deferred)**: Maintenance scheduling, real-time notification system
- **Tier 3 (Post-Launch)**: Full offline sync for sensor readings, user manual polish
- **MQTT Production Strategy**: Conduct load testing in current sprint to inform broker architecture decision (managed service vs. production Mosquitto)
- **UAT Participants**: Alberto (CEO), Lucia (assistant), Marco from Reseller Solutions (first external customer)
- **UAT Target Week**: October 27th
