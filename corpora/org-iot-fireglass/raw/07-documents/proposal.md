# FireGlass Platform Proposal
## Atlas Forge LLC → Innovative Windows LLC

**Document Date:** 2025-07-21
**Project Duration:** 15–17 weeks
**Total Budget:** €120,000
**Prepared by:** Samir Osei, Project Manager, Atlas Forge LLC

---

## Executive Summary

Innovative Windows LLC operates a geographically distributed fleet of commercial and residential window installations across Central Europe. Current fleet management relies on manual inspection schedules, paper-based reporting, and delayed incident response. This project proposes **FireGlass**, an integrated CRM and IoT platform that enables real-time monitoring of window installations via Helion thermal sensors, automated compliance reporting, and predictive maintenance scheduling.

FireGlass will deliver:
- Unified dashboard for monitoring 500+ installations across multiple sites
- Real-time sensor data ingestion from Helion IoT network (HelionLink protocol)
- Automated compliance inspection workflows with field signature capture
- REST API for integration with existing ERP systems
- Browser-based and progressive web application for field technicians

Expected outcomes: 40% reduction in manual inspection labor, 15% faster incident response, 99.5% fleet visibility within 6 months of deployment.

---

## Understanding of Client Requirements

Alberto Neri, CEO of Innovative Windows LLC, has outlined the following business objectives:

1. **Fleet Visibility:** Establish continuous, real-time sensor monitoring with sub-second latency across all active installations (via Helion TG-400, SM-220, and AQ-100 sensors). Enable the operations team to identify thermal anomalies, seal failures, or sensor malfunctions within minutes rather than weeks.

2. **Compliance Automation:** Generate standardized inspection reports and ASG-FP Level 2 compliance certificates automatically, reducing administrative overhead and ensuring audit trail integrity.

3. **Predictive Maintenance:** Analyze sensor trends to predict window seal degradation, thermal performance decline, and replacement cycles. Transition from reactive maintenance to proactive scheduling.

4. **Field Operations:** Equip technicians with a mobile-first interface for on-site inspections, sensor data review, and signature capture. Eliminate paper forms and enable offline form drafting with sync-on-reconnect.

5. **Stakeholder Reporting:** Provide customizable PDF/CSV export for customer-facing compliance reports, warranty claims documentation, and performance dashboards shared with facility managers.

---

## Proposed Solution Overview

### Platform Architecture

FireGlass is a cloud-native SaaS platform built on a modern, scalable technology stack:

**Frontend:** Next.js 14 (React) with TypeScript
**Backend:** Node.js API layer (Express-compatible)
**Database:** PostgreSQL with Prisma ORM
**Real-time Data:** MQTT broker (HelionLink protocol) for sensor ingestion
**Authentication:** Supabase Auth (JWT-based)
**Hosting:** Supabase (managed PostgreSQL + Auth)

### Core Modules

1. **Authentication & Access Control**
   - Role-based access control (Admin, Operations Manager, Field Technician, View-Only)
   - Single sign-on integration (LDAP/Active Directory ready)
   - Audit logging for compliance

2. **Installation Management**
   - Centralized registry of all window installations with geolocation, specifications, and lifecycle metadata
   - Bulk import from CSV
   - Location tagging and hierarchical organization by facility/region

3. **Sensor Dashboard**
   - Real-time monitoring of 500+ Helion sensors (TG-400, SM-220, AQ-100 models) simultaneously
   - Traffic light (red/amber/green) status indicators
   - Alert feed with severity filtering
   - Historical trend charts (7-day, 30-day, 90-day views)
   - Configurable alert thresholds per sensor model

