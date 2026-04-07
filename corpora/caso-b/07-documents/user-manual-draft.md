# FireGlass User Manual (DRAFT)

**Version:** 0.3 (Draft)
**Status:** NOT FOR CLIENT DISTRIBUTION
**Prepared by:** Clara Duval, Atlas Forge LLC
**Last Updated:** 2025-10-15
**Target Audience:** Field Technicians, Operations Managers, Administrators

---

⚠️ **DRAFT NOTICE:** This document is incomplete and subject to revision. Sections marked [TODO] or "[Section pending]" are not yet written. Final version pending UAT completion and client feedback.

---

## 1. Getting Started

### 1.1 Login & Account Setup

**Step 1: Access the Platform**
- Open your web browser (Chrome, Firefox, Safari, or Edge)
- Navigate to: https://fireglass.innovativewindows.eu
- You will see the FireGlass login screen

**Step 2: Enter Your Credentials**
- **Email:** Your Innovative Windows LLC email address (e.g., john.smith@innovativewindows.eu)
- **Password:** Your initial temporary password (sent by your administrator)
- Click **"Login"** button

**Step 3: Change Your Password (First Login)**
- You will be prompted to create a new password
- **Requirements:** Minimum 12 characters, include uppercase, lowercase, number, and special character
- Click **"Set Password"** when done

**Step 4: Optional: Set Up Two-Factor Authentication (2FA)**
- If your administrator requires 2FA, you will see a prompt: "Set up 2FA?"
- Click **"Start 2FA Setup"**
- Scan QR code with Authenticator app (Google Authenticator, Microsoft Authenticator, Authy, etc.)
- Enter 6-digit code from app
- Click **"Verify"** and save recovery codes in a safe place
- Click **"Continue"**

**Step 5: Welcome to Dashboard**
- You are now logged in and will see the FireGlass Dashboard

---

### 1.2 First-Time User Walkthrough

When you first log in, FireGlass displays an interactive tutorial:

1. **"Welcome to FireGlass"** → Click "Next" to dismiss
2. **Dashboard Overview** → Highlights key areas (KPI cards, sensor cards, map)
3. **Quick Actions** → Shows how to navigate to Inspections, Reports, etc.

To skip the tutorial, click **"Skip Tutorial"** at any time. You can re-run it from Settings → Help.

---

### 1.3 Browser Setup & Mobile Installation

#### Desktop / Laptop Setup

- **Recommended:** Chrome or Firefox (latest versions)
- **Minimum Window Size:** 1024 × 768 pixels (for full UI; responsive design adapts to smaller)
- **Plugins:** None required; cookies and JavaScript must be enabled

#### Mobile / Tablet Setup

**For iPhone/iPad:**
1. Open Safari and navigate to https://fireglass.innovativewindows.eu
2. Tap **Share** (arrow icon at bottom)
3. Tap **Add to Home Screen**
4. Tap **Add** to install the PWA (Progressive Web App)
5. Open the FireGlass app from your home screen

**For Android:**
1. Open Chrome (or Firefox) and navigate to https://fireglass.innovativewindows.eu
2. Tap the **3-dot menu** (top right)
3. Tap **"Install app"** (or "Add to Home Screen")
4. Tap **Install** to confirm
5. Open the FireGlass app from your home screen

**Offline Support:** After installation, you can use FireGlass offline to draft inspections. Forms sync when you reconnect.

---

## 2. Dashboard Overview

### 2.1 Main Dashboard Layout

When you log in, you see the **Dashboard** — the main control center:

