# IoT Landscape for Fire Safety and Smart Building Systems

**Technical Reference Document | Innovative Windows LLC**

**Compiled by:** Samir | **Date:** March 2026

---

## Executive Context

FireGlass integrates Helion IoT sensors into fire-resistant window systems, enabling real-time monitoring of fire conditions (heat, smoke particle density, air quality) and integration with Building Management Systems (BMS). This document provides a technical overview of the IoT protocols, platforms, ecosystems, and sensor manufacturers relevant to fire safety and smart building applications.

**Key Decision Point:** Innovative Windows LLC has selected **MQTT v5** as the primary protocol for Helion sensor communication. This document explains that choice and outlines future considerations for protocol flexibility and vendor independence. Interoperability is ensured through EPFC-Connect, a new industry standard for BMS integration.

---

## MQTT v5: Protocol Foundation for FireGlass

### MQTT Protocol Overview

MQTT (Message Queuing Telemetry Transport) is a lightweight, publish-subscribe protocol optimized for low-bandwidth, high-latency IoT networks. Originally developed by IBM and Eurotech; standardized by OASIS. Version 5 (released 2019) adds important features for reliability and security critical to fire safety systems.

### MQTT v5 Characteristics

- **Protocol Header Size:** 2 bytes (minimal overhead)
- **Bandwidth:** 10–100 KB/s for typical sensor streams
- **Latency:** Sub-second (typical range: 100–500ms)
- **Security:** TLS/SSL encryption; username/password or certificate-based auth
- **QoS Levels:** Three levels (0=fire-and-forget, 1=at-least-once, 2=exactly-once)
- **Broker Architecture:** Requires central message broker (e.g., Mosquitto, HiveMQ, EMQX)
- **New in v5:** Enhanced authentication, property-based messaging, shared subscriptions (enables multi-node load balancing)

### Why MQTT v5 for Helion

- **Native firmware support:** Helion sensors include MQTT v5 stack (minimal power consumption for edge devices)
- **Topic-based routing:** Logical topic hierarchy: `/building/{building_id}/zone/{zone_id}/fire_sensor/{sensor_id}/temperature`
- **Loose coupling:** Sensors publish; subscribers (local gateways, cloud dashboards) listen without sensors knowing consumer identity
- **Mature ecosystem:** Thousands of off-the-shelf integrations with BMS platforms
- **Backward compatibility:** v5 maintains compatibility with v3.1.1 deployments (crucial for legacy building systems)

### MQTT v5 Advantages for Fire Safety

- **Low power consumption** (ideal for battery-backed sensors during power loss)
- **Simple pub/sub model** (easy to implement, debug, and audit)
- **Wide industry adoption** in building automation
- **Excellent scaling:** Single broker can handle 100,000+ concurrent connections
- **Publish properties (v5 feature):** Can include metadata (timestamp, sensor model, firmware version) in message header without expanding payload
- **Session resumption:** Retained messages and durable subscriptions support offline-capable clients

### MQTT v5 Limitations and Mitigations

- **Requires always-on broker:** Single point of failure unless clustered or replicated
- **No native REST API:** Requires gateway layer for HTTP-based systems (solved by EPFC-Connect)
- **Less suitable for high-volume data streams:** Video, high-frequency sensor arrays need supplementary protocols

### Typical Data Volume for FireGlass

- Helion sensor: Temperature reading + smoke density + CO2 every 5 seconds = 12 readings/minute
- 50 sensors per building: 600 readings/minute = ~10 KB/minute (very low bandwidth)
- Easily runs on 4G LTE or WiFi
- Cloud sync occurs asynchronously; local edge processing ensures real-time fire alerts

---

## Helion Sensor Technologies: Manufacturer Overview

**Manufacturer:** Helion Sensor Technologies (German precision sensor manufacturer, headquartered in Munich)

