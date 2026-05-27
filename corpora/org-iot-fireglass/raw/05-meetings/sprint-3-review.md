# Meeting Transcript: Sprint 3 Review and Demo

**Date:** 2025-08-15
**Time:** 14:30 – 15:32 (CET)
**Location:** Video Call
**Attendees:** Alberto Neri (Innovative Windows LLC), Lucia Ferretti (Innovative Windows LLC), Samir Osei (Atlas Forge LLC), Clara Duval (Atlas Forge LLC), John Smith (Atlas Forge LLC)
**Facilitator:** Samir Osei
**Note-taker:** Lucia Ferretti

---

## Agenda
1. Sprint 3 deliverables demo
2. Customer management module walkthrough
3. Sensor dashboard and mock data architecture
4. Helion integration status and blockers
5. Field testing feedback from John Smith
6. Sprint 4 planning and priorities
7. Data access and permissions follow-up

---

## Transcript

**Samir Osei:** Alright, welcome to the Sprint 3 review. We're really excited to show you what we've built over the last two weeks. This sprint was all about getting the customer management module solid and building out the foundation for the sensor integration. Clara's going to walk through the UI, and then John's got some field testing insights. So Clara, why don't you start with a screen share?

**Clara Duval:** Yeah, okay, um, let me get my screen up. So, what you're seeing here is the Installations module. This is the main dashboard that a technician or manager would see. You can see a list view of all installations — this shows the customer name, the address, the window configuration, the installation date, and the current status. So "In Progress," "Completed," "Warranty," "Service Call," that kind of thing. You can click into any installation and see the full details.

**Alberto Neri:** Okay, this looks great. I mean, the layout is clean, the information is easy to find. But, um, where's the live sensor data? Like, I can see the installation details, but I'm not seeing any data from the Helion sensors that are actually installed there.

**Samir Osei:** Yeah, good question. So, that's coming. We've got the architecture in place for receiving sensor data, but we don't have actual sensor data flowing in yet. We're using mock data right now to test the dashboard layout and the real-time update mechanism. Um, Clara, can you show them the mock data setup?

**Clara Duval:** Sure. So, we've created a test environment where we simulate sensor readings coming in every sixty seconds. Each sensor publishes temperature in Celsius and smoke density readings to the MQTT broker. We're using Mosquitto locally for development, and then we subscribe to those topics in the application and update the dashboard in real time. So the data isn't real, but the pipeline is real. We're proving that the architecture works.

**Lucia Ferretti:** But when will you have actual sensor data?

**Samir Osei:** Um, that's where we're stuck a little bit. We're still waiting on the detailed documentation from Helion — the HelionLink protocol spec. Without that, we can't write the converter that translates their proprietary format into something we can use. We've been reaching out to their technical team, but the documentation hasn't come through yet.

**John Smith:** So actually, I've been looking at this from a different angle. I've got a demo unit of the Helion sensor, and I've been, uh, basically reverse-engineering the protocol over the last week. I've got some findings to share.

**Samir Osei:** Oh, John, that's fantastic. What have you got?

**John Smith:** Alright, so, the sensor sends out readings in JSON format. Temperature comes as a decimal in Celsius with two decimal places — so like 23.45. Smoke density is on a proprietary scale from zero to a thousand, not in micrograms per cubic meter like we might have assumed. Battery level, um, it always reads 100 on mains-powered units, which is what most of your installations are using. And the heartbeat interval — that's how often the sensor broadcasts — is locked at sixty seconds. You can't configure it. The device is pretty rigid about that.

**Alberto Neri:** Wait, so the documentation you're working from — is that something you reverse-engineered, or did Helion give it to you?

**John Smith:** I reverse-engineered it. I hooked up a logic analyzer to the serial output and decoded the messages. It's not pretty, but it works.

**Samir Osei:** John, that's great work. Um, but I want to note that ideally we'd have the official documentation. Not because your work isn't solid, but because if the firmware updates, the format might change and we'd need to adjust. So I'm still going to chase Helion, but your findings are incredibly valuable for the short term. Can you document this in a technical spec so we can reference it?

**John Smith:** Yeah, I'll put something together. It'll be informal, but it'll be clear.

**Clara Duval:** This is actually perfect because I was wondering about idempotency. Like, what happens if a sensor reading gets delivered twice due to a network issue? If we don't deduplicate, we'll double-count or get duplicate alerts. With the sixty-second heartbeat and the timestamp precision you found, we can use a combination of device_id and timestamp as an idempotency key.

**Samir Osei:** Exactly. Good thinking, Clara. So once we've got the official docs or John's spec is finalized, we'll write that into Sprint 4. Now, let me ask you this, John — you've been testing this in the field, right? Or at least simulating field conditions?

**John Smith:** Yeah, some. I've tested with the sensor in a basement, which is typical for where a lot of your installations end up. And that's actually where I want to raise a concern. The connectivity. The demo unit is struggling to maintain a connection in basements. WiFi is weak, and if you're in a concrete space, it drops out. I think offline mode is going to be critical. The sensor can't just fail when the network is down — it needs to cache readings and sync when it comes back online.

