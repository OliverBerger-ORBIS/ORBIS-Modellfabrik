# ORBIS Modellfabrik - Agile Production Simulation 24V
>If you have any questions, please contact fischertechnik-technik@fischer.de

## 🏗️ System-Architektur

### **APS (Agile Production Simulation) - As-Is System**
- **Fischertechnik-Fabrik** mit Original-Komponenten
- **APS-CCU** - Central Control Unit (Raspberry PI)
- **APS-NodeRED** - Node-RED Flows für Steuerung
- **APS-Module** - Physische Module (DRILL, HBW, etc.)

### **OMF (ORBIS-Modellfabrik) - To-Be System**
- **OMF3-Dashboard** - Angular-basierte Steuerung (aktuell in Entwicklung)
- **OMF2-Dashboard** - Streamlit-basierte Steuerung (Legacy, wird durch OMF3 ersetzt)
- **Session Manager** - Helper-App für Session-Replay (Streamlit)
- **OMF-CCU** - Nachbau der APS-CCU Funktionalität

> **📋 Namenskonvention:** Groß-Schreibweise mit Bindestrich (z.B. APS-CCU, OMF3-Dashboard)

## 🎯 Quick Start

- **Neue Teammitglieder:** Starte mit [Strategy Vision](docs/01-strategy/vision.md) → [Project Structure](docs/02-architecture/project-structure.md)
- **Entwickler:** [Project Structure](docs/02-architecture/project-structure.md) → [How-Tos](docs/04-howto/)
- **Architekten:** [Decision Records](docs/03-decision-records/) → [Architecture](docs/02-architecture/)

## 🤖 **Cursor AI / Agent Einweisung**

### **🚨 KRITISCH: JEDER AGENT MUSS DIESE DOKUMENTATION LESEN!**

**⚠️ STOP! Bevor du irgendetwas machst, MUSS du diese Dokumentation lesen:**

1. **📖 MANDATORY DEVELOPMENT METHODOLOGY:** [Development Workflow](docs/04-howto/development/workflow.md) - **MUSS GELESEN WERDEN!**
2. **📖 ZENTRALE AGENT-DOKUMENTATION:** [Agent Onboarding Architecture](docs/04-howto/agent-onboarding-architecture.md) - **MUSS GELESEN WERDEN!**

**🚨 NIEMALS direkt mit Implementierung beginnen ohne diese Dokumentation gelesen zu haben!**
**🚨 NIEMALS spekulieren oder raten - IMMER erst Dokumentation lesen!**
**🚨 NIEMALS "ich mache mal schnell..." - IMMER erst verstehen, dann handeln!**

### **✅ BESTÄTIGUNG ERFORDERLICH**
**Jeder Agent MUSS bestätigen dass er:**
- ✅ Die Development Workflow-Dokumentation gelesen hat
- ✅ Die Agent Onboarding Architecture-Dokumentation gelesen hat  
- ✅ Die Methodologie verstanden hat
- ✅ Die Architektur-Prinzipien verstanden hat

**NUR NACH dieser Bestätigung darf der Agent mit der Arbeit beginnen!**

### **🚨 KRITISCHE VERBOTE (HÖCHSTE PRIORITÄT)**
- **NIEMALS Streamlit-Apps starten:** `streamlit run` ❌ (Verursacht Race-Conditions, MQTT-Konflikte)
- **NUR User startet Streamlit-Apps** - Agent startet KEINE Streamlit-Apps
- **NIEMALS Angular-Apps starten ohne User-Freigabe:** `nx serve ccu-ui` nur nach expliziter Bestätigung

### **📋 Dokumentations-Workflow für neue Agenten/Chats**
1. **🚨 MANDATORY DEVELOPMENT METHODOLOGY:** [Development Workflow](docs/04-howto/development/workflow.md) - **MUSS GELESEN WERDEN!**
2. **🚨 ZENTRALE AGENT-DOKUMENTATION:** [Agent Onboarding Architecture](docs/04-howto/agent-onboarding-architecture.md) - **MUSS GELESEN WERDEN!**
3. **Projekt-Status verstehen:** [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) - Aktueller Sprint, Status, Arbeiten
4. **Strategische Übersicht:** [Roadmap](docs/01-strategy/roadmap.md) - Alle Entwicklungsphasen
5. **Konkrete ToDos:** [plan.md](plan.md) - Messe-Vorbereitung und aktuelle Aufgaben
6. **Sprint-Details:** [docs/sprints/](docs/sprints/) - Detaillierte Sprint-Dokumentation
7. **Architektur verstehen:** [OMF3 Project Structure](docs/02-architecture/project-structure.md) - Technische Grundlagen
8. **MQTT Client:** [MQTT Client Connection](docs/04-howto/mqtt_client_connection.md) - MQTT-Integration
9. **Tab Stream Pattern:** [Tab Stream Initialization Pattern](docs/03-decision-records/11-tab-stream-initialization-pattern.md) - **KRITISCH** - Timing-unabhängige Datenanzeige

