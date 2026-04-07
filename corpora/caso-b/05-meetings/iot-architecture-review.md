# Meeting Transcript: IoT Architecture Technical Review

**Date:** 2025-09-02
**Time:** 10:00 – 10:47 (CET)
**Location:** Video Call
**Attendees:** Samir Osei (Atlas Forge LLC), Clara Duval (Atlas Forge LLC), John Smith (Atlas Forge LLC)
**Facilitator:** Samir Osei
**Note-taker:** Clara Duval

---

## Agenda
1. MQTT topic structure and naming conventions
2. Helion protocol findings and sensor payload analysis
3. Data deduplication and idempotency strategy
4. Raw vs processed data storage approach
5. Broker selection (Mosquitto vs cloud) for production scaling
6. Alert threshold configuration and sensor heatmap parameters
7. Sprint 4 implementation plan

---

## Transcript

**Samir Osei:** Alright, this is our internal architecture review for the IoT side of FireGlass. It's just us today, so we can dig into the technical details without needing to over-explain anything. John's done some great reverse-engineering work on the Helion protocol, and I want to make sure we've thought through all the architecture decisions before we start building in Sprint 4. So, let's start with the MQTT structure. John, you want to walk us through what you found?

**John Smith:** Yeah, sure. So the sensors (TG-400, SM-220, AQ-100) output JSON messages over the HelionLink v2.3 protocol, which then gets translated into MQTT. We've been using a topic structure of `fire-glass/` as the main namespace. So individual installations get their own topic tree. Like, an installation with ID "inst-001" has topics like `fire-glass/installations/inst-001/sensors/sensor-001/temperature` and `fire-glass/installations/inst-001/sensors/sensor-001/smoke-density`. Temperature readings are in Celsius with two decimal places. Smoke density is on Helion's proprietary zero-to-one-thousand scale, not in micrograms per cubic meter. We'll need to handle that conversion if customers ever want standard units.

**Clara Duval:** Okay, so I had a question about the topic structure. Why `fire-glass/` with a hyphen instead of just `fireglass/`? I mean, I'm looking at it, and the hyphen doesn't really add anything. It just makes it slightly more verbose.

**Samir Osei:** That's fair. Honestly, I think when we first documented it, we just went with what felt right. But you're right, there's no functional reason for the hyphen. We could simplify to `fireglass/`. The only thing is, we've already got some of that in the docs and in the mock simulator. Um, but it's not a huge deal to change it now if we want to.

**John Smith:** I'd say just keep it as is. We've got it documented with `fire-glass/`, and changing it now would just be busywork. It doesn't affect performance or anything.

**Samir Osei:** Yeah, you're right. Let's keep `fire-glass/` and move on. So, John, tell us about the sensor payload structure.

**John Smith:** Right. So each sensor publishes a JSON message that looks roughly like this — I'll describe it since I don't have it written out. The message includes a timestamp in ISO-8601 format, the device ID of the sensor, the current temperature reading in Celsius with two decimal places, the smoke density value on the zero-to-one-thousand scale, and a battery level. Now, here's the thing — the battery level always reads 100 on mains-powered units, which is basically all of them. It's not actually sending a meaningful battery percentage. That's something we should document because it might confuse users if they see battery at 100 percent forever.

**Clara Duval:** That's interesting. So we can basically ignore the battery field for mains-powered units?

**John Smith:** Yeah, exactly. Unless they ever sell battery-powered versions, which doesn't seem to be in the roadmap right now.

**Samir Osei:** Got it. And the heartbeat interval — that's the frequency at which the sensor publishes?

**John Smith:** Right. It's locked at sixty seconds. The TG-400 and SM-220 broadcast every sixty seconds, and that interval is not configurable from HelionLink v2.3. So even if the temperature hasn't changed since the last reading, you're still getting a new message with the same data. That's why we need deduplication.

