# FTS/AGV Analysis Example Application

## 🎯 Anforderung

Erstellen einer Beispiel-App, die prinzipiell nahtlos in die omf3 Angular-App in einem neuen Tab eingebaut werden kann. Die Anwendung dient der Auswertung und sinnvollen Darstellung von Daten zum FTS/AGV-Modul.

## 📋 Zielsetzung

### Primäres Ziel
Auswertung und Darstellung von FTS/AGV-relevanten Informationen aus MQTT-Topics, insbesondere:
- **Batteriestatus**: Visualisierung des aktuellen Batteriezustands (Voltage, Percentage, Charging State)
- **Routen**: Darstellung der geplanten und aktuellen Navigationsrouten (VDA5050)
- **Aktueller Standort**: Echtzeit-Position des mobilen Transportsystems auf dem Shopfloor-Layout
- **Action States**: Status der aktuellen Aktionen (DOCK, PASS, PICK, DROP, etc.)
- **Load Information**: Informationen über geladene Workpieces

### Datenquellen
Die Daten werden aus vorhandenen MQTT-Topic-Payloads verwendet:
- **FTS Topics**: `fts/v1/ff/5iO4/state`, `fts/v1/ff/5iO4/order`, `fts/v1/ff/5iO4/connection`
- **CCU Topics**: `ccu/order/active`, `ccu/order/completed` (relevant für FTS-Navigation)
- **Module Topics**: Module States für FTS-Interaktionen (HBW, DPS, AIQS)

> **Hinweis**: Die Daten liegen derzeit nur als `*.log` oder `*.db` Dateien vor (siehe `data/omf-data/fts-analysis/` für analysierte Beispieldaten).

## 🏗️ Architektur & Integration

### Layout-Integration
Die Beispiel-Anwendung verwendet das **shopfloor-preview Layout**:
- Integration in das bestehende `shopfloor-preview` Component
- FTS-Position wird als Overlay auf dem Shopfloor-Layout dargestellt
- Routen werden als Pfade zwischen Nodes visualisiert
- Nutzung der vorhandenen `ftsPosition` Input-Property

### Beispiel-App Struktur
Die Anwendung folgt dem etablierten Pattern für Beispiel-Apps:
- **Verzeichnis**: `examples/fts-analysis-angular/`
- **Standalone Angular App**: Unabhängig lauffähig für Entwicklung und Testing
- **OMF3-kompatibel**: Verwendet die gleichen Libraries und Patterns wie die Hauptanwendung
- **Integration-ready**: Nach Approval nahtlos in omf3 integrierbar

### Technische Umsetzung
- **Angular**: Standalone Components, OnPush Change Detection
- **RxJS**: Observable-basierte Datenströme (kompatibel mit OMF3 MessageMonitorService)
- **TypeScript**: Strikte Typisierung, Shared Types mit omf3
- **MQTT Integration**: Mock Service für Entwicklung, später echte MQTT-Subscriptions
- **Layout**: Nutzung von `shopfloor_layout.json` für Shopfloor-Koordinaten

## 🚀 Use Cases

### 1. FTS Status Dashboard
**Ziel**: Übersichtliche Darstellung des aktuellen FTS-Zustands
- Batteriestatus mit visueller Anzeige (Prozent, Spannung, Ladezustand)
- Aktuelle Position auf dem Shopfloor-Layout
- Aktueller Action State (DOCK, PASS, PICK, DROP, etc.)
- Load Information (geladene Workpieces)

### 2. Route Visualization
**Ziel**: Visualisierung der FTS-Navigationsrouten
- Geplante Route aus `fts/v1/ff/5iO4/order` (VDA5050 Format)
- Aktuelle Route mit Node-Sequenz
- Abgeschlossene Route-Segmente
- Interaktive Route-Exploration

### 3. Track & Trace Scenario
**Ziel**: Nachverfolgung von Workpieces durch den gesamten Produktionsprozess

**Workpiece-ID basierte Nachverfolgung**:
- **Storage-Prozess**: Welche Module waren beteiligt? (HBW, DPS)
- **Production-Prozess**: Welche Maschinen waren beteiligt? (MILL, DRILL, AIQS)
- **FTS-Transport**: Welche Routen wurden genutzt? Welche Timestamps?
- **Umgebungsdaten**: Sensor-Daten (Temperatur, Druck) zu relevanten Zeitpunkten
- **Zukünftige Erweiterungen**:
  - ERP-Daten Integration (Purchase Orders, Customer Orders)
  - Raw Material Tracking (Wer hat geliefert? Wer hat bestellt?)
  - Produktionsrelevante Einstellungen pro Workpiece

**Datenverknüpfung**:
- Timestamp-basierte Kopplung von MQTT-Topics
- Workpiece-ID als gemeinsamer Schlüssel
- Session-Daten als Datenquelle (aktuell aus `*.log`/`*.db` Dateien)