```
┌─────────────────────────────────────────────────────┐
│  FireGlass Logo   [Search]         [User Name] [?]  │ ← Header
├──────────┬────────────────────────────────────────┤
│ Menu     │ Dashboard                               │
│ • Dash   │                                         │
│ • Instl. │ ┌─ KPI Cards ──────────────────────┐   │
│ • Inspc. │ │ Sensors Online | Alerts | Installs│   │
│ • Reports│ │ 487 / 500      │ 12     │ 512    │   │
│ • Maint. │ └─────────────────────────────────┘   │
│ • Admin  │                                         │
│ • Setg.  │ ┌─ Installation Status Cards ─────────┐ │
│ • Help   │ │ [GREEN] [AMBER] [RED] [GREEN] ...  │ │
│          │ │ (scrollable, click for detail)      │ │
│          │ └─────────────────────────────────────┘ │
│          │                                         │
│          │ ┌─ Alert Feed ── │ ─ Map View ───────┐ │
│          │ │ Recent Alerts  │ │ Installations   │ │
│          │ │ (scrollable)   │ │ Map (clickable) │ │
│          │ └────────────────┴─────────────────┘ │
│          │                                         │
└──────────┴────────────────────────────────────────┘
```

### 2.2 Key Dashboard Elements

#### KPI (Key Performance Indicator) Cards

At the top of the dashboard, you see three cards summarizing your fleet:

1. **Sensors Online:** Shows how many sensors are currently connected and sending data
   - Example: "487 / 500" means 487 out of 500 sensors are online
   - Color: Green if ≥95% online, Amber if 85–94%, Red if <85%

2. **Active Alerts:** Number of critical or warning-level alerts in the last 24 hours
   - Click to view the full alert feed

3. **Total Installations:** Total number of installations in your fleet
   - Example: "512" installations

#### Installation Status Cards

Below the KPI cards, you see a horizontal scrollable row of **Installation Status Cards**. Each card shows:

- **Installation ID:** e.g., "FG-087-MainOffice"
- **Location:** Building or facility name
- **Sensor Status:** e.g., "4/4 online" (all 4 sensors working)
- **Status Indicator:** Color circle (Green = OK, Amber = Warning, Red = Problem)
- **Last Reading:** Timestamp of most recent sensor data (e.g., "2 min ago")
- **Sparkline Chart:** Tiny 7-day temperature trend

**To view installation details:** Click the card or the arrow (→) icon.

#### Alert Feed (Bottom Left)

Real-time list of recent alerts. Each alert shows:

- **Icon & Color:** Red circle = critical, Amber = warning
- **Sensor/Installation ID:** Which installation triggered the alert
- **Description:** What happened (e.g., "Temperature exceeds 30°C")
- **Time:** How long ago the alert occurred
- **Action Link:** "View" or "Acknowledge" the alert

**To dismiss an alert:** Click "Acknowledge" (it moves to history but stays logged).

#### Map View (Bottom Right)

**[Section pending — interactive map display not yet mocked]**

All your installations displayed as markers on a map. Marker color indicates status (green/amber/red). Click a marker to see the installation detail sidebar.

---

### 2.3 Navigating the Menu

The left sidebar shows the main navigation menu:

- **Dashboard:** Home screen (current view)
- **Installations:** List and manage all installations
- **Inspections:** View and create inspection records
- **Reports:** Generate and download reports (PDF/CSV)
- **Maintenance:** Schedule and track maintenance tasks
- **Administration:** [Admin only] User management, settings, sensor config
- **Settings:** Profile, preferences, security
- **Help:** Documentation, FAQs, contact support

Click any menu item to navigate. On mobile, the menu collapses into a hamburger icon (☰).

---

## 3. Managing Installations

### 3.1 View All Installations

**Step 1:** Click **"Installations"** in the left menu

**Step 2:** You will see a list of all installations you have access to:

