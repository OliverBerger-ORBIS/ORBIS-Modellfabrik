# ORBIS Modellfabrik - Projekt Status

**Letzte Aktualisierung:** 13.11.2025  
**Aktueller Status:** OMF3 Entwicklung läuft, OMF2 als Legacy markiert

> **Dokumentations-Strategie:** Dieses Dokument ist die zentrale Quelle für alle Projekt-Änderungen und Status-Updates. Keine separate CHANGELOG.md - alles hier!

## 🚀 Aktuelle Arbeiten

### ✅ **OMF3 Entwicklung läuft** (seit 06.11.2025)
- **Angular + Nx Workspace** - Moderne Frontend-Architektur ✅
- **MQTT-Client Library** - WebSocket MQTT Adapter + Mock Adapter ✅
- **Gateway Library** - Topic→Entity Mapping mit Schema-Validierung ✅
- **Business Library** - RxJS Streams für Dashboard-Daten ✅
- **Entities Library** - TypeScript Types und JSON Parser ✅
- **CCU-UI Dashboard** - Tabbed Shell mit i18n Foundation ✅
- **MessageMonitorService** - State Persistence für MQTT Messages ✅
- **I18n Runtime Switching** - URL-basierte Locale-Routing (EN/DE/FR) ✅
- **CI/CD Umstellung** - GitHub Actions auf OMF3 Tests umgestellt ✅
- **Status:** OMF3 ist produktionsreif und demo-fähig ✅

### 🎯 **Messe-Vorbereitung läuft** (bis 26.11.2025)
- **Messevorbereitung** - Unterbau, Marketing-Banner, Aufbau/Abbau-Test (in Arbeit)
- **Messe in Mulhouse** - 24-26.11.2025 (geplant)
- **Status:** Auf Kurs für Messe-Demo am 24-26.11.2025 🎯

## 📋 Aktuelle Entwicklungsphase

### **Phase 3: OMF3-Entwicklung (AKTUELL)**
- ✅ **Angular + Nx Workspace** - Moderne Frontend-Architektur etabliert
- ✅ **MQTT-Client Library** - WebSocket + Mock Adapter implementiert
- ✅ **Gateway Library** - Topic→Entity Mapping mit Schema-Validierung
- ✅ **Business Library** - RxJS Streams für Dashboard-Daten
- ✅ **Entities Library** - TypeScript Types und JSON Parser
- ✅ **CCU-UI Dashboard** - Tabbed Shell mit i18n Foundation
- ✅ **MessageMonitorService** - State Persistence (BehaviorSubject + CircularBuffer)
- ✅ **I18n Runtime Switching** - URL-basierte Locale-Routing (EN/DE/FR)
- ✅ **CI/CD Umstellung** - GitHub Actions auf OMF3 Tests umgestellt
- ✅ **Tab Stream Pattern** - Konsistente Dateninitialisierung dokumentiert und getestet
- ✅ **Message Monitor Tab** - UI mit Filtering, JSON Syntax Highlighting
- ✅ **Shopfloor-Highlighting** - Orange Highlighting für aktive Routes und FTS
- ✅ **MQTT-Verbindungsstatus** - Visuelle Status-Anzeige in Sidebar und Header

### **Phase 2: OMF2-Architektur (ABGESCHLOSSEN - Legacy)**
- ✅ **OMF2 Migration vollständig abgeschlossen** (16.10.2025)
- ✅ **Drei-Schichten-Architektur implementiert** - MQTT Client → Gateway → Business Manager
- ✅ **Registry Manager** - Zentrale Konfiguration für alle Schemas und Templates
- ✅ **Gateway-Routing-Pattern** - Schema-Validierung und Topic-Routing
- ✅ **Business Manager** - ModuleManager, WorkpieceManager, SensorManager, OrderManager
- ✅ **Order Manager** - Vollständige Order-Lifecycle-Verwaltung
- ✅ **Storage Orders Logic** - PICK/DROP → LADEN/ENTLADEN AGV Logik
- ✅ **i18n-System** - DE/EN/FR Support mit 195+ Translation Keys
- ✅ **Best Practice Logging** - Multi-Level Ringbuffer mit UI-Integration
- ✅ **Tests** - 341/341 Tests bestehen
- **Status:** OMF2 ist produktionsreif, wird durch OMF3 ersetzt (Legacy)

## 📋 Nächste Schritte

### **🎯 Messe-Vorbereitung (Priorität 1)**
- **Messevorbereitung** - Unterbau erstellen, Marketing-Banner, Aufbau/Abbau-Test
- **Messe in Mulhouse** - 24-26.11.2025 - Live-Demonstration des OMF3 Dashboards

### **🔧 Technische Verbesserungen (Priorität 2)**
- **Auto-Refresh** - MQTT-Trigger für UI-Refresh (falls benötigt)
- **Sensor Data UI** - Temperatur-Skala, Kamera-Controls verbessern
- **Live-Test Sessions** - Mit echter Fabrik durchführen

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

### **Phase 2: OMF2-Architektur** ✅ (Legacy)
- ✅ **Drei-Schichten-Architektur** vollständig implementiert
- ✅ **Registry Manager** zentrale Konfiguration für alle Schemas
- ✅ **Gateway-Routing-Pattern** Schema-Validierung und Topic-Routing
- ✅ **Business Manager** ModuleManager, WorkpieceManager, SensorManager, OrderManager
- ✅ **Order Manager** vollständige Order-Lifecycle-Verwaltung
- ✅ **Storage Orders Logic** PICK/DROP → LADEN/ENTLADEN AGV Logik
- ✅ **i18n-System** DE/EN/FR Support mit 195+ Translation Keys
- ✅ **Best Practice Logging** Multi-Level Ringbuffer mit UI-Integration
- ✅ **Tests** Alle Tests bestehen
- **Status:** OMF2 ist produktionsreif, wird durch OMF3 ersetzt (Legacy)

