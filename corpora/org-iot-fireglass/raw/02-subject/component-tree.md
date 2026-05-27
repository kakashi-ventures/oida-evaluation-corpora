# FireGlass Component Tree & Architecture

**Project**: FireGlass (Smart Fire-Resistant Windows Platform)
**Client**: Innovative Windows LLC
**Vendor**: Atlas Forge LLC
**Last Updated**: 2026-03-24
**Tech Lead**: Samir Osei
**Team**: Samir Osei (Tech Lead), Clara Duval (Junior Dev)

---

## 1. Project Structure Overview

FireGlass is built on **Next.js 14 with App Router**, following modern file-based routing conventions. The architecture emphasizes server-side rendering for security-critical dashboard pages, with client-side React Context for authorization state management via CASL.

```
src/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   ├── page.tsx
│   │   │   └── components/
│   │   │       ├── LoginForm.tsx
│   │   │       └── MFASetup.tsx
│   │   ├── signup/
│   │   │   └── page.tsx
│   │   ├── reset-password/
│   │   │   └── page.tsx
│   │   └── layout.tsx              # Auth layout (no sidebar)
│   │
│   ├── (dashboard)/
│   │   ├── layout.tsx              # Protected layout with sidebar + header
│   │   ├── page.tsx                # Dashboard home
│   │   ├── installations/
│   │   │   ├── page.tsx            # List installations
│   │   │   ├── [id]/
│   │   │   │   ├── page.tsx        # Installation detail
│   │   │   │   ├── edit/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── sensors/
│   │   │   │       ├── page.tsx    # Sensors for installation
│   │   │   │       └── [sensorId]/
│   │   │   │           └── page.tsx
│   │   │   └── new/
│   │   │       └── page.tsx        # Create new installation
│   │   │
│   │   ├── sensors/
│   │   │   ├── page.tsx            # Global sensor dashboard
│   │   │   └── [sensorId]/
│   │   │       └── page.tsx        # Sensor detail view
│   │   │
│   │   ├── inspections/
│   │   │   ├── page.tsx            # Inspections list
│   │   │   ├── [id]/
│   │   │   │   ├── page.tsx        # Inspection detail
│   │   │   │   └── edit/
│   │   │   │       └── page.tsx
│   │   │   └── new/
│   │   │       └── page.tsx        # Create inspection
│   │   │
│   │   ├── maintenance/
│   │   │   ├── page.tsx            # Maintenance schedule & logs
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   │
│   │   ├── reports/
│   │   │   ├── page.tsx            # Reports index
│   │   │   ├── sensor-trends/
│   │   │   │   └── page.tsx
│   │   │   ├── compliance/
│   │   │   │   └── page.tsx
│   │   │   └── custom/
│   │   │       └── page.tsx
│   │   │
│   │   └── settings/
│   │       ├── page.tsx            # User settings
│   │       ├── organization/
│   │       │   └── page.tsx
│   │       ├── integrations/
│   │       │   └── page.tsx
│   │       └── audit-log/
│   │           └── page.tsx
│   │
│   ├── api/
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── route.ts
│   │   │   ├── logout/
│   │   │   │   └── route.ts
│   │   │   ├── refresh/
│   │   │   │   └── route.ts
│   │   │   └── mfa/
│   │   │       └── route.ts
│   │   │
│   │   ├── installations/
│   │   │   ├── route.ts            # POST/GET list, POST create
│   │   │   └── [id]/
│   │   │       ├── route.ts        # GET/PUT/DELETE
│   │   │       └── sensors/
│   │   │           └── route.ts
│   │   │
│   │   ├── sensors/
│   │   │   ├── route.ts            # GET list, filter by installation
│   │   │   ├── [id]/
│   │   │   │   └── route.ts        # GET details, historical data
│   │   │   └── realtime/
│   │   │       └── route.ts        # WebSocket upgrade endpoint
│   │   │
│   │   ├── inspections/
│   │   │   ├── route.ts
│   │   │   └── [id]/
│   │   │       └── route.ts
│   │   │
│   │   └── webhooks/
│   │       ├── sensor-alerts/
│   │       │   └── route.ts        # MQTT-triggered alerts
│   │       └── mqtt-data/
│   │           └── route.ts        # HelionLink protocol ingestion
│   │
│   ├── error.tsx                   # Global error boundary
│   ├── not-found.tsx               # 404 handler
│   └── layout.tsx                  # Root layout (providers)
│
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Modal.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Alert.tsx
│   │   ├── Tabs.tsx
│   │   ├── Pagination.tsx
│   │   └── Tooltip.tsx
│   │
│   ├── forms/
│   │   ├── InstallationForm.tsx
│   │   ├── SensorConfigForm.tsx
│   │   ├── InspectionForm.tsx
│   │   ├── InspectionSignatureCanvas.tsx    # TODO: evaluate react-signature-pad-next
│   │   ├── MaintenanceLogForm.tsx
│   │   ├── AlertRulesForm.tsx
│   │   ├── UserInviteForm.tsx
│   │   └── SearchFilterBar.tsx
│   │
│   ├── charts/
│   │   ├── SensorTemperatureChart.tsx
│   │   ├── SensorHumidityChart.tsx
│   │   ├── SensorHeatmap.tsx                # WIP — Clara started, needs Helion firmware docs for color thresholds
│   │   ├── TrendAnalysisChart.tsx
│   │   ├── ComplianceMetricsChart.tsx
│   │   ├── AlertFrequencyChart.tsx
│   │   └── ChartContainer.tsx               # Recharts wrapper with loading states
│   │
│   ├── maps/
│   │   ├── InstallationMap.tsx              # Legacy: keeping MapboxGL integration for now, will migrate to Maplibre in Phase 2
│   │   ├── MultiInstallationMap.tsx
│   │   ├── SensorLocationMarker.tsx
│   │   └── GeoZoneVisualization.tsx
│   │
│   ├── layout/
│   │   ├── DashboardLayout.tsx
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── PageBreadcrumbs.tsx
│   │   └── PermissionBoundary.tsx           # CASL-based component wrapper
│   │
│   └── providers/
│       ├── AuthProvider.tsx
│       ├── CaslProvider.tsx
│       ├── NotificationProvider.tsx
│       └── OfflineSyncProvider.tsx          # Partial implementation — currently only caches inspection forms, not sensor readings
│
├── lib/
│   ├── prisma.ts                   # Prisma client singleton
│   ├── supabase.ts                 # Supabase client (auth + real-time)
│   ├── mqtt.ts                     # MQTT client for HelionLink integration
│   ├── casl/
│   │   ├── ability.ts              # CASL ability definitions
│   │   ├── roles.ts                # Role enum and permission matrix
│   │   └── rules.ts                # CASL rule generators
│   ├── auth/
│   │   ├── jwt.ts
│   │   ├── session.ts
│   │   ├── mfa.ts
│   │   └── rbac.ts                 # Role-based access control helpers
│   ├── api/
│   │   ├── request.ts              # Typed fetch wrapper
│   │   └── types.ts                # API response/request types
│   ├── utils/
│   │   ├── formatters.ts           # Date, temperature, sensor ID formatting
│   │   ├── validators.ts           # Input validation
│   │   ├── errors.ts               # Custom error classes
│   │   └── constants.ts            # App-wide constants
│   └── hooks.ts                    # Exported hook index
│
├── hooks/
│   ├── useAuth.ts                  # Get current user, logout
│   ├── usePermissions.ts           # CASL ability hook
│   ├── useSensorData.ts            # Fetch & cache sensor readings
│   ├── useRealtimeSensor.ts        # Real-time sensor updates (direct MQTT subscription from browser)
│   ├── useInstallationFilters.ts   # Installation list filters + sorting
│   ├── useOfflineSync.ts           # Offline form persistence
│   ├── useAlerts.ts                # Alert subscriptions
│   ├── useNotifications.ts         # Toast/notification system
│   ├── usePaginatedQuery.ts        # Pagination helper
│   └── useDebounce.ts              # Debounce utility
│
├── types/
│   ├── auth.ts                     # User, Role, Session types
│   ├── installation.ts             # Installation, Site types
│   ├── sensor.ts                   # Sensor, SensorReading types
│   ├── inspection.ts               # Inspection, InspectionItem types
│   ├── maintenance.ts              # MaintenanceLog, MaintenancePlan types
│   ├── alert.ts                    # AlertRule, AlertEvent types
│   ├── casl.ts                     # CASL Subject, Action types
│   └── api.ts                      # API request/response envelopes
│
├── styles/
│   ├── globals.css                 # Tailwind directives
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   └── theme/
│       ├── colors.ts               # Theme color palette
│       └── breakpoints.ts          # Responsive breakpoints
│
├── middleware.ts                   # Next.js middleware (auth, redirects)
├── next.config.js                  # Next.js configuration
├── package.json
├── tsconfig.json
├── prisma/
│   └── schema.prisma               # Prisma schema (database models)
└── .env.local                      # Local env (development only)
```

