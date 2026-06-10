# Technical Requirements — Case B: FireGlass Platform

**Project**: FireGlass CRM/IoT Platform for Smart Fire-Resistant Windows
**Client**: Innovative Windows LLC
**Vendor**: Atlas Forge LLC
**Document Version**: 1.0
**Date**: 2025-07-21
**Prepared by**: Samir Osei, Tech Lead / Project Manager, Atlas Forge LLC

---

## Executive Summary

FireGlass is a comprehensive CRM and IoT management platform designed to enable Innovative Windows LLC to monitor, manage, and maintain a distributed fleet of smart fire-resistant windows equipped with integrated environmental sensors. The platform will support real-time sensor data ingestion, remote window diagnostics, maintenance scheduling, compliance reporting, and multi-role access control across technician, project manager, reseller, and end-user personas.

This document outlines the technical architecture, system requirements, integration points, authorization model, and known constraints that will guide development over the 15–17 week engagement.

---

## 1. Business Context & Objectives

Innovative Windows LLC manufactures fire-resistant window systems with embedded sensors measuring:
- **Heat** (ambient and edge temperature via Helion TG-400)
- **Smoke particle density** (optical sensor feedback via Helion SM-220)
- **Air quality metrics** (CO, CO₂, VOC via Helion AQ-100)

FireGlass will serve three primary use cases:

1. **Field Installation & Inspection**: Technicians (e.g., John Smith) inspect and validate window installations on-site using mobile devices, with offline capability for regions with spotty connectivity.

2. **Fleet Monitoring**: Project managers and resellers monitor sensor health and performance across customer installations in real-time, triggering alerts when thresholds are breached.

3. **Compliance & Reporting**: End users receive automated maintenance reports, maintenance history, and compliance documentation (with dual digital signatures) for fire safety audits.

---

## 2. Technology Stack & Architectural Decisions

### 2.1 Framework & Language

**Next.js 14 with TypeScript**

- **Rationale**: Unified JavaScript/TypeScript across frontend and backend (API routes) reduces context switching and allows rapid iteration. Next.js 14 provides:
  - Edge function support for low-latency API operations
  - Built-in image optimization (critical for PDF generation and mobile UX)
  - Incremental Static Regeneration (ISR) for report caching
  - Middleware support for authentication/authorization at the edge
  - Strong TypeScript support out of the box

- **Alternatives considered and rejected**:
  - **SvelteKit**: Excellent DX but smaller ecosystem for enterprise integrations; Prisma ORM tooling less mature.
  - **Remix**: Strong data-loading patterns, but OAuth/MQTT integrations require more custom scaffolding than Next.js.
  - **NestJS + React SPA**: Clean separation, but added deployment complexity for a 15-week sprint; monorepo overhead not justified.

### 2.2 Database & ORM

**PostgreSQL + Prisma**

- **PostgreSQL**: Mature, battle-tested for IoT data time-series patterns. Native JSON support for sensor payloads; Window functions for rolling averages on sensor telemetry.
- **Prisma**: Type-safe ORM with strong TypeScript integration. Migrations are version-controlled and reversible. Relation management simplifies the complex authorization queries (role inheritance, row-level security joins).

### 2.3 Authentication & Session Management

**Supabase (Auth + Row-Level Security)**

- **Supabase** provides PostgreSQL + Auth as a managed service, eliminating operational overhead:
  - JWT token generation with custom claims (role, customer_id, site_id)
  - Built-in OAuth2 providers (optional future enhancement)
  - Row-Level Security (RLS) policies enforced at the database layer (see Section 5)
  - Real-time subscriptions via WebSocket (critical for live sensor dashboards)

- **JWT Token Strategy**:
  - Access token: 15-minute expiry (security hardening; refresh token rotation per OAuth 2.0 best practice)
  - Refresh token: 7-day expiry, rotated on use
  - Custom claims embedded: `user_id`, `role`, `customer_id`, `site_id`, `organization_id`
  - Token validation occurs at middleware layer (Next.js middleware) and database layer (RLS policy checks)

### 2.4 Real-Time Communication

**MQTT + WebSocket Hybrid Strategy**

