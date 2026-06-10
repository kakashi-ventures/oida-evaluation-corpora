# User Stories — Case B: FireGlass CRM/IoT Platform

**Project**: FireGlass (Smart Window Management & IoT Monitoring)
**Client**: Innovative Windows LLC
**Vendor**: Atlas Forge LLC
**Contract Start**: 2025-07-21
**Duration**: 15–17 weeks
**Technology Stack**: Next.js 14, TypeScript, Prisma, PostgreSQL, MQTT, Supabase

---

## Epic 1: Authentication & Authorization

### US-001: Admin creates user account with role assignment
**Status**: Done
**Priority**: P1

As an **Administrator**, I want to create new user accounts and assign roles (Admin, Manager, Technician, Field Tech, Viewer, Guest) so that team members can access the system with appropriate permissions.

**Acceptance Criteria**:
- Admin can navigate to a user management dashboard
- Role selection dropdown includes all six roles with clear permission descriptions
- New user receives an invitation email with a secure setup link
- System logs all user creation events in the audit trail

---

### US-002: User logs in with email and password
**Status**: In Progress
**Priority**: P1

As a **User**, I want to log in with my email and password so that I can access the FireGlass platform securely.

**Acceptance Criteria**:
- Login form accepts valid email format
- Password field is masked during input
- Failed login attempts are logged and limited to 5 per 15 minutes
- Successful login redirects to personalized dashboard

---

### US-003: Role-based permission enforcement using CASL
**Status**: Done
**Priority**: P1

As a **System**, I want to enforce permissions via CASL (role-based access control) so that users can only access resources and actions authorized for their role.

**Acceptance Criteria**:
- Admin can view and edit all installations and maintenance records
- Manager can view all installations but edit only assigned ones
- Technician can view/edit only assigned installations and create maintenance reports
- Field Tech can log sensor readings and upload photos but cannot modify installation data
- Guest can view read-only reports only
- Viewer has read-only access to all dashboards

---

### US-004: Shell account invitation flow for client stakeholders
**Status**: To Do
**Priority**: P2

As a **Manager**, I want to invite external stakeholders (e.g., client executives) to view reports without creating full user accounts so that information sharing is streamlined.

**Acceptance Criteria**:
- Manager can generate a time-limited invitation link (valid 7 days)
- Invitation link grants read-only access to specified reports
- Guest can view dashboards without login after following the link
- Manager can revoke invitations at any time

---

### US-005: Row-Level Security (RLS) for multi-tenant data isolation
**Status**: Blocked
**Priority**: P1
**Blocking Reason**: Pending legal review of GDPR data isolation requirements and consent flow compliance. Legal team review scheduled for 2025-08-15.

As a **System**, I want to enforce Row-Level Security at the database level so that each organization's data is completely isolated and no user can access another organization's records.

**Acceptance Criteria**:
- PostgreSQL RLS policies prevent cross-tenant data leakage
- Every query filters data by authenticated user's organization_id
- Audit logs show any attempted unauthorized access
- Security testing confirms zero data leakage between test organizations

---

## Epic 2: Installation Management

### US-006: Create installation record with project code generation
**Status**: Done
**Priority**: P1

As a **Manager**, I want to create a new installation record and automatically generate a unique project code so that each installation is tracked consistently.

