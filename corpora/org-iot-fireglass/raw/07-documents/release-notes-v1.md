# FireGlass v1.0.0-beta — Release Notes

**Release Date:** 2025-11-03
**Version:** 1.0.0-beta
**Status:** Production Deployment (Canary: 10% → 50% → 100%)
**For:** Innovative Windows LLC

---

## Overview

FireGlass v1.0.0-beta is the MVP release of the cloud-native CRM/IoT platform for real-time window installation monitoring, automated compliance reporting, and predictive maintenance scheduling. This release delivers the core functionality outlined in the project proposal (2025-07-21) and completes the 8-sprint development cycle.

**Release Duration:** July 21 – November 3, 2025 (16 weeks)
**Build Commit:** `git rev-parse HEAD` = `a3f7b9c2e1d8...` (full hash in deployment manifest)
**Tested On:** Chrome 118+, Firefox 119+, Safari 17+, mobile (iOS 15+, Android 10+)

---

## What's New in v1.0

### 1. Installation Management (Complete)

- **Installation Registry:** Create, read, update, delete (CRUD) operations for all window installations
- **Bulk Import:** CSV import for up to 500 installations at once with validation and preview
- **Geolocation Tagging:** Every installation mapped to physical location; searchable by region and facility
- **Metadata Tracking:** Installation lifecycle history (created, last inspected, last modified, assigned sensors)
- **Role-Based Visibility:** Technicians see assigned installations only; managers/admins see full fleet

**New in v1.0:**
- Hierarchical organization (Region → Facility → Installation) in sidebar navigation
- Installation search bar with fuzzy matching (location name, ID, facility code)
- Bulk edit (change status, assigned technician) for multiple installations
- Export installation roster to CSV (admin feature)

### 2. Real-Time Sensor Dashboard (Complete)

- **Live Monitoring:** Dashboard displays all active Helion sensors (TG-400 thermal, SM-220 smoke, AQ-100 air quality) with current readings
- **Traffic Light Indicators:** Green (normal), Amber (warning), Red (critical) status per sensor
- **Alert Feed:** Real-time notification of sensor threshold violations, anomalies, and lifecycle events
- **Map View:** Geographic visualization of all installations; click markers to view detail
- **Status Cards:** Installation-level overview (sensor count, online %, last reading time)
- **Configurable Thresholds:** Admins define alert thresholds per sensor type

**New in v1.0:**
- 5-second polling interval for sensor data (refreshes dashboard automatically)
- Sparkline charts (7-day trend) embedded in status cards
- Alert filtering (severity, source, date range)
- Offline alert history (last 100 alerts cached locally)
- Dark mode (manual toggle in Settings; auto-respects system preference)
- Sensor model-specific validation: TG-400 (-20°C to +1200°C thermal range), SM-220 smoke density, AQ-100 VOC calibration

### 3. Inspection Workflow (Complete)

- **Digital Inspection Forms:** Multi-step form for on-site inspection capture
- **Offline Support:** Forms drafted offline (IndexedDB); synced on network reconnect
- **Checklists:** Pre-configured checklists per inspection type (Preventive, Incident, Compliance)
- **Photo Upload:** Technician can capture and annotate photos on-site
- **Signature Capture:** Canvas-based signature capture for technician and facility manager sign-off
- **Timestamped Submission:** Every submission tagged with date, time, technician ID

**New in v1.0:**
- Photo compression (webp, 85% quality) to reduce upload size on slow networks
- Signature canvas library: signature_pad (active maintenance, broad browser support)
- Geolocation lock (GPS coordinates auto-captured on form submit if available)
- Inspection history timeline for each installation (sorted by date, searchable by technician)
- Bulk inspection scheduling (assign same inspection type to multiple installations)

### 4. Report Generation & Export (Complete)

- **Compliance Reports (PDF):** Standardized, customer-facing compliance summary with ASG-FP Level 2 certification metadata
  - Includes inspection history, sensor trend summary, technician sign-offs
  - Branded header with Innovative Windows LLC logo (provided by client)
  - Suitable for regulatory audits, ISO 9001 certification, EPFC-2200 compliance verification
  - ASG-FP Level 2 audit-ready PDFs with dual digital signatures

