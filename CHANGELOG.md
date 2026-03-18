# Changelog

All notable changes to OSF Dashboard will be documented here.

**Hinweis zur Use-Case-Nummerierung (ab v0.7.11):** Ältere Changelog-Einträge, die „UC-06 Interoperability“ oder „UC-06 (Edge Interoperability)“ erwähnen, beziehen sich auf den Use-Case, der seit v0.7.11 als **UC-00 Interoperability** bezeichnet wird. UC-07 Process Optimization wurde zu UC-06.

## [Unreleased]

## [0.9.8] - 2026-03-19

### Fixed
- **Revert v0.9.7:** FTS-Layer wieder im Canvas – v0.9.7 (Layer außerhalb) führte zu komplett weißem Shopfloor auf localhost. Zurück zum funktionierenden Stand (Layer in Canvas, z-index 100, filter).

## [0.9.7] - 2026-03-19 (REVERTED)

### Fixed (reverted – brach localhost)
- FTS-Layer außerhalb Canvas – führte zu weißem Shopfloor.

## [0.9.6] - 2026-03-19

### Fixed
- **AGV-Tab / RPi-Rendering:** `box-shadow` statt `filter: drop-shadow` auf `.preview__fts` – filter erzeugt Stacking Context, verursacht RPi/localhost-Unterschiede. Box-shadow nicht.

## [0.9.5] - 2026-03-19

### Fixed
- **AGV-Tab / RPi-Rendering:** `transform: translateZ(0)` auf `.preview__fts-layer` – erzwingt eigene Compositor-Layer; Adresse für localhost-ok/RPi-nok bei gleichem Safari/Mac.

## [0.9.4] - 2026-03-19

### Fixed
- **AGV-Tab / RPi-Rendering:** `isolation: isolate` auf `.preview__fts-layer` – stabilisiert das AGV-Overlay über verschiedene Browser/Plattformen (localhost vs. RPi 192.168.0.100).

## [0.9.3] - 2026-03-18

**AGV-Overlay Z-Index, Shopfloor Layout Höhennutzung, AIQS DSP Action**

### Fixed
- **AGV-Tab:** AGV-Icon überdeckt wieder Modul- und Intersection-SVGs (z.B. HBW). Regression seit 2-AGV-Unterstützung behoben durch dedizierten `.preview__fts-layer` (z-index: 100).
- **Shopfloor Layout / Module-Tab:** Rechte Modul-Info-Spalte nutzt verfügbare Höhe; keine unnötige Scrollbar mehr, wenn unterhalb noch Platz ist. Grid `align-items: stretch`, `max-height` entfernt.

### Added
- **AIQS DSP Action:** Topic `dsp/aiqs/action` (changeLight/changeColor) in AIQS-Detail-Section – Current/Previous Farbanzeige und Developer-Bereich (letzte 2 Nachrichten). Analog zu DRILL.
- **Fixtures:** `aiqs-action` Fixture und `createAiqsActionFixtureStream()` für Mock-Tests.
- **Tests:** `getAiqsActionData()` Unit-Tests.

## [0.9.1] - 2026-03-17

**RPi Kiosk-Modus, Lager-Anzeige bei geleertem Storage**

### Added
- **RPi Kiosk-Modus:** OSF startet direkt im Live-Modus, wenn von der Live-Broker-Adresse (192.168.0.100) ausgeliefert – kein manueller Environment-Wechsel mehr nötig.
- **Lager-Anzeige ohne Persistence:** Sync aus MessageMonitor-History beim Init; Polling für spät eintreffende Stock-Nachrichten (z. B. retained nach Storage-Leerung). HbwStockGrid und Process-Tab zeigen Lager auch bei leerem Local Storage.

### Changed
- **EnvironmentService:** `loadInitialEnvironment()` prüft `window.location.hostname === live.mqttHost` → Default `live` statt `mock`.

## [0.9.0] - 2026-03-17

**Minor: Shopfloor Live-Modus Fix, Lager-Anzeige, Tab Stream Pattern, Build-Warnings**