**Clara Duval:** Which brings me to the idempotency question I've been thinking about. If the broker delivers the same message twice — which can happen with MQTT's "at least once" delivery guarantee — we need a way to recognize that it's the same reading and not process it twice. The idempotency key I proposed was device_id plus timestamp. Since the sensor publishes on a fixed sixty-second interval and includes a timestamp, we can use that combination to deduplicate in the application layer.

**Samir Osei:** Right. So basically, if we receive a message with device_id "sensor-001" and timestamp "2025-09-02T10:05:30Z" and we've already processed a message with that exact combination, we skip it. Is that what you're thinking?

**Clara Duval:** Exactly. We could hash the combination and store it in a cache with a TTL of maybe ten minutes. If we see the same hash, we know it's a duplicate.

**John Smith:** That sounds solid. We could do that in the MQTT listener before it hits the database. Prevents bad data from getting written in the first place.

**Samir Osei:** Good thinking. Alright, so that brings us to the data storage question. We've talked about storing both raw and processed sensor data. Let me lay out what I'm thinking. We have a `sensor_readings_raw` table where we store the complete MQTT payload as a JSONB column. That's forensics and debugging — if something goes wrong, we can look at the exact message that came in. Then we have a `sensor_readings` table with typed columns: device_id, installation_id, timestamp, temperature_celsius, smoke_density_scale, battery_level. We can have indexes on device_id and timestamp so queries are fast.

**Clara Duval:** What about retention? We can't keep raw data forever.

**Samir Osei:** Right. So my thinking is we keep raw data for one week online. After that, we can either delete it or archive it to cold storage like S3. For the processed data, we keep thirty days online in Postgres, and then we start aggregating. So instead of storing every single sixty-second reading for a sensor, we compute hourly averages, daily averages, and store those. That way, if you want to look at a trend over three months, you're not scanning millions of rows.

**John Smith:** That makes sense. But do we aggregate in real time or in a batch job?

**Samir Osei:** Probably a batch job. Like, every night at 2 AM, we run a job that computes the previous day's hourly and daily aggregates. That's simpler than trying to do it in real time, and it doesn't impact the live system performance.

**Clara Duval:** What if someone queries for a time range that spans both raw data and aggregated data?

**Samir Osei:** Good question. We'd query raw data for the recent period, and then aggregated data for the older period, and combine them in the application. A little more complex, but it works. We can optimize the queries to make it efficient.

**John Smith:** Okay, so that handles the data side. What about the broker infrastructure? Are we staying with Mosquitto?

**Samir Osei:** That's what I want to talk about next. Mosquitto works fine for development and early production. It's self-hosted, it's open source, it's free. But as we scale, there are pros and cons. If we're running it on our own infrastructure, we're responsible for uptime, scaling, monitoring, backups. If we go with a cloud broker like, um, let's say HiveMQ or AWS IoT Core or Google Cloud IoT, they handle all that, but they charge per message or per device.

**Clara Duval:** How much more expensive would a cloud option be?

**Samir Osei:** Depends on the volume. Let's say we're at max capacity — let me do the math. Seven hundred sensors, sixty-second heartbeat, that's about seven hundred messages per minute, forty-two thousand per hour, about a million per day. Some cloud brokers charge like fifty bucks per million messages. So we'd be looking at maybe one-fifty to two hundred a month at scale. Mosquitto, if we host it on a small server, might be fifty a month for the hosting.

**John Smith:** So Mosquitto is cheaper, but it requires us to manage it.

**Samir Osei:** Right. I'd say let's start with Mosquitto, ship it to production with Innovative Windows, and then if reliability becomes an issue or we start adding features that would be easier on a cloud platform, we can migrate. For now, Mosquitto is the right call.

**Clara Duval:** Okay, so back to the heatmap component that Alberto wanted. We need to know the temperature thresholds. Like, at what temperature is the sensor reading "hot" versus "critical" versus "normal"?

**Samir Osei:** Alberto and Lucia said they'd pull that from their supplier safety guidelines. Once we have those numbers, you can plug them into the heatmap. But here's the thing — we might have different thresholds depending on the window type or the installation location. Like, a window in direct sunlight might run hotter than one in a shaded location, but the maximum safe temperature is the same.