- **Performance Reports (PDF/CSV):** 30-day, 60-day, 90-day trend analysis
  - Sensor readings (temperature/humidity trends)
  - Alert frequency and severity
  - Predictive maintenance recommendations (based on trend slope)

- **Maintenance Log (CSV):** Chronological export of all maintenance activities
  - Installation ID, date, action type (inspection, sensor replacement, calibration)
  - Technician attribution, notes
  - Suitable for ERP system import

- **Custom Reports:** User-selected fields and date ranges exported to PDF or CSV

**New in v1.0:**
- Report generation latency: ≤5 seconds for 500 installations (95th percentile)
- Scheduled reports (daily, weekly, monthly) with automatic email delivery
- Report archive (storage of last 100 generated reports, with download/delete)
- PDF signature blocks for technician and facility manager attestation
- CSV export encoding: UTF-8 with BOM for Excel compatibility
- Compliance reporting module generates ASG-FP Level 2 audit-ready PDFs with dual digital signatures
- EU-SmartSafe Mark compliance metadata included in report headers

### 5. Authentication & Access Control (Complete)

- **Role-Based Access Control (RBAC):**
  - **Admin:** Full access (manage users, configure settings, view all data)
  - **Manager:** Operations management (schedule inspections, view all installations, approve reports)
  - **Field Technician:** Limited to assigned installations; can submit inspections
  - **View-Only:** Read-only access for stakeholders (facility managers, auditors)

- **Single Sign-On Readiness:** Provisioned for LDAP/Active Directory (integration in v1.1)
- **Session Management:** JWT tokens with 12-hour expiration; auto-refresh when active
- **Audit Logging:** All user actions logged (login, creation, modification, deletion) with timestamp and user ID

**New in v1.0:**
- User management interface (admin only): add/remove users, reset passwords, assign roles
- Two-factor authentication (2FA) optional (admin toggle); uses Time-based OTP (TOTP) via Authenticator apps
- Forced password reset on first login
- Account lockout after 5 failed login attempts (15-minute cooldown)

### 6. API for Third-Party Integration (Complete)

- **RESTful API:** Fully documented, versioned API (v1) for integration with ERP, CRM, BI tools
- **Authentication:** Bearer token (JWT); API key support (admin panel)
- **Endpoints:**
  - GET /api/v1/installations
  - POST /api/v1/inspections
  - GET /api/v1/reports/{id}
  - GET /api/v1/sensors/{installation_id}/readings
  - (15+ endpoints total; see API documentation)
- **Rate Limiting:** 1,000 requests per hour per client (upgradeable)
- **Data Format:** JSON request/response; ISO 8601 timestamps; OpenAPI 3.0 spec

**New in v1.0:**
- Webhook support (beta): POST to client-specified URL on inspection submission or alert trigger
- Pagination support (limit/offset) for large result sets
- Filtering and sorting on common fields (date, status, region)
- Batch operations (POST /api/v1/installations/bulk-import)

### 7. Progressive Web App (PWA) Features (Complete)

- **Offline Support:** Inspection form drafting works offline; syncs when reconnected
- **Home Screen Install:** "Add to Home Screen" banner on mobile devices
- **Service Worker:** Caches critical assets (JS, CSS) for faster repeat visits
- **Background Sync:** Pending submissions queue locally and transmit when online
- **Responsive Design:** Optimized for desktop (≥1024px), tablet (768–1023px), mobile (<768px)
- **Touch-Friendly:** 48px+ touch targets for field technician gloved hands

**New in v1.0:**
- Offline-first inspection form (IndexedDB persistence)
- Network status indicator (top-right corner: "online" / "offline" badge)
- Manual sync button (Sync icon) for user-triggered upload of queued data
- Capacity indicator: "Offline draft storage: 12 MB / 50 MB available"

### 8. Monitoring & Observability (Ops Support)

- **Error Tracking:** Sentry integration for real-time error reporting
  - Automatic error grouping and trend analysis
  - Source maps for production debugging

- **Logging:** Structured JSON logs (Winston) with context (user ID, request ID, action)
  - Log aggregation via ELK stack (Elasticsearch, Logstash, Kibana) — ops team responsibility

- **Uptime Monitoring:** Synthetic health checks (ping dashboard, API health) every 5 minutes
  - PagerDuty integration for alert escalation