### Fixed
- **Shopfloor Tab (Live-Modus):** Module zeigten alle „Disconnected“, obwohl CCU/APS lief – Root Cause: `getDashboardController()` ohne Argumente löste fälschlich „Switch to Mock“ aus und zerstörte MQTT-Controller. Fix: Bedingung auf expliziten Mock-Switch eingeschränkt (`messageMonitor !== undefined`).
- **Lager-/Inventory-Anzeige (Live-Modus):** Lager erschien leer trotz eingehender `ccu/state/stock`-Nachrichten. Fix: Gateway und ConnectionService unterstützen beide Stock-Topics (`ccu/state/stock`, `/j1/txt/1/f/i/stock`); Process-Tab und HbwStockGrid nutzen Dashboard-Getter statt gecachter Referenz.
- **Build-Warnungen:** track-trace SCSS-Budget, ajv CommonJS, fehlende i18n-Übersetzungen (agvTabSelectLabel, uc05LiveDemoSirenToggleLabel, moduleNameAGV, fixtureLabelStorageBlueAgv2/Parallel) behoben.

### Added
- **Regressions-Tests:** `getDashboardController` mode-switching – Mock/Replay darf Live-Modus nicht mehr brechen. Tests in `mock-dashboard.spec.ts`.
- **resetDashboardControllerForTesting()** – für Test-Isolation bei getDashboardController-Tests.

### Changed
- **Tab Stream Pattern (DR 11):** Live-Priorität dokumentiert; Stock-Topics (CCU vs. Fischertechnik Legacy); Dashboard-Getter-Regel für Pattern-2-Komponenten; Beide Stock-Topics in Process-Tab und HbwStockGrid.
- **Shopfloor-Tab:** Nutzt `this.dashboard.streams` (Tab-Stream-Pattern).

## [0.8.13] - 2026-03-16

**Sensor-Tab Erweiterung, Arduino MultiSensor R4, Gas MQ-2**

### Added
- **Sensor-Tab:** Flame (Gefahr in % mit Farbverlauf grün→gelb→rot), SW-420 (grün/rot Rechtecke), MPU-6050 (Gauge Magnitude 0–35k), Gas MQ-2 (neue Kachel, Gefahrenbalken)
- **Arduino MultiSensor R4 WiFi:** Sketch `OSF_MultiSensor_R4WiFi` – MPU-6050, SW-420, Flammensensor, MQ-2 Gas (Topics `osf/arduino/...`)
- **Fixtures:** sensor-startup mit Arduino-Idle, Gas in Arduino-Presets (idle/warning/alarm)
- **Doku:** [arduino-r4-multisensor-verdrahtung.md](docs/05-hardware/arduino-r4-multisensor-verdrahtung.md) – Breadboard-Verdrahtung R4 + alle Sensoren

### Fixed
- **Mock-Dashboard:** MessageMonitor/Arduino-Controller bei Wechsel zu Mock korrekt neu initialisieren (Fixtures erscheinen in Sensor-Kacheln)

## [0.8.12] - 2026-03-13

**AGV-Tab NAV-Buttons, Analyse-Doku**

### Added
- **AGV-Tab Commands:** Drei NAV-Buttons – DPS → HBW, AIQS → HBW, → Intersection 2 (ersetzen alte „Drive to Intersection 2“-Buttons)
- **Konditionale Buttons:** DPS → HBW nur aktiv wenn AGV am DPS; AIQS → HBW nur bei AIQS; → Intersection 2 nur bei bekannter Position + vorhandenem Pfad
- **Analyse-Doku:** [fts-navigation-how-it-works-2026-03.md](docs/07-analysis/fts-navigation-how-it-works-2026-03.md) – Wie funktioniert FTS-Navigation, Topics, Payloads
- **Analyse-Skript:** `scripts/analyze_session_fts_positions.py` – Single-Order-Filter (`--single-only`), HBW-Position, `at_hbw`/`single_order` im Report
- **E2E-Task Sprint 17:** NAV-Buttons AGV-Tab (Live-Modus) testen

### Changed
- **AGV-Tab:** Verwendet `selectedAgvSerial` für alle Commands (AGV-2-Auswahl nutzt korrekte Serial, kein festes 5iO4)

## [0.8.11] - 2026-03-10

**UC-05 Live Demo, Park-Button, I18n**

### Added
- **UC-05 Live Demo:** Tabs Konzept | Live Demo; Toggle „Auto-park on vibration alarm“; Vibration RED → Park + Cancel (ENQUEUED)
- **Park-Button im Header:** Neben Reset, sendet `ccu/set/park` (analog Fischertechnik-UI)
- **I18n DE/FR:** headerParkButton, uc05TabConcept, uc05TabLiveDemo, uc05LiveDemoTitle/Desc/Toggle/Steps/Hint/Feedback

### Changed
- **E2E-Task:** UC-05 Live-Demo testen (Toggle → Order → Vibration → Orders-Tab); Abhängigkeit Arduino-Sensor

## [0.8.10] - 2026-03-13

