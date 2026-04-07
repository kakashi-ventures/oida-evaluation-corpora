# Email: Field testing notes — Milan site visit

**From:** John Smith <john.smith@atlasforge.dev>
**To:** Samir Osei <samir.osei@atlasforge.dev>, Clara Duval <clara.duval@atlasforge.dev>
**CC:**
**Date:** 2025-09-15 18:42
**Subject:** Field testing notes — Milan site visit

---

Samir, Clara,

Just got back from the Milan install. Here's what happened:

**The good:**
- Installed 3 windows with sensors (units A, B, C)
- 2 of 3 came online immediately after power-up
- The UI picked them up no problem

**The problems:**
- Unit C drops connection intermittently (every 5-10 min). Alberto's site has a lot of WiFi networks (offices on 3 floors). Probably interference, but could also be power supply issue — I'll test a different outlet next week.
- `device_battery_pct` always reads 100% on all three. They're mains-powered, so that makes sense, but the firmware should maybe report a different value or null for mains units? Worth flagging to Helion if they ever respond lol.
- Offline mode worked fine for the inspection checklist forms (saved locally, synced later) but we get nothing for sensor readings. When the connection dropped, we couldn't log any temperature data. Field workers need that.
- I took a bunch of photos of the install (before/after, cable routing, etc.) but the photo upload failed — hit a file size limit. Had to compress everything to ~200KB each which is pretty low res. Not a blocker but annoying for documentation.

Next steps: I can swap the outlet on Unit C and re-test. But we should plan for unreliable connections in the architecture somewhere.

— John

P.S. Has anyone tried the new Thai place on Via Garibaldi? John recommended it — wait that's me. Never mind.