**New in v1.0:**
- Health check endpoint: GET /api/health → { status: "ok", uptime_seconds: 123456, db_latency_ms: 45 }
- Performance metrics dashboard (admin view): API response time percentiles, dashboard load time, error rate trends

---

## Known Issues & Limitations

### Known Issues (Documented for v1.0 Production)

**FG-001: Sensor Table Performance on Low-End Devices**
- **Symptom:** Dashboard sensor table with 50+ rows may experience jank (frame drops) on low-end Android devices or when network is slow
- **Root Cause:** React re-renders entire table on sensor update; virtualization not yet implemented
- **Workaround:** Filter status cards to show fewer sensors at once; use "All Sensors" view instead of detail page
- **Planned Fix:** v1.1 (Sprint 9+) with react-window virtualization
- **Impact:** Low (cosmetic; feature works, performance degraded)

**FG-002: Offline Inspection Sync Edge Case**
- **Symptom:** If an installation is deleted from server while inspection form is drafted offline, form submission fails silently after reconnect
- **Root Cause:** Client-side validation doesn't check if installation still exists before upload
- **Workaround:** Check installation availability before submitting queued inspections; manual re-creation of form if needed
- **Planned Fix:** v1.1 with better error handling and user notification
- **Impact:** Low (rare scenario; data not lost, just queued locally)

**FG-003: PDF Report Generation Latency (Large Datasets)**
- **Symptom:** Generating compliance report for 500+ installations can take 8–12 seconds (target: ≤5s)
- **Root Cause:** pdfkit library sequential processing; no parallelization
- **Workaround:** Generate reports for ≤250 installations at a time; use async generation with email delivery
- **Planned Fix:** v1.1 with headless Chrome or serverless (AWS Lambda) PDF generation
- **Impact:** Medium (still usable; impacts user experience for large datasets)

---

## Deferred Features (Not in v1.0 MVP)

The following features were originally scoped but deferred to v1.1+ based on project timeline and prioritization:

1. **Push Notifications:** Originally planned for alert notifications. Deferred due to browser compatibility complexity. Replaced with:
   - CSV export of recent alerts
   - Email notification for critical alerts (admin configurable)
   - Polling-based refresh (5 seconds) in web UI

2. **Native Mobile Apps (iOS/Android):** Initially considered. Deferred in favor of PWA (cross-platform, no app store review cycle). Native apps reconsidered for v1.1 if market demand warrants.

3. **ERP System Integration:** Out-of-the-box connectors for SAP, NetSuite, etc. Deferred to v1.1. API-first design allows custom integration now.

4. **Advanced BI Dashboard:** ML-powered anomaly detection, predictive maintenance recommendations. Deferred to v1.1+. Basic trend charts included in v1.0 reports.

5. **Customer Portal:** Facility manager read-only access to their installation data. Deferred to v1.1. Workaround: export reports and email to customers.

6. **Multi-Language Support:** Internationalization (i18n) deferred. v1.0 English only. German translation planned for v1.1 (Q1 2026).

7. **Full EPFC-2201 §4.3 EU-SmartSafe Mark certification for cloud broker deployment:** Cloud deployment certification deferred to v1.1. v1.0 ASG-FP Level 2 on-premises compliance available.

---

## System Requirements

### Server Requirements (Hosting)

- **Platform:** Supabase (managed PostgreSQL)
- **Compute:** Vercel (serverless Next.js) or self-hosted (Docker, 2 CPU cores, 4 GB RAM minimum)
- **Database:** PostgreSQL 13+
- **Storage:** 100 GB (initial); scale as needed for sensor data retention (2-year historical)
- **Uptime SLA:** 99.5% (8 AM – 6 PM CET, business hours)

### Client Requirements (User Access)

- **Browser:** Chrome 118+, Firefox 119+, Safari 17+, Edge 118+ (latest 2 versions)
- **Mobile:** iOS 15+, Android 10+
- **Network:** Broadband (≥2 Mbps for dashboard; ≥1 Mbps for field forms)
- **Device:** Desktop (1920×1080 or higher), Tablet (iPad Air 2+, Android 8+), Smartphone (iPhone 11+, Android 10+)

### Helion IoT Requirements

