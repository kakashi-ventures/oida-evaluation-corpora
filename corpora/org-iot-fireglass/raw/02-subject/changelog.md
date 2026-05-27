# Changelog

All notable changes to FireGlass will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en.1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-21

### Added
- Initial project kickoff and repository setup
- Core authentication system with JWT tokens
- User role-based access control (Admin, Technician, Manager)
- PostgreSQL database schema for installations and inspections

## [0.2.0] - 2025-07-28

### Added
- Installation CRUD endpoints (Create, Read, Update, Delete)
- Basic UI scaffolding for installation management dashboard
- Inspection workflow core logic
- Initial checklist engine framework

### Changed
- Restructured API routes for better modularity

## [0.3.0] - 2025-08-04

### Added
- Map visualization component using Leaflet.js
- Installation geolocation features
- Checklist item templates for standard fire-resistant window inspections
- PDF generation for inspection reports

### Fixed
- Memory leak in form state management

## [0.4.0] - 2025-08-10

### Added
- Email notification system for inspection scheduling
- Internationalization (i18n) support for Italian and English
- Translation files for core UI elements
- User preference settings for language and timezone

### Changed
- Improved inspection workflow UI with step indicators
- Enhanced PDF report formatting with branded headers

## [0.5.0] - 2025-08-18

### Added
- Sensor dashboard (initial implementation)
- Real-time data display for temperature and resistance readings
- HelionLink MQTT broker connection module

### Changed
- Installation map now shows sensor status indicators
- Database schema extended for sensor metadata storage

### Fixed
- Corrected timezone offset calculations in event logging

## [0.6.0] - 2025-08-24

### Added
- HelionLink integration layer for MQTT pub/sub operations
- Helion sensor pairing workflow
- Initial sensor health monitoring dashboard

### Changed
- Refactored auth middleware. Again.
- Improved error handling in installation creation flow

## [0.7.0] - 2025-08-31

### Added
- Sensor data validation pipeline
- Checklist completion tracking with timestamps
- Bulk inspection operations for multi-site deployments

### Fixed
- Race condition in sensor data aggregation that was causing stale readings

## [0.8.0] - 2025-09-05

### Changed
- MQTT message retry logic (attempting to work around Helion firmware limitations)
- Increased connection timeout thresholds for HelionLink communication

### Known Issues
- Helion firmware documentation remains incomplete; some sensor models returning unexpected data formats

## [0.9.0] - 2025-09-12

### Added
- Advanced filtering options in installation list view
- Sensor anomaly detection heuristics
- Inspection history timeline view

### Fixed
- Database query N+1 problem in inspection report generation

## [0.9.1] - 2025-09-16

### Changed
- Optimized PDF generation performance
- Consolidated i18n JSON files for faster bundle load times

## [0.9.2] - 2025-09-21

### Added
- Email template customization for different inspection types
- Sensor calibration tracking per Helion unit

### Fixed
- Finally fixed the cursed race condition in sensor polling — was a stale closure in the useEffect cleanup that was causing phantom data points to appear in the dashboard

## [0.10.0] - 2025-09-27

### Added
- Checklist archival system for completed inspections
- Sensor batch import feature for initial installation setup

### Changed
- Improved map clustering behavior at high zoom levels
- User authentication now includes activity logging

## [0.10.1] - 2025-10-01

### Fixed
- Missing error boundary in sensor dashboard preventing full page crashes
- Authentication token refresh not properly clearing old sessions

## [0.10.2] - 2025-10-05

### Added
- Support for multiple sensor types in dashboard configuration
- Inspection notes with rich text formatting

### Changed
- HelionLink MQTT topic structure to better align with Helion data schema (partial support pending firmware updates)

## [0.10.3] - 2025-10-09

### Fixed
- Typos in Italian translation files for installation status messages

### Removed
- [REVERTED] Experimental real-time sensor sync feature that introduced race conditions between local and remote state

## [0.11.0] - 2025-10-13

### Added
- Inspection workflow approval step for managers
- Export checklist data to CSV format
- Retry mechanism for failed email notifications

### Changed
- Consolidated HelionLink connection pooling to reduce memory overhead
- Improved sensor dashboard responsiveness on mobile devices

### Fixed
- Sensor data occasionally appearing out of chronological order due to MQTT message ordering assumptions

---

**Dataset License**: CC BY 4.0  
**Generated**: 2026-03-24  
**Project**: FireGlass CRM/IoT Platform  
**Organization**: Innovative Windows LLC (Atlas Forge LLC)