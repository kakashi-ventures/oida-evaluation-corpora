# Fire Safety Regulations and Compliance Landscape

**Reference Document for Innovative Windows LLC (FireGlass)**

**Compiled by:** Samir | **Date:** March 2026

---

## DISCLAIMER

**IMPORTANT:** This section was compiled by Samir based on conversations with Alberto and publicly available regulatory summaries. It should **NOT** be treated as legal advice. Alberto's legal team should review and validate all compliance claims before using this information in marketing materials, certifications, or regulatory submissions.

---

## Overview

Innovative Windows LLC's FireGlass product operates within a complex, multi-jurisdictional regulatory environment. This document outlines the primary regulatory frameworks affecting fire-resistant glazing with IoT-enabled sensor integration in Europe. The regulations fall into three categories:

1. **Product fire safety standards** (EPFC framework, national codes)
2. **Equipment/IoT compliance** (CE marking, EU-SmartSafe Mark, sensor standards)
3. **Data privacy and security** (GDPR, IoT device security)

---

## EPFC-2200: Passive Fire Protection Performance Requirements

**Full Title:** European Passive Fire Council Standard 2200 — Performance Requirements for Passive Fire Protection in Commercial and Residential Buildings

**Scope:** The EPFC-2200 standard specifies minimum performance requirements for passive fire barriers (including fire-resistant glazing) in buildings across EU member states. It establishes a unified framework replacing fragmented national standards while allowing national building codes to reference it as the baseline requirement.

### Performance Tiers and Classification

The EPFC defines fire-resistant glazing performance across four key metrics:

1. **Thermal Resistance (REI Rating)**
   - REI30: 30-minute fire resistance (residential, lower-risk commercial)
   - REI60: 60-minute fire resistance (high-occupancy commercial, multi-family)
   - REI90/120: 90–120 minute resistance (industrial, hazardous material storage)

2. **Structural Integrity**
   - Window frame must maintain closure under fire conditions
   - Glass must not shatter or allow flame passage
   - Seals must contain smoke penetration

3. **Thermal Isolation**
   - Temperature on non-fire side must not exceed 250°C above ambient
   - Prevents ignition of adjacent materials

4. **Durability and Cycling**
   - Windows must withstand 500 thermal cycles (-20°C to +800°C) per Veridian TRC-500 test protocol
   - Structural integrity and thermal properties must remain stable post-cycling

### Testing and Certification Requirements

To classify a product under EPFC-2200, manufacturers must conduct:

1. **Thermal Furnace Testing (Fire Endurance)**
   - Full window assembly tested in ISO 9239-compatible furnace
   - Measures time-to-failure under standardized fire curve
   - Cost: €12,000–€18,000 per variant
   - Duration: 12–16 weeks
   - Laboratory must be accredited per ISO 17025 (Veridian Test Labs is accredited)

2. **Smoke and Toxic Gas Testing**
   - 72-hour smoke density test at elevated temperatures
   - Measures flame spread, smoke development, flaming droplets
   - Cost: €6,000–€9,000
   - Duration: 8–10 weeks

3. **Durability and Thermal Cycling (Veridian TRC-500 Protocol)**
   - 500 thermal cycles between -20°C and +800°C
   - 72-hour smoke exposure test post-cycling
   - False positive test (smoke detection at >90% humidity)
   - Cost: €8,000–€12,000
   - Duration: 14–18 weeks
   - Critical for IoT-enabled windows (sensors must remain reliable)

4. **Installation and Sealant Verification**
   - Frame-to-wall interface testing
   - Sealant durability validation
   - Cost: €3,000–€5,000

### Timeline and Cost

- **Initial EPFC-2200 Classification:** 8–10 months
- **Total Investment:** €29,000–€44,000 per product variant
- **Validity:** Indefinite (subject to surveillance audits every 2 years by accredited labs)
- **Surveillance Audits:** €5,000–€8,000 every 2 years

### Documentation Requirements

Once classified, manufacturers must maintain:
- Technical Documentation (TDoc) in English; updates required if product changes
- Declaration of Performance (DoP) in relevant national languages
- Installation and maintenance guides
- Thermal cycling test reports (Veridian TRC-500)

