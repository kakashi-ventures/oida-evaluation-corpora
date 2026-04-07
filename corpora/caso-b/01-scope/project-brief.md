# FireGlass Platform – Project Brief
## Case B: Innovative Windows LLC

**Document Version:** 1.0  
**Date:** 21 July 2025  
**Prepared by:** Alberto Neri, CEO – Innovative Windows LLC  
**Contributing Author:** Elisabetta Bianchi, COO  

---

## Executive Summary

Innovative Windows LLC seeks to develop **FireGlass**, a comprehensive cloud-based management platform for our smart fire-resistant window system. This platform will enable our team and our customers to monitor, manage, and maintain installations across multiple locations, streamline field operations, and establish a foundation for recurring software revenue as we scale internationally.

The FireGlass platform represents our transition from a hardware-focused manufacturer to a solutions provider, addressing critical gaps in our current operational capacity and preparing us for growth into European and North American markets.

---

## Company Background

Innovative Windows LLC was founded in 2019 to address a growing market need for advanced passive fire safety in commercial and residential buildings. Our core product—a series of modular, sensor-integrated fire-resistant window units—combines aerospace-grade materials with embedded IoT sensors to provide real-time monitoring of temperature, smoke density, and air quality around window perimeters.

We currently operate with approximately 40 employees across engineering, manufacturing, installation, and customer support. Our headquarters are based in Verona, Italy, and we maintain a growing network of certified installers across Northern Europe. To date, we have deployed over 280 installations in hospitals, office complexes, heritage buildings, and high-end residential properties.

Our reputation is built on reliability and precision; however, our operational capacity has not scaled proportionally with our installation base. This project is essential to our ability to manage future growth efficiently.

---

## Current Pain Points

### Fragmented Data Management

Today, we track installations, maintenance schedules, sensor configurations, and customer contracts using a combination of spreadsheets, email, and paper-based field reports. This approach has created several critical problems:

