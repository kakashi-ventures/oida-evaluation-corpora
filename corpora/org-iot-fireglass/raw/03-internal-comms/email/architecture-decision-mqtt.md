# Email: Architecture Decision — MQTT vs WebSocket

**From:** Samir Osei <samir.osei@atlasforge.dev>
**To:** Clara Duval <clara.duval@atlasforge.dev>
**CC:**
**Date:** 2025-08-05 14:32
**Subject:** Architecture Decision — MQTT vs WebSocket for IoT layer

---

Clara,

I've been thinking about the IoT data flow architecture, and I want to get your input before we commit to the implementation.

**Current thinking**: We use MQTT as the primary pub/sub layer between sensors and the backend. Sensors publish telemetry to an MQTT broker (HelionLink protocol wraps the payload). The Node.js backend subscribes to sensor topics, validates/stores readings in PostgreSQL, and emits events to connected clients via WebSocket.

**Why MQTT for sensors**:
- Native support in embedded systems and sensor firmware
- QoS guarantees (we need at least QoS 1 for reliability)
- Built-in pub/sub model — cleanly decouples sensor hardware from business logic
- Works across network boundaries with TLS/mTLS

**Why WebSocket for browsers**:
- MQTT.js exists and can run in browsers, but it adds ~50KB to the bundle
- We'd need to expose the MQTT broker to the internet (certificate management, DDoS risk)
- Connection pooling with WebSocket is simpler on the server side
- We still want an API layer for permission checks, audit logging, rate limiting

So the architecture is: **Sensors → MQTT → Backend → WebSocket + REST API → Dashboard UI**

Happy to discuss, but I think this gives us good separation of concerns.

— Samir

---

**From:** Clara Duval <clara.duval@atlasforge.dev>
**Date:** 2025-08-05 16:47
**Subject:** Re: Architecture Decision — MQTT vs WebSocket for IoT layer

Samir,

I read through the architecture doc, and I had a question. I looked up mqtt.js and it turns out you can actually run it in the browser. Couldn't we skip the WebSocket layer entirely? Sensors publish to MQTT, dashboard connects directly to the broker, subscriptions update in real time. Simpler topology.

What's the concern with exposing the MQTT broker? Feels like "DDoS risk" is solvable with a reverse proxy and rate limiting (which we need anyway for the REST API).

— Clara

---

**From:** Samir Osei <samir.osei@atlasforge.dev>
**Date:** 2025-08-05 17:55
**Subject:** Re: Architecture Decision — MQTT vs WebSocket for IoT layer

Clara,

Great question — I appreciate the pushback. You're right that mqtt.js works in browsers, and for a simple read-only dashboard your approach is actually elegant.

Here's the catch though:

1. **Permission scoping**: If a Technician's browser connects directly to MQTT, we can't enforce permission rules at the broker level. They could subscribe to any topic (e.g., `pyrosense/installation/999/temperature`). The reverse proxy can't easily block topics based on user roles. With WebSocket + API, we're filtering in application logic where we control RBAC.

2. **Audit trail**: Every telemetry read is a compliance touch point. We need server-side logging of "who viewed what reading when". Direct MQTT doesn't give us that for free.

3. **Bundle size** is real but not the biggest issue.

You're right that it's not unsolvable — we could add custom MQTT authentication plugins and broker-level ACLs — but that gets complex. The hybrid approach (MQTT backend, WebSocket frontend) is a more conventional pattern that lets us reuse our existing API middleware.

That said, your point has merit for the inspection dashboard use case. Maybe we revisit for Phase 2 if the WebSocket bottleneck becomes real.

Let's stick with the hybrid plan for MVP.

— Samir
