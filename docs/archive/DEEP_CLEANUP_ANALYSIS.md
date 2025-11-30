# Tiefe Dokumentations-Cleanup Analyse

**Datum:** 2025-11-13  
**Zweck:** Vollständige Analyse aller .md Dateien und Quellen auf OMF2/Streamlit-Bezug und Veraltung

## 🔄 UI-/Integration-Aufgabenstatus (Stand 2025-11-22)

| # | Aufgabe | Status | Notizen |
|---|---------|--------|---------|
| 1 | Publish-Buttons, Topics & Payloads mit OMF2 abgeglichen (inkl. Tests & Assert-Review) | ✅ erledigt | Buttons publizieren korrekt, Assertions überprüft |
| 2 | Tests für `resetFactory(withStorage)` (Default `false`) ergänzen | ⛔ offen | Testfälle fehlen noch |
| 3 | Kamera-Steuerung (SVG-Buttons, Stop, `home`, Step-Size-Parameter, Layout, Photo entfernt) | ✅ erledigt | Umsetzung live |
| 4 | I18n/Terminologie (AGV statt FTS, HBW-Text, „Finished“-Button, Produktfarben) | ✅ erledigt | Übersetzungen aktualisiert |
| 5 | Publish-/Camera-Testsuite (bereits umgesetzt, nicht rückgängig zu machen) | ✅ erledigt | Läuft in CI |
| 6 | Chrome‑Mac Live-Verbindungsanalyse (Vergleich `v0.3.0-pre-cleanup`, Diagnostic-Tool, GitHub-Summary) | ❓ offen | Ursache weiter untersuchen, Logging ggf. ausbauen |
| 7 | Tabs (Configuration, Sensor, Process etc.) auf Overview-Caching-Pattern bringen, alle Topics unabhängig vom Tab-Status anzeigen | ❓ offen (**Top-Priorität**) | Orders & Overview fertig, restliche Tabs nachziehen, Fixtures „Startup“ prüfen |
| 8 | Message-Monitor-Filter (Safari, AGV-Auswahl) | ✅ erledigt | Filter-UI konsistent |
| 9 | Faktenblätter ohne „NodeRed“ für Module-Status nutzen | ✅ erledigt | Gateway-/Tab-Logik angepasst |
|10 | Stock-Anzeige bleibt nach Tab-/Language-Wechsel stabil | ✅ erledigt | Inventory-State-Service aktiv |
|11 | Mock-/Live-/Replay-Controller-Benennung & -Verwendung klären | ❓ offen | Benennung/Doku abstimmen |
|12 | Orders-Tab-Icons, Workpiece-Darstellung & Zoom-Controls | ✅ erledigt | UI entspricht Spezifikation |

**Aktuelle Priorität:** Aufgabe 7 – sämtliche übrigen Tabs (außer Orders) auf das Persistenzmuster aus dem Overview-Tab (Pattern 2 + Cache-Service) umstellen und sicherstellen, dass alle Topics auch ohne aktiven Tab angezeigt werden.

## 📋 Analyse-Methodik

1. **Alle .md Dateien** im Projekt durchsucht
2. **OMF2/Streamlit-Bezug** geprüft (grep nach `omf2|OMF2|streamlit|Streamlit|st\.|request_refresh`)
3. **Relevanz für OMF3** bewertet
4. **Veraltung** identifiziert

## 🗂️ Kategorisierung

### ❌ **LÖSCHEN - OMF2/Streamlit-spezifisch, nicht relevant für OMF3**

#### **docs/02-architecture/**
- `implementation-status.md` - OMF2 Implementation Status (veraltet)
- `implementation/ccu-module-manager.md` - OMF2 CCU Module Manager (Python)
- `implementation/module-state-manager.md` - OMF2 Module State Manager (Python)
- `implementation/monitor-manager.md` - OMF2 Monitor Manager (Python)

#### **docs/04-howto/**
- `UI_DEVELOPMENT_GUIDE.md` - OMF2 UI Development Guide (Streamlit-spezifisch, `st.`, `render_*_tab()`)
- `ASSET_MANAGEMENT_REFACTORING.md` - OMF2 Asset Management Refactoring Plan
- `SHOPFLOOR_LAYOUT_GUIDE.md` - OMF2 Shopfloor Layout System (Python, Streamlit)
- `ui_symbols.md` - OMF2 UI Symbols (Streamlit-spezifisch)
- `logging-implementation-guide.md` - OMF2 Logging System (Python)
- `validate-and-release.md` - OMF2 Release-Prozess (veraltet)

