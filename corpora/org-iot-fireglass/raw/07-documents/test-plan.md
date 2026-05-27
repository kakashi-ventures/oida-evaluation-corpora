# FireGlass v1.0 MVP — QA Test Plan

**Document Date:** 2025-08-19
**Prepared by:** QA Team (Atlas Forge LLC)
**Status:** Approved for Sprint 3 onwards
**Last Updated:** 2025-08-19

---

## 1. Test Scope & Objectives

### In Scope

- **Authentication & Authorization:** Login, role-based access, session management
- **Installation Management:** CRUD operations, bulk import, filtering
- **Sensor Dashboard:** Real-time data ingestion (Helion TG-400, SM-220, AQ-100), visualization, alert generation
- **Inspection Workflow:** Form submission, offline drafting, signature capture
- **Report Generation:** PDF/CSV export (with ASG-FP Level 2 compliance metadata), template rendering
- **API Endpoints:** REST interface for third-party integrations
- **Database Integrity:** Schema validation, migration testing, data consistency
- **Security:** Input validation, SQL injection prevention, XSS protection, CSRF tokens
- **Performance:** API response time, dashboard load time, report generation latency
- **Mobile/PWA:** Offline functionality, responsive layout, touch interaction
- **Hardware Validation:** Helion sensor compatibility validated per Veridian TRC-500 protocol (pre-deployment testing by Veridian Test Labs)

### Out of Scope

- **External integrations:** ERP system sync (deferred to v1.1)
- **Notification system:** Push notifications (descoped; replaced with CSV export)
- **Native mobile apps:** Android/iOS native (PWA only for v1.0)
- **Advanced analytics:** Machine learning anomaly detection (future enhancement)
- **Customer portal:** Facility manager read-only dashboard (v1.1 feature)
- **Full EU-SmartSafe Mark certification:** Cloud broker deployment deferred to v1.1 (EPFC-2201 §4.3)

---

## 2. Test Environments

### Development (Dev)

- **URL:** http://localhost:3000 (local Next.js dev server)
- **Database:** PostgreSQL (local Docker container)
- **Data:** Fresh DB snapshot from migrations; test fixtures
- **Refresh:** Automatic on code changes; manual reset available
- **Frequency:** Continuous integration on every commit to develop branch

### Staging

- **URL:** https://staging-fireglass.atlas-forge.dev
- **Database:** PostgreSQL (managed Supabase, separate from production)
- **Data:** Copy of production data (refreshed weekly) + test fixtures
- **SSL/TLS:** Valid certificate, HTTPS enforced
- **Refresh:** Deployed on every merge to staging branch (GitHub Actions)
- **Frequency:** UAT testing, integration testing, load testing

### Production

- **URL:** https://fireglass.innovativewindows.eu
- **Database:** PostgreSQL (managed Supabase, encrypted at rest)
- **Data:** Live customer data (confidential)
- **SSL/TLS:** Valid certificate, HTTPS enforced
- **Refresh:** Deployed manually via GitHub Actions (approval-gated)
- **Frequency:** Post-UAT, rollout strategy: canary (10% → 50% → 100%)

### Test Data

- **Sample Installations:** 100 test installations across 5 regions, with sensor IDs and lifecycle history
- **Sensor Data:** 500 Helion sensors with simulated readings (temperature, humidity)
- **Users:** Admin, Manager, Technician, View-Only test accounts with known credentials
- **Files:** Test images, CSV import samples, PDF report templates

---

## 3. Test Categories & Strategies

### Unit Tests

**Responsibility:** Developers (Clara Duval)
**Framework:** Jest + React Testing Library
**Coverage Target:** ≥80% code coverage
**Frequency:** On every commit

**Test Scope:**
- Prisma schema validation (database constraints)
- API route handlers (request/response validation)
- React component props validation and state management
- Utility functions (data transformation, formatting, validation)
- Error handling and edge cases