- **Sensor Version:** Helion v2.x (HelionLink v2.3 protocol)
- **Sensor Models:** TG-400 (thermal, -20°C to +1200°C), SM-220 (smoke detection), AQ-100 (air quality/VOC)
- **MQTT Broker:** Accessible from FireGlass platform (network configuration: see IT setup guide)
- **Polling Interval:** 5 seconds (configurable by admin)
- **Expected Sensor Count:** 500–5,000 sensors per deployment (platform tested to 5,000)
- **Pre-Deployment Validation:** Veridian TRC-500 hardware compatibility testing required

---

## Getting Started

### For End Users (Field Technicians, Managers)

1. **Login:** Navigate to https://fireglass.innovativewindows.eu
2. **First-Time Setup:**
   - Enter email and temporary password (sent by admin)
   - Change password on first login
   - (Optional) Set up 2FA via Authenticator app
3. **Dashboard:** Review current installation status, sensor readings, pending inspections
4. **Mobile PWA:** Tap menu → "Install app" (mobile browsers) to add to home screen

### For Administrators

1. **User Management:** Admin panel → Users → invite new users, assign roles
2. **Installation Setup:** Import CSV of installations (template provided)
3. **Sensor Configuration:** Link Helion sensors to installations; set alert thresholds
4. **Scheduled Reports:** Configure daily/weekly/monthly compliance reports
5. **Monitoring:** Admin dashboard → Health checks, error logs, user activity

### Documentation

- **User Guide:** https://docs.fireglass.innovativewindows.eu/user-guide (PDF download available)
- **API Reference:** https://docs.fireglass.innovativewindows.eu/api
- **Admin Setup Guide:** https://docs.fireglass.innovativewindows.eu/admin-setup
- **Troubleshooting:** https://docs.fireglass.innovativewindows.eu/faq
- **Email Support:** support@atlas-forge.dev (4-hour response SLA during business hours)
- **Phone Support:** +49 (0)30 xxxx xxxx (Mon–Fri, 9 AM – 5 PM CET)

---

## Migration & Upgrade Path

### From v0.x (If Applicable)

FireGlass v1.0 is the initial production release; no prior versions in production. Test environment data is not migrated; use fresh database.

### Upgrading to v1.1+ (Future)

- Backward compatibility maintained (API v1 will be supported alongside v2 if breaking changes introduced)
- Data migrations provided for new schema versions
- Staged rollout recommended (staging → canary 10% → 50% → 100%)

---

## Security & Compliance

### Security Measures

- **HTTPS/TLS 1.3:** All traffic encrypted in transit
- **Data at Rest:** PostgreSQL encryption (AES-256)
- **Authentication:** JWT tokens, optional 2FA (TOTP)
- **RBAC:** Fine-grained role-based access control
- **Audit Logging:** All user actions logged immutably
- **Secrets Management:** API keys, database passwords stored in Supabase Secrets (not in code)
- **Dependency Scanning:** npm audit run on CI; Snyk continuous monitoring

### Compliance

- **Data Retention:** Sensor data retained for 2 years (configurable); manual deletion available
- **GDPR:** Data export and deletion mechanisms available for users
- **Audit Trail:** 100% of user actions logged for compliance audits (ISO 9001, building code)
- **Penetration Testing:** Conducted pre-release; no critical vulnerabilities found

### Data Privacy

- **PII Handling:** User emails and phone numbers encrypted in database
- **Logs:** No sensitive data (passwords, API keys) logged; service-level redaction enabled
- **Third-Party Access:** None (no analytics trackers, only Sentry error tracking in staging/production)

---

## Performance & Reliability

### Performance Benchmarks (Validated in Staging)

| Metric | Actual | Target |
|--------|--------|--------|
| Dashboard Load Time (FCP) | 1.2s | <1.5s ✓ |
| Dashboard Interactivity (TTI) | 2.8s | <3s ✓ |
| API Response (GET /installations) | 280ms | <500ms ✓ |
| Sensor Data Polling Latency | 4.8s avg | 5s ✓ |
| Report Generation (500 installations) | 4.2s | <5s ✓ |
| Mobile Lighthouse Score | 92 | ≥90 ✓ |

### Uptime & Reliability

- **Uptime Target:** 99.5% (8 AM – 6 PM CET business hours)
- **Recovery Time Objective (RTO):** <15 minutes (incident response, restart services)
- **Recovery Point Objective (RPO):** <5 minutes (database replication lag)
- **Incident Response:** On-call team available during business hours; escalation procedures defined

---

## Installation & Deployment