4. **Inspection Workflow**
   - Digital inspection checklists (pre-configured for Innovative Windows' standards)
   - Photo upload and annotation (field technician can capture images of anomalies)
   - Signature canvas for technician and facility manager sign-off
   - Timestamped submission with geolocation lock

5. **Report Generation**
   - Automated compliance reports (PDF) based on inspection data and sensor trends
   - Customizable templates for different customer segments
   - CSV export for integration with customer systems
   - Scheduled report delivery via email

6. **Maintenance Scheduling**
   - Calendar interface for planned maintenance events
   - Bulk assignment of technicians to maintenance tasks
   - Integration with sensor alert data to prioritize high-risk installations
   - Notification of assigned technicians (via PWA push)

---

## Technology Stack Rationale

**Next.js 14** provides server-side rendering, static generation, and API route capabilities in a single framework, accelerating development and improving SEO for public-facing elements. TypeScript ensures type safety across the stack, reducing runtime errors in a safety-critical fleet management context.

**PostgreSQL** with Prisma ORM offers relational data integrity for complex installation hierarchies, sensor relationships, and audit trails. Prisma's schema migrations and type generation integrate seamlessly with TypeScript.

**MQTT via HelionLink v2.3** is the proven protocol for Helion sensor networks. Our IoT layer subscribes to sensor topics and persists readings to PostgreSQL at configurable intervals (default: 5-second polling).

**Supabase** manages authentication, row-level security, and real-time subscriptions, reducing infrastructure management overhead.

---

## Timeline & Deliverables

### Project Phases (15–17 weeks, 8 sprints)

| Sprint | Duration | Scope |
|--------|----------|-------|
| 1–2 | Weeks 1–4 | Infrastructure, Auth, API foundations, Database schema |
| 3–4 | Weeks 5–8 | Installation management, Sensor ingestion, Dashboard MVP |
| 5 | Weeks 9–11 | Inspection workflow, Form builder, Photo upload |
| 6 | Weeks 12–14 | Report generation, Export (PDF/CSV), Performance tuning |
| 7 | Weeks 15–16 | UAT, Bug fixes, Documentation, Training materials |
| 8 | Week 17 | Deployment, Go-live support, Contingency |

### Deliverables

- **Functional Platform:** Fully deployed FireGlass instance accessible via modern web browsers and PWA on field technician devices
- **REST API:** Documented, versioned API for third-party integrations (ERP, CRM, BI tools)
- **Database Schema:** Comprehensive Prisma schema with migration history
- **Deployment Configuration:** Docker Compose / Kubernetes manifests, CI/CD pipeline (GitHub Actions)
- **User Documentation:** End-user guide, admin manual, API reference
- **Training Materials:** Video walkthroughs, quick-start guide, troubleshooting checklist
- **Handoff Package:** Source code repository (private GitHub), deployment runbooks, SLA agreements

---

## Budget Breakdown

| Category | Amount | Notes |
|----------|--------|-------|
| Development (8 sprints × €7,500) | €60,000 | Core platform, integrations, testing |
| Infrastructure & DevOps | €20,000 | Database, hosting, CI/CD, monitoring setup |
| Quality Assurance | €15,000 | Test automation, UAT coordination, bug fixes |
| Project Management & Coordination | €15,000 | Sprint planning, stakeholder meetings, documentation |
| Contingency Buffer | €10,000 | Scope adjustments, unforeseen technical debt |
| **Total** | **€120,000** | |

**Sprint Cost:** €7,500 per sprint covers 1 FTE senior developer, 0.5 FTE full-stack engineer, and 0.25 FTE QA specialist per sprint. Samir Osei (PM/Tech Lead) time is allocated across project management and critical development tasks.

---

## Team Composition

| Role | Name | Responsibility |
|------|------|-----------------|
| Project Manager / Tech Lead | Samir Osei | Architecture decisions, sprint planning, client liaison, critical development tasks |
| Senior Full-Stack Developer | Clara Duval | Next.js app, API design, Prisma schema, database optimization, code review |
| Field Technology Specialist | John Smith | IoT integration (HelionLink v2.3 protocol), sensor network setup, on-site validation, field UX testing |
| Installation Partner | StructuraBuild S.r.l. | On-site sensor deployment, technician coordination, installation compliance verification |

**Client Contact:** Alberto Neri (CEO), with operational delegation to Innovative Windows operations team.

---

## Assumptions & Constraints

### Assumptions

1. Innovative Windows will provide 2–3 dedicated staff members for UAT and change management
2. Helion sensor network (TG-400, SM-220, AQ-100) is operational and stable before platform deployment
3. Client will provide sample CSV of 50–100 installations for development/testing
4. Uptime SLA expectations: 99.5% during business hours (8–18 CET)
5. Data retention: minimum 2 years of sensor readings for compliance; ASG-FP Level 2 audit logs retained per regulatory requirement
6. NordShield Insurance carrier approval obtained prior to platform go-live

### Constraints

1. **Network Connectivity:** Field technicians may operate in areas with spotty cellular/WiFi coverage; the PWA must support offline form drafting with sync-on-reconnect
2. **Legacy Integration:** Initial scope excludes synchronization with existing ERP systems; API-first design allows future integration
3. **Regulatory Compliance:** Platform must maintain audit trails for ISO 9001 / EPFC-2200 building code compliance audits and generate ASG-FP Level 2 certification reports
4. **Sensor Maintenance:** Helion sensors require periodic battery replacement and calibration; platform tracks maintenance history but does not automate logistics

---

## Payment Terms

- **30% upfront** (€36,000) upon contract signature
- **40% at project midpoint** (€48,000) upon successful UAT sign-off (end of Sprint 6)
- **30% at delivery** (€36,000) upon production deployment and 4-week post-launch support window

All payments due within 30 days of invoice. Late payment subject to 1.5% monthly interest.

---

## Success Criteria & Acceptance

FireGlass v1.0 MVP is deemed successfully delivered when:

1. ✓ Dashboard displays real-time sensor data (5-second polling latency) for ≥99% of Helion sensors
2. ✓ All CRUD operations (Installation, Inspection, Report) function without errors in UAT
3. ✓ Inspection workflow supports offline drafting on PWA with sync-on-reconnect
4. ✓ Report generation produces valid PDF/CSV exports within 5 seconds
5. ✓ Platform uptime ≥99% over 4-week pre-production pilot
6. ✓ User documentation and training materials reviewed and approved by client
7. ✓ Zero critical security vulnerabilities in penetration test

---

## Next Steps

1. **Week of 2025-07-28:** Kick-off meeting, team introductions, environmental setup
2. **2025-08-04:** Client provides sample installation data and sensor network credentials
3. **Sprint 1 Standup (Weekly):** Every Monday 10:00 CET, progress reviews Friday end-of-day
4. **Bi-weekly Steering Calls:** Every other Wednesday 15:00 CET with Alberto Neri + ops team

---

**Prepared by:** Samir Osei
**Date:** 2025-07-21
**Signature:** _______
**Client Acceptance:** _______

---

*This proposal is valid for 30 days. Pricing and timeline subject to revision if scope or team composition changes.*
