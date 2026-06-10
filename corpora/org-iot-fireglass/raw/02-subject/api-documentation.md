# FireGlass API Documentation

**Version:** 1.0.0
**Last Updated:** 2025-12-15
**Maintainers:** Samir Osei (Tech Lead), Clara Duval (Junior Dev)

---

## Table of Contents

1. [Overview](#overview)
2. [Base URL & Authentication](#base-url--authentication)
3. [Endpoints](#endpoints)
4. [Request/Response Examples](#requestresponse-examples)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Pagination](#pagination)
8. [WebSocket Events](#websocket-events)
9. [Postman Collection](#postman-collection)

---

## Overview

The FireGlass API provides access to the complete smart fire-resistant window management platform. The system integrates IoT sensor data from Helion devices (via HelionLink protocol) with a Next.js 14 + TypeScript backend, using PostgreSQL for persistence and Supabase for authentication and real-time capabilities.

### Key Features

- JWT-based authentication with automatic token refresh
- Real-time sensor streaming via WebSockets
- Cursor-based pagination for list endpoints
- Comprehensive audit trails for installations and inspections
- PDF report generation for compliance documentation
- MQTT integration for sensor telemetry (`fireglass/*` topic prefix)

---

## Base URL & Authentication

### Base URL

```
https://api.fireglass.atlas-forge.io/api
```

All endpoints require HTTPS. Development and staging URLs:
- **Development:** `https://dev-api.fireglass.atlas-forge.io/api`
- **Staging:** `https://staging-api.fireglass.atlas-forge.io/api`

### Authentication

FireGlass uses JWT (JSON Web Tokens) issued by Supabase Auth. All authenticated requests must include:

```
Authorization: Bearer <JWT_TOKEN>
```

#### Token Lifecycle

1. **Login** → Receive `access_token` (15 minutes) and `refresh_token` (7 days)
2. **Access Token Expiry** → Use refresh token to obtain new access token
3. **Refresh Token Expiry** → User must re-authenticate

#### Headers

```
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-API-Version: 1.0
```

---

## Endpoints

### Authentication

#### `POST /auth/login`

Authenticate a user and receive JWT tokens.

**Request:**
```json
{
  "email": "john.smith@innovativewindows.com",
  "password": "SecurePassword123!",
  "role": "field_technician"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 900,
  "user": {
    "id": "user_12345",
    "email": "john.smith@innovativewindows.com",
    "name": "John Smith",
    "role": "field_technician"
  }
}
```

---

#### `POST /auth/refresh`

Obtain a new access token using a refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 900
}
```

---

#### `GET /auth/me`

Retrieve the current authenticated user's profile.

**Response (200 OK):**
```json
{
  "id": "user_12345",
  "email": "john.smith@innovativewindows.com",
  "name": "John Smith",
  "role": "field_technician",
  "company": "Innovative Windows LLC",
  "created_at": "2025-07-21T10:30:00Z",
  "permissions": [
    "read:installations",
    "read:sensors",
    "write:inspections"
  ]
}
```

---

### Customers

#### `GET /customers`

List all customers with pagination.

**Query Parameters:**
- `cursor` (string, optional) — Cursor for pagination
- `limit` (integer, optional, default: 20) — Number of results

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "cust_00001",
      "name": "Innovative Windows LLC",
      "industry": "Manufacturing",
      "ceo": "Alberto Neri",
      "contact_email": "admin@innovativewindows.com",
      "contact_phone": "+1-555-0100",
      "status": "active",
      "created_at": "2025-07-21T08:00:00Z",
      "updated_at": "2025-12-10T14:22:00Z"
    }
  ],
  "pagination": {
    "cursor": "eyJvZmZzZXQiOjIwfQ==",
    "has_more": false
  }
}
```

---

#### `POST /customers`

Create a new customer.

**Request:**
```json
{
  "name": "BuildTech Industries",
  "industry": "Construction",
  "ceo": "Margaret Thompson",
  "contact_email": "contact@buildtech.com",
  "contact_phone": "+1-555-0200"
}
```

**Response (201 Created):**
```json
{
  "id": "cust_00002",
  "name": "BuildTech Industries",
  "industry": "Construction",
  "ceo": "Margaret Thompson",
  "contact_email": "contact@buildtech.com",
  "contact_phone": "+1-555-0200",
  "status": "active",
  "created_at": "2025-12-15T09:30:00Z",
  "updated_at": "2025-12-15T09:30:00Z"
}
```

---

#### `GET /customers/:id`

Retrieve a specific customer by ID.

**Response (200 OK):**
```json
{
  "id": "cust_00001",
  "name": "Innovative Windows LLC",
  "industry": "Manufacturing",
  "ceo": "Alberto Neri",
  "contact_email": "admin@innovativewindows.com",
  "contact_phone": "+1-555-0100",
  "status": "active",
  "sites_count": 3,
  "created_at": "2025-07-21T08:00:00Z",
  "updated_at": "2025-12-10T14:22:00Z"
}
```

---

#### `PUT /customers/:id`

Update a customer's details.

**Request:**
```json
{
  "contact_email": "newemail@innovativewindows.com",
  "contact_phone": "+1-555-0101"
}
```

**Response (200 OK):** Updated customer object

#### `DELETE /customers/:id`

Delete a customer (soft delete).

**Response (204 No Content)**

---

### Sites

#### `GET /customers/:customer_id/sites`

List all sites for a customer.

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "site_00001",
      "customer_id": "cust_00001",
      "name": "Main Manufacturing Facility",
      "location": "Cleveland, OH",
      "latitude": 41.4993,
      "longitude": -81.6944,
      "building_type": "industrial_warehouse",
      "total_windows": 24,
      "installed_windows": 18,
      "status": "operational",
      "created_at": "2025-08-05T10:00:00Z"
    }
  ],
  "pagination": {
    "cursor": null,
    "has_more": false
  }
}
```

---

#### `POST /customers/:customer_id/sites`

Create a new site for a customer.

**Request:**
```json
{
  "name": "Secondary Facility",
  "location": "Columbus, OH",
  "latitude": 39.9612,
  "longitude": -82.9988,
  "building_type": "office_complex"
}
```

**Response (201 Created):** Site object

---

### Installations

#### `POST /installations`

Create a new installation project.

**Request:**
```json
{
  "site_id": "site_00001",
  "planned_window_count": 24,
  "installation_date": "2025-09-15",
  "technician_id": "tech_john_smith",
  "notes": "Upgrade to fire-resistant smart windows with IoT monitoring"
}
```

**Response (201 Created):**
```json
{
  "id": "inst_00001",
  "project_code": "FG-2025-09-CLV-001",
  "site_id": "site_00001",
  "planned_window_count": 24,
  "installation_date": "2025-09-15",
  "technician_id": "tech_john_smith",
  "status": "scheduled",
  "progress_percentage": 0,
  "created_at": "2025-09-01T11:00:00Z",
  "updated_at": "2025-09-01T11:00:00Z"
}
```

**Notes:** The `project_code` is auto-generated in the format `FG-YYYY-MM-CITY-###`.

---

#### `GET /installations/:id`

Retrieve installation details.

**Response (200 OK):**
```json
{
  "id": "inst_00001",
  "project_code": "FG-2025-09-CLV-001",
  "site_id": "site_00001",
  "planned_window_count": 24,
  "completed_window_count": 18,
  "installation_date": "2025-09-15",
  "completion_date": "2025-10-02",
  "technician_id": "tech_john_smith",
  "status": "in_progress",
  "progress_percentage": 75,
  "notes": "Upgrade to fire-resistant smart windows with IoT monitoring",
  "created_at": "2025-09-01T11:00:00Z",
  "updated_at": "2025-10-02T14:30:00Z"
}
```

---

#### `PUT /installations/:id`

Update installation progress.

**Request:**
```json
{
  "completed_window_count": 20,
  "status": "in_progress"
}
```

**Response (200 OK):** Updated installation object

---

### Windows

#### `POST /windows`

Register a new smart window and assign sensors.

**Request:**
```json
{
  "installation_id": "inst_00001",
  "window_code": "W-CLV-001",
  "location": "Building A, Floor 2, North Wall",
  "orientation": "north",
  "dimensions": {
    "width_mm": 1200,
    "height_mm": 1500
  },
  "sensor_ids": ["sensor_pyr_001", "sensor_pyr_002"]
}
```

**Response (201 Created):**
```json
{
  "id": "window_00001",
  "installation_id": "inst_00001",
  "window_code": "W-CLV-001",
  "location": "Building A, Floor 2, North Wall",
  "orientation": "north",
  "dimensions": {
    "width_mm": 1200,
    "height_mm": 1500
  },
  "sensor_ids": ["sensor_pyr_001", "sensor_pyr_002"],
  "status": "operational",
  "installed_at": "2025-09-15T08:30:00Z",
  "created_at": "2025-09-15T08:30:00Z"
}
```

---

#### `GET /windows/:id`

Retrieve window details including sensor status.

**Response (200 OK):**
```json
{
  "id": "window_00001",
  "installation_id": "inst_00001",
  "window_code": "W-CLV-001",
  "location": "Building A, Floor 2, North Wall",
  "orientation": "north",
  "status": "operational",
  "installed_at": "2025-09-15T08:30:00Z",
  "sensors": [
    {
      "id": "sensor_pyr_001",
      "type": "heat_temperature",
      "status": "active",
      "last_reading_at": "2025-12-15T14:22:15Z"
    },
    {
      "id": "sensor_pyr_002",
      "type": "smoke_density",
      "status": "active",
      "last_reading_at": "2025-12-15T14:22:10Z"
    }
  ]
}
```

---

#### `PUT /windows/:id/status`

Update window lifecycle event.

**Request:**
```json
{
  "event": "maintenance_scheduled",
  "notes": "Annual inspection and calibration"
}
```

**Response (200 OK):**
```json
{
  "id": "window_00001",
  "status": "maintenance_scheduled",
  "last_event": "maintenance_scheduled",
  "last_event_at": "2025-12-15T14:25:00Z",
  "updated_at": "2025-12-15T14:25:00Z"
}
```

---

### Sensors

#### `GET /sensors`

List all sensors with optional filtering.

**Query Parameters:**
- `installation_id` (string, optional)
- `type` (string, optional) — `heat_temperature`, `smoke_density`, `air_quality`
- `status` (string, optional) — `active`, `inactive`, `error`
- `cursor` (string, optional)

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "sensor_pyr_001",
      "serial_number": "PYR-2025-08-0001",
      "type": "heat_temperature",
      "status": "active",
      "window_id": "window_00001",
      "last_calibration_date": "2025-11-20T10:30:00Z",
      "battery_percentage": 87,
      "firmware_version": "2.1.3",
      "last_reading_at": "2025-12-15T14:22:15Z",
      "created_at": "2025-09-15T08:30:00Z"
    },
    {
      "id": "sensor_pyr_002",
      "serial_number": "PYR-2025-08-0002",
      "type": "smoke_density",
      "status": "active",
      "window_id": "window_00001",
      "last_calibration_date": "2025-11-20T09:15:00Z",
      "battery_percentage": 92,
      "firmware_version": "2.1.3",
      "last_reading_at": "2025-12-15T14:22:10Z",
      "created_at": "2025-09-15T08:30:00Z"
    }
  ],
  "pagination": {
    "cursor": null,
    "has_more": false
  }
}
```

---

#### `GET /sensors/:id`

Retrieve a specific sensor's metadata and current status.

**Response (200 OK):**
```json
{
  "id": "sensor_pyr_001",
  "serial_number": "PYR-2025-08-0001",
  "type": "heat_temperature",
  "status": "active",
  "window_id": "window_00001",
  "calibratedAt": "2025-11-20T10:30:00Z",
  "battery_percentage": 87,
  "firmware_version": "2.1.3",
  "rssi": -65,
  "last_reading_at": "2025-12-15T14:22:15Z",
  "created_at": "2025-09-15T08:30:00Z"
}
```

**Note:** There is a schema mismatch — the response uses `calibratedAt` while list endpoint uses `last_calibration_date`. See database schema for the canonical field name.

---

#### `GET /sensors/:id/readings`

Retrieve sensor readings with time-range filtering.

**Query Parameters:**
- `start_time` (ISO 8601, required)
- `end_time` (ISO 8601, required)
- `limit` (integer, optional, default: 100)

**Response (200 OK):**
```json
{
  "sensor_id": "sensor_pyr_001",
  "type": "heat_temperature",
  "unit": "celsius",
  "readings": [
    {
      "timestamp": "2025-12-15T14:00:00Z",
      "value": 22.5,
      "raw_value": 22.5
    },
    {
      "timestamp": "2025-12-15T14:05:00Z",
      "value": 23.1,
      "raw_value": 23.1
    },
    {
      "timestamp": "2025-12-15T14:10:00Z",
      "value": 24.8,
      "raw_value": 24.8
    }
  ],
  "total_readings": 144,
  "start_time": "2025-12-15T00:00:00Z",
  "end_time": "2025-12-15T23:59:59Z"
}
```

---

#### `POST /sensors/batch`

Submit multiple sensor readings in a single request.

**Request:**
```json
{
  "readings": [
    {
      "sensor_id": "sensor_pyr_001",
      "timestamp": "2025-12-15T14:22:15Z",
      "value": 24.8
    },
    {
      "sensor_id": "sensor_pyr_002",
      "timestamp": "2025-12-15T14:22:10Z",
      "value": 0.12
    }
  ]
}
```

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "count": 2,
  "message": "Readings queued for processing"
}
```

