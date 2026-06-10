# FireGlass Known Issues

**Last Updated:** 2026-03-24  
**Platform:** FireGlass CRM/IoT v2.1-beta  
**Client:** Innovative Windows LLC  
**Status:** Pre-Launch Assessment

---

## Critical Issues (Blocking Go-Live)

### FG-001: Duplicate Sensor Readings Under Concurrent Writes
**Severity:** Critical  
**Status:** In Progress  
**Component:** MQTT Message Handler, Sensor Data Pipeline  
**Assigned to:** Clara Duval  

**Description:**
When HelionLink system processes Helion TG-400/SM-220/AQ-100 sensor bursts (>10 readings/second during thermal events), the `sensor_readings` table experiences race conditions in the concurrent INSERT operation. The same reading with identical `sensor_id`, `timestamp`, and `temperature` value gets written 2-4 times. This corrupts historical data and causes false alarms in analytics dashboards.

**Root Cause:**  
Missing unique constraint on `(sensor_id, timestamp_ms)` combined with unsynchronized cursor advancement in the Node.js MQTT subscription handler.

**Impact:**  
- Data integrity violation; analytics reports show inflated event frequency
- Violates SLA reporting accuracy for client audits
- Blocks production deployment until resolved

**Workaround:**
Temporarily reduce sensor polling frequency to <2 readings/second in HelionLink v2.3 device config. This degrades fire detection responsiveness but prevents duplicates.

**Resolution Path:**  
- Add database-level unique constraint on `(sensor_id, timestamp_ms)`
- Implement message deduplication cache in MQTT handler (10-second sliding window)
- Add integration test with load simulation (>50 concurrent writes)

---

### FG-002: Sensor Timeout Handling — Offline/Zero Ambiguity
**Severity:** Critical  
**Status:** Open  
**Component:** Helion Sensor Driver, RLS Policy on sensor_readings Table  
**Assigned to:** Samir Osei  

**Description:**
When a Helion TG-400/SM-220/AQ-100 device goes offline (network loss, power loss), the system cannot distinguish between "device is offline and not reporting" versus "device is online and reporting legitimate zero temperature readings." Currently, both conditions result in NULL entries in `sensor_readings.temperature`. This causes:
- False negatives in thermal monitoring (fire condition never detected because system assumes device is working)
- Unnecessary maintenance alerts when device is intentionally powered down for testing

**Root Cause:**
The RLS (Row-Level Security) policy filters out NULL temperature readings, but doesn't log the `device_status` field. The HelionLink device driver has no heartbeat/keepalive mechanism.

**Impact:**  
- Unsafe operation; critical fire events may be missed
- Blocks go-live certification
- Field teams cannot diagnose equipment failures vs. legitimate low-temp conditions

**Workaround:**
Manually check device status in HelionLink v2.3 dashboard every 15 minutes. Not viable for unattended installations.

**Resolution Path:**  
- Add `device_status` enum column: `online`, `offline`, `offline_suspected`, `zero_reading`
- Implement 30-second heartbeat from Helion to MQTT broker
- Update RLS policy to expose `device_status` to analytics
- Add automated alert when device is offline for >5 minutes

---

## High-Severity Issues

### FG-003: Inspection PDF Generator Crashes on Special Characters
**Severity:** High  
**Status:** In Progress  
**Component:** Inspection PDF Generator, Report Engine  
**Assigned to:** Clara Duval  

**Description:**  
When an inspection report includes customer names, window descriptions, or notes containing non-ASCII characters (é, ñ, 中文, emoji), the PDF generation library throws an unhandled exception and the report fails to generate. Users can see the inspection data in the web UI but cannot export.

**Workaround:**  
Manually edit inspection notes to remove special characters before generating PDF.

**Status Update:**  
Narrowed to iText7 font encoding issue. Testing UTF-8 fallback font library.

---

### FG-004: RLS Policy Blocks Field Techs from Viewing Own Readings
**Severity:** High  
**Status:** Open  
**Component:** PostgreSQL RLS Policy, Authentication Layer  
**Assigned to:** Samir Osei  

**Description:**  
John Smith (Field Tech, user role: `field_technician`) cannot view sensor readings from installations he personally commissioned, because the RLS policy on `sensor_readings` requires a direct `user_id` match in the `readings_access` join table. Commissioned devices are assigned to the company, not individual techs.

**Impact:**  
Field technicians cannot verify their own work or troubleshoot on-site.

**Reported by:** John Smith (Field Testing)

---