---

## 2. Key Component Details

### Auth Components

#### **LoginForm** (`/components/forms/LoginForm.tsx`)

```typescript
interface LoginFormProps {
  onSubmitSuccess?: () => void;
  redirectTo?: string;
}

interface LoginPayload {
  email: string;
  password: string;
  rememberMe?: boolean;
}
```

**Description**: Handles email/password authentication with optional MFA prompt. Integrates with Supabase Auth and stores JWT in secure httpOnly cookies.

**Dependencies**: `Button`, `Input`, `Alert`, `useAuth` hook, Supabase client

---

#### **MFASetup** (`/components/forms/MFASetup.tsx`)

```typescript
interface MFASetupProps {
  userId: string;
  onComplete: (backupCodes: string[]) => void;
}
```

**Description**: TOTP setup flow with QR code display and backup code generation.

**Dependencies**: `qrcode.react`, `Button`, `Input`, Supabase MFA API

---

### Dashboard Components

#### **DashboardLayout** (`/components/layout/DashboardLayout.tsx`)

```typescript
interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
}
```

**Description**: Main layout wrapper providing sidebar, header, and breadcrumb navigation. Applies CASL ability checks to render/hide sections based on user role.

**Dependencies**: `Sidebar`, `Header`, `PageBreadcrumbs`, `PermissionBoundary`, `useAuth`, `usePermissions`