```
┌──────────────────────────────────────────────────┐
│ Installations (512)                              │
│ [+ New Installation] [Import CSV]                │
│                                                  │
│ Search: [________________] Filter: [Region ▼]   │
│                                                  │
│ Installation ID  │ Location        │ Sensors │ │
│ ─────────────────────────────────────────────  │
│ FG-087           │ Downtown Office │ 4/4 🟢  │ │
│ FG-088           │ North Park      │ 3/3 🟢  │ │
│ FG-089           │ Harbor Building │ 5/5 🟡  │ │
│ FG-090           │ Central Complex │ 2/4 🔴  │ │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 3.2 Search & Filter

**Search by ID or Name:**
1. Click the search box: [________________]
2. Type installation ID (e.g., "FG-087") or location name (e.g., "Downtown Office")
3. Press Enter or wait 2 seconds for results to auto-filter

**Filter by Region:**
1. Click the **"Filter"** dropdown (top right)
2. Select region: Central Europe, North, South, East, or West
3. List updates to show only installations in that region

**Clear filters:** Click "Reset" or click the ✕ icon next to filter name

### 3.3 Create a New Installation

**[TODO: Step-by-step form walkthrough pending UI finalization]**

### 3.4 View Installation Detail

**Step 1:** Click an installation card or name in the list

**Step 2:** You see the Installation Detail page:

```
┌─────────────────────────────────────────────────┐
│ FG-087: Downtown Business Center, Suite 4B     │
│ [Edit] [More Details] [View Contract]          │
├─────────────────────────────────────────────────┤
│                                                 │
│ Sensor Status                                   │
│ ┌───────────────────────────────────────────┐  │
│ │ PYRO-4521-A  │ 23.4°C  │ 🟢 OK  │ 1 min  │  │
│ │ PYRO-4521-B  │ 45% RH  │ 🟢 OK  │ 1 min  │  │
│ │ PYRO-4522-A  │ 22.8°C  │ 🟢 OK  │ 3 min  │  │
│ │ PYRO-4522-B  │ 52% RH  │ 🟡 WARN│ 3 min  │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ Inspection & Lifecycle                         │
│ Last Inspection: 2025-07-15 (28 days ago)    │
│ Next Due: 2025-09-15 (approx. 34 days)       │
│ [Schedule Inspection]                          │
│                                                 │
│ 7-Day Sensor Trend (Temperature)              │
│ [Line chart showing 7-day history]            │
│                                                 │
│ Maintenance Notes                              │
│ 2025-08-01: Sensor PYRO-4522-B recalibrated │
│ [Add Note]                                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Key Information:**
- **Sensor readings:** Live temperature, humidity, and other metrics for each sensor
- **Status indicators:** Color circle shows sensor health
- **Inspection history:** When was the last inspection, when is the next due?
- **Sensor trend:** 7-day chart showing temperature or humidity history
- **Maintenance notes:** Any recent service or calibration work logged here

---

## 4. Sensor Monitoring

### 4.1 Understanding Sensor Readings

Your installation may include up to three sensor types: **Helion TG-400** (thermal), **SM-220** (smoke), and **AQ-100** (air quality).

Each sensor displays:

- **Sensor ID:** Unique identifier (e.g., "PYRO-4521-A")
- **Sensor Type/Model:** TG-400, SM-220, or AQ-100
- **Reading:** Current temperature (°C), smoke density, or VOC index
- **Status:** 🟢 OK (normal), 🟡 WARN (warning), 🔴 CRIT (critical)
- **Time:** How long ago the reading was received (e.g., "1 min ago")

**Normal ranges** (default):
- **Helion TG-400 Thermal:** -20°C to +1200°C operating range; 15–25°C (OK), 25–30°C (WARN), >30°C (CRIT) for typical office installations
- **SM-220 Smoke Detector:** Particle density thresholds per facility class
- **AQ-100 Air Quality:** VOC index thresholds, typical office 0–100 ppm (OK), 100–500 ppm (WARN)
- Humidity (general): 30–60% RH (OK), 20–30% or 60–70% (WARN), <20% or >70% (CRIT)

Admin users can adjust these thresholds in **Administration > Sensor Configuration**.

### 4.2 Alert Handling

When a sensor reading exceeds a warning or critical threshold, an **Alert** is generated:

1. A red/amber circle appears in the Alert Feed (bottom left of dashboard)
2. The installation status card changes color
3. The sensor table row highlights

**To acknowledge an alert:**
1. Click the alert in the feed
2. Click **"Acknowledge"** button
3. Alert moves to history (no longer in "recent alerts" list)

**Note:** Acknowledging does NOT fix the underlying sensor issue; it just marks you as aware.

### 4.3 Investigating a Sensor Issue

**Step 1:** Click the alert or installation card

**Step 2:** Navigate to the installation detail page

