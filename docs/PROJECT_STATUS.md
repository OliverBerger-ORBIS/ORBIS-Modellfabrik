# ORBIS Modellfabrik - Projekt Status

**Letzte Aktualisierung:** 16.10.2025  
**Aktueller Status:** OMF2 Migration abgeschlossen, Messe-Vorbereitung läuft

> **Dokumentations-Strategie:** Dieses Dokument ist die zentrale Quelle für alle Projekt-Änderungen und Status-Updates. Keine separate CHANGELOG.md - alles hier!

## 🚀 Aktuelle Arbeiten

### ✅ **OMF2 Migration abgeschlossen** (16.10.2025)
- **Drei-Schichten-Architektur** - Vollständig implementiert und getestet ✅
- **Registry Manager** - Zentrale Konfiguration für alle Schemas und Templates ✅
- **Gateway-Routing-Pattern** - Schema-Validierung und Topic-Routing ✅
- **Business Manager** - ModuleManager, WorkpieceManager, SensorManager, OrderManager ✅
- **Production Order Manager** - Vollständige Order-Lifecycle-Verwaltung ✅
- **Storage Orders Logic** - PICK/DROP → LADEN/ENTLADEN AGV Logik ✅
- **i18n-System** - DE/EN/FR Support mit 195+ Translation Keys ✅
- **Best Practice Logging** - Multi-Level Ringbuffer mit UI-Integration ✅
- **Tests** - Alle Tests bestehen ✅
- **Status:** OMF2 ist produktionsreif und demo-fähig ✅

### 🎯 **Messe-Vorbereitung läuft** (bis 25.11.2025)
- **Factory Layout** - 3×4 Grid mit echten omf_* SVG-Icons (teilweise implementiert)
- **Auto-Refresh** - MQTT-Trigger für UI-Refresh (geplant)
- **Sensor Data UI** - Temperatur-Skala, Kamera-Controls (geplant)
- **HTML-Templates i18n** - Workpiece-Box übersetzen (geplant)
- **Live-Test Sessions** - 4 Sessions mit echter Fabrik (geplant)
- **Status:** Auf Kurs für Messe-Demo am 25.11.2025 🎯

### ✅ **Mermaid Diagramm-System optimiert** (20.09.2025)
- **Hybrid-Ansatz** implementiert: zentrale vs. dezentrale Diagramme
- **`docs/_shared/diagrams/`** als zentrale Bibliothek für wiederverwendbare Architektur-Diagramme
- **Build-System** mit `npm run diagrams` für automatische SVG-Generierung
- **Kontext-spezifische Diagramme** bleiben bei entsprechenden Dokumenten
- **Obsolet `docs/diagrams/`** entfernt - nutzt jetzt vorhandene `_shared/` Infrastruktur
- **Cross-Platform Testing** erfolgreich - Windows + VSCode getestet

## 📋 Aktuelle Entwicklungsphase

### **Phase 2: OMF2-Architektur (ABGESCHLOSSEN)**
- ✅ **OMF2 Migration vollständig abgeschlossen** (16.10.2025)
- ✅ **Drei-Schichten-Architektur implementiert** - MQTT Client → Gateway → Business Manager
- ✅ **Registry Manager** - Zentrale Konfiguration für alle Schemas und Templates
- ✅ **Gateway-Routing-Pattern** - Schema-Validierung und Topic-Routing
- ✅ **Business Manager** - ModuleManager, WorkpieceManager, SensorManager, OrderManager
- ✅ **Production Order Manager** - Vollständige Order-Lifecycle-Verwaltung
- ✅ **Storage Orders Logic** - PICK/DROP → LADEN/ENTLADEN AGV Logik
- ✅ **i18n-System** - DE/EN/FR Support mit 195+ Translation Keys
- ✅ **Best Practice Logging** - Multi-Level Ringbuffer mit UI-Integration
- ✅ **Tests** - 341/341 Tests bestehen

### **Phase 3: Messe-Vorbereitung (AKTUELL)**
- 🎯 **Factory Layout** - 3×4 Grid mit echten omf_* SVG-Icons (teilweise implementiert)
- 🎯 **Auto-Refresh** - MQTT-Trigger für UI-Refresh (geplant)
- 🎯 **Sensor Data UI** - Temperatur-Skala, Kamera-Controls (geplant)
- 🎯 **HTML-Templates i18n** - Workpiece-Box übersetzen (geplant)
- 🎯 **Live-Test Sessions** - 4 Sessions mit echter Fabrik (geplant)
- **Ziel:** Demo-fähig bis 25.11.2025

