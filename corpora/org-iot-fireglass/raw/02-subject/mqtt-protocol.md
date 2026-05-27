# FireGlass MQTT Protocol Specification

**Project:** FireGlass (Atlas Forge LLC for Innovative Windows LLC)
**Document Version:** 1.2
**Last Updated:** 2025-09-15
**Status:** In Development (Broker configuration deferred; Security implementation in progress)

---

## 1. Protocol Overview

MQTT (Message Queuing Telemetry Transport) was selected as the primary protocol for FireGlass IoT communication due to its lightweight footprint, low bandwidth requirements, and suitability for sensor-to-cloud architectures. The Helion sensors deployed in Innovative Windows' smart fire-resistant window installations transmit real-time environmental and fire-risk data (temperature, smoke particle density, air quality metrics) at intervals ranging from 30 seconds to 5 minutes depending on operational context.

### Rationale

The FireGlass system must handle:
- **High-frequency telemetry** from distributed sensor arrays (one or more Helion units per window installation)
- **Unreliable network conditions** at customer premises (fallback to cellular, intermittent WiFi)
- **Low-power constraints** on edge hardware
- **Real-time alerting** for threshold breaches (smoke density > 500 μg/m³, edge temperature > 65°C)
- **Scalability** to hundreds of customer sites with thousands of sensors

MQTT excels in these scenarios because it:
- Uses publish-subscribe architecture, decoupling producers and consumers
- Offers flexible QoS levels (0, 1, 2) for different reliability requirements
- Supports last-will-testament for graceful connection loss detection
- Provides retained messages for stateful sensor status
- Operates efficiently over TCP with minimal overhead

### QoS Strategy Overview

The FireGlass implementation employs a tiered QoS approach:
- **QoS 1 (At Least Once):** Routine sensor readings (temperature, smoke, air quality) — acceptable for some duplicate data points; loss of single readings is non-critical
- **QoS 2 (Exactly Once):** Alert payloads and threshold breaches — critical events require guaranteed delivery with no duplicates
- **QoS 0 (At Most Once):** Heartbeat/status pings — fire-and-forget, low overhead, acceptable loss

---

## 2. Broker Configuration

### Current Status: UNRESOLVED

The broker hosting decision remains unresolved as of this specification. Three options are under evaluation:

1. **Mosquitto (Self-Hosted)**
   - Lightweight, open-source MQTT broker
   - Full control over infrastructure and data residency
   - Operational overhead for provisioning, monitoring, and scaling
   - Suitable for on-premise or private cloud deployment

2. **AWS IoT Core**
   - Managed service with built-in security (mutual TLS, fine-grained IAM policies)
   - Scales automatically to millions of concurrent connections
   - Integrated with AWS ecosystem (CloudWatch, Lambda, DynamoDB)
   - Per-message and connection costs; potential lock-in risk

3. **HiveMQ Cloud**
   - Fully managed MQTT broker with 99.99% SLA
   - Built-in monitoring, audit logging, and role-based access control
   - Enterprise-grade clustering and failover
   - Transparent pricing; vendor-neutral (not tied to cloud provider)

### Decision Deferred to Sprint 4

**Samir Osei (Tech Lead)** has deferred the broker selection pending load testing results. Before committing to a production broker, the team needs to:
- Simulate peak load scenarios (1,000+ concurrent sensor connections)
- Measure message throughput and latency under stress
- Evaluate cost implications for the projected customer base
- Test failover and disaster recovery procedures

### Development Environment

For all current development work, the team is **using a local Mosquitto instance** running on the development machine. Configuration:

```bash
# Docker container: eclipse-mosquitto:latest
# Port: 1883 (unencrypted, for dev only)
# Exposed to localhost only
docker run -p 1883:1883 eclipse-mosquitto
```

All development clients (simulator, Node.js backend, test harnesses) connect to `mqtt://localhost:1883`.

---

## 3. Topic Hierarchy

FireGlass employs a hierarchical topic structure that organizes data by customer, site, window, and metric type. This design enables:
- **Selective subscriptions** by the backend (e.g., all windows at a specific site)
- **Granular access control** (future: ACLs per customer)
- **Logical organization** for monitoring and troubleshooting