**Alberto Neri:** So if a technician is in the field and loses connectivity, the system just... stops?

**John Smith:** Not stops, but it can't report sensor data in real time if the connection is gone. The sensor might be recording locally, but we're not receiving it.

**Samir Osei:** That's a good point, and it's actually something we should design for. Let me add that to the backlog. We can build an offline sync mechanism where the mobile app or the field interface can cache data and push it when the connection returns. It's not super hard, but it's important for your use case.

**Alberto Neri:** Yeah, I think that's important. If we're asking technicians to rely on this system, it can't fail the moment they go underground.

**Clara Duval:** I actually started thinking about this already. I was sketching out a sensor simulator — basically a local service that can generate sensor readings and act as a fallback when the real broker isn't available. It's not complete, but I think it could be useful for testing and for offline scenarios.

**Samir Osei:** That's great. Hold on to that, Clara. We might lean on it more in later sprints.

**Alberto Neri:** So, when I look at this dashboard, um, I'm impressed with the interface. The layout is really clean. But honestly, I expected to see real sensor data by now. I mean, we're already three sprints in, and we're still showing mock data.

**Samir Osei:** I hear that, and I understand the frustration. The truth is, Helion's lack of documentation has been a blocker. But we're not sitting idle — we've been building the architecture, and now we've got John's reverse-engineering findings. In Sprint 4, we're going to focus hard on integrating real sensor data. We're confident that we can have at least basic Helion integration working by the end of that sprint.

**Alberto Neri:** Alright. And the Argus Safety Group audit is in November, so we're still on track for that?

**Samir Osei:** Yes. We've got about ten weeks left, and the compliance features are less complex than the sensor integration. We'll get to those.

**Lucia Ferretti:** I also wanted to ask again about my access to the admin dashboard. I was hoping I'd have it by now so I could start exploring the system.

**Clara Duval:** Oh, um, sorry about that. We have the authentication system in place, so we can definitely add a user account for you. You'll be able to log in by next week. Samir, we're good on that, right?

**Samir Osei:** Yes, absolutely. We'll create an admin user for Lucia before our next standup. I apologize that it slipped.

**Lucia Ferretti:** Thank you. I'd like to start playing around with the data entry so I can give feedback on the forms and the workflow.

**Alberto Neri:** That's good. Lucia's been in this business a long time, so her feedback is valuable.

**Samir Osei:** Agreed. Okay, so, let me talk about Sprint 4. Our main focus is going to be Helion integration. We're going to take John's spec, we're going to write the HelionLink converter, and we're going to connect real sensor data to the dashboard. We'll also start building out some of the visualization — like a heatmap view or a trend chart. Clara, we talked about a sensor heatmap component. Can you give Alberto a sense of what that would look like?

**Clara Duval:** Yeah, so the idea is you could see all your installations on a map, and each one is color-coded based on the current temperature reading from the sensor. Like, green might be normal, yellow is elevated, red is critical. It would update in real time as the data comes in. It's good for getting a quick visual sense of where your hot spots are.

**Alberto Neri:** That's exactly what I want. Can that be ready for the next sprint?

**Clara Duval:** Um, I think the component itself can be built pretty quickly. The main thing is, we need to know what the temperature ranges are for the color thresholds. Like, at what temperature does it turn from green to yellow? At what point is it a critical red? Right now I'm just using placeholder values.

**Samir Osei:** That's a good question for Helion when we get their documentation. Different window types or different installation types might have different safe temperature ranges.

**Alberto Neri:** I can probably figure that out. We have some safety guidelines from our suppliers. Lucia, do we have that documentation?

**Lucia Ferretti:** I can pull it. There's a standards doc from one of our glass suppliers that has thermal limits.

**Samir Osei:** Perfect. If you can get us those numbers, Clara can plug them in and we'll have a solid heatmap component.

**John Smith:** One more thing I want to mention — I was testing the sensor in a production installation last week, and I got the owner's permission to gather some data. The readings look consistent, no weird outliers, and the sixty-second interval is steady. I also noticed that the sensor broadcasts a heartbeat even when there's no change in readings. So we'll be getting a lot of status updates with the same data. That's why Clara's idempotency key thing is important.

**Samir Osei:** Good observation. Did you measure the MQTT message size?

**John Smith:** Yeah, they're small. Maybe, uh, a hundred and fifty bytes per message, uncompressed. So bandwidth isn't a concern.

**Clara Duval:** What about the frequency? You said heartbeat is every sixty seconds. Is that per sensor or per installation?

**John Smith:** Per sensor. So if an installation has three sensors, you're getting three messages every sixty seconds.

**Samir Osei:** Right. So with two hundred installations and maybe one-point-five sensors per installation on average, that's roughly three hundred sensors, three hundred messages per minute. We can absolutely handle that.

**Alberto Neri:** How about as we scale? You mentioned we'd probably hit four or five hundred installations. What's the load at that scale?