- **MQTT (IoT ↔ Backend)**: Helion sensors (fire-resistant window environmental sensors) transmit readings via MQTT protocol to a broker (hosted on Supabase or self-managed). Topic structure:
  ```
  fire-glass/customer/{customer_id}/site/{site_id}/window/{window_id}/{metric}
  # Example: fire-glass/customer/cust-001/site/site-A/window/win-042/heat
  ```
  Payload format follows HelionLink v2.3 specification — see mqtt-protocol.md for full schema.

- **WebSocket (Backend ↔ Frontend)**: Real-time dashboard updates; technicians receive live alerts when thresholds are breached. Supabase Realtime subscriptions handle client-side subscriptions to PostgreSQL changes.

- **Rationale for hybrid**: MQTT is industry standard for IoT device communication; WebSocket provides responsive UI feedback without polling overhead.

- **Known tension** (to be resolved in design phase): Frequency of sensor polling vs. event-driven ingestion. High-frequency polling (sub-second) reduces latency but increases broker load and database write volume. Event-driven (threshold-triggered) reduces noise but may miss transient spikes. Design will establish compromise: sensors emit readings every 5 seconds; application logic filters and aggregates.

### 2.5 File Storage & Document Management

**Supabase Storage (AWS S3 backend)**

- PDF reports generated server-side (Node.js library: `@react-pdf/renderer` or `pdfkit`)
- Dual digital signatures appended to PDFs (technician + end-user consent forms)
- QR codes embedded in PDFs for off-chain window identification verification

### 2.6 Mobile & Progressive Web App

**React Native / Web (Mobile-First Mandatory)**

- Primary interface: responsive React web app (Next.js + React)
- Mobile-optimized: touch-friendly buttons, large tap targets (48px minimum)
- Technician workflow: offline-first architecture using IndexedDB for local cache; sync to backend when connectivity restored
- **Offline requirements**: Technicians must be able to:
  - Access cached inspection forms
  - Capture sensor readings (via Bluetooth or manual entry if hardware unreachable)
  - Generate inspection checklists
  - Take photos/annotate windows
  - All data queued for sync upon reconnection

---

## 3. Authorization & Access Control Model

### 3.1 Six-Role Hierarchy

| Role | Scope | Primary Capabilities |
|------|-------|---------------------|
| **Admin** | Organization-wide | Full read/write/delete; user management; system configuration; billing |
| **Reseller** | Multiple customer accounts (as assigned) | Manage assigned customers' projects, technicians, reporting; no system config |
| **Project Manager** | Single or multiple sites (customer-level) | Create inspections, review reports, assign technicians, export compliance docs |
| **Technician** | Assigned sites/windows | Field inspection, sensor capture, photo upload, signature collection |
| **Site Manager** | Single customer account; all sites | Read-only dashboards, maintenance history, approve technician sign-offs |
| **End User** | Single window / customer property | View maintenance reports, acknowledge alerts, basic sensor history |

### 3.2 Authorization Implementation: CASL + Row-Level Security

**Frontend Authorization (CASL)**

- CASL.js rules engine defines what actions (read, create, update, delete) are permissible for each role
- Rules fetched from backend on login and cached in Redux/Context
- Example rule (pseudo-code):
  ```javascript
  ability.can('read', 'Inspection', { site_id: user.site_id })
  ability.can('update', 'Report', { author_id: user.id })
  ```

**Backend Authorization (PostgreSQL RLS + Prisma)**

- Every table with sensitive data enforces RLS policies
- Policies are row-level: users see only rows matching their `customer_id`, `site_id`, or `organization_id`
- Example RLS policy for `inspections` table:
  ```sql
  CREATE POLICY inspect_user_sites ON inspections
    FOR SELECT
    USING (site_id IN (
      SELECT site_id FROM user_site_access WHERE user_id = auth.uid()
    ))
  ```

- **Rationale**: Supabase's managed RLS + Prisma ensures authorization is enforced at the database layer, preventing accidental data leaks if API logic is compromised.

### 3.3 Multi-Tenancy & Data Isolation

- **Organization model**: Innovative Windows LLC is Organization A; future resellers are additional Organizations
- **Tenant key**: `organization_id` + `customer_id` embedded in all queries and JWT claims
- **Scoping**: Queries automatically filtered by JWT claims at Prisma middleware layer
- **Audit logging**: All mutations (create, update, delete) logged with `user_id`, `timestamp`, `organization_id`, `action`

