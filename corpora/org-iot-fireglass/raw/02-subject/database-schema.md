# FireGlass Database Schema
## Innovative Windows LLC - CRM/IoT Platform

**Author:** Clara Duval  
**Platform:** Next.js 14, TypeScript, Prisma, PostgreSQL  
**License:** CC BY 4.0  
**Last Updated:** 2026-03-24

---

## Overview

This document defines the relational schema for the FireGlass platform, a comprehensive CRM and IoT management system for smart fire-resistant window installations. The schema encompasses customer relationship management, IoT sensor data collection, maintenance workflows, and audit trails.

---

## Prisma Models

### Organization

```prisma
model Organization {
  id                  String     @id @default(cuid())
  name                String     @unique
  slug                String     @unique
  description         String?
  website             String?
  industry            String?
  country             String?
  timezone            String     @default("UTC")
  status              String     @default("active") // active, suspended, archived
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  users               User[]
  customers           Customer[]
  sites               Site[]
  roles               Role[]
  apiKeys             ApiKey[]
  sessions            Session[]
  invitations         Invitation[]
  auditLogs           AuditLog[]
  notifications       Notification[]

  @@index([slug])
  @@index([status])
}
```

### User

```prisma
model User {
  id                  String     @id @default(cuid())
  organizationId      String
  email               String
  firstName           String
  lastName            String
  avatar              String?
  passwordHash        String
  isEmailVerified     Boolean    @default(false)
  emailVerifiedAt     DateTime?
  lastLoginAt         DateTime?
  status              String     @default("active") // active, inactive, suspended
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  organization        Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  userRoles           UserRole[]
  apiKeys             ApiKey[]
  sessions            Session[]
  inspectionSignatures InspectionSignature[]
  auditLogs           AuditLog[]
  notificationPreferences NotificationPreference[]

  @@unique([organizationId, email])
  @@index([organizationId])
  @@index([status])
}
```

### Role

```prisma
model Role {
  id                  String     @id @default(cuid())
  organizationId      String
  name                String
  description         String?
  isBuiltIn           Boolean    @default(false)
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  organization        Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  userRoles           UserRole[]
  permissions         Permission[]

  @@unique([organizationId, name])
  @@index([organizationId])
}
```

### UserRole

```prisma
model UserRole {
  id                  String     @id @default(cuid())
  userId              String
  roleId              String
  assignedAt          DateTime   @default(now())
  assignedBy          String?
  
  user                User       @relation(fields: [userId], references: [id], onDelete: Cascade)
  role                Role       @relation(fields: [roleId], references: [id], onDelete: Cascade)

  @@unique([userId, roleId])
  @@index([userId])
  @@index([roleId])
}
```

### Permission

```prisma
model Permission {
  id                  String     @id @default(cuid())
  roleId              String
  resource            String     // e.g., "customers", "installations", "sensors"
  action              String     // e.g., "read", "create", "update", "delete"
  createdAt           DateTime   @default(now())
  
  role                Role       @relation(fields: [roleId], references: [id], onDelete: Cascade)

  @@unique([roleId, resource, action])
  @@index([roleId])
}
```

### Customer

```prisma
model Customer {
  id                  String     @id @default(cuid())
  organizationId      String
  name                String
  email               String?
  phone               String?
  address             String?
  city                String?
  state               String?
  postalCode          String?
  country             String?
  companyName         String?
  industry            String?
  status              String     @default("active") // active, inactive, archived
  notes               String?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  organization        Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  sites               Site[]
  auditLogs           AuditLog[]

  @@index([organizationId])
  @@index([email])
  @@index([status])
  @@index([createdAt])
}
```

### Site

```prisma
model Site {
  id                  String     @id @default(cuid())
  organizationId      String
  customerId          String
  name                String
  address             String
  city                String
  state               String
  postalCode          String
  country             String
  latitude            Float?
  longitude           Float?
  siteType            String     // residential, commercial, industrial, institutional
  squareFootage       Float?
  status              String     @default("active") // active, inactive, archived
  contractStartDate   DateTime?
  contractEndDate     DateTime?
  notes               String?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  organization        Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  customer            Customer   @relation(fields: [customerId], references: [id], onDelete: Cascade)
  installations      Installation[]
  inspections        Inspection[]
  maintenanceSchedules MaintenanceSchedule[]
  geoLocation        GeoLocation?
  qrCodes            QRCode[]
  auditLogs          AuditLog[]

  @@index([organizationId])
  @@index([customerId])
  @@index([status])
  @@index([createdAt])
}
```

### Installation