### FG-005: MQTT Broker Connection Pool Exhaustion
**Severity:** High
**Status:** In Progress
**Component:** MQTT Connection Manager, HelionLink Integration
**Assigned to:** Clara Duval

**Description:**
Under prolonged operation (>48 hours), the MQTT connection pool leaks. Connections accumulate in `TIME_WAIT` state and eventually the broker rejects new client connections with "Connection Refused." System requires restart.

**Workaround:**
Restart the HelionLink gateway service daily.

---

### FG-005a: Helion SM-220 Failure in Extreme-Heat Testing
**Severity:** High
**Status:** Known Limitation
**Component:** Helion SM-220 Sensor, Hardware
**Assigned to:** Samir Osei

**Description:**
During Veridian TRC-500 test protocol evaluation at extreme temperatures (780°C sustained), Helion SM-220 smoke sensor units failed 3 out of 500 test cycles. Helion confirmed this failure rate is within acceptable tolerance for EPFC-2200 compliance standards. However, the manufacturer flagged this as a known limitation for extreme-heat environments and recommends supplementary cooling systems or alternative sensor placement in installations exposed to sustained >750°C thermal events.

**Impact:**
Minimal for standard fire-resistant window deployments (typical fire exposure rarely exceeds 600°C for extended periods). Not a go-live blocker, but should be disclosed to customers in high-risk industrial environments.

**Status:**
Documented for reference; no remediation required for current product launch.

---

### FG-006: Admin Dashboard Slow Query on Large Datasets (>50K Sensors)
**Severity:** High  
**Status:** Deferred  
**Component:** Dashboard Analytics, sensor_readings Index  
**Assigned to:** Samir Osei (backlog)  

**Description:**  
The admin dashboard "All Readings" view performs a full table scan without indexes on the 7-day filtered query, causing 15-30 second load times. Unacceptable for real-time operations.

**Workaround:**  
Filter by specific sensor or date range to reduce result set.

---

## Medium-Severity Issues

### FG-007: Offline Sync Conflict Resolution — Last-Write-Wins (Deferred, Important)
**Severity:** Medium  
**Status:** Deferred  
**Component:** Offline Cache, Sync Engine  
**Assigned to:** Product Backlog  

**Description:**  
When field techs lose connectivity and make edits to inspection data offline, then regain connection, the sync engine uses a naive "last-write-wins" approach. If HQ updates the same record while the tech is offline, the offline changes overwrite HQ's updates without warning.

**Example Scenario:**  
- Tech edits Window-A status to "Repaired" while offline
- HQ notes a compliance issue on Window-A and marks it "Needs Re-inspection"
- Tech's offline edit syncs and overwrites HQ's compliance flag
- No conflict notification occurs

**Current Rationale for Deferral:**  
Timeline pressure for launch; team decided to document and warn users. Merge-based resolution requires significant engineering investment (operational transformation or CRDT library).

**Future Priority:**  
High. Should be addressed in v2.2 post-launch.

---

### FG-008: PDF Export Memory Leak
**Severity:** Medium  
**Status:** Open  
**Component:** Inspection PDF Generator, Node.js Process  
**Assigned to:** Clara Duval  

**Description:**  
Generating >20 PDFs in rapid succession causes the Node.js process memory to spike and never release. After ~50 PDFs, process memory reaches 800MB+. Subsequent PDF generation is slow.

**Workaround:**  
Generate reports in small batches; allow 2-minute interval between batches.

---

### FG-009: Mobile Responsive Layout Breaks on Tablet (iPad Air Gen 5)
**Severity:** Medium  
**Status:** Open  
**Component:** Frontend UI, Responsive CSS  
**Assigned to:** Clara Duval (backlog)  

**Description:**  
At iPad landscape orientation (1180px width), the sensor graph overlaps the sidebar navigation, making the interface unusable. Affects <5% of user devices but breaks field tech workflows on tablets.

---

### FG-010: Sensor Reading Timestamp Timezone Ambiguity
**Severity:** Medium  
**Status:** In Progress  
**Component:** Sensor Data Pipeline, API Response  
**Assigned to:** Samir Osei  

**Description:**  
The API returns sensor readings with timestamps but no explicit timezone information. Client applications assume UTC, but HelionLink devices operate in local timezone. Causes 8-12 hour misalignment in time-series analysis for installations outside UTC regions.

**Workaround:**  
Append `Z` to timestamps to force UTC interpretation (workaround is unreliable).

---