**Example Tests:**
```
✓ Authentication: Prisma User model validates email format
✓ Installation: API POST /installations rejects duplicate installation IDs
✓ Dashboard: SensorStatusCard renders traffic-light color correctly
✓ Forms: InspectionForm validation prevents submission with missing required fields
✓ Utils: formatSensorReading(23.456) returns "23.4°C" ±0.1°C
```

### Integration Tests

**Responsibility:** Clara Duval & QA team
**Framework:** Jest with supertest (API), Puppeteer (browser automation)
**Frequency:** Daily (on develop branch), before each release

**Test Scope:**
- API endpoint workflows (e.g., create installation → list installations → delete)
- Database transactions and rollback behavior
- Authentication flow (login → set JWT → access protected routes)
- Data sync between frontend and API
- File upload and image processing pipeline

**Example Tests:**
```
✓ E2E: Create Installation > Get Detail > Edit Metadata > Delete
✓ E2E: Import CSV installations > Verify row count > Query by region
✓ E2E: Login > Navigate Dashboard > Verify sensor data loads
✓ E2E: Upload inspection form > Generate report > Download PDF
```

### End-to-End (E2E) Tests

**Responsibility:** QA team with developer input
**Framework:** Playwright or Cypress (cross-browser automation)
**Frequency:** Before each sprint review, before production deployment
**Browsers:** Chrome, Firefox, Safari (latest versions)
**Devices:** Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)

**Critical User Journeys:**
1. **Field Tech Inspection Workflow**
   - Login with technician credentials
   - Search installation by location
   - Complete inspection checklist offline
   - Upload photos with annotations
   - Capture signature
   - Submit and sync on reconnect
   - Verify inspection in dashboard

2. **Manager Report Generation**
   - Login with manager credentials
   - Navigate to Reports
   - Configure report parameters (date range, installations, type)
   - Generate PDF and CSV
   - Verify content and formatting
   - Email report (mock)

3. **Admin Installation Bulk Import**
   - Login with admin credentials
   - Upload CSV (100 installations)
   - Preview and validate
   - Confirm import
   - Verify all installations in database
   - Spot-check sensor links

4. **Real-Time Dashboard Monitoring**
   - Login and navigate to dashboard
   - Observe sensor status cards updating (5-second polling)
   - Trigger synthetic sensor alert
   - Verify alert appears in feed within 5 seconds
   - Click alert and navigate to installation detail

### Performance Tests

**Responsibility:** Clara Duval & QA team
**Tool:** Lighthouse (web vitals), JMeter (load testing)
**Frequency:** Before each release, monthly stress tests

**Performance Targets:**
- **API Response Time:** ≤500ms (all endpoints, 95th percentile)
  - GET /api/installations/list: ≤300ms (for 500 installations)
  - POST /api/inspections: ≤400ms
  - GET /api/reports/generate: ≤5,000ms (5 seconds for PDF generation)

- **Dashboard Load Time:** First meaningful paint <2s, interactive <3s
- **Mobile PWA:** Lighthouse score ≥90 (Performance, PWA, Accessibility, Best Practices)
- **Database Query Time:** ≤100ms for common queries (indexed properly)
- **Concurrent Users:** Support ≥50 simultaneous API requests without degradation

**Load Test Scenarios:**
- 50 concurrent users logging in
- 100 concurrent sensor data ingestion requests (5-second interval)
- 10 concurrent report generation requests
- Dashboard refresh with 500 sensor updates per 5 seconds

### Security Tests

**Responsibility:** Clara Duval, external security consultant (contract)
**Frequency:** Pre-UAT (week 12), post-deployment (week 17)

