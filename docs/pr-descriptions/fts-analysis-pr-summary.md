# FTS/AGV Analysis Example Application

## 🎯 Ziel

Erstellen einer Beispiel-App für die Auswertung und Darstellung von FTS/AGV-Daten, die nahtlos in die omf3 Angular-App als neuer Tab integrierbar ist.

## 📋 Features

### Primäre Funktionen
- **Batteriestatus**: Visualisierung (Voltage, Percentage, Charging State)
- **Routen**: Darstellung geplanter und aktueller Navigationsrouten (VDA5050)
- **Aktueller Standort**: Echtzeit-Position auf dem Shopfloor-Layout
- **Action States**: Status der aktuellen Aktionen (DOCK, PASS, PICK, DROP)
- **Load Information**: Informationen über geladene Workpieces

### Track & Trace
- **Workpiece-ID basierte Nachverfolgung**: Kompletter Storage- und Production-Prozess
- **Timestamp-basierte Kopplung**: Verknüpfung von MQTT-Topics über Timestamps
- **Zukünftige Erweiterungen**: ERP-Daten Integration (Purchase Orders, Customer Orders, Raw Material Tracking)

## 🏗️ Architektur

- **Beispiel-App**: `examples/fts-analysis-angular/` (standalone lauffähig)
- **Layout**: Integration in `shopfloor-preview` Component
- **Datenquellen**: MQTT-Topics (`fts/v1/ff/5iO4/*`, `ccu/order/*`, `module/v1/ff/*`)
- **Pattern**: Folgt OMF3-Architektur (RxJS, TypeScript, OnPush, MessageMonitorService)

## 📊 Datenanalyse

Analysierte Sessions für Entwicklung:
- **Production Order BWR**: 3625 Messages, 1528 FTS-relevante (42%)
- **Storage Orders**: ~576 Messages, ~208 FTS-relevante (36%)

Siehe `data/omf-data/fts-analysis/` für strukturierte Daten.

## 🔄 Integration

1. **Entwicklung**: Standalone Beispiel-App in `examples/fts-analysis-angular/`
2. **Integration**: Nach Approval als Tab in omf3 (`fts-tab.component.ts`)
3. **Shopfloor**: FTS-Position Overlay auf bestehendem Layout

## 📝 Details

Vollständige Beschreibung: `docs/pr-descriptions/fts-analysis-example-app.md`