**John Smith:** So should the thresholds be configurable per installation?

**Samir Osei:** Maybe. Let's start with global thresholds and see if that's sufficient. We can always make them configurable later if customers ask for it.

**Clara Duval:** I'll build the component with placeholder values for now — like green for 0-40 Celsius, yellow for 40-60, red for 60 and above. Once we get the actual values from Alberto, I can update them. The component structure will support changing those easily.

**Samir Osei:** Perfect. One more thing I want to touch on — the alert system. We talked about alerts in the last client meeting, but we haven't designed it yet. When a sensor reading goes outside the safe range, what happens?

**John Smith:** Best practice would probably be a multi-channel notification. Like, an email to the site manager, a push notification to the mobile app, and maybe a webhook so they can integrate with their own systems.

**Samir Osei:** We can build the core alert logic in Sprint 4. Emails are straightforward — we can use Sendgrid or whoever. Push notifications need a mobile app, which we don't have yet. So let's start with email and in-app notifications, and we can add push later.

**Clara Duval:** Should there be different alert levels? Like, a warning that just logs something versus a critical alert that pages someone?

**Samir Osei:** Probably, yeah. Let me add that to the design. We can have severity levels — info, warning, critical. And different thresholds trigger different levels.

**John Smith:** I'm also wondering about alert fatigue. If the temperature bounces around the threshold, you don't want to send a hundred alerts in a minute.

**Clara Duval:** We could have a cooldown period. Like, once we send an alert for a device, we don't send another one for that same condition for thirty minutes. Or until the sensor reading goes back to normal and then exceeds the threshold again.

**Samir Osei:** Good idea. Let's call that "alert debouncing." I'll add it to the spec. Alright, I think we've covered the main architectural questions. Let me just recap what we're building for Sprint 4.

**John Smith:** So, to be clear, Sprint 4 is when we actually hook up the real sensor data?

**Samir Osei:** Yes. We're going to take your reverse-engineered Helion spec, write the HelionLink v2.3-to-MQTT converter, and start receiving real sensor readings from the TG-400 and SM-220 units. We'll implement the deduplication logic, build the alerts system with EPFC-2201 alert latency requirements (<10s end-to-end), and get the heatmap visualization working. That's a lot of work, but it's doable in two weeks if we stay focused.

**Clara Duval:** What about the offline mode that John brought up last sprint? Is that in scope for Sprint 4?

**Samir Osei:** It's on the radar, but it might slip to Sprint 5 depending on how the sensor integration goes. The core real-time stuff is the priority. We can always come back to offline caching.

**John Smith:** I've been thinking about offline mode, though. If the broker goes down or the connection drops, the system should gracefully degrade. Like, it should keep trying to reconnect without crashing.

**Samir Osei:** Absolutely. Resilience is important. We'll build that into the MQTT listener. Automatic reconnection, exponential backoff, that kind of thing.

**Clara Duval:** Um, I also started sketching out that sensor simulator I mentioned before. The idea is a little service that generates synthetic sensor readings that match the actual Helion format. It could be useful for testing scenarios, or like we talked about, for offline fallback mode. It's not done, but I've got a skeleton. Should I keep working on it?

**Samir Osei:** Yeah, definitely. Don't make it a priority, but keep it in your back pocket. It could be handy for testing the alert system before we've got real hardware, or for generating test data for load testing.

**John Smith:** One thing I want to clarify — when we're getting sensor data from real installations, are we planning to aggregate it by installation or by customer? Like, if a customer has multiple installations, do they see them separately or combined?

**Samir Osei:** Good question. I think we show them separately at first — each installation has its own dashboard view. But we could add a customer-level dashboard that shows all their installations at once. That's probably Sprint 5 stuff.

**Clara Duval:** That makes sense. And for the heatmap component, do we show all installations or let the user filter?

**Samir Osei:** All installations, but with filters. Like, filter by region, filter by status, filter by customer. Users can customize their view. Again, we can build that in phases.

