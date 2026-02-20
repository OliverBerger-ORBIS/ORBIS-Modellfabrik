# Node-RED Analysis Tools

## 🎯 Zweck
Diese Tools analysieren die Node-RED Flows der Fischertechnik APS (Agile Production Simulation) und generieren Dokumentation mit Mermaid-Diagrammen.

## 📁 Scripts

### `aps_analysis.py`
**Hauptanalyse-Script** - Generiert die komplette APS-Dokumentation
- Analysiert `flows.json` aus `integrations/node_red/backups/`
- Fokussiert auf Module: MILL, DRILL, AIQS, DPS, HBW
- Erstellt Markdown-Dokumentation in `docs/07-analysis/node-red/aps_docs/`
- Generiert Mermaid-Diagramme für System-Architektur, State Machines, OPC-UA, MQTT

### `generate_module_status_diagrams.py`
**Diagramm-Generator** - Erstellt Status-Übergangs-Diagramme
- Generiert individuelle Mermaid-Diagramme für jeden Produktionsmodul
- Erstellt System-Architektur, OPC-UA Communication, MQTT Topic Hierarchy
- Speichert Diagramme als `.mermaid` Dateien

### `generate_diagrams.py`
**Zusätzliche Diagramme** - Erstellt weitere Visualisierungen
- Generiert Module Flow Diagram
- Erstellt MQTT Topic Hierarchy
- Erstellt OPC-UA Communication Flow
- Erstellt System Overview

## 📊 Daten

### `aps_analysis_data.json`
**Rohdaten** - Enthält die extrahierten Analyse-Ergebnisse
- Module States und Commands
- OPC-UA NodeIds
- MQTT Topics
- State Transitions
- Für Referenz und Debugging

## 🚀 Verwendung

### Komplette Analyse durchführen:
```bash
cd tools/node_red_analysis/
python aps_analysis.py
```

### Nur Diagramme generieren:
```bash
cd tools/node_red_analysis/
python generate_module_status_diagrams.py
python generate_diagrams.py
```

## 📋 Voraussetzungen

- Python 3.x
- `flows.json` in `integrations/node_red/backups/`
- Mermaid-Unterstützung für Diagramm-Rendering

## 🎯 Ausgabe

Die Scripts generieren:
- **Dokumentation**: `docs/07-analysis/node-red/aps_docs/`
- **Diagramme**: `.mermaid` Dateien
- **Rohdaten**: `aps_analysis_data.json`

## 📝 Hinweise

- Scripts analysieren nur die relevanten Module (MILL, DRILL, AIQS, DPS, HBW)
- OVEN-Modul wird ignoriert (nicht in unserer Konfiguration)
- Alle Diagramme werden direkt in Markdown eingebettet
- Dokumentation beschreibt das System **vor** OSF-UI-Integration