// TODO: Document batch sensor reading endpoint — Clara was working on this

#### `DELETE /v1/sensors/bulk`

**Deprecated** — use `/api/sensors/batch` instead.

---

### Inspections

#### `GET /inspections`

List inspections with filtering.

**Query Parameters:**
- `installation_id` (string, optional)
- `status` (string, optional) — `pending`, `in_progress`, `completed`
- `cursor` (string, optional)

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "insp_00001",
      "installation_id": "inst_00001",
      "inspector_id": "user_tech_001",
      "inspection_date": "2025-10-01T09:00:00Z",
      "status": "completed",
      "findings_count": 2,
      "signature_status": "signed",
      "created_at": "2025-10-01T09:00:00Z"
    }
  ],
  "pagination": {
    "cursor": null,
    "has_more": false
  }
}
```

---

#### `POST /inspections`

Create a new inspection record.

**Request:**
```json
{
  "installation_id": "inst_00001",
  "inspector_id": "user_tech_001",
  "inspection_date": "2025-10-01T09:00:00Z",
  "notes": "Post-installation compliance check"
}
```

**Response (201 Created):**
```json
{
  "id": "insp_00001",
  "installation_id": "inst_00001",
  "inspector_id": "user_tech_001",
  "inspection_date": "2025-10-01T09:00:00Z",
  "status": "in_progress",
  "signature_status": "pending",
  "created_at": "2025-10-01T09:00:00Z"
}
```

---

#### `POST /inspections/:id/sign`

Sign an inspection with digital signature.

**Request:**
```json
{
  "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "signed_by": "John Smith",
  "timestamp": "2025-10-01T10:30:00Z"
}
```

**Response (200 OK):**
```json
{
  "id": "insp_00001",
  "signature_status": "signed",
  "signed_at": "2025-10-01T10:30:00Z",
  "signed_by": "John Smith"
}
```

---

### Maintenance

#### `POST /maintenance/schedule`

Schedule maintenance for a window or sensor.

**Request:**
```json
{
  "window_id": "window_00001",
  "maintenance_type": "calibration",
  "scheduled_date": "2025-12-20T09:00:00Z",
  "technician_id": "tech_john_smith",
  "notes": "Quarterly calibration check"
}
```

**Response (201 Created):**
```json
{
  "id": "maint_00001",
  "window_id": "window_00001",
  "maintenance_type": "calibration",
  "scheduled_date": "2025-12-20T09:00:00Z",
  "technician_id": "tech_john_smith",
  "status": "scheduled",
  "created_at": "2025-12-15T14:30:00Z"
}
```

---

#### `POST /maintenance/:id/complete`

Mark maintenance as completed and generate report.

**Request:**
```json
{
  "completion_date": "2025-12-20T11:00:00Z",
  "findings": [
    {
      "sensor_id": "sensor_pyr_001",
      "status": "operational",
      "notes": "Battery at 87%, no issues"
    }
  ],
  "next_maintenance_date": "2026-03-20"
}
```

**Response (200 OK):**
```json
{
  "id": "maint_00001",
  "status": "completed",
  "completion_date": "2025-12-20T11:00:00Z",
  "report_url": "/reports/maintenance/maint_00001.pdf"
}
```

---

### Reports

#### `GET /reports/compliance`

Generate compliance report for an installation.

**Query Parameters:**
- `installation_id` (string, required)
- `format` (string, optional) — `pdf`, `json` (default: `pdf`)

**Response (200 OK):**
Returns PDF file with compliance documentation.

**Response Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="FG-2025-09-CLV-001-Compliance.pdf"
```