---

#### **PermissionBoundary** (`/components/layout/PermissionBoundary.tsx`)

```typescript
interface PermissionBoundaryProps {
  action: "read" | "create" | "update" | "delete";
  subject: "Installation" | "Sensor" | "Inspection" | "Maintenance";
  field?: string;                  // For field-level permissions
  children: React.ReactNode;
  fallback?: React.ReactNode;      // Rendered if permission denied
}
```

**Description**: CASL-based component wrapper. Evaluates ability rules and conditionally renders children or fallback. Used to hide UI elements and API access points based on role.

**Dependencies**: `usePermissions` (CASL), `Alert`

---

### Installation Components

#### **InstallationForm** (`/components/forms/InstallationForm.tsx`)

```typescript
interface InstallationFormProps {
  mode: "create" | "edit";
  installationId?: string;
  onSubmitSuccess?: (installation: Installation) => void;
  defaultValues?: Partial<Installation>;
}

interface InstallationPayload {
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  projectManagerId: string;
  siteManagerId: string;
  notes?: string;
  tags?: string[];
  customFields?: Record<string, unknown>;
}
```

**Description**: Dynamic form for creating/editing installations with geolocation picker. Validates address via PostGIS, assigns managers, and persists to PostgreSQL via Prisma.

**Dependencies**: `Input`, `Select`, `Button`, `Alert`, `InstallationMap`, custom API hook

---