**Shopfloor Tab, Production Flow, CI/CD, SSH-Setup**

### Added
- **Production Flow auf GitHub Pages:** Fixtures in github-pages Build; Deploy nutzt github-pages Config; Process-Tab zeigt BLUE/WHITE/RED korrekt
- **CI workflow_dispatch:** Manueller CI-Start möglich
- **.github/README.md:** Aktualisiert mit aktuellen Workflows (ci, deploy, pull-request, release)

### Changed
- **Shopfloor Tab:** Dock- und Charge-Buttons für AGVs nur wenn `connected` (analog Original ff UI Modules-Tab)
- **Workflows:** Node 22, FORCE_JAVASCRIPT_ACTIONS_TO_NODE24; Codecov continue-on-error
- **Deploy:** github-pages Config statt production; Fixtures an Root für Mock/Process-Tab

### Fixed
- **CI-Trigger:** Push von Mac triggert CI (SSH github.com-orbis für OliverBerger-ORBIS)
- **Node-Deprecation:** Opt-in Node 24 für Actions

## [0.8.9] - 2026-03-12

**Order-Tab Highlight, AGV-Farben, DR-24**

### Added
- **DR-24:** [Shopfloor-Highlight-Farben](docs/03-decision-records/24-shopfloor-highlight-colors.md) – Order-Tab Grün (aktiver Schritt), AGV-1/2-Farben im AGV-Tab und Presentation-Tab
- **Presentation-Tab:** Doku ergänzt – AGV-1 orange, AGV-2 gelb (nutzt AGV-Tab mit presentationMode)

### Changed
- **Order-Tab:** Aktives Modul (z.B. HBW bei PROCESS-Step) in ORBIS-Highlight-Grün statt Blau – konsistent mit FTS auf Route
- **Shopfloor-Preview:** Neuer Input `highlightStyle: 'selection' | 'active-step'`; Order-Card übergibt `'active-step'`
- **AGV-Farben:** Festlegung „nur AGV-Tab“ → „AGV-Tab und Presentation-Tab“ (second-agv-2026-03.md, color-palette.ts)

### Fixed
- Semantische Einheit „aktiver Schritt“ im Order-Tab: FTS und Modul beide grün

## [0.8.8] - 2026-03-11

**Version Single Source of Truth, Workflow-Aufräumung**

### Changed
- **Versionierung:** Ein Befehl `npm run version:bump -- X.Y.Z` – package.json bleibt Source of Truth
- **Workflows:** Deploy bei jedem main-Push; obsolete Workflows entfernt (Heading Icons, Struktur, Shopfloor-Check)
- **VERSIONING.md:** Klarere Doku; .cursorrules ergänzt

## [0.8.7] - 2026-03-10

**AGV-2 Farbkorrektur (LogiMAT-Vorbereitung)**

### Fixed
- **AGV-2 Farbe:** CSS override entfernt – AGV-2 (jp93) zeigt nun Gelb statt Orange im Shopfloor-Preview
- **AGV-Hervorhebung:** Schatten, Glow und gestrichelter Ring AGV-spezifisch (AGV-1 orange, AGV-2 gelb)

## [0.8.6] - 2026-03-09

**Arduino MPU-6050, Relais vereinheitlicht, timestamp analog Fischertechnik**

### Added
- **Arduino MPU-6050:** Vibrationssensor mit I2C, 3-Stufen-Ampel (Grün/Gelb/Rot+Sirene), NTP für ISO-8601-timestamp
- **Schritt-für-Schritt SW-420 (§1.1):** Verdrahtungsanleitung analog MPU §5.3.1, einheitliche Relais-Logik
- **Preloads MPU-6050:** osf_arduino_vibration_mpu6050-1_* (state, connection, yellow, red)
- **Sprint 17:** Arduino-Tasks erledigt, E2E-Test Vibrationssensor als Task ergänzt

### Changed
- **Relais aktiv-niedrig (einheitlich):** SW-420 und MPU-6050 nutzen gleiche Logik (LOW = ein), Sketch SW-420 angepasst
- **Feldname timestamp:** `ts` → `timestamp` in state-Payload (analog Fischertechnik/DSP), keine Rückwärtskompat
- **DR-18, Doku:** state-Payload mit timestamp, NTPClient (nicht NTPClient_Generic)
- **Fixtures/Preloads:** timestamp statt ts in allen OSF-Arduino-Vibration-Payloads

### Fixed
- **Doku Relais:** SW-420 war fälschlich aktiv-high dokumentiert, vereinheitlicht

