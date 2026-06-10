# FireGlass UI/UX — Wireframe Notes & Design Specifications

**Document Date:** 2025-08-12
**Prepared by:** Samir Osei & Clara Duval (with design input from Alberto Neri)
**Design Tool:** Figma (mockups shared in #fireglass-project Slack channel)
**Current Status:** High-fidelity wireframes approved by client, ready for component implementation

---

## Overview

This document describes the layout, navigation flow, and key design decisions for FireGlass v1.0 MVP. Detailed Figma mockups are maintained in the project Slack workspace; this document serves as a reference guide for developers implementing components.

---

## 1. Global Navigation & Layout

### Top-Level Navigation

- **Sidebar (persistent, collapsible on mobile)**
  - FireGlass logo + version
  - Main menu items:
    - Dashboard
    - Installations
    - Inspections
    - Reports
    - Maintenance Scheduling
    - Administration (admin/manager only)
    - Settings
    - Help & Support

- **Header Bar**
  - Current user profile badge (name, role)
  - Notifications icon with unread count badge
  - Search bar (quick-search installations by ID, name, or location)
  - Logout button

### Color Palette

- **Primary:** #2563EB (vibrant blue)
- **Status indicators:** Red (#DC2626), Amber (#F59E0B), Green (#10B981) — traffic light convention
- **Neutral:** #F3F4F6 (light), #6B7280 (medium), #1F2937 (dark)
- **Accent:** #8B5CF6 (purple for secondary CTAs)

---

## 2. Dashboard (Main Overview)

### Layout Grid

```
┌─────────────────────────────────────────────────────────────┐
│                         HEADER                              │
├──────────────┬──────────────────────────────────────────────┤
│   SIDEBAR    │                                              │
│              │        DASHBOARD MAIN CONTENT                │
│              │                                              │
│              │  ┌─────────────────────────────────────────┐ │
│              │  │ KPI Cards (3 columns)                   │ │
│              │  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ │ │
│              │  │ │ Sensors  │ │ Alerts   │ │ Installs │ │ │
│              │  │ │ Online   │ │ Pending  │ │ Total    │ │ │
│              │  │ │ 487/500  │ │ 12       │ │ 512      │ │ │
│              │  │ └──────────┘ └──────────┘ └──────────┘ │ │
│              │  └─────────────────────────────────────────┘ │
│              │                                              │
│              │  ┌─────────────────────────────────────────┐ │
│              │  │ Installation Status Cards (scrollable)  │ │
│              │  │ [ GREEN ][ AMBER ][ RED ][ GREEN ]      │ │
│              │  │ Each card: location, sensor count,      │ │
│              │  │ last reading timestamp, drill-down link │ │
│              │  └─────────────────────────────────────────┘ │
│              │                                              │
│              │  ┌──────────────┬──────────────────────────┐ │
│              │  │ Alert Feed   │ Map View                 │ │
│              │  │ (recent 10)  │ (installations plotted)  │ │
│              │  │              │                          │ │
│              │  │ 🔴 Sensor    │                          │ │
│              │  │    FG-087    │                          │ │
│              │  │    2 min ago │                          │ │
│              │  │              │                          │ │
│              │  │ 🟠 Inspection│                          │ │
│              │  │    due FG-156│                          │ │
│              │  │    in 5 days │                          │ │
│              │  └──────────────┴──────────────────────────┘ │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

### KPI Cards

- **Sensors Online:** Show count and % of total online sensors (green/amber/red indicator based on threshold)
- **Active Alerts:** Count of critical/warning alerts in the past 24 hours
- **Total Installations:** Snapshot of fleet size
- **Next Scheduled Maintenance:** Count of tasks in next 7 days

### Installation Status Cards

**Design Notes from Alberto:** "I want to see status at a glance. Use the red/amber/green traffic light colors so operations staff can scan quickly."

- Each card displays:
  - Installation ID (e.g., "FG-087-MainOffice")
  - Location name
  - Sensor count and status with type icons: flame (TG-400), smoke cloud (SM-220), leaf/air (AQ-100)
  - Last sensor reading timestamp
  - Temperature / humidity sparkline (tiny 7-day chart)
  - Drill-down chevron (→) to installation detail page

- Cards are sortable/filterable by:
  - Status (green/amber/red)
  - Region
  - Installation type
  - Last alert date
  - Sensor model (TG-400, SM-220, AQ-100)

### Alert Feed

- **Real-time alerts** from sensor triggers and inspection due-date events
- Each alert entry shows:
  - Icon (circle colored by severity)
  - Sensor or installation ID
  - Alert description
  - Time elapsed ("2 min ago")
  - Action link (view installation, acknowledge, dismiss)

- Alert feed auto-refreshes every 5 seconds; older items slide down

### Map View

- **Mapbox-based** (or similar) showing all installations as markers
- Marker color indicates status (red/amber/green)
- Clicking marker opens installation detail sidebar
- Search/filter integration with location-based querying
- Zoom to fit all installations on load

---

## 3. Installation Detail Page

### Layout

```
┌──────────────────────────────────────────────────────┐
│ HEADER: Breadcrumb > Dashboard > Installations > FG-087 │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─ Installation Info Card ─────────────────────┐  │
│  │ FG-087: Downtown Business Center, Suite 4B   │  │
│  │ Region: Central Europe | Installed: 2023-05 │  │
│  │ Asset Class: Commercial | Building Type: Office │
│  │ Contact: John Facility Manager (john@...) │  │
│  │ [Edit] [More Details] [View Contract]      │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Sensor Status ───────────────────────────────┐  │
│  │                                               │  │
│  │ Sensor ID      | Reading    | Status | Time  │  │
│  │ ─────────────────────────────────────────────│  │
│  │ PYRO-4521-A    | 23.4°C     | 🟢 OK  | 1 min │  │
│  │ PYRO-4521-B    | 45% RH     | 🟢 OK  | 1 min │  │
│  │ PYRO-4522-A    | 22.8°C     | 🟢 OK  | 3 min │  │
│  │ PYRO-4522-B    | 52% RH     | 🟠 WARN| 3 min │  │
│  │                                               │  │
│  │ Last Updated: 2025-08-12 14:52:33 CET       │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Inspection & Lifecycle ──────────────────────┐  │
│  │                                               │  │
│  │ Last Inspection: 2025-07-15 (28 days ago)   │  │
│  │ Next Due: 2025-09-15 (approx. 34 days)      │  │
│  │ Inspection History:                          │  │
│  │   2025-07-15 | Preventive | PASS | Clara D. │  │
│  │   2025-06-15 | Preventive | PASS | John S. │  │
│  │   2025-05-20 | Incident   | FAIL→FIX | J.S.│  │
│  │                                               │  │
│  │ [Schedule Inspection] [View Inspection Log]  │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Sensor Readings (7-day Chart) ──────────────┐  │
│  │                                               │  │
│  │  Temperature Trend                            │  │
│  │  30°C │     ╱╲                                │  │
│  │  25°C │    ╱  ╲      ╱╲     ╱                │  │
│  │  20°C │───╱────╲────╱──╲───╱                 │  │
│  │  15°C │                                       │  │
│  │       └───┴───┴───┴───┴───┴───┴───→ Days     │  │
│  │       Mon   Tue   Wed   Thu   Fri Sat Sun    │  │
│  │                                               │  │
│  │ [View Detailed Analytics]                    │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌─ Maintenance Notes ───────────────────────────┐  │
│  │ 2025-08-01: Sensor PYRO-4522-B recalibrated │  │
│  │ 2025-07-15: Battery replaced (PYRO-4521-A)  │  │
│  │                                               │  │
│  │ [Add Note]                                    │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Key Features

- **Breadcrumb navigation** at top for context
- **Installation info card** with editable metadata (admin/manager only)
- **Sensor status table** with current readings, thresholds, and time-since-update
- **Inspection lifecycle** showing last inspection date, next due date, and history
- **7-day sensor trend chart** (temperature, humidity, or custom metric selectable)
- **Maintenance notes** field with timestamp and technician attribution
- **Action buttons:** Schedule Inspection, Export Report, Edit Metadata, View Timeline

### Design Note from Clara

"The sensor table needs to refresh smoothly. Current library [specific library name redacted] updates in place, but we need to monitor performance with 50+ sensors per installation. John mentioned we might want to batch updates per 5-second interval rather than per-sensor."

---

## 4. Inspection Form

### Multi-Step Form Flow

```
Step 1: Installation Selection
  ↓
Step 2: Inspection Type & Checklist
  ↓
Step 3: Sensor Readings Review
  ↓
Step 4: Photo Upload & Annotations
  ↓
Step 5: Signature Capture
  ↓
Step 6: Review & Submit
```

### Step 1: Installation Selection

- **Search/filter** for installation ID, location, or facility manager name
- **List view** of recent installations (with status indicator)
- **Location map** to select by proximity
- Offline mode: form drafts cached to IndexedDB; sync on reconnect

### Step 2: Inspection Type & Checklist

**Inspection Types:**
- Preventive (routine, quarterly)
- Post-Incident (follow-up to sensor alert)
- Compliance (annual audit)
- Custom (ad-hoc field tech assessment)

**Checklist Items** (configurable per inspection type):
- Visual inspection: frames intact?
- Seal integrity check
- Sensor attachment inspection
- Environmental conditions noted
- Anomalies observed (free text)
- Photos required? (Y/N)

Each checklist item is a radio button (OK / FAIL / NOT APPLICABLE). If FAIL is selected, a required comment field appears.

### Step 3: Sensor Readings Review

- Pre-populate with **last 3 sensor readings** from Helion
- Allow technician to accept or override values
- Visual indicators for values outside normal range
- Timestamp auto-set to current time (editable by admin)

### Step 4: Photo Upload & Annotations

- **Camera widget** (on mobile, opens native camera; on desktop, file picker)
- Upload up to 10 photos per inspection
- **Lightweight annotation tool:** draw arrows/circles, add labels
- Photo metadata auto-captured (geolocation, timestamp)

**Design Note from Clara:** "We need to verify that our image compression doesn't lose detail. Field techs are shooting evidence of seal failures. Recommend lossless or high-quality JPG (90+)."

### Step 5: Signature Capture

- **Canvas element** for technician signature (not a typed initial)
- **Second signature area** for facility manager or supervisor
- Signature image embedded in PDF report

**Design Note from Clara:** "Signature library evaluation pending. Current candidates: signature_pad (well-maintained), canvas-drawing-js (lightweight but no clear maintenance). We need to demo with actual field techs to ensure the canvas is responsive enough on tablets."

### Step 6: Review & Submit

- Summary page showing all entered data
- Editable sections (click to edit each step)
- **Final submit button** (locked until all required fields complete)
- Offline: saves draft locally if network unavailable, prompts sync on reconnect

---

## 5. Maintenance Scheduling Interface

### Layout

```
┌──────────────────────────────────────────────────────┐
│ Maintenance Schedule | Calendar View | List View     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  August 2025                                         │
│  ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┐       │
│  │ Sun │ Mon │ Tue │ Wed │ Thu │ Fri │ Sat │       │
│  ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤       │
│  │ 3   │ 4   │ 5   │ 6   │ 7   │ 8   │ 9   │       │
│  │     │[2]  │     │[3]  │     │     │[1]  │       │
│  │     │tasks│     │tasks│     │     │task │       │
│  ├─────┼─────┼─────┼─────┼─────┼─────┼─────┤       │
│  │ 10  │ 11  │ 12  │ 13  │ 14  │ 15  │ 16  │       │
│  │     │     │[1]  │     │     │[4]  │     │       │
│  │     │     │task │     │     │tasks│     │       │
│  └─────┴─────┴─────┴─────┴─────┴─────┴─────┘       │
│                                                      │
│  Day Detail (selected date: 2025-08-08):           │
│  ┌──────────────────────────────────────────────┐  │
│  │ Assigned Tasks (Fri, Aug 8, 2025)            │  │
│  │                                              │  │
│  │ FG-087 | Preventive Inspection               │  │
│  │ Assigned: Clara Duval | Est. Duration: 1h   │  │
│  │ Status: NOT STARTED | [Start] [Reschedule]  │  │
│  │                                              │  │
│  │ FG-156 | Post-Incident Follow-up             │  │
│  │ Assigned: John Smith | Est. Duration: 2h    │  │
│  │ Status: SCHEDULED | [Start] [Reassign]      │  │
│  │                                              │  │
│  │ FG-203 | Sensor Calibration                  │  │
│  │ Assigned: John Smith | Est. Duration: 30m   │  │
│  │ Status: IN PROGRESS (started 10:30)         │  │
│  │ [Mark Complete] [Extend Time]               │  │
│  │                                              │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  [+ New Task] [Bulk Assign] [View Technician Load] │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Features

- **Calendar view** showing task density (# tasks per day)
- **List view** for filter/sort by technician, installation, priority, or date range
- **Bulk assignment:** select multiple installations and assign to technician in one action
- **Task details:** Installation ID, type, assigned technician, estimated duration, priority
- **Status tracking:** NOT STARTED → IN PROGRESS → COMPLETED
- **Technician workload dashboard** showing utilization and capacity
- **Integration with sensor alerts:** high-priority installations can auto-create maintenance tasks

---

## 6. Report Generation & Export

### Layout

```
┌─────────────────────────────────────────────────────┐
│ Reports | Generate | View Archive                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Report Builder                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Report Type:                                │   │
│  │ ☐ Compliance Summary (ISO 9001, building)  │   │
│  │ ☐ Performance Analysis (30/60/90-day trend)│   │
│  │ ☐ Maintenance Log                          │   │
│  │ ☐ Custom Report (select fields)            │   │
│  │                                             │   │
│  │ Date Range:                                 │   │
│  │ From: [2025-07-01] To: [2025-08-12]       │   │
│  │                                             │   │
│  │ Scope:                                      │   │
│  │ ☑ All Installations                        │   │
│  │ ☐ Specific Installation: [FG-087____]      │   │
│  │ ☐ Region: [Central Europe]                 │   │
│  │                                             │   │
│  │ Format:                                     │   │
│  │ ◉ PDF (formatted for printing)             │   │
│  │ ☐ CSV (for spreadsheet import)             │   │
│  │ ☐ JSON (for API integration)               │   │
│  │                                             │   │
│  │ [Generate Report] [Schedule Monthly] [Save Template] │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Report Archive                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Date Gen.  │ Type        │ Scope    │ Format│   │
│  │ 2025-08-12 │ Compliance  │ All     │ PDF   │   │
│  │ 2025-08-01 │ Performance │ Region  │ CSV   │   │
│  │ 2025-07-20 │ Maint. Log  │ FG-087  │ PDF   │   │
│  │                                             │   │
│  │ [View] [Download] [Email] [Delete]        │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Scheduled Reports                                  │
│  ☑ Monthly Compliance (every 1st of month, 9 AM)  │
│  ☑ Weekly Performance (every Monday, 8 AM)        │
│  [+ Add Scheduled Report]                         │   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Report Types

1. **Compliance Summary:** Installation metadata, inspection history, pass/fail statuses, signed-off dates, ASG-FP Level 2 certification metadata. Report output includes ASG-FP compliance metadata block (certification level, audit date, Argus Safety Group reference number). Customer-facing document suitable for auditors.
2. **Performance Analysis:** Sensor trend charts (TG-400, SM-220, AQ-100 specific), anomaly detection, temperature/humidity patterns, predicted maintenance needs.
3. **Maintenance Log:** Chronological list of all inspections and sensor maintenance (EPFC-2200 tagged), with technician attribution.
4. **Custom Report:** User-selected fields (installations, date range, metrics, sensor models) exported to chosen format.

### Export Formats

- **PDF:** Branded header, formatted tables, embedded charts, signature blocks
- **CSV:** Tabular data for Excel import, spreadsheet analysis
- **JSON:** Machine-readable for BI tool integration

### Generation Performance

- Reports generated server-side (Next.js API route)
- Target: generation completes within 5 seconds for ≤500 installations
- Large reports (>1000 installations) may be async with email delivery

---

## 7. Mobile & Responsive Design

### Breakpoints

- **Desktop:** ≥1024px (sidebar always visible)
- **Tablet:** 768px–1023px (sidebar collapsible, bottom sheet modals)
- **Mobile:** <768px (sidebar hamburger menu, full-width modals)

### Mobile Inspection Workflow

**Key Changes:**
- Form steps are full-screen (no multi-column layout)
- Camera widget opens native camera app (iOS/Android)
- Signature canvas optimized for touch input (larger touch targets)
- Scrollable form with submit button pinned to bottom

### PWA Features

- **Offline support:** Installation list, recent inspections, and draft inspection forms cached to IndexedDB
- **Background sync:** Inspection submissions queued and synced when online
- **Push notifications:** (Note: Push notifications were descoped; replaced with CSV export for reporting)
- **Home screen install:** "Add to Home Screen" banner on mobile browsers

### Device Considerations

- **Field tablets** (iPad, Android 10"): landscape orientation support, gloved-hand-friendly button sizing (≥48px)
- **Smartphones** (iOS/Android): portrait-primary, responsive form fields
- **Desktop browsers:** Chrome, Firefox, Safari (latest 2 versions)

---

## 8. Design References & Decisions

### Figma Mockups Location

All high-fidelity wireframes are maintained in the project Figma workspace under:
- **Team:** Innovative Windows LLC
- **Project:** FireGlass v1.0 MVP
- **Shared in:** #fireglass-project Slack channel (pinned messages)

### Color Accessibility

- **WCAG AA compliance:** All color combinations meet ≥4.5:1 contrast ratio
- Traffic light colors (red/amber/green) supplemented with icons/text labels for color-blind accessibility
- Tested with: WebAIM Contrast Checker, Stark Figma plugin

### Icon Set

- **Lucide React** for UI icons (consistent, open-source, 24x24 standard)
- Custom icons for Helion and HelionLink branding (to be provided by client)

### Typography

- **Font:** Inter (system stack fallback: -apple-system, BlinkMacSystemFont)
- **Hierarchy:** Headings (h1–h3), body text (14px), labels (12px)
- **Line height:** 1.5 for readability on small screens

---

## 9. Known Design Issues & Open Questions

1. **Sensor Table Performance (from Clara):**
   > "Current table library re-renders all rows on any sensor update. With 50+ sensors per installation, this causes jank. Recommend virtualization (react-window) or batch updates."

   **Status:** Pending performance testing in Sprint 4. Clara to prototype optimized table component.

2. **Signature Canvas Library (from Clara):**
   > "Signature library selection is critical. Current leading candidates are signature_pad (active maintenance, broad browser support) and canvas-drawing-js (lighter weight but unclear maintenance roadmap). Recommend live demo with field technicians before finalizing."

   **Status:** Pending POC in early Sprint 5. John Smith to arrange field tech session for usability feedback.

3. **Offline Sync Strategy:**
   > "PWA drafts should auto-save to IndexedDB every 30 seconds. On reconnect, should re-validate data against server before submitting (e.g., if installation was deleted, prevent submission). Need to define error handling flow."

   **Status:** Defined in data-sync-strategy.md. Clara to implement in Sprint 4.

4. **Report Generation Latency:**
   > "Current PDF generation library (pdfkit) may be slow for large datasets. Benchmark against 500-installation report and consider headless-chrome or serverless function if >10s generation time."

   **Status:** Benchmark planned for Sprint 6 (performance tuning phase).

5. **Mobile Camera Integration:**
   > "Field techs need to upload photos quickly. Native camera on mobile is faster than web input. Should we explore Capacitor (React Native web bridge) for deeper device integration, or stick with web input?"

   **Status:** MVP uses web file input. Capacitor integration deferred to v1.1 if performance issues arise.

---

## 10. Accessibility & Usability Notes

### WCAG 2.1 AA Compliance

- All form inputs have associated labels (explicit or aria-label)
- Color not the only indicator of status (icons + text)
- Keyboard navigation fully supported (tab order, focus visible)
- Screen reader tested with NVDA (Windows) and VoiceOver (Mac)
- Estimated reading level: 8th-grade (simple, jargon-free UX copy)

### Field Technician Usability

- **Quick access:** Inspection form accessible from dashboard in ≤3 taps
- **Offline-first:** No spinning loaders; local edits persist even if network drops
- **Minimalist design:** Inspection checklist visible without scrolling (5–7 items per screen)
- **Large touch targets:** Buttons ≥48px × 48px for gloved-hand operation

---

## 11. Future Enhancements (Out of Scope for v1.0)

- Native iOS/Android apps (currently PWA only)
- Notification push system (replaced with CSV export + email)
- Advanced analytics dashboard (BI tool integration via API)
- Machine learning-based anomaly detection (sensor trend analysis)
- Customer portal (facility manager dashboard for read-only access)
- Multi-language support (initial launch: English only, German translation planned for v1.1)

---

**Document Status:** APPROVED (Client sign-off: 2025-08-12)
**Last Updated:** 2025-08-12 by Samir Osei
**Next Review:** Sprint 4 (component development) or upon scope change
