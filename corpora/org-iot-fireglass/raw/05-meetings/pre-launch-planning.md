# Meeting Transcript: Pre-Launch Planning & UAT Preparation

**Date:** 2025-10-24
**Time:** 09:00 – 10:00 (CET)
**Location:** Video Call
**Attendees:** Alberto Neri (CEO, Innovative Windows LLC), Lucia Ferretti (Assistant, Innovative Windows LLC), Samir Osei (Tech Lead/PM, Atlas Forge), Clara Duval (Junior Developer, Atlas Forge), John Smith (Field Technician, Atlas Forge)
**Facilitator:** Samir Osei
**Note-taker:** Lucia Ferretti

---

## Agenda
1. UAT plan walkthrough (week of October 27th)
2. Pre-launch checklist review
3. Known bugs and proposed fixes
4. PDF report formatting demo
5. Mobile inspection workflow validation
6. Go-live and phased rollout strategy
7. Data migration from legacy systems
8. Security considerations for MQTT

---

## Transcript

**Samir:** Okay, everyone. So, um, this is the big one. We're three days away from UAT, and I want to make sure everyone knows what's happening, what to expect, and what the path to launch looks like from here. So let's start with the UAT plan itself.

**Alberto:** Right. Let's walk through it.

**Samir:** Okay, so the UAT window is Monday, October 27th through Friday, October 31st. We have a staging environment up and running with realistic data — the three Milan installation sites, some test sensor data coming through, that kind of thing. The team running UAT is you, Alberto, Lucia, and Marco from Reseller Solutions. Is Marco confirmed?

**Lucia:** He confirmed yesterday. He's going to be on the Monday morning kickoff call, and then he'll work through the scenarios at his own pace with my support.

**Samir:** Excellent. Um, so the test scenarios are: sensor installation workflows, using the dashboard to view live data, generating compliance reports and signing them, exporting installation data to CSV, and running through the mobile inspection workflow end-to-end. The idea is, you're going to use the system like a real customer would, find the bugs, find the things that don't make sense, and tell us.

**Clara:** And we've got a dedicated Slack channel for UAT feedback, so you don't have to wait for meetings. Just post issues as you find them.

**Alberto:** Good. Um, what happens with bugs we find?

**Samir:** Depends on severity. Critical bugs — things that break the core workflow — we fix immediately and re-deploy to staging. Medium bugs we triage and decide whether they block launch or they're post-launch fixes. Low severity is nice-to-have, post-launch.

**John:** Speaking of bugs, um, there are a few known ones that I've been tracking. Clara, you had a PR for the duplicate sensor readings issue, right?

**Clara:** Yeah, I do. FG-001 — we're sometimes seeing duplicate MQTT messages from the broker, which causes duplicate sensor readings in the database. The root cause is a resubscribe logic that's not idempotent. I've got a fix in code review right now, and I'm hoping to merge it before UAT starts.

**Alberto:** When's that?

**Clara:** Um, today or tomorrow. It's pretty straightforward fix. Just needed another set of eyes on it.

**Samir:** Okay, so that should be merged by Monday. The other known issue is FG-002 — sensor timeout versus offline status ambiguity. Like, we don't cleanly distinguish between a sensor that's temporarily disconnected versus one that's just not sending data.

**John:** Right, and that affects the dashboard because you can't tell if a sensor is down or if it's just... not reporting.

**Clara:** I proposed a UI indicator — like, if a sensor hasn't reported in more than, um, three minutes, we show a "stale" state instead of just showing the last reading.

**Samir:** That's good. John, does that solve the problem from a field perspective?

**John:** Yeah, I think so. If I'm looking at the dashboard and I see a sensor is stale, that tells me I need to go check on it. That's better than the ambiguity.

**Clara:** I'll get that deployed to staging today.

**Samir:** Good. Um, okay, moving on. Alberto, I know you wanted to see the PDF report generation. Let me show you the current version.

**Samir:** [shares screen] So this is the compliance report PDF. It's got the header with FireGlass branding, it shows installation details — date, location, window count, sensor model and serial numbers. Then there's a section for inspection findings. And then at the bottom, there's signature lines for dual signatures with date and printed name fields.