**Step 3:** Look at the sensor readings:
- Is the reading normal now, or still high?
- When was the last reading received?

**Step 4:** Check the maintenance notes:
- Was there recent service work?
- Is the sensor due for calibration?

**Step 5:** If the problem persists:
- Add a maintenance note (click "Add Note")
- Schedule an inspection (click "Schedule Inspection")
- Contact the field technician team (see Help section)

---

## 5. Conducting Inspections

### 5.1 Start an Inspection

**Step 1:** Click **"Inspections"** in the left menu

**Step 2:** Click **"+ New Inspection"** (or from dashboard: click installation card → "Schedule Inspection")

**Step 3:** You see the inspection form (multi-step wizard):

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

---

### 5.2 Step-by-Step Inspection Workflow

#### **STEP 1: Installation Selection**

1. **Search for installation:** Type ID or location name (e.g., "FG-087" or "Downtown Office")
2. **Select from list:** Click the installation you want to inspect
3. **Click "Next >"** to proceed to Step 2

#### **STEP 2: Inspection Type & Checklist**

1. **Select Inspection Type:**
   - **Preventive:** Routine maintenance, every 3 months
   - **Incident:** Follow-up to an alert or issue
   - **Compliance:** Annual audit for regulatory compliance
   - **Custom:** Technician-defined inspection

2. **Complete the Checklist:**
   Each checklist item shows a question with radio buttons:
   - ☑ **OK** – Normal condition
   - ☑ **FAIL** – Problem found
   - ☑ **N/A** – Not applicable

   **Example checklist:**
   ```
   ☑ Frames intact and undamaged?
       ☑ OK   ☐ FAIL   ☐ N/A

   ☑ Seal intact (no visible cracks)?
       ☐ OK   ☑ FAIL   ☐ N/A  [Required comment: ________]

   ☑ Sensors properly attached?
       ☑ OK   ☐ FAIL   ☐ N/A

   ☑ Anomalies observed?
       ☑ OK   ☐ FAIL   ☐ N/A  [If FAIL, describe: ________]
   ```

3. **For FAIL items:** A comment field appears (required). Describe the problem.

4. **Click "Next >"** to proceed to Step 3

#### **STEP 3: Sensor Readings Review**

This step shows the **3 most recent sensor readings** from the installation:

```
┌─ Sensor Readings ──────────────────┐
│ Pre-populated from Helion       │
│                                    │
│ Sensor: PYRO-4521-A                │
│ Temperature: 23.4°C  [editable]    │
│ Time: 2025-10-15 14:52 [editable]  │
│                                    │
│ Sensor: PYRO-4521-B                │
│ Humidity: 45% RH  [editable]       │
│ Time: 2025-10-15 14:52 [editable]  │
│                                    │
│ [Accept readings] [Edit]           │
└────────────────────────────────────┘
```

**You can:**
- Accept the readings as-is
- Edit a reading if it was incorrect (e.g., technician took manual measurement)

**Click "Next >"** to proceed to Step 4

#### **STEP 4: Photo Upload & Annotations**

1. **Take or upload photos:**
   - On mobile: Tap camera icon → takes photo with native camera app
   - On desktop: Tap camera icon → file picker to select from computer
   - Upload up to 10 photos per inspection

2. **View uploaded photos as thumbnails**

3. **Optional: Annotate photos**
   - Tap a photo to zoom and annotate
   - **Annotation tools:**
     - Pen/draw tool (draw arrows or circles)
     - Text tool (add labels like "Crack here")
     - Color selector

4. **Click "Next >"** to proceed to Step 5

**Note:** If connection is slow or you're offline, photos are queued locally and uploaded when you reconnect.

#### **STEP 5: Signature Capture**

1. **Sign here (technician):**
   - A blank canvas appears
   - Sign your name in the canvas (use finger on tablet/phone, mouse on desktop)
   - If you make a mistake, click **"Clear"** and sign again

2. **Facility manager signature (optional):**
   - Another blank canvas appears for the facility manager to sign
   - Only required for Compliance inspections