**Market Position:** Leading supplier of industrial environmental sensors for fire safety, HVAC monitoring, and industrial hygiene applications. Operates in 18 EU countries with regional distribution through systems integrators (e.g., StructuraBuild S.r.l.).

### Helion Product Lines

#### ThermoGuard Line (Heat and Smoke Detection)

**TG-400 (Temperature Sensor)**
- Range: 0–500°C (±2°C accuracy)
- Response time: <2 seconds to significant temperature change
- Protocol: HelionLink (proprietary bridge to MQTT v5)
- Power: Mains 110–240V AC
- Output: Temperature readings every 5 seconds (configurable 1–60 seconds)
- Installation: Window-mounted thermal probe or remote ceiling mount

**SM-220 (Smoke Particle Density Sensor)**
- Range: 0–500 mg/m³ (±5 mg/m³ accuracy)
- Detection method: Optical light scattering (photodiode-based)
- Response time: <3 seconds to smoke ingress
- Protocol: HelionLink to MQTT v5
- Power: Mains with battery backup (24-hour duration on backup)
- Output: Smoke density + air clarity index every 5 seconds
- False positive rate: <0.1% at high humidity (>90%), low temperature (<80°C)

#### AirSense Line (Air Quality Monitoring)

**AQ-100 (Multi-Gas Air Quality)**
- Sensors: CO2 (0–2,000 ppm ±30 ppm), O2 (16–25% ±0.5%), VOC (0–500 ppb)
- Protocol: HelionLink to MQTT v5
- Power: Mains with USB-C backup
- Output: Individual gas concentrations every 10 seconds
- Use case: Occupancy monitoring, HVAC optimization, secondary smoke detection

### HelionLink Protocol (Proprietary Bridge)

HelionLink is Helion's proprietary IoT communication layer that bridges sensor firmware to MQTT v5 cloud platforms.

**How It Works:**
1. Sensor measures (e.g., TG-400 detects 145°C)
2. Sensor firmware packs reading into HelionLink frame (includes timestamp, sensor ID, accuracy metadata)
3. HelionLink frame transmitted to local gateway (WiFi, Ethernet, or BLE)
4. Gateway converts HelionLink to MQTT v5 and publishes: `/building/zone-a/fire_sensor/tg-400-001/temperature` with payload `{"value": 145.2, "unit": "celsius", "accuracy": "±2", "timestamp": "2026-03-24T14:32:15Z"}`

**Advantages:**
- Optimized for low-power operation
- Hardware security module (HSM) support for X.509 authentication
- Automatic failover if WiFi unavailable (switches to Ethernet or buffered local storage)

**Limitations:**
- Proprietary lock-in if customers want to swap TG-400 for competitor's temperature sensor
- Requires Helion firmware updates (support responsibility for Innovative Windows LLC)

### Helion Integration with FireGlass

FireGlass windows integrate TG-400 (temperature) and SM-220 (smoke) directly into window frame. HelionLink gateway is positioned in window frame or nearby (up to 10 meters via BLE).

**Typical Installation:**
- Thermal probe embedded in window seal (contact with glass interior)
- Smoke sensor in window header (above glass, sampling air in building)
- HelionLink gateway (matchbox-sized, powered by building circuit)
- WiFi or Ethernet backhaul to customer's MQTT broker or cloud platform

---

## Competitive Sensor Manufacturers

The fire safety IoT sensor market includes several manufacturers. Understanding the broader ecosystem informs future product roadmaps and potential partnerships.

### SensorPulse Technologies (Swedish Competitor)

**Market Position:** Mid-market manufacturer of building environmental sensors; competing with Helion in Nordic and Northern European markets.

**Product Range:**
- Temperature/Humidity sensors (buildings, industrial)
- Smoke optical and ionization sensors
- CO2 and air quality sensors
- Connectivity: MQTT, HTTP REST, Zigbee, Modbus

