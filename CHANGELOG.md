# Changelog

All notable changes to OMF3 Dashboard will be documented here.

## [Unreleased]

### Added
- Windows helper scripts for npm/Node.js setup (run-omf3.ps1, run-omf3.bat, add-node-to-user-path.ps1)
- Comprehensive npm/Node.js setup documentation (docs_orbis/how-to-use-npm.md) for Windows developers
- Scripts handle common Windows issues: PATH problems, missing npx, automatic dependency installation

### Added
- Module sequence commands feature for DRILL, MILL, and AIQS modules
- Manual sequence command execution with individual send buttons (PICK, DRILL/MILL/CHECK_QUALITY, DROP)
- Developer mode for sequence commands showing sent payloads with formatted JSON
- Reset button to clear sent commands for repeated testing
- Sequence command files (DRILL-Sequence.json, MILL-Sequence.json, AIQS-Sequence.json) with real-life payload structure
- Tests for sequence command loading, sending, tracking, and reset functionality

### Changed
- Sequence command payloads now match real-life structure:
  - Added timestamp field (dynamically set on send)
  - Removed priority and timeout from metadata
  - Added workpieceId to metadata (14-character hex format)
  - Metadata now only contains type and workpieceId

## [0.4.0] - 2025-12-16

### Added
- ECME (European Company Manufacturing Everything) customer configuration
- New SVG icons for devices: CNC, Hydraulic, 3D Printer, Weight, Laser
- New SVG icons for systems: SCADA, Industrial Process, Cargo, Pump
- Comprehensive HOWTO guide for adding new customer configurations (`HOWTO_ADD_CUSTOMER.md`)
- Tests for label wrapping functionality in sf-devices and sf-systems boxes
- Semver versioning documentation (Decision Record + HowTo)
- I18n translations for new device and system labels (DE/FR)

### Changed
- Renamed customer DEF to ECME (European Company Manufacturing Everything)
- Updated icon registry with new device and system icons
- Enhanced label wrapping logic to handle break hints correctly

### Fixed
- Label wrapping now correctly removes break hints when label fits on one line
- Label wrapping adds hyphens correctly when wrapping occurs

## [0.3.0] - 2025-12-14

### Added
- Phase 1: Test coverage increased from 29% to 60%
- Phase 2: DSP Architecture config refactoring (-33% code)
- Builder Pattern for diagram configs
- Helper functions for container/connection IDs

### Changed
- Consolidated DSP architecture configurations
- Removed legacy dsp-architecture.config.ts (946 lines)

## [0.2.0] - 2025-11-10

### Added
- DSP Architecture Animation with 3 views (Functional, Component, Deployment)
- Shopfloor Preview Component
- MQTT-based real-time updates

## [0.1.0] - 2025-08-14

### Added
- Initial OMF3 Dashboard release
- Angular 18 application
- MQTT Client integration
- Order Management tabs