> **📋 Detail-Planung:** Siehe [plan.md](../plan.md) für konkrete Tasks und ToDos



## 📋 Nächste Schritte

### **🎯 Messe-Vorbereitung (Priorität 1)**
- **Factory Layout** - 3×4 Grid mit echten omf_* SVG-Icons vervollständigen
- **Auto-Refresh** - MQTT-Trigger für UI-Refresh implementieren
- **Sensor Data UI** - Temperatur-Skala, Kamera-Controls verbessern
- **HTML-Templates i18n** - Workpiece-Box übersetzen (DE/EN/FR)
- **Live-Test Sessions** - 4 Sessions mit echter Fabrik durchführen

### **🔧 Technische Verbesserungen (Priorität 2)**
- **Template-Analyzer reparieren** - Topics aus Template-Deskriptionen entfernen
- **Cross-Platform Testing** - Windows + VSCode für Mermaid
- **Weitere Architektur-Diagramme** - Message-Flow, Registry-Model

### **🔍 Integration & Analyse (Priorität 3)**
- **APS-CCU tiefere Analyse** - Central Control Unit: Docker-Container analysieren
- **TXT-Controller Analyse** - AIQS, DPS, FTS Funktionsanalyse
- **Rollenbasierte Tab-Sichtbarkeit** - Operator/Supervisor/Admin Rollen implementieren

## ✅ **Abgeschlossene Arbeiten**

### **Phase 1: APS "as IS" - Fischertechnik-System verstehen** ✅
- ✅ **APS-Ecosystem dokumentiert** - System-Übersicht, Komponenten-Mapping
- ✅ **Mosquitto Log-Analyse** - MQTT-Kommunikation, Client-IDs, Topics
- ✅ **APS-NodeRED Flows analysiert** - OPC-UA, State-Machine, VDA 5050
- ✅ **APS-CCU als Herz der Fabrik identifiziert**

### **Phase 2: OMF2-Architektur** ✅
- ✅ **Drei-Schichten-Architektur** vollständig implementiert
- ✅ **Registry Manager** zentrale Konfiguration für alle Schemas
- ✅ **Gateway-Routing-Pattern** Schema-Validierung und Topic-Routing
- ✅ **Business Manager** ModuleManager, WorkpieceManager, SensorManager, OrderManager
- ✅ **Production Order Manager** vollständige Order-Lifecycle-Verwaltung
- ✅ **Storage Orders Logic** PICK/DROP → LADEN/ENTLADEN AGV Logik
- ✅ **i18n-System** DE/EN/FR Support mit 195+ Translation Keys
- ✅ **Best Practice Logging** Multi-Level Ringbuffer mit UI-Integration
- ✅ **Tests** Alle Tests bestehen

### **Dokumentation & Architektur** ✅
- ✅ **Sprint-Dokumentation** erstellen (sprint_01 bis sprint_06)
- ✅ **Mermaid Diagramm-System** - Hybrid-Ansatz mit `docs/_shared/diagrams/`
- ✅ **Pre-commit und Git/GitHub Workflow** - Projekt-spezifische Hooks
- ✅ **Registry-Konsolidierung** - Alle Legacy-Konfigurationen zu Registry migriert

## 📊 Sprint-Vorgehen

### **Sprint-Strategie:**
- **2-Wochen-Zyklen** für kontinuierliche Entwicklung
- **PROJECT_STATUS.md** = Zentrale Change-Dokumentation
- **Sprint-Dokumentation** = Detaillierte Rückblicke in `docs/sprints/`
- **Keine CHANGELOG.md** = Redundanz vermeiden

### **Change-Management:**
- **Alle Änderungen** werden hier dokumentiert
- **Sprint-Status** wird kontinuierlich aktualisiert
- **Wichtige Entscheidungen** in `docs/03-decision-records/`

### **🔧 TECHNISCHE PRIORITÄTEN (Sprint 07):**
- **Factory Layout** - 3×4 Grid mit echten omf_* SVG-Icons
- **Auto-Refresh** - MQTT-Trigger für UI-Refresh implementieren
- **Sensor Data UI** - Temperatur-Skala, Kamera-Controls verbessern
- **HTML-Templates i18n** - Workpiece-Box übersetzen (DE/EN/FR)
- **Live-Test Session #1** - Mit echter Fabrik durchführen

