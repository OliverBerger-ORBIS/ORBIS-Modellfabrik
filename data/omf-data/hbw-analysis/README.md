# HBW Session Analysis Data

Diese Dateien enthalten die analysierten MQTT-Session-Daten für das **HBW (High Bay Warehouse)** Modul.

## Zweck

Die Analyse-Scripts extrahieren alle HBW-relevanten Topics und Payloads aus Session-Log-Dateien, um strukturierte JSON-Daten für die Entwicklung von Beispiel-Anwendungen bereitzustellen.

## Datei-Namenskonvention

Jede Session generiert mehrere Dateien:

- `{session-name}_metadata.json` - Gesamt-Statistiken und Metadaten
- `{session-name}_hbw_connection.json` - Connection-Status Messages
- `{session-name}_hbw_state.json` - State-Update Messages
- `{session-name}_hbw_order.json` - Order-Command Messages
- `{session-name}_hbw_instant_action.json` - Instant Action Messages
- `{session-name}_hbw_factsheet.json` - Factsheet Messages
- `{session-name}_all_hbw_messages.json` - Alle HBW-relevanten Messages
- `{session-name}_storage_operations.json` - STORE/PICK/DROP Operationen
- `{session-name}_storage_order_context.json` - Messages im STORAGE-ORDER Kontext
- `{session-name}_storage_commands_context.json` - Messages im Kontext von Storage-Commands

## Relevante Topics

### Direkte HBW-Topics
- `module/v1/ff/SVR3QA0022/connection` - Connection Status
- `module/v1/ff/SVR3QA0022/state` - State Updates
- `module/v1/ff/SVR3QA0022/order` - Order Commands
- `module/v1/ff/SVR3QA0022/instantAction` - Instant Actions
- `module/v1/ff/SVR3QA0022/factsheet` - Factsheet

### NodeRed-enriched Topics
- `module/v1/ff/NodeRed/SVR3QA0022/connection` - Connection (NodeRed enriched)
- `module/v1/ff/NodeRed/SVR3QA0022/state` - State (NodeRed enriched)
- `module/v1/ff/NodeRed/SVR3QA0022/factsheet` - Factsheet (NodeRed)

### Weitere relevante Topics
- `ccu/order/active` - CCU Active Order
- `ccu/order/completed` - CCU Completed Order
- `ccu/order/request` - CCU Order Request
- `ccu/state/calibration/SVR3QA0022` - HBW Calibration State
- `ccu/set/calibration` - CCU Calibration Commands
- `ccu/pairing/state` - CCU Pairing State (enthält HBW Info)

## Datenformat

### Metadata-Datei
```json
{
  "session_name": "auftrag-blau_1",
  "analysis_timestamp": "2025-12-17T...",
  "hbw_serial": "SVR3QA0022",
  "total_messages": 1234,
  "hbw_relevant_messages": 56,
  "topic_counts": {...},
  "commands_found": {"PICK": 10, "DROP": 8, "STORE": 5},
  "storage_operations_count": 23,
  ...
}
```

### Message-Format
Jede Message enthält:
```json
{
  "timestamp": "2025-12-17T10:30:00.000Z",
  "topic": "module/v1/ff/SVR3QA0022/state",
  "payload": "{...}" // JSON-String oder Objekt
}
```

## HBW-spezifische Commands

- **PICK** - Workpiece aus Lager entnehmen
- **DROP** - Workpiece im Lager ablegen
- **STORE** - Workpiece im Lager einlagern

## Verwendung

Die Scripts können für einzelne Sessions oder alle Sessions ausgeführt werden:

```bash
# Einzelne Session
python3 scripts/analyze_hbw_sessions.py data/omf-data/sessions/auftrag-blau_1.log

# Alle Sessions (Bash-Loop)
for log in data/omf-data/sessions/*.log; do
  python3 scripts/analyze_hbw_sessions.py "$log"
done
```

## Wichtige Erkenntnisse

- **HBW** ist primär für Storage-Operationen zuständig (STORAGE-ORDER)
- **Commands**: PICK, DROP, STORE (Lager-Operationen)
- **Kein TXT-Controller**: HBW kommuniziert nur über OPC-UA/NodeRed
- **Storage-Slots**: Informationen über Lagerstände können in State-Messages enthalten sein

## Nächste Schritte

Diese Daten werden verwendet, um:
1. HBW-spezifische Beispiel-Anwendungen zu entwickeln
2. Storage-Slot-Visualisierungen zu erstellen
3. Inventory-Management-Features zu implementieren
