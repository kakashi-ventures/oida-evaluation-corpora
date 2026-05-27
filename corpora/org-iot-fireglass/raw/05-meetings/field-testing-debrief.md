# Meeting Transcript: Field Testing Debrief — Milan Sites

**Date:** 2025-09-22
**Time:** 14:00 – 14:40 (CET)
**Location:** Video Call
**Attendees:** Samir Osei (Tech Lead/PM, Atlas Forge), Clara Duval (Junior Developer, Atlas Forge), John Smith (Field Technician, Atlas Forge)
**Facilitator:** Samir Osei
**Note-taker:** Clara Duval

---

## Agenda
1. Debrief on Milan field installations (3 sites)
2. Technical issues and sensor connectivity problems
3. Photo upload and offline sync limitations
4. Battery reporting bug and QR code feature feedback
5. Bluetooth fallback discussion for sensor pairing

---

## Transcript

**Samir:** Alright, so John, thanks for jumping on this. We really need to hear how the field testing went. Three sites, right? Can you walk us through each one?

**John:** Yeah, absolutely. So, um, I want to say it went pretty well overall, but there were definitely some hiccups. Let me start with Site 1 — that's the office building on Via Montenapoleone in the financial district.

**Samir:** Okay, Via Montenapoleone. That's the blue-chip office one.

**John:** That's the one, yeah. So that was probably the smoothest installation. Eight windows total, all of them got the Helion sensors installed cleanly. I mean, the WiFi coverage there was honestly... it was the best WiFi I've seen on a job site. Like, seriously. The building manager had just upgraded their network, so the signal strength was solid throughout. All eight sensors connected on the first or second try. No real drama with that one.

**Clara:** That's great. So the pairing process worked without issues?

**John:** Yeah, the pairing worked fine. It was literally — I open the app, scan the QR code on the sensor, um, it finds the WiFi network, and boom, it's connected. The whole thing probably took, I dunno, five minutes per sensor? Maybe less. It was smooth.

**Samir:** Excellent. Okay, what about Site 2?

**John:** Site 2 is the Navigli residential property. That one was, um, messier. We had five windows there, and I need to tell you, two of the sensors just... they had trouble connecting. And the reason became pretty clear when I got there — there's, like, a basement level that they want to monitor, and the WiFi just doesn't reach down there. It's stone walls, old building. The signal is basically nonexistent.

**Clara:** So you couldn't pair those sensors in the basement?

**John:** Exactly. I tried, and it was just timing out. So what I ended up doing — and this is not ideal, but it worked — I had to hotspot from my phone, right? I created a mobile hotspot, brought it down to the basement, got the sensors paired to that, and then... um, once they were connected, they actually picked up the building's regular WiFi when I brought the phone back upstairs.

**Samir:** Interesting. So they did eventually connect to the main network?

**John:** They did, yeah. But it took some fiddling. And the other thing is, um, I had a user experience moment there where I'm standing in a basement with a shovel in one hand and my phone in the other, trying to pair sensors. Not exactly, um, not exactly a smooth process to describe to the client.

**Clara:** No, I can imagine. Did you have any dropouts after the initial pairing?

**John:** Not really with those two, actually. Once they were connected, they seemed stable. But then, um, the other three sensors at that site were fine — normal pairing, no issues.

**Samir:** Okay, and Site 3?

**John:** Site 3 is the Porta Romana warehouse. This one was the most problematic, I have to say. Twelve windows total — large space, industrial environment. And, um, the WiFi interference there is significant. There's machinery running, forklifts with their own RF stuff, I dunno, just a lot of noise on the 2.4 GHz band.

**Clara:** How many of the sensors had issues there?

**John:** Well, they all paired okay, which was good. But one of them — and I documented this, I've got timestamps — one sensor started dropping intermittently. Like, every four hours or so, it would just disconnect and then reconnect a few minutes later. Very consistent pattern.

**Samir:** Every four hours? That's... actually, that sounds like it might be a WiFi power-saving feature or something on the access point itself. Did you check the router settings?

**John:** Um, I looked at it, but I'm not deep enough in networking to say for sure. The building manager said they hadn't touched anything recently. I did try moving the sensor to a slightly different location, and it helped a little, but the drops still happened.

**Samir:** We should probably investigate that one when we do the follow-up visit. Maybe it's a channel congestion thing, or the sensor firmware needs to handle reconnects better.

**John:** Yeah, that makes sense. Okay, so moving on — one thing I want to flag is the offline sync. I was hoping to be able to, um, capture sensor readings while offline and have them sync up later. But that didn't work the way I thought. The inspection form workflow saved locally, which was great, but sensor data readings... there was no offline capture for those.

**Clara:** Right, yeah. The sensor readings come directly from the MQTT stream. We haven't built offline queuing for that yet.

**John:** Exactly. And, um, honestly, it's not a deal-breaker for our use case, because we're always going to have WiFi at these sites. But it's worth knowing. The inspection form workflow, though, that actually works really well. I was able to fill out inspection forms, and the signature capture on my tablet — um, that was clean. The signature just worked.