### Topic Structure

```
fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/{metric}
```

**Note:** The topic prefix here is `fireglass/` (no hyphen). This specification currently differs from an earlier draft that used `fire-glass/` — this inconsistency is under review and should be resolved before production.

### Path Components

- **`customer_id`**: Unique identifier for the customer organization (e.g., `cust_001`, `innovative-windows-hq`)
- **`site_id`**: Unique identifier for the customer's installation site (e.g., `site_nyc_office`, `site_manufacturing_facility`)
- **`window_id`**: Unique identifier for the smart window unit (e.g., `win_floor3_east`, `win_demo_unit_1`)
- **`metric`**: Sensor reading type (see subsections below)

### Metric Types and Topics

#### Temperature Readings
```
fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/temperature/ambient
fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/temperature/edge
```

- `ambient`: Room temperature near the window (°C) — measured by Helion TG-400
- `edge`: Temperature at the window glass edge (critical for fire detection; °C) — measured by Helion TG-400
- Example: `fireglass/customer/innovative-windows-hq/site/site_nyc_office/window/win_042/temperature/edge` maps to a TG-400 reading

#### Smoke Particle Density
```
fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/smoke
```

Optical sensor output in μg/m³ (micrograms per cubic meter) from Helion SM-220. Threshold: >500 triggers alert.

#### Air Quality
```
fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/air-quality/co
fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/air-quality/co2
fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/air-quality/voc
```

- `co`: Carbon monoxide concentration (ppm) — from Helion AQ-100
- `co2`: Carbon dioxide concentration (ppm) — from Helion AQ-100
- `voc`: Volatile organic compound index (0–500 scale) — from Helion AQ-100

#### Device Status / Heartbeat
```
fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/status
```

Device connectivity, firmware version, battery status. Published every 5 minutes (QoS 1, retained).

#### Alerts
```
fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/alert
```

Threshold breach notifications (smoke, temperature, etc.). Published on-demand (QoS 2).

### Wildcards

The backend subscribes to multiple topics using wildcards:

```
# Subscribe to all metrics for a specific window
fireglass/customer/cust_001/site/site_nyc/window/win_001/#

# Subscribe to all temperature readings across a site
fireglass/customer/cust_001/site/site_nyc/window/+/temperature/#

# Subscribe to all alerts across all customers (typically filtered at app level)
fireglass/customer/+/site/+/window/+/alert
```

---

## 4. Message Payloads

All payloads are transmitted as JSON UTF-8 strings. Timestamps are in ISO 8601 format (with time zone) unless otherwise noted.

### 4.1 Temperature Reading Payload