---

## EPFC-2201: Smart and Connected Fire Protection Systems

**Full Title:** European Passive Fire Council Standard 2201 — Extension for Interconnected and IoT-Enabled Fire Protection Systems

**Scope:** EPFC-2201 defines additional requirements for passive fire barriers with active monitoring capabilities (e.g., Helion IoT sensors integrated into FireGlass windows). It addresses alert latency, sensor reliability, cybersecurity, data retention, and fail-safe behavior.

### Key Requirements for IoT-Integrated Windows

1. **Alert Latency**
   - **Fire condition detection to occupant alert:** Must occur within **10 seconds** of threshold breach
   - Temperature >150°C AND smoke density >100 mg/m³ triggers immediate local alarm
   - Cloud notification must follow within 30 seconds (secondary channel)
   - Failure to meet 10-second threshold results in EPFC-2201 Level 1 classification (passive-only; no active monitoring credit)

2. **Sensor Reliability**
   - Minimum sensor uptime: **99.5%** (calculated over 30-day rolling windows)
   - False positive rate: <0.1% at >90% humidity, <80°C, and normal air quality
   - False negative rate: <0.05% when actual fire conditions present
   - Monthly self-test required (automated diagnostic)
   - Veridian TRC-500 post-test validation mandatory

3. **Cybersecurity and EU-SmartSafe Mark**
   - All IoT sensors must comply with **EU-SmartSafe Mark** requirements:
     - End-to-end encryption (AES-256 minimum)
     - Secure over-the-air (OTA) firmware updates (signed, rollback protection)
     - Electrical isolation (fail-safe circuit design; no loss of fire detection on power loss)
     - Authentication: certificate-based (X.509) or hardware security module (HSM)
   - Network traffic: TLS 1.2+ mandatory
   - Sensitive data (sensor raw readings, building location) must not be stored unencrypted

4. **Data Retention and Privacy**
   - Fire event logs: minimum **5 years** retention for regulatory audit compliance
   - Sensor telemetry: minimum **90 days** on-premises; older data may be aggregated or archived
   - Personal data (if any): subject to GDPR, data minimization principles
   - Customers must have right to export data in open format (JSON, CSV)

5. **Fail-Safe Behavior**
   - Loss of network connectivity: System continues local fire detection and alarm; no degradation
   - Loss of power: Passive fire rating remains intact; backup battery supports 24-hour sensor operation if mains power lost
   - Sensor malfunction: System alerts facilities manager and falls back to passive-only protection
   - No "smart failure modes" that disable fire protection

### EPFC-2201 Certification Levels

- **Level 1:** Passive fire protection only (per EPFC-2200; no active monitoring)
- **Level 2:** Passive + active monitoring (heat/smoke detection with alert latency <10s, sensor reliability ≥99.5%, cybersecurity per EU-SmartSafe Mark)
- **Level 3:** Level 2 + automatic actuation (automatic door closure, ventilation adjustment, sprinkler integration upon alert)

FireGlass currently targets **Level 2** certification via Helion sensors (detection + alerts). Level 3 requires additional mechanical integration work.

### Testing and Compliance Path

1. **EPFC-2200 base classification** (thermal, structural, durability)
2. **Helion sensor integration validation:**
   - Alert latency testing (simulated fire conditions in controlled lab)
   - Humidity and temperature cycling for false positive/negative rates
   - Cybersecurity code review and penetration testing
   - Cost: €15,000–€25,000
   - Duration: 12–16 weeks
3. **EU-SmartSafe Mark validation** (if not already certified separately)
4. **Audit by Argus Safety Group** (ASG-FP certification body)

---

## Argus Safety Group (ASG-FP) Certification

**Overview:** Argus Safety Group is an independent European certification body specializing in passive fire protection systems. Based in Zurich, ASG operates in 14 EU countries and issues proprietary **ASG-FP certification** for fire-rated window systems.

### ASG-FP Certification Levels