#### **InstallationMap** (`/components/maps/InstallationMap.tsx`)

```typescript
interface InstallationMapProps {
  installation: Installation;
  sensors?: Sensor[];
  onLocationChange?: (lat: number, lng: number) => void;
  readOnly?: boolean;
}
```

**Description**: Renders installation location on interactive map with sensor markers. **Legacy: keeping MapboxGL integration for now, will migrate to Maplibre in Phase 2**.

**Dependencies**: `mapbox-gl`, `SensorLocationMarker`

---

### Sensor Components

#### **SensorTemperatureChart** (`/components/charts/SensorTemperatureChart.tsx`)

```typescript
interface SensorTemperatureChartProps {
  sensorId: string;
  timeRange: "1h" | "1d" | "7d" | "30d";
  onDataPointClick?: (reading: SensorReading) => void;
}
```

**Description**: Renders temperature readings from Helion sensor as line chart using Recharts. Auto-refreshes every 30s via `useSensorData` hook.

**Dependencies**: `recharts`, `useSensorData`, `ChartContainer`

---

#### **SensorHeatmap** (`/components/charts/SensorHeatmap.tsx`)

```typescript
interface SensorHeatmapProps {
  installationId: string;
  sensorIds: string[];
  anomalyThreshold?: number;
}
```

**Description**: Visualizes temperature distribution across multiple sensors in grid format with color-coded heat zones. **WIP — Clara started this, needs Helion firmware docs to finalize color thresholds**.

**Dependencies**: `recharts`, `heatmap-js` (pending), Sensor data API

---

#### **SensorHumidityChart** (`/components/charts/SensorHumidityChart.tsx`)

```typescript
interface SensorHumidityChartProps {
  sensorId: string;
  timeRange: "1h" | "1d" | "7d" | "30d";
}
```

**Description**: Bar chart showing humidity levels from Helion sensor. Used for corrosion risk assessment.

**Dependencies**: `recharts`, `useSensorData`

---

### Inspection Components

#### **InspectionForm** (`/components/forms/InspectionForm.tsx`)

```typescript
interface InspectionFormProps {
  mode: "create" | "edit";
  inspectionId?: string;
  installationId: string;
  onSubmitSuccess?: (inspection: Inspection) => void;
}

interface InspectionPayload {
  installationId: string;
  technicianId: string;
  scheduledDate: Date;
  notes: string;
  items: InspectionItem[];
  signatureBlob?: Blob;
  photoPaths?: string[];
}
```

**Description**: Multi-step form for creating inspections with photo uploads, checklist items, and digital signature. Supports offline submission via `useOfflineSync`.

**Dependencies**: `Input`, `InspectionSignatureCanvas`, `Button`, `useOfflineSync`, `Alert`

---

#### **InspectionSignatureCanvas** (`/components/forms/InspectionSignatureCanvas.tsx`)

```typescript
interface InspectionSignatureCanvasProps {
  onSignatureCapture: (signatureBlob: Blob, dataURL: string) => void;
  technicianName: string;
  timestamp?: Date;
}
```

**Description**: HTML5 Canvas-based signature capture with clear/undo controls. Exports signature as PNG blob for Supabase storage.

**Dependencies**: `react-signature-pad-next` (TODO: evaluate if this library is still maintained)

---

### Maintenance Components

#### **MaintenanceLogForm** (`/components/forms/MaintenanceLogForm.tsx`)

```typescript
interface MaintenanceLogFormProps {
  installationId: string;
  onSubmitSuccess?: (log: MaintenanceLog) => void;
}

interface MaintenanceLogPayload {
  installationId: string;
  type: "preventive" | "corrective" | "emergency";
  description: string;
  laborHours: number;
  parts: MaintenancePart[];
  nextDueDate: Date;
  technicianId: string;
}
```

**Description**: Form for logging maintenance activities. Calculates next maintenance due date based on sensor hours and previous history.

**Dependencies**: `Input`, `Select`, `Button`, `useSensorData` (for sensor hours)