---

### Notifications

#### `GET /notifications`

Retrieve user notifications.

**Query Parameters:**
- `status` (string, optional) — `unread`, `read`, `all`
- `limit` (integer, optional, default: 50)

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "notif_00001",
      "type": "sensor_alert",
      "title": "High Temperature Alert",
      "message": "Sensor pyr_001 exceeded threshold: 65°C",
      "status": "unread",
      "created_at": "2025-12-15T14:15:00Z"
    }
  ]
}
```

---

#### `PUT /notifications/:id`

Mark notification as read.

**Request:**
```json
{
  "status": "read"
}
```

**Response (200 OK):** Updated notification object

---

## Request/Response Examples

### Complete Sensor Reading Workflow

**Step 1: Get sensor data**
```bash
curl -X GET "https://api.fireglass.atlas-forge.io/api/sensors/sensor_pyr_001/readings?start_time=2025-12-15T00:00:00Z&end_time=2025-12-15T23:59:59Z" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json"
```

**Step 2: Submit new readings**
```bash
curl -X POST "https://api.fireglass.atlas-forge.io/api/sensors/batch" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "readings": [
      {
        "sensor_id": "sensor_pyr_001",
        "timestamp": "2025-12-15T15:00:00Z",
        "value": 25.3
      }
    ]
  }'