### **🌐 ZUKUNFTSPLANUNG:**
- **Messe-Vorbereitung** - Factory Layout, Auto-Refresh, Sensor Data UI, Live-Test Sessions
- **Post-Messe Erweiterungen** - APS-NodeRED Funktionalität, DSP-Anbindung, ORBIS Cloud
- **Weitere Architektur-Diagramme** - Message-Flow, Registry-Model (bereits implementiert)

## 📊 Sprint-Status

### Sprint 07 (16.10 - 29.10.2025) - **AKTUELL**
- **Status:** In Bearbeitung
- **Fokus:** Messe-Vorbereitung und UI-Polish
- **Geplant:** Factory Layout, Auto-Refresh, Sensor Data UI, HTML-Templates i18n, Live-Test Sessions
- **Nächste Schritte:** Factory Layout Icons, Auto-Refresh Implementation, Live-Test Session #1

### Sprint 06 (02.10 - 15.10.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** OMF2-Refactoring und Architektur-Migration
- **Erreicht:** Drei-Schichten-Architektur, Registry Manager, Gateway-Routing, Business Manager, Production Order Manager, Storage Orders Logic, i18n-System, Best Practice Logging, 341/341 Tests
- **Meilenstein:** OMF2 ist produktionsreif und demo-fähig ✅

### Sprint 05 (18.09 - 01.10.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Component-Strukturierung und User-Konzept Vorbereitung
- **Erreicht:** APS Dashboard vollständig in OMF-Dashboard integriert, Component-Bereinigung abgeschlossen
- **Nächste Schritte:** User-Konzept umsetzen (Rollenbasierte Tab-Sichtbarkeit), Sprint-Dokumentation

### Sprint 04 (04.09 - 17.09.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** OMF-Architektur, Singleton Pattern, Registry Support
- **Erreicht:** FTS-Steuerung, Pub-Sub Analyse, Client-ID Zuordnung, Node-RED Analyse

### Sprint 03 (23.08 - 03.09.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Tiefe Analyse, Template Analyser, Session Analyse
- **Erreicht:** Topics-Verständnis, Registry-Aufbau

### Sprint 02 (07.08 - 22.08.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Einfaches OMF-Dashboard, Nachrichten-Zentrale
- **Erreicht:** Overview über Modul-Status, erste Commands

### Sprint 01 (24.07 - 06.08.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Verstehen des APS-Systems, Helper-Apps
- **Erreicht:** Session Manager, MQTT-Aufnahme, Themenbezogene Sessions

## 🎯 Wichtige Doings

### **Entscheidungen getroffen:**
- **Drei-Schichten-Architektur** MQTT Client → Gateway → Business Manager
- **Registry Manager** zentrale Konfiguration für alle Schemas und Templates
- **Gateway-Routing-Pattern** Schema-Validierung und Topic-Routing
- **Message Processing Pattern** standardisierte Message-Verarbeitung
- **i18n-Architektur** Lazy Loading, Session State Integration, 3 Sprachen
- **Best Practice Logging** Multi-Level Ringbuffer mit Thread-Safety
- **UI-Refresh-Pattern** request_refresh() statt st.rerun()
- **Asymmetrische Architektur** Commands über NodeRed, Telemetry direct

### **Technische Meilensteine:**
- **OMF2-Architektur** vollständig implementiert (Drei-Schichten-Architektur)
- **Registry Manager** zentrale Konfiguration für alle Schemas und Templates
- **Gateway-Routing-Pattern** Schema-Validierung und Topic-Routing
- **Business Manager** ModuleManager, WorkpieceManager, SensorManager, OrderManager
- **Production Order Manager** vollständige Order-Lifecycle-Verwaltung
- **Storage Orders Logic** PICK/DROP → LADEN/ENTLADEN AGV Logik
- **i18n-System** DE/EN/FR Support mit 195+ Translation Keys
- **Best Practice Logging** Multi-Level Ringbuffer mit UI-Integration
- **Tests** 341/341 Tests bestehen
- **Dokumentations-Restrukturierung** Legacy vs. Implementierte Dokumente getrennt


## 🔗 Wichtige Links

- **Aktuelle Sprint-Dokumentation:** `docs/sprints/`
- **Decision Records:** `docs/03-decision-records/`
- **Architektur:** `docs/02-architecture/`
- **APS-Analyse:** `docs/06-integrations/mosquitto/`
- **APS Dashboard Integration Status:** `docs/07-analysis/aps-dashboard-integration-status.md`
- **APS Overview Implementation Status:** `docs/07-analysis/aps-overview-implementation-complete.md`

---

**Status:** OMF2 Migration abgeschlossen, Messe-Vorbereitung läuft erfolgreich 🎯
