# Glossary - Eindeutige Begrifflichkeiten & IDs

## 🔑 Zentrale Begriffe

### OMF (Orbis Modellfabrik)
**Definition:** Das gesamte System zur Steuerung der Fischertechnik-Modellfabrik über MQTT.

**Kontext:** OMF umfasst Dashboard, Session-Manager, Registry und alle Steuerungskomponenten.

### Registry
**Definition:** `registry/model/v1/` - Single Source of Truth für alle MQTT-Nachrichtenstrukturen.

**Enthält:** Templates, Mappings, Enums, Module-Definitionen, Workpiece-Definitionen.

### Template
**Definition:** Topic-freie Definition einer MQTT-Nachrichtenstruktur.

**Schema:** `domain.object.variant` (z.B. `module.state.drill`)

**Wichtig:** Templates enthalten KEINE Topic-Strings!

### Mapping
**Definition:** Verbindung zwischen MQTT-Topic und Template.

**Priorität:** Exact > Pattern (Serial-Number-spezifisch vor generisch)

### Topic
**Definition:** MQTT-Topic-String für Nachrichtenrouting.

**Schema:** `module/v1/ff/{serial_number}/{type}`

## 🏭 System-Komponenten

### CCU (Central Control Unit)
**Definition:** Zentrale Steuerungseinheit für Workflow-Orchestrierung.

**MQTT-Topics:** `ccu/order/request`, `ccu/state/*`

**Rolle:** Erstellt und verwaltet Produktionsaufträge.

### Node-RED
**Definition:** MQTT ↔ OPC-UA Vermittler zwischen Dashboard und Hardware.

**Rolle:** Übersetzt MQTT-Befehle zu OPC-UA-Calls und aggregiert Status-Daten.

### Module
**Definition:** Physische Produktionsmodule (HBW, DRILL, MILL, AIQS, DPS).

**Steuerung:** Über OPC-UA (via Node-RED), Status über MQTT.

### FTS (Fahrerlose Transportsysteme)
**Definition:** Automatische Transporteinheiten für Workpiece-Transport.

**MQTT-Topics:** `fts/v1/ff/5iO4/*`

### TXT Controller
**Definition:** Fischertechnik-Controller für Sensoren und einfache Steuerung.

**MQTT-Topics:** `/j1/txt/1/f/i/*`

## 📊 Message-Types

### Order (Outbound)
**Definition:** Befehl von Dashboard an Module.

**Beispiel:** `module/v1/ff/SVR4H76449/order` mit `{"command": "DRILL"}`

### State (Inbound)
**Definition:** Status-Update von Module an Dashboard.

**Beispiel:** `module/v1/ff/SVR4H76449/state` mit `{"actionState": {"state": "RUNNING"}}`

### Connection (Bidirectional)
**Definition:** Verbindungsstatus zwischen System und Modulen.

**States:** `ONLINE`, `OFFLINE`, `CONNECTIONBROKEN`

## 🆔 ID-Systeme

### Serial Numbers (Module)
**Format:** `SVR` + 3 Ziffern + 2 Buchstaben + 4 Ziffern

**Beispiele:**
- `SVR3QA0022` - HBW (Hochregallager)
- `SVR3QA2098` - MILL (Fräsmaschine)
- `SVR4H76449` - DRILL (Bohrmaschine)
- `SVR4H73275` - DPS (Drehmaschine)
- `SVR4H76530` - AIQS (Qualitätsprüfung)

### NFC Codes (Workpieces)
**Format:** 14-stellige Hexadezimal-Zeichenkette

**Beispiele:**
- `040a8dca341291` - Rotes Workpiece
- `047f8cca341290` - Weißes Workpiece
- `047389ca341291` - Blaues Workpiece

**Validierung:** Regex `^[0-9A-Fa-f]{14}$`

### Order IDs
**Format:** UUID v4 oder sequenzielle Nummer