---

### Layout Components

#### **Sidebar** (`/components/ui/Sidebar.tsx`)

```typescript
interface SidebarProps {
  collapsed?: boolean;
  onCollapseChange?: (collapsed: boolean) => void;
}
```

**Description**: Collapsible navigation sidebar with role-based menu items. Uses CASL to determine visible sections (Installations, Sensors, Inspections, Maintenance, Reports, Settings).

**Dependencies**: `useAuth`, `usePermissions`, `Link`, `PermissionBoundary`

---

#### **Header** (`/components/layout/Header.tsx`)

```typescript
interface HeaderProps {
  title?: string;
  actions?: React.ReactNode;
  notifications?: Notification[];
}
```

**Description**: Top bar with user profile dropdown, notification bell, and org switcher.

**Dependencies**: `useAuth`, `useNotifications`, `Modal`

---

### Chart/Visualization Components

#### **TrendAnalysisChart** (`/components/charts/TrendAnalysisChart.tsx`)

```typescript
interface TrendAnalysisChartProps {
  sensorIds: string[];
  metric: "temperature" | "humidity" | "co2";
  timeRange: string;
}
```

**Description**: Multi-line chart comparing sensor trends over time. Used in Reports > Sensor Trends dashboard.

**Dependencies**: `recharts`, `useSensorData`

---

#### **ComplianceMetricsChart** (`/components/charts/ComplianceMetricsChart.tsx`)

```typescript
interface ComplianceMetricsChartProps {
  installationId: string;
  startDate: Date;
  endDate: Date;
}
```

**Description**: Donut chart showing compliance status (compliant/at-risk/non-compliant) based on inspection and sensor data.

**Dependencies**: `recharts`, API integration

---

#### **ChartContainer** (`/components/charts/ChartContainer.tsx`)

```typescript
interface ChartContainerProps {
  children: React.ReactNode;
  isLoading?: boolean;
  error?: Error | null;
  onRetry?: () => void;
  title?: string;
  exportable?: boolean;
}
```

**Description**: Wrapper component providing loading states, error fallbacks, and CSV export functionality for charts.

**Dependencies**: `Alert`, `Button`, `Skeleton`

---

---

## 3. State Management Architecture

FireGlass uses a **hybrid approach combining React Context + Server Components**:

### Authentication Context (`AuthProvider`)

```typescript
interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  error: AuthError | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
}
```

**Implementation**: Server-side session validation via middleware; client-side context caches current user and provides login/logout methods.

---

### Authorization Context (`CaslProvider`)

```typescript
interface CaslContextValue {
  ability: Ability;
  can: (action: string, subject: string, field?: string) => boolean;
  cannot: (action: string, subject: string, field?: string) => boolean;
}
```

**Implementation**: Wraps CASL Ability instance. Rules regenerate on user role changes via WebSocket event from Supabase Realtime.

---

### Notification Context (`NotificationProvider`)

```typescript
interface Notification {
  id: string;
  type: "success" | "error" | "info" | "warning";
  message: string;
  duration?: number;
}

interface NotificationContextValue {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, "id">) => void;
  removeNotification: (id: string) => void;
}
```

**Implementation**: Toast notifications for form submissions, API errors, and real-time alerts.

---

### Offline Sync Context (`OfflineSyncProvider`)

```typescript
interface OfflineSyncContextValue {
  pendingChanges: OfflineChange[];
  addPendingChange: (change: OfflineChange) => Promise<void>;
  syncPendingChanges: () => Promise<SyncResult>;
  isSyncing: boolean;
}
```

**Implementation**: LocalStorage-backed queue for inspection forms submitted offline. **Partial implementation — currently only caches inspection forms, not sensor readings**.

---

## 4. Key Custom Hooks

### `useAuth()` (`/hooks/useAuth.ts`)

```typescript
interface UseAuthReturn {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  logout: () => Promise<void>;
}
```