## [0.8.5] - 2026-03-03

**Vibrationssensor SW-420: Live-Hardware, semantische Payload, Will-Message**

### Added
- **MQTT-Auth:** Arduino-Sketch nutzt Credentials (default/default) für APS-Broker
- **Will-Message:** connectionState OFFLINE bei ungraceful disconnect – wie Fischertechnik-Module
- **Connection-Payload:** connectionState ONLINE/OFFLINE, ip, serialNumber (Fischertechnik-konform)
- **Troubleshooting:** [arduino-vibrationssensor.md](docs/05-hardware/arduino-vibrationssensor.md) §4.1 – Schicht-für-Schicht Debug (LAN → Broker → mosquitto_sub mit Auth → Arduino-Connect)

### Changed
- **State-Payload:** `ampel` → `vibrationDetected` (boolean) – SW-420-Sensorsignal direkt, OSF-UI mappt auf Ampel-Darstellung
- **OSF-UI:** vibrationLevel/vibrationStatus aus vibrationDetected; Legacy ampel für Session-Replay
- **Mock-Buttons:** „Send idle“ / „Send alarm“ → injectVibrationState(false/true)
- **Preloads/Fixtures:** vibrationDetected, connectionState-Format

### Fixed
- **Live-Hardware:** Roundtrip Arduino→Broker→OSF-UI erfolgreich (MQTT-Auth war Ursache)

## [0.8.4] - 2026-02-18

**Deployment-Dokumentation und Session Recorder qos/retain**

### Added
- **ADR 19:** [OSF-UI Deployment-Strategie](docs/03-decision-records/19-osf-ui-deployment-strategy.md) – Deployment-Ziele (lokal, GitHub Pages, Docker/RPi), Betriebsmodi pro Ziel, ein Build für alle
- **Session Recorder v1.2:** Speichert `qos` und `retain` in `.log`-Dateien für retain-Verifizierung
- **Replay Station:** Liest qos/retain aus Log-Sessions, übergibt an Replay-Controller
- **Analyse-Script:** `scripts/analyze_retain_in_logs.py` für Logs mit qos/retain-Feldern
- **Fischertechnik-Tiefenanalyse:** [FISCHERTECHNIK-VS-OSF-UI-STARTUP-AND-DATA.md](docs/07-analysis/FISCHERTECHNIK-VS-OSF-UI-STARTUP-AND-DATA.md) – App-Start, Datenspeicherung, Topics
- **Tests:** Roundtrip `save_log_session`/`load_log_session` mit qos/retain

### Changed
- **Deployment-Doku:** `deployment-alternatives.md` entfernt, Verweis auf ADR 19 in github-pages-deployment.md
- **session-log-analyse.md:** Session Recorder v1.2 dokumentiert, Option A–D neu nummeriert, Analyse-Script erwähnt
- **AS-IS-FISCHERTECHNIK-COMPARISON:** Session-Log-Analyse-Status aktualisiert (v1.2, analyze_retain_in_logs.py)
- **Sprint 16:** Wiring abgehakt, Tiefenanalyse Fischertechnik ergänzt, Session-Log-Kontext präzisiert
- **A1-DE / uc-00-interoperability:** Templates/Connectoren-Aspekt ergänzt

## [0.8.3] - 2026-02-18

**I18n-Übersetzungsqualität und Duplikat-Behebung**

### Changed
- **Übersetzungen DE:** „Nein Auftrag“ → „Kein Auftrag“, „Befehl History“ → „Befehlsverlauf“, Anglizismen bereinigt; Platzhalter für moduleTab*CommandHistory, overviewCurrentStock, trackTraceWorkpiecesTitle ergänzt; AI-Lifecycle-Texte ins Deutsche übersetzt
- **Übersetzungen FR:** „Commande History“ → „Historique des commandes“, messageMonitorSubheading übersetzt; AI-Lifecycle-Texte ins Französische (IA-konsistent); trackTraceWorkpiecesTitle mit Zähler-Placeholder
- **Übersetzung EN:** navSensor „Environment Data“ → „Environmental Data“
- **I18n-Duplikate behoben:** Eindeutige IDs für ftsStatusLabel/Driving, dpsLabelNfcCode/NfcCodeWorkpieceId, dpsLabelHistory/HistoryWithCount, aiqsLabelHistory/HistoryWithCount, dspActionFixtureLabel/TabButtonLabel
- **Ungenutzte I18n-Keys entfernt:** uc00.note.connector, uc02.note.connector (nach connectorNote-Entfernung aus UC-Diagrammen)

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
