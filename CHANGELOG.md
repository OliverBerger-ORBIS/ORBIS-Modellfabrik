# Changelog

All notable changes to OSF Dashboard will be documented here.

**Hinweis zur Use-Case-Nummerierung (ab v0.7.11):** Ältere Changelog-Einträge, die „UC-06 Interoperability“ oder „UC-06 (Edge Interoperability)“ erwähnen, beziehen sich auf den Use-Case, der seit v0.7.11 als **UC-00 Interoperability** bezeichnet wird. UC-07 Process Optimization wurde zu UC-06.

## [Unreleased]

## [0.8.2] - 2026-02-26

**Vibrationssensor SW-420 in osf-ui integriert (Sprint 16).**

### Added
- **OSF-Topics:** ConnectionService abonniert `osf/#` für Arduino-Erweiterungen
- **Message Monitor:** Filter „OSF Topics“ für Topics mit Präfix `osf/`
- **Sensor-Tab:** Vibrations-Kachel mit Ampel-Anzeige (Grün/Rot), Impulse-Zähler und Status-Label
- **Mock-Modus:** Buttons „Ruhe senden“ und „Alarm senden“ zum Simulieren von Vibrations-Alarm
- **Fixtures:** sensor-startup und osf-vibration-test Preset mit Vibrations-Nachrichten (connection, state)
- **Replay-Preloads:** JSON-Dateien für `osf/arduino/vibration/sw420-1/connection` und `state` (GRUEN/ROT)
- **package.json:** Script `serve:osf-ui` für `nx run osf-ui:serve`

### Changed
- **Arduino Sketch:** USE_MQTT=1, nicht blockierender MQTT-Reconnect (5s Intervall), High-Level-Relais (Pin 5→Grün, Pin 6→Rot+Sirene)
- **arduino-vibrationssensor.md:** Gekürzt, Verdrahtungs-Tabellen verdichtet, OSF-Topics-Test (Mock/Replay) dokumentiert, Status Mock/Replay positiv getestet

## [0.8.1] - 2026-02-25

**ERP/MES Integration (Sprint 16):** Order-requestId-Erweiterung und Vorbereitung für dsp/correlation (Request/Info).

### Added
- **CCU Order-RequestId:** Order/request und Order/response um optionales `requestId` erweitert – Korrelation von externen Systemen (ERP, MES) mit CCU-Orders
- **OSF-UI Correlation:** `CorrelationInfoService` empfängt `dsp/correlation/info`, speichert nach `ccuOrderId`/`requestId`
- **OSF-UI Request:** `requestCorrelationInfo({ ccuOrderId?, requestId? })` sendet an `dsp/correlation/request` – Vorbereitung für DSP_Edge-Anfragen
- **Order-Card:** Button „Request ERP info“, Anzeige von ERP-Daten (customerOrderId, purchaseOrderId etc.) aus CorrelationInfoService
- **Track & Trace:** ERP-Kontext aus CorrelationInfoService (primär) und ErpOrderDataService (Fallback)
- **CCU Ein-Repo:** Vollständige 24V-Dev-Quelle in `integrations/APS-CCU/` – lokale Entwicklung ohne Pi
- **Test-Scripts:** `correlation_test.py`, `run-correlation-test.sh`, `watch-order-topics.sh` für Replay-Tests

### Changed
- **Order-Tab:** Replay/Live nutzt MessageMonitor für `ccu/order/active` und `ccu/order/completed` (CCU-Snapshot-Semantik wie CCU-Frontend)
- **Dokumentation:** [order-requestid-extension.md](docs/07-analysis/order-requestid-extension.md), [ccu-modification-and-deployment-analysis.md](docs/07-analysis/ccu-modification-and-deployment-analysis.md)

### Fixed
- **correlation_test.py:** `on_message`-Callback zuweisen, `connect_failed`-Event statt `sys.exit` im MQTT-Thread
- **test_order_flow.sh:** Subshell bei `mosquitto_sub` entfernt für korrekte PID-Erfassung

## [0.8.0] - 2026-02-23

**Versionskreis 0.8.x:** Arduino-Erweiterung, ggf. ERP/MES-Integration