**Description**: Accesses current user from AuthContext. Handles session refresh on mount and token expiry.

---

### `usePermissions()` (`/hooks/usePermissions.ts`)

```typescript
interface UsePermissionsReturn {
  ability: Ability;
  can: (action: Action, subject: Subject, field?: string) => boolean;
  cannot: (action: Action, subject: Subject, field?: string) => boolean;
}
```

**Description**: Provides CASL ability instance for checking permissions in components. Re-evaluates rules when user role changes.

---

### `useSensorData()` (`/hooks/useSensorData.ts`)

```typescript
interface UseSensorDataOptions {
  sensorId: string;
  timeRange?: "1h" | "1d" | "7d" | "30d";
  pollInterval?: number;
  skipIfOffline?: boolean;
}

interface UseSensorDataReturn {
  data: SensorReading[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}
```

**Description**: Fetches sensor readings from PostgreSQL via `/api/sensors/[id]` endpoint. Polls API every 30s by default; caches results in localStorage for offline fallback.

---

### `useRealtimeSensor()` (`/hooks/useRealtimeSensor.ts`)

```typescript
interface UseRealtimeSensorOptions {
  sensorId: string;
  onDataReceived?: (reading: SensorReading) => void;
}

interface UseRealtimeSensorReturn {
  latestReading: SensorReading | null;
  isConnected: boolean;
}
```

**Description**: Establishes real-time WebSocket connection to sensor data stream. **NOTE: This hook implementation uses direct MQTT subscription from the browser, which conflicts with the architecture documentation that specifies WebSocket via Supabase Realtime**. Requires investigation.

---

### `useInstallationFilters()` (`/hooks/useInstallationFilters.ts`)

```typescript
interface InstallationFilters {
  search?: string;
  projectManagerId?: string;
  complianceStatus?: "compliant" | "at-risk" | "non-compliant";
  dateRange?: { start: Date; end: Date };
}

interface UseInstallationFiltersReturn {
  filters: InstallationFilters;
  setFilters: (filters: InstallationFilters) => void;
  installations: Installation[];
  isLoading: boolean;
  total: number;
  page: number;
  setPage: (page: number) => void;
}
```

**Description**: Manages installation list filters, sorting, and pagination. URL-synced via query parameters.

---

### `useOfflineSync()` (`/hooks/useOfflineSync.ts`)

```typescript
interface UseOfflineSyncReturn {
  pendingChanges: OfflineChange[];
  addPendingChange: (change: OfflineChange) => Promise<void>;
  syncPendingChanges: () => Promise<SyncResult>;
  isSyncing: boolean;
  hasOfflineChanges: boolean;
}
```

**Description**: Manages offline inspection form submissions using IndexedDB. On connection restore, syncs pending forms to backend.

---

### `useAlerts()` (`/hooks/useAlerts.ts`)

```typescript
interface UseAlertsReturn {
  alerts: AlertEvent[];
  isLoading: boolean;
  subscribe: (sensorId: string) => void;
  unsubscribe: (sensorId: string) => void;
}
```

**Description**: Subscribes to real-time alert events from Supabase Realtime. Triggers toast notifications on high-temperature or anomaly alerts.

---

### `useNotifications()` (`/hooks/useNotifications.ts`)

```typescript
interface UseNotificationsReturn {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, "id">) => void;
  removeNotification: (id: string) => void;
}
```

**Description**: Toast notification system. Automatically removes notifications after 5s (configurable).

---

### `usePaginatedQuery()` (`/hooks/usePaginatedQuery.ts`)

```typescript
interface UsePaginatedQueryOptions {
  endpoint: string;
  pageSize?: number;
  query?: Record<string, unknown>;
}

interface UsePaginatedQueryReturn<T> {
  data: T[];
  isLoading: boolean;
  page: number;
  totalPages: number;
  hasMore: boolean;
  setPage: (page: number) => void;
}
```

**Description**: Generic pagination wrapper for list endpoints. Caches pages in React Query.

---

---

## 5. Form Architecture