**Beispiele:**
- `2ecc8911-1ce4-44d4-bc1a-d9574ef62464` (UUID)
- `12345` (Sequenziell)

### Action IDs
**Format:** UUID v4

**Verwendung:** Eindeutige Identifikation von Aktionen innerhalb eines Orders.

## 🎯 Action States

### Primary States
- **PENDING** - Aktion empfangen, wartet auf Start
- **RUNNING** - Aktion wird aktuell ausgeführt
- **FINISHED** - Aktion erfolgreich abgeschlossen
- **FAILED** - Aktion fehlgeschlagen

### Connection States
- **ONLINE** - Modul verbunden und betriebsbereit
- **OFFLINE** - Modul getrennt
- **CONNECTIONBROKEN** - Verbindung unerwartet verloren

## 🔧 Commands

### Module Commands
- **PICK** - Workpiece aufnehmen
- **DROP** - Workpiece ablegen
- **STORE** - Workpiece einlagern (HBW)
- **DRILL** - Bohren (DRILL-Modul)
- **MILL** - Fräsen (MILL-Modul)
- **CHECK_QUALITY** - Qualitätsprüfung (AIQS-Modul)

### CCU Commands
- **RESET_FACTORY** - Gesamte Fabrik zurücksetzen
- **PAUSE_PRODUCTION** - Produktion pausieren
- **RESUME_PRODUCTION** - Produktion fortsetzen

## 📦 Workpiece Types

### Farben
- **RED** - Rotes Workpiece
- **WHITE** - Weißes Workpiece  
- **BLUE** - Blaues Workpiece

### Order Types
- **STORAGE** - Nur Einlagerung (HBW)
- **PRODUCTION** - Produktionsauftrag (DRILL/MILL)
- **AI** - Mit KI-Qualitätsprüfung

## 🏗️ Template-Keys

### Module Templates
- `module.state.{subtype}` - Modul-Status (drill, mill, aiqs, dps, hbw_inventory)
- `module.connection.{subtype}` - Modul-Verbindung
- `module.order.{subtype}` - Modul-Befehle
- `module.factsheet.{subtype}` - Modul-Informationen

### CCU Templates
- `ccu.state.pairing` - CCU Pairing-Status
- `ccu.state.status` - CCU System-Status
- `ccu.state.config` - CCU Konfiguration
- `ccu.state.layout` - CCU Layout-Status
- `ccu.state.stock` - CCU Lager-Status

### FTS Templates
- `fts.connection` - FTS Verbindungsstatus
- `fts.state` - FTS Status
- `fts.order` - FTS Befehle
- `fts.factsheet` - FTS Informationen

## 🔄 Message-Directions

### Outbound (Dashboard → Module)
- Orders, Commands, Steuerungsbefehle
- QoS: 1 (At least once)

### Inbound (Module → Dashboard)
- States, Status, Telemetrie
- QoS: 0 (At most once)

### Bidirectional
- Connection-Status, Heartbeats
- QoS: 1 (At least once)

## 📍 Topic-Patterns

### Exact Mappings
```
module/v1/ff/SVR3QA0022/state → module.state.hbw_inventory
module/v1/ff/SVR4H76449/state → module.state.drill
ccu/state/pairing → ccu.state.pairing
```

### Pattern Mappings
```
module/v1/ff/{module_id}/state → module.state
module/v1/ff/{module_id}/connection → module.connection
module/v1/ff/{module_id}/order → module.order
```

## 🎨 UI-Konventionen

### Icons
- 📊 State/Status
- 🔌 Connection
- 📋 Orders/Commands
- 🏭 Modules
- 🚛 FTS
- 🎛️ CCU

### Colors
- 🟢 Online/Success
- 🔴 Offline/Error
- 🟡 Pending/Running
- ⚪ Neutral/Info

---

**"Eindeutige Begriffe verhindern Missverständnisse - Dieses Glossar ist die Referenz für alle OMF-Komponenten."**
