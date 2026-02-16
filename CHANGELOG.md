# Changelog

All notable changes to OSF Dashboard will be documented here.

## [Unreleased]

## [0.7.7] - 2026-02-16

### Added
- **Use Case Visualization:** Detail view now links to animated SVG graphics.
- **Navigation:** Accessible via Use-Case in DSP tab or direct link `/#/en/dsp/use-case`.
- **Settings:** Link added in settings page.

## [0.7.6] - 2026-02-04

### Changed
- **DSP Architecture (Functional View):** Refined step visibility and icon positioning for Steps 13-19
  - **Steps 13-18:** SmartFactory (UX) box (`dsp-ux`) is now hidden in steps 13-18, only visible from step 19 onwards
  - **Step 17:** Middle Edge icon (`logo-edge-b`) highlighted with connection to central MC icon; MC function icons visible
  - **Step 18:** All three Edge icons (`logo-edge-a`, `logo-edge-b`, `logo-edge-c`) highlighted with dashed connections between them; MC function icons visible
  - **Step 19:** SmartFactory (UX) box highlighted with connection to Edge; MC container shows only MC function icons (no Edge icons), no connection from Edge to MC
  - **Icon Positioning:** Edge icons positioned in 120° segment (120°, 180°, 240°), MC function icons in separate 120° segment (300°, 0°, 60°) to prevent overlap

## [0.7.5] - 2026-02-04

### Changed
- **DSP Architecture (Functional View):** SmartFactory Dashboard step moved to the end (now after Edge Node Visualization Complete); SmartFactory (UX) box is visible starting from step 19.
- **DSP Architecture (Component View):** Business Process layer connections now point to the DSP Edge box (instead of DISC).

### Added
- **DSP Architecture:** Info toggle (ℹ) to show/hide step title + description overlay.

## [0.7.4] - 2026-01-16

### Added
- **UC-06 (Edge Interoperability):** Added `edge-interoperability` icon as part of Use Case 06 implementation.

### Changed
- **Documentation:** Updated `dsp-svg-inventory.md` and refreshed the full inventory.

## [0.6.0] - 2025-12-22

### Added
- **Module Hardware Configuration (Task 16):** Integration of OMF2 module hardware configuration into OSF
  - **ModuleHardwareService:** New service to load and provide hardware configuration (OPC-UA servers, TXT controllers)
  - **modules_hardware.json:** Hardware configuration file with OMF2-derived data (English as default language)
  - **Configuration Tab Enhancements:**
    - Separate sections for OPC-UA Server and TXT 4.0 Controller details
    - Large icons for OPC-UA Server and TXT Controller (66% of station icon size)
    - Sections only displayed when hardware is present
    - TXT Controller IP addresses marked as DHCP (dynamically assigned)
  - **Icons:** New SVG icons for OPC-UA Server (`opc-ua-server.svg`) and TXT Controller (`txt-controller.svg`)
  - **i18n:** German and French translations for hardware configuration labels
  - **Tests:** Complete test suite for `ModuleHardwareService`, Configuration Tab tests extended

### Changed
- **hardware-architecture.md:** Updated with reference to `modules_hardware.json` and OSF integration
- **PROJECT_STATUS.md:** Task 16 marked as completed

### Removed
- **OMF2 Analysis Documents:** Removed temporary analysis documents (`OMF2_MODULE_CONFIGURATION_ANALYSIS.md`, `OMF2_MODULE_CONFIGURATION_ANALYSIS_UPDATE.md`, `OMF2_MODULE_CONFIGURATION_INTEGRATION_PLAN.md`) - information now consolidated in `hardware-architecture.md`

## [0.5.2] - 2025-12-20

### Changed
- **OSF Rebranding (Task 13):** Complete rebranding from OMF3 to OSF
  - **App Renaming:** `ccu-ui` → `osf-ui` (directory, project.json, scripts, CI/CD)
  - **Workspace Renaming:** `omf3/` → `osf/` (directory, Nx scope, TypeScript paths)
  - **Component Renaming:** `module-tab` → `shopfloor-tab` (files, class, selector, route, CSS classes, storage keys)
  - **Component Renaming:** `fts-tab` → `agv-tab` (files, class, services, route; FTS remains in MQTT topics and German translations)
  - **Package Name:** `omf3-workspace` → `osf-workspace`
  - **Documentation:** Updated project structure, architecture docs, and main README files
  - **Routes:** All `/module` routes changed to `/shopfloor`, DSP architecture component URLs updated
  - **Table Header:** Shopfloor tab table header changed back to "Modules" (tab name remains "Shopfloor" for DSP connection)

## [0.5.1] - 2025-12-20