All forms use **React Hook Form + Zod** for validation:

```typescript
// Example: InstallationForm validation schema
const installationSchema = z.object({
  name: z.string().min(3, "Name must be at least 3 characters"),
  address: z.string().min(10),
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  projectManagerId: z.string().uuid(),
  siteManagerId: z.string().uuid(),
  tags: z.array(z.string()).optional(),
});

type InstallationFormData = z.infer<typeof installationSchema>;
```

Forms support **offline-first submission** via `useOfflineSync` when network unavailable.

---

## 6. API Route Structure

All API routes enforce **CASL authorization** at route handler level:

```typescript
// /api/installations/[id]/route.ts (example)
export async function PUT(req: Request, { params }) {
  const user = await getSession();
  const ability = defineAbility(user.role);

  if (!ability.can("update", "Installation")) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  // Update logic...
}
```

**Row-Level Security (RLS)** enforced via Prisma `findFirst` queries filtered by user organization:

```typescript
const installation = await prisma.installation.findFirst({
  where: {
    id: installationId,
    organization: { id: user.organizationId }, // RLS check
  },
});
```

---

## 7. Real-Time Data Flow

**Sensor readings** flow via multiple channels:

1. **MQTT (HelionLink protocol)**: Helion sensors → MQTT broker → `/api/webhooks/mqtt-data` webhook
2. **Supabase Realtime**: Database changes → WebSocket → `useRealtimeSensor` hook
3. **Polling**: `useSensorData` hook polls `/api/sensors/[id]` every 30s for chart updates

**Alert events** trigger via:
- Supabase Edge Function (threshold detection)
- MQTT-to-REST bridge (direct HelionLink integration)
- Notifies users via `useAlerts` hook + toast notifications

---

## 8. Deployment & Build

- **Framework**: Next.js 14 (App Router)
- **Package Manager**: pnpm
- **Build Command**: `pnpm build`
- **Runtime**: Node.js 18+
- **Database**: PostgreSQL (via Prisma)
- **Auth**: Supabase (JWT + Session)
- **Real-time**: Supabase Realtime (WebSocket) + MQTT (Helion)
- **Storage**: Supabase Storage (inspection photos, signatures)
- **CSS**: Tailwind CSS 3.x

---

## 9. Known Issues & TODOs

- `SensorHeatmap`: WIP, needs Helion firmware documentation for color threshold finalization
- `InspectionSignatureCanvas`: Evaluate if `react-signature-pad-next` is still maintained; consider alternatives
- `useRealtimeSensor`: Direct MQTT browser subscription conflicts with architecture spec (should use Supabase Realtime)
- `OfflineSyncProvider`: Partial implementation; only caches inspection forms, not sensor readings
- Maps: Legacy MapboxGL integration; migration to Maplibre planned for Phase 2 (already passed in changelog)

---

## 10. Component Dependencies Summary

| Component | Dependencies | Notes |
|-----------|--------------|-------|
| DashboardLayout | Sidebar, Header, PermissionBoundary, useAuth, usePermissions | Core layout wrapper |
| InstallationForm | Input, Select, Button, InstallationMap, validation | Geolocation integration |
| InspectionForm | InspectionSignatureCanvas, useOfflineSync, Button, Input | Offline-capable |
| SensorTemperatureChart | recharts, useSensorData, ChartContainer | Real-time polling |
| SensorHeatmap | recharts, heatmap-js (pending), Sensor API | WIP — color threshold refinement |
| InspectionSignatureCanvas | react-signature-pad-next, Canvas API | Signature export to PNG |
| PermissionBoundary | usePermissions (CASL), Alert | Authorization wrapper |
| useRealtimeSensor | WebSocket/MQTT client | Conflicts with arch doc |
| OfflineSyncProvider | IndexedDB, localStorage | Partial implementation |

---

**Document Version**: 1.0
**Last Reviewed**: 2026-03-24
**Maintainer**: Samir Osei (Tech Lead)