**Test Scope:**
- **Authentication:** JWT token expiration, session hijacking, brute-force login attempts
- **Authorization:** RBAC enforcement (admin can't access technician-only routes; technicians can't modify reports)
- **Input Validation:** SQL injection (e.g., installation name: `'; DROP TABLE installations; --`)
- **XSS Prevention:** Embedded script in inspection notes: `<img src=x onerror="alert('xss')">`
- **CSRF Protection:** Form submissions with invalid CSRF tokens
- **Secrets Management:** No hardcoded API keys, database passwords in codebase or version control
- **HTTPS/TLS:** Valid certificate, secure cookie flags, HSTS headers
- **Data Privacy:** PII (contact emails, phone numbers) not logged; encrypted at rest

**Vulnerability Scanning:**
- OWASP Zap (automated web app scanner)
- npm audit (dependency vulnerabilities)
- SonarQube (code quality and security hotspots)
- Snyk (continuous vulnerability monitoring)

### User Acceptance Testing (UAT)

**Responsibility:** Client (Innovative Windows LLC) + QA support
**Duration:** 2 weeks (Sprint 7)
**Environment:** Staging (production-like, non-live data)
**Participants:** Alberto Neri (CEO), operations manager, 2–3 field technicians

**UAT Objectives:**
- Verify all MVP features work as intended
- Validate business process alignment (inspection workflow matches field operations)
- Confirm data accuracy (sensor readings, report generation)
- Assess usability (form complexity, navigation intuitiveness)
- Identify last-minute bugs or edge cases

**UAT Sign-Off Criteria:**
- ≥95% of test scenarios pass without critical defects
- All high-priority bugs resolved or documented as known issues
- Client approval signature on UAT report

---

## 4. Test Scenarios by Module

### Module 1: Authentication & Access Control

| Test ID | Scenario | Steps | Expected Result | Status |
|---------|----------|-------|-----------------|--------|
| AUTH-001 | Valid login | 1. Enter admin email & password<br>2. Click Submit | JWT token issued, dashboard loads | Pending |
| AUTH-002 | Invalid password | 1. Enter valid email, wrong password<br>2. Click Submit | Error message, no login | Pending |
| AUTH-003 | Account lockout | 1. Fail login 5× with wrong password<br>2. Attempt 6th login | Account locked for 15 min; error message | Pending |
| AUTH-004 | Session expiration | 1. Login<br>2. Wait 12+ hours<br>3. Perform action | Redirect to login, session expired error | Pending |
| AUTH-005 | RBAC: Technician access | 1. Login as technician<br>2. Access /admin/users | Access denied error (403) | Pending |
| AUTH-006 | RBAC: Admin access | 1. Login as admin<br>2. Access /admin/users | Admin users page loads | Pending |

### Module 2: Installation Management

| Test ID | Scenario | Steps | Expected Result | Status |
|---------|----------|-------|-----------------|--------|
| INST-001 | Create installation | 1. Navigate to Installations<br>2. Click "+ New"<br>3. Fill form (ID, name, location)<br>4. Submit | Installation created, appears in list | Pending |
| INST-002 | Edit installation | 1. Open existing installation<br>2. Edit name<br>3. Save | Metadata updated, no data loss | Pending |
| INST-003 | Delete installation | 1. Open installation<br>2. Click "Delete"<br>3. Confirm | Installation removed from list | Pending |
| INST-004 | Bulk import CSV | 1. Navigate to Installations<br>2. Click "Import CSV"<br>3. Upload file (100 rows)<br>4. Confirm | All 100 installations created, no duplicates | Pending |
| INST-005 | Filter by region | 1. Dashboard<br>2. Filter installations by "Central Europe"<br>3. Verify list | Only Central Europe installations shown | Pending |
| INST-006 | Search by ID | 1. Use search bar<br>2. Enter "FG-087"<br>3. Press Enter | FG-087 installation appears; others filtered | Pending |

### Module 3: Sensor Monitoring & Dashboard

