# ORBIS SmartFactory - Fischertechnik Agile Production Simulation 24V
>If you have any questions, please contact fischertechnik-technik@fischer.de

## 🏗️ System-Architektur

### **APS (Agile Production Simulation) - As-Is System**
Besteht aus Software-Componenten und Physischen Geräten/Devices
- **Fischertechnik-ModellFabrik (FMF)** mit Original-Komponenten
- **APS-Module** - Physische Module (DRILL, HBW, etc.)
Die Software-Komponenten
- **APS-CCU** - Central Control Unit (Raspberry PI)
- **APS-NodeRED** - Node-RED Flows für Steuerung
_ weitere Software auf den sog. TXT4.0 Controller der DEvices


### **OSF (ORBIS-SmartFactory) - To-Be System**
- **OSF-Dashboard** - Angular-basierte Steuerung (aktuell in Entwicklung, ehemals OMF3)
- **Session Manager** - Helper-App für Session-Replay (Streamlit)
## **Ziel**
Integration von OSF in die ORBIS-Produkte DSP,MES,.. (Oder anders herum Integration der ORBIS-Produkte in OSF): zur Visualisierung/Darstellung der Fähigkeiten und Funktionen der ORBIS-Produkte.
Was auch immer dafür angepasst werden muss in den Software-Komponenten ist Teil des Projektes.


> **📋 Namenskonvention:** Groß-Schreibweise mit Bindestrich (z.B. APS-CCU, OSF-Dashboard)

## 🎯 Quick Start

- **Neue Teammitglieder:** Starte mit [Strategy Vision](docs/01-strategy/vision.md) → [Project Structure](docs/02-architecture/project-structure.md)
- **Entwickler:** [Project Structure](docs/02-architecture/project-structure.md) → [How-Tos](docs/04-howto/)
- **Architekten:** [Decision Records](docs/03-decision-records/) → [Architecture](docs/02-architecture/)

## 📚 Documentation Structure

### 01-Strategy
- [Vision](docs/01-strategy/vision.md) - MQTT-first Leitidee & v1-Zielbild
- [Project Overview](docs/01-strategy/project-overview.md) - Projekt-Übersicht
- [Roadmap](docs/01-strategy/roadmap.md) - Entwicklungsphasen

### 02-Architecture
- [OSF Project Structure](docs/02-architecture/project-structure.md) - Nx Workspace Struktur und Architektur
- [Naming Conventions](docs/02-architecture/naming-conventions.md) - Topics, Template-Keys, IDs
- [APS Data Flow](docs/02-architecture/aps-data-flow.md) - APS Datenverarbeitung & Storage

### 03-Decision Records (ADRs)
- [Tab Stream Initialization Pattern](docs/03-decision-records/11-tab-stream-initialization-pattern.md) - Timing-unabhängige Tab-Stream-Initialisierung
- [MessageMonitorService Storage](docs/03-decision-records/12-message-monitor-service-storage.md) - Speicherverwaltung
- [MQTT Connection Loop Prevention](docs/03-decision-records/13-mqtt-connection-loop-prevention.md) - Connection Loop Prävention

### 04-How-To
- [MQTT Client Connection](docs/04-howto/mqtt_client_connection.md) - MQTT-Client Integration
- [UI Symbols Usage Guide](docs/04-howto/ui_symbols.md) - SVG Icons für Headings und Shopfloor
- [Shopfloor Layout Guide](docs/04-howto/SHOPFLOOR_LAYOUT_GUIDE.md) - Shopfloor-Layout Konfiguration
- [Session Manager](docs/04-howto/helper_apps/session-manager/README.md) - Session-Replay Funktionalität

### 06-Integrations
- [APS AS-IS Documentation](docs/06-integrations/00-REFERENCE/README.md) - APS Referenz-Dokumentation
- [APS-CCU](docs/06-integrations/APS-CCU/README.md) - APS CCU Dokumentation
- [APS-NodeRED](docs/06-integrations/APS-NodeRED/README.md) - APS NodeRED Dokumentation

### 99-Glossary
- [Glossary](docs/99-glossary.md) - Eindeutige Begrifflichkeiten & IDs

## 🔗 Quick Links

- **OSF Source Code:** `osf/` - Angular Dashboard & Libraries
- **Session Manager:** `session_manager/` - Helper-App für Session-Replay
- **APS Integrations:** `integrations/` - APS AS-IS Komponenten
- **Legacy Docs:** [Archive](docs/archive/) - Veraltete Dokumentation

## 🚀 Getting Started

1. **Repository klonen:** `git clone <repo-url>`
2. **Verstehe das System:** [Vision](docs/01-strategy/vision.md) (5 Min)
3. **Architektur verstehen:** [OSF Project Structure](docs/02-architecture/project-structure.md) (10 Min)
4. **Naming Conventions:** [Naming Conventions](docs/02-architecture/naming-conventions.md) (5 Min)
5. **Praktisch arbeiten:** [How-Tos](docs/04-howto/) (je nach Aufgabe)

### OSF Development Setup

```bash
# Dependencies installieren
npm install

# Development Server starten
nx serve osf-ui

# Tests ausführen
nx test osf-ui
nx test mqtt-client
nx test gateway
nx test business

# Build
nx build osf-ui
```

Die OSF-Anwendung ist dann unter `http://localhost:4200` verfügbar.

### Session Manager (Helper-App)

```bash
# Virtual Environment aktivieren
source .venv/bin/activate

# Session Manager starten
streamlit run session_manager/app.py
```