```

---

## Error Handling

All errors follow a standard response format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "email",
        "issue": "Invalid email format"
      }
    ],
    "request_id": "req_abc123def456"
  }
}
```

### Common HTTP Status Codes

| Status | Description |
|--------|-------------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async operation) |
| 204 | No Content |
| 400 | Bad Request — validation failed |
| 401 | Unauthorized — invalid/expired token |
| 403 | Forbidden — insufficient permissions |
| 404 | Not Found |
| 409 | Conflict — duplicate resource |
| 429 | Too Many Requests — rate limited |
| 500 | Internal Server Error |

### Error Codes

- `VALIDATION_ERROR` — Input validation failed
- `AUTHENTICATION_FAILED` — Login credentials invalid
- `TOKEN_EXPIRED` — JWT token has expired
- `INSUFFICIENT_PERMISSIONS` — User lacks required role/permission
- `RESOURCE_NOT_FOUND` — Requested resource does not exist
- `DUPLICATE_RESOURCE` — Resource already exists
- `RATE_LIMIT_EXCEEDED` — Too many requests
- `INTERNAL_ERROR` — Server error

---

## Rate Limiting

Rate limits will be configured post-launch based on load testing results. Current implementation includes:

- Per-user rate limiting on authentication endpoints
- Per-IP rate limiting on public endpoints
- Burst allowances for real-time sensor data submission

