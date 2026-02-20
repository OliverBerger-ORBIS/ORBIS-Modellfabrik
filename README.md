# ORBIS SmartFactory

> Fragen? fischertechnik-technik@fischer.de

**OSF** (ORBIS-SmartFactory) ist Konzept und Vision: **Unsere Produkte** (DSP, MES, …) und Leistungen demonstrierbar machen – mit Use Cases, Demos, Messeauftritten. Die Fischertechnik APS 24V (FMF + APS) dient als physische Testumgebung. Details: [Vision](docs/01-strategy/vision.md) (Konzept, FMF/APS, Projekt-Scope).

---

## 🎯 Quick Start

- **Neue Teammitglieder:** [Vision](docs/01-strategy/vision.md) → [Project Structure](docs/02-architecture/project-structure.md)
- **Entwickler:** [Project Structure](docs/02-architecture/project-structure.md) → [How-Tos](docs/04-howto/)
- **Architekten:** [Decision Records](docs/03-decision-records/) → [Architecture](docs/02-architecture/)
- **Anwender/Demonstratoren (Messe, Kunden):** [Use-Case Bibliothek](docs/02-architecture/use-case-library.md) → [OBS Präsentation](docs/04-howto/presentation/obs-video-presentation-setup.md)

## 🏗️ System-Übersicht

### APS (As-Is) – Fischertechnik-System
- **FMF** (Fischertechnik-ModellFabrik) – physische Komponenten (DRILL, HBW, etc.), TXT4.0
- **APS** – Software-Teil: APS-CCU, APS-NodeRED, Frontend

### OSF (To-Be) – Unser System
- **OSF-UI** – Dashboard zur Visualisierung (Angular, ehemals OMF3)
- **Session Manager** – Helper-App für Session-Replay (Streamlit)

### Wo liegt was?
- **OSF:** `osf/` – Angular Dashboard & Libraries
- **Session Manager:** `session_manager/` – Session-Replay
- **APS-Referenz:** `integrations/` – APS AS-IS Komponenten, TXT-Controller
- **Legacy:** [Archive](docs/archive/) – Veraltete Dokumentation

> **Namenskonvention:** Groß-Schreibweise mit Bindestrich (z.B. APS-CCU, OSF-UI)

---

## 📚 Dokumentations-Struktur

### 01-Strategy
- [Vision](docs/01-strategy/vision.md) – Konzept, FMF/APS, MQTT-first
- [Roadmap](docs/01-strategy/roadmap.md) – Entwicklungsphasen

### 02-Architecture
- [OSF Project Structure](docs/02-architecture/project-structure.md) – Nx Workspace & Architektur
- [Naming Conventions](docs/02-architecture/naming-conventions.md) – Topics, Template-Keys, IDs
- [APS Data Flow](docs/02-architecture/aps-data-flow.md) – APS Datenverarbeitung & Storage

### 03-Decision Records (ADRs)
- [Tab Stream Initialization Pattern](docs/03-decision-records/11-tab-stream-initialization-pattern.md)
- [MessageMonitorService Storage](docs/03-decision-records/12-message-monitor-service-storage.md)

### 04-How-To
- [MQTT WebSocket Debug Guide](docs/04-howto/mqtt-websocket-debug-guide.md) – MQTT-Debugging, Verbindung
- [UI Symbols Usage Guide](docs/04-howto/ui_symbols.md) – SVG Icons
- [Shopfloor Layout Guide](docs/04-howto/SHOPFLOOR_LAYOUT_GUIDE.md) – Shopfloor-Konfiguration
- [Session Manager](docs/04-howto/helper_apps/session-manager/README.md) – Session-Replay
- [OBS Präsentation](docs/04-howto/presentation/obs-video-presentation-setup.md) – Messe/Kunden-Demos

