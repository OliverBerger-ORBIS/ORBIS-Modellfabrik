# ORBIS Modellfabrik - Agile Production Simulation 24V
>If you have any questions, please contact fischertechnik-technik@fischer.de

## 🏗️ System-Architektur

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

## 🎯 Quick Start

- **Neue Teammitglieder:** Starte mit [Strategy Vision](docs/01-strategy/vision.md) → [System Context](docs/02-architecture/system-context.md)
- **Entwickler:** [Registry Model](docs/02-architecture/registry-model.md) → [How-Tos](docs/04-howto/)
- **Architekten:** [Decision Records](docs/03-decision-records/) → [Architecture](docs/02-architecture/)

## 🤖 **Cursor AI / Agent Einweisung**

### **🚨 MANDATORY: Development Methodology (HÖCHSTE PRIORITÄT)**
- **📖 MUSS LESEN:** [Development Workflow](docs/04-howto/development/workflow.md) **BEVOR** Implementierung beginnt!
- **📋 METHODOLOGIE BEFOLGEN:** Analyse → Planung → Absprache → Implementierung → Test → Dokumentation → Commit
- **🎨 UI-SYMBOL REGELN:** **NIEMALS hardcodierte Icons verwenden - immer UISymbols!**
- **✅ BESTÄTIGEN:** Agent muss bestätigen dass er die Vorgehensweise verstanden hat
- **NIEMALS direkt mit Implementierung beginnen** ohne diese Schritte!

### **🚨 KRITISCHE VERBOTE (HÖCHSTE PRIORITÄT)**
- **NIEMALS Streamlit-Apps starten:** `streamlit run` ❌ (Verursacht Race-Conditions, MQTT-Konflikte)
- **NUR User startet Streamlit-Apps** - Agent startet KEINE Streamlit-Apps

### **📋 Dokumentations-Workflow für neue Agenten/Chats**
1. **Projekt-Status verstehen:** [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) - Aktueller Sprint, Status, Arbeiten
2. **Strategische Übersicht:** [Roadmap](docs/01-strategy/roadmap.md) - Alle Entwicklungsphasen
3. **Konkrete ToDos:** [plan.md](plan.md) - Messe-Vorbereitung und aktuelle Aufgaben
4. **Sprint-Details:** [docs/sprints/](docs/sprints/) - Detaillierte Sprint-Dokumentation
5. **Architektur verstehen:** [OMF2 Architecture](docs/02-architecture/omf2-architecture.md) - Technische Grundlagen
6. **Registry System:** [OMF2 Registry System](docs/02-architecture/omf2-registry-system.md) - **KRITISCH** - OMF-Entitäten-Zugriff
7. **Logging System:** [Logging Implementation Guide](docs/04-howto/logging-implementation-guide.md) - **KRITISCH** - Log-Analyse und Debugging