- **Level 1 (ASG-FP-1):** Passive fire protection only (meets EPFC-2200)
- **Level 2 (ASG-FP-2):** Passive + active monitoring (meets EPFC-2200 + EPFC-2201 Level 2)
- **Level 3 (ASG-FP-3):** Passive + monitoring + automatic actuation (meets EPFC-2201 Level 3)

### Certification Requirements

ASG-FP certification validates:
- EPFC-2200 compliance (thermal, structural, durability per Veridian TRC-500)
- EPFC-2201 compliance (for Level 2/3): alert latency, sensor reliability, cybersecurity, fail-safe behavior
- EU-SmartSafe Mark compliance (if Level 2/3)
- Installation standards and frame/seal specifications
- Quality management system (ISO 9001 or equivalent)
- Technical documentation completeness

### Certification Timeline

1. **Application & Document Review:** 2–3 weeks
2. **Laboratory Testing and Validation:** 12–16 weeks (can run parallel with EPFC-2200 testing)
3. **Cybersecurity Audit (Level 2/3 only):** 3–4 weeks
4. **ASG Final Audit:** 1–2 weeks on-site
5. **Certification Issuance:** Upon successful audit
6. **Recertification:** Every 3 years with annual surveillance audits

**Total Timeline to ASG-FP-2 Certification:** 6–7 months for new product

### Cost Structure

- **ASG-FP-1 (Passive Only):** €25,000–€35,000 (product certification)
- **ASG-FP-2 (Passive + Monitoring):** €40,000–€60,000 (includes Helion sensor validation)
- **ASG-FP-3 (Passive + Monitoring + Actuation):** €55,000–€80,000 (includes mechanical integration)
- **Annual Surveillance Audit:** €8,000–€12,000
- **Recertification (every 3 years):** €30,000–€50,000

### Business Impact of ASG-FP Certification

Insurance companies (e.g., NordShield Insurance) offer premium discounts of 12–18% for properties using ASG-FP-2 or ASG-FP-3 certified systems. This creates direct revenue linkage: certification leads to customer adoption, which leads to insurance savings, which justifies capital investment.

---

## National Variations in Fire Safety Codes

### Italy: D.M. 16/02/2007 and EPFC Harmonization

**Scope:** Italian Ministerial Decree on Fire Safety; harmonized with EPFC-2200 as of 2024 amendment.

**Key Requirements:**
- Buildings over 3,000 m² or specific use types must have fire safety certification
- Fire-resistant barriers required in high-occupancy buildings
- Compartmentalization: walls and openings (including windows) must meet EPFC REI ratings
- REI30 minimum for standard commercial; REI60 for high-occupancy or complex buildings
- Windows in escape routes must be non-opening or have limited opening; REI60 minimum

**Compliance Path:**
- Product: EPFC-2200 classification + ASG-FP certification
- Installation: Certification by approved technical office (studio tecnico abilitato)
- Annual audit: Certified engineer required
- Digital compliance records: Mandatory as of 2024 (supports FireGlass IoT advantage)
- Cost: €3,000–€8,000 per building annually for audit and documentation

---

### Germany: DIN 4102 Cross-Certification with EPFC

**Scope:** DIN 4102 (Fire Behavior of Building Materials) predates EPFC but remains influential in Germany and Central Europe.

**Key Difference:** DIN 4102 uses slightly different testing methodologies than EPFC-2200. Products meeting EPFC REI60 may not directly map to DIN B1/B2 without additional validation.

**Requirements:**
- German building codes still reference DIN 4102 in many states (Länder)
- Manufacturers exporting to Germany should obtain EPFC-2200 + DIN 4102 cross-certification
- Cross-certification requires additional documentation review; not automatic

**Timeline:**
- Additional DIN 4102 validation: 6–8 weeks and €4,000–€6,000 on top of EPFC-2200

**Market Implication:** Operating in Germany requires dual certification strategy. This is a compliance cost but also a potential competitive advantage if competitors are not DIN 4102 certified.

---

### United Kingdom: BS 476 and Building Safety Act

**Scope:** Post-Brexit (January 2020), UK maintains BS 476 (traditional fire testing) while voluntarily accepting EN/EPFC standards.

**Building Safety Act (2022) and "Golden Thread" Requirement:**

