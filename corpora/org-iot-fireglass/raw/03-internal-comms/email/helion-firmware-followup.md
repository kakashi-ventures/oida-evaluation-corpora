# Email: Helion firmware docs — still waiting

**From:** Samir Osei <samir.osei@atlasforge.dev>
**To:** Clara Duval <clara.duval@atlasforge.dev>, John Smith <john.smith@atlasforge.dev>
**CC:**
**Date:** 2025-08-18 11:23
**Subject:** Helion firmware docs — still waiting

---

Team,

I've been chasing Helion for the complete HelionLink v2.3 protocol specification and firmware changelog. Sent two emails (Aug 10 and Aug 16) with no response beyond an auto-reply saying "we'll get back to you within 5 business days."

This is blocking our sensor integration work. We need clarity on the TG-400 heat sensor and SM-220 smoke detector firmware. Specific needs:
- Exact payload format for temperature/humidity/battery readings
- Update cadence constraints
- Error/alarm packet structure
- Known firmware quirks in batch deployments

John, I know you've been reverse-engineering payloads from the TG-400 demo unit we received at FireTech Europe last spring. How far have we gotten?

Clara, once John shares what he's figured out, can you start documenting it? Even incomplete docs are better than nothing — we can fill in gaps as we learn.

Worst case, we rely on John's field observations and hope for the best. Not ideal, but we're running out of time.

— Samir

---

**From:** John Smith <john.smith@atlasforge.dev>
**Date:** 2025-08-18 12:04
**Subject:** Re: Helion firmware docs — still waiting

Samir,

I've captured about 15 sensor payloads using a packet sniffer on the demo unit. The main fields I've identified so far:

- `sensor_id` (4 bytes, hex)
- `timestamp` (Unix epoch, 4 bytes)
- `temp_c` (float, 2 decimal places)
- `humidity_pct` (0-100, unsigned byte)
- `signal_strength` (RSSI, -120 to 0 dBm)
- `device_battery_pct` (0-100, unsigned byte)

There's a 2-byte checksum at the end (CRC-16, I think). Still don't know the heartbeat interval, whether we get partial packets on connection loss, or the alarm payload structure.

Attached a sample of captured payloads (see pyrosense-payload-samples.json). Can iterate as I get more data.

— John

---

**From:** Clara Duval <clara.duval@atlasforge.dev>
**Date:** 2025-08-18 14:51
**Subject:** Re: Helion firmware docs — still waiting

Great start, John. Samir, I can build a TypeScript decoder based on what John's figured out and mock the unknown fields. Once Helion gets back to us (or doesn't), we can validate against real payloads in the field.

I'll document assumptions and gaps in the decoder comments. Should keep us unblocked for sprint work.

— Clara