### Removed
- **Overview-Tab:** Completely removed as all features have been migrated to Process-Tab and Module-Tab (Shopfloor)
  - Purchase Orders and Customer Orders → Process-Tab
  - HBW Inventory Grid → Module-Tab (HBW Stock Grid)
  - OrdersViewComponent and AgvViewComponent removed (never functional)
- **Fixtures:** Removed `overview-startup` and `overview-active` presets from tab-fixtures.ts
- Overview-Tab route removed from navigation and routing

### Changed
- **Process-Tab:** Fixtures updated from `overview-*` to `process-startup` and `order-*` presets
- **Default Route:** Changed from `overview` to `dsp` (localhost:4200/#/en/dsp)
- **Browser Tab:** Title updated from "OSF-apps-ccu-ui" to "OSF Dashboard", favicon set to `orbis-dsp-logo.svg`
- **Version Display:** Moved from Footer to Sidebar, now shows "OSF Dashboard v0.5.1" with proper spacing
- **Language Service:** Default route fallback changed from `'overview'` to `'dsp'`

## [0.5.0] - 2025-12-20

### Added
- Windows helper scripts for npm/Node.js setup (run-omf3.ps1, run-omf3.bat, add-node-to-user-path.ps1)
- Comprehensive npm/Node.js setup documentation (docs_orbis/how-to-use-npm.md) for Windows developers
- Scripts handle common Windows issues: PATH problems, missing npx, automatic dependency installation
- Module sequence commands feature for DRILL, MILL, and AIQS modules
- Manual sequence command execution with individual send buttons (PICK, DRILL/MILL/CHECK_QUALITY, DROP)
- Developer mode for sequence commands showing sent payloads with formatted JSON
- Reset button to clear sent commands for repeated testing
- Sequence command files (DRILL-Sequence.json, MILL-Sequence.json, AIQS-Sequence.json) with real-life payload structure
- Tests for sequence command loading, sending, tracking, and reset functionality
- **Track-Trace Enhancements:**
  - TURN LEFT/RIGHT Icons: FTS TURN Events show specific icons based on direction (from FTS Order Stream)
  - Order Status: Active/Completed status from `ccu/order/active` and `ccu/order/completed` streams
  - ERP Data Integration: `ErpOrderDataService` links Purchase/Customer Orders from Process-Tab to Track-Trace Order Context
  - Additional Date Fields: Event analysis extracts specific dates (Raw Material Order Date, Delivery Date, Storage Date, Customer Order Date, Production Start Date, Delivery End Date)
  - I18n: All new data fields with English defaults and DE/FR translations
- **Process-Tab:**
  - ERP-Info-Box component for Purchase/Customer Orders
  - Accordion structure with "Beschaffungs-Prozess" (Purchase Orders + Storage Flow) and "Produktions-Prozess" (Customer Orders + Production Flow)
- **Shopfloor/Module-Tab:**
  - Enhanced module highlighting (selected module with blue border, non-selected with background color only)
  - HBW Stock-Grid optimization (square boxes, label overlay, full width utilization)
  - Module status extension for all modules (DPS/AIQS/HBW/DRILL/MILL) with unified structure
  - Tab renamed to "Shopfloor" and moved to position 2 in navigation
- **Orders-Tab:**
  - Layout reversed (Shopfloor left 3fr, Steps right 2fr) with responsive breakpoint at 1200px
  - Shopfloor-Preview in OrderCards
  - Finished list collapsed by default, Storage Orders auto-expand
  - Tab moved to position 4 in navigation
- **Configuration-Tab:**
  - CSS Grid layout (Shopfloor left, Module right, responsive breakpoints)
- **DSP Architecture:**
  - Edge Animation sequence refined (MC functions → EDGE xyz_2 link → xyz_1/3 added → all three dashed highlight)
- Tests for `ErpOrderDataService` and extended tests for `WorkpieceHistoryService`
- OSF Rebranding Plan document (`docs/PLAN_OSF_REBRANDING.md`)

### Changed
- Sequence command payloads now match real-life structure:
  - Added timestamp field (dynamically set on send)
  - Removed priority and timeout from metadata
  - Added workpieceId to metadata (14-character hex format)
  - Metadata now only contains type and workpieceId
- Track-Trace component: Enhanced with ERP data integration, order status, and additional date fields
- Shopfloor-Preview: Canvas size increased by 5px padding on all sides to prevent highlight clipping
- Module-Tab: Renamed to "Shopfloor" in UI/Navigation, moved to position 2
- Process-Tab: Moved to position 3 in navigation
- Orders-Tab: Moved to position 4 in navigation

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