Rate limit headers in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1671091200
```

When rate limited, the API returns `429 Too Many Requests` with retry-after information.

---

## Pagination

All list endpoints support cursor-based pagination for efficient data retrieval.

**Request:**
```
GET /customers?cursor=eyJvZmZzZXQiOjIwfQ==&limit=20
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "cursor": "eyJvZmZzZXQiOjQwfQ==",
    "has_more": true
  }
}
```

To get the next page, use the returned `cursor` value in the subsequent request. When `has_more` is `false`, you've reached the end of results.

---

## WebSocket Events

Real-time sensor data is streamed via WebSocket. Connect to:

```
wss://api.fireglass.atlas-forge.io/ws
```

### Connection Handshake

After establishing the WebSocket connection, authenticate with:

```json
{
  "type": "auth",
  "token": "<JWT_TOKEN>"
}
```

### Subscribe to Sensor Data

```json
{
  "type": "subscribe",
  "channel": "sensors",
  "filters": {
    "window_id": "window_00001",
    "sensor_types": ["heat_temperature", "smoke_density"]
  }
}
```

### Incoming Events

Real-time sensor readings:
```json
{
  "type": "sensor_reading",
  "sensor_id": "sensor_pyr_001",
  "timestamp": "2025-12-15T14:22:15Z",
  "value": 24.8,
  "unit": "celsius"
}
```

MQTT topic subscription (HelionLink protocol via Helion devices):
```
fireglass/sensors/{sensor_id}/temperature
fireglass/sensors/{sensor_id}/smoke_density
fireglass/sensors/{sensor_id}/air_quality
```

Example MQTT payload:
```json
{
  "sensor_id": "sensor_pyr_001",
  "value": 24.8,
  "unit": "celsius",
  "timestamp": 1702656135
}
```

---

## Postman Collection

See the FireGlass Postman collection (shared in #dev-tools Slack channel) for pre-configured request templates and environment variables.

The collection includes:
- All endpoint examples
- Pre-filled authentication headers
- Test scripts for validation
- Environment variables for dev/staging/production

---

## Support & Contact

For API support and questions:

- **Tech Lead:** Samir Osei (samir.osei@atlasforge.io)
- **Junior Developer:** Clara Duval (clara.duval@atlasforge.io)
- **Slack Channel:** #fireglass-dev

Last updated: **2025-12-15**
API Version: **1.0.0**