---

## 4. Core Data Model & Entities

### 4.1 Primary Entities

```
Organization
  ├── Customer
  │    ├── Site
  │    │    ├── Window
  │    │    │    ├── Sensor (Helion device)
  │    │    │    │    └── SensorReading (real-time telemetry)
  │    │    │    └── Inspection
  │    │    │         └── InspectionSignature (technician + end-user)
  │    │    └── Maintenance (scheduled or reactive)
  │    │         └── MaintenanceReport (PDF + dual signature)
  │    └── User (Project Manager, Site Manager)
  ├── Technician (field staff)
  └── Reseller (partner)
```

### 4.2 Sensor & Telemetry Schema

**Helion Sensor Device** (TG-400, SM-220, AQ-100):
- `sensor_id` (unique identifier, linked to window)
- `firmware_version` (vendor-provided; auto-detection on first pairing)
- `last_heartbeat` (timestamp; used to detect offline sensors)
- `calibration_date` (maintenance record)
- Hardware compatibility validated against Veridian TRC-500 test protocol (500 thermal cycles, 72h smoke exposure)

**SensorReading**:
- `reading_id` (UUID)
- `sensor_id` (foreign key)
- `metric` (enum: `heat`, `smoke`, `air_quality`)
- `value` (float)
- `unit` (°C, ppm, µg/m³)
- `timestamp` (UTC, precision: millisecond)
- `status` (enum: `ok`, `warning`, `critical`)

### 4.3 Inspection & Maintenance Workflow

**Inspection**:
- Created by Technician or Project Manager
- Captures checklist responses, sensor readings, photos
- Status: `draft`, `submitted`, `approved`, `rejected`
- Linked to Window and Technician

**MaintenanceReport**:
- Generated from Inspection
- Contains: summary, photo gallery, sensor history graph, recommendations
- Dual signature fields: technician_signature (digital), end_user_signature (digital)
- Format: PDF + JSON metadata
- Language: IT (default) or EN (user-selectable)

---

## 5. Integration Points

### 5.1 Helion Sensor Hardware Integration

**Challenge**: Helion firmware documentation is **pending from hardware vendor** (as of kickoff). Requires vendor API spec or MQTT protocol definition.

**Assumptions** (to be validated):
- Sensors communicate via MQTT with JSON payloads
- Topic structure: `{device_id}/{metric}`
- Payload format:
  ```json
  {
    "sensor_id": "win-042-heat",
    "value": 42.5,
    "unit": "celsius",
    "timestamp": "2025-08-15T10:30:45Z",
    "battery_level": 87
  }
  ```

**Integration approach**:
- MQTT client (Node.js library: `mqtt`) subscribes to all topics
- Message handler validates payload, persists to PostgreSQL `SensorReading` table
- Anomalies (missed heartbeats, out-of-range values) trigger alert pipeline

### 5.2 PDF Report Generation & Digital Signatures

**Library**: `react-pdf` or `pdfkit` (decision pending)

**Workflow**:
1. Report template populated with inspection data + sensor graphs
2. QR code generated (links to window record in FireGlass)
3. Report hashed for integrity verification
4. Technician signs via on-screen pad or stylus (captured as image blob)
5. PDF embedded with technician signature
6. Report sent to End User (via email + dashboard download)
7. End User signs PDF (analog or digital) and uploads
8. Final PDF archived in Supabase Storage

### 5.3 Email & Notifications

**Service**: Supabase Email (PostMark backend) or SendGrid integration

**Triggers**:
- Threshold breaches: alert email to Project Manager + Site Manager
- Report ready: email to End User with PDF download link
- Maintenance reminder: scheduled email 30 days before calibration due

### 5.3a Compliance Standards

All IoT-connected components must adhere to the following standards:
- **EPFC-2200**: Passive fire protection performance requirements
- **EPFC-2201**: Connected systems extension, including HelionLink API latency requirements of <10s for critical alerts
- **EU-SmartSafe Mark**: All IoT components must achieve EU-SmartSafe Mark compliance (E2E encryption, secure OTA firmware updates, electrical isolation per EPFC-2201 §4.3)

### 5.4 Mobile Bluetooth Integration (Optional Phase 2)