3. **Click "Next >"** to proceed to Step 6

#### **STEP 6: Review & Submit**

Review all data entered:

```
┌─ Inspection Summary ─────────────┐
│                                  │
│ Installation: FG-087             │
│ Type: Preventive                 │
│ Checklist: 4 OK, 1 FAIL, 0 N/A  │
│ Readings: 4 sensors reviewed     │
│ Photos: 3 uploaded               │
│ Signatures: Technician + Manager │
│                                  │
│ [< Back] [Edit] [SUBMIT]         │
└──────────────────────────────────┘
```

**If data looks correct:**
1. Click **"SUBMIT"** button
2. If online, inspection is sent to server immediately
3. If offline, inspection is saved locally and queued for sync

**After submit:**
- Success message: "Inspection submitted successfully"
- You are redirected to Inspections list
- Inspection appears in the list with "Submitted" status

---

### 5.3 Offline Inspection Drafting

If you lose network connection while completing an inspection:

1. **Form auto-saves** every 30 seconds to your device (offline storage)
2. **Bottom of screen shows:** "⚠ Offline – Data saved locally"
3. **You can continue** filling out the form and adding photos
4. **When you reconnect:**
   - A **"Sync"** button appears (bottom right)
   - Click it to upload queued inspections
   - Success message confirms upload

**Important:** Drafts are stored locally on your device. If you clear your browser data, drafts may be lost. Make sure to sync before closing the app.

---

## 6. Generating Reports

### 6.1 Access Reports

**Step 1:** Click **"Reports"** in the left menu

**Step 2:** You see the Reports interface:

```
┌──────────────────────────────────┐
│ Reports                          │
│ [+ Generate Report]              │
│                                  │
│ Recent Reports                   │
│ ┌──────────────────────────────┐ │
│ │ Compliance (2025-10-15) PDF  │ │
│ │ [View] [Download] [Delete]   │ │
│ │                              │ │
│ │ Performance (2025-10-10) CSV │ │
│ │ [View] [Download] [Delete]   │ │
│ └──────────────────────────────┘ │
│                                  │
│ Scheduled Reports                │
│ ☑ Monthly Compliance (1st, 9 AM) │
│ ☑ Weekly Performance (Mon, 8 AM) │
│                                  │
└──────────────────────────────────┘
```

---

### 6.2 Generate a Report

**Step 1:** Click **"+ Generate Report"**

**Step 2:** Configure report parameters:

```
Report Type:
☐ Compliance Summary (inspection history, signatures, ASG-FP Level 2 metadata)
☐ Performance Analysis (30/60/90-day trends)
☐ Maintenance Log (chronological activity, EPFC-2200 tagged)
☐ Custom Report (pick your fields)

Date Range:
From: [2025-07-01] To: [2025-10-15]

Scope:
☑ All Installations
☐ Specific: [FG-087] ▼
☐ Region: [Central Europe] ▼

Format:
◉ PDF (includes ASG-FP compliance metadata)
☐ CSV
☐ JSON

[Generate Report]
```

**Note:** Generated PDFs include the ASG-FP Level 2 certification metadata block required for Argus Safety Group audits.

**Step 3:** Click **"Generate Report"**

**Step 4:** Wait for generation (usually <5 seconds). You will see:
- Progress bar or spinner
- "Report generated successfully" message

**Step 5:** Report appears in your Recent Reports list

---

### 6.3 Download or Email Report

1. In the Recent Reports list, click **"Download"** to save PDF/CSV to your computer
2. Or click **"Email"** to send report to an email address (requires setup in Settings)

---

## 7. Maintenance Scheduling

**[Section pending — calendar and task assignment UI not yet finalized]**

### 7.1 View Maintenance Schedule

### 7.2 Create a Maintenance Task

### 7.3 Assign Tasks to Technicians

---

## 8. Administration

**[Section pending — admin panel features deferred to UAT; placeholder text]**

### 8.1 User Management

**For Admin users only.** Manage user accounts:
- Add new users
- Assign roles (Admin, Manager, Technician, View-Only)
- Reset passwords
- Deactivate users

