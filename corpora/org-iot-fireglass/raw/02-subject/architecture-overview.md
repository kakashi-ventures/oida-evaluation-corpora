# FireGlass Architecture Overview

**Author:** Samir Osei (Tech Lead)  
**Last Updated:** March 2026  
**Status:** Active Development

## Introduction

FireGlass is a comprehensive CRM and IoT platform designed for Innovative Windows LLC, enabling real-time monitoring and management of smart fire-resistant window systems. This document provides a technical overview of the system architecture, component interactions, and data flow patterns.

The platform integrates three core domains:
- **CRM Layer:** Customer and order management via React-based dashboard
- **IoT Layer:** Real-time sensor data collection from Helion devices via HelionLink
- **Integration Layer:** Cloud-based data persistence and real-time synchronization

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FIREGLASS PLATFORM                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  CLIENT LAYER                                                │   │
│  │  ┌──────────────────────┐  ┌──────────────────────────────┐ │   │
│  │  │  React Dashboard     │  │  Mobile/Desktop Clients      │ │   │
│  │  │  (TypeScript)        │  │  WebSocket connections       │ │   │
│  │  └──────────────────────┘  └──────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                             ▲                                         │
│                             │ HTTPS/WSS                               │
│                             ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  API LAYER (Next.js 14 + TypeScript)                        │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐   │   │
│  │  │ Auth Routes    │  │ CRM Routes     │  │ IoT Routes   │   │   │
│  │  │ (JWT/OAuth)    │  │ (/api/...)     │  │ (/api/iot)   │   │   │
│  │  └────────────────┘  └────────────────┘  └──────────────┘   │   │
│  │                                                               │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │  Message Handler (IoT Data Processing)              │   │   │
│  │  │  - Parses MQTT payloads                             │   │   │
│  │  │  - Validates sensor readings                        │   │   │
│  │  │  - Triggers alerts & notifications                 │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                             ▲                                         │
│                             │                                         │
│                      ┌──────┴──────┐                                  │
│                      │             │                                  │
│                      ▼             ▼                                  │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐     │
│  │  DATA PERSISTENCE LAYER  │  │  IOT BROKER LAYER            │     │
│  │                          │  │                              │     │
│  │  ┌────────────────────┐  │  │  ┌────────────────────────┐  │     │
│  │  │   PostgreSQL       │  │  │  │  MQTT Broker           │  │     │
│  │  │   (Prisma ORM)     │  │  │  │  (Message Queue)       │  │     │
│  │  │                    │  │  │  │                        │  │     │
│  │  │  Tables:           │  │  │  │  Pending: Self-managed │  │     │
│  │  │  - users           │  │  │  │  Mosquitto vs Cloud    │  │     │
│  │  │  - customers       │  │  │  │  Broker decision       │  │     │
│  │  │  - orders          │  │  │  │                        │  │     │
│  │  │  - sensor_data     │  │  │  │  Topic routing:        │  │     │
│  │  │  - alerts          │  │  │  │  See mqtt-protocol.md  │  │     │
│  │  └────────────────────┘  │  │  │                        │  │     │
│  └──────────────────────────┘  │  │  HelionLink v2.3:      │  │     │
│                                 │  │  Proprietary MQTT v5   │  │     │
│                                 │  │  bridge for device     │  │     │
│                                 │  │  communication         │  │     │
│                                 │  │                        │  │     │
│                                 │  └────────────────────────┘  │     │
│                                 │                              │     │
│                                 │  ┌────────────────────────┐  │     │
│                                 │  │  Supabase Realtime     │  │     │
│                                 │  │  (WebSocket Sync)      │  │     │
│                                 │  └────────────────────────┘  │     │
│                                 └──────────────────────────────┘     │
│                                 ▲                                    │
│                                 │                                    │
│                                 ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  EDGE/DEVICE LAYER                                          │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │  Helion Sensors (HelionLink)                        │   │   │
│  │  │  - Sensors: Helion TG-400 (thermal monitoring),     │   │   │
│  │  │    SM-220 (smoke particle density),                 │   │   │
│  │  │    AQ-100 (air quality — CO, CO₂, VOC)             │   │   │
│  │  │  - Fire detection status                             │   │   │
│  │  │  - Device health metrics                             │   │   │
│  │  │  - Local edge processing                             │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### 1. Data Flow: Sensor Readings to Dashboard