**John Smith:** I had one more thought on the protocol side. The Helion sensor also publishes some diagnostic information — like signal strength, uptime. Should we capture that?

**Samir Osei:** Capture it, definitely. Store it in the raw data table. We might not display it in the dashboard right now, but it's useful metadata. As the system matures, we can build diagnostics features that use that information.

**Clara Duval:** Alright, I think I've got a clear picture of what we're building. Real sensor data, deduplication, alerts, heatmap visualization. The main dependency is getting the exact HelionLink spec from John's reverse-engineering documented, and then Alberto's temperature thresholds.

**Samir Osei:** Right. John, can you finalize that protocol spec by end of week?

**John Smith:** Yeah, I'll get it done. Maybe Wednesday or Thursday.

**Samir Osei:** Perfect. And I'm going to follow up with Helion one more time. If they come through with official documentation, we can validate it against John's findings. If not, we're good to go with what he's got.

**Clara Duval:** Is there anything else we should think about before we start building?

**Samir Osei:** Um, I don't think so. This feels solid. The architecture is straightforward, the data model is clean, and we've thought through the failure modes. I feel good about Sprint 4.

**John Smith:** One last thing — performance. Are we concerned about the database getting slow as data accumulates?

**Samir Osei:** Not for the first few months. But we should monitor it. If queries start to slow down, we'll add indexes or optimize the aggregation strategy. With the Postgres setup we're planning, we should be able to handle millions of readings without problems. If we start hitting limits, we can shard or add a time-series database like InfluxDB for metrics. But that's not a near-term concern.

**Clara Duval:** Alright. I think I'm ready to start coding. Should we schedule a quick sync before Sprint 4 starts to make sure everyone's on the same page?

**Samir Osei:** Yeah, let's do a thirty-minute call on Tuesday morning. We'll sync up on the exact API contract for the HelionLink converter, make sure we're all aligned on the data model, and maybe do a quick code review of John's protocol spec. Sound good?

**John Smith:** Works for me.

**Clara Duval:** Yep, I'm good.

**Samir Osei:** Great. Thanks, team. This was a productive call. We've got a solid plan, and I'm confident we can deliver on the real-time sensor features next sprint. Let's go build something cool.

---

## Action Items
- [ ] **John Smith**: Finalize reverse-engineered Helion protocol documentation with complete payload schema — Due: 2025-09-04
- [ ] **Samir Osei**: Follow up with Helion for official HelionLink specification — Due: 2025-09-03
- [ ] **Samir Osei**: Schedule pre-Sprint 4 technical sync meeting (Tue Sept 7) — Due: 2025-09-02
- [ ] **Clara Duval**: Continue development of sensor simulator for testing and potential offline fallback — Due: TBD (ongoing, lower priority)
- [ ] **Samir Osei**: Draft alert system specification with severity levels and debouncing logic — Due: 2025-09-05
- [ ] **Clara Duval**: Build heatmap component with placeholder temperature thresholds (pending Alberto's values) — Due: 2025-09-12

## Decisions Made
- MQTT topic prefix `fire-glass/` confirmed (retain hyphenated format for consistency with existing documentation)
- Sensor idempotency key will use device_id + timestamp hash with 10-minute cache TTL to prevent duplicate processing
- Dual storage approach approved: raw JSONB payloads (1-week retention) + typed processed columns (30-day retention with aggregation)
- Raw data older than 30 days to be archived to cold storage; daily aggregation job to run nightly at 02:00 CET
- Mosquitto MQTT broker selected for production (cost and simplicity advantages over cloud options; can migrate later if needed)
- Temperature thresholds for heatmap visualization to be sourced from customer supplier safety guidelines
- Alert system will support multi-level severity (info, warning, critical) with 30-minute debouncing per device
- Core sensor integration prioritized for Sprint 4; offline mode deferred to Sprint 5
- Real-time MQTT listener to include automatic reconnection with exponential backoff for resilience
- Customer-level aggregated dashboards deferred to Sprint 5 (focus on per-installation views first)
- Diagnostic metadata (signal strength, uptime) to be captured in raw data table for future feature development
