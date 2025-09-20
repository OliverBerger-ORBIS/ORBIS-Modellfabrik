# ORBIS Modellfabrik - Projekt-Übersicht

## 🎯 Projektziel
Verständnis der Funktionsweise der APS Fischertechnik Anwendung, um eine eigene Anwendung zu bauen, die die Steuerung der Modellfabrik übernimmt.

### APS-Fischertechnik System
- **Reale Miniatur-Fabrik** mit verschiedenen Modulen
- **Software zur Steuerung** der Fabrik-Prozesse
- **Hauptprozesse:**
  - Wareneingang
  - Produktion nach Bestellung

## 🚀 Geplante Vorgehensweise

### Phase 1: Nachrichten-Fluß aufnehmen ✅
- **Session-Rekording** der Komponenten und Module der APS-Fabrik
- **Status:** Abgeschlossen (über Python-Script)

### Phase 2: Session-Analyse 🔄 **IN ENTWICKLUNG**
- **Status:** Session Manager teilweise funktional
- **Erreicht:** Session Recorder, Replay Station, Timeline-Visualisierung
- **Fehlt:** Graph-Visualisierung, vollständige Template-Analyse
- **Nächster Schritt:** Graph-Visualisierung und Template-Integration

### Phase 3: Steuerungs-Entwicklung 🚀 **AKTUELLER FOKUS**
- **Ziel:** Node-RED Flows ersetzen und komplette Produktionssteuerung übernehmen
- **Tool:** OMF Dashboard + DSP (Distributed Shopfloor Processing)
- **Funktion:** Automatische Produktionssteuerung mit Timing-Management

#### ✅ Abgeschlossen:
1. **ModuleStateManager implementiert** ⏱️
   - Automatische Sequenz-Ausführung funktional
   - Status-Subscription für alle Module
   - PICK → PROCESS → DROP Timing automatisiert

2. **Logging-System implementiert** 📋
   - Thread-sicheres Logging mit JSON-Format
   - Live-Logs im Dashboard verfügbar
   - Strukturierte Logs für Analyse

3. **Dashboard-Integration** 🎛️
   - Modul-Steuerung Tab hinzugefügt
   - Logs Tab für Live-Monitoring
   - UI-Refresh-Mechanismus implementiert

#### Nächste Schritte:
1. **Logger-Integration** in alle Komponenten 📝
2. **Command-Response-Testing** implementieren 🧪
3. **Real-Factory-Validation** durchführen 🏭

2. **OPC-UA Integration über DSP** 🔌
   - Direkte SPS-Kommunikation über DSP RPI
   - Node-ID Mapping (ns=4;i=5 = pick, ns=4;i=6 = drop)
   - MQTT-Bridge zwischen OMF Dashboard und DSP

3. **Node-RED schrittweise ersetzen** 🔄
   - Parallel-Entwicklung mit Command-Vergleich
   - Einzelne Modul-Tabs deaktivieren
   - Vollständige Übernahme der Produktionssteuerung

#### Detaillierte Strategie:
- **Dokumentation:** `docs/analysis/node-red-replacement-strategy.md`
- **Status:** 📋 **STRATEGIE DEFINIERT** - Bereit für Implementierung

## 🏗️ Teilprojekte

### Session Manager (Helper App) - **UNABHÄNGIG**
**Zweck:** Analyse und Replay der aufgenommenen Sessions
**Status:** Unabhängige Helper-Anwendung

#### Komponenten:
1. **Session Recorder** ✅ **VOLLSTÄNDIG FUNKTIONAL**
   - MQTT-Nachrichten aufnehmen und speichern
   - SQLite + Log-Dateien erstellen
   - Manueller Refresh-Button für Status-Updates
   - Thread-sichere Nachrichten-Sammlung

2. **Session Analyse** 🔄 **IN ENTWICKLUNG**
   - Timeline-Visualisierung mit Plotly ✅
   - Topic-Filterung und Kategorisierung ✅
   - Regex-Filter für Session-Dateien ✅
   - Interaktive Datenpunkt-Details ✅
   - **Graph-Visualisierung** ❌ (Message-Ketten basierend auf Meta-Daten)

3. **Replay Station** ✅ **VOLLSTÄNDIG FUNKTIONAL**
   - **Replay-Funktionalität:** Abspielen von Sessions über lokalen MQTT-Broker
   - **Zweck:** Test des OMF Dashboards ohne reale Hardware
   - **Vorteil:** Test ohne aktive Fabrik
   - **Nachteil:** Keine Kontrolle über reale Effekte
   - **Features:** Geschwindigkeitskontrolle, Pause/Stop, nur .db Dateien