```prisma
model Installation {
  id                  String     @id @default(cuid())
  siteId              String
  installationDate    DateTime
  completionDate      DateTime?
  status              String     @default("planned") // planned, in_progress, completed, discontinued
  notes               String?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  site                Site       @relation(fields: [siteId], references: [id], onDelete: Cascade)
  windows             Window[]
  sensors             Sensor[]
  inspections         Inspection[]
  maintenanceReports  MaintenanceReport[]
  auditLogs           AuditLog[]

  @@index([siteId])
  @@index([status])
  @@index([installationDate])
}
```

### Window

```prisma
model Window {
  id                  String     @id @default(cuid())
  installationId      String
  windowModelId       String
  serialNumber        String     @unique
  location            String     // e.g., "Conference Room A", "North Wall"
  width              Float?     // in inches
  height             Float?     // in inches
  orientation         String?    // N, NE, E, SE, S, SW, W, NW
  installationDate    DateTime?
  fireRating          String?    // e.g., "60 min", "120 min"
  status              String     @default("operational") // operational, maintenance, decommissioned
  lastInspectionDate  DateTime?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  installation        Installation @relation(fields: [installationId], references: [id], onDelete: Cascade)
  windowModel         WindowModel @relation(fields: [windowModelId], references: [id])
  sensors             Sensor[]
  lifecycleEvents     WindowLifecycleEvent[]
  auditLogs           AuditLog[]

  @@index([installationId])
  @@index([windowModelId])
  @@index([serialNumber])
  @@index([status])
}
```

### WindowModel

```prisma
model WindowModel {
  id                  String     @id @default(cuid())
  modelName           String     @unique
  manufacturer        String
  glassType           String?
  frameType           String?
  thermalRating       Float?     // U-value
  soundRating         Float?     // STC rating
  fireRating          String?
  productionYear      Int?
  status              String     @default("active") // active, discontinued
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  windows             Window[]

  @@index([manufacturer])
  @@index([status])
}
```

### WindowLifecycleEvent

```prisma
model WindowLifecycleEvent {
  id                  String     @id @default(cuid())
  windowId            String
  eventType           String     // manufactured, shipped, installed, inspected, repaired, decommissioned
  eventDate           DateTime
  description         String?
  createdAt           DateTime   @default(now())
  
  window              Window     @relation(fields: [windowId], references: [id], onDelete: Cascade)

  @@index([windowId])
  @@index([eventType])
  @@index([eventDate])
}
```

### Sensor

```prisma
model Sensor {
  id                  String     @id @default(cuid())
  installationId      String
  windowId            String?
  sensorType          String     // temperature, humidity, smoke, heat, pressure
  serialNumber        String     @unique
  modelName           String?
  // NOTE: Helion firmware version field is unreliable until HelionLink v2.3 docs arrive — returns '2.3.0' by default on all units regardless of actual version
  firmwareVersion     String?
  // sensor_model String? // TG-400 | SM-220 | AQ-100 — populated from HelionLink device registration payload
  batteryLevel        Int?       // 0-100
  lastHeartbeat       DateTime?
  status              String     @default("active") // active, inactive, error, decommissioned
  locationDescription String?
  calibrationDate     DateTime?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  installation        Installation @relation(fields: [installationId], references: [id], onDelete: Cascade)
  window              Window?    @relation(fields: [windowId], references: [id], onDelete: SetNull)
  readings            SensorReading[]
  alerts              SensorAlert[]
  auditLogs           AuditLog[]

  @@index([installationId])
  @@index([windowId])
  @@index([serialNumber])
  @@index([status])
}
```

### SensorReading

```prisma
model SensorReading {
  id                  String     @id @default(cuid())
  sensorId            String
  readingValue        Float
  readingUnit         String     // C, F, %, PPM, Pa, etc.
  readingTimestamp    DateTime
  // HelionLink v2.3 payload — see mqtt-protocol.md for schema
  // TODO: evaluate TimescaleDB extension for time-series performance — Clara
  createdAt           DateTime   @default(now())

  sensor              Sensor     @relation(fields: [sensorId], references: [id], onDelete: Cascade)

  @@index([sensorId])
  @@index([readingTimestamp])
  @@index([createdAt])
}
```

### SensorAlert

```prisma
model SensorAlert {
  id                  String     @id @default(cuid())
  sensorId            String
  alertType           String     // threshold_exceeded, sensor_offline, low_battery
  severity            String     // critical, high, medium, low
  message             String
  readingValue        Float?
  thresholdValue      Float?
  isResolved          Boolean    @default(false)
  resolvedAt          DateTime?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  sensor              Sensor     @relation(fields: [sensorId], references: [id], onDelete: Cascade)

  @@index([sensorId])
  @@index([severity])
  @@index([isResolved])
  @@index([createdAt])
}
```

### Inspection