**Acceptance Criteria**:
- Project code format is: CC-TTT-AAA-YYYY-SSSS (Country-Type-Area-Year-Sequential)
- Example: IT-DWL-CNT-2025-0001 (Italy, Dwelling, Center, 2025, Sequential #1)
- Code is auto-generated and non-editable after creation
- Installation form includes fields for address, client contact, installation date, and window count

---

### US-007: Map visualization of all active installations
**Status**: In Progress
**Priority**: P2

As a **Manager**, I want to view all installations on an interactive map so that I can monitor geographic distribution and respond to regional issues quickly.

**Acceptance Criteria**:
- Map displays all installations as markers with color coding by status
- Clicking a marker opens a popup with installation name, project code, and contact info
- Map supports zoom and pan, with street map and satellite views
- Clustering enables visibility when many installations are close together

---

### US-008: Log GPS coordinates for field installation visits
**Status**: To Do
**Priority**: P2

As a **Field Technician**, I want to automatically record GPS coordinates and timestamp when I arrive at an installation site so that proof of visit and location history are maintained.

**Acceptance Criteria**:
- Mobile app requests location permission on first field visit
- GPS coordinates captured with ±5 meter accuracy
- Timestamp and technician ID are recorded with each location log
- Offline mode queues GPS logs for upload when connectivity returns

---

### US-009: Assign multiple window models to single installation
**Status**: To Do
**Priority**: P2

As a **Manager**, I want to assign multiple window models (Model A, B, or C) to a single installation so that complex buildings with mixed window types are properly documented.

**Acceptance Criteria**:
- Installation form allows adding multiple window line items
- Each line item specifies model type, quantity, location (floor/room), and serial number range
- System calculates total maintenance task count based on model-specific checklists
- Installation summary displays breakdown of window models and counts

---

## Epic 3: Window Lifecycle

### US-010: Register Helion windows with QR codes and serial numbers
**Status**: Done
**Priority**: P1

As a **Technician**, I want to scan a QR code on each Helion window to register it in the system with its unique serial number so that every window is tracked individually.

**Acceptance Criteria**:
- Mobile app has a QR code scanner that captures the code
- Serial number is extracted from QR code and validated (format: PS-XXXX-YYYY-ZZZZ)
- Registration links window to installation and assigns it to one of three models
- Duplicate serial number scan triggers a warning

---

### US-011: Track window lifecycle states and transitions
**Status**: In Progress
**Priority**: P1

As a **System**, I want to track window state transitions (Active, Under Maintenance, Deactivated, Replaced) so that the maintenance workflow respects the window's current condition.

**Acceptance Criteria**:
- Window state transitions are logged with timestamp and responsible user
- Transitions follow business rules (e.g., cannot schedule maintenance for Deactivated windows)
- Dashboard shows count of windows in each state
- Historical state changes are visible in the window detail view

---

### US-012: Sensor data ingestion with <200ms response time target
**Status**: In Progress
**Priority**: P1

As a **System**, I want to ingest Helion sensor data (temperature, smoke, air quality) via MQTT with a response time of <200ms so that real-time monitoring dashboards remain responsive and alerts are triggered without delay.

**Acceptance Criteria**:
- MQTT broker receives sensor payloads and publishes to HelionLink subscriptions
- Data is written to PostgreSQL within <200ms of receipt
- Dashboard updates within 500ms of sensor event
- Latency is monitored continuously and logged for performance analysis

---

### US-013: Generate maintenance checklist based on window model
**Status**: To Do
**Priority**: P2

As a **Technician**, I want the system to auto-generate a maintenance checklist specific to the window model so that I perform all required checks without omissions.

**Acceptance Criteria**:
- Model A windows trigger a 15-point checklist (seal integrity, sensor function, frame cracks, etc.)
- Model B windows trigger an 18-point checklist (includes thermal imaging review)
- Model C windows trigger a 32-point checklist (comprehensive inspection plus calibration)
- Technician can mark checklist items complete and add notes per item

---

### US-014: Assign window maintenance state and track replacement history
**Status**: Blocked
**Priority**: P2
**Blocking Reason**: Awaiting Helion firmware documentation to clarify sensor reset procedures and compatibility matrix with HelionLink gateway versions. Vendor to provide by 2025-09-01.

As a **Technician**, I want to mark windows as requiring maintenance and track when they are repaired or replaced so that installation managers know the current maintenance state.

**Acceptance Criteria**:
- Technician can update window state to "Needs Maintenance" or "Replaced"
- Replacement record includes old serial number, new serial number, date, and reason
- System prevents scheduling new maintenance for replaced windows
- Replacement history is visible in compliance reports

---

## Epic 4: Maintenance Interventions

### US-015: Simple form-based maintenance workflow
**Status**: Done
**Priority**: P1

As a **Technician**, I want to complete a simple maintenance form (technician name, date, work description, parts replaced) so that quick interventions are logged without excessive overhead.

**Acceptance Criteria**:
- Form has fields: Technician, Date, Work Description, Parts Replaced, Notes
- Form submission triggers PDF report generation
- Report is stored in the database and linked to the installation
- Offline mode allows form completion with sync on reconnect

---

### US-016: Smart checklist-based maintenance workflow with severity scoring
**Status**: In Progress
**Priority**: P1

As a **Technician**, I want to complete a comprehensive checklist during maintenance so that all safety-critical items are inspected and issues are scored for severity (0–100 scale).

**Acceptance Criteria**:
- Checklist includes model-specific items (15/18/32 items depending on window model)
- Each checklist item can be marked Pass, Fail, or N/A with optional notes
- Failed items trigger a severity score popup (0–100 slider) to quantify urgency
- Aggregate severity score is calculated and displayed at the end

---

### US-017: Dual signature workflow for maintenance completion
**Status**: To Do
**Priority**: P2

As a **Manager**, I want maintenance interventions to require dual signatures (technician and supervisor) so that work quality is verified before closure.

**Acceptance Criteria**:
- Maintenance form shows signature blocks for Technician and Manager/Supervisor
- Both parties must sign (digitally or via touchscreen) before form can be submitted
- Unsigned forms are marked as "Pending Approval" in the dashboard
- Signature metadata (timestamp, device ID) is recorded for audit purposes

---

### US-018: Auto-generate and email PDF maintenance reports
**Status**: Blocked
**Priority**: P2
**Blocking Reason**: Awaiting integration credentials from Supabase storage backend and approval of email delivery service (currently evaluating SendGrid vs. Resend). Expected completion 2025-08-20.

As a **System**, I want to automatically generate a PDF report after maintenance completion and email it to the client and technician so that records are distributed immediately.

**Acceptance Criteria**:
- PDF includes installation info, window serial numbers, checklist results, signatures, and severity scores
- Report is stored in Supabase and linked to the maintenance record
- Email is sent to client contact and technician within 60 seconds of form submission
- Email includes a secure link to view the PDF in the browser
- Email delivery status is logged for audit trail

---

## Epic 5: IoT Monitoring (HelionLink)

### US-019: MQTT sensor subscription and real-time data ingestion
**Status**: In Progress
**Priority**: P1

As a **System**, I want to subscribe to MQTT topics from Helion sensors (temperature, smoke density, air quality) and ingest data in real-time so that the platform maintains current sensor readings.

**Acceptance Criteria**:
- System connects to MQTT broker and subscribes to `/heatlink/sensors/+/telemetry`
- Sensor payloads are parsed and validated (JSON schema)
- Data is written to PostgreSQL with timestamp and sensor_id
- Connection loss triggers a reconnection algorithm with exponential backoff
- Sensor payloads older than 5 minutes are flagged as stale

---

### US-020: Real-time dashboard with sensor readings and historical graphs
**Status**: To Do
**Priority**: P1

As a **Manager**, I want to view a real-time dashboard showing current temperature, smoke, and air quality readings for each installation so that I can monitor safety conditions at a glance.

**Acceptance Criteria**:
- Dashboard displays current readings as gauge charts (temperature, smoke density, air quality percentages)
- Each gauge shows green/yellow/red zones based on safety thresholds
- Historical graphs show 24-hour, 7-day, and 30-day trends for each sensor
- Data points are updated every 5 seconds without requiring page refresh

---

### US-021: Automated alarm workflow when sensor thresholds are breached
**Status**: To Do
**Priority**: P1

As a **System**, I want to trigger automated alarms when sensor readings exceed safety thresholds so that critical events are flagged immediately to responsible personnel.

**Acceptance Criteria**:
- Configurable thresholds for temperature (e.g., >60°C), smoke density (>20%), and air quality (AQI >150)
- When threshold is breached, an in-app notification is sent to all Managers and Supervisors
- SMS or email alert is sent to designated on-call technician
- Alarm state is logged and visible in the dashboard with timestamp and severity
- Operator can manually acknowledge or dismiss alarms

---

### US-022: Remote relay control for emergency window operation
**Status**: Blocked
**Priority**: P2
**Blocking Reason**: Pending firmware release from Helion hardware team for relay module integration. Currently waiting for v2.1 firmware which includes relay control API. Expected release 2025-09-15.

As a **Manager**, I want to remotely trigger emergency venting of a Helion window (via relay control) so that smoke can be vented in case of fire events.

**Acceptance Criteria**:
- Dashboard displays a "Vent Window" button for each window with an active relay module
- Button requires confirmation and logs the operator's ID and timestamp
- Relay command is sent via MQTT to the target window
- Confirmation of relay state is received within 5 seconds
- Venting action is logged in the audit trail with details

---

## Epic 6: Reporting & Compliance

### US-023: Generate fire safety compliance reports
**Status**: Done
**Priority**: P1

As a **Manager**, I want to generate a fire safety compliance report that summarizes all installations, their maintenance history, and sensor status so that I can demonstrate compliance with fire safety regulations.

**Acceptance Criteria**:
- Report includes installation list with project codes and addresses
- Maintenance history shows last inspection date, technician name, and severity scores
- Sensor status dashboard shows current readings for all installations
- Report can be filtered by date range and installation region
- Report is generated as PDF and can be exported as CSV

---

### US-024: View maintenance history with technician details and issue severity
**Status**: In Progress
**Priority**: P2

As a **Manager**, I want to view a maintenance history log that shows all past interventions, including technician names, dates, work performed, and severity scores so that I can identify patterns and schedule preventive work.

**Acceptance Criteria**:
- Maintenance history is displayed as a sortable table with columns: Date, Installation, Technician, Work Type, Severity Score, Status
- Filtering is available by installation, date range, technician, and severity level
- Clicking a row expands to show the full maintenance report and checklist results
- Export to CSV includes all visible columns

---

### US-025: Audit trail with immutable logs of all system actions
**Status**: To Do
**Priority**: P3

As a **Compliance Officer**, I want to view an immutable audit trail of all system actions (logins, data modifications, report generation, alert acknowledgments) so that I can satisfy audit requirements and investigate security incidents.

**Acceptance Criteria**:
- Audit trail logs user ID, action type, resource ID, timestamp, IP address, and change details
- Logs are stored in an append-only table that cannot be modified or deleted
- Audit report can be filtered by date, user, action type, or resource
- Report can be exported as PDF with digital signature for compliance submission
- Access to audit logs is restricted to Admin and Compliance Officer roles only

---

## Summary

| Epic | Story Count | Done | In Progress | To Do | Blocked |
|------|-------------|------|-------------|-------|---------|
| 1. Authentication & Authorization | 5 | 2 | 1 | 1 | 1 |
| 2. Installation Management | 4 | 1 | 1 | 2 | 0 |
| 3. Window Lifecycle | 5 | 2 | 2 | 1 | 1 |
| 4. Maintenance Interventions | 4 | 1 | 1 | 1 | 1 |
| 5. IoT Monitoring (HelionLink) | 4 | 0 | 1 | 2 | 1 |
| 6. Reporting & Compliance | 3 | 2 | 1 | 1 | 0 |
| **Total** | **25** | **8** | **6** | **7** | **4** |

---

## Key Notes

- **Blocked Stories**: US-005 (GDPR legal review), US-014 (firmware docs pending), US-018 (Supabase integration), US-022 (firmware relay module)
- **KPI Reference**: US-012 specifies <200ms response time for sensor data ingestion—this will be compared against the test plan's 500ms latency target.
- **Project Code Format**: CC-TTT-AAA-YYYY-SSSS ensures consistency across all installations (e.g., IT-DWL-CNT-2025-0001).
- **Window Models**: Maintenance checklists vary by model (Model A: 15 items, Model B: 18 items, Model C: 32 items).
- **IoT Integration**: All sensor data flows through HelionLink (MQTT broker) with real-time ingestion into PostgreSQL.