Die Session Manager-Anwendung ist dann unter `http://localhost:8501` verfügbar.

---

**"Code as Doc" - Docs erklären das Warum und Wie.**

## 🎯 Entwicklungshinweise

### **OSF STATE-OF-THE-ART REGELN:**
- **TypeScript:** Strikte Typisierung, keine `any` ohne Begründung
- **RxJS:** Observable Patterns korrekt verwenden (`shareReplay`, `refCount: false` für persistente Streams)
- **Angular:** Component-basierte Architektur, Services für Business Logic
- **Nx Workspace:** Library-basierte Struktur, klare Abhängigkeiten
- **MessageMonitorService:** Für Timing-unabhängige Datenanzeige verwenden
- **Tab Stream Pattern:** Pattern 1 oder Pattern 2 korrekt anwenden
- **Automatische Regel-Erzwingung:** Pre-commit Hooks sorgen für Einhaltung


## 📁 Project Structure

### OSF (Aktuell in Entwicklung, ehemals OMF3)
- `osf/apps/osf-ui/` - **Angular Dashboard Application**
  - Angular-basierte UI
  - MQTT Client Integration (WebSocket)
  - MessageMonitorService für State Persistence
  - I18n Support (DE, EN, FR)
- `osf/libs/` - **Libraries**
  - `mqtt-client/` - MQTT Client Library (WebSocket, Mock)
  - `gateway/` - Gateway Library (Topic Mapping)
  - `business/` - Business Logic Library (Derived Streams)
  - `entities/` - Entity Types Library
  - `testing-fixtures/` - Testing Fixtures Library
- `osf/testing/fixtures/` - Test Fixtures (JSON/JSONL)

### OMF2 (Legacy)
- `omf2/` - **Legacy Streamlit Dashboard**
  - Wird durch OSF ersetzt
  - Bleibt bis zur vollständigen Migration produktiv

### Session Manager (Helper-App)
- `session_manager/` - **Session-Replay Helper-App**
  - Unabhängige Streamlit-App
  - Session-Replay über lokalen MQTT-Broker
  - Wird weiterhin verwendet

### APS AS-IS (Integrations)
- `integrations/` - **APS AS-IS Komponenten**
  - APS-CCU, APS-NodeRED, TXT-Controller
  - Original fischertechnik Komponenten

### System-Architektur

#### **OSF (Aktuell) - Angular-basierte Architektur**
- **Nx Workspace**: Monorepo-Struktur für bessere Code-Organisation
- **RxJS**: Reactive Programming mit Observables
- **TypeScript**: Type Safety über alle Libraries
- **Angular**: Modern UI Framework mit Component-based Architecture
- **MessageMonitorService**: State Persistence für sofortige Datenanzeige
- **Tab Stream Pattern**: Timing-unabhängige Initialisierung

#### **Session Manager - Helper-Anwendung**
- **Session Manager**: Unabhängige Helper-App für Session-Replay
- **Replay-Funktionalität**: Session Manager spielt Sessions über lokalen MQTT-Broker ab

## External Links
- [Product Page](https://www.fischertechnik.de/en/products/industry-and-universities/training-models/569289-agile-production-simulation-24v)
- [Overview Page](https://www.fischertechnik.de/en/industry-and-universities/technical-documents/simulate/agile-production-simulation#overview)
- [Quick Start Guide](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/quick-start-guide-agile-production-simulation_en.pdf)
- [Documentation](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/documentation_aps_en-0424.pdf)
- [Assigment Plans](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/assignmentplans_aps_en.pdf)
- [Calibration](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/calibration-en.zip)
- [Digital Learning Platform](https://www.fischertechnik-digital-learning-platform.de/)
- [Update Blog](https://www.fischertechnik.de/en/industry-and-universities/technical-documents/simulate/agile-production-simulation/update-blog)
- [Troubleshooting (DE)](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/de/fehlersuche_aps_de.pdf)

## Content

The PLC project archives of the individual modules are in the `PLC-programs` folder.

The solution to the exercise can be found in the folder `PLC-programs\S7_1200_TIAv18\Exercises`.

The `TXT4.0 programs` folder contains the project files of the 4 different TXTs of the APS.

The `Node-RED` folder contains the flows of Node-RED as a Json file

### Documentation

For detailed documentation of the Node-RED flows, system architecture, and development guidelines, see the [Orbis Documentation Directory](./docs/).

### Raspberry PI Image / Central Control Unit (CCU)

The Raspberry PI image can be found under the following link: https://short.omm.cloud/rpi-v130

see [Installation Instructions](RPI_Image.md)

For experienced users, SSH is enabled on the image with username `ff22` and password `ff22+`

### TXT 4.0 Controller

[ROBO Pro Coding](https://www.fischertechnik.de/de-de/industrie-und-hochschulen/apps) is required to access the code of the [TXT 4.0 Controllers](https://www.fischertechnik.de/txt40controller). This can be found in the Microsoft Store via the search.

Once the program has started, the project files can be imported and changed.

### Node-RED

A [Node-RED](https://nodered.org/) container is running on the Raspberry PI of the APS. To view the Node-RED flows of the APS, you can connect to the Node-RED via `http://192.168.0.100:1880/`. This requires a LAN or WLAN connection to the APS.

### PLC

TIAv18 is required to access the PLC programs.

As soon as TIAv18 is installed, the project files can be loaded and edited.