```prisma
model Inspection {
  id                  String     @id @default(cuid())
  siteId              String
  installationId      String
  inspectionDate      DateTime
  inspectorName       String
  inspectionType      String     // routine, compliance, incident
  status              String     @default("pending") // pending, in_progress, completed
  notes               String?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  site                Site       @relation(fields: [siteId], references: [id], onDelete: Cascade)
  installation        Installation @relation(fields: [installationId], references: [id], onDelete: Cascade)
  checklists          InspectionChecklist[]
  signatures          InspectionSignature[]
  auditLogs           AuditLog[]

  @@index([siteId])
  @@index([installationId])
  @@index([inspectionType])
  @@index([status])
  @@index([inspectionDate])
}
```

### InspectionChecklist

```prisma
model InspectionChecklist {
  id                  String     @id @default(cuid())
  inspectionId        String
  title               String
  description         String?
  status              String     @default("pending") // pending, in_progress, completed
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  inspection          Inspection @relation(fields: [inspectionId], references: [id], onDelete: Cascade)
  items               InspectionChecklistItem[]

  @@index([inspectionId])
}
```

### InspectionChecklistItem

```prisma
model InspectionChecklistItem {
  id                  String     @id @default(cuid())
  checklistId         String
  itemName            String
  itemDescription     String?
  isCompleted         Boolean    @default(false)
  notes               String?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  checklist           InspectionChecklist @relation(fields: [checklistId], references: [id], onDelete: Cascade)

  @@index([checklistId])
}
```

### InspectionSignature

```prisma
model InspectionSignature {
  id                  String     @id @default(cuid())
  inspectionId        String
  userId              String
  signatureData       String     // base64-encoded signature image
  signedAt            DateTime
  createdAt           DateTime   @default(now())
  
  inspection          Inspection @relation(fields: [inspectionId], references: [id], onDelete: Cascade)
  user                User       @relation(fields: [userId], references: [id], onDelete: Restrict)

  @@unique([inspectionId, userId])
  @@index([inspectionId])
  @@index([userId])
}
```

### MaintenanceSchedule

```prisma
model MaintenanceSchedule {
  id                  String     @id @default(cuid())
  siteId              String
  scheduleType        String     // preventive, corrective, predictive
  frequency           String?    // daily, weekly, monthly, quarterly, annually
  nextMaintenanceDate DateTime
  lastMaintenanceDate DateTime?
  status              String     @default("scheduled") // scheduled, completed, cancelled
  notes               String?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  site                Site       @relation(fields: [siteId], references: [id], onDelete: Cascade)
  reports             MaintenanceReport[]

  @@index([siteId])
  @@index([nextMaintenanceDate])
  @@index([status])
}
```

### MaintenanceReport

```prisma
model MaintenanceReport {
  id                  String     @id @default(cuid())
  installationId      String
  scheduleId          String
  maintenanceDate     DateTime
  technician          String
  workDescription     String
  partsReplaced       String?
  estimatedCost       Float?
  status              String     @default("pending") // pending, approved, completed
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  installation        Installation @relation(fields: [installationId], references: [id], onDelete: Cascade)
  schedule            MaintenanceSchedule @relation(fields: [scheduleId], references: [id], onDelete: Cascade)
  pdfs                MaintenanceReportPDF[]
  auditLogs           AuditLog[]

  @@index([installationId])
  @@index([scheduleId])
  @@index([status])
  @@index([maintenanceDate])
}
```

### MaintenanceReportPDF

```prisma
model MaintenanceReportPDF {
  id                  String     @id @default(cuid())
  reportId            String
  fileName            String
  fileSize            Int
  mimeType            String
  storageKey          String     // S3 or cloud storage reference
  uploadedAt          DateTime   @default(now())
  
  report              MaintenanceReport @relation(fields: [reportId], references: [id], onDelete: Cascade)

  @@index([reportId])
}
```

### Notification

```prisma
model Notification {
  id                  String     @id @default(cuid())
  organizationId      String
  recipientId         String?
  notificationType    String     // alert, reminder, update, warning
  subject             String
  message             String
  isRead              Boolean    @default(false)
  readAt              DateTime?
  createdAt           DateTime   @default(now())
  
  organization        Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)

  @@index([organizationId])
  @@index([recipientId])
  @@index([isRead])
  @@index([createdAt])
}
```

### NotificationPreference

```prisma
model NotificationPreference {
  id                  String     @id @default(cuid())
  userId              String     @unique
  emailAlerts         Boolean    @default(true)
  smsAlerts           Boolean    @default(false)
  pushNotifications   Boolean    @default(true)
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  user                User       @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
}
```

### AuditLog