### **🎯 Dokumentations-Prinzipien**
- **roadmap.md** = Strategischer Überblick (keine konkreten ToDos)
- **PROJECT_STATUS.md** = Sprint-Status und aktuelle Arbeiten  
- **plan.md** = Konkrete Messe-Vorbereitung + Post-Messe Tasks
- **docs/sprints/** = Detaillierte Sprint-Dokumentation
- **docs/01-strategy/** = Strategische Grundlagen
- **docs/02-architecture/** = Technische Architektur
- **docs/03-decision-records/** = Architektur-Entscheidungen
- **docs/04-howto/** = Praktische Anleitungen
- **docs/04-howto/logging-implementation-guide.md** = **EINZIGE** Logging-Dokumentation

### **🔄 MANDATORY AGENT WORKFLOW (KRITISCH)**

**🚨 NIEMALS direkt implementieren ohne vorherige Analyse und Abstimmung!**

#### **1. ANALYSE-PHASE (OBLIGATORISCH)**
- **Verstehe das Problem:** Was ist der aktuelle Zustand?
- **Identifiziere Abhängigkeiten:** Was ist bereits implementiert?
- **Erkenne Lücken:** Was fehlt noch?
- **Verstehe Kontext:** Wie passt es in die Architektur?

#### **2. PLAN-PHASE (OBLIGATORISCH)**
- **Erstelle Optionen:** Verschiedene Lösungsansätze
- **Bewerte Vor-/Nachteile:** Welcher Ansatz ist am besten?
- **Definiere Scope:** Was wird in diesem Schritt gemacht?
- **Stelle Fragen:** Bei Unklarheiten IMMER nachfragen

#### **3. ABSTIMMUNG (OBLIGATORISCH)**
- **Präsentiere Plan:** Klare Optionen mit Vor-/Nachteilen
- **Warte auf Freigabe:** NIEMALS ohne User-Bestätigung implementieren
- **Kläre Details:** Bei Unsicherheiten nachfragen
- **Bestätige Scope:** Was genau wird gemacht?

#### **4. IMPLEMENTIERUNG (NUR NACH FREIGABE)**
- **Folge dem abgestimmten Plan:** Keine Abweichungen ohne Rücksprache
- **Teste kontinuierlich:** Nach jeder Änderung Tests laufen lassen
- **Dokumentiere Änderungen:** Was wurde gemacht und warum
- **Validiere Ergebnis:** Entspricht es den Anforderungen?

#### **🚨 ANTI-PATTERN VERMEIDEN:**
- ❌ **Direkte Implementierung** ohne Analyse
- ❌ **"Ich mache mal schnell..."** ohne Abstimmung
- ❌ **Implizite Annahmen** über User-Wünsche
- ❌ **Scope-Creep** während der Implementierung

#### **✅ BEST PRACTICE:**
- ✅ **Immer erst verstehen, dann planen, dann abstimmen, dann implementieren**
- ✅ **Klare Kommunikation** über Pläne und Optionen
- ✅ **Kleine, abgestimmte Schritte** statt große Änderungen
- ✅ **Kontinuierliche Validierung** mit Tests

### **🧪 Test-First Development Workflow**

**🚨 KRITISCH: Test-First Ansatz für alle Architektur-Änderungen!**

#### **1. VORBEREITUNG (OBLIGATORISCH)**
- **Alle Tests durchführen** → Baseline: Was funktioniert aktuell?
- **Test-Coverage prüfen:** Deckt die Tests alle Architektur-Stufen ab?
- **Fehlende Tests ergänzen** vor der Implementierung

#### **2. ARCHITEKTUR-VERSTÄNDNIS (OBLIGATORISCH)**
**Asymmetrische Architektur-Kette:** (siehe [OMF2 Architecture](docs/02-architecture/omf2-architecture.md))
```
mqtt_client → gateway → business_function (*manager) → ui_komponente
```
**Metadaten-Quellen:**
- Registry-Komponenten
- Code-Anpassungen (onMessage Handler im Gateway)

#### **3. IMPLEMENTIERUNG (NUR NACH TEST-VORBEREITUNG)**
- **Alle Komponenten anpassen** in der Architektur-Kette
- **Registry-Referenzen** aktualisieren
- **Gateway Message Handler** anpassen
- **UI-Komponenten** anpassen

#### **4. VALIDIERUNG (OBLIGATORISCH)**
- **Tests erneut durchführen** → Alles muss grün sein
- **UI-Integrationstest:** [Session Manager Replay Station](docs/04-howto/helper_apps/session-manager/README.md)
- **Log-File-Analyse:** Agent kontrolliert parallel
- **UI-Ergebnis:** User kontrolliert in der UI

#### **5. TEST-DATEN**
- **Test-Payloads** aus Sessions oder `data/*` Quellen
- **Session-Manager Replay-Station** für UI-Integrationstests

#### **🎯 Beispiel: Manager-Renaming**
```
1. Tests der zu renamenden Komponenten prüfen
2. Test-Coverage für alle Architektur-Stufen bewerten
3. Fehlende Tests ergänzen vor dem Renaming
4. Renaming durchführen (alle Architektur-Komponenten)
5. Tests erneut durchführen → muss grün sein
6. UI-Integrationstest mit Session Manager
```

### **🔧 Entwicklung-Regeln (AUTOMATISCH BEFOLGEN)**
- **Absolute Imports:** `from omf.dashboard.tools.logging_config import get_logger`
- **Absolute Pfade:** `project_root / "data/omf-data/sessions"`
- **OMF-Logging:** `get_logger("module.component")` statt `logging.getLogger()`
- **UI-Refresh:** `request_refresh()` statt `st.rerun()`
- **Pre-commit Hooks:** Immer befolgen, nie mit `--no-verify` überspringen
- **Tests:** Nach jeder Änderung ausführen mit aktiviertem `.venv`

> **📚 Vollständige Regeln:** Siehe [Development Rules Compliance](docs/03-decision-records/07-development-rules-compliance.md)

## 📚 Documentation Structure

### 01-Strategy
- [Vision](docs/01-strategy/vision.md) - MQTT-first Leitidee & v1-Zielbild
- [Goals](docs/01-strategy/goals.md) - Erfolgskriterien & Qualitätsmerkmale
- [Scope](docs/01-strategy/scope.md) - v1 vs. v1.1/2.0 Ausblick

### 02-Architecture
- [System Context](docs/02-architecture/system-context.md) - Kontextdiagramm (CCU, Module, Node-RED, OMF)
- [Message Flow](docs/02-architecture/message-flow.md) - End-to-End-Flows (Order→Module, State→Dashboard)
- [Registry Model](docs/02-architecture/registry-model.md) - Registry-Prinzipien & Versionierung
- [Naming Conventions](docs/02-architecture/naming-conventions.md) - Topics, Template-Keys, IDs

### 03-Decision Records (ADRs)
- [ADR-0001: Topic-free Templates](docs/03-decision-records/ADR-0001-registry-topic-free-templates.md)
- [ADR-0002: Exact Overrides per Serial](docs/03-decision-records/ADR-0002-exact-overrides-per-serial.md)

### 04-How-To
- [Add a New Module](docs/04-howto/add-a-new-module.md) - Template → Mapping → Tests
- [Define a New Topic](docs/04-howto/define-a-new-topic.md) - Pattern vs. Exact
- [Build and Run](docs/04-howto/build-and-run.md) - OMF Dashboard & Session-Manager
- [Validate and Release](docs/04-howto/validate-and-release.md) - Make-Targets & Versioning

### 05-Reference
- [Topics](docs/05-reference/topics.md) - Logische Topic-Gruppen
- [Templates](docs/05-reference/templates.md) - Template-Index & Migration Mapping
- [Enums](docs/05-reference/enums.md) - Zentrale Listen (Availability/Action/Workpiece)

### 06-Integrations
- [Node-RED](docs/06-integrations/node-red/) - Node-RED Integration & Management

### 99-Glossary
- [Glossary](docs/99-glossary.md) - Eindeutige Begrifflichkeiten & IDs

## 🔗 Quick Links

- **Registry:** `registry/model/v1/` - Single Source of Truth
- **Source Code:** `omf/` - Runtime & Tools
- **Integrations:** `integrations/` - Externe Systeme (Node-RED, etc.)
- **Legacy Docs:** [Archive](docs/archive/) - Veraltete Dokumentation

## 🚀 Getting Started

1. **Repository klonen:** `git clone --recursive <repo-url>` (inkl. Submodule)
2. **Verstehe das System:** [Vision](docs/01-strategy/vision.md) (5 Min)
3. **Architektur verstehen:** [System Context](docs/02-architecture/system-context.md) (10 Min)
4. **Registry-Prinzipien:** [Registry Model](docs/02-architecture/registry-model.md) (5 Min)
5. **Praktisch arbeiten:** [How-Tos](docs/04-howto/) (je nach Aufgabe)

### Upstream (Submodule)
- **Nach dem Klonen:** `git submodule update --init --recursive`
- **Upstream aktualisieren:** 
  ```bash
  cd vendor/fischertechnik && git fetch && git checkout main && cd ../..
  git add vendor/fischertechnik && git commit -m "chore: bump upstream"
  ```

---

**"Code as Doc" - Registry ist die Quelle der Wahrheit, Docs erklären das Warum und Wie.**

## 🎯 Entwicklungshinweise

### **STATE-OF-THE-ART REGELN:**
- **Robuste Pfad-Konstanten:** `from omf.dashboard.tools.path_constants import PROJECT_ROOT, SESSIONS_DIR, CONFIG_DIR`
- **Absolute Imports für externe Module:** `from omf.dashboard.tools.logging_config import get_logger`
- **Relative Imports für Paket-interne Module:** `from .aps_overview_commands import show_aps_overview_commands`
- **OMF-Logging-System:** `get_logger("omf.module.component")` statt `logging.getLogger()`
- **UI-Refresh Pattern:** `request_refresh()` statt `st.rerun()`
- **Keine sys.path.append Hacks:** Absolute Imports verwenden
- **Automatische Regel-Erzwingung:** Pre-commit Hooks sorgen für Einhaltung

> **📚 State-of-the-Art Standards:** Siehe [Decision Record: Development Rules Compliance](docs/03-decision-records/07-development-rules-compliance.md) und [Path Constants](omf/dashboard/tools/path_constants.py)

### **Cursor AI Konfiguration:**
- `.cursorrules` - Projekt-spezifische Regeln
- `.vscode/settings.json` - Cursor-spezifische Einstellungen
- `pyproject.toml` - Python-spezifische Konfiguration

## 📁 Project Structure

### Upstream (Submodule)
- `vendor/fischertechnik/` - Original fischertechnik Repository als Submodule
  - `PLC-programs/` - Original PLC programs  
  - `TXT4.0-programs/` - Original TXT4.0 programs
  - `Node-RED/` - Original Node-RED flows
  - `doc/` - Original documentation

### Orbis Customizations
- `docs/` - Orbis documentation and analysis
- `omf/` - Legacy OMF Dashboard (Hauptanwendung)
  - `omf/` - OMF Dashboard (Legacy-Version)
  - `helper_apps/` - Helper-Anwendungen (unabhängig)
    - `session_manager/` - Session Manager (Replay-Funktionalität)
- `omf2/` - **NEUE OMF2 Architektur** (Empfohlen)
  - `omf2/omf.py` - Streamlit Dashboard Entry Point
  - `omf2/admin/` - Admin Domain (MQTT Client + Gateway + Manager)
  - `omf2/ccu/` - CCU Domain (MQTT Client + Gateway + Manager)
  - `omf2/nodered/` - Node-RED Domain (Gateway + Manager)
  - `omf2/common/` - Shared Components (Logger, Registry, Manager)
  - `omf2/factory/` - Factory Pattern für Singleton-Erstellung
  - `omf2/ui/` - Streamlit UI Components
  - `omf2/registry/` - Registry v2 (Topics, Schemas, MQTT Clients)
  - `omf2/config/` - Konfigurationsdateien (MQTT, Logging)
  - `omf2/docs/` - OMF2-spezifische Dokumentation
  - `omf2/tests/` - OMF2 Test Suite (55 Tests)
- `tests/` - Legacy Orbis tests
- `registry/` - Legacy Registry & Schemas
- `data/` - Unsere Daten (`mqtt-data/`, `omf-data/`)

### System-Architektur

#### **OMF2 (Empfohlen) - Moderne Architektur**
- **Drei-Schichten-Architektur**: MQTT Client → Gateway → Business Manager
- **Thread-sichere Singleton**: Alle Komponenten sind thread-safe
- **Schema-driven**: Registry-basierte Validierung und Routing
- **Best Practice Logging**: Level-spezifische Ringbuffer mit UI-Integration
- **55 erfolgreiche Tests**: Vollständige Test-Abdeckung

#### **OMF (Legacy) - Bestehende Architektur**
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

Siehe [Decision Record: Development Rules Compliance](docs/03-decision-records/07-development-rules-compliance.md) für detaillierte Entwicklungsregeln und Import-Standards.

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

- **[Node-RED Documentation](./docs/node-red/)** - Complete flow analysis, state machine, and development guides
- **[System Architecture](./docs/node-red/architecture.md)** - Overall system design and components
- **[Flows Overview](./docs/node-red/flows-overview.md)** - Detailed tab and module structure
- **[State Machine](./docs/node-red/state-machine.md)** - VDA 5050 compliant state transitions


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

---

## OMF2 Streamlit Dashboard

Das OMF2 Dashboard ist eine moderne, webbasierte Anwendung zur Steuerung und Überwachung der ORBIS Modellfabrik. Die Anwendung ist als Streamlit-App implementiert und bietet eine rollenbasierte, mehrsprachige Benutzeroberfläche.

### Schnellstart OMF2

```bash
# Virtual Environment aktivieren
source .venv/bin/activate

# Installation der Abhängigkeiten
pip install -r requirements.txt

# Starten der OMF2 Streamlit-App
streamlit run omf2/omf.py
```

Die OMF2-Anwendung ist dann unter `http://localhost:8501` verfügbar.

### OMF2 Core-Architektur

Das OMF2 Dashboard folgt einer professionellen **Drei-Schichten-Architektur**:

#### **🔌 MQTT CLIENT LAYER (Transport)**
- **Thread-sichere Singleton** für alle Domänen (Admin, CCU, Node-RED)
- **Raw MQTT → Clean JSON** Transformation
- **Meta-Parameter-System** (timestamp, qos, retain)
- **Robust Payload-Handling** für alle JSON-Typen
- **Buffer-Management** für UI-Monitoring

#### **🚪 GATEWAY LAYER (Validation & Routing)**
- **Schema-Validation** mit Registry-Schemas
- **Topic-Routing** (Set-basiert + Präfix-basiert)
- **Error-Handling** mit detailliertem Logging
- **Clean Data Contract** (NIE raw bytes an Manager)
- **Domain-spezifische Gateways** (Admin, CCU, Node-RED)

#### **🏢 BUSINESS MANAGER LAYER (Business Logic)**
- **State-Holder Pattern** für Business-Daten
- **Schema-basierte Verarbeitung** mit Registry-Integration
- **Domain-agnostic Manager** (Message, Topic, Sensor, Module)
- **Clean API** für UI-Komponenten
- **Thread-safe Operations** für MQTT-Callbacks

### OMF2 Features

- **Best Practice Logging-System** mit Level-spezifischen Ringbuffern
- **UI-Logging Integration** mit dedizierten Error & Warning Tabs
- **Registry v2 Integration** für alle Komponenten
- **Schema-driven Architecture** mit JSON-Schema-Validierung
- **Thread-safe Singleton Pattern** für alle Komponenten
- **55 erfolgreiche Tests** für die gesamte Architektur

### OMF2 Tests

```bash
# Alle OMF2-Tests ausführen
python -m pytest omf2/tests/ -v

# Spezifische Test-Suites
python -m pytest omf2/tests/test_comprehensive_architecture.py -v
python -m pytest omf2/tests/test_gateway_factory.py -v
python -m pytest omf2/tests/test_registry_manager_comprehensive.py -v
```

### OMF2 Konfiguration

- **MQTT-Einstellungen**: `omf2/config/mqtt_settings.yml`
- **Logging-Konfiguration**: `omf2/config/logging_config.yml`
- **Registry-Schemas**: `omf2/registry/schemas/`
- **Topic-Definitionen**: `omf2/registry/topics/`

Für detaillierte Architektur-Informationen siehe `omf2/docs/ARCHITECTURE.md`.