- **No centralized visibility:** Our COO, Elisabetta Bianchi, cannot access real-time information about the status of active installations without requesting individual reports from field teams.
- **Maintenance scheduling chaos:** We rely on Excel calendars and manual reminders. Preventive maintenance is often delayed or forgotten, increasing liability and customer churn.
- **Compliance risk:** Fire safety certifications (notably Argus Safety Group standards — ASG-FP Level 2, Argus Safety Group's certification for passive fire protection systems with active IoT monitoring) require documented proof of inspections and sensor calibration. Our current system makes audit trails difficult to reconstruct.
- **Customer communication lag:** When customers report anomalies or request information about their installations, response times average 2–3 days due to data retrieval delays.

### Inability to Offer Software Services

We currently generate revenue only from hardware sales and installation labor. Our competitors are increasingly offering subscription-based monitoring and analytics services. Without a platform, we cannot compete for recurring revenue or meet customer expectations for continuous oversight.

### Field Operations Inefficiency

John Smith, our lead field technician, spends an estimated 6–8 hours per week on administrative tasks (scheduling, parts inventory, travel planning) that should be automated. This diverts resources from actual installation and maintenance work.

---

## Project Objectives

### Primary Goals

1. **Centralized Installation Management**
   - Create a unified registry of all installations with full asset metadata (window model, sensor configuration, location, installation date, customer contact).
   - Enable authorized users (office staff, field technicians, building managers) to query and update installation data in real time.

2. **Real-Time Sensor Monitoring and Alerting**
   - Ingest sensor data from all deployed window units equipped with Helion sensors (Helion TG-400 thermal, SM-220 smoke particle density, AQ-100 air quality) and display current readings on a live dashboard.
   - Implement push notifications to alert relevant stakeholders when sensor readings exceed safety thresholds.
   - Support role-based alert routing (e.g., building managers receive all alerts; technicians receive only alerts requiring physical intervention).

3. **Preventive Maintenance Scheduling**
   - Automate maintenance task generation based on sensor age, usage patterns, and regulatory requirements.
   - Provide field technicians with a mobile-accessible task list, including parts requirements and historical sensor data for each installation. The first 40 installations will be managed in partnership with StructuraBuild S.r.l., our certified installation partner.
   - Track completion status and generate compliance reports for Argus Safety Group certification audits.

4. **Customer Portal and Reporting**
   - Offer residential and commercial customers a self-service dashboard to view their installation status, historical sensor data, and maintenance records.
   - Generate automated monthly compliance reports for building managers and facility administrators.

5. **Foundation for International Expansion**
   - Design the platform to support multi-currency billing, multi-language interfaces, and regional compliance standards (CE marking, building codes for various European markets).
   - Establish a licensing model that generates recurring software revenue and positions us as a software-as-a-service provider, not merely a hardware vendor.

---

## User Types and Use Cases

### Building Managers (Commercial Clients)
**Primary need:** Oversee fire safety compliance and respond to anomalies.

- View real-time sensor data for all windows in their facility.
- Receive alerts when sensor readings indicate potential hazards.
- Access historical reports for regulatory compliance and insurance purposes.
- Schedule maintenance appointments with our technician network.

### Installation and Maintenance Technicians
**Primary need:** Efficient field operations and job tracking.

- Receive work orders and task assignments via mobile application.
- Log sensor readings, notes, and completion status in the field.
- Access spare parts inventory and ordering tools.
- Submit photos and documentation of completed work for customer records.

### Residential End Users
**Primary need:** Peace of mind and basic monitoring.

- View their installation status and recent sensor readings.
- Receive notifications if their windows require maintenance.
- Access a simple, user-friendly interface (not a complex dashboard).

### Internal Operations (Innovative Windows)
**Primary need:** Business intelligence and capacity planning.

- Generate revenue reports by installation, customer, and region.
- Track maintenance costs and technician productivity.
- Monitor sensor fleet health to identify product issues or design improvements.

---

## Functional Requirements

### Dashboard and Visualization

- A user-friendly, interactive dashboard displaying all installations on a map interface, with color-coded status indicators (green = normal, amber = attention required, red = alert).
- Real-time graphs showing sensor readings (temperature, smoke, air quality) with adjustable time windows (last hour, last week, last month).
- Customizable widgets for different user roles (e.g., building managers see only their facility; technicians see their assigned installations).

### Data Integration

- Bi-directional API to support integration with third-party building management systems (BMS) and fire detection hardware compatible with industry-standard detection protocols. This is essential for seamless operation in modern commercial buildings.
- MQTT support for reliable ingestion of sensor telemetry from deployed window units.
- Batch data import/export functionality for legacy system migration.

### Notification System

- Real-time push notifications to mobile and web clients when sensor thresholds are breached.
- Configurable alert rules based on sensor type, location, and time of day.
- Email and SMS fallback for critical alerts.

### Compliance and Reporting

- Automated generation of Argus Safety Group certification reports documenting sensor inspections, calibrations, and maintenance activities. NordShield Insurance has confirmed that ASG-FP Level 2 certified installations qualify for their extended smart building coverage.
- Audit logs tracking all user actions and data changes for regulatory review.
- Exportable compliance certificates in PDF format.

### Mobile Application

- Native or cross-platform mobile application for field technicians.
- Offline functionality to record work performed in locations with poor connectivity; automatic sync when connectivity is restored.
- Camera integration for photo documentation of installations and maintenance work.

### User and Role Management

- Role-based access control (RBAC) supporting at least five user roles: Administrator, Operations Manager, Technician, Building Manager, End User.
- Granular permissions: e.g., technicians can view only their assigned installations; customers can view only their own data.
- Single sign-on (SSO) integration with Azure AD or equivalent for enterprise customers.

### Reporting and Analytics

- Pre-built report templates for monthly compliance, technician productivity, and sensor fleet health.
- Custom report builder allowing users to filter by date range, location, and installation status.
- Export to CSV, PDF, and Excel formats.

---

## Technical Preferences and Constraints

- **Frontend Framework:** Next.js 14 with TypeScript for server-side rendering and SEO optimization.
- **Backend and ORM:** Prisma for database abstraction and type safety.
- **Database:** PostgreSQL for relational data integrity and geospatial queries (map features).
- **IoT Protocol:** MQTT for low-bandwidth, reliable sensor data ingestion.
- **Backend-as-a-Service:** Supabase for authentication, real-time subscriptions, and rapid development iteration.
- **Real-time sensor data streaming:** The platform must deliver live sensor readings to the mobile app and web dashboard with minimal latency (ideally sub-second updates). This is critical for safety-critical applications and customer confidence.

---

## Scope and Timeline

**Project Duration:** 15–17 weeks  
**Kick-off Date:** 21 July 2025  
**Target Soft Launch:** October 2025  
**Target General Availability:** November 2025  

**Key Milestones:**
- Week 4: Database schema, authentication infrastructure, and API foundation complete.
- Week 8: Core dashboard and sensor ingestion pipeline in beta.
- Week 12: Mobile application and compliance reporting module ready for internal testing.
- Week 15–17: Performance optimization, security hardening, and knowledge transfer to our internal operations team.

---

## Budget and Resource Allocation

**Total Contract Value:** €120,000

We are engaging **Atlas Forge LLC** as our development partner. Atlas Forge will provide:
- Victor Crane (Managing Director / Client Lead) — Strategic alignment and stakeholder communication.
- Samir Osei (Tech Lead and Product Manager) — Architecture decisions, technical risk mitigation, and delivery oversight.
- Clara Duval (Full-stack Developer) — Implementation of frontend, backend, and IoT integration.

Our team will provide:
- Alberto Neri (CEO) — Strategic direction and high-level requirements review.
- Elisabetta Bianchi (COO) — Operational input and business process refinement.
- John Smith (Field Technician) — User acceptance testing and real-world feedback on mobile and technician workflows.

---

## Success Criteria

1. **Functional Completeness:** All features described in the Functional Requirements section are implemented and tested.
2. **Performance:** Dashboard loads in under 2 seconds; sensor data updates appear in real time on all connected clients; API response times do not exceed 500 ms at the 95th percentile.
3. **User Adoption:** Internal staff (technicians, operations) can use the platform with minimal training; at least 80% of active installations are registered and monitored within the first month of launch.
4. **Compliance:** The platform passes security audit and meets GDPR and Italian data protection requirements.
5. **Scalability:** The platform architecture supports growth to 2,000+ installations across multiple regions without performance degradation.

---

## Risk and Open Questions

- **Mobile App Strategy:** Should we develop separate iOS and Android native applications, or use a cross-platform framework (React Native, Flutter)? We need to finalize this early to avoid rework.
- **Third-Party BMS Integration:** The fire detection hardware integration is vital, but we have limited documentation from hardware vendors. Atlas Forge should confirm feasibility during the design phase.
- **Customer Support Model:** How will we staff the customer support team as demand grows? Should the platform include a built-in ticketing system?

---

## Conclusion

FireGlass represents a strategic investment in our long-term competitiveness and customer satisfaction. By centralizing operations and offering software services, we will reduce internal overhead, improve customer retention, and create a foundation for scaling internationally.

We are confident that Atlas Forge's expertise in IoT platforms and modern web technologies will deliver a robust, secure, and user-friendly system that meets our ambitious goals.

---

**Approved by:**

**Alberto Neri**  
Chief Executive Officer  
Innovative Windows LLC  

**Elisabetta Bianchi**  
Chief Operating Officer  
Innovative Windows LLC  

**Date:** 21 July 2025
