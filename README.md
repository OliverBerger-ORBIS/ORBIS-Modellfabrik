# ORBIS Modellfabrik - Agile Production Simulation 24V
>If you have any questions, please contact fischertechnik-technik@fischer.de

## 🎯 Quick Start

- **Neue Teammitglieder:** Starte mit [Strategy Vision](docs_orbis/01-strategy/vision.md) → [System Context](docs_orbis/02-architecture/system-context.md)
- **Entwickler:** [Registry Model](docs_orbis/02-architecture/registry-model.md) → [How-Tos](docs_orbis/04-howto/)
- **Architekten:** [Decision Records](docs_orbis/03-decision-records/) → [Architecture](docs_orbis/02-architecture/)

## 📚 Documentation Structure

### 01-Strategy
- [Vision](docs_orbis/01-strategy/vision.md) - MQTT-first Leitidee & v1-Zielbild
- [Goals](docs_orbis/01-strategy/goals.md) - Erfolgskriterien & Qualitätsmerkmale
- [Scope](docs_orbis/01-strategy/scope.md) - v1 vs. v1.1/2.0 Ausblick

### 02-Architecture
- [System Context](docs_orbis/02-architecture/system-context.md) - Kontextdiagramm (CCU, Module, Node-RED, OMF)
- [Message Flow](docs_orbis/02-architecture/message-flow.md) - End-to-End-Flows (Order→Module, State→Dashboard)
- [Registry Model](docs_orbis/02-architecture/registry-model.md) - Registry-Prinzipien & Versionierung
- [Naming Conventions](docs_orbis/02-architecture/naming-conventions.md) - Topics, Template-Keys, IDs

### 03-Decision Records (ADRs)
- [ADR-0001: Topic-free Templates](docs_orbis/03-decision-records/ADR-0001-registry-topic-free-templates.md)
- [ADR-0002: Exact Overrides per Serial](docs_orbis/03-decision-records/ADR-0002-exact-overrides-per-serial.md)

### 04-How-To
- [Add a New Module](docs_orbis/04-howto/add-a-new-module.md) - Template → Mapping → Tests
- [Define a New Topic](docs_orbis/04-howto/define-a-new-topic.md) - Pattern vs. Exact
- [Build and Run](docs_orbis/04-howto/build-and-run.md) - OMF Dashboard & Session-Manager
- [Validate and Release](docs_orbis/04-howto/validate-and-release.md) - Make-Targets & Versioning

### 05-Reference
- [Topics](docs_orbis/05-reference/topics.md) - Logische Topic-Gruppen
- [Templates](docs_orbis/05-reference/templates.md) - Template-Index & Migration Mapping
- [Enums](docs_orbis/05-reference/enums.md) - Zentrale Listen (Availability/Action/Workpiece)

### 06-Integrations
- [Node-RED](docs_orbis/06-integrations/node-red/) - Node-RED Integration & Management

### 99-Glossary
- [Glossary](docs_orbis/99-glossary.md) - Eindeutige Begrifflichkeiten & IDs

## 🔗 Quick Links

- **Registry:** `registry/model/v1/` - Single Source of Truth
- **Source Code:** `src_orbis/` - Runtime & Tools
- **Integrations:** `integrations/` - Externe Systeme (Node-RED, etc.)
- **Legacy Docs:** [Archive](docs_orbis/archive/) - Veraltete Dokumentation

## 🚀 Getting Started

1. **Verstehe das System:** [Vision](docs_orbis/01-strategy/vision.md) (5 Min)
2. **Architektur verstehen:** [System Context](docs_orbis/02-architecture/system-context.md) (10 Min)
3. **Registry-Prinzipien:** [Registry Model](docs_orbis/02-architecture/registry-model.md) (5 Min)
4. **Praktisch arbeiten:** [How-Tos](docs_orbis/04-howto/) (je nach Aufgabe)

---

**"Code as Doc" - Registry ist die Quelle der Wahrheit, Docs erklären das Warum und Wie.**

## 🎯 Entwicklungshinweise

### **KRITISCHE REGELN:**
- **NUR absolute Pfade:** `/Users/oliver/Projects/ORBIS-Modellfabrik/path/to/file`
- **NUR absolute Imports:** `from src_orbis.omf.module import Class`
- **KEINE relativen Pfade/Imports** ❌

### **Cursor AI Konfiguration:**
- `.cursorrules` - Projekt-spezifische Regeln
- `.vscode/settings.json` - Cursor-spezifische Einstellungen
- `pyproject.toml` - Python-spezifische Konfiguration

## 📁 Project Structure

### Original Fischertechnik Content
- `data/` - Original data files
- `PLC-programs/` - Original PLC programs  
- `TXT4.0-programs/` - Original TXT4.0 programs
- `Node-RED/` - Original Node-RED flows
- `doc/` - Original documentation

### Orbis Customizations
- `docs_orbis/` - Orbis documentation and analysis
- `src_orbis/` - Orbis source code
  - `omf/` - OMF Dashboard (Hauptanwendung)
  - `helper_apps/` - Helper-Anwendungen (unabhängig)
    - `session_manager/` - Session Manager (Replay-Funktionalität)
- `tests_orbis/` - Orbis tests
- `registry/` - Registry & Schemas (Single Source of Truth)
- `data/` - Unsere Daten (`mqtt-data/`, `omf-data/`)

### System-Architektur
- **OMF Dashboard**: Hauptanwendung für Fabrik-Steuerung
- **Session Manager**: Unabhängige Helper-App für Session-Replay
- **Keine direkte Kopplung**: Beide Systeme arbeiten unabhängig
- **Replay-Funktionalität**: Session Manager spielt Sessions über lokalen MQTT-Broker ab

### Struktur-Validierung
```bash
# Struktur validieren
make validate-structure

# Automatische Korrektur versuchen
make fix-structure

# Alle Checks ausführen
make all-checks
```

Siehe [Developer Guide](docs_orbis/developer_guide) für detaillierte Entwicklungsregeln und Import-Standards.

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

For detailed documentation of the Node-RED flows, system architecture, and development guidelines, see the [Orbis Documentation Directory](./docs_orbis/).

- **[Node-RED Documentation](./docs_orbis/node-red/)** - Complete flow analysis, state machine, and development guides
- **[System Architecture](./docs_orbis/node-red/architecture.md)** - Overall system design and components
- **[Flows Overview](./docs_orbis/node-red/flows-overview.md)** - Detailed tab and module structure
- **[State Machine](./docs_orbis/node-red/state-machine.md)** - VDA 5050 compliant state transitions


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