| Test ID | Scenario | Steps | Expected Result | Status |
|---------|----------|-------|-----------------|--------|
| SENSOR-001 | Real-time updates | 1. Open dashboard<br>2. Observe sensor cards (Helion TG-400, SM-220, AQ-100)<br>3. Trigger synthetic sensor reading update | Cards refresh within 5 seconds; timestamp updates | Pending |
| SENSOR-002 | Status indicators | 1. View TG-400 with 22°C (normal)<br>2. View TG-400 with 35°C (alert) | Green indicator for normal, red for alert | Pending |
| SENSOR-003 | Alert trigger | 1. Sensor reading exceeds threshold<br>2. Observe alert feed | Alert appears in feed within 5 sec; severity color applied | Pending |
| SENSOR-004 | Installation offline | 1. Simulate sensor network outage<br>2. View installation detail after 2 min | Sensors marked "offline"; timestamp shows last reading | Pending |
| SENSOR-005 | Helion model specifics | 1. Dashboard shows installations with mixed sensor types<br>2. Verify TG-400 thermal range validation | TG-400 displays -20°C to +1200°C range; SM-220 smoke density threshold; AQ-100 VOC calibration verified | Pending |
| SENSOR-006 | Sensor readings export | 1. View installation detail<br>2. Click "Export"<br>3. Download CSV | CSV contains sensor ID, model, reading, timestamp for 7 days | Pending |
| SENSOR-007 | End-to-end alert latency (EPFC-2201) | 1. Trigger sensor threshold event<br>2. Measure time to dashboard notification | Alert appears in ≤10 seconds (EPFC-2201 requirement) | Pending |

### Module 4: Inspection Workflow

| Test ID | Scenario | Steps | Expected Result | Status |
|---------|----------|-------|-----------------|--------|
| INSP-001 | Create inspection | 1. Dashboard > Inspections<br>2. "+ New Inspection"<br>3. Select installation<br>4. Choose type (Preventive)<br>5. Complete checklist<br>6. Submit | Inspection saved, appears in list with timestamp | Pending |
| INSP-002 | Offline drafting | 1. Open inspection form<br>2. Go offline (DevTools > offline)<br>3. Complete form<br>4. Click Submit | Form saved to IndexedDB; queued for sync | Pending |
| INSP-003 | Sync on reconnect | 1. Offline form drafted & queued<br>2. Go online<br>3. Wait 5 sec | Form submitted to server, confirmed in list | Pending |
| INSP-004 | Checklist validation | 1. Open inspection form<br>2. Leave required field (e.g., seal integrity) blank<br>3. Click Submit | Validation error; form not submitted | Pending |
| INSP-005 | Photo upload | 1. Inspection form Step 4<br>2. Click camera icon<br>3. Select 3 test photos<br>4. Verify upload | Photos appear as thumbnails; metadata preserved | Pending |
| INSP-006 | Signature capture | 1. Inspection form Step 5<br>2. Sign on canvas<br>3. Click "Accept Signature" | Signature image stored; embedded in report | Pending |
| INSP-007 | Inspection history | 1. Open installation detail<br>2. View "Inspection & Lifecycle" section | All past inspections listed with dates, technician, status | Pending |

### Module 5: Report Generation

| Test ID | Scenario | Steps | Expected Result | Status |
|---------|----------|-------|-----------------|--------|
| REPORT-001 | Generate PDF | 1. Reports > "+ Generate"<br>2. Select "Compliance Summary"<br>3. Date range (30 days)<br>4. Format: PDF<br>5. Submit | PDF generated in ≤5 sec, downloadable, branded header with ASG-FP Level 2 metadata block | Pending |
| REPORT-002 | Generate CSV | 1. Reports > "+ Generate"<br>2. Type: "Maintenance Log"<br>3. Format: CSV<br>4. Submit | CSV generated, contains installation ID, date, technician, action; EPFC-2200 compliance tagged | Pending |
| REPORT-003 | PDF compliance metadata | 1. Generate compliance report<br>2. Open PDF<br>3. Verify metadata block | Includes installations, inspection dates, pass/fail, technician signatures, ASG-FP Level 2 certification level, audit date, Argus Safety Group reference number | Pending |
| REPORT-004 | Scheduled report | 1. Reports > "Scheduled Reports"<br>2. "+ Add"<br>3. Monthly, 1st of month, 9 AM<br>4. Save | Report generated automatically on schedule; email sent (mock) | Pending |
| REPORT-005 | Large dataset | 1. Generate report for 500 installations<br>2. Date range: 90 days<br>3. Observe generation time | Completes in ≤10 sec; no timeout | Pending |
| REPORT-006 | Report archive | 1. Reports tab<br>2. View archive of past 10 reports | All reports listed with generation date, type, format, download link; includes EU-SmartSafe Mark compliance status | Pending |