**Samir Osei:** So maybe four hundred and fifty installations, seven hundred sensors. That's about seven hundred messages per minute. Still very manageable. We might want to look at the broker setup — like, whether we use Mosquitto or a cloud-based MQTT service — but that's a tuning decision for later.

**Lucia Ferretti:** Is there a cost difference between those options?

**Samir Osei:** There could be. Cloud brokers charge per message or per device. Mosquitto is self-hosted and free. We'll evaluate that when we've got better data on actual throughput. Right now, Mosquitto is fine for development and early production.

**Alberto Neri:** Alright. What else is on the radar for Sprint 4?

**Samir Osei:** Beyond sensor integration, we're going to continue building out the customer management features — things like adding notes, tracking service history, that kind of thing. We're also going to start work on basic alerts. So if a sensor reading goes outside a normal range, the system sends a notification. That's pretty critical for your use case.

**Clara Duval:** I'm also thinking we should revisit the MQTT topic structure. Right now we're using `fire-glass/` as a prefix, but simpler might be better. Like just `fireglass/`. It doesn't really matter functionally, but for consistency and clarity, um, we should probably decide now before we build out too much.

**Samir Osei:** Good point. Let's keep `fire-glass/` for now since we've already documented it. We can always refactor later if it becomes an issue.

**Alberto Neri:** I appreciate the level of detail you all are going into. I want to make sure we've thought through the architecture. One question though — you mentioned storing both raw and processed sensor data. That still feels like it could bloat the database.

**Samir Osei:** It could, but we can manage it. We'll keep raw payloads for maybe a week, and processed data we'll keep longer — maybe thirty days online and then archive to cold storage after that. The nice thing about Postgres is it's really efficient with JSON blobs, and we can compress old data.

**John Smith:** Actually, I had another thought on the field side. We might want an export feature so technicians can pull down sensor data for a specific installation and take it offline. Like, if they need to show a customer a report of readings over the last month, they should be able to do that without being connected.

**Samir Osei:** That's useful. We can add that to the backlog. Might be a nice feature to have in Sprint 5.

**Alberto Neri:** Okay, I think I've got a clear picture. So, the real data is coming in Sprint 4, we've got offline mode as a priority, and we're moving toward something that actually looks and feels like a production system. Am I reading that right?

**Samir Osei:** Yes, exactly. Sprint 4 is when things really start feeling real. We'll have live sensor data, alerts, and the dashboard will be actually useful.

**Clara Duval:** I'm just hoping Helion comes through with those docs soon. John's reverse-engineering is solid, but it would be good to have official specs.

**Samir Osei:** I'm going to send them a follow-up email right after this call. We've been waiting three weeks, so I'll escalate a bit.

**Alberto Neri:** Yeah, please do. Tell them we've got a production timeline and we're depending on them. Sometimes that lights a fire.

**Samir Osei:** Will do. Alright, I think that's the main stuff. Let me just recap the action items and we can close out.

**Lucia Ferretti:** I have one more thing. When is the next demo? I want to make sure Alberto has it on his calendar.

**Samir Osei:** Same time, two weeks from now. August 29th, 2:30 PM CET.

**Lucia Ferretti:** Got it, I'll add it.

**Samir Osei:** Perfect. Thanks everyone. Good work, team. Clara, John, great effort in these first three sprints. And Alberto, Lucia, your feedback is really helpful. Let's keep this momentum going.

---

## Action Items
- [ ] **Samir Osei**: Send escalation email to Helion requesting HelionLink documentation — Due: 2025-08-15
- [ ] **John Smith**: Document reverse-engineered Helion protocol findings in technical spec — Due: 2025-08-18
- [ ] **Clara Duval**: Create admin user account for Lucia Ferretti and send login credentials — Due: 2025-08-18
- [ ] **Alberto Neri** / **Lucia Ferretti**: Provide sensor temperature threshold values from supplier safety guidelines — Due: 2025-08-20
- [ ] **Clara Duval**: Keep sensor simulator code for potential offline mode use in Sprint 4 — Due: TBD
- [ ] **Samir Osei**: Evaluate offline sync architecture and add to Sprint 4 backlog — Due: 2025-08-20
- [ ] **Samir Osei**: Plan MQTT broker evaluation (Mosquitto vs cloud) for future scaling — Due: 2025-08-30

## Decisions Made
- Mock data architecture validated; real Helion integration to begin in Sprint 4
- Offline mode confirmed as critical feature due to basement connectivity issues
- Sensor idempotency key will use device_id + timestamp combination
- MQTT topic prefix `fire-glass/` retained (not changing to simpler format)
- Both raw and processed sensor data will be stored (with tiered retention)
- Admin dashboard access for Lucia Ferretti to be enabled by Sprint 3 end
- Sensor heatmap component approved for Sprint 4 (pending temperature threshold values)
- Alerts system to be prioritized in Sprint 4
- Export functionality for sensor data to be added to future backlog (Sprint 5 consideration)