The journey of a sensor reading through the FireGlass platform follows this sequence:

```
Helion Sensor (HelionLink)
         │
         │ MQTT Protocol
         │ (JSON payload)
         ▼
┌─────────────────────┐
│  MQTT Broker        │
│  (Topic routing)    │
└─────────────────────┘
         │
         │ Connection from API
         │ Message subscription
         ▼
┌─────────────────────────────────────┐
│  Message Handler (Node.js)          │
│  - Deserialize payload              │
│  - Validate data schema             │
│  - Check timestamp & device ID      │
│  - Execute business logic           │
└─────────────────────────────────────┘
         │
         │ Prisma query
         ▼
┌─────────────────────────────────────┐
│  PostgreSQL                         │
│  INSERT INTO sensor_data            │
│  (timestamp, device_id, temp, ...)  │
└─────────────────────────────────────┘
         │
         │ Database trigger/subscription
         ▼
┌─────────────────────────────────────┐
│  Supabase Realtime                  │
│  - Broadcasts change to subscribers │
│  - WebSocket event to dashboard     │
└─────────────────────────────────────┘
         │
         │ WSS connection
         ▼
┌─────────────────────────────────────┐
│  React Dashboard                    │
│  - Updates UI in real-time          │
│  - Charts & gauges refresh          │
│  - Alerts triggered if needed       │
└─────────────────────────────────────┘
```

**Latency Profile:**
- Sensor → Broker: ~100ms (MQTT publish)
- Broker → API: ~50ms (message delivery)
- API → Database: ~30ms (Prisma write)
- Database → Realtime: ~20ms (trigger)
- Realtime → Client: ~100-200ms (WebSocket)
- **Total end-to-end: ~300-500ms** (acceptable for fire-resistant window monitoring)

### 2. Authentication Flow

```
User Login Request
       │
       ▼
┌──────────────────────────────┐
│  Next.js Auth API (/auth)    │
│  - Receive credentials       │
│  - Hash password             │
│  - Query PostgreSQL users    │
└──────────────────────────────┘
       │
       ├─────────────────────────┐
       │                         │
    Success              Failure │
       │                         ▼
       │              Return 401 Unauthorized
       ▼
┌──────────────────────────────┐
│  Generate JWT Token          │
│  - User ID in payload        │
│  - Exp: 24 hours             │
│  - HttpOnly cookie           │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Return to Client            │
│  - Set secure cookie         │
│  - Redirect to dashboard     │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Protected Routes            │
│  - Middleware validates JWT  │
│  - Extracts user context     │
│  - Enforces role-based ACL   │
└──────────────────────────────┘
```

### 3. File Storage Flow

FireGlass stores files (sensor logs, reports, PDFs) via Supabase Storage:

```
File Upload (Dashboard)
       │
       ▼
┌────────────────────────────────┐
│  Browser FormData               │
│  - File blob                    │
│  - Metadata (name, type)        │
└────────────────────────────────┘
       │
       │ HTTPS POST
       ▼
┌────────────────────────────────┐
│  Next.js Upload Route           │
│  (/api/files/upload)            │
│  - Validate JWT                 │
│  - Check file size (< 50MB)     │
│  - Scan MIME type               │
└────────────────────────────────┘
       │
       │ Supabase SDK
       ▼
┌────────────────────────────────┐
│  Supabase Storage Bucket        │
│  Path: /customers/{id}/docs/    │
│  - Encrypted at rest            │
│  - Signed URLs for access       │
└────────────────────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  PostgreSQL Metadata            │
│  INSERT INTO file_records       │
│  - bucket_path                  │
│  - owner_id                     │
│  - created_at                   │
│  - access_log                   │
└────────────────────────────────┘
```

## Deployment Architecture

FireGlass is deployed across two managed cloud platforms:

