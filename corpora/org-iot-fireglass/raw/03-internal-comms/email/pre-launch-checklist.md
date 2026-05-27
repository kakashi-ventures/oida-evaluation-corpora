# Email: Pre-launch checklist — FireGlass MVP

**From:** Samir Osei <samir.osei@atlasforge.dev>
**To:** Clara Duval <clara.duval@atlasforge.dev>, John Smith <john.smith@atlasforge.dev>
**CC:**
**Date:** 2025-10-20 09:30
**Subject:** Pre-launch checklist — FireGlass MVP

---

Team,

We're 1 week out from UAT (week of Oct 27). Here's the pre-launch status checklist:

**DONE**
- [ x ] Authentication (Supabase JWT, role-based access)
- [ x ] CRUD operations for installations, windows, users
- [ x ] Inspection forms with offline sync
- [ x ] CASL permission middleware
- [ x ] TypeScript strict mode, linting, build

**IN PROGRESS**
- [ ] Sensor ingestion (real-time telemetry, deduplication)
  - [ ] Bug FG-001 (duplicate readings on reconnect) still open — investigating
  - [ ] Payload decoder working, CRC validation passes on test data
- [ ] PDF report generation (basic template done, needs styling)
- [ ] User manual (Clara drafting)

**PARTIAL**
- [ ] Offline sync (inspection forms only; sensor readings still require connectivity)
- [ ] MQTT broker (currently using Mosquitto dev instance — need to decide: managed Mosquitto cloud, AWS IoT Core, or on-prem?)

**NOT STARTED**
- [ ] Load testing (target: 50 concurrent sensor connections, API at p95 <500ms)
- [ ] Production database migration and backup plan

**BLOCKERS / DECISIONS NEEDED**
1. **MQTT hosting**: We need to pick a production broker by end of week
2. **Load testing timeline**: Can't ship without baseline numbers. Should we defer to Phase 2 if we run out of time?
3. **Compliance**: Argus Safety Group certification requirements (Alberto mentioned this in the last call)

Push hard on FG-001. Everything else is achievable.

UAT starts Oct 27. Client acceptance criteria TBD.

— Samir

---

**From:** Clara Duval <clara.duval@atlasforge.dev>
**Date:** 2025-10-20 11:15
**Subject:** Re: Pre-launch checklist — FireGlass MVP

Samir,

What about the compliance report template? Alberto mentioned Argus Safety Group cert requirements in the last call. Is that in scope for MVP?

Also, I'm almost done with the user manual. Should have drafts to you by EOD tomorrow.

— Clara

---

**From:** Samir Osei <samir.osei@atlasforge.dev>
**Date:** 2025-10-20 11:47
**Subject:** Re: Pre-launch checklist — FireGlass MVP

Good catch. Yes, I should have flagged that. Argus Safety Group compliance is in scope — it's a requirement for Alberto's insurance partners. I'm adding a compliance report template to the checklist (status: blocked, waiting for Argus Safety Group spec from client).

Can you check the test-plan for the acceptance criteria on that? I want to make sure we're aligned on what "compliance ready" means before UAT.

— Samir