### Added
- **Arduino Integration:** Struktur `integrations/Arduino/` für Arduino-Sketches (analog zu TXT-Controller/ROBO Pro)
- **Sketch Vibrationssensor_SW420:** Basis-Programm für SW-420, Relais, 12V-Signalampel
- **Arduino IDE Setup How-To:** [arduino-ide-setup.md](docs/04-howto/setup/arduino-ide-setup.md) – Installation, Sketchbook-Speicherort, Systemtest (Blink)
- **ROBO Pro Setup How-To:** [robo-pro-setup.md](docs/04-howto/setup/robo-pro-setup.md) – Installation für TXT-Controller
- **Hardware-Doku:** [arduino-vibrationssensor.md](docs/05-hardware/arduino-vibrationssensor.md) – Verdrahtung, Aufbau, MPU-6050-Ausblick

### Changed
- **integrations/README.md:** Arduino-Abschnitt ergänzt
- **Vibrationssensor-Projekt:** Vollständiger Sketch in Repo, Verknüpfung Hardware-Doku ↔ integrations/Arduino

## [0.7.11] - 2026-02-21

### Changed
- **Use-Case-Nummerierung:** UC-06 → UC-00 (Interoperability), UC-07 → UC-06 (Process Optimization); alle Referenzen in Code, Doku, Locales und Routing angepasst
- **UC-00 Interoperability (Event-to-Process Map):** Strukturelle Überarbeitung der rechten Spalte
  - Drei Abschnitte mit linksbündigen Überschriften: Process View, Target systems, Use-Cases
  - Outcome-Bereich: 6 Use-Case-Boxen (UC-01 bis UC-06) mit Icon und Titel statt textueller Beschreibung
  - Box-Layout: Titel oben, Icon zentriert darunter; zweizeilige Titel für lange Namen
  - Target-Systeme (ERP, MES, Analytics) in Originalhöhe; Use-Case-Boxen quadratisch/unten positioniert
  - Event-to-Process Timeline: Kreise, Icons und Labels symmetrisch zur Box (gleiche Ränder links/rechts)
- **Dokumentation:** use-case-inventory.md und use-case-library.md nach UC-00, 01 … 06 sortiert
- **UseCaseControlsComponent:** Anzeige von `useCaseCode` und `useCaseTitle` getrennt
- **SVG-Titel:** UC-Code aus SVG-Titeln bei UC-03, UC-04, UC-05, UC-06 entfernt

## [0.7.9] - 2026-02-18

### Added
- **Use-Case SVG Export:** Script `node scripts/export-use-case-svgs.js` exportiert alle Use-Case-Diagramme (UC-01 bis UC-06) nach `assets/svg/use-cases/`
  - Icons (DSP Edge, MILL, DRILL etc.) werden als Base64-Data-URIs eingebettet für standalone-Anzeige (Markdown, file://)
  - CSS-Variablen-Fallbacks für UC-06 (ORBIS-Farben) bei eigenständigem SVG
  - Puppeteer-Chrome erforderlich: `npx puppeteer browsers install chrome` bei Fehlermeldung
- **Use-Case-Bibliothek:** Zentraldokumentation [use-case-library.md](docs/02-architecture/use-case-library.md) (Routing, Dateien, Steps)

### Changed
- **Use-Case-Inventory:** Hinweis auf Puppeteer-Installation, SVG-Export
- **Sprint 15:** Verweis auf Use-Case-Bibliothek, gekürzte UC-Details

## [0.7.8] - 2026-02-18

### Added
- **AIQS Quality-Check (Klassifikation & Beschreibung):** TXT Controller überträgt Qualitätsprüf-Ergebnisse mit Klassifikation (ML-Label, z.B. BOHO, MIPO2, CRACK) und Beschreibung (lesbar, z.B. „2x milled pocket“) via MQTT auf `/j1/txt/1/i/quality_check` – Vorbereitung für Rückmeldung an zentrales QS-System (MES, ERP)
- **OSF Shopfloor-Tab:** Anzeige von Quality Check Ergebnis (passed/failed), Farbe (White/Red/Blue), Klassifikation und Beschreibung in den Device-Details bei AIQS (Bereich „Last Image“)
- **I18n:** Übersetzungen für alle neuen AIQS Quality-Check Labels und Werte in DE und FR
- **Dokumentation:** How-To `aiqs-quality-check-enumeration.md` mit RoboPro-Workflow (Blockly-Modus, keine direkten Python-Änderungen im Repo)

### Changed
- **Locale-Dateien:** AIQS-Übersetzungen in `public/locale/` ergänzt (Runtime-Load)

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
