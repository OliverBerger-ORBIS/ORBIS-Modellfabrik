# OMF Vision - MQTT-First Architecture

## 🎯 Leitidee

**Steuerung über MQTT-Kommandos, Node-RED vermittelt zu OPC-UA**

Das OMF-System basiert auf der Prämisse, dass alle Steuerungslogik über MQTT-Nachrichten abgewickelt wird. Node-RED fungiert als intelligenter Vermittler zwischen der hochrangigen MQTT-Steuerung und der niedrigrangigen OPC-UA-Kommunikation mit den physischen Modulen.

## 🏗️ System-Namenskonvention

### **APS (Agile Production Simulation) - As-Is System**
- **Fischertechnik-Fabrik** mit Original-Komponenten
- **APS-CCU** - Central Control Unit (Raspberry PI)
- **APS-NodeRED** - Node-RED Flows für Steuerung
- **APS-Module** - Physische Module (DRILL, HBW, etc.)

### **OMF (ORBIS-Modellfabrik) - To-Be System**
- **OMF-Dashboard** - Streamlit-basierte Steuerung
- **OMF-CCU** - Nachbau der APS-CCU Funktionalität
- **OMF-NodeRED** - Ersatz für APS-NodeRED
- **OMF-Module** - Software-Simulation der APS-Module

> **📋 Namenskonvention:** Groß-Schreibweise mit Bindestrich (z.B. APS-CCU, OMF-Dashboard)

## 🏗️ Architektur-Prinzipien

### 1. MQTT als Steuerungsebene
- **Alle Befehle** gehen über MQTT-Topics (`module/v1/ff/{serial}/order`)
- **Alle Status-Updates** kommen über MQTT-Topics (`module/v1/ff/{serial}/state`)
- **Keine direkte OPC-UA-Steuerung** aus dem OMF-Dashboard

### 2. Node-RED als Vermittler
- **Übersetzt** MQTT-Befehle in OPC-UA-Calls
- **Aggregiert** OPC-UA-Daten zu MQTT-Status-Nachrichten
- **Implementiert** Modul-spezifische Logik (State-Machine, Error-Handling)

### 3. Registry als Single Source of Truth
- **Templates** definieren Nachrichtenstrukturen (topic-frei)
- **Mappings** verbinden Topics mit Templates
- **Enums** standardisieren Werte (Action-States, Workpiece-Types)

## 🎯 v1 Erfolgskriterien

### Funktionale Ziele
- ✅ **OMF-Dashboard** kann DRILL mit `PICK → DRILL → DROP` anweisen
- ✅ **HBW-Verwaltung** über MQTT-Befehle (STORE, PICK, DROP)
- ✅ **AIQS-Bewertung** mit `CHECK_QUALITY` und `PASSED/FAILED` Results
- ✅ **Tests via Replay** stabil und reproduzierbar

### Qualitätsmerkmale
- **Deterministischer Resolver:** Topic → Template-Mapping ist eindeutig
- **Valide Templates:** Alle Nachrichten entsprechen Registry-Schema
- **Reproduzierbare Replays:** Session-Manager ermöglicht deterministische Tests

## 🔄 Message-Flow-Prinzip

```
User (Dashboard) → MQTT Order → Node-RED → OPC-UA → Modul
Modul → OPC-UA → Node-RED → MQTT State → Dashboard
```

### Beispiel: DRILL-Befehl
1. **Dashboard** sendet `module/v1/ff/SVR4H76449/order` mit `{"command": "DRILL", "type": "WHITE"}`
2. **Node-RED** übersetzt zu OPC-UA-Call an DRILL-Modul
3. **DRILL-Modul** führt Aktion aus
4. **Node-RED** sammelt OPC-UA-Status und sendet `module/v1/ff/SVR4H76449/state`
5. **Dashboard** zeigt Status-Update an

## 🚀 v1.1/2.0 Ausblick

### v1.1 - Erweiterte Module
- **FTS-Integration** (Fahrerlose Transportsysteme)
- **TXT-Controller** Integration
- **Erweiterte Workflows** (Multi-Modul-Sequenzen)

### v2.0 - Intelligente Steuerung
- **KI-basierte Optimierung** von Produktionssequenzen
- **Predictive Maintenance** basierend auf MQTT-Telemetrie
- **Distributed Control** ohne zentrale CCU

## 💡 Warum MQTT-First?

### Vorteile
- **Entkopplung:** Dashboard unabhängig von OPC-UA-Details
- **Skalierbarkeit:** Neue Module über MQTT-Topics hinzufügbar
- **Testbarkeit:** Replay-System für deterministische Tests
- **Wartbarkeit:** Klare Trennung von Steuerung und Hardware

### Trade-offs
- **Komplexität:** Zusätzliche Schicht (Node-RED) erforderlich
- **Latenz:** MQTT → Node-RED → OPC-UA → Hardware
- **Abhängigkeiten:** Node-RED muss verfügbar sein

---

**"MQTT-First bedeutet: Alles was steuerbar ist, ist über MQTT steuerbar."**
