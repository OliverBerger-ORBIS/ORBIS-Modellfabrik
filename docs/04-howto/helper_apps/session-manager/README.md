# 🎬 Session Manager - Helper App Dokumentation

## 📋 Übersicht

Der **Session Manager** ist eine unabhängige Helper App zur Analyse der APS Fischertechnik Miniatur-Fabrik. Er dient dem Verständnis der Nachrichten-Semantik und -Funktionsweise für die Entwicklung einer eigenen Steuerungsanwendung.

## 🎯 Zweck

- **📹 Aufnahme** von MQTT-Sessions der APS-Fabrik
- **🎬 Wiedergabe** von aufgezeichneten Sessions
- **📊 Analyse** der Nachrichten-Ströme und -Muster
- **🔍 Template-Erkennung** für MessageGenerator

## 🎯 Zweck-Diagramm

```mermaid
graph TD
    A[APS-Fabrik] -->|Live MQTT| B[📹 Session Recorder]
    B -->|Speichert| C[Session Files]
    
    C -->|Analysiert| D[📊 Session Analysis]
    C -->|Generiert| E[🔍 Template Analysis]
    C -->|Replay| F[🎬 Replay Station]
    
    D -->|Erkennt| G[Message Patterns]
    E -->|Erstellt| H[Message Templates]
    F -->|Testet| I[OMF Dashboard]
    
    style A fill:#fff8e1
    style B fill:#90caf9,stroke:#1976d2,stroke-width:3px
    style C fill:#f5f5f5
    style D fill:#bbdefb
    style E fill:#bbdefb
    style F fill:#bbdefb
    style G fill:#e3f2fd
    style H fill:#e3f2fd
    style I fill:#e3f2fd
```

### **Farbnuancen-Erklärung:**
- **🔵 Dunkelblau (`#90caf9`):** Session Recorder - **Zentrale Komponente** (Aufnahme)
- **🔵 Mittelblau (`#bbdefb`):** Session Analysis, Template Analysis, Replay Station - **Kern-Funktionen**
- **🔵 Hellblau (`#e3f2fd`):** Message Patterns, Templates, OMF Dashboard - **Ergebnisse/Output**
- **🟡 Gelb (`#fff8e1`):** APS-Fabrik - **FT Hardware (Input)**
- **⚪ Grau (`#f5f5f5`):** Session Files - **Daten-Speicher**

## 🏗️ Architektur

## 📅 Sprint-Zuordnung

Die Session Manager Komponenten wurden in folgenden Sprints entwickelt:

| Komponente | Sprint | Zeitraum | Beschreibung |
|------------|--------|----------|--------------|
| **📹 Session Recorder** | Sprint 1 | 24.07 - 06.08.2025 | MQTT-Aufnahme, SQLite + Log-Dateien |
| **🎬 Replay Station** | Sprint 2 | 07.08 - 22.08.2025 | Session-Wiedergabe für Dashboard-Tests |
| **📊 Session Analysis** | Sprint 3 | 23.08 - 03.09.2025 | Timeline-Visualisierung, Template Analyser |
| **🔍 Template Analysis** | Sprint 4 | 04.09 - 17.09.2025 | Registry-Aufbau, Template-Integration |
| **⚡ Optimierungen** | Sprint 5 | 18.09 - 01.10.2025 | Performance, UI, Integration |

## 📚 Dokumentation

### 🎯 Tab-spezifische Anleitungen

| Tab | Beschreibung | Dokumentation |
|-----|-------------|---------------|
| 📹 **Session Recorder** | MQTT-Sessions aufnehmen | [session-recorder.md](session-recorder.md) |
| 🎬 **Replay Station** | Sessions wiedergeben | [replay-station.md](replay-station.md) |
| 📊 **Session Analysis** | Sessions analysieren | [session-analysis.md](session-analysis.md) |
| 🔍 **Template Analysis** | Message-Templates erkennen | [template-analysis.md](template-analysis.md) |

### 🔧 Allgemeine Themen

- [**Troubleshooting**](troubleshooting.md) - Häufige Probleme und Lösungen

## 🚀 Schnellstart

```bash
# Session Manager starten
streamlit run omf/helper_apps/session_manager/session_manager.py
```

## 📈 Sprint-Zuordnung

- **Sprint 1-2:** Grundstruktur und Session Recorder
- **Sprint 3-4:** Replay Station und Session Analysis  
- **Sprint 5:** Template Analysis und Optimierungen

## 🔗 Verwandte Dokumentation

- [**OMF Dashboard**](../../development/dashboard-components.md) - Haupt-Dashboard
- [**MQTT Integration**](../../communication/mqtt/) - MQTT-Kommunikation
- [**Template System**](../../../02-architecture/message-template-system.md) - Message-Templates
- [**Mermaid Diagramm Regeln**](../../diagrams/cursor-ai-mermaid-rules.md) - Cursor AI Regeln für Diagramme