```json
{
  "sensor_id": "pyr_001",
  "window_id": "win_floor3_east",
  "metric_type": "temperature",
  "location": "ambient",
  "value": 22.5,
  "unit": "celsius",
  "timestamp": "2025-09-15T14:32:17.456Z",
  "quality": "good",
  "rssi": -65,
  "sensor_model": "TG-400"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `sensor_id` | string | Helion unit identifier |
| `window_id` | string | Associated window identifier |
| `metric_type` | string | Always `"temperature"` |
| `location` | string | `"ambient"` or `"edge"` |
| `value` | number | Temperature in °C |
| `unit` | string | Always `"celsius"` |
| `timestamp` | string | ISO 8601 with timezone |
| `quality` | string | `"good"`, `"fair"`, `"poor"` (signal quality) |
| `rssi` | number | WiFi signal strength (dBm) |
| `sensor_model` | string | Model identifier (`"TG-400"` for temperature) |

### 4.2 Smoke Density Payload

```json
{
  "sensor_id": "pyr_001",
  "window_id": "win_floor3_east",
  "metric_type": "smoke",
  "value": 145.3,
  "unit": "micrograms_per_cubic_meter",
  "timestamp": "2025-09-15T14:32:45.123Z",
  "quality": "good",
  "optical_sensor_version": "v1.2",
  "calibration_date": "2025-08-15",
  "sensor_model": "SM-220"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `sensor_id` | string | Helion unit identifier |
| `window_id` | string | Associated window identifier |
| `metric_type` | string | Always `"smoke"` |
| `value` | number | Particle density in μg/m³ |
| `unit` | string | Always `"micrograms_per_cubic_meter"` |
| `timestamp` | string | ISO 8601 with timezone |
| `quality` | string | `"good"`, `"fair"`, `"poor"` |
| `optical_sensor_version` | string | Optical sensor firmware version |
| `calibration_date` | string | Date of last calibration (YYYY-MM-DD) |
| `sensor_model` | string | Model identifier (`"SM-220"` for smoke) |

### 4.3 Air Quality Payload

```json
{
  "sensor_id": "pyr_001",
  "window_id": "win_floor3_east",
  "metric_type": "air_quality",
  "readings": {
    "co": {
      "value": 0.8,
      "unit": "ppm"
    },
    "co2": {
      "value": 410,
      "unit": "ppm"
    },
    "voc": {
      "value": 85,
      "unit": "index"
    }
  },
  "timestamp": "2025-09-15T14:33:12.789Z",
  "quality": "good",
  "sensor_model": "AQ-100"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `sensor_id` | string | Helion unit identifier |
| `window_id` | string | Associated window identifier |
| `metric_type` | string | Always `"air_quality"` |
| `readings` | object | Sub-object containing CO, CO₂, VOC measurements |
| `readings.co.value` | number | Carbon monoxide (ppm) |
| `readings.co2.value` | number | Carbon dioxide (ppm) |
| `readings.voc.value` | number | VOC index (0–500) |
| `timestamp` | string | ISO 8601 with timezone |
| `quality` | string | Overall reading quality |
| `sensor_model` | string | Model identifier (`"AQ-100"` for air quality) |

### 4.4 Device Status / Heartbeat Payload

```json
{
  "sensor_id": "pyr_001",
  "window_id": "win_floor3_east",
  "firmware_version": "2.3.1",
  "hardware_version": "rev_b",
  "device_battery_pct": 100,
  "uptime_seconds": 86400,
  "timestamp": "2025-09-15T14:35:00.000Z",
  "wifi_ssid": "customer-network",
  "wifi_signal_strength": -65
}
```

| Field | Type | Description |
|-------|------|-------------|
| `sensor_id` | string | Helion unit identifier |
| `window_id` | string | Associated window identifier |
| `firmware_version` | string | Current firmware version (e.g., `"2.3.1"`) |
| `hardware_version` | string | Hardware revision (e.g., `"rev_b"`) |
| `device_battery_pct` | number | Battery percentage (0–100) |
| `uptime_seconds` | number | Seconds since last boot |
| `timestamp` | string | ISO 8601 with timezone |
| `wifi_ssid` | string | Connected SSID |
| `wifi_signal_strength` | number | RSSI in dBm |

**NOTE on battery field:** The `device_battery_pct` field is always `100` for mains-powered Helion units. This is a firmware limitation, not removable. The manufacturer (Helion) confirmed that all current deployments will be mains-powered; this field is retained for future extensibility.

**NOTE on timestamp format:** The timestamp format was changed from Unix epoch (seconds since 1970-01-01 UTC) to ISO 8601 in firmware version 2.3.1. The backend must handle both formats for backward compatibility with devices running older firmware:
- **Old format (v2.3.0 and earlier):** `1726416900` (numeric Unix timestamp)
- **New format (v2.3.1+):** `"2025-09-15T14:35:00.000Z"` (ISO 8601 string)

```json
{
  "sensor_id": "pyr_001",
  // NOTE: timestamp format changed from Unix epoch to ISO 8601 in firmware v2.3.1 — backend must handle both
  "timestamp": 1726416900,
  "firmware_version": "2.3.0"
}
```

### 4.5 Alert Payload (Threshold Breach)

```json
{
  "alert_id": "alert_20250915_001",
  "sensor_id": "pyr_001",
  "window_id": "win_floor3_east",
  "customer_id": "cust_001",
  "site_id": "site_nyc",
  "alert_type": "threshold_breach",
  "severity": "critical",
  "metric": "smoke",
  "threshold": 500,
  "current_value": 625.8,
  "unit": "micrograms_per_cubic_meter",
  "triggered_at": "2025-09-15T14:36:42.123Z",
  "description": "Smoke particle density exceeds critical threshold of 500 μg/m³"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `alert_id` | string | Unique alert identifier |
| `sensor_id` | string | Helion unit identifier |
| `window_id` | string | Associated window identifier |
| `customer_id` | string | Customer organization ID |
| `site_id` | string | Site identifier |
| `alert_type` | string | `"threshold_breach"`, `"connectivity_loss"`, etc. |
| `severity` | string | `"warning"`, `"critical"` |
| `metric` | string | Metric that triggered alert (e.g., `"smoke"`, `"temperature"`) |
| `threshold` | number | Threshold value that was exceeded |
| `current_value` | number | Current sensor reading |
| `unit` | string | Unit of measurement |
| `triggered_at` | string | ISO 8601 timestamp when alert was generated |
| `description` | string | Human-readable description |

---

## 5. QoS Strategy

### QoS 1: Sensor Readings (At Least Once)

**Topics:**
- `fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/temperature/#`
- `fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/smoke`
- `fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/air-quality/#`

**Justification:** Sensor readings are telemetry data. While we prefer not to lose data, the loss of a single reading (out of many per minute) does not impact the overall safety model. QoS 1 ensures the message is delivered at least once (may be duplicated), with less overhead than QoS 2.

**Implementation:**
```typescript
// Node.js mqtt.js example
client.publish(
  `fireglass/customer/${customerId}/site/${siteId}/window/${windowId}/temperature/ambient`,
  JSON.stringify(payload),
  { qos: 1 }
);
```

### QoS 2: Alerts (Exactly Once)

**Topics:**
- `fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/alert`

**Justification:** Alerts signal critical events (fire risk, threshold breach). Duplicate alerts could trigger redundant notifications or false escalations. QoS 2 guarantees exactly-once delivery, with higher overhead but acceptable for low-frequency alert events.

**Implementation:**
```typescript
client.publish(
  `fireglass/customer/${customerId}/site/${siteId}/window/${windowId}/alert`,
  JSON.stringify(alertPayload),
  { qos: 2 }
);
```

### QoS 0: Heartbeats (At Most Once)

**Topics:**
- `fireglass/customer/{customer_id}/site/{site_id}/window/{window_id}/status`

**Justification:** Heartbeats are sent frequently (every 5 minutes) and serve as a "keep-alive" signal. The loss of a single heartbeat is acceptable; the backend can infer device health from the absence of readings. QoS 0 minimizes overhead.

**Implementation:**
```typescript
client.publish(
  `fireglass/customer/${customerId}/site/${siteId}/window/${windowId}/status`,
  JSON.stringify(heartbeatPayload),
  { qos: 0 }
);
```

---

## 6. Retained Messages

MQTT retained messages are used to maintain state for device status and allow late-joining subscribers to immediately access the most recent value.

### Strategy

- **Device Status (Heartbeat):** Retained with QoS 1. When a new backend instance subscribes to a site, it immediately receives the latest status for all windows, enabling rapid state reconstruction without waiting for the next heartbeat cycle.

- **Sensor Readings:** Not retained. Readings are telemetry; retaining each reading would create unnecessary broker storage overhead and mislead subscribers about stale data age.

- **Alerts:** Not retained. Alerts are events; a late-joining subscriber should not process expired alerts.

### Implementation (Helion Firmware)

```
// Pseudo-code for Helion device
MQTT.publish(
  topic: "fireglass/customer/{id}/site/{id}/window/{id}/status",
  payload: heartbeatJson,
  qos: 1,
  retain: true
)
```

### Clearing Retained Messages

To clear a retained message (e.g., when decommissioning a window), publish an empty payload with retain flag:

```bash
mosquitto_pub -h localhost -t "fireglass/customer/cust_001/site/site_nyc/window/win_001/status" -n -r
```

---

## 7. Security

### Current State: Aspirational

The FireGlass security model is **aspirational** and not yet fully implemented. The current development and testing environment uses username/password authentication over unencrypted MQTT. Production deployment will upgrade to the following.

### Compliance Requirements

EPFC-2201 §4.3 requires EU-SmartSafe Mark compliance for all field-deployed IoT sensors. HelionLink v2.3 includes TLS 1.3 support as standard — pending activation in production deployment.

### Target: TLS + Client Certificates

1. **Broker-to-Client Encryption (TLS 1.2+)**
   - All MQTT connections use TLS on port 8883
   - Broker certificate signed by a trusted CA (Let's Encrypt or corporate PKI)
   - Prevents eavesdropping on sensor data in transit

2. **Client Authentication (Mutual TLS)**
   - Each Helion device is provisioned with a unique client certificate (signed by FireGlass CA)
   - Each backend service instance has a service certificate
   - Broker validates client certificate and revokes access if compromised
   - No username/password required; identity is cryptographic

3. **Authorization**
   - ACLs (Access Control Lists) on the broker restrict which topics each client can publish/subscribe to
   - Helion devices can only publish to `fireglass/customer/{their_customer_id}/#`
   - Backend services can subscribe to `fireglass/customer/#` but cannot publish to sensor topics

### Development Setup (Current)

For development and testing, Mosquitto is configured with basic authentication:

```conf
# mosquitto.conf (dev only)
allow_anonymous false
password_file /etc/mosquitto/passwd
```

Users are created via:
```bash
mosquitto_passwd -c /etc/mosquitto/passwd pyrosense_dev
```

This is **NOT suitable for production** and will be replaced with TLS + certificates before any customer deployment.

---

## 8. Client Implementation Notes

### 8.1 Device-Side (Helion Firmware)

The Helion sensors are firmware-based IoT devices that handle MQTT publication. The firmware is maintained by the sensor manufacturer and provided as a closed binary.

**Firmware Integration Status:**

Helion TG-400, SM-220, and AQ-100 firmware documentation (v2.3) was requested from Helion Sensor Technologies on 2025-08-04. As of this writing, the team has received only the basic MQTT payload format specification. The comprehensive integration specification—including OTA (over-the-air) update commands, calibration endpoints, and debug logging endpoints—is pending delivery from the manufacturer.

**Current Integration Approach:**

John Smith (Field Technician) has been testing with sample payloads reverse-engineered from the demo unit. The team has confirmed that:
- Basic sensor reading payloads conform to the schema in Section 4 (with minor variations in timestamp format depending on firmware version)
- The device connects to the MQTT broker using the configured SSID and credentials
- Heartbeat interval is configurable (currently 5 minutes)
- Threshold values for alerts are configurable via a local web interface on the device

**Outstanding Items:**

- Full firmware API documentation (for OTA updates and remote recalibration)
- Calibration procedure and safety specifications
- Expected latency and jitter in message publication
- Failure modes and recovery behavior (e.g., broker disconnection, network loss)

Until these are received, integration testing is limited to the happy path (normal operation with live broker). Fault injection testing is pending.

### 8.2 Server-Side (Node.js Backend)

The FireGlass backend is a Next.js 14 TypeScript application. MQTT subscription and message handling use the **mqtt.js** library.

#### Installation

```bash
npm install mqtt
```

#### Basic Connection

```typescript
import mqtt, { MqttClient } from 'mqtt';

const client: MqttClient = mqtt.connect('mqtt://localhost:1883', {
  clientId: 'fireglass-backend-001',
  username: 'backend_user',
  password: 'secure_password_here', // TODO: move to env var
});

client.on('connect', () => {
  console.log('Connected to MQTT broker');
  // Subscribe to all FireGlass topics
  client.subscribe('fireglass/customer/+/site/+/window/+/#', (err) => {
    if (err) console.error('Subscription error:', err);
  });
});

client.on('error', (err) => {
  console.error('MQTT client error:', err);
});
```

#### Message Handler with Payload Parsing

```typescript
client.on('message', (topic: string, payload: Buffer) => {
  try {
    const message = JSON.parse(payload.toString());
    const parts = topic.split('/');

    const customerId = parts[2];
    const siteId = parts[4];
    const windowId = parts[6];
    const metric = parts.slice(7).join('/'); // e.g., "temperature/ambient"

    // Route to appropriate handler
    if (metric.startsWith('alert')) {
      handleAlert(message, customerId, siteId, windowId);
    } else if (metric.includes('temperature')) {
      handleTemperature(message, customerId, siteId, windowId);
    } else if (metric === 'smoke') {
      handleSmoke(message, customerId, siteId, windowId);
    } else if (metric.includes('air-quality')) {
      handleAirQuality(message, customerId, siteId, windowId);
    } else if (metric === 'status') {
      handleStatus(message, customerId, siteId, windowId);
    }
  } catch (error) {
    console.error(`Failed to parse message on topic ${topic}:`, error);
  }
});
```

#### Handling Timestamp Format Variations

```typescript
function parseTimestamp(ts: string | number): Date {
  if (typeof ts === 'number') {
    // Unix epoch (seconds)
    return new Date(ts * 1000);
  }
  // ISO 8601 string
  return new Date(ts);
}

const readingTime = parseTimestamp(message.timestamp);
```

#### Publishing Alerts from Backend

```typescript
function publishAlert(
  customerId: string,
  siteId: string,
  windowId: string,
  alertData: AlertPayload
): Promise<void> {
  return new Promise((resolve, reject) => {
    const topic = `fireglass/customer/${customerId}/site/${siteId}/window/${windowId}/alert`;
    client.publish(topic, JSON.stringify(alertData), { qos: 2 }, (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
}
```

---

## 9. Monitoring & Dead Letter Queue

### Monitoring (Planned)

The team plans to implement the following monitoring capabilities:
- **Broker metrics:** Connection count, message throughput, queue depth
- **Client health:** Last message timestamp per device, connection status, message loss rate
- **Alert tracking:** Alert volume by type, response time, escalation status
- **Error rates:** MQTT connection failures, message parse errors, delivery failures

Monitoring will be integrated with Prometheus and visualized in Grafana. Target: Sprint 5.

### Dead Letter Queue

**TBD.** Samir flagged this as P2 for post-launch. Failed messages currently logged to console only.

> Clara: should we at least write them to a file? —Slack #dev-backend, 2025-09-12

---

## 10. Development Tools

### Sensor Simulator

For local development, use the sensor-simulator script to generate mock Helion data:

```bash
ts-node /tools/mqtt-simulator.ts --customer cust_001 --site site_dev --window win_demo --rate 30s
```

This tool publishes synthetic sensor payloads (temperature, smoke, air quality, status, alerts) at configurable intervals to the local Mosquitto broker. Useful for:
- Testing backend subscription and message handling logic
- Developing alert thresholds without hardware
- Load testing with multiple simulated windows

**Note:** The sensor-simulator script is referenced in this specification but has not yet been committed to the project repository. See `/tools/mqtt-simulator.ts` (pending).

---

## Appendix: Topic Reference

| Topic | QoS | Retained | Frequency | Purpose |
|-------|-----|----------|-----------|---------|
| `fireglass/customer/{id}/site/{id}/window/{id}/temperature/ambient` | 1 | No | 1 min | Ambient room temperature |
| `fireglass/customer/{id}/site/{id}/window/{id}/temperature/edge` | 1 | No | 1 min | Window edge temperature (fire risk) |
| `fireglass/customer/{id}/site/{id}/window/{id}/smoke` | 1 | No | 1 min | Smoke particle density |
| `fireglass/customer/{id}/site/{id}/window/{id}/air-quality/co` | 1 | No | 2 min | Carbon monoxide concentration |
| `fireglass/customer/{id}/site/{id}/window/{id}/air-quality/co2` | 1 | No | 2 min | Carbon dioxide concentration |
| `fireglass/customer/{id}/site/{id}/window/{id}/air-quality/voc` | 1 | No | 2 min | Volatile organic compound index |
| `fireglass/customer/{id}/site/{id}/window/{id}/status` | 1 | Yes | 5 min | Device heartbeat and status |
| `fireglass/customer/{id}/site/{id}/window/{id}/alert` | 2 | No | On breach | Threshold breach notifications |

---

**Document prepared by:** Samir Osei (Tech Lead), with contributions from Clara Duval (Junior Dev) and John Smith (Field Technician)
**Review Status:** Pending QA and security review
**Next Review:** 2025-10-15