### Module 6: API Integration

| Test ID | Scenario | Steps | Expected Result | Status |
|---------|----------|-------|-----------------|--------|
| API-001 | List installations | GET /api/installations?limit=10&offset=0 | 200 OK, JSON array of installations | Pending |
| API-002 | Get installation detail | GET /api/installations/{id} | 200 OK, full installation object with sensor links | Pending |
| API-003 | Create installation | POST /api/installations with valid JSON payload | 201 Created, new installation ID returned | Pending |
| API-004 | Invalid request | POST /api/installations with missing required field | 400 Bad Request, error message | Pending |
| API-005 | Unauthorized access | GET /api/admin/users without admin token | 403 Forbidden | Pending |
| API-006 | Rate limiting | 100 requests to any endpoint in 1 sec | Rate limit exceeded; 429 Too Many Requests returned | Pending |

---

## 5. Performance Benchmarks & Targets

### API Performance

| Endpoint | Current Target | 95th Percentile | Notes |
|----------|----------------|-----------------|-------|
| GET /api/installations/list | ≤500ms | ≤600ms | Filters 500 installations; paginated |
| POST /api/inspections | ≤500ms | ≤600ms | Submit form + file upload |
| GET /api/installations/{id} | ≤200ms | ≤250ms | Fetch single installation + sensor data |
| GET /api/reports/generate | ≤5,000ms | ≤7,000ms | PDF generation for 500 installations |
| POST /api/sensor-readings | ≤100ms | ≤150ms | MQTT ingestion, batch insert |

**Baseline:** Establish using Apache JMeter or k6; retest monthly to detect regressions.

### Dashboard Performance (Lighthouse)

| Metric | Target |
|--------|--------|
| First Contentful Paint (FCP) | <1.5s |
| Largest Contentful Paint (LCP) | <2.5s |
| Cumulative Layout Shift (CLS) | <0.1 |
| Time to Interactive (TTI) | <3s |
| Performance Score (Lighthouse) | ≥90 |

### Mobile PWA (Lighthouse)

| Category | Target |
|----------|--------|
| Performance | ≥90 |
| Accessibility | ≥95 |
| Best Practices | ≥90 |
| PWA | ≥90 |

### Database Query Time

| Query | Current Target | Notes |
|-------|----------------|-------|
| SELECT installations WHERE region = ? | ≤50ms | Indexed on region |
| SELECT sensors WHERE installation_id = ? | ≤20ms | Indexed on installation_id |
| INSERT inspection + photos | ≤100ms | Transaction, batch photos |

---

## 6. Known Limitations & Exclusions

### Known Issues (To Be Documented Before UAT)

1. **FG-001:** Sensor table with 50+ rows may experience jank on low-end devices (Chrome Dev Tools throttling: Slow 4G + 4× CPU slowdown). Mitigation: virtualization (react-window) planned for v1.1.

2. **FG-002:** Offline inspection sync may fail silently if installation is deleted on server before reconnect. Mitigation: pending error handling flow definition (documented in data-sync-strategy.md).

3. **FG-003:** PDF report generation uses pdfkit, which may be slow for 500+ installations. Target generation time ≤10s; pending benchmark in Sprint 6.