### FG-011: Duplicate Email Notifications on Thermal Alerts
**Severity:** Medium  
**Status:** Won't Fix  
**Component:** Alert Engine, Email Service  
**Assigned to:** Samir Osei  

**Description:**  
When a sensor reads high temperature for >2 consecutive cycles, users receive 2-3 duplicate alert emails within 30 seconds due to missing deduplication in the notification queue. Not a logic error; users see the same alert twice.

**Rationale for Won't Fix:**  
Affects <3% of installations (only multi-sensor high-fire-risk sites). Requires architectural refactor of alert queue system. Cost/benefit not justified pre-launch. Post-launch, can address via simple message ID deduplication without major changes.

---

## Low-Severity Issues

### FG-012: Map Clustering Breaks on Firefox Mobile
**Severity:** Low  
**Status:** Won't Fix  
**Component:** Sensor Map View, Leaflet.js Plugin  
**Assigned to:** Clara Duval (closed)  

**Description:**  
The sensor location map uses Leaflet clustering plugin. On Firefox Mobile (iOS and Android), cluster markers fail to render and map becomes visually broken. Works on Chrome, Safari, and desktop browsers.

**Impact:**  
<2% of active users. Field techs primarily use Chrome on Android; desktop team uses desktop browsers.

**Rationale for Won't Fix:**  
Browser incompatibility affects minimal user base and does not block core functionality (manual sensor list view still works). Fixing requires Leaflet plugin rewrite or switching libraries. Deprioritized in favor of launch timeline.

---

### FG-013: "Export to CSV" Button Missing Tooltip
**Severity:** Low  
**Status:** Open  
**Component:** Frontend UI, Data Export  
**Assigned to:** Product Backlog  

**Description:**  
The "Export" button on the reports page lacks a tooltip. Users unfamiliar with the icon sometimes miss the export feature. Cosmetic issue.

---

### FG-014: Sensor Calibration Drift Not Logged
**Severity:** Low  
**Status:** Open  
**Component:** Helion Device Driver, Audit Log  
**Assigned to:** Backlog  

**Description:**  
When field techs recalibrate Helion sensors in the field, the system does not record the calibration event in the audit log. Makes it difficult to track sensor accuracy history.

---

## Summary Table

| Issue ID | Title | Severity | Status | Component | Assigned |
|----------|-------|----------|--------|-----------|----------|
| FG-001 | Duplicate Sensor Readings Under Concurrent Writes | Critical | In Progress | MQTT Handler | Clara Duval |
| FG-002 | Sensor Timeout Handling — Offline/Zero Ambiguity | Critical | Open | Helion Driver | Samir Osei |
| FG-003 | Inspection PDF Generator Crashes on Special Characters | High | In Progress | PDF Generator | Clara Duval |
| FG-004 | RLS Policy Blocks Field Techs from Viewing Own Readings | High | Open | Auth/RLS | Samir Osei |
| FG-005 | MQTT Broker Connection Pool Exhaustion | High | In Progress | MQTT Manager | Clara Duval |
| FG-005a | Helion SM-220 Failure in Extreme-Heat Testing | High | Known Limitation | Hardware | Samir Osei |
| FG-006 | Admin Dashboard Slow Query on Large Datasets | High | Deferred | Analytics | Samir Osei |
| FG-007 | Offline Sync Conflict Resolution — Last-Write-Wins | Medium | Deferred | Sync Engine | Backlog |
| FG-008 | PDF Export Memory Leak | Medium | Open | PDF Generator | Clara Duval |
| FG-009 | Mobile Responsive Layout Breaks on Tablet | Medium | Open | Frontend UI | Clara Duval |
| FG-010 | Sensor Reading Timestamp Timezone Ambiguity | Medium | In Progress | API/Data | Samir Osei |
| FG-011 | Duplicate Email Notifications on Thermal Alerts | Medium | Won't Fix | Alert Engine | Samir Osei |
| FG-012 | Map Clustering Breaks on Firefox Mobile | Low | Won't Fix | Map View | Clara Duval |
| FG-013 | "Export to CSV" Button Missing Tooltip | Low | Open | Frontend UI | Backlog |
| FG-014 | Sensor Calibration Drift Not Logged | Low | Open | Audit Log | Backlog |

---

## Release Blockers

**Must resolve before go-live:**
- FG-001 (Concurrency/Duplicate Reads)
- FG-002 (Sensor Offline Detection)

**All other issues tracked for post-launch sprints.**

---

*Document prepared for Innovative Windows LLC pre-launch review.*  
*Dataset provided under CC BY 4.0 License.*