**Out of scope for MVP** but designed for future expansion: Technicians may pair Helion sensors directly via Bluetooth Low Energy (BLE) for in-field verification before MQTT handshake.

---

## 6. Multi-Language & Localization

**Supported Languages (MVP)**:
- Italian (default, for Innovative Windows LLC and Verona-based customers)
- English (for international resellers and technical documentation)

**Approach**:
- i18n library: `next-intl`
- Translation files: JSON, organized by domain (auth, inspection, reports, alerts)
- Database support: `language_preference` field on User record; `language` parameter in report generation API
- Dynamic imports for language-specific date/number formatting

---

## 7. Constraints & Known Limitations

### 7.1 Offline Capability (Partial)

**Requirement**: Technicians work in areas with unreliable connectivity; must continue inspections offline.

**Implementation**:
- IndexedDB cache stores: inspection forms, cached window/site metadata, baseline sensor readings
- Service Worker syncs queued mutations to backend when connectivity restored
- **Limitation**: Real-time sensor data is NOT available offline (requires live MQTT connection); technicians can only view cached historical data or manually enter readings

**Mitigation**: Field technicians briefed to capture manual readings (via physical gauge or form entry) if hardware unavailable; data reconciled post-sync.

### 7.2 Third-Party Sensor Firmware Documentation (Pending)

**Status**: Helion vendor has not yet provided:
- MQTT protocol specification
- JSON payload schemas
- Firmware update procedures
- Hardware error codes / diagnostic messages

**Risk**: Implementation of IoT integration may require rework once documentation arrives; timeline may slip if vendor delays exceed 2 weeks.

**Mitigation**: Develop abstract sensor interface (TypeScript interface `ISensorDriver`) to allow easy swapping of implementations; mock sensor driver for development/testing.

### 7.3 Mobile-First but Not Native App

**Constraint**: Platform is responsive web app, not native iOS/Android app.

**Rationale**: Reduced development cost, cross-platform compatibility, faster deployment iterations.

**Limitation**: Technicians cannot access native OS features (e.g., biometric unlock, background location tracking) without web API wrappers.

---

## 8. Performance & Scalability Targets

### 8.1 Expected Load

| Metric | Target |
|--------|--------|
| Concurrent users | 50–100 (peak) |
| Sensor devices | 500–1000 |
| Sensor readings/day | ~10 million (assuming 1000 devices × 4 metrics × 5 sec interval × 24 hr) |
| Report generation/day | 10–20 |

### 8.2 Performance Requirements

- **API response time**: p95 < 500ms (JWT validation + RLS policies + Prisma query)
- **Real-time dashboard update**: < 2 seconds from sensor event to UI refresh
- **PDF generation**: < 10 seconds for a 20-page report with embedded graphs
- **Mobile load time**: < 3 seconds on 4G LTE connection

### 8.3 Infrastructure

- **Database**: Supabase (PostgreSQL 15+, 4GB+ RAM, auto-scaling backups)
- **Backend**: Next.js on Vercel (serverless Edge Functions for API routes)
- **MQTT Broker**: Supabase Realtime (or third-party broker: Mosquitto / AWS IoT Core, TBD)
- **Storage**: Supabase Storage (S3 backend) for PDFs and inspection photos
- **CDN**: Vercel Edge Network for static assets and API caching

---

## 9. Security Considerations

### 9.1 Authentication & Token Management

- **JWT tokens**: Issued with 15-minute expiry; refresh tokens rotated on use
- **HTTPS/TLS**: All communication encrypted in transit
- **CSRF protection**: SameSite cookies; CSRF tokens on state-changing operations
- **Rate limiting**: API endpoints rate-limited to 1000 req/min per user (to prevent brute-force or IoT device misconfiguration)

### 9.2 Data Protection

- **Encryption at rest**: PostgreSQL and Supabase Storage support transparent encryption (TBD: key management via AWS KMS or Supabase vaults)
- **Audit logging**: All mutations logged with user, timestamp, operation, organization_id
- **GDPR compliance**: Data retention policy (30-day purge of sensor telemetry by default; customer-configurable); user data export/deletion APIs

### 9.3 Third-Party Integrations

- **Email service**: API key stored in environment variables (non-exportable)
- **MQTT broker**: TLS endpoint with certificate pinning (if self-hosted)
- **PDF signing**: Private keys stored in HSM or AWS Secrets Manager (phase 2)