### Deferred Features (Not in MVP)

- Push notifications (replaced with CSV export and email)
- Native iOS/Android apps (PWA only)
- Advanced BI dashboards with ML anomaly detection
- Customer portal (read-only facility manager access)
- ERP system synchronization

### Browser/Device Limitations

- **Unsupported Browsers:** IE 11 (end-of-life); Safari <13 (lack of modern JS features)
- **Offline Limitations:** Offline form drafting limited to IndexedDB (typically ≤50MB); large photo uploads may fail
- **Mobile:** Signature canvas performance on older Android devices (Android 5–7) may degrade; recommended min. Android 8

---

## 7. Acceptance Criteria for UAT Sign-Off

FireGlass v1.0 MVP is ready for production deployment when:

1. ✓ **Functional Completeness:** All user stories from Product Backlog completed and merged to main branch
2. ✓ **Test Coverage:** ≥80% code coverage for critical paths (auth, sensor ingestion, inspection, report generation)
3. ✓ **E2E Test Pass Rate:** ≥95% of critical user journey tests pass in staging
4. ✓ **Performance Baselines:** All API endpoints meet ≤500ms target (95th percentile); dashboard Lighthouse score ≥90
5. ✓ **Security:** No critical or high-severity vulnerabilities identified in penetration test; OWASP Zap scan clean
6. ✓ **UAT Sign-Off:** Client (Innovative Windows LLC) approves in writing; ≥95% of UAT scenarios pass
7. ✓ **Known Issues Documented:** All known limitations and deferred features documented in release notes
8. ✓ **Deployment Runbook:** Tested deployment procedure documented and rehearsed
9. ✓ **Rollback Plan:** Procedure for reverting to previous production version in case of critical issue
10. ✓ **Support Handoff:** Operations team trained on monitoring, logging, alert thresholds

---

## 8. Test Data Strategy

### Data Sets

- **Installations:** 100 test installations across 5 regions (Central Europe, North, South, East, West)
- **Sensors:** 500 Helion sensors (5 per installation); simulated readings in normal range
- **Inspections:** 50 completed inspections (mix of Preventive, Incident, Compliance types)
- **Users:** Admin (1), Manager (2), Technician (5), View-Only (3) test accounts
- **Files:** 10 sample CSV imports, 5 test images (for inspection upload), 3 report templates

### Data Reset

- **Dev Environment:** Automatic reset on each CI run (migrations from scratch)
- **Staging:** Weekly reset to fresh production snapshot + test fixtures
- **Production:** No automatic reset; only manual cleanup by ops team

---

## 9. Bug Severity & Prioritization

| Severity | Definition | Example | Fix Timeline |
|----------|-----------|---------|--------------|
| **Critical** | Feature completely non-functional; production data loss risk | Sensor data not ingesting; all reports blank | Fix immediately; block release |
| **High** | Major feature broken; workaround difficult | Dashboard doesn't refresh; inspection form submission fails | Fix before UAT; block release |
| **Medium** | Feature works but with significant limitation; workaround exists | Report generation takes 15s (target 5s); minor UI glitch | Fix before release; review case-by-case |
| **Low** | Minor cosmetic issue; feature works as intended | Button color doesn't match design; typo in label | Document for v1.1; not blocking |

---

## 10. Risk Assessment & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Sensor data ingestion delays >5s | Medium | High | Load testing in Sprint 4; MQTT broker scaling plan |
| PDF report generation timeout | Medium | High | Benchmark in Sprint 6; consider serverless option |
| Mobile offline sync data corruption | Low | High | Thorough integration testing; transaction-based sync |
| Security vulnerabilities in dependencies | Medium | High | npm audit on CI; Snyk continuous monitoring |
| UAT discovers workflow misalignment | High | Medium | Prototype inspection form with field techs early (Sprint 5) |
| Database query performance degrades at scale | Medium | Medium | Query optimization, indexing strategy; Monitor in staging |