```prisma
model AuditLog {
  id                  String     @id @default(cuid())
  organizationId      String
  userId              String?
  entityType          String     // User, Customer, Site, Installation, Window, Sensor, etc.
  entityId            String
  action              String     // created, updated, deleted, viewed
  changes             String?    // JSON-serialized field changes
  ipAddress           String?
  userAgent           String?
  timestamp           DateTime   @default(now())
  
  organization        Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)

  @@index([organizationId])
  @@index([userId])
  @@index([entityType])
  @@index([entityId])
  @@index([action])
  @@index([timestamp])
}
```

### ApiKey

```prisma
model ApiKey {
  id                  String     @id @default(cuid())
  organizationId      String
  userId              String
  keyHash             String     @unique
  name                String
  scope               String     // comma-separated: read_sensors, write_maintenance, etc.
  isActive            Boolean    @default(true)
  lastUsedAt          DateTime?
  expiresAt           DateTime?
  createdAt           DateTime   @default(now())
  
  organization        Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  user                User       @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([organizationId])
  @@index([userId])
  @@index([isActive])
}
```

### Session

```prisma
model Session {
  id                  String     @id @default(cuid())
  organizationId      String
  userId              String
  sessionToken        String     @unique
  ipAddress           String?
  userAgent           String?
  expiresAt           DateTime
  createdAt           DateTime   @default(now())
  
  organization        Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)
  user                User       @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([organizationId])
  @@index([userId])
  @@index([expiresAt])
}
```

### Invitation

```prisma
model Invitation {
  id                  String     @id @default(cuid())
  organizationId      String
  email               String
  invitationToken     String     @unique
  expiresAt           DateTime
  invitedBy           String?
  status              String     @default("pending") // pending, accepted, declined
  acceptedAt          DateTime?
  createdAt           DateTime   @default(now())
  
  organization        Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)

  @@unique([organizationId, email])
  @@index([organizationId])
  @@index([email])
  @@index([status])
}
```

### QRCode

```prisma
model QRCode {
  id                  String     @id @default(cuid())
  siteId              String
  code                String     @unique
  linkedResource      String?    // e.g., "window:abc123", "sensor:def456"
  isActive            Boolean    @default(true)
  scanCount           Int        @default(0)
  lastScannedAt       DateTime?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  site                Site       @relation(fields: [siteId], references: [id], onDelete: Cascade)

  @@index([siteId])
  @@index([code])
  @@index([isActive])
}
```

### ProjectCode

```prisma
model ProjectCode {
  id                  String     @id @default(cuid())
  organizationId      String
  code                String     @unique
  projectName         String
  description         String?
  status              String     @default("active") // active, completed, archived
  startDate           DateTime?
  endDate             DateTime?
  createdAt           DateTime   @default(now())
  updatedAt           DateTime   @updatedAt
  
  organization        Organization @relation(fields: [organizationId], references: [id])

  @@index([organizationId])
  @@index([code])
  @@index([status])
}
```

### GeoLocation

```prisma
model GeoLocation {
  id                  String     @id @default(cuid())
  siteId              String     @unique
  latitude            Float
  longitude           Float
  accuracy            Float?     // meters
  altitude            Float?     // meters
  lastUpdated         DateTime   @updatedAt
  
  site                Site       @relation(fields: [siteId], references: [id], onDelete: Cascade)

  @@index([latitude, longitude])
}
```

---

## Security Considerations

### Row-Level Security (RLS)

The following tables should enforce RLS policies at the database level:

- **User**: Users can only view/edit their own profile and organization members
- **AuditLog**: Only organization admins can access audit logs (RLS policy required)
- **ApiKey**: Users can only access their own keys; admins can view all (RLS policy required)
- **Session**: Users can only view their own active sessions (RLS policy required)
- **SensorReading**: Access controlled via Site and Installation hierarchy (RLS policy required)
- **SensorAlert**: Access controlled via Site and Installation hierarchy (RLS policy required)
- **MaintenanceReport**: Access controlled via Installation and Site (RLS policy required)

---

## Indexing Strategy

All primary access patterns include appropriate indexes:
- Organization-based filtering
- User lookups by email
- Status-based filtering
- Temporal filtering (createdAt, eventDate, readingTimestamp)
- Relationship navigation (foreign keys)

---

## Performance Notes

- SensorReading table accumulates high-volume time-series data; consider TimescaleDB extension for optimized compression and querying
- Aggregate queries on SensorReading should use materialized views or data warehouse for historical analysis
- Maintain separate reporting indexes for AuditLog queries beyond 90 days

---

## Compliance & Privacy

- All personally identifiable information (PII) in User and Customer tables should be encrypted at rest
- Audit logs capture all access and modifications for compliance reporting
- Session and invitation tokens should be hashed and never logged in plaintext
- GDPR: Implement data export and deletion workflows per customer requests

---

**End of Schema Document**