### **Phase 3: OMF3-Entwicklung** ✅ (Aktuell)
- ✅ **Angular + Nx Workspace** - Moderne Frontend-Architektur
- ✅ **MQTT-Client Library** - WebSocket + Mock Adapter
- ✅ **Gateway Library** - Topic→Entity Mapping
- ✅ **Business Library** - RxJS Streams
- ✅ **Entities Library** - TypeScript Types
- ✅ **CCU-UI Dashboard** - Tabbed Shell mit i18n
- ✅ **MessageMonitorService** - State Persistence
- ✅ **I18n Runtime Switching** - URL-basierte Locale-Routing
- ✅ **CI/CD Umstellung** - OMF3 Tests in GitHub Actions
- ✅ **Tab Stream Pattern** - Konsistente Dateninitialisierung
- ✅ **Message Monitor Tab** - UI mit Filtering
- ✅ **Shopfloor-Highlighting** - Orange Highlighting
- ✅ **MQTT-Verbindungsstatus** - Visuelle Status-Anzeige

### **Dokumentation & Architektur** ✅
- ✅ **Sprint-Dokumentation** erstellen (sprint_01 bis sprint_09)
- ✅ **Mermaid Diagramm-System** - Hybrid-Ansatz mit `docs/_shared/diagrams/`
- ✅ **Pre-commit und Git/GitHub Workflow** - Projekt-spezifische Hooks
- ✅ **OMF3 Architektur-Dokumentation** - Project Structure, Decision Records
- ✅ **Dokumentations-Cleanup** - OMF2-spezifische Docs entfernt/archiviert

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

## 📊 Sprint-Status

### Sprint 09 (13.11 - 27.11.2025) - **AKTUELL**
- **Status:** In Bearbeitung
- **Fokus:** OMF3 Integration, MessageMonitorService, UI-Verbesserungen, Messevorbereitung
- **Erreicht:** MessageMonitorService, I18n Runtime Switching, CI/CD Umstellung, Message Monitor Tab, Tab Stream Pattern, Shopfloor-Highlighting, MQTT-Verbindungsstatus
- **In Arbeit:** Messevorbereitung (Unterbau, Banner, Aufbau/Abbau-Test)
- **Geplant:** Messe in Mulhouse (24-26.11.2025)

### Sprint 08 (30.10 - 12.11.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Asset-Management Refactoring, Sprachprüfung, OMF3 Entwicklung Start
- **Erreicht:** Asset-Management konsolidiert, Sprachprüfung abgeschlossen, OMF3 Grundstruktur aufgebaut (Angular + Nx Workspace, MQTT-Client, Gateway, Business, Entities, CCU-UI Skeleton)
- **Meilenstein:** OMF3 Grundstruktur steht ✅

### Sprint 07 (16.10 - 29.10.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** OMF2-Refactoring und Architektur-Migration
- **Erreicht:** Drei-Schichten-Architektur, Registry Manager, Gateway-Routing, Business Manager, Production Order Manager, Storage Orders Logic, i18n-System, Best Practice Logging, 341/341 Tests
- **Meilenstein:** OMF2 ist produktionsreif und demo-fähig ✅

### Sprint 06 (02.10 - 15.10.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** OMF2-Refactoring und Architektur-Migration
- **Erreicht:** Drei-Schichten-Architektur, Registry Manager, Gateway-Routing, Business Manager, Production Order Manager, Storage Orders Logic, i18n-System, Best Practice Logging, 341/341 Tests

### Sprint 05 (18.09 - 01.10.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Component-Strukturierung und User-Konzept Vorbereitung
- **Erreicht:** APS Dashboard vollständig in OMF-Dashboard integriert, Component-Bereinigung abgeschlossen

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
- **OMF3 Architektur** Angular + Nx Workspace für moderne Frontend-Entwicklung
- **Library-Struktur** Getrennte Libraries für MQTT, Gateway, Business, Entities
- **Tab Stream Pattern** Zwei Patterns für konsistente Dateninitialisierung
- **MessageMonitorService** Persistence-Strategie (localStorage, keine Camera-Daten)
- **I18n Runtime** URL-basierte Locale-Routing für bessere UX
- **CI/CD** Vollständige Umstellung auf OMF3 Tests

### **Technische Meilensteine:**
- **OMF3 Architektur** Angular + Nx Workspace etabliert
- **Library-Struktur** MQTT-Client, Gateway, Business, Entities implementiert
- **MessageMonitorService** State Persistence mit BehaviorSubject + CircularBuffer
- **I18n Runtime** URL-basierte Locale-Routing ohne Reload
- **CI/CD** Vollständige Umstellung auf OMF3 Tests
- **Tab Stream Pattern** Konsistente Dateninitialisierung dokumentiert und getestet
- **UI-Polish** Konsistente Highlighting und Status-Anzeigen

## 🔗 Wichtige Links

- **Aktuelle Sprint-Dokumentation:** `docs/sprints/`
- **Decision Records:** `docs/03-decision-records/`
- **Architektur:** `docs/02-architecture/`
- **OMF3 README:** `omf3/README.md`
- **APS-Analyse:** `docs/06-integrations/`

---

**Status:** OMF3 Entwicklung läuft erfolgreich, OMF2 als Legacy markiert 🎯