4. **Template Analyse** 🔄 **IN ENTWICKLUNG**
   - **Bestehende Basis:** `analysis_tools/template_analyzers` ✅
   - **Integration:** Template-Analyse in Session Manager ❌
   - **Ziel:** Message-Struktur-Bibliothek für MessageGenerator
   - **Funktion:** Messages generieren und parsen

### OMF Dashboard - **HAUPTANWENDUNG**
**Zweck:** Hauptanwendung für Fabrik-Steuerung
**Status:** Unabhängige Hauptanwendung

#### Komponenten:
1. **Nachrichten-Zentrale** 📋
   - Zentrale Message-Verwaltung
   - Kommunikation mit Fabrik-Modulen

2. **Steuerung** 📋
   - Benutzeroberfläche für Fabrik-Steuerung
   - Prozess-Management

## 🔗 System-Architektur

### **Wichtige Klarstellung: KEINE INTEGRATION**
- **OMF Dashboard** und **Session Manager** sind **vollständig unabhängig**
- **Keine direkte Kopplung** zwischen den Systemen
- **Separate Entwicklung** und Wartung
- **Replay-Zweck:** Session Manager dient nur zum Abspielen von Sessions
- **Lokaler MQTT:** Replay erfolgt über lokalen Mosquitto-Broker

## 🔧 Technische Architektur

### MQTT-basierte Kommunikation
- **Protokoll:** MQTT für Message-Transport
- **Topics:** Strukturierte Nachrichten zwischen Komponenten
- **Session-Format:** JSON-basierte Logs

### OMF (ORBIS Modellfabrik) Framework
- **Topic-Management:** Kategorisierung und Friendly Names
- **Message-Templates:** Standardisierte Nachrichten-Formate
- **Settings-Management:** Konfigurierbare Vorfilter und Einstellungen

## 📊 Aktuelle Entwicklungsphase

### Session Manager - Session Analyse
- **Status:** In Entwicklung
- **Features:**
  - ✅ Session-Loading und Parsing
  - ✅ Timeline-Visualisierung
  - ✅ Topic-Filterung (Kategorie, Sub-Kategorie, Friendly Name, Topic Name)
  - ✅ Vorfilter-System für uninteressante Topics
  - ✅ Zeitfilter für Timeline-Analyse
  - ✅ Settings-Management
  - 🔄 Payload-Analyse und Message-Details

### Nächste Schritte
1. ✅**Template-Analyse** implementieren
2. ✅**Replay-Station** für Dashboard-Tests
3. ✅**OMF Dashboard** Funktionalitäts-Erweiterung
4. ✅**MessageGenerator** Entwicklung
5. ✅**MQTT Mosquitto** Analyse des Brokers in RPi
6. ✅**Analyse der TXT Controler von DPS** APS-Dasboard als CCU der Fischertechnik FAbrik
7. **APS-Dashboard** Erweiterung um Funktionalität des Dashboards von Fischertechnik
8. **I18n** Unterstützung für alle Dashboard Views (EN,DE,FR)
9. **Doku Sprints** Dokumenation retrospektive was in den Sprints ab Sproint 01 gemacht wurde
10. **Doku Helper-App** Doku mit Mermaid Diagrammen und Umstrukturierung der Tabs nach dem logischen Ablauf (Session Recorder Session Replay (als default), Session Analyse, Optional Template Analysis
11. **Mermaid** Grafiken isolieren und als Referenz in mehrere Dokus einbinden, IDE mit entsprechenden extensions, damit das funktioniert
12. **Architektur** Doku anpassen an Ergenisse aus APS-Analyse. OMF-Dashboad besteht aus "APS-Dashboard" Funktionalität + "DPS-Control"-Funktionalität von NodeREd nachimplementieren


## ⚠️ Wichtige Architektur-Hinweise
- **Keine Integration:** OMF Dashboard und Session Manager sind unabhängig
- **Replay-Zweck:** Session Manager dient nur zum Abspielen von Sessions
- **Lokaler MQTT:** Replay erfolgt über lokalen Mosquitto-Broker
- **Separate Entwicklung:** Beide Systeme werden unabhängig weiterentwickelt

## 🎯 Erfolgskriterien
- [ ] Vollständiges Verständnis der APS-Nachrichten-Semantik
- [ ] Funktionierender MessageGenerator
- [ ] Testbare OMF Dashboard-Integration
- [ ] Dokumentierte Message-Templates
- [ ] Replay-Station für isolierte Tests