**[TODO: Step-by-step user creation walkthrough]**

### 8.2 Sensor Configuration

**For Admin users only.** Configure sensor thresholds:
- Set alert thresholds (warning/critical levels)
- Link sensors to installations
- Configure polling interval (default: 5 seconds)

**[TODO: Threshold configuration walkthrough]**

### 8.3 Settings & System Configuration

**[TODO: Email notification setup, report templates, etc.]**

---

## 9. Settings & User Preferences

### 9.1 Update Your Profile

**Step 1:** Click your **name** (top right) → **"Settings"**

**Step 2:** Click **"Profile"** tab

**Step 3:** Edit:
- Full name
- Email address (optional; usually not changed)
- Phone number (optional)
- Department / role (informational)

**Step 4:** Click **"Save"**

---

### 9.2 Change Your Password

**Step 1:** Settings → **"Security"** tab

**Step 2:** Click **"Change Password"**

**Step 3:** Enter:
- Current password
- New password (12+ characters, mix of upper/lower/number/special)
- Confirm new password

**Step 4:** Click **"Update Password"**

---

### 9.3 Set Up / Manage Two-Factor Authentication (2FA)

**Step 1:** Settings → **"Security"** tab

**Step 2:** Click **"Set Up 2FA"** (if not already enabled)

**Step 3:** Use an Authenticator app:
- Google Authenticator
- Microsoft Authenticator
- Authy
- (any app supporting TOTP)

**Step 4:** Scan the QR code shown on screen, or manually enter the setup key

**Step 5:** Open your app and enter the 6-digit code

**Step 6:** Click **"Verify"**

**Step 7:** Save recovery codes in a safe place (backup in case you lose your phone)

---

### 9.4 Email Notifications & Report Delivery

**[TODO: Email notification preferences setup pending backend configuration]**

---

## 10. Troubleshooting

### 10.1 Common Issues

#### Q: "I forgot my password. How do I reset it?"

**A:** On the login page, click **"Forgot password?"**
- Enter your email
- Check your inbox for a reset link
- Click the link and set a new password
- If you don't receive an email, check your spam folder or contact support@atlas-forge.dev

---

#### Q: "I can't log in. I keep getting 'Invalid credentials' error."