Effective January 2024, requires:
- Digital fire safety record for buildings over 7 stories and >7,000 m²
- "Golden thread" documentation: continuous audit trail of fire-rated materials and maintenance
- Responsible Person (building manager) must maintain and audit records
- Non-compliance penalties: up to £5,000 per day

**Opportunity for FireGlass:**
IoT-enabled windows can automatically generate audit-ready records, supporting "Golden Thread" compliance. Helion sensors create timestamped event logs, dramatically reducing audit workload.

**Market Access:**
- UK accepts EPFC-2200 classification but may require BS 476 cross-reference for legacy properties
- Additional cost: €3,000–€5,000 for cross-reference documentation

---

## EU-SmartSafe Mark for IoT Devices in Fire-Risk Environments

**Overview:** EU-SmartSafe Mark is a compliance mark for IoT devices deployed in buildings with fire-risk or critical safety applications. Mandated for EPFC-2201 Level 2+ certification.

### Key Requirements

1. **End-to-End Encryption**
   - All sensor data encrypted in transit (TLS 1.2+) and at rest (AES-256)
   - No plaintext transmission of fire-sensitive data

2. **Secure OTA Firmware Updates**
   - Signed firmware packages (digital signature verification)
   - Rollback protection (prevent downgrade attacks)
   - Staged rollout capability (test on subset before full deployment)

3. **Electrical Isolation**
   - Fire detection circuit isolated from network circuits
   - No loss of fire alert capability if network fails
   - Backup battery support (minimum 24 hours) if mains power lost

4. **Authentication and Audit Trail**
   - Certificate-based device authentication (X.509)
   - Device logs all access, configuration changes, alerts
   - Logs retained for minimum 5 years

### Certification Process

- **Code Review:** Security audit of firmware, API, data handling
- **Penetration Testing:** Simulated attack scenarios
- **Compliance Audit:** Verify encryption, authentication, isolation
- **Duration:** 8–12 weeks
- **Cost:** €10,000–€18,000

---

## Data Privacy and GDPR Implications

### GDPR Scope for Building Sensor Data

Helion sensors collect and transmit data (heat, smoke density, air quality). If any data is:
- Linked to individuals (e.g., occupancy tracking via location of sensor triggering)
- Processed across borders
- Retained in identifiable form

...then GDPR applies.

### Key Requirements

1. **Data Processing Agreement (DPA):** Innovative Windows LLC and customers must have a signed DPA if customer data is collected. The contract must specify:
   - Data types collected (temperature, smoke, CO2; not personal data unless occupancy zone is individually identifiable)
   - Retention period (5 years for fire events; 90 days for telemetry)
   - Recipients (third-party cloud processors, insurance auditors)
   - Deletion procedures (automated purge after retention period)

2. **Privacy by Design:** IoT systems should minimize personal data collection. Example:
   - Collect: "Heat detected above 150°C in Zone A" (compliant)
   - Don't collect: "Employee John Smith's workstation has heat above 150°C" (requires explicit GDPR consent)

3. **Data Retention:** Sensor data retained only as long as needed for fire safety purposes.

4. **Cross-Border Transfer:** Data cannot be transferred outside EU/EEA without Standard Contractual Clauses (SCCs) or Adequacy Decision. Cloud platforms (AWS, Azure) maintain EU data centers; always verify regional compliance.

### Practical Implementation for FireGlass

- Recommend customers adopt privacy-by-design principles in their IoT deployment
- Provide data retention and deletion specifications in technical documentation
- If offering cloud services, ensure EU data residency
- Sign DPA template with all customers

---

## Building Code Trends: Digital Fire Safety Records

### EU Digital Building Directive (Coming 2027)

The European Commission is finalizing the Digital Building Directive, which will require:
- All new buildings and major renovations to maintain digital fire safety records
- Building Information Models (BIM) to include fire safety data
- Interoperability with national fire registries

**Implication for Innovative Windows LLC:**
- IoT sensors that automatically generate audit-ready records will be a key competitive advantage
- MQTT-based systems with standardized data formats (Brick Schema, FIWARE) will be preferred
- FireGlass should be positioned as "future-proof" and compatible with emerging BIM standards