#### **docs/07-analysis/**
- `aps-dashboard-tabs-analysis/` (gesamtes Verzeichnis) - OMF2 APS Dashboard Tabs Analyse
  - `README.md`
  - `implementation-roadmap.md`
  - `tab-01-overview.md`
  - `tab-02-orders.md`
  - `tab-03-processes.md`
  - `tab-04-configuration.md`
  - `tab-05-modules.md`
- `aps-overview-implementation-complete.md` - OMF2 APS Overview Implementation
- `PRODUCTION_ORDER_MANAGER_IMPLEMENTATION.md` - OMF2 Production Order Manager
- `PRODUCTION_ORDER_MANAGER_QUICK_REFERENCE.md` - OMF2 Quick Reference
- `ORDER_MANAGER_BLOCKING_PROBLEM.md` - OMF2 Order Manager Problem
- `SESSION_MANAGER_MIGRATION_ANALYSIS.md` - OMF2 Session Manager Migration
- `SESSION_MANAGER_MIGRATION_COMPLETE.md` - OMF2 Migration Complete
- `SESSION_MANAGER_MIGRATION_STATUS.md` - OMF2 Migration Status
- `SHOPFLOOR_LAYOUT_HIGHLIGHTING_STATUS.md` - OMF2 Shopfloor Highlighting
- `SVG_ICON_MAPPING_GUIDE.md` - OMF2 SVG Icon Mapping
- `SYMBOL_IMPLEMENTATION_GUIDE.md` - OMF2 Symbol Implementation
- `UI_SYMBOL_STYLE_GUIDE.md` - OMF2 UI Symbol Style
- `CCU_DOMAIN_SYMBOL_GUIDELINES.md` - OMF2 CCU Domain Symbols
- `MIGRATION_TO_SVG_RENDERING_PLAN.md` - OMF2 SVG Rendering Plan
- `LOG_DISPLAY_IMPROVEMENTS.md` - OMF2 Log Display
- `TODO_COMMENT_GUIDELINES.md` - OMF2 TODO Guidelines (veraltet)
- `CONSOLIDATION_COMPLETE.md` - OMF2 Consolidation (veraltet)
- `DOCUMENTATION_CORRECTIONS_APPLIED.md` - OMF2 Documentation Corrections (veraltet)
- `DOCUMENTATION_REVIEW_INTEGRATION_DOCS.md` - OMF2 Review (veraltet)

#### **Root-Verzeichnis**
- `plan.md` - OMF2 Messe-Vorbereitung Plan (vollständig OMF2-spezifisch, veraltet)

### ✅ **BEHALTEN - Noch relevant für Referenz**

#### **docs/07-analysis/** (8 Dateien - bleiben wo sie sind)
- `ccu-backend-mqtt-orchestration.md` - ✅ **BEHALTEN** - CCU Backend MQTT Referenz
- `registry-mosquitto-log-analysis.md` - ✅ **BEHALTEN** - Registry/Mosquitto Analyse Referenz
- `registry-missing-topics-proposals.md` - ✅ **BEHALTEN** - Registry Topics Proposals Referenz
- `REGISTRY_TOPIC_STRUCTURE.md` - ✅ **BEHALTEN** - Registry Topic Structure Referenz
- `TOPIC_SCHEMA_CORRELATION.md` - ✅ **BEHALTEN** - Topic Schema Correlation Referenz
- `topic-naming-convention-analysis.md` - ✅ **BEHALTEN** - Topic Naming Analysis Referenz
- `production-order-analysis-results.md` - ✅ **BEHALTEN** - Production Order Analysis Referenz
- `sensor-data-integration-complete.md` - ✅ **BEHALTEN** - Sensor Data Integration Referenz

### ✅ **BEHALTEN - Noch relevant oder OMF3-spezifisch**

#### **docs/02-architecture/**
- `omf2-architecture.md` - ✅ **BEHALTEN** - Bis OMF3-Architektur vollständig dokumentiert ist
- `omf2-registry-system.md` - ✅ **BEHALTEN** - Bis OMF3-Architektur vollständig dokumentiert ist
- `aps-data-flow.md` - APS Data Flow (allgemein relevant)
- `message-processing-pattern.md` - Message Processing Pattern (allgemein relevant)
- `message-sending-architecture.md` - Message Sending Architecture (allgemein relevant)
- `multiple_client_per_role.md` - Multiple Client Pattern (allgemein relevant)
- `naming-conventions.md` - Naming Conventions (allgemein relevant)
- `project-structure.md` - Project Structure (bereits auf OMF3 aktualisiert)