---

## 11. Test Execution Timeline

| Phase | Sprint(s) | Duration | Lead | Deliverables |
|-------|-----------|----------|------|--------------|
| **Unit & Component Testing** | 1–6 (ongoing) | Per sprint | Clara Duval | Jest coverage reports, test suites |
| **Integration Testing** | 2–6 (ongoing) | Per sprint | QA team | Integration test reports |
| **E2E Testing** | 4–6 (ongoing) | 2 days/week | QA team | E2E test results, regression reports |
| **Security Testing** | 5–6 | 2 weeks | External consultant | Penetration test report, OWASP Zap results |
| **Load Testing** | 6 | 3 days | QA team + Clara | Performance benchmark report |
| **UAT (Client)** | 7 | 2 weeks | Client + QA support | UAT sign-off, defect log, release notes |
| **Production Smoke Test** | 8 | 1 day | Operations team | Go-live checklist, post-deployment validation |

---

## 12. Test Tools & Infrastructure

| Tool | Purpose | Status |
|------|---------|--------|
| Jest | Unit testing framework | ✓ Configured |
| React Testing Library | Component testing | ✓ Configured |
| Playwright / Cypress | E2E browser automation | Pending (Sprint 3 setup) |
| JMeter | Load & performance testing | Pending (Sprint 5 setup) |
| OWASP Zap | Web application security scanning | Pending (contract security consultant) |
| Lighthouse CI | Continuous performance monitoring | Pending (GitHub Actions integration) |
| Sentry | Error tracking & monitoring (staging/production) | ✓ Configured |
| DataDog / New Relic | APM monitoring (optional, pending budget) | TBD |

---

## 13. Test Metrics & Reporting

### Weekly Test Report

- **Test Execution Rate:** % of planned tests executed
- **Pass Rate:** % of tests passing (target: ≥95%)
- **Defect Density:** # bugs per 1000 lines of code
- **Coverage:** Code coverage %, E2E coverage (critical paths)
- **Performance Trends:** API response time trending, dashboard load time

### Sprint Review

- Test results summary (pass/fail, severity distribution)
- Known issues & risk log
- Recommendations for next sprint

---

**Document Status:** APPROVED FOR DEVELOPMENT
**Prepared by:** QA Team, Atlas Forge LLC
**Last Updated:** 2025-08-19 by [QA Lead]
**Next Review:** Sprint 3 (update with actual test results)

---

## APPENDIX: Performance Target Contradiction Note

**⚠️ KNOWN DISCREPANCY:**

This test plan specifies **API response time target of ≤500ms** (Section 5, table). However, user story **US-012** ("Sensor Dashboard Real-Time Updates") specifies a target of **<200ms**.

**Status:** This contradiction has been flagged to Samir Osei for clarification. For the purposes of Sprint testing, the team should test against BOTH targets:
- **Functional requirement:** <200ms (per US-012)
- **Test plan baseline:** ≤500ms (per this document)

The stricter <200ms target will be adopted once conflicting requirements are resolved. Pending clarification in Sprint 3 Sprint Planning.

---

## APPENDIX: Veridian TRC-500 Protocol & Compliance Requirements

**Hardware Validation:** Helion sensor compatibility (TG-400 thermal, SM-220 smoke, AQ-100 air quality) validated per **Veridian TRC-500 test protocol** conducted by Veridian Test Labs during pre-deployment phase (Sprint 5).

**Key Test Scenarios:**
- Helion TG-400 thermal range: -20°C to +1200°C (validated)
- SM-220 smoke particle density threshold compliance
- AQ-100 VOC (volatile organic compound) index calibration accuracy
- HelionLink v2.3 protocol handshake latency

**Compliance Output:** Pre-deployment validation certificate issued by Veridian Test Labs, referenced in ASG-FP Level 2 audit trail.