### 06-Integrations
- [FISCHERTECHNIK-OFFICIAL](docs/06-integrations/FISCHERTECHNIK-OFFICIAL.md) – Offizielle MQTT-Doku, CCU-Source, Repo-Zuordnung
- [fischertechnik-official/](docs/06-integrations/fischertechnik-official/) – Lokale Kopie der FT-MQTT-Doku
- [00-REFERENCE](docs/06-integrations/00-REFERENCE/README.md) – ORBIS-spezifische APS-Referenz
- [APS-CCU](docs/06-integrations/APS-CCU/README.md) | [APS-NodeRED](docs/06-integrations/APS-NodeRED/README.md)

### 99-Glossary
- [Glossary](docs/99-glossary.md) – Begrifflichkeiten & IDs

---

## 🔗 Integrations & externe Quellen

### Fischertechnik – Bei Erweiterungen: wo ansetzen?

| Änderung / Erweiterung | Repo | Quellen | Tool |
|------------------------|------|---------|------|
| **MQTT, CCU, Node-RED** | [24V-**Dev**](https://github.com/fischertechnik/Agile-Production-Simulation-24V-Dev) | central-control, nodeRed, docs, mosquitto, DEPLOYMENT.md | Docker, npm, Node-RED |
| **TXT-Programme (\*.ft)** | [24V](https://github.com/fischertechnik/Agile-Production-Simulation-24V) – Originale dort; OSF-Versionen in `integrations/TXT-*/archives/` | TXT4.0-programs/ | RoBO Pro Coding |
| **PLC-Programme (\*.zap18)** | [24V](https://github.com/fischertechnik/Agile-Production-Simulation-24V) | PLC-programs/S7_1200_TIAv18/ | TIA Portal, UA-Expert |

→ Details: [FISCHERTECHNIK-OFFICIAL](docs/06-integrations/FISCHERTECHNIK-OFFICIAL.md) | [fischertechnik-official/](docs/06-integrations/fischertechnik-official/) (lokale Kopie)

### Fischertechnik Produktseiten
- [Product Page](https://www.fischertechnik.de/en/products/industry-and-universities/training-models/569289-agile-production-simulation-24v)
- [Documentation PDF](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/documentation_aps_en-0424.pdf)
- [Quick Start Guide](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/quick-start-guide-agile-production-simulation_en.pdf)
- [Troubleshooting (DE)](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/de/fehlersuche_aps_de.pdf)

---

## 🚀 Getting Started

1. **Repository klonen**
2. **System verstehen:** [Vision](docs/01-strategy/vision.md) (5 Min)
3. **Architektur:** [OSF Project Structure](docs/02-architecture/project-structure.md) (10 Min)
4. **Praktisch:** [How-Tos](docs/04-howto/) (je nach Aufgabe)

### OSF Development

```bash
npm install
nx serve osf-ui
# → http://localhost:4200
```

### Session Manager

```bash
source .venv/bin/activate
streamlit run session_manager/app.py
# → http://localhost:8501
```

---

## 📁 Project Structure

| Verzeichnis | Inhalt |
|-------------|--------|
| `osf/` | Angular Dashboard, mqtt-client, gateway, business, entities |
| `session_manager/` | Session-Replay Helper-App |
| `integrations/` | APS-CCU, APS-NodeRED, TXT-Controller (archives/ + workspaces/) – alle OSF-Versionen |

### OSF-Regeln
- **TypeScript:** Strikte Typisierung
- **RxJS:** `shareReplay`, `refCount: false` für persistente Streams
- **MessageMonitorService** für Timing-unabhängige Anzeige
- **Tab Stream Pattern** – siehe Decision Records

---

## 📋 APS-Hardware-Referenz (Submodul vendor/fischertechnik)

- **PLC-programs/** – Module (HBW, DPS, AIQS, DRILL, MILL, OVEN), TIA Portal
- **TXT4.0-programs/** – FF_AI_24V.ft, FF_CGW.ft, FF_DPS_24V.ft, fts_main.ft – RoBO Pro Coding
- **Node-RED/flows.json** – Node-RED Flows
- **CCU:** [RPI Image](RPI_Image.md), SSH: `ff22` / `ff22+`

---

*"Code as Doc" – Docs erklären das Warum und Wie.*