**Alberto:** Can you scroll down? I want to see the formatting.

**Samir:** [scrolls] So the layout is, um, pretty standard. Header, body, footer with page numbers and document ID. The signature block is this bit here at the bottom.

**Alberto:** Okay, so I want to request a change. The header — can we add the customer name and the site address there? Because we might print these reports, and the context needs to be clear on the page itself without having to flip back to a cover sheet.

**Clara:** Yeah, we can do that. I'll adjust the template.

**Alberto:** And the footer — can the date be in a different format? This is showing as ISO 8601, but our customers are mostly in Italy, and they're going to want DD.MM.YYYY.

**Clara:** Absolutely. I'll update the formatting. Anything else?

**Alberto:** No, I think that's good. So when will these changes be in staging?

**Clara:** Um, probably tomorrow morning. Latest by Friday for sure.

**Alberto:** Great. Um, alright. John, can you walk us through the mobile inspection workflow that you tested in the field?

**John:** Yeah, sure. So, the idea is, I'm on site with a tablet, and I need to document the installation. I open the app, I scan the QR code on the window, the system pulls up that window record. Then I can add photos, I can add notes, and I can capture a signature to sign off on the installation being complete.

**Samir:** And this all works offline? Like, if you lose WiFi, you can still capture the data?

**John:** Exactly. And then when you get back online, it syncs up. Which is really important for field work, because, like, you can't always rely on connectivity.

**Alberto:** How long does the sync take?

**John:** Um, it's pretty fast. I'm talking seconds. The form data is usually just text and a signature, so it's not a lot of data.

**Lucia:** And the signature capture specifically — is that reliable?

**John:** Yeah, I tested it a bunch. The signature comes through clearly. You can see it on the report. And the timestamps are right.

**Samir:** Okay, good. Um, one thing we should test during UAT — the photo upload thing. John, you hit the file size limit during field testing. Clara, we increased that, right?

**Clara:** Yeah, we bumped it to 20 MB and added automatic compression on the client side. So theoretically, you can take a high-res photo and it'll compress it before upload. Saves bandwidth and keeps things snappy.

**John:** That's going to help a lot. Because I was struggling with that during the Milan work.

**Samir:** Great. Okay, um, let's talk about go-live. Because UAT is validation, but then we need an actual launch plan.

**Alberto:** I'm thinking phased rollout. Start with the Milan sites — they're already installed, they're already generating data. So we turn on production mode for those three sites, monitor them for a week, make sure everything is stable.

**Samir:** That's smart. And then?

**Alberto:** Then we bring on a few more customers. Maybe our Reseller Solutions partnership — Marco and his network. And we take feedback, iterate, scale from there.

**Samir:** Timeline-wise, we're looking at Monday, November 3rd for Milan go-live. Then, um, I'd say end of November for broader rollout to resellers if things are stable.

**Lucia:** Does that timeline work for you, Samir?

**Samir:** It does if UAT is clean. Which, um, I'm fairly confident it will be. We've tested pretty extensively internally.

**Alberto:** Okay. Um, one thing I need to mention. We have three years of installation records in Excel. Window records, client data, that kind of thing. Is there a way to import that data into the system, or do we have to manually re-enter everything?

**Samir:** [pause] That, um, that wasn't in the original scope. But, uh, we can build a CSV import tool pretty quickly. It would allow you to upload a CSV and map the columns to our database schema.

**Clara:** I can do that. I'd say, like, two days of work, maybe three. It's not complex, just a little bit of file parsing and validation.

**Samir:** Alberto, is that timeline okay for your purposes?

**Alberto:** If we can have it by end of November, yeah, that works. We'll do the manual migration for the big customers, and then the CSV import takes care of the rest.

**Clara:** I'll put that on the backlog for post-UAT. We can knock it out the first week after launch.

**Alberto:** Great. Um, so there's one other thing. Security. Samir, the email you sent mentioned that we're using username and password for MQTT. Is that a concern?

**Samir:** Good question. So, um, here's the situation. The sensors are on a private network within your facilities. They're not exposed to the internet. So, authentication-wise, username and password is acceptable for that internal use case. But, um, if you ever wanted to deploy sensors on a public network, or if you wanted to expose the MQTT broker externally, then you'd want TLS certificates and more robust authentication.