#### **docs/04-howto/**
- `mqtt_client_connection.md` - MQTT Client Connection (allgemein relevant)
- `agent-onboarding-architecture.md` - Agent Onboarding (allgemein relevant)
- `integrate-copilot-fix-branches.md` - Copilot Integration (allgemein relevant)
- `setup/` - Setup Guides (allgemein relevant)
- `helper_apps/session-manager/` - Session Manager (noch aktiv)
- `testing/` - Testing Guides (allgemein relevant)
- `troubleshooting/` - Troubleshooting (allgemein relevant)
- `development/` - Development Guides (allgemein relevant)
- `diagrams/` - Diagram Guides (allgemein relevant)

#### **docs/06-integrations/**
- Alle Dateien behalten (APS-Referenz-Dokumentation, noch relevant)

#### **docs/03-decision-records/**
- Alle Dateien behalten (OMF3 Decision Records)

#### **docs/sprints/**
- Alle Dateien behalten (historisch relevant, Sprint-Dokumentation)

## 📊 Zusammenfassung

| Kategorie | Anzahl | Aktion |
|-----------|--------|--------|
| **Löschen** | ~33 Dateien | ❌ Löschen |
| **Behalten** | ~110+ Dateien | ✅ Behalten |

## 🎯 Empfohlene Aktionen

### 1. **Löschen (33 Dateien)**

#### **docs/02-architecture/** (4 Dateien)
- `implementation-status.md`
- `implementation/ccu-module-manager.md`
- `implementation/module-state-manager.md`
- `implementation/monitor-manager.md`

#### **docs/04-howto/** (6 Dateien)
- `UI_DEVELOPMENT_GUIDE.md`
- `ASSET_MANAGEMENT_REFACTORING.md`
- `SHOPFLOOR_LAYOUT_GUIDE.md`
- `ui_symbols.md`
- `logging-implementation-guide.md`
- `validate-and-release.md`

#### **docs/07-analysis/** (22 Dateien)
- `aps-dashboard-tabs-analysis/` (gesamtes Verzeichnis, 7 Dateien)
- `aps-overview-implementation-complete.md`
- `PRODUCTION_ORDER_MANAGER_IMPLEMENTATION.md`
- `PRODUCTION_ORDER_MANAGER_QUICK_REFERENCE.md`
- `ORDER_MANAGER_BLOCKING_PROBLEM.md`
- `SESSION_MANAGER_MIGRATION_ANALYSIS.md`
- `SESSION_MANAGER_MIGRATION_COMPLETE.md`
- `SESSION_MANAGER_MIGRATION_STATUS.md`
- `SHOPFLOOR_LAYOUT_HIGHLIGHTING_STATUS.md`
- `SVG_ICON_MAPPING_GUIDE.md`
- `SYMBOL_IMPLEMENTATION_GUIDE.md`
- `UI_SYMBOL_STYLE_GUIDE.md`
- `CCU_DOMAIN_SYMBOL_GUIDELINES.md`
- `MIGRATION_TO_SVG_RENDERING_PLAN.md`
- `LOG_DISPLAY_IMPROVEMENTS.md`
- `TODO_COMMENT_GUIDELINES.md`
- `CONSOLIDATION_COMPLETE.md`
- `DOCUMENTATION_CORRECTIONS_APPLIED.md`
- `DOCUMENTATION_REVIEW_INTEGRATION_DOCS.md`

#### **Root-Verzeichnis** (1 Datei)
- `plan.md`

### 2. **Verzeichnisse aufräumen**
- `docs/02-architecture/implementation/` - löschen (wenn leer)
- `docs/07-analysis/aps-dashboard-tabs-analysis/` - löschen (wenn leer)

## ⚠️ **WICHTIGE HINWEISE**

1. **OMF2 Code bleibt:** `omf2/*` wird nicht gelöscht, nur Dokumentation
2. **OMF2 Architektur-Docs bleiben:** `omf2-architecture.md` und `omf2-registry-system.md` bleiben bis OMF3-Architektur vollständig dokumentiert ist
3. **Analysis-Docs bleiben:** Registry/Topic-Analysen in `docs/07-analysis/` bleiben als Referenz
4. **Session Manager bleibt:** `docs/04-howto/helper_apps/session-manager/` bleibt (noch aktiv)
5. **APS-Referenz bleibt:** `docs/06-integrations/` bleibt (noch relevant)
6. **Sprint-Dokumentation bleibt:** `docs/sprints/` bleibt (historisch relevant)

## 📝 **Nächste Schritte**

1. ✅ Analyse abgeschlossen
2. ⏳ User-Freigabe für Löschung/Archivierung
3. ⏳ Cleanup durchführen
4. ⏳ README.md aktualisieren (falls nötig)