---

## 10. Project Phases & Milestones

### Phase 1: MVP (Weeks 1–8)

- Authentication & authorization framework (CASL + RLS)
- Inspection CRUD + offline sync (IndexedDB)
- Mock sensor integration (no real hardware)
- Single-language (IT) UI
- PDF report generation (single signature)

### Phase 2: IoT Integration (Weeks 9–13)

- Real Helion hardware testing (once firmware docs arrive)
- MQTT subscription + real-time dashboard
- Alert rules engine (threshold triggers)
- Email notifications

### Phase 3: Polish & Reseller Ready (Weeks 14–17)

- Multi-language (EN added)
- Performance optimization (caching, query tuning)
- Technician mobile app refinements
- Reseller onboarding documentation
- Load testing & security audit

---

## 11. Open Questions & Risks

| # | Question | Owner | Impact | Status |
|---|----------|-------|--------|--------|
| 1 | What is the exact MQTT payload schema from Helion (TG-400/SM-220/AQ-100 firmware & HelionLink protocol)? | Victor Crane (Client Lead) to contact vendor | HIGH: blocks IoT integration | **PENDING** |
| 2 | Should real-time sensor ingestion use polling (5-sec intervals) or event-driven (threshold alerts only)? | Samir Osei (Tech Lead) + Alberto Neri (Client CEO) design session | MEDIUM: affects broker load, UI responsiveness | **UNRESOLVED** |
| 3 | Will Innovative Windows LLC host MQTT broker in-house or rely on Supabase Realtime? | Alberto Neri + Elisabetta Bianchi (COO) infrastructure decision | HIGH: affects deployment, operations cost | **PENDING** |
| 4 | What is the SLA for technician digital signature capture (time limit, retry logic if network fails during signing)? | Samir Osei + John Smith (field technician) requirements gathering | MEDIUM: affects workflow UX, legal liability | **UNRESOLVED** |

---

## 12. Success Criteria & Acceptance Testing

- **Functional**: All user stories in backlog pass acceptance tests; authorization matrix verified (6 roles, CASL + RLS)
- **Performance**: MVP dashboard loads < 3s on 4G; PDF generation < 10s
- **Mobile**: Responsive on iOS Safari & Chrome Mobile; offline sync tested with 1-hour connectivity gaps
- **Security**: Penetration test passed; no hardcoded secrets; OWASP Top 10 mitigations verified
- **Documentation**: API docs (OpenAPI/Swagger), deployment runbook, technician training guide

---

## 13. Team & Communication

**Atlas Forge Team**:
- **Victor Crane** (Managing Director / Client Lead): Client relationship, scope, vendor coordination
- **Samir Osei** (Tech Lead / PM): Architecture, development roadmap, technical decisions
- **Clara Duval** (Full-stack Developer): Implementation, code review, technical documentation

**Innovative Windows LLC Key Contacts**:
- **Alberto Neri** (CEO): Strategic decisions, reseller partnerships
- **Elisabetta Bianchi** (COO): Infrastructure, operations, field team logistics
- **John Smith** (Field Technician): Requirements validation, UX feedback, pilot testing

**Cadence**:
- Weekly sync (Monday 10:00 CET): Victor + Samir + Alberto + Elisabetta
- Bi-weekly technical deep-dives: Samir + Clara + John Smith (inspection workflow review)
- Ad-hoc vendor liaison: Victor with Helion sensor manufacturer

---

## 14. Appendix: Glossary

- **CASL**: Client-side Authorization Service Layer; JavaScript library for frontend permission checks
- **RLS**: Row-Level Security; PostgreSQL feature enforcing data access policies at database layer
- **MQTT**: Message Queuing Telemetry Transport; lightweight IoT pub/sub protocol
- **WebSocket**: Full-duplex communication channel for real-time server-to-client updates
- **JWT**: JSON Web Token; stateless auth credential with embedded claims
- **Helion**: Manufacturer of smart fire-resistant window environmental sensors
- **QR Code**: Machine-readable identifier embedded in maintenance reports for window traceability
- **Dual Signature**: Separate digital signatures from technician (service provider) and end-user (property owner) on maintenance reports

---

**Document End**