**A:**
1. Double-check your email and password (case-sensitive)
2. Confirm your account is active (ask admin if you're new)
3. If you've tried >5 times, your account may be locked for 15 minutes
4. Wait 15 min and try again
5. If still failing, contact support: support@atlas-forge.dev

---

#### Q: "The dashboard is loading very slowly."

**A:**
1. Check your internet connection (≥2 Mbps recommended)
2. Try a hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
3. Try a different browser (Chrome, Firefox, Safari)
4. Try accessing from a different device to isolate the issue
5. Check if FireGlass is down: [See status page — link TBD]
6. If persisting, contact support

---

#### Q: "Photos are not uploading in the inspection form."

**A:**
1. Check file size: each photo should be <10 MB
2. Check file format: JPG, PNG, WebP supported (not TIFF, BMP, etc.)
3. Try uploading one photo at a time
4. If offline, photos will be queued; reconnect and click "Sync"
5. Try a different browser or clear browser cache (Ctrl+Shift+Delete)
6. Contact support if problem persists

---

### 10.2 Offline Mode Issues

#### Q: "I'm offline but the app won't let me submit the inspection form."

**A:**
1. Offline inspection forms are saved to your device automatically every 30 seconds
2. You can continue filling out the form offline
3. When you reconnect, a "Sync" button will appear
4. Click "Sync" to upload queued inspections
5. If sync fails, check your internet and try again
6. If you lose the form (cleared cache), contact support to recover from server backup

---

### 10.3 Reporting Bugs

If you encounter a bug:

1. **Screenshot:** Take a screenshot of the error (if visible)
2. **Steps:** Note exactly what you did before the error occurred
3. **Browser info:** Note your browser name and version (Chrome 120, Safari 17, etc.)
4. **Send to support:**
   - Email: support@atlas-forge.dev
   - Subject: "FireGlass Bug Report: [Short description]"
   - Include: screenshots, steps to reproduce, browser info, timestamp

---

## 11. FAQ

### Q: How often are sensor readings updated?

**A:** By default, every 5 seconds. Sensors are polled from the Helion network; readings are stored and displayed in real-time on the dashboard. If you see "3 min ago", the sensor may be offline or not transmitting.

---

### Q: Can I delete an inspection after submitting it?

**A:** No. Submitted inspections are locked and cannot be deleted (for audit trail integrity). If there's an error, add a note to the installation explaining the issue and schedule a new inspection.

---

### Q: How long is sensor data kept?

**A:** 2 years by default. After 2 years, old sensor readings are archived and may not be visible in trend charts. Admin can adjust retention policy.

---

### Q: Can I use FireGlass on my phone while offline?

**A:** Yes! FireGlass PWA (Progressive Web App) works offline:
- Dashboard and installation list load offline (cached data)
- Inspection form can be drafted offline (auto-saves to device)
- When you reconnect, click "Sync" to upload queued inspections
- Note: Real-time sensor updates only work when online

---

### Q: Who can generate reports?

**A:**
- **Admin:** Can generate any report
- **Manager:** Can generate Compliance, Performance, Maintenance reports for all installations
- **Technician:** Can view their own inspection history but cannot generate reports
- **View-Only:** Can view reports shared by managers/admins

---

### Q: How do I know if a sensor is failing?

**A:**
- Red indicator (🔴) or "CRIT" status = sensor reading above critical threshold
- "Offline" status = sensor not sending data (may be unpowered, network issue)
- Check the maintenance notes for the installation (any recent service work?)
- Schedule an inspection to check sensor physical condition

---

## 12. Getting Help

### 12.1 Built-In Help

- Click **"Help"** in the left menu
- Access user guide (PDF), FAQs, and video tutorials
- Report a bug or submit feature request

---

### 12.2 Email Support

**Email:** support@atlas-forge.dev
**Response SLA:** 4 hours during business hours (Mon–Fri, 9 AM–5 PM CET)

When contacting support, include:
- Your name and email
- Installation/sensor ID (if applicable)
- Steps to reproduce the issue
- Browser and device information
- Screenshot (if error visible)

---

### 12.3 Phone Support

**[Number pending — to be filled in during handoff]**

---

## Appendix: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `/` | Open search (dashboard) |
| `?` | Open keyboard shortcut help |
| `Esc` | Close modal or cancel form |
| `Ctrl+S` / `Cmd+S` | Save (if applicable) |
| `Ctrl+P` / `Cmd+P` | Print current page |

---

## Document Status

**Version:** 0.3 (Draft)
**Status:** INCOMPLETE — NOT FOR CLIENT DISTRIBUTION
**Prepared by:** Clara Duval
**Last Updated:** 2025-10-15

**Sections Completed:**
- ✓ Getting Started
- ✓ Dashboard Overview
- ✓ Managing Installations
- ✓ Sensor Monitoring
- ✓ Conducting Inspections
- ✓ Generating Reports (basic)
- ✓ Settings & User Preferences
- ✓ Troubleshooting & FAQ

**Sections Pending (TBD):**
- [ ] Maintenance Scheduling (UI finalization pending)
- [ ] Administration (deferred to post-UAT)
- [ ] Figure 3.2 reference (screenshot of sensor dashboard layout) — **FILE NOT FOUND**

**Known Issues:**
- Navigation path references differ slightly from component-tree.md (e.g., manual says "Settings > User Management" but component tree shows "Administration > User Management" — needs alignment)
- Some UI elements not yet final (fields, buttons, layouts pending UAT feedback)

**Next Steps:**
1. Incorporate UAT feedback from field technicians (Sprint 7)
2. Finalize screenshots and figures
3. Complete deferred sections
4. Full proofread and formatting review
5. Prepare final version for client distribution (post-UAT, week of 2025-11-03)

---

*For questions about this draft, contact Clara Duval (clara@atlas-forge.dev) or Samir Osei (samir@atlas-forge.dev).*