## 📊 Datenanalyse & Vorbereitung

### Analysierte Sessions
Für die Entwicklung wurden bereits Session-Daten analysiert:
- **Production Order BWR**: 3625 Messages, 1528 FTS-relevante (42%)
- **Storage Orders** (White/Blue/Red): ~576 Messages, ~208 FTS-relevante (36%)

**Datenstruktur**: Siehe `data/omf-data/fts-analysis/README.md`

### Relevante Topics
- `fts/v1/ff/5iO4/state`: 334 Messages (Production), ~25 Messages (Storage)
- `fts/v1/ff/5iO4/order`: 23 Messages (Production), ~2 Messages (Storage)
- `ccu/order/active`: 63 Messages (Production), ~7 Messages (Storage)

## 🔄 Integration in OMF3

### Schritt 1: Beispiel-App Entwicklung
- Entwicklung in `examples/fts-analysis-angular/`
- Mock MQTT Service für Testdaten
- Verwendung von OMF3 Libraries (mqtt-client, gateway, entities)

### Schritt 2: Integration als Tab
Nach Approval der Beispiel-App:
- Neuer Tab in `omf3/apps/ccu-ui/src/app/tabs/fts-tab.component.ts`
- Integration der FTS-Analyse-Komponenten
- Ersetzung des Mock Services durch echte MQTT-Subscriptions
- Nutzung des MessageMonitorService für State Persistence

### Schritt 3: Shopfloor-Integration
- Erweiterung der `shopfloor-preview` Komponente
- FTS-Position Overlay (bereits vorhanden via `ftsPosition` Input)
- Route-Visualisierung als SVG-Pfade
- Interaktive Route-Exploration

## 📁 Dateistruktur (Beispiel-App)

```
examples/fts-analysis-angular/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── fts-status/          # FTS Status Dashboard
│   │   │   ├── fts-battery/         # Batteriestatus Visualisierung
│   │   │   ├── fts-route/           # Route Visualization
│   │   │   ├── fts-position/        # Position auf Shopfloor
│   │   │   └── track-trace/         # Track & Trace Component
│   │   ├── services/
│   │   │   ├── fts-data.service.ts  # FTS-Daten Service
│   │   │   ├── mqtt-mock.service.ts # Mock MQTT Service
│   │   │   └── track-trace.service.ts # Track & Trace Logic
│   │   └── app.component.ts
│   └── assets/
│       └── shopfloor/
│           └── shopfloor_layout.json  # Shopfloor Layout (shared)
├── README.md
└── package.json
```

## 🎨 UI-Konzeption

### FTS Status Dashboard
- **Batterie-Anzeige**: Circular Progress mit Spannung und Prozent
- **Position**: Shopfloor-Layout mit FTS-Marker
- **Action State**: Badge mit aktueller Aktion
- **Load Info**: Liste der geladenen Workpieces

### Route Visualization
- **Shopfloor-Overlay**: Route als farbige Linie auf dem Layout
- **Node-Marker**: Aktueller Node, geplante Nodes
- **Route-Info**: Liste der Nodes mit Timestamps

### Track & Trace
- **Workpiece-Suche**: Input für Workpiece-ID
- **Timeline**: Chronologische Darstellung aller Events
- **Module-Interaktionen**: Welche Module waren beteiligt?
- **FTS-Transport**: Welche Routen wurden genutzt?

## 🔗 Verwandte Komponenten

- **Shopfloor Preview**: `omf3/apps/ccu-ui/src/app/components/shopfloor-preview`
- **MQTT Client**: `omf3/libs/mqtt-client/`
- **Gateway**: `omf3/libs/gateway/`
- **Entities**: `omf3/libs/entities/`
- **FTS Topics Registry**: `omf2/registry/topics/fts.yml`
- **Session Analysis**: `data/omf-data/fts-analysis/`

## 📝 Nächste Schritte

1. ✅ **Datenanalyse**: Session-Daten analysiert (siehe `data/omf-data/fts-analysis/`)
2. 🔄 **Beispiel-App Entwicklung**: Implementierung in `examples/fts-analysis-angular/`
3. ⏳ **Integration**: Nach Approval Integration als Tab in omf3
4. ⏳ **Track & Trace**: Erweiterung um ERP-Daten Integration

## 🎯 Erfolgskriterien

- [ ] Beispiel-App läuft standalone in `examples/fts-analysis-angular/`
- [ ] FTS Status Dashboard zeigt Batterie, Position, Action State
- [ ] Route Visualization funktioniert mit Shopfloor-Layout
- [ ] Track & Trace kann Workpiece-ID basiert nachverfolgen
- [ ] Code folgt OMF3 Patterns (RxJS, TypeScript, OnPush)
- [ ] Integration-ready für omf3 Tab