**Protocol:** SPulse-Link (similar proprietary bridge to Helion's HelionLink)

**Compatibility with FireGlass:**
- SensorPulse sensors can connect to same MQTT broker as Helion
- No native interoperability between HelionLink and SPulse-Link (different firmware, calibration)
- Could be alternative if customer requires redundant sensor networks
- Key differentiator: Helion offers better thermal accuracy (±2°C vs. SensorPulse ±3°C)

### ThermalVision Labs (Austrian Competitor)

**Market Position:** Specialist in thermal imaging and high-accuracy temperature sensing for industrial applications. Growing into fire safety market (early stage).

**Product Range:**
- Infrared thermal sensors (non-contact temperature measurement)
- High-precision pyrometers
- Experimental MQTT support (v5 support planned Q3 2026)

**Challenges for FireGlass Competition:**
- Thermal imaging requires line-of-sight (not suitable for window-embedded sensors)
- Higher power consumption (poor battery support)
- Smaller MQTT ecosystem (limited cloud integrations)
- Higher cost per sensor

**Relevance to FireGlass:**
- Low threat in near term; unlikely to displace Helion for window integration
- Potential complementary sensor (secondary high-accuracy thermal confirmation in large buildings)

### ClimateSense Global (US-Based Competitor)

**Market Position:** Large multinational sensor conglomerate; dominates North American market; expanding into EU via acquisition (2024).

**Product Range:**
- Temperature, humidity, CO2 sensors (very generic; not fire-safety optimized)
- Proprietary cloud platform (limited MQTT support; prefers Azure IoT Hub)
- Extensive partner network but weak fire safety domain expertise

**Challenges for FireGlass Competition:**
- Not optimized for fire detection (response times slower than Helion)
- Azure cloud dependency (less attractive in EU due to data residency concerns)
- Generic sensor design (not fire-rated for EPFC-2200/2201 compliance)

**Relevance to FireGlass:**
- Potential threat only if ClimateSense develops fire-specialized sensors and invests in EPFC certification
- Current trajectory suggests they will remain generalist; unlikely to threaten Helion's fire safety domain position

---

## Building Management Systems (BMS) Integration

### EPFC-Connect Interoperability Standard

**Overview:** EPFC-Connect is a new technical specification (released 2025) for interoperability between fire protection systems and BMS. It standardizes how fire sensors (Helion, SensorPulse, etc.) communicate with building automation platforms.

**Protocol Foundation:** REST API + MQTT v5 hybrid

**Key Endpoints:**

```
GET /epfc/systems/{system_id}/sensors
  Returns: List of all fire sensors with metadata (location, type, last reading)

GET /epfc/systems/{system_id}/sensors/{sensor_id}/readings
  Returns: Time-series data (last 24 hours to 5 years based on retention policy)

POST /epfc/systems/{system_id}/alerts
  Subscribes to fire event notifications (webhook or MQTT topic)

GET /epfc/systems/{system_id}/health
  Returns: System uptime, sensor availability, network status
```

**MQTT Topic Structure (EPFC-Connect compatible):**

```
epfc/{building_id}/{zone_id}/{sensor_id}/temperature
epfc/{building_id}/{zone_id}/{sensor_id}/smoke_density
epfc/{building_id}/{zone_id}/{sensor_id}/alert_status
epfc/{building_id}/{zone_id}/{sensor_id}/diagnostic
```

**Advantages:**
- Unified data model for all fire sensors (regardless of manufacturer)
- REST gateway for legacy BMS systems that don't support MQTT
- Standardized metadata (sensor accuracy, battery status, calibration due date)
- Enables multi-sensor redundancy (customer can mix Helion + SensorPulse sensors in same system)

**Adoption Status:**
- EPFC-Connect v1.0 released Q2 2025
- Supported by: Helion (via firmware update Q3 2026), SensorPulse (Q4 2026), ThermalVision Labs (planned Q3 2026)
- Adoption mandated for new EPFC-2201 Level 2+ certifications (ASG-FP-2+) starting 2027

**Implementation for FireGlass:**
- Helion firmware will support EPFC-Connect via OTA update
- FireGlass cloud platform will expose EPFC-Connect endpoints
- Enables customers to integrate with any BMS vendor without custom middleware

---

## Edge Computing vs. Cloud Processing for Fire Safety

A critical architectural decision for any building IoT system is where to process sensor data: at the edge (sensor or local gateway) or in the cloud.

### Edge Computing Approach

**Definition:** Data processing occurs on local gateways, edge servers, or IoT devices before transmission to cloud.

**Architecture Example for FireGlass:**
```
Helion Sensors --> Local MQTT Broker --> Edge Processing (Rules Engine)
--> Cloud Archival + Analytics
```

**Advantages:**
- **Low Latency:** Fire alerts generated in milliseconds (not seconds) — critical for fire safety
- **Privacy:** Raw sensor data does not leave the building
- **Resilience:** System operates during network outages (no dependency on cloud)
- **Bandwidth Efficiency:** Only processed results sent to cloud (summaries, alerts, exceptions)
- **Regulatory Compliance:** Sensitive data stays on-premises (GDPR, audit compliance)

**Disadvantages:**
- Higher capex for local edge hardware (gateway device, storage)
- Maintenance burden (updates, security patching)
- Limited historical analytics across multiple buildings
- Duplicate logic across multiple sites (no centralized ML model sharing)

**Recommended Use Case for Fire Safety:**
- **Critical Path:** Fire detection and alarm → local rules engine → immediate notification (no network latency required)
- **Secondary Path:** Aggregated analytics and predictive maintenance → cloud (acceptable 5–10 minute latency)

### Cloud Processing Approach

**Definition:** Raw sensor data sent to cloud; processing and storage centralized.

**Architecture Example:**
```
Helion Sensors --> MQTT Cloud Broker (AWS IoT, Azure IoT Hub)
--> Lambda/Azure Functions --> Database + Dashboard
```

**Advantages:**
- **Scalability:** Handle unlimited sensor growth
- **Analytics:** Machine learning models on aggregated multi-building data
- **Cost Flexibility:** Pay-as-you-go for compute resources
- **Global Insights:** Cross-building pattern detection, benchmarking

**Disadvantages:**
- **Latency Risk:** Fire alerts may be delayed by network/cloud processing (unacceptable for fire safety)
- **Privacy/GDPR:** Requires data residency guarantees
- **Vendor Lock-in:** Cloud platform dependency
- **Costs:** Bandwidth + compute fees can accumulate

**Recommended Use Case for Fire Safety:**
- **NOT suitable** as the sole architecture for fire detection (too risky)
- Suitable for secondary analytics: occupancy patterns, seal degradation trends, predictive maintenance

### Recommended Hybrid Approach (for FireGlass)

**Best Practice:** Edge processing for immediate fire safety; cloud for analytics and audit trails.

1. **Local MQTT Broker** with rules engine (e.g., Mosquitto + custom middleware)
2. **Fire Detection Logic** runs locally: If temp > 150°C AND smoke > 100 mg/m³ → immediate local alarm (within 5 seconds)
3. **Cloud Sync:** Event logs, daily aggregated analytics, anomaly detection shipped to cloud asynchronously
4. **Network Resilience:** System functions offline; syncs when connection restored
5. **Audit Trail:** Cloud maintains 5-year log of all fire events, system diagnostics, compliance checks

---

## Major IoT Cloud Platforms for Building Automation

Three major cloud platform providers dominate the building IoT market. Each offers services for data ingestion, storage, analytics, and device management.

### AWS IoT Core

**Market Position:** Dominant player in enterprise IoT; used by ~40% of large commercial real estate platforms.

**Key Services:**
- **IoT Core:** MQTT/WebSocket broker; device connectivity and provisioning
- **IoT Rules Engine:** SQL-based rule definition for message routing
- **DynamoDB/S3:** Data storage (structured and unstructured)
- **Lambda:** Serverless compute for event processing
- **SageMaker:** Machine learning for predictive maintenance

**MQTT Integration:**
AWS IoT Core provides native MQTT v5 endpoint. Helion sensors can publish directly to AWS using certificate-based authentication (X.509).

**Cost Model:**
- **Data Ingestion:** $0.02 per 1 million MQTT messages
- **Storage:** $0.25 per GB/month in DynamoDB
- **Compute (Lambda):** Pay-per-execution
- **Typical Monthly Cost for 100-Building Network:** $200–$500

**Pros for FireGlass:**
- Mature, reliable service
- MQTT v5 native support
- Integration with Brick Schema and FIWARE (via third-party adapters)
- Strong security and compliance (SOC 2, HIPAA, GDPR-ready with EU data residency options)

**Cons:**
- Learning curve (AWS ecosystem is large)
- Vendor lock-in (data export can be complex)
- Egress fees (data downloaded from AWS incurs charges)

---

### Microsoft Azure IoT Hub

**Market Position:** ~25% market share in enterprise IoT; strong in organizations with existing Azure/Office 365 footprint.

**Key Services:**
- **IoT Hub:** Managed MQTT/AMQP/HTTPS gateway
- **Stream Analytics:** Real-time data processing (SQL-like language)
- **Cosmos DB:** Globally distributed NoSQL database
- **Azure Machine Learning:** ML model deployment and monitoring
- **Power BI:** Data visualization and dashboards

**MQTT Integration:**
Azure IoT Hub supports MQTT v5 but prefers proprietary AMQP. MQTT integration available but less optimized than AWS.

**Cost Model:**
- **S1 Standard Tier:** ~$400/month (includes 400,000 messages/day)
- **Storage:** ~$0.50/GB in Cosmos DB
- **Typical Monthly Cost:** $400–$800

**Pros for FireGlass:**
- Strong integration with Microsoft enterprise software (Office, Teams, Power Platform)
- Good for organizations already on Azure
- EU data residency options (Germany, UK)

**Cons:**
- MQTT less native than AWS
- Learning curve with Azure-specific tools
- Fewer third-party integrations with building IoT standards (Brick, FIWARE)

---

## Connectivity Options for Building Sensors

Different buildings have different network infrastructure. Fire safety sensors must be reliable; selecting the right connectivity is critical.

### WiFi (802.11ac/WiFi 6)

**Characteristics:**
- **Range:** 50–100 meters (requires robust network planning in large buildings)
- **Bandwidth:** 150+ Mbps (more than sufficient for sensors)
- **Power Consumption:** Moderate (sensors can be mains-powered)
- **Cost:** Minimal incremental cost (buildings already have WiFi)

**Suitable For:**
- Buildings with modern WiFi infrastructure (enterprise networks)
- New constructions where access points can be planned
- Retrofit buildings with acceptable signal strength

**Challenges:**
- Legacy buildings may have poor coverage
- Interference from other devices (microwaves, Bluetooth, adjacent networks)
- Corporate WiFi networks may restrict IoT device connectivity (security policies)
- Industrial environments: metal/machinery cause severe attenuation

**For FireGlass:** Recommended primary connectivity given building mains power availability. Helion includes WiFi 6 (802.11ax) module for excellent range and reliability.

---

### Ethernet (Hardwired)

**Characteristics:**
- **Range:** Limited to physical wiring (typically building infrastructure)
- **Bandwidth:** Gigabit (1 Gbps) or Fast Ethernet (100 Mbps)
- **Power Consumption:** Minimal (Power-over-Ethernet option available)
- **Reliability:** Extremely high (wired, no interference)
- **Cost:** Moderate (requires cable runs during construction or retrofit)

**Suitable For:**
- Buildings with existing Ethernet infrastructure
- New construction where network cabling is planned
- Fire-critical systems requiring maximum reliability

**For FireGlass:** Recommended as preferred option for new construction. Helion includes optional Ethernet port with PoE support. Eliminates WiFi reliability concerns.

---

## Data Standards and Interoperability Formats

One of the largest pain points in building IoT is fragmentation in data formats. Three major standards are emerging; interoperability with these will be critical for market adoption.

### Brick Schema

**Overview:** Semantic data model for building systems. Built on web technologies (RDF, OWL). Developed by open community with backing from research institutions and major building vendors.

**Data Model Example (RDF):**
```
<pyrosense_temp_sensor> a brick:Fire_Temperature_Sensor ;
    brick:hasSensor <temp_measurement> ;
    brick:isPartOf <building_zone_a> ;
    brick:hasTag "critical" .

<temp_measurement> a brick:Temperature ;
    brick:value "145.2"^^xsd:double ;
    brick:unit qudt:DegreeCelsius .
```

**Key Advantage:**
- Rich semantic relationships (machine-interpretable)
- Enables reasoning and inference (e.g., "all critical fire sensors in Zone A")
- Foundation for future AI/ML applications

**Complexity:**
- Steeper learning curve (RDF/OWL knowledge required)
- Slower adoption than Haystack in commercial market

**Implementation for FireGlass:**
- Cloud platform will support Brick Schema export (planned 2027)
- Enables research institutions and large enterprises to query FireGlass data using semantic tools

---

### FIWARE (European Open-Source Initiative)

**Overview:** Open data standards and reference architecture for smart cities and buildings. Supported by the European Commission. Gaining traction in EU-funded smart building projects.

**Key Components:**
- **NGSI-LD:** Context information management (similar to Brick Schema)
- **Open Geospatial Consortium (OGC):** Geographic information integration
- **European data governance:** Built for GDPR compliance

**Data Model Example:**
```json
{
  "id": "urn:ngsi-ld:Fire_Sensor:helion_tg400_001",
  "type": "FireSensor",
  "temperature": {
    "type": "Property",
    "value": 145.2,
    "unitCode": "CEL"
  },
  "smokeParticleDensity": {
    "type": "Property",
    "value": 85.5,
    "unitCode": "MGM3"
  },
  "location": {
    "type": "GeoProperty",
    "value": { "type": "Point", "coordinates": [12.5, 45.6] }
  }
}
```

**Key Advantage:**
- EU-backed standard (relevant for European expansion)
- Strong GDPR and data governance integration
- Interoperability with EU Digital Twin initiatives

**Implementation for FireGlass:**
- FIWARE is increasingly mandatory in EU-funded smart building projects
- Cloud platform will support NGSI-LD export (planned 2027)
- Positions FireGlass as compliant with European digital infrastructure initiatives

---

## Challenges in Current IoT Fire Safety Market

### 1. Firmware Fragmentation

**Problem:** Each sensor manufacturer (Helion, SensorPulse, ThermalVision Labs, ClimateSense) maintains proprietary firmware. Firmware updates are inconsistent:
- Update frequency varies (Helion: quarterly; others: ad-hoc)
- Update deployment: some OTA-capable, others require manual installation
- Breaking changes: firmware updates sometimes alter data formats, requiring BMS platform updates

**Impact on FireGlass:**
- Customers hesitate to mix sensor brands (risk of incompatible firmware versions)
- Support burden increases (must maintain compatibility with multiple firmware versions)

**Mitigation:**
- EPFC-Connect standardizes data formats (regardless of firmware version)
- Helion will commit to backward-compatible firmware updates (5-year support window)
- Publish firmware release notes with migration guidance

### 2. Certification Delays

**Problem:** EPFC-2200, EPFC-2201, and ASG-FP certifications require lengthy lab testing. Typical timeline: 8–10 months. Competitors may introduce features faster than certifications can validate.

**Impact on FireGlass:**
- New sensor models may be delayed 12+ months before entering market
- Regulatory changes (EU Smart Building Directive) may supersede certification requirements during test phase

**Mitigation:**
- Plan certification pipeline 18 months in advance
- Maintain dialogue with Veridian Test Labs and ASG to track regulatory changes
- Consider modular product architecture (certify core platform, then add features with incremental certifications)

### 3. WiFi Interference in Industrial Environments

**Problem:** Industrial buildings (manufacturing, warehousing) have metal structures, machinery, and RF noise. WiFi propagation is severely attenuated. 2.4 GHz band heavily congested.

**Impact on FireGlass:**
- WiFi reliability < 95% in some industrial buildings (unacceptable for fire safety)
- Fallback to Ethernet required; retrofit costs high

**Mitigation:**
- Design Helion sensors with dual connectivity (WiFi + Ethernet PoE)
- Recommend WiFi site survey before installation
- For industrial retrofit: Ethernet as primary; WiFi as backup
- Consider LoRaWAN or NB-IoT for outdoor/perimeter sensors (future roadmap 2027+)

---

## Recommended Interoperability Roadmap for Innovative Windows LLC

**Current State (2026):**
- Helion sensors publish native MQTT v5
- Customers receive raw MQTT telemetry
- Integration with customer BMS requires custom middleware
- Limited standardization

**Recommended 2026–2028 Roadmap:**

1. **Phase 1: EPFC-Connect Compliance (Q3 2026)**
   - Helion firmware update to support EPFC-Connect REST + MQTT endpoints
   - FireGlass cloud platform exposes EPFC-Connect interface
   - Enables BMS vendors to integrate without custom development

2. **Phase 2: Brick Schema Export (2027)**
   - Cloud platform exports Helion telemetry in Brick Schema format
   - Enables interoperability with research institutions and large enterprises

3. **Phase 3: FIWARE NGSI-LD Export (2027)**
   - Cloud platform exports Helion telemetry in NGSI-LD format
   - Positions FireGlass as compliant with EU Digital Twin initiatives

4. **Phase 4: Multi-Sensor Ecosystem (2028)**
   - Evaluate support for SensorPulse and other manufacturers (via EPFC-Connect)
   - Protocol-agnostic gateway (Apache NiFi, Node-RED) for legacy sensor integration
   - Maintains Helion as primary offering; permits customer choice for redundancy

---

## Technical Debt and Vendor Lock-In Mitigation

**Current Risk:**
Helion is a proprietary sensor platform. If Innovative Windows LLC fails to support open standards, customers will perceive vendor lock-in.

**Mitigation Recommendations:**

1. **Open Data Export:** Always allow customers to export raw sensor data (CSV, JSON, MQTT topics) without proprietary licensing

2. **Standard Protocol Support:** MQTT v5 is already open standard; continue supporting it without proprietary wrappers

3. **Clear Interoperability Roadmap:** Communicate Brick Schema/FIWARE/EPFC-Connect plans to customers in writing

4. **Avoid Proprietary Cloud Lock-In:** If building cloud services, use standard APIs (not AWS-only); ensure GDPR data portability

5. **Firmware Transparency:** Publish firmware release notes, deprecation schedules, and backward-compatibility commitments

---

## References and Reading

- OASIS MQTT Version 5.0 Specification
- EPFC-2200 and EPFC-2201 Standards (available from European Passive Fire Council)
- EPFC-Connect Technical Specification v1.0 (2025)
- Brick Schema Documentation (https://brickschema.org)
- FIWARE Smart Data Models (https://smartdatamodels.org)
- AWS IoT Core Developer Guide
- EU Building Performance Directive - Digital Building Data Requirements (2024)
- Veridian TRC-500 Test Protocol (available from Veridian Test Labs, Lyon)

---

*This document reflects the technical landscape as of March 2026. IoT standards and platform capabilities evolve rapidly. Review and update annually.*