**Clara:** Good. We've been testing that locally, but field validation is always different.

**John:** Yeah, so that part is solid. But, um, I did hit an issue with photo uploads. I was trying to attach photos of the installations to the inspection records, and I kept getting errors. Turns out there's a, um, a 5MB file limit on the uploads?

**Samir:** Ah, yeah. That's a safety guard we put in place early. Clara, wasn't that something we talked about?

**Clara:** It was, yeah. It's a hard limit we set in the server config. John, what kind of file sizes were you trying to upload?

**John:** I had some pretty high-res photos from my camera. Some of them were coming in at like 8, 9 MB, maybe even bigger. I had to basically, um, compress them on the fly using my phone, which is not ideal when you're in the field trying to document stuff.

**Samir:** Okay, so we need to increase that limit and probably add some automatic image compression on the client side. Clara, can you add that to the sprint?

**Clara:** Yeah, I'll put it down. Maybe we do like a 15 or 20 MB limit, and then compress anything larger before upload?

**Samir:** That sounds good. John, anything else?

**John:** Um, one more thing. I noticed the device battery percentage in the app — it's always showing 100%, even when I know the battery has been in use. The sensors should have some kind of battery monitoring, right?

**Samir:** They do, yeah. The Helion sensors report battery level over the MQTT stream. But, um, we might not be reading that field correctly. Clara, is that something you've seen?

**Clara:** We're parsing the MQTT payload, so it should be coming through. But I don't think we're actually storing it in the database yet. We're probably just ignoring that field.

**John:** Okay, so that's a bug.

**Clara:** Yeah, it is. It's on our list somewhere, but we should prioritize it. That's actual operational data.

**John:** For sure. Um, one positive thing I want to mention — the QR code scanning feature for window identification. That worked really well. I was able to scan the code, the app pulled up the right window record, all the details were there. That's actually a really nice workflow. Saves a lot of time compared to manually entering window IDs or looking things up.

**Samir:** That's good to hear. We spent some time on that, so I'm glad it's working.

**John:** Yeah, it definitely is. Um, so one thing the team was asking about — and I think this came up in some of the preliminary chats — is whether we could add Bluetooth as a fallback for sensor pairing. Because, like, the WiFi issues at Site 2 and Site 3 made me think, what if we could pair via Bluetooth first and then do the WiFi configuration after?

**Samir:** That's... actually not a bad idea. The sensors do have Bluetooth capability, right?

**John:** I think so, yeah. I'd have to check the specs, but it would solve the WiFi-first dependency.

**Clara:** That would add some complexity, but it's definitely doable. We'd need to build the Bluetooth pairing flow in the app, and then there's the whole question of what state the sensor is in post-Bluetooth pairing.

**Samir:** Let's add that to the backlog, but I don't think it's critical for the current release. John, is that something that would be a blocker?

**John:** No, no, I think we can work around it with the hotspot approach I did at Site 2. It's not elegant, but it works. Would be nice to have for future installations, though.

**Samir:** Okay, good. Um, before we wrap up — oh, actually, John, I wanted to ask. Did you have a chance to show anything to the clients at any of these sites?

**John:** Um, well, at Porta Romana, yeah. I showed the dashboard to the building manager — just the live sensor data view, you know, showing the readings coming in from all the windows. And, um, they actually loved it. They were really impressed. Said it was exactly what they were looking for.

**Samir:** Oh, that's great feedback.

**John:** Yeah, so, um, that's a good sign that the dashboard is actually addressing what they need.

**Samir:** Okay, excellent. Well, thanks for all of this, John. This is really useful data. Clara and I will get together and prioritize the fixes — the upload limit, the battery reporting, maybe add the Bluetooth stuff to the roadmap. And, um, we'll loop you in on any follow-up visits we need to do.

**John:** Sounds good. Happy to help. Let me know if you need anything else.

**Samir:** Thanks, John. Clara, you good?

**Clara:** Yeah, I've got notes. I'll get these into our system and we can plan the fixes.

---

## Action Items
- [ ] **Clara**: Increase photo upload file size limit to 15–20 MB and implement client-side image compression — Due: 2025-09-29
- [ ] **Samir & Clara**: Investigate battery reporting issue (`device_battery_pct` always showing 100%) — Due: 2025-09-26
- [ ] **Samir**: Investigate WiFi dropout pattern at Porta Romana Site 3 (intermittent disconnection every ~4 hours) — Due: 2025-10-03
- [ ] **Clara**: Add Bluetooth sensor pairing fallback to product backlog for future release — Due: 2025-10-15
- [ ] **Samir**: Schedule follow-up field visit to Porta Romana to troubleshoot sensor connectivity — Due: 2025-10-01

## Decisions Made
- Field testing validation: QR code scanning workflow approved for production use
- Offline sensor reading sync deferred (WiFi availability makes it non-critical for current use case)
- Bluetooth fallback pairing added to backlog but not prioritized for current sprint