### Insurance Industry Shift: Continuous Compliance Monitoring

Insurance carriers (including NordShield Insurance, a key Scandinavian player) are moving toward:
- Real-time sensor data for risk assessment (no longer just point-in-time audits)
- Predictive maintenance models based on historical sensor data
- Dynamic pricing (premium discounts for properties with active ASG-FP-2+ certified IoT monitoring)

This creates multi-year revenue opportunity: recurring sensor service subscriptions, data analytics, integration services.

---

## Veridian TRC-500 Durability Test Protocol

**Overview:** Veridian Test Labs (ISO 17025 accredited, based in Lyon, France) operates the TRC-500 thermal cycling protocol, which is mandatory for EPFC-2200 and EPFC-2201 compliance.

### Test Parameters

- **Thermal Cycling:** 500 cycles from -20°C to +800°C
- **Cycle Frequency:** Typically 2–3 cycles per day
- **Total Duration:** 250–350 days (duration varies by test scheduling)
- **Smoke Exposure:** 72-hour smoke density test post-cycling
- **False Positive Test:** >90% humidity, <80°C ambient, normal air quality; must not trigger false alarms

### Validation Criteria

- Window must maintain structural integrity (no frame warping >5mm)
- Thermal resistance (REI rating) must not degrade >10% post-cycling
- Helion sensors must maintain ±2°C temperature accuracy, ±5 mg/m³ smoke accuracy post-cycling
- No visible corrosion or seal degradation

### Cost and Timeline

- **Cost:** €8,000–€12,000
- **Duration:** 14–18 weeks (depends on cycle frequency and waiting queue at Veridian)
- **Facility:** Only Veridian Labs offers TRC-500; no alternative labs currently accredited

---

## Summary Compliance Roadmap for Innovative Windows LLC

### Phase 1: EU Market Baseline (2025–2026)
- [x] EPFC-2200 classification (thermal, structural, durability testing)
- [ ] Veridian TRC-500 durability validation (initiated Q2 2026, expected completion Q4 2026)
- [ ] ASG-FP-2 certification (Passive + Helion monitoring; planned Q4 2026–Q1 2027)
- [ ] EU-SmartSafe Mark validation for Helion sensors (lab testing in progress)
- [ ] GDPR Data Processing Agreements (legal review in progress)
- [ ] CE marking for Helion sensors (lab testing scheduled Q3 2026)

### Phase 2: Expanded EU + UK (2026–2027)
- [ ] DIN 4102 cross-certification for Germany (planned Q2 2027)
- [ ] UK BS 476 / Approved Document B cross-reference (planned Q3 2027)
- [ ] Digital Building Directive readiness (BIM/IoT standardization; planned 2027)
- [ ] GDPR compliance audit and ISO 27001 planning (security certification)
- [ ] Presentation at FireTech Europe (Milan, annual trade fair) to announce ASG-FP-2 certification

### Phase 3: Industry Leadership (2027+)
- [ ] Integration with NordShield Insurance premium discount program
- [ ] Participation in Passive Fire Summit (Brussels, annual conference) as thought leader
- [ ] Support for EPFC-Connect interoperability specification (REST + MQTT-based BMS integration)
- [ ] Potential Level 3 (ASG-FP-3) development for automatic actuation markets

---

## Risk Mitigation Recommendations

1. **Legal Review:** Have Alberto's legal team review all regulatory claims in marketing materials before publication.
2. **Certification Tracking:** Maintain a compliance calendar and responsibility matrix. Recertification deadlines (Veridian TRC-500, ASG-FP surveillance audits) require planning.
3. **Documentation Standards:** Establish single-source-of-truth for Technical Documentation (TDoc), DoP, audit records. Critical for audit efficiency and customer confidence.
4. **GDPR Readiness:** Document all data flows from Helion sensors. Have customer contracts include DPA templates.
5. **Regulatory Intelligence:** Subscribe to EPFC standards updates, ASG certification announcements, and EU Building Directive news to track changes.

---

*For questions or clarifications on specific regulatory requirements, contact your legal and compliance advisors. This document is a working reference and should be updated quarterly as regulations evolve.*