### Production Deployment

Deployed via GitHub Actions on merge to `main` branch. Requires approval from Release Manager (Samir Osei).

**Deployment Steps:**
1. Feature branch → GitHub Pull Request
2. CI checks pass (tests, lint, security scan)
3. Code review approval (≥2 maintainers)
4. Merge to `main`
5. GitHub Actions triggered: build Docker image, run smoke tests, deploy to canary (10%)
6. Monitor metrics for 30 minutes (error rate, API latency, uptime)
7. If healthy: promote to 50%, then 100%
8. Rollback plan: revert commit, re-deploy previous image within 15 minutes

**Rollback:** In case of critical issue, run GitHub Actions "Rollback" workflow to revert to last stable version.

### Docker Image

- **Registry:** Docker Hub (atlas-forge/fireglass)
- **Tag:** `latest`, `v1.0.0-beta`, `v1.0.0-beta-SHORTSHA`
- **Image Size:** ~450 MB
- **Build Time:** ~5 minutes

### Environment Variables

```
NODE_ENV=production
DATABASE_URL=postgresql://...  # Supabase connection
NEXTAUTH_SECRET=...  # Auth session secret
NEXTAUTH_URL=https://fireglass.innovativewindows.eu
MQTT_BROKER=mqtt://broker.example.com:1883
SENTRY_DSN=https://...  # Error tracking
```

See `.env.example` in repository for full list.

---

## Post-Launch Support

### 4-Week Stability Window

Following production deployment (2025-11-03), Atlas Forge team provides:

- **Daily monitoring:** Health checks, error logs, user activity
- **On-call support:** Samir Osei (PM), Clara Duval (Dev) on rotation
- **Bug fix SLA:** Critical bugs fixed within 4 hours; high-priority within 24 hours
- **Weekly sync:** Status meeting with Innovative Windows LLC operations team

### Handoff (Post-Stability Window, 2025-12-01)

- **Operations manual:** Runbooks for common tasks (restart service, database backup, log review)
- **Monitoring setup:** Sentry alerts, uptime monitoring, capacity planning
- **Support escalation:** Contact matrix, ticket system (Jira) setup
- **Training:** On-site training for admin users (optional, 8-hour session)

---

## Feedback & Support

### Reporting Issues

- **Bug Reports:** Email support@atlas-forge.dev with:
  - Browser / device information
  - Exact steps to reproduce
  - Screenshots / error messages
  - Expected vs. actual behavior

- **Feature Requests:** Document in Innovative Windows LLC Jira project or email support team

### Support Hours

- **Business Hours:** Monday–Friday, 9 AM – 5 PM CET
- **4-Hour Response SLA** during business hours (critical issues)
- **Extended Support:** Available for additional fees (24/7, off-hours)

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| 1.0.0-beta | 2025-11-03 | Production | Initial release |
| 0.9.0 (dev) | 2025-10-27 | Pre-release | UAT completion |
| 0.8.0 (staging) | 2025-09-15 | Testing | Feature freeze |

---

## Credits & Acknowledgments

**Development Team:**
- Samir Osei (Project Manager, Tech Lead)
- Clara Duval (Senior Full-Stack Developer)
- John Smith (Field Technology Specialist)

**Client Liaison:** Alberto Neri (CEO, Innovative Windows LLC)

**Special Thanks:** Innovative Windows LLC operations team for UAT participation and feedback.

---

## Next Steps & Roadmap (v1.1+)

**Planned for Q1 2026 (v1.1):**
- Sensor table virtualization (performance optimization)
- Push notifications (browser-based)
- German language support (i18n)
- Advanced BI dashboard with trend analysis
- ERP integration templates

**Planned for Q2 2026 (v1.2):**
- Native iOS app
- Native Android app
- SAP/NetSuite connector templates
- Customer portal (read-only facility manager access)

**Planned for Q3 2026 (v2.0):**
- ML-powered anomaly detection
- Predictive maintenance scoring
- Multi-tenant architecture (regional deployments)
- Advanced role definitions (custom RBAC)

---

**Release Prepared By:** Samir Osei, Atlas Forge LLC
**Date:** 2025-11-03
**Approved By:** Alberto Neri, Innovative Windows LLC CEO

---

*For the latest version, visit: https://docs.fireglass.innovativewindows.eu/release-notes*