### **🎯 Dokumentations-Prinzipien**
- **roadmap.md** = Strategischer Überblick (keine konkreten ToDos)
- **PROJECT_STATUS.md** = Sprint-Status und aktuelle Arbeiten  
- **plan.md** = Konkrete Messe-Vorbereitung + Post-Messe Tasks
- **docs/sprints/** = Detaillierte Sprint-Dokumentation
- **docs/01-strategy/** = Strategische Grundlagen
- **docs/02-architecture/** = Technische Architektur (OMF3)
- **docs/03-decision-records/** = Architektur-Entscheidungen (OMF3)
- **docs/04-howto/** = Praktische Anleitungen

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
**OMF3 Architektur-Kette:** (siehe [OMF3 Project Structure](docs/02-architecture/project-structure.md))
```
mqtt_client → gateway → business → angular_components
```
**Metadaten-Quellen:**
- Entity Types (`omf3/libs/entities/`)
- Gateway Topic Mapping (`omf3/libs/gateway/`)
- Business Logic (`omf3/libs/business/`)

#### **3. IMPLEMENTIERUNG (NUR NACH TEST-VORBEREITUNG)**
- **Alle Komponenten anpassen** in der Architektur-Kette
- **Entity Types** aktualisieren
- **Gateway Topic Mapping** anpassen
- **Business Logic** anpassen
- **Angular Components** anpassen

#### **4. VALIDIERUNG (OBLIGATORISCH)**
- **Tests erneut durchführen** → Alles muss grün sein
- **UI-Integrationstest:** [Session Manager Replay Station](docs/04-howto/helper_apps/session-manager/README.md)
- **Browser-Test:** Angular App im Browser testen
- **UI-Ergebnis:** User kontrolliert in der UI

#### **5. TEST-DATEN**
- **Test-Payloads** aus Sessions oder `data/*` Quellen
- **Session-Manager Replay-Station** für UI-Integrationstests
- **Testing Fixtures** (`omf3/testing/fixtures/`)

### **🔧 Entwicklung-Regeln (AUTOMATISCH BEFOLGEN)**
- **TypeScript:** Strikte Typisierung, keine `any` ohne Begründung
- **RxJS:** Observable Patterns korrekt verwenden
- **Angular:** Component-basierte Architektur
- **Nx Workspace:** Library-basierte Struktur
- **Pre-commit Hooks:** Immer befolgen, nie mit `--no-verify` überspringen
- **Tests:** Nach jeder Änderung ausführen

> **📚 Vollständige Regeln:** Siehe [Development Rules Compliance](docs/03-decision-records/07-development-rules-compliance.md)

## 📚 Documentation Structure

### 01-Strategy
- [Vision](docs/01-strategy/vision.md) - MQTT-first Leitidee & v1-Zielbild
- [Project Overview](docs/01-strategy/project-overview.md) - Projekt-Übersicht
- [Roadmap](docs/01-strategy/roadmap.md) - Entwicklungsphasen

### 02-Architecture
- [OMF3 Project Structure](docs/02-architecture/project-structure.md) - Nx Workspace Struktur und Architektur
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

- **OMF3 Source Code:** `omf3/` - Angular Dashboard & Libraries
- **OMF2 Source Code:** `omf2/` - Legacy Streamlit Dashboard
- **Session Manager:** `session_manager/` - Helper-App für Session-Replay
- **APS Integrations:** `integrations/` - APS AS-IS Komponenten
- **Legacy Docs:** [Archive](docs/archive/) - Veraltete Dokumentation

## 🚀 Getting Started

1. **Repository klonen:** `git clone <repo-url>`
2. **Verstehe das System:** [Vision](docs/01-strategy/vision.md) (5 Min)
3. **Architektur verstehen:** [OMF3 Project Structure](docs/02-architecture/project-structure.md) (10 Min)
4. **Naming Conventions:** [Naming Conventions](docs/02-architecture/naming-conventions.md) (5 Min)
5. **Praktisch arbeiten:** [How-Tos](docs/04-howto/) (je nach Aufgabe)

### OMF3 Development Setup

```bash
# Dependencies installieren
npm install

# Development Server starten
nx serve ccu-ui

# Tests ausführen
nx test ccu-ui
nx test mqtt-client
nx test gateway
nx test business

# Build
nx build ccu-ui
```

Die OMF3-Anwendung ist dann unter `http://localhost:4200` verfügbar.

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

### **OMF3 STATE-OF-THE-ART REGELN:**
- **TypeScript:** Strikte Typisierung, keine `any` ohne Begründung
- **RxJS:** Observable Patterns korrekt verwenden (`shareReplay`, `refCount: false` für persistente Streams)
- **Angular:** Component-basierte Architektur, Services für Business Logic
- **Nx Workspace:** Library-basierte Struktur, klare Abhängigkeiten
- **MessageMonitorService:** Für Timing-unabhängige Datenanzeige verwenden
- **Tab Stream Pattern:** Pattern 1 oder Pattern 2 korrekt anwenden
- **Automatische Regel-Erzwingung:** Pre-commit Hooks sorgen für Einhaltung

### **Cursor AI Konfiguration:**
- `.cursorrules` - Projekt-spezifische Regeln
- `.vscode/settings.json` - Cursor-spezifische Einstellungen
- `tsconfig.base.json` - TypeScript-Konfiguration

## 📁 Project Structure

### OMF3 (Aktuell in Entwicklung)
- `omf3/apps/ccu-ui/` - **Angular Dashboard Application**
  - Angular-basierte UI
  - MQTT Client Integration (WebSocket)
  - MessageMonitorService für State Persistence
  - I18n Support (DE, EN, FR)
- `omf3/libs/` - **Libraries**
  - `mqtt-client/` - MQTT Client Library (WebSocket, Mock)
  - `gateway/` - Gateway Library (Topic Mapping)
  - `business/` - Business Logic Library (Derived Streams)
  - `entities/` - Entity Types Library
  - `testing-fixtures/` - Testing Fixtures Library
- `omf3/testing/fixtures/` - Test Fixtures (JSON/JSONL)

### OMF2 (Legacy)
- `omf2/` - **Legacy Streamlit Dashboard**
  - Wird durch OMF3 ersetzt
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

#### **OMF3 (Aktuell) - Angular-basierte Architektur**
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