### Frontend & API Deployment (Vercel)
- **Runtime:** Node.js 20.x
- **Framework:** Next.js 14 with App Router
- **Build output:** Optimized bundles + serverless functions
- **Environment:** 
  - Production: `firegl.innovative-windows.app`
  - Staging: `firegl-staging.innovative-windows.app`
- **Auto-scaling:** Vercel's auto-scale (handles traffic spikes)
- **Regions:** US (Primary), EU (Redundant)

### Database & Backend Deployment (Supabase Cloud)
- **Database:** PostgreSQL 15 (managed)
- **Region:** us-east-1 (AWS)
- **Backup:** Automated daily, 7-day retention
- **Realtime:** Built-in (WebSocket server pool)
- **Storage:** S3-backed with CDN
- **Vector DB:** pgvector extension (future use for anomaly detection)

### MQTT Broker Hosting (Pending Decision)

**Current Status:** We're evaluating two approaches for the MQTT broker that handles Helion HelionLink sensor traffic:

1. **Self-Managed Mosquitto**
   - Pros: Full control, no vendor lock-in, lower cost at scale
   - Cons: Operational overhead, manual scaling, requires DevOps
   - Deployment: Docker on AWS EC2 or Lightsail

2. **Cloud Broker (e.g., AWS IoT Core, Supabase MQTT plugin)**
   - Pros: Managed scaling, built-in security, less ops burden
   - Cons: Higher costs, vendor lock-in, additional integrations
   - Deployment: Native cloud service

**Decision Timeline:** End of Q2 2026. Will depend on sensor volume projections and team bandwidth.

**Note:** See `mqtt-protocol.md` for detailed topic structure, message schemas, and QoS requirements.

## Key Technologies & Rationale

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + TypeScript | Type-safe UI, component reusability |
| **Runtime** | Next.js 14 | SSR for SEO, API routes, edge functions |
| **Database** | PostgreSQL 15 | ACID compliance, relational integrity, JSON support |
| **ORM** | Prisma 5 | Type-safe DB access, migrations, schema versioning |
| **IoT Messaging** | MQTT 3.1.1 | Lightweight, low-latency, pub/sub pattern |
| **Real-time Sync** | Supabase Realtime | WebSocket-based change broadcasting |
| **Authentication** | JWT + HTTP-only cookies | Stateless sessions, CSRF protection |
| **File Storage** | Supabase Storage | S3 compatibility, CDN, signed URLs |

## Compliance & Standards

**EPFC-2201 Compliance:** The FireGlass architecture must support EPFC-2201 (European standard for connected fire protection systems) alert latency requirements. Specifically, the end-to-end latency from sensor trigger to dashboard notification must be <10 seconds. This covers:
- Alert latency: <10s from trigger to notification
- Fail-safe mechanisms: Device defaults to safe state on loss of connectivity
- Cybersecurity: TLS 1.3 encryption standard (via HelionLink v2.3), mutual authentication, and audit logging

Current latency profile (see Section 2, Data Flow) totals ~300-500ms end-to-end, comfortably within the EPFC-2201 requirement.

**EU-SmartSafe Mark:** All field-deployed IoT sensors (Helion TG-400, SM-220, AQ-100) require EU-SmartSafe Mark compliance certification per EPFC-2201 §4.3.

## Cross-References

- **MQTT Protocol Details:** See `mqtt-protocol.md` for topic structure, payload schemas, QoS levels, and device ID conventions.
- **API Documentation:** See `api-routes.md` for endpoint specifications.
- **Database Schema:** See `database-schema.md` for table definitions and relationships.
- **Deployment Guide:** See `deployment.md` for CI/CD pipelines and scaling strategies.

## Notes for Future Work

1. **Latency Optimization:** Consider edge caching for dashboard queries using Vercel's Edge Functions.
2. **Scalability:** Current setup supports ~100K simultaneous connections; monitor and plan for growth.
3. **Security Audit:** Schedule quarterly penetration testing for API and IoT endpoints.
4. **Disaster Recovery:** Document RTO/RPO targets and test failover procedures quarterly.

---

**Built by:** Atlas Forge LLC  
**For:** Innovative Windows LLC  
**License:** CC BY 4.0