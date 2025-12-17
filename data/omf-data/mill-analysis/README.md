# MILL Session Analysis Data

Diese Dateien enthalten die analysierten MQTT-Session-Daten für das **MILL (Frässtation)** Modul.

## Zweck

Die Analyse-Scripts extrahieren alle MILL-relevante Topics und Payloads aus Session-Log-Dateien, um strukturierte JSON-Daten für die Entwicklung von Beispiel-Anwendungen bereitzustellen.

## Datei-Namenskonvention

Jede Session generiert mehrere Dateien:

- `{session-name}_metadata.json` - Gesamt-Statistiken und Metadaten
- `{session-name}_mill_connection.json` - Connection-Status Messages
- `{session-name}_mill_state.json` - State-Update Messages
- `{session-name}_mill_order.json` - Order-Command Messages
- `{session-name}_mill_instant_action.json` - Instant Action Messages
- `{session-name}_mill_factsheet.json` - Factsheet Messages
- `{session-name}_all_mill_messages.json` - Alle MILL-relevanten Messages
- `{session-name}_mill_operations.json` - PICK/MILL/DROP Operationen
- `{session-name}_production_order_context.json` - Messages im PRODUCTION-ORDER Kontext
- `{session-name}_mill_commands_context.json` - Messages im Kontext von MILL-Commands

## Relevante Topics

### Direkte MILL-Topics
- `module/v1/ff/SVR3QA2098/connection` - Connection Status
- `module/v1/ff/SVR3QA2098/state` - State Updates
- `module/v1/ff/SVR3QA2098/order` - Order Commands
- `module/v1/ff/SVR3QA2098/instantAction` - Instant Actions
- `module/v1/ff/SVR3QA2098/factsheet` - Factsheet

### NodeRed-enriched Topics
- `module/v1/ff/NodeRed/SVR3QA2098/connection` - Connection (NodeRed enriched)
- `module/v1/ff/NodeRed/SVR3QA2098/state` - State (NodeRed enriched)
- `module/v1/ff/NodeRed/SVR3QA2098/factsheet` - Factsheet (NodeRed)

### Weitere relevante Topics
- `ccu/order/active` - CCU Active Order
- `ccu/order/completed` - CCU Completed Order
- `ccu/order/request` - CCU Order Request
- `ccu/state/calibration/SVR3QA2098` - MILL Calibration State
- `ccu/set/calibration` - CCU Calibration Commands
- `ccu/pairing/state` - CCU Pairing State (enthält MILL Info)

## Datenformat

### Metadata-Datei
```json
{
  "session_name": "auftrag-blau_1",
  "analysis_timestamp": "2025-12-17T...",
  "mill_serial": "SVR3QA2098",
  "total_messages": 1234,
  "mill_relevant_messages": 56,
  "topic_counts": {...},
  "commands_found": {"PICK": 10, "MILL": 8, "DROP": 5},
  "mill_operations_count": 23,
  ...
}
```

### Message-Format
Jede Message enthält:
```json
{
  "timestamp": "2025-12-17T10:30:00.000Z",
  "topic": "module/v1/ff/SVR3QA2098/state",
  "payload": "{...}" // JSON-String oder Objekt
}
```

## MILL-spezifische Commands

- **PICK** - Workpiece aufnehmen
- **MILL** - Fräsen (Production-Operation)
- **DROP** - Workpiece ablegen

## Verwendung

Die Scripts können für einzelne Sessions oder alle Sessions ausgeführt werden:

```bash
# Einzelne Session
python3 scripts/analyze_mill_sessions.py data/omf-data/sessions/auftrag-blau_1.log

# Alle Sessions (Bash-Loop)
for log in data/omf-data/sessions/*.log; do
  python3 scripts/analyze_mill_sessions.py "$log"
done
```

## Wichtige Erkenntnisse

- **MILL** ist primär für Production-Operationen zuständig (PRODUCTION-ORDER)
- **Commands**: PICK → MILL → DROP (Standard-Produktionssequenz)
- **Kein TXT-Controller**: MILL kommuniziert nur über OPC-UA/NodeRed
- **Production Duration**: MILL-Operationen haben eine definierte Dauer (typisch 5-10 Sekunden)

## Nächste Schritte

Diese Daten werden verwendet, um:
1. MILL-spezifische Beispiel-Anwendungen zu entwickeln
2. Production-Status-Visualisierungen zu erstellen
3. Command-History-Features zu implementieren