**Alberto:** So it's fine for what we're doing now?

**Samir:** For now, yeah. It's fine. It's not a vulnerability if the network is private. But I'd recommend as a future improvement to upgrade to TLS, just for defense-in-depth. And if you ever expand beyond your own facilities, that becomes critical.

**Clara:** We can document that as a recommendation for the next version or a security upgrade down the road.

**Alberto:** Okay, that makes sense. Um, I think — actually, I think we're in pretty good shape. I'm going to be honest, like three weeks ago I was worried we weren't going to make it. But the team's done solid work here.

**Samir:** We've had some bumps, but I think we've managed the scope well and the core product is strong.

**Lucia:** What's the handoff looking like post-launch? Like, do we have support lined up?

**Samir:** Um, yeah, that's in our contract. We've got six months of maintenance and support included. So, production issues, bug fixes, questions from your team — that all comes to us. And then, um, we'll do a monthly check-in to make sure everything's running smoothly.

**Alberto:** Good. Um, alright. I think we're ready. Let's do UAT next week and see what breaks.

**Clara:** [laughs] Hopefully nothing.

**John:** Or hopefully we find the small stuff before it becomes big stuff.

**Samir:** Exactly. Okay, um, one last thing. Just a reminder — next week we're going to be on high alert. UAT testing, bugs coming in, rapid iterations. It's going to be a bit chaotic. But that's normal. And, um, I'll be reachable the whole time. If you hit something that blocks you, let me know immediately and we'll figure it out.

**Alberto:** Sounds good. And Marco — Lucia, can you make sure he knows to reach out directly if he hits issues?

**Lucia:** Already on it. I sent him the contact list and the channel information.

**Samir:** Perfect. Alright, I think we're done. Anything else?

**Alberto:** No, I think that's comprehensive. Thanks, everyone. Let's have a successful UAT and get this thing launched.

**Clara:** Thanks, Alberto. See you Monday.

**John:** Looking forward to it.

---

## Action Items
- [ ] **Clara**: Merge FG-001 fix (duplicate sensor readings) to main branch — Due: 2025-10-24
- [ ] **Clara**: Implement sensor stale state indicator (FG-002: 3-minute threshold for "stale" status) — Due: 2025-10-25
- [ ] **Clara**: Update compliance PDF report template with customer name, site address, and DD.MM.YYYY date format — Due: 2025-10-25
- [ ] **Samir**: Confirm staging environment is fully populated with Milan site data and ready for UAT — Due: 2025-10-27
- [ ] **Samir**: Conduct UAT kickoff call with Alberto, Lucia, and Marco on Monday, October 27th — Due: 2025-10-27
- [ ] **Clara**: Develop CSV import tool for historical installation and client data — Due: 2025-11-07
- [ ] **Samir & Clara**: Deploy CSV import tool to production — Due: 2025-11-10
- [ ] **Samir**: Schedule post-launch monthly check-in with Innovative Windows LLC — Due: 2025-11-03
- [ ] **Lucia**: Brief Marco from Reseller Solutions on UAT participation, testing scenarios, and support contact information — Due: 2025-10-25

## Decisions Made
- **UAT Timeline**: October 27–31, 2025 with Milan staging environment
- **Go-Live Plan**: Phased rollout starting with Milan production sites (November 3rd), broader reseller rollout end of November
- **Known Bugs**: FG-001 (duplicate readings) to be merged pre-UAT; FG-002 (stale sensor indicator) to be deployed by UAT start
- **PDF Report Format**: Updated with customer name, site address, and regional date formatting (DD.MM.YYYY)
- **Data Migration**: CSV import tool to be built post-launch (week of November 3rd) for legacy installation records
- **MQTT Security**: Current username/password authentication acceptable for private internal network; TLS certificate upgrade recommended for future public deployment
- **Support Model**: Six months post-launch maintenance and support included; monthly check-ins scheduled
- **External Reseller Validation**: Marco from Reseller Solutions approved for UAT participation to validate reseller workflow and CSV export